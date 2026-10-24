"""Build an attributed offline kit closure without executing upstream source.

The source checkout stays unmodified: wheel resources are copied to build_lib;
sdist resources go only to its temporary release tree. The same closure can then
build a wheel from that sdist without a SAGE repository or network connection.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.bdist_wheel import bdist_wheel
from setuptools.command.install import install
from setuptools.command.sdist import sdist


PACKAGE_ROOT = Path(__file__).resolve().parent
CATALOG = "extensions/ecc/catalog.json"
CONTRACT = "SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT.md"
AUTHORED_RESOURCES = (
    CATALOG,
    CONTRACT,
    "LICENSE",
    "extensions/ecc/sage_ecc.py",
    "extensions/ecc/descriptors.json",
    "extensions/ecc/policy.json",
    "extensions/ecc/manifest.json",
    "extensions/ecc/upstream-lock.json",
    "extensions/ecc/enhancements.json",
    "extensions/ecc/README.fa-en.md",
    "extensions/ecc/THIRD_PARTY_NOTICES.md",
    "extensions/ecc/review/OVERLAP-MATRIX.fa.md",
    "schemas/extensions/sage-ecc-catalog.schema.json",
    "docs/catalog/index.html",
    "skills/registry.json",
    "extensions/technology-engineering/manifest.json",
    "extensions/technology-engineering/policy.json",
    "schemas/extensions/sage-technology-engineering.schema.json",
    "extensions/autonomous-runtime/manifest.json",
    "extensions/autonomous-runtime/acceptance.json",
    "SAGE_AUTONOMOUS_RUNTIME_DELTA.md",
    "runtime/autonomous/README.fa-en.md",
    "runtime/autonomous/DESIGN.md",
    "extensions/ruflo/manifest.json",
    "extensions/ruflo/policy.json",
    "extensions/ruflo/catalog.json",
    "extensions/ruflo/CAPABILITY-MAP.fa.md",
    "extensions/ruflo/README.fa-en.md",
    "extensions/ruflo/LIVE_BINDING.fa-en.md",
    "extensions/ruflo/live-acceptance.json",
    "extensions/ruflo/sage_ruflo.py",
    "extensions/ruflo/sage_ruflo_catalog.py",
    "schemas/extensions/sage-ruflo-approval.schema.json",
    "extensions/ruflo/runtime/package.json",
    "extensions/ruflo/runtime/package-lock.json",
    "extensions/ruflo/runtime/Dockerfile",
    "extensions/ruflo/runtime/.dockerignore",
)


def build_path(value) -> Path:
    """Keep catalog resource paths intact even under long Windows temp roots."""
    path = Path(value).absolute()
    if os.name == "nt" and not str(path).startswith("\\\\?\\"):
        text = str(path)
        return Path("\\\\?\\UNC\\" + text[2:] if text.startswith("\\\\") else "\\\\?\\" + text)
    return path


def resource_root() -> Path:
    bundled = PACKAGE_ROOT / "src/sage_runtime/_kit"
    if (bundled / CATALOG).is_file() and (bundled / CONTRACT).is_file():
        return build_path(bundled)
    repo = PACKAGE_ROOT.parents[1]
    if (repo / CATALOG).is_file() and (repo / CONTRACT).is_file():
        return build_path(repo)
    raise RuntimeError("Offline SAGE catalog sources are missing; build from the complete repository or attributed sdist.")


def safe_source(root: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if (not relative or pure.is_absolute() or "\\" in relative or ":" in relative
            or any(part in ("", ".", "..") for part in relative.split("/"))):
        raise RuntimeError("Unsafe packaged resource path.")
    source = root.joinpath(*pure.parts)
    for component in (source, *source.parents):
        details = component.lstat()
        if (stat.S_ISLNK(details.st_mode)
                or getattr(details, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)):
            raise RuntimeError("Links/reparse points are not accepted in packaged resources.")
        if component == root:
            break
    if not source.is_file() or not source.resolve().is_relative_to(root.resolve()):
        raise RuntimeError("A packaged resource is not a contained regular file.")
    if source.stat().st_size > 16 * 1024 * 1024:
        raise RuntimeError("A packaged resource exceeds its byte limit.")
    return source


def source_closure(root: Path) -> dict[str, str | None]:
    catalog_bytes = safe_source(root, CATALOG).read_bytes()
    catalog = json.loads(catalog_bytes.decode("utf-8"))
    if catalog.get("schema_version") != "sage-ecc/0.1":
        raise RuntimeError("Unexpected offline catalog protocol.")
    sources: dict[str, str | None] = {name: None for name in AUTHORED_RESOURCES}
    sources[CATALOG] = hashlib.sha256(catalog_bytes).hexdigest()

    def add(relative: str, expected: str) -> None:
        if (relative not in AUTHORED_RESOURCES
                and not relative.startswith(("sources/upstream/ecc/", "skills/",
                                             "extensions/technology-engineering/",
                                             "extensions/ecc/licenses/"))):
            raise RuntimeError("Catalog resource is outside the public capability source roots.")
        if not isinstance(expected, str) or len(expected) != 64:
            raise RuntimeError("Every declared source needs a SHA256 pin.")
        if relative in sources and sources[relative] not in (None, expected):
            raise RuntimeError("Conflicting source pins in the packaged catalog.")
        sources[relative] = expected

    for entry in catalog["entries"]:
        add(entry["local_path"], entry["source"]["sha256"])
        for resource in entry.get("resources", []):
            add(resource["local_path"], resource["sha256"])
    for notice in catalog.get("notices", []):
        add(notice["local_path"], notice["sha256"])
    return sources


def stage_resources(destination: Path) -> dict:
    destination = build_path(destination)
    root = resource_root()
    closure = source_closure(root)
    if len(closure) > 4096:
        raise RuntimeError("Offline kit source closure exceeds its file-count limit.")
    verified = []
    total_bytes = 0
    # Validate the complete closure before making any resource copies.
    for relative, expected in sorted(closure.items()):
        source = safe_source(root, relative)
        data = source.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if expected is not None and digest != expected:
            raise RuntimeError("Catalog SHA256 mismatch: " + relative)
        total_bytes += len(data)
        if total_bytes > 64 * 1024 * 1024:
            raise RuntimeError("Offline kit source closure exceeds its byte limit.")
        verified.append((relative, data, digest, len(data)))
    # A reused build directory must not leak stale files into the next wheel.
    # Refuse unexpected data rather than recursively deleting a caller's files.
    for component in (destination, *destination.parents):
        try:
            details = component.lstat()
        except FileNotFoundError:
            continue
        if (stat.S_ISLNK(details.st_mode)
                or getattr(details, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)):
            raise RuntimeError("Linked build destinations are not accepted.")
    allowed = set(closure) | {"BUNDLED_RESOURCES.json"}
    if destination.exists():
        for candidate in destination.rglob("*"):
            details = candidate.lstat()
            if (stat.S_ISLNK(details.st_mode)
                    or getattr(details, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)):
                raise RuntimeError("Linked build resources are not accepted.")
            if candidate.is_file() and candidate.relative_to(destination).as_posix() not in allowed:
                raise RuntimeError("Unexpected stale resource in build output; use a clean build directory.")
            if not candidate.is_file() and not candidate.is_dir():
                raise RuntimeError("Special files are not accepted in build output.")
    for relative, data, _, _ in verified:
        target = destination.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Write exactly the bytes that were validated, not a later reread of a
        # source file that an editor or concurrent worker may have changed.
        target.write_bytes(data)
    inventory = {
        "schema_version": "sage-runtime-kit/0.1",
        "treatment": "attributed_source_data_not_executed",
        "upstream_authenticity_verified": False,
        "catalog_source_pins": json.loads(next(data for relative, data, _, _ in verified if relative == CATALOG))["sources"],
        "files": [{"path": relative, "sha256": digest, "bytes": size}
                  for relative, _, digest, size in verified],
    }
    (destination / "BUNDLED_RESOURCES.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return inventory


class BuildWithOfflineKit(build_py):
    def finalize_options(self) -> None:
        super().finalize_options()
        self.build_lib = str(build_path(self.build_lib))

    def run(self) -> None:
        super().run()
        stage_resources(Path(self.build_lib) / "sage_runtime/_kit")


class WheelWithLongPaths(bdist_wheel):
    def finalize_options(self) -> None:
        super().finalize_options()
        self.bdist_dir = str(build_path(self.bdist_dir))


class InstallWithLongPaths(install):
    def finalize_options(self) -> None:
        super().finalize_options()
        if os.name == "nt":
            # Wheel's Windows install scheme adds a literal '/.'; extended paths
            # deliberately do not normalize it, so normalize before using them.
            for name in ("build_lib", "install_lib", "install_libbase", "install_purelib",
                         "install_platlib", "install_data", "install_headers", "install_scripts"):
                value = getattr(self, name, None)
                if value:
                    setattr(self, name, str(build_path(os.path.normpath(value))))


class SourceWithOfflineKit(sdist):
    def make_release_tree(self, base_dir, files) -> None:
        super().make_release_tree(base_dir, files)
        stage_resources(Path(base_dir) / "src/sage_runtime/_kit")


if __name__ == "__main__":
    setup(cmdclass={"build_py": BuildWithOfflineKit, "bdist_wheel": WheelWithLongPaths,
                    "install": InstallWithLongPaths, "sdist": SourceWithOfflineKit})
