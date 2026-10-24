"""Bounded source-data validation; generated files never grant runtime authority."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import stat
import unicodedata
import uuid


class SageError(Exception):
    """A classified error whose message may safely be shown to a user."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


@dataclass
class Policy:
    max_model_calls: int = 12
    max_repairs: int = 2
    max_seconds: int = 900
    max_file_bytes: int = 131072
    max_project_bytes: int = 2097152
    max_files: int = 64
    max_context_bytes: int = 131072

    def __post_init__(self):
        bounds = {
            "max_model_calls": (1, 12),
            "max_repairs": (0, 8),
            "max_seconds": (1, 3600),
            "max_file_bytes": (1, 1048576),
            "max_project_bytes": (1, 16777216),
            "max_files": (1, 256),
            "max_context_bytes": (1, 1048576),
        }
        for field, (minimum, maximum) in bounds.items():
            value = getattr(self, field)
            if type(value) is not int or not minimum <= value <= maximum:
                raise SageError("INVALID_POLICY", f"{field} must be an integer between {minimum} and {maximum}.")
        if self.max_file_bytes > self.max_project_bytes:
            raise SageError("INVALID_POLICY", "The per-file limit cannot exceed the project limit.")


_PROTECTED = {
    ".git", ".sage", ".codex", ".claude", ".agents", ".github", ".gitlab",
    ".ssh", ".aws", ".azure", ".config", ".kube", ".gnupg", "hooks",
    "credentials", "credentials.json", "credentials.ini", "secrets.json",
    "secrets.yaml", "secrets.yml", ".npmrc", ".pypirc", ".netrc",
    ".gitconfig", ".gitmodules", ".gitattributes", "agents.md", "claude.md",
    "authorized_keys", "known_hosts", "id_rsa", "id_ed25519", "id_ecdsa",
    "desktop.ini", "ntuser.dat", "powershell_profile.ps1", "profile.ps1", ".sage-workspace.json",
    "docker-compose.override.yml",
}
_DEVICE = re.compile(r"^(?:con|prn|aux|nul|clock\$|conin\$|conout\$|com[1-9¹²³]|lpt[1-9¹²³])(?:\.|$)", re.I)
_SHORT_ALIAS = re.compile(r"~[0-9]+(?:\.|$)")
_BIDI = frozenset("\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069")
_SECRET_PATTERNS = (
    re.compile(r"\bsk-(?:or-v1-|ant-api\d+-)?[A-Za-z0-9_-]{20,}"),
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
    re.compile(r"\bAIza[A-Za-z0-9_-]{20,}"),
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----"),
)
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)[\"']?(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password|secret[_-]?key)[\"']?\s*[:=]\s*[\"']([^\"'\r\n]{8,512})[\"']"
)
_PLACEHOLDER = re.compile(r"(?i)(?:example|placeholder|changeme|your[_ -]|redacted|dummy|test|not[_ -]|fake|\$\{|<|process\.env|os\.environ)")


def safe_relative(value: str) -> str:
    """Validate a portable, exact POSIX relative source path (never normalize it)."""
    if not isinstance(value, str) or not value or len(value) > 240:
        raise SageError("UNSAFE_PATH", "A source path must be a nonempty relative POSIX path of at most 240 characters.")
    if value.startswith("/") or "\\" in value or any(c in value for c in ':<>"|?*'):
        raise SageError("UNSAFE_PATH", "Absolute paths, Windows aliases, streams and wildcard paths are not accepted.")
    if any(ord(c) < 32 or 127 <= ord(c) <= 159 or 0xD800 <= ord(c) <= 0xDFFF or c in _BIDI for c in value):
        raise SageError("UNSAFE_PATH", "Control characters and bidirectional path overrides are not accepted.")
    if unicodedata.normalize("NFC", value) != value:
        raise SageError("UNSAFE_PATH", "Source paths must use canonical Unicode spelling.")
    parts = value.split("/")
    if len(parts) > 16:
        raise SageError("UNSAFE_PATH", "Source paths are limited to 16 components.")
    for part in parts:
        folded = part.casefold()
        if not part or part in (".", "..") or part != part.strip() or part.endswith("."):
            raise SageError("UNSAFE_PATH", "Empty, traversal, trailing-dot and whitespace path aliases are not accepted.")
        if len(part) > 100 or _DEVICE.match(part) or _SHORT_ALIAS.search(part):
            raise SageError("UNSAFE_PATH", "Device names, DOS short-name aliases and oversized filename components are not accepted.")
        if folded in _PROTECTED or folded == ".env" or folded.startswith(".env.") or folded.endswith((".pem", ".key", ".p12", ".pfx")):
            raise SageError("PROTECTED_PATH", "Generated source cannot change runtime controls, credentials, hooks or private keys.")
    return value


