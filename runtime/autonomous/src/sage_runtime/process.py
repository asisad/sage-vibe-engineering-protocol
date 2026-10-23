"""Bounded, shell-free process execution for controller-owned commands only."""

from __future__ import annotations

import ctypes
import math
import os
import signal
import subprocess
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path


def minimal_environment(*, provider: bool = False) -> dict[str, str]:
    """Allowlist OS necessities; checks never inherit model/API credentials."""
    names = {
        "PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "COMSPEC", "TEMP", "TMP",
        "LANG", "LC_ALL", "LOCALAPPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)",
        "PROGRAMDATA",
    }
    if provider:
        # Codex account credentials are looked up by the CLI, never read here.
        names.update({"USERPROFILE", "HOME", "APPDATA", "CODEX_HOME"})
    result = {key: value for key, value in os.environ.items() if key.upper() in names}
    result.update({"PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "NO_COLOR": "1"})
    return result


class _WindowsJob:
    """Kill-on-close job; confines descendants of this process invocation."""

    def __init__(self, process: subprocess.Popen[bytes]):
        self.handle = None
        if os.name != "nt":
            return
        from ctypes import wintypes

        class BASIC(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64),
                        ("PerJobUserTimeLimit", ctypes.c_int64),
                        ("LimitFlags", wintypes.DWORD),
                        ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t),
                        ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t),
                        ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD)]

        class IO(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in
                        ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                         "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

        class EXTENDED(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", BASIC), ("IoInfo", IO),
                        ("ProcessMemoryLimit", ctypes.c_size_t),
                        ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryUsed", ctypes.c_size_t),
                        ("PeakJobMemoryUsed", ctypes.c_size_t)]

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateJobObjectW.restype = wintypes.HANDLE
        kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int,
                                                  ctypes.c_void_p, wintypes.DWORD]
        kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.CreateJobObjectW(None, None)
        if not handle:
            raise OSError("Unable to create owned process job")
        info = EXTENDED()
        info.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not kernel.SetInformationJobObject(handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
            kernel.CloseHandle(handle)
            raise OSError("Unable to bound owned process job")
        if not kernel.AssignProcessToJobObject(handle, wintypes.HANDLE(process._handle)):
            kernel.CloseHandle(handle)
            raise OSError("Unable to assign owned process job")
        self.handle, self.kernel = handle, kernel

    def close(self) -> None:
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


def run_bounded(
    argv: Sequence[str], *, cwd: str | Path, env: Mapping[str, str],
    timeout_seconds: float, input_text: str | None = None,
    max_output_bytes: int = 262144,
    cancel_check: Callable[[], bool] | None = None,
) -> dict:
    """Run exactly once without shell expansion; stop the owned tree on limits.

    stdout/stderr share one byte ceiling. A limit or cancellation is not success,
    even when a child happened to return exit code zero during termination.
    """
    if (not argv or isinstance(argv, (str, bytes)) or
            any(not isinstance(arg, str) or "\0" in arg for arg in argv)):
        raise ValueError("argv must be a non-empty list of safe strings")
    if (not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool) or
            not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 3600):
        raise ValueError("timeout_seconds must be finite and within 3600 seconds")
    if not isinstance(max_output_bytes, int) or not 1024 <= max_output_bytes <= 4194304:
        raise ValueError("output ceiling must be between 1024 and 4194304 bytes")
    started = time.monotonic()
    base = {"argv": list(argv), "exit_code": None, "stdout": "", "stderr": "",
            "duration_seconds": 0.0, "timed_out": False, "cancelled": False,
            "output_truncated": False, "launch_error": False}
    if cancel_check and cancel_check():
        base["cancelled"] = True
        return base
    process = None
    job = None
    try:
        process = subprocess.Popen(
            list(argv), cwd=str(cwd), env=dict(env), stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
            start_new_session=os.name != "nt",
        )
        job = _WindowsJob(process)
    except OSError:
        if process:
            process.kill()
            process.wait()
        base["launch_error"] = True
        base["stderr"] = "Process launch or process-tree isolation unavailable."
        base["duration_seconds"] = round(time.monotonic() - started, 6)
        return base

    streams = {"stdout": bytearray(), "stderr": bytearray()}
    lock = threading.Lock()
    output_limit = threading.Event()

    def collect(name: str) -> None:
        stream = getattr(process, name)
        try:
            while True:
                block = stream.read(4096)
                if not block:
                    break
                with lock:
                    remaining = max_output_bytes - sum(len(value) for value in streams.values())
                    streams[name].extend(block[:max(remaining, 0)])
                    if len(block) > remaining:
                        output_limit.set()
        except (OSError, ValueError):
            pass

    readers = [threading.Thread(target=collect, args=(name,), daemon=True) for name in streams]
    for thread in readers:
        thread.start()

    def feed() -> None:
        try:
            if input_text:
                process.stdin.write(input_text.encode("utf-8"))
                process.stdin.flush()
        except (BrokenPipeError, OSError, ValueError):
            pass
        finally:
            try:
                process.stdin.close()
            except (OSError, ValueError):
                pass

    writer = threading.Thread(target=feed, daemon=True)
    writer.start()

    def terminate() -> None:
        if os.name == "nt":
            job.close()
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if process.poll() is None:
            process.kill()

    try:
        while process.poll() is None:
            if cancel_check and cancel_check():
                base["cancelled"] = True
                terminate()
                break
            if time.monotonic() - started >= timeout_seconds:
                base["timed_out"] = True
                terminate()
                break
            if output_limit.is_set():
                base["output_truncated"] = True
                terminate()
                break
            time.sleep(0.025)
        process.wait(timeout=5)
    finally:
        # Also kills lingering grandchildren whose parent exited successfully.
        terminate()
        for thread in readers:
            thread.join(timeout=2)
        writer.join(timeout=1)
        for name, value in streams.items():
            base[name] = bytes(value).decode("utf-8", errors="replace")
        base["output_truncated"] = base["output_truncated"] or output_limit.is_set()
        base["exit_code"] = process.returncode
        base["duration_seconds"] = round(time.monotonic() - started, 6)
        for name in ("stdin", "stdout", "stderr"):
            try:
                getattr(process, name).close()
            except (OSError, ValueError):
                pass
    return base
