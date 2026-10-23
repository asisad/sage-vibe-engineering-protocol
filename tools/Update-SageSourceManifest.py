#!/usr/bin/env python3
"""Refresh current tracked-source hashes after staging reviewed source changes.

Historical manifests stay untouched. SOURCE_MANIFEST.json cannot hash itself.
New files must be staged first; ignored runtime outputs are not enrolled.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "SOURCE_MANIFEST.json"


def main():
    document = json.loads(PATH.read_text(encoding="utf-8"))
    catalog = json.loads((ROOT / "extensions/ecc/catalog.json").read_text(encoding="utf-8"))
    tracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files", "-z"])
    paths = sorted({p.decode("utf-8") for p in tracked.split(b"\0") if p})
    entries = []
    for relative in paths:
        if relative == "SOURCE_MANIFEST.json":
            continue
        path = ROOT / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Only regular current files can be recorded: {relative}")
        entries.append({"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    if not any(row["path"] == "extensions/ecc/catalog.json" for row in entries):
        raise ValueError("Stage reviewed extension files before refreshing their source manifest")
    autonomous_path = ROOT / "extensions/autonomous-runtime/manifest.json"
    autonomous = json.loads(autonomous_path.read_text(encoding="utf-8")) if autonomous_path.is_file() else None
    document["manifest_id"] = ("sage.source-manifest.v0.8.4+ecc-catalog+autonomous-runtime.2026-10-24"
                               if autonomous else "sage.source-manifest.v0.8.4+ecc-catalog.2026-10-23")
    document["recorded_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    document["upstream_pins"]["affaan-m/ECC"] = {
        "repository": "https://github.com/affaan-m/ECC",
        "commit": catalog["sources"]["ECC"]["commit"],
        "reuse": "ATTRIBUTED_SOURCE_CATALOG_WITH_PER_ITEM_DISPOSITIONS",
        "source_inventory": "extensions/ecc/upstream-lock.json",
    }
    document.setdefault("source_extensions", {})["ecc_capabilities"] = {
        "version": "0.1.0", "channel": "SOURCE_BRANCH_REVIEW_CANDIDATE",
        "live_execution": False, "native_installation": False,
    }
    if autonomous:
        document["source_extensions"]["bounded_autonomous_runtime"] = {
            "version": autonomous["version"], "channel": autonomous["status"],
            "default_live_execution": False, "explicit_task_approval_required": True,
            "native_ecc_installation": False, "manifest": "extensions/autonomous-runtime/manifest.json",
        }
    document["entries"] = entries
    PATH.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "UPDATED", "tracked_files_hashed": len(entries),
                      "historical_manifests_modified": False}))


if __name__ == "__main__":
    main()