def _reject_credentials(text: str) -> None:
    if any(pattern.search(text) for pattern in _SECRET_PATTERNS):
        raise SageError("CREDENTIAL_DETECTED", "A recognizable credential or private key was rejected; its value is not logged.")
    for match in _SECRET_ASSIGNMENT.finditer(text):
        if not _PLACEHOLDER.search(match.group(1)):
            raise SageError("CREDENTIAL_DETECTED", "A literal credential assignment was rejected; use an external credential reference.")


def _is_link(info: os.stat_result) -> bool:
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def reject_links(value: os.PathLike | str) -> Path:
    """Check an absolute file/directory and every existing ancestor without resolving links."""
    try:
        path = Path(value)
    except (TypeError, ValueError):
        raise SageError("UNSAFE_PATH", "A valid absolute filesystem path is required.") from None
    if not path.is_absolute() or ".." in path.parts:
        raise SageError("UNSAFE_PATH", "An explicit absolute path is required.")
    for component in reversed((path, *path.parents)):
        try:
            info = component.lstat()
        except FileNotFoundError:
            continue
        except OSError:
            raise SageError("FILE_ACCESS", "A path could not be inspected safely.") from None
        if _is_link(info):
            raise SageError("UNSAFE_LINK", "Symlinks, junctions and reparse points are not accepted.")
        if component != path and not stat.S_ISDIR(info.st_mode):
            raise SageError("UNSAFE_PATH", "A path ancestor is not a regular directory.")
        if component == path and not (stat.S_ISDIR(info.st_mode) or (stat.S_ISREG(info.st_mode) and info.st_nlink == 1)):
            raise SageError("UNSAFE_LINK", "A path must identify a regular, single-link file or directory.")
    return path


def _checked_absolute(value: os.PathLike | str, *, allow_missing: bool = False) -> Path:
    try:
        path = Path(value)
    except (TypeError, ValueError):
        raise SageError("UNSAFE_WORKSPACE", "A valid absolute directory path is required.") from None
    if not path.is_absolute() or path.parent == path or ".." in path.parts:
        raise SageError("UNSAFE_WORKSPACE", "An explicit absolute, non-root directory is required.")
    # Do not resolve first: resolution would erase evidence of a symlink/junction.
    for component in reversed((path, *path.parents)):
        try:
            info = component.lstat()
        except FileNotFoundError:
            if allow_missing:
                continue
            raise SageError("MISSING_DIRECTORY", "A required directory does not exist.") from None
        except OSError:
            raise SageError("FILE_ACCESS", "A directory ancestor could not be inspected safely.") from None
        if _is_link(info):
            raise SageError("UNSAFE_LINK", "Symlinks, junctions and reparse points are not accepted.")
        if not stat.S_ISDIR(info.st_mode):
            raise SageError("UNSAFE_WORKSPACE", "A workspace ancestor is not a regular directory.")
    return path


def _read_regular(path: Path, limit: int) -> bytes:
    try:
        before = path.lstat()
        if _is_link(before) or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise SageError("UNSAFE_LINK", "Only single-link regular files may be read or replaced.")
        if before.st_size > limit:
            raise SageError("SIZE_LIMIT", "A file exceeds the permitted byte limit.")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1 or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
                raise SageError("UNSAFE_LINK", "A file changed identity during validation.")
            data = stream.read(limit + 1)
        if len(data) > limit:
            raise SageError("SIZE_LIMIT", "A file exceeds the permitted byte limit.")
        return data
    except SageError:
        raise
    except OSError:
        raise SageError("FILE_ACCESS", "A regular file could not be read safely.") from None


