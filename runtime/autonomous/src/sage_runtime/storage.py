"""Private checkpoints committed by an append-only, SHA-256 chained ledger.

A save first durably creates an immutable snapshot, then appends the ledger
commit. An interrupted, unreferenced snapshot is not a committed state. A torn
ledger record fails closed; this module never silently truncates evidence.
Hash chaining detects corruption, not a privileged attacker rewriting all data.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import threading
import uuid

from .safety import SageError, _checked_absolute, _is_link, _read_regular


_RUN_ID = re.compile(r"^[a-f0-9]{32}$")
_SNAPSHOT = re.compile(r"^cp-[a-f0-9]{32}\.json$")
_EVENT = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,63}$")
_HASH = re.compile(r"^[a-f0-9]{64}$")
_MAX_STATE_BYTES = 8388608
_MAX_EVENT_BYTES = 65536
_MAX_LEDGER_BYTES = 16777216
_MAX_RECORDS = 4096
_MAX_SNAPSHOT_READ_BYTES = 268435456
_ZERO = "0" * 64
_LOCK_GUARD = threading.RLock()
_HELD_LOCKS: dict = {}


def _validate_json(value, *, depth=0, counter=None):
    if counter is None:
        counter = [0]
    counter[0] += 1
    if depth > 32 or counter[0] > 100000:
        raise SageError("STATE_LIMIT", "Structured state is too deeply nested or contains too many values.")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise SageError("INVALID_STATE", "State object keys must be strings.")
            _validate_json(child, depth=depth + 1, counter=counter)
    elif isinstance(value, list):
        for child in value:
            _validate_json(child, depth=depth + 1, counter=counter)
    elif isinstance(value, str) and len(value) > _MAX_STATE_BYTES:
        raise SageError("STATE_LIMIT", "A structured string exceeds the bounded state size.")
    elif value is not None and type(value) not in (str, int, float, bool):
        raise SageError("INVALID_STATE", "Only bounded JSON values can be persisted.")


def _canonical(value, limit):
    try:
        _validate_json(value)
        data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except SageError:
        raise
    except (TypeError, ValueError, UnicodeError, RecursionError, OverflowError):
        raise SageError("INVALID_STATE", "State must be finite, valid UTF-8 JSON.") from None
    if len(data) > limit:
        raise SageError("STATE_LIMIT", "Structured state exceeds its bounded byte limit.")
    return data


def _object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise SageError("INTEGRITY_ERROR", "Evidence contains duplicate JSON keys.")
        result[key] = value
    return result


def _parse(data):
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_object_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        _validate_json(value)
        return value
    except SageError:
        raise
    except (ValueError, UnicodeError, RecursionError):
        raise SageError("INTEGRITY_ERROR", "Evidence contains malformed or non-finite JSON.") from None


def _fsync_directory(directory: Path):
    # Windows does not expose a standard-library directory fsync; file fsync and
    # atomic same-directory replace remain used there, without a power-loss claim.
    if os.name != "nt":
        fd = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def _write_new(path: Path, data: bytes):
    _checked_absolute(path.parent)
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        _fsync_directory(path.parent)
    except OSError:
        raise SageError("STORE_WRITE", "A new private evidence file could not be written safely.") from None


class RunStore:
    def __init__(self, base):
        self.base = _checked_absolute(base, allow_missing=True)
        try:
            self.base.mkdir(parents=True, exist_ok=True, mode=0o700)
            _checked_absolute(self.base)
        except SageError:
            raise
        except OSError:
            raise SageError("STORE_WRITE", "The private state directory could not be prepared.") from None

    def run_dir(self, run_id) -> Path:
        if not isinstance(run_id, str) or not _RUN_ID.fullmatch(run_id):
            raise SageError("INVALID_RUN_ID", "A run identifier must be exactly 32 lowercase hexadecimal characters.")
        directory = self.base / run_id
        _checked_absolute(directory)
        return directory

    @contextmanager
    def lock(self, run_id):
        directory = self.run_dir(run_id)
        key = os.path.normcase(str(directory))
        owner = threading.get_ident()
        with _LOCK_GUARD:
            held = _HELD_LOCKS.get(key)
            if held is not None:
                if held["owner"] != owner:
                    raise SageError("RUN_LOCKED", "This run is already owned by another active controller.")
                held["depth"] += 1
            else:
                lockfile = directory / "run.lock"
                fd = None
                try:
                    if lockfile.exists() or lockfile.is_symlink():
                        existing = lockfile.lstat()
                        if _is_link(existing) or not stat.S_ISREG(existing.st_mode) or existing.st_nlink != 1 or existing.st_size not in (0, 1):
                            raise SageError("INTEGRITY_ERROR", "The run lock is not a valid single-link lock file.")
                    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
                    fd = os.open(lockfile, flags, 0o600)
                    info = os.fstat(fd)
                    if _is_link(info) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size not in (0, 1):
                        raise SageError("INTEGRITY_ERROR", "The run lock is not a valid single-link lock file.")
                    if info.st_size == 0:
                        os.write(fd, b"\0")
                        os.fsync(fd)
                    os.lseek(fd, 0, os.SEEK_SET)
                    if os.name == "nt":
                        import msvcrt
                        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    _HELD_LOCKS[key] = {"owner": owner, "depth": 1, "fd": fd}
                except SageError:
                    if fd is not None:
                        os.close(fd)
                    raise
                except OSError:
                    if fd is not None:
                        os.close(fd)
                    raise SageError("RUN_LOCKED", "The run lock is unavailable; no stale-lock takeover was attempted.") from None
        try:
            yield
        finally:
            with _LOCK_GUARD:
                held = _HELD_LOCKS[key]
                held["depth"] -= 1
                if held["depth"] == 0:
                    fd = held["fd"]
                    try:
                        os.lseek(fd, 0, os.SEEK_SET)
                        if os.name == "nt":
                            import msvcrt
                            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                        else:
                            import fcntl
                            fcntl.flock(fd, fcntl.LOCK_UN)
                    finally:
                        os.close(fd)
                        del _HELD_LOCKS[key]

    def create(self, manifest) -> str:
        if not isinstance(manifest, dict):
            raise SageError("INVALID_STATE", "Initial run state must be a JSON object.")
        _canonical(manifest, _MAX_STATE_BYTES)
        run_id = uuid.uuid4().hex
        directory = self.base / run_id
        try:
            directory.mkdir(mode=0o700)
            (directory / "checkpoints").mkdir(mode=0o700)
            _write_new(directory / "ledger.jsonl", b"")
            self.save(run_id, manifest)
            _fsync_directory(self.base)
        except SageError:
            raise
        except OSError:
            raise SageError("STORE_WRITE", "A private run directory could not be created.") from None
        return run_id

    def _records(self, run_id):
        directory = self.run_dir(run_id)
        ledger = _read_regular(directory / "ledger.jsonl", _MAX_LEDGER_BYTES)
        if ledger and not ledger.endswith(b"\n"):
            raise SageError("INTEGRITY_ERROR", "The ledger has a torn final record; evidence was not silently truncated.")
        records = []
        previous = _ZERO
        for line in ledger.splitlines():
            if len(records) >= _MAX_RECORDS or not line or len(line) > _MAX_EVENT_BYTES:
                raise SageError("INTEGRITY_ERROR", "The ledger exceeds record bounds or contains an empty record.")
            record = _parse(line)
            expected_keys = {"seq", "run_id", "timestamp", "event", "data", "previous_hash", "hash"}
            if not isinstance(record, dict) or set(record) != expected_keys:
                raise SageError("INTEGRITY_ERROR", "A ledger record has an invalid shape.")
            if type(record["seq"]) is not int or record["seq"] != len(records) + 1 or record["run_id"] != run_id or record["previous_hash"] != previous:
                raise SageError("INTEGRITY_ERROR", "Ledger ordering, ownership or hash-chain continuity failed.")
            if not isinstance(record["event"], str) or not _EVENT.fullmatch(record["event"]) or not isinstance(record["data"], dict):
                raise SageError("INTEGRITY_ERROR", "A ledger record contains an invalid event.")
            if not isinstance(record["timestamp"], str) or len(record["timestamp"]) > 40:
                raise SageError("INTEGRITY_ERROR", "A ledger record timestamp is invalid.")
            try:
                timestamp = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
                if timestamp.tzinfo is None:
                    raise ValueError()
            except ValueError:
                raise SageError("INTEGRITY_ERROR", "A ledger record timestamp is invalid.") from None
            digest = record["hash"]
            if not isinstance(digest, str) or not _HASH.fullmatch(digest):
                raise SageError("INTEGRITY_ERROR", "A ledger record hash is invalid.")
            unsigned = {key: value for key, value in record.items() if key != "hash"}
            if hashlib.sha256(_canonical(unsigned, _MAX_EVENT_BYTES)).hexdigest() != digest:
                raise SageError("INTEGRITY_ERROR", "Ledger content no longer matches its chained hash.")
            records.append(record)
            previous = digest
        return records

    def _checkpoint_states(self, run_id, records):
        latest = None
        total = 0
        directory = self.run_dir(run_id) / "checkpoints"
        _checked_absolute(directory)
        for record in records:
            if record["event"] != "checkpoint":
                continue
            data = record["data"]
            if set(data) != {"snapshot", "state_sha256", "snapshot_sha256"} or not isinstance(data["snapshot"], str) or not _SNAPSHOT.fullmatch(data["snapshot"]):
                raise SageError("INTEGRITY_ERROR", "A checkpoint reference has an invalid shape.")
            for field in ("state_sha256", "snapshot_sha256"):
                if not isinstance(data[field], str) or not _HASH.fullmatch(data[field]):
                    raise SageError("INTEGRITY_ERROR", "A checkpoint reference hash is invalid.")
            raw = _read_regular(directory / data["snapshot"], _MAX_STATE_BYTES + 4096)
            total += len(raw)
            if total > _MAX_SNAPSHOT_READ_BYTES:
                raise SageError("STATE_LIMIT", "Checkpoint history exceeds the bounded verification size.")
            if hashlib.sha256(raw).hexdigest() != data["snapshot_sha256"]:
                raise SageError("INTEGRITY_ERROR", "A checkpoint snapshot was modified after ledger commit.")
            snapshot = _parse(raw)
            if not isinstance(snapshot, dict) or set(snapshot) != {"version", "run_id", "state_sha256", "state"} or snapshot["version"] != 1 or snapshot["run_id"] != run_id or not isinstance(snapshot["state"], dict):
                raise SageError("INTEGRITY_ERROR", "A checkpoint snapshot has an invalid shape or owner.")
            actual = hashlib.sha256(_canonical(snapshot["state"], _MAX_STATE_BYTES)).hexdigest()
            if actual != data["state_sha256"] or snapshot["state_sha256"] != actual:
                raise SageError("INTEGRITY_ERROR", "Checkpoint state is not bound to the ledger.")
            latest = snapshot["state"]
        if latest is None:
            raise SageError("INTEGRITY_ERROR", "The run does not contain a committed checkpoint.")
        return latest

    def _append(self, run_id, event, data, records):
        if not isinstance(event, str) or not _EVENT.fullmatch(event) or not isinstance(data, dict):
            raise SageError("INVALID_EVENT", "Events require a short stable name and a JSON object.")
        if len(records) >= _MAX_RECORDS:
            raise SageError("STATE_LIMIT", "The ledger record budget is exhausted.")
        record = {
            "seq": len(records) + 1,
            "run_id": run_id,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "event": event,
            "data": data,
            "previous_hash": records[-1]["hash"] if records else _ZERO,
        }
        record["hash"] = hashlib.sha256(_canonical(record, _MAX_EVENT_BYTES)).hexdigest()
        encoded = _canonical(record, _MAX_EVENT_BYTES) + b"\n"
        directory = self.run_dir(run_id)
        ledger = directory / "ledger.jsonl"
        info = ledger.lstat()
        if _is_link(info) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise SageError("UNSAFE_LINK", "The ledger must remain a single-link regular file.")
        if info.st_size + len(encoded) > _MAX_LEDGER_BYTES:
            raise SageError("STATE_LIMIT", "The ledger byte budget is exhausted.")
        try:
            flags = os.O_WRONLY | os.O_APPEND | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(ledger, flags)
            with os.fdopen(fd, "ab", buffering=0) as stream:
                opened = os.fstat(stream.fileno())
                if (info.st_dev, info.st_ino) != (opened.st_dev, opened.st_ino) or opened.st_nlink != 1:
                    raise SageError("UNSAFE_LINK", "The ledger changed identity before append.")
                remaining = memoryview(encoded)
                while remaining:
                    count = stream.write(remaining)
                    if not count:
                        raise OSError()
                    remaining = remaining[count:]
                os.fsync(stream.fileno())
        except SageError:
            raise
        except OSError:
            raise SageError("STORE_WRITE", "The evidence record could not be durably appended.") from None
        return record

    def save(self, run_id, state):
        if not isinstance(state, dict):
            raise SageError("INVALID_STATE", "Run state must be a JSON object.")
        state_bytes = _canonical(state, _MAX_STATE_BYTES)
        state_hash = hashlib.sha256(state_bytes).hexdigest()
        with self.lock(run_id):
            records = self._records(run_id)
            if records:
                self._checkpoint_states(run_id, records)
            snapshot = {"version": 1, "run_id": run_id, "state_sha256": state_hash, "state": state}
            raw = _canonical(snapshot, _MAX_STATE_BYTES + 4096)
            if len(records) >= _MAX_RECORDS:
                raise SageError("STATE_LIMIT", "The ledger record budget is exhausted.")
            history_bytes = sum((self.run_dir(run_id) / "checkpoints" / record["data"]["snapshot"]).lstat().st_size
                                for record in records if record["event"] == "checkpoint")
            if history_bytes + len(raw) > _MAX_SNAPSHOT_READ_BYTES:
                raise SageError("STATE_LIMIT", "Checkpoint history would exceed its bounded verification size.")
            name = "cp-" + uuid.uuid4().hex + ".json"
            _write_new(self.run_dir(run_id) / "checkpoints" / name, raw)
            self._append(run_id, "checkpoint", {"snapshot": name, "state_sha256": state_hash, "snapshot_sha256": hashlib.sha256(raw).hexdigest()}, records)

    def load(self, run_id):
        with self.lock(run_id):
            return self._checkpoint_states(run_id, self._records(run_id))

    def event(self, run_id, event, data):
        if event == "checkpoint":
            raise SageError("INVALID_EVENT", "Checkpoint events are reserved for the state store.")
        with self.lock(run_id):
            records = self._records(run_id)
            self._checkpoint_states(run_id, records)
            return self._append(run_id, event, data, records)

    def events(self, run_id):
        with self.lock(run_id):
            records = self._records(run_id)
            self._checkpoint_states(run_id, records)
            return records

    def verify(self, run_id) -> bool:
        with self.lock(run_id):
            self._checkpoint_states(run_id, self._records(run_id))
            return True
