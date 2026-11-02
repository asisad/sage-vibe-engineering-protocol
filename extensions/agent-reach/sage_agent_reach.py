#!/usr/bin/env python3
"""SAGE / Deep Research Agent Reach adapter and local Obsidian report outbox.

Standard-library-only, explicit read-only invocations. This is not an MCP server,
a SAGE approval engine, a background daemon, or an OS security sandbox.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import time
from urllib.parse import quote, urlsplit, urlunsplit
from uuid import uuid4

SCHEMA = "sage-agent-reach/0.1"
VERSION = "0.1.0"
ACTIONS = {
    "github": {"search", "read"},
    "web": {"search", "read"},
    "v2ex": {"hot", "node", "read", "user"},
    "youtube": {"read", "search", "subtitle", "transcribe"},
    "bilibili": {"search", "read", "hot", "subtitle"},
    "reddit": {"search", "read", "subreddit"},
    "twitter": {"search", "profile", "tweets", "thread"},
    "facebook": {"search", "profile"},
    "instagram": {"search", "profile", "posts"},
    "xiaohongshu": {"search", "read", "comments"},
    "xueqiu": {"quote", "search", "hot_posts", "hot_stocks"},
    "boss": {"search", "read"},
    "linkedin": {"jobs", "read"},
    "xiaoyuzhou": {"transcribe"},
    "auto": {"read"},
}
STOP_CODES = {"PLATFORM_BLOCKED", "RATE_LIMITED", "NEED_LOGIN", "BUSY"}
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
SECRET = re.compile(
    r"(?i)(?:bearer\s+)[a-z0-9._~+/=-]{8,}"
    r"|(?:sk-[a-z0-9_-]{12,}|ghp_[a-z0-9]{16,}|github_pat_[a-z0-9_]{16,})"
    r"|(?:(?:password|api[_-]?key|access[_-]?token|refresh[_-]?token|cookie|secret)"
    r"\s*[=:]\s*)[^\s,;]+"
)
MAX_EVENTS = 300
MAX_ITEMS_IN_NOTE = 8
MAX_ITEMS_IN_RESPONSE = 50
MAX_STDOUT = 2_000_000
MAX_ANSWER = 40_000
MAX_TASK_BYTES = 2_500_000
MAX_ARG_CHARS = 4000
BEGIN = "<!-- AGENT-REACH:BEGIN:{key} -->"
END = "<!-- AGENT-REACH:END:{key} -->"


class AdapterError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def redact(value: object, limit: int = 2000) -> str:
    raw = str(value or "")[:limit]
    return SECRET.sub("[REDACTED]", raw)


def markdown(value: object, limit: int = 2000) -> str:
    # Untrusted page titles, snippets and answers are text, never Markdown instructions.
    value = redact(value, limit).replace("\r", " ").replace("\n", " ")
    return re.sub(r"([\\`*_[\]()<>{}!|#])", r"\\\1", value)


def public_url(value: object) -> str:
    try:
        parsed = urlsplit(str(value).strip())
        host = (parsed.hostname or "").lower().rstrip(".")
        if parsed.scheme not in {"https", "http"} or not host or parsed.username or parsed.password:
            return ""
        if host in {"localhost", "metadata.google.internal"} or host.endswith((".local", ".internal", ".lan")):
            return ""
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            ip = None
        if ip is not None and not ip.is_global:
            return ""
        if "." not in host and ip is None:
            return ""
        # Remove query and fragment; they can contain login tokens and tracking IDs.
        netloc = host if ":" not in host else f"[{host}]"
        if parsed.port is not None and parsed.port not in (80, 443):
            netloc += f":{parsed.port}"
        return urlunsplit((parsed.scheme, netloc, quote(parsed.path or "/", safe="/-._~:@+%="), "", ""))
    except (ValueError, TypeError):
        return ""


def clean_identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise AdapterError("INVALID_INPUT", f"{label} must be a 1-80 character ASCII identifier.")
    return value


def relative_folder(value: str) -> Path:
    value = value.replace("\\", "/")
    parts = value.split("/")
    if not value or value.startswith("/") or any(p in ("", ".", "..") or ":" in p for p in parts):
        raise AdapterError("INVALID_PATH", "The report folder must be a safe vault-relative path.")
    if any(not re.fullmatch(r"[\w ._-]{1,80}", p, flags=re.UNICODE) for p in parts):
        raise AdapterError("INVALID_PATH", "Unsupported characters in report folder.")
    return Path(*parts)


def no_link_parts(path: Path) -> None:
    for part in (path, *path.parents):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or (
            getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        ):
            raise AdapterError("UNSAFE_PATH", "Symlinks and reparse points are not supported for report paths.")


def ensure_private(path: Path) -> None:
    no_link_parts(path)
    was_missing = not path.exists()
    path.mkdir(parents=True, exist_ok=True)
    if os.name != "nt" and was_missing:
        path.chmod(0o700)


def atomic_text(path: Path, content: str, *, private: bool = True) -> None:
    if len(content.encode("utf-8")) > MAX_TASK_BYTES:
        raise AdapterError("REPORT_LIMIT", "Report exceeds the bounded size limit.")
    if private:
        ensure_private(path.parent)
    else:
        no_link_parts(path.parent)
        path.parent.mkdir(parents=True, exist_ok=True)
    no_link_parts(path)
    temp = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        with temp.open("x", encoding="utf-8", newline="\n") as f:
            if os.name != "nt" and private:
                os.chmod(temp, 0o600)
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def save_json(path: Path, data: dict) -> None:
    atomic_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def load_json(path: Path) -> dict:
    no_link_parts(path)
    if not path.is_file():
        return {}
    if path.stat().st_size > MAX_TASK_BYTES:
        raise AdapterError("REPORT_LIMIT", "Stored report exceeds the read limit.")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise AdapterError("INVALID_STATE", "Expected a JSON object.")
    return data


def state_root(value: str | None) -> Path:
    root = Path(value).expanduser() if value else Path.home() / ".sage" / "agent-reach"
    if not root.is_absolute():
        raise AdapterError("INVALID_PATH", "State root must be absolute.")
    # Never write evidence into the public SAGE source checkout.
    source = Path(__file__).resolve().parents[2]
    if root.resolve() == source or source in root.resolve().parents:
        raise AdapterError("INVALID_PATH", "State root cannot be inside the SAGE source tree.")
    no_link_parts(root)
    return root


@contextmanager
def locked(root: Path):
    ensure_private(root)
    lock = root / ".writer.lock"
    deadline = time.monotonic() + 5
    while True:
        try:
            fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.close(fd)
            break
        except FileExistsError:
            no_link_parts(lock)
            if time.monotonic() >= deadline:
                raise AdapterError("REPORT_BUSY", "Local report writer is busy.")
            time.sleep(0.04)
    try:
        yield
    finally:
        lock.unlink(missing_ok=True)


def task_key(agent: str, task: str) -> str:
    return hashlib.sha256((agent + "\0" + task).encode("utf-8")).hexdigest()[:24]


def task_file(root: Path, agent: str, task: str) -> Path:
    return root / "tasks" / (task_key(agent, task) + ".json")


def append_record(root: Path, agent: str, task: str, event: dict | None = None,
                  *, answer: str | None = None, title: str | None = None,
                  confidence: str | None = None) -> dict:
    with locked(root):
        path = task_file(root, agent, task)
        doc = load_json(path)
        if not doc:
            doc = {"schema_version": SCHEMA, "task_id": task, "agent_id": agent,
                   "created_at": now(), "updated_at": now(), "title": task,
                   "events": [], "answer": "", "confidence": "unverified",
                   "dropped_events": 0, "synced_digest": ""}
        if doc.get("task_id") != task or doc.get("agent_id") != agent:
            raise AdapterError("INVALID_STATE", "Report identity does not match its stored file.")
        if event:
            if not any(e.get("event_id") == event["event_id"] for e in doc["events"]):
                if len(doc["events"]) >= MAX_EVENTS:
                    doc["dropped_events"] += 1
                else:
                    doc["events"].append(event)
        if answer is not None:
            doc["answer"] = redact(answer, MAX_ANSWER)
            doc["finished_at"] = now()
        if title:
            doc["title"] = redact(title, 160)
        if confidence:
            if confidence not in {"high", "medium", "low", "unverified"}:
                raise AdapterError("INVALID_INPUT", "Unsupported confidence classification.")
            doc["confidence"] = confidence
        doc["updated_at"] = now()
        save_json(path, doc)
        return doc


def snippet_items(items: list) -> list:
    result = []
    for item in items[:MAX_ITEMS_IN_NOTE]:
        if not isinstance(item, dict):
            continue
        body = str(item.get("text") or "")
        result.append({"title": redact(item.get("title"), 180),
                       "url": public_url(item.get("url")),
                       "author": redact(item.get("author"), 80),
                       "published_at": redact(item.get("published_at"), 50),
                       "excerpt": redact(body, 250),
                       "text_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest()})
    return result


def normalized_result(result: dict) -> dict:
    items = []
    source_items = result.get("items") if isinstance(result.get("items"), list) else []
    for item in source_items[:MAX_ITEMS_IN_RESPONSE]:
        if not isinstance(item, dict):
            continue
        items.append({"title": redact(item.get("title"), 200),
                      "url": public_url(item.get("url")),
                      "author": redact(item.get("author"), 100),
                      "published_at": redact(item.get("published_at"), 100),
                      "text": redact(item.get("text"), 12_000)})
    err = result.get("error") if isinstance(result.get("error"), dict) else {}
    return {"ok": result.get("ok") is True,
            "channel": result.get("channel"), "action": result.get("action"),
            "backend": result.get("backend"), "items": items,
            "total_returned": len(source_items), "items_truncated": len(source_items) > len(items),
            "error": ({"code": redact(err.get("code"), 100),
                       "message": redact(err.get("message"), 500)} if err else None)}


def report_content(doc: dict) -> str:
    key = task_key(doc["agent_id"], doc["task_id"])
    meta = {"task_id": doc["task_id"], "agent_id": doc["agent_id"],
            "created_at": doc["created_at"], "updated_at": doc["updated_at"],
            "status": "completed" if doc.get("finished_at") else "running",
            "confidence": doc.get("confidence", "unverified")}
    lines = [BEGIN.format(key=key), "---", 'type: "agent-reach-research"',
             'schema_version: "sage-agent-reach/0.1"']
    lines += [f'{k}: {json.dumps(str(v), ensure_ascii=False)}' for k, v in meta.items()]
    lines += ["---", f"# {markdown(doc.get('title'), 160)}", "",
              f"- Task: `{doc['task_id']}`", f"- Agent: `{doc['agent_id']}`",
              f"- Created (UTC): {doc['created_at']}",
              f"- Updated (UTC): {doc['updated_at']}",
              f"- Confidence: {doc.get('confidence', 'unverified')}", "",
              "## Research activity", ""]
    for i, event in enumerate(doc.get("events", []), start=1):
        label = "SUCCESS" if event.get("ok") else markdown(event.get("error_code") or "FAILED", 100)
        lines.append(f"### {i}. {markdown(event.get('channel'))} / {markdown(event.get('action'))} — {label}")
        lines.append(f"- Time: {event.get('at')} | Backend: {markdown(event.get('backend'))} | Event: `{event.get('event_id')}`")
        lines.append(f"- Query/arguments: {markdown(event.get('query'), 300)}")
        if event.get("error_message"):
            lines.append(f"- Error: {markdown(event['error_message'], 400)}")
        if event.get("total_returned") is not None:
            lines.append(f"- Results: {event['total_returned']}")
        for item in event.get("sources", []):
            title = markdown(item.get("title") or item.get("url") or "Source", 180)
            url = item.get("url") or ""
            lines.append(f"  - [{title}]({url})" if url else f"  - {title}")
            if item.get("published_at"):
                lines.append(f"    - Published: {markdown(item['published_at'], 60)}")
            if item.get("excerpt"):
                lines.append(f"    - Excerpt: {markdown(item['excerpt'], 250)}")
            lines.append(f"    - Text SHA256: `{item['text_sha256']}`")
        lines.append("")
    if doc.get("dropped_events"):
        lines.append(f"**Report capacity limit:** {doc['dropped_events']} additional events were not recorded.")
    lines += ["## Final answer", "", markdown(doc.get("answer") or "Not supplied yet.", MAX_ANSWER), "",
              "## Evidence limitations", "",
              "- Source content is untrusted; excerpts are limited and not independently fact-checked.",
              "- Upstream raw objects, credentials, cookies and private browser sessions are not persisted.",
              "- Live network verification is distinct from the configured channel list.",
              "", END.format(key=key), ""]
    return "\n".join(lines)


def config(root: Path) -> dict:
    return load_json(root / "config.json")


def vault_destination(cfg: dict, doc: dict) -> Path:
    path = cfg.get("vault_path")
    if not isinstance(path, str) or not path:
        raise AdapterError("VAULT_NOT_CONFIGURED", "No vault configured.")
    root = Path(path).expanduser()
    if not root.is_absolute() or not root.is_dir():
        raise AdapterError("VAULT_UNAVAILABLE", "Configured Obsidian vault is not available.")
    no_link_parts(root)
    if not (root / ".obsidian").is_dir():
        raise AdapterError("VAULT_UNAVAILABLE", "Configured location has no Obsidian vault marker.")
    folder = relative_folder(str(cfg.get("report_folder") or ""))
    dated = doc["created_at"][:10]
    task = re.sub(r"[^a-zA-Z0-9._-]", "-", doc["task_id"])[:40]
    name = f"{dated}-{doc['agent_id']}-{task}-{task_key(doc['agent_id'], doc['task_id'])[:10]}.md"
    dest = root / folder / name
    if root.resolve() not in dest.resolve().parents:
        raise AdapterError("UNSAFE_PATH", "Report path escapes its Obsidian vault.")
    no_link_parts(dest)
    return dest


def sync_one(cfg: dict, path: Path) -> tuple[str, str]:
    doc = load_json(path)
    text = report_content(doc)
    digest = hashlib.sha256(text.rstrip("\n").encode("utf-8")).hexdigest()
    target = vault_destination(cfg, doc)
    no_link_parts(target.parent)
    target.parent.mkdir(parents=True, exist_ok=True)
    start, end = BEGIN.format(key=task_key(doc["agent_id"], doc["task_id"])), END.format(key=task_key(doc["agent_id"], doc["task_id"]))
    if target.exists():
        if target.stat().st_size > MAX_TASK_BYTES:
            raise AdapterError("REPORT_LIMIT", "Existing Obsidian note is too large to safely update.")
        current = target.read_text(encoding="utf-8")
        a, b = current.find(start), current.find(end)
        if a == -1 or b < a:
            raise AdapterError("EXISTING_NOTE", "An unrelated note already occupies this path.")
        b += len(end)
        current_managed = current[a:b]
        old_digest = hashlib.sha256(current_managed.rstrip("\n").encode("utf-8")).hexdigest()
        if doc.get("synced_digest") and old_digest != doc["synced_digest"]:
            raise AdapterError("MANAGED_NOTE_MODIFIED", "The managed region was edited outside the adapter.")
        if doc.get("synced_digest") == digest and old_digest == digest:
            return "ALREADY_SYNCED", str(target)
        if not doc.get("synced_digest"):
            raise AdapterError("EXISTING_NOTE", "Cannot take ownership of an existing note.")
        text = current[:a] + text.rstrip("\n") + current[b:]
    atomic_text(target, text, private=False)
    doc["synced_digest"] = digest
    # Caller owns the lock; the JSON is saved separately from note writing.
    save_json(path, doc)
    return "SYNCED", str(target)


def sync_reports(root: Path, limit: int = 10, focus: Path | None = None) -> dict:
    cfg = config(root)
    if not cfg.get("vault_path"):
        return {"status": "PENDING", "reason": "VAULT_NOT_CONFIGURED", "synced": 0}
    paths = sorted((root / "tasks").glob("*.json")) if (root / "tasks").is_dir() else []
    synced, already, failed, last = 0, 0, 0, ""
    batch_size = max(1, min(limit, 100))
    with locked(root):
        cursor_path = root / "sync-cursor.json"
        cursor = int(load_json(cursor_path).get("index", 0))
        rotated = paths[cursor % len(paths):] + paths[:cursor % len(paths)] if paths else []
        if focus in rotated:
            rotated.remove(focus)
            rotated.insert(0, focus)
        for path in rotated[:batch_size]:
            try:
                outcome, destination = sync_one(cfg, path)
                synced += int(outcome == "SYNCED")
                already += int(outcome == "ALREADY_SYNCED")
                last = destination
            except (AdapterError, OSError, UnicodeError, ValueError) as exc:
                failed += 1
                last = exc.code if isinstance(exc, AdapterError) else "VAULT_WRITE_FAILED"
        if paths:
            save_json(cursor_path, {"index": (cursor + batch_size) % len(paths)})
    status = "SYNCED" if failed == 0 and len(paths) <= batch_size else "PENDING"
    return {"status": status, "synced": synced, "already_synced": already,
            "failed": failed, "queued": max(0, len(paths) - batch_size), "last": last}


def wrap_result(status: str, result: dict | None = None, report: dict | None = None,
                error: dict | None = None, request_id: str | None = None) -> dict:
    return {"schema_version": SCHEMA, "request_id": request_id or uuid4().hex,
            "status": status, "result": result, "report": report,
            "error": error}


def parse_params(raw: str, channel: str, action: str) -> list[str]:
    try:
        params = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AdapterError("INVALID_INPUT", "params-json must be valid JSON.") from exc
    if not isinstance(params, list) or len(params) > 16 or any(
        not isinstance(p, str) or len(p) > MAX_ARG_CHARS or "\x00" in p for p in params
    ):
        raise AdapterError("INVALID_INPUT", "Expected up to 16 short string parameters.")
    if channel == "auto":
        if len(params) != 1 or not public_url(params[0]):
            raise AdapterError("INVALID_URL", "Auto read requires exactly one public HTTP(S) URL.")
    if action in {"read", "subtitle", "transcribe"} and params and "//" in params[0]:
        if not public_url(params[0]):
            raise AdapterError("INVALID_URL", "Only public HTTP(S) links are allowed.")
    return params


def invoke(args: argparse.Namespace, root: Path) -> tuple[int, dict]:
    clean_identifier(args.task_id, "task-id")
    clean_identifier(args.agent, "agent")
    clean_identifier(args.authority_ref, "authority-ref")
    if not args.live:
        raise AdapterError("LIVE_OPT_IN_REQUIRED", "Live internet access requires --live.")
    if args.channel not in ACTIONS or args.action not in ACTIONS[args.channel]:
        raise AdapterError("ACTION_DENIED", "Only declared Agent Reach 1.6 read/search actions are permitted.")
    params = parse_params(args.params_json, args.channel, args.action)
    exe = shutil.which("agent-reach")
    if not exe:
        raise AdapterError("TOOL_UNAVAILABLE", "agent-reach executable is not on PATH.")
    command = [exe, "read", *params] if args.channel == "auto" else [exe, args.channel, args.action, *params]
    request_id = uuid4().hex
    recorded_at = now()
    started = time.monotonic()
    raw: dict
    try:
        completed = subprocess.run(command, capture_output=True, encoding="utf-8", errors="replace",
                                   timeout=args.timeout, check=False)
        if len(completed.stdout.encode("utf-8")) > MAX_STDOUT:
            raise AdapterError("UPSTREAM_LIMIT", "Upstream JSON exceeded the response limit.")
        try:
            raw = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise AdapterError("INVALID_UPSTREAM_JSON", "Agent Reach did not return valid JSON.") from exc
        if not isinstance(raw, dict) or not isinstance(raw.get("ok"), bool):
            raise AdapterError("INVALID_UPSTREAM_JSON", "Agent Reach response lacks expected ok value.")
        normalized = normalized_result(raw)
        code = (normalized.get("error") or {}).get("code")
        status = "SUCCESS" if normalized["ok"] else "BLOCKED" if code in STOP_CODES else "UPSTREAM_ERROR"
        rc = 0 if status == "SUCCESS" else 2
    except subprocess.TimeoutExpired:
        normalized = {"ok": False, "channel": args.channel, "action": args.action,
                      "backend": None, "items": [], "total_returned": 0,
                      "error": {"code": "TIMEOUT", "message": "Agent Reach invocation timed out."}}
        status, rc = "UPSTREAM_ERROR", 2
    except (OSError, AdapterError) as exc:
        code = exc.code if isinstance(exc, AdapterError) else "EXECUTION_FAILED"
        normalized = {"ok": False, "channel": args.channel, "action": args.action,
                      "backend": None, "items": [], "total_returned": 0,
                      "error": {"code": code, "message": redact(str(exc), 300)}}
        status, rc = "UPSTREAM_ERROR", 2
    err = normalized.get("error") or {}
    event = {"event_id": args.event_id or request_id, "at": recorded_at,
             "channel": args.channel, "action": args.action,
             "backend": normalized.get("backend"), "ok": normalized["ok"],
             "authority_ref": args.authority_ref,
             "query": redact(" ".join(params), 300), "error_code": err.get("code"),
             "error_message": err.get("message"),
             "duration_ms": round((time.monotonic() - started) * 1000),
             "total_returned": normalized.get("total_returned"),
             "sources": snippet_items(normalized["items"])}
    try:
        append_record(root, args.agent, args.task_id, event, title=args.title)
        report = sync_reports(root, limit=10, focus=task_file(root, args.agent, args.task_id))
    except (AdapterError, OSError, ValueError) as exc:
        report = {"status": "PENDING", "reason": exc.code if isinstance(exc, AdapterError) else "LOCAL_REPORT_WRITE_FAILED"}
    return rc, wrap_result(status, normalized, report, request_id=request_id)


def finalize(args: argparse.Namespace, root: Path) -> dict:
    clean_identifier(args.task_id, "task-id")
    clean_identifier(args.agent, "agent")
    if not args.answer_file:
        raise AdapterError("INVALID_INPUT", "finalize requires --answer-file.")
    file = Path(args.answer_file).expanduser()
    no_link_parts(file)
    if not file.is_file() or file.stat().st_size > MAX_ANSWER * 4:
        raise AdapterError("INVALID_INPUT", "Answer file is missing or too large.")
    answer = file.read_text(encoding="utf-8")
    if len(answer) > MAX_ANSWER:
        raise AdapterError("REPORT_LIMIT", "Answer text exceeds the report limit.")
    append_record(root, args.agent, args.task_id, answer=answer, title=args.title,
                  confidence=args.confidence)
    report = sync_reports(root, limit=10, focus=task_file(root, args.agent, args.task_id))
    return wrap_result("RECORDED", {"task_id": args.task_id, "agent": args.agent}, report)


def configure_vault(args: argparse.Namespace, root: Path) -> dict:
    folder = relative_folder(args.folder)
    vault = Path(args.vault).expanduser()
    if not vault.is_absolute() or not vault.is_dir():
        raise AdapterError("VAULT_UNAVAILABLE", "Supply an existing absolute Obsidian vault path.")
    no_link_parts(vault)
    if not (vault / ".obsidian").is_dir():
        raise AdapterError("VAULT_UNAVAILABLE", "This folder has no .obsidian directory.")
    if root.resolve() == vault.resolve() or vault.resolve() in root.resolve().parents:
        raise AdapterError("INVALID_PATH", "Local outbox must not be inside the vault.")
    with locked(root):
        save_json(root / "config.json", {"vault_path": str(vault.resolve()),
                                         "report_folder": folder.as_posix(),
                                         "configured_at": now()})
    return wrap_result("CONFIGURED", {"vault": str(vault.resolve()), "folder": folder.as_posix()},
                       {"status": "PENDING", "reason": "Run sync or the next instrumented call."})


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Read-only Agent Reach adapter for SAGE and Deep Research")
    p.add_argument("--json", action="store_true", help="Output is always JSON")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("status", "invoke", "finalize", "configure-vault", "sync"):
        x = sub.add_parser(name)
        x.add_argument("--state-dir", help="Absolute private outbox directory (default ~/.sage/agent-reach)")
        if name == "invoke":
            x.add_argument("--task-id", required=True)
            x.add_argument("--agent", required=True, help="sage or deep-research (or another agent ID)")
            x.add_argument("--authority-ref", required=True, help="Upstream decision/approval reference; not an authorization grant")
            x.add_argument("--channel", required=True, choices=sorted(ACTIONS))
            x.add_argument("--action", required=True)
            x.add_argument("--params-json", default="[]")
            x.add_argument("--timeout", type=int, default=45)
            x.add_argument("--event-id")
            x.add_argument("--title")
            x.add_argument("--live", action="store_true")
        if name == "finalize":
            x.add_argument("--task-id", required=True)
            x.add_argument("--agent", required=True)
            x.add_argument("--answer-file", required=True)
            x.add_argument("--title")
            x.add_argument("--confidence", choices=("high", "medium", "low", "unverified"), default="unverified")
        if name == "configure-vault":
            x.add_argument("--vault", required=True)
            x.add_argument("--folder", required=True)
        if name == "sync":
            x.add_argument("--limit", type=int, default=10)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        root = state_root(args.state_dir)
        if args.command == "status":
            pending = len(list((root / "tasks").glob("*.json"))) if (root / "tasks").is_dir() else 0
            cfg = config(root)
            reply = wrap_result("READY_TO_CONFIGURE" if shutil.which("agent-reach") else "TOOL_UNAVAILABLE",
                                {"version": VERSION, "reach_executable": shutil.which("agent-reach"),
                                 "vault_configured": bool(cfg.get("vault_path")), "task_records": pending,
                                 "live_by_default": False, "agent_reach_version_verified": False})
            code = 0
        elif args.command == "invoke":
            if not 1 <= args.timeout <= 300:
                raise AdapterError("INVALID_INPUT", "Timeout must be between 1 and 300 seconds.")
            if args.event_id:
                clean_identifier(args.event_id, "event-id")
            code, reply = invoke(args, root)
        elif args.command == "finalize":
            reply, code = finalize(args, root), 0
        elif args.command == "configure-vault":
            reply, code = configure_vault(args, root), 0
        else:
            reply, code = wrap_result("REPORT_STATUS", sync_reports(root, limit=args.limit)), 0
    except (AdapterError, OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        reason = exc.code if isinstance(exc, AdapterError) else "ADAPTER_ERROR"
        reply = wrap_result("BLOCKED", error={"code": reason, "message": redact(str(exc), 180)})
        code = 2
    print(json.dumps(reply, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