def project_manifest(workspace: os.PathLike | str) -> list[dict]:
    """Hash a bounded project tree, excluding only its root-level .git metadata."""
    root = _checked_absolute(workspace, allow_missing=True)
    if not root.exists():
        return []
    manifest = []
    total = 0
    directories = 0
    discovered_directories = 0
    pending = [(root, "")]
    names = set()
    while pending:
        directory, prefix = pending.pop()
        _checked_absolute(directory)
        directories += 1
        if directories > 512:
            raise SageError("SIZE_LIMIT", "The project contains too many directories.")
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    relative = f"{prefix}/{entry.name}" if prefix else entry.name
                    info = entry.stat(follow_symlinks=False)
                    if _is_link(info):
                        raise SageError("UNSAFE_LINK", "A project contains an unexpected symlink or reparse point.")
                    if prefix == "" and entry.name in (".git", ".sage-workspace.json"):
                        # Windows scandir metadata can omit the hardlink count;
                        # obtain the full lstat before checking this excluded leaf.
                        info = Path(entry.path).lstat()
                        if _is_link(info) or not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)) or (stat.S_ISREG(info.st_mode) and info.st_nlink != 1):
                            raise SageError("UNSAFE_LINK", "Git metadata must not be a link or special file.")
                        if entry.name.casefold() == ".sage-workspace.json" and not stat.S_ISREG(info.st_mode):
                            raise SageError("PROTECTED_PATH", "The controller owner marker must be a regular file.")
                        continue
                    safe_relative(relative)
                    if relative.casefold() in names:
                        raise SageError("DUPLICATE_PATH", "Case-alias source paths are not portable or safe.")
                    names.add(relative.casefold())
                    if stat.S_ISDIR(info.st_mode):
                        discovered_directories += 1
                        if discovered_directories > 511:
                            raise SageError("SIZE_LIMIT", "The project contains too many directories.")
                        pending.append((Path(entry.path), relative))
                        continue
                    if not stat.S_ISREG(info.st_mode):
                        raise SageError("SPECIAL_FILE", "A project may contain only normal directories and source files.")
                    if len(manifest) >= 256:
                        raise SageError("SIZE_LIMIT", "The project contains too many files.")
                    data = _read_regular(Path(entry.path), 1048576)
                    total += len(data)
                    if total > 16777216:
                        raise SageError("SIZE_LIMIT", "The project exceeds the bounded inspection size.")
                    try:
                        source = data.decode("utf-8")
                    except UnicodeDecodeError:
                        raise SageError("INVALID_SOURCE", "Only UTF-8 source files are accepted by this runtime.") from None
                    _reject_credentials(source)
                    manifest.append({"path": relative, "sha256": hashlib.sha256(data).hexdigest(), "size_bytes": len(data)})
        except SageError:
            raise
        except OSError:
            raise SageError("FILE_ACCESS", "A project directory could not be inspected safely.") from None
    return sorted(manifest, key=lambda record: record["path"])


def _atomic_project_write(path: Path, data: bytes, root: Path) -> None:
    _checked_absolute(root)
    _checked_absolute(path.parent)
    if path.exists() or path.is_symlink():
        _read_regular(path, 1048576)
    temp = path.parent / (".sage-write-" + uuid.uuid4().hex)
    fd = None
    try:
        fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(fd, "wb") as stream:
            fd = None
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        _checked_absolute(path.parent)
        if path.exists() or path.is_symlink():
            _read_regular(path, 1048576)
        os.replace(temp, path)
    except SageError:
        raise
    except OSError:
        raise SageError("FILE_WRITE", "A validated source file could not be written atomically.") from None
    finally:
        if fd is not None:
            os.close(fd)
        # Only a runtime-created temporary file is removed; never project source.
        try:
            temp.unlink(missing_ok=True)
        except OSError:
            pass


def _prepare_project_files(workspace: os.PathLike | str, files: list[dict], policy: Policy):
    """Validate the complete intended mutation without creating files/directories."""
    if not isinstance(policy, Policy):
        raise SageError("INVALID_POLICY", "A validated Policy is required.")
    policy.__post_init__()  # Reject mutation of a formerly valid policy.
    root = _checked_absolute(workspace, allow_missing=True)
    if not isinstance(files, list) or not files or len(files) > policy.max_files:
        raise SageError("INVALID_FILES", "Source packets must be a bounded, nonempty list.")
    existing = project_manifest(root)
    current = {record["path"]: record for record in existing}
    aliases = {record["path"].casefold(): record["path"] for record in existing}
    prepared = []
    supplied = set()
    for packet in files:
        if not isinstance(packet, dict) or set(packet) != {"path", "content"}:
            raise SageError("INVALID_FILES", "Each source packet must contain exactly path and content.")
        relative = safe_relative(packet["path"])
        folded = relative.casefold()
        if folded in supplied or (folded in aliases and aliases[folded] != relative):
            raise SageError("DUPLICATE_PATH", "Duplicate or case-alias source packets are not accepted.")
        supplied.add(folded)
        if not isinstance(packet["content"], str):
            raise SageError("INVALID_SOURCE", "Source content must be UTF-8 text.")
        try:
            data = packet["content"].encode("utf-8")
        except UnicodeEncodeError:
            raise SageError("INVALID_SOURCE", "Source content contains an invalid Unicode sequence.") from None
        if len(data) > policy.max_file_bytes:
            raise SageError("SIZE_LIMIT", "A generated file exceeds the policy byte limit.")
        _reject_credentials(packet["content"])
        current[relative] = {"path": relative, "sha256": hashlib.sha256(data).hexdigest(), "size_bytes": len(data)}
        prepared.append((relative, data))
    # A file cannot simultaneously be a parent directory, including case aliases.
    all_paths = {record.casefold() for record in current}
    directory_aliases = {}
    for relative in current:
        parts = relative.split("/")
        if any("/".join(parts[:index]).casefold() in all_paths for index in range(1, len(parts))):
            raise SageError("PATH_CONFLICT", "A source file conflicts with a required parent directory.")
        for index in range(1, len(parts)):
            parent = "/".join(parts[:index])
            if parent.casefold() in directory_aliases and directory_aliases[parent.casefold()] != parent:
                raise SageError("DUPLICATE_PATH", "Case-alias source directories are not accepted.")
            directory_aliases[parent.casefold()] = parent
    if len(current) > policy.max_files or sum(record["size_bytes"] for record in current.values()) > policy.max_project_bytes:
        raise SageError("SIZE_LIMIT", "The resulting project exceeds policy file or byte limits.")
    if any(record["size_bytes"] > policy.max_file_bytes for record in current.values()):
        raise SageError("SIZE_LIMIT", "An existing source file exceeds the selected policy limit.")
    # All existing directories, even empty ones, were inspected above. Preflight
    # destinations before mkdir so a late conflict cannot cause partial output.
    for relative, _ in prepared:
        target = root.joinpath(*relative.split("/"))
        cursor = root
        for component in relative.split("/"):
            if cursor.is_dir():
                with os.scandir(cursor) as entries:
                    for entry in entries:
                        if entry.name.casefold() == component.casefold() and entry.name != component:
                            raise SageError("DUPLICATE_PATH", "A source destination aliases an existing directory or filename.")
            cursor = cursor / component
        for ancestor in (target, *target.parents):
            if ancestor == root.parent:
                break
            try:
                info = ancestor.lstat()
            except FileNotFoundError:
                continue
            if _is_link(info) or (ancestor != target and not stat.S_ISDIR(info.st_mode)):
                raise SageError("UNSAFE_LINK", "A source destination traverses a link or non-directory.")
            if ancestor == target and not stat.S_ISREG(info.st_mode):
                raise SageError("PATH_CONFLICT", "A source destination already exists as a directory or special file.")
    return root, prepared, sorted(current.values(), key=lambda record: record["path"])


def preflight_project_files(workspace: os.PathLike | str, files: list[dict], policy: Policy) -> list[dict]:
    """Return the predicted full manifest without modifying source or directories."""
    return _prepare_project_files(workspace, files, policy)[2]


def write_project_files(workspace: os.PathLike | str, files: list[dict], policy: Policy) -> list[dict]:
    """Preflight every packet and the existing tree before creating any source."""
    root, prepared, _ = _prepare_project_files(workspace, files, policy)
    try:
        root.mkdir(parents=True, exist_ok=True)
        _checked_absolute(root)
        for relative, data in prepared:
            target = root.joinpath(*relative.split("/"))
            target.parent.mkdir(parents=True, exist_ok=True)
            _atomic_project_write(target, data, root)
    except SageError:
        raise
    except OSError:
        raise SageError("FILE_WRITE", "Validated project directories could not be created safely.") from None
    return project_manifest(root)
