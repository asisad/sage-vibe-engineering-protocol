#!/usr/bin/env python3
"""Search Ruflo pinned upstream *definitions*, not executable capabilities."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

CATALOG = Path(__file__).with_name("catalog.json")
LIMIT = 100


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("stats", "list", "search", "show", "plan"))
    parser.add_argument("query", nargs="?")
    parser.add_argument("--kind", choices=("agent_definition", "skill", "plugin_manifest", "runtime_module"))
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = cat["entries"]
    if args.limit < 1 or args.limit > LIMIT or args.offset < 0:
        print(json.dumps({"ok": False, "error": "INVALID_PAGINATION"}))
        return 2
    found = []
    if args.action == "stats":
        result = {k: cat[k] for k in ("pinned_tag", "pinned_commit", "inventory_definitions",
                                    "counts_by_kind", "all_source_files_in_four_trees")}
    elif args.action == "show":
        found = [e for e in entries if e["id"] == args.query]
        if not found:
            print(json.dumps({"ok": False, "error": "NOT_FOUND"}))
            return 2
        result = found[0]
    else:
        needle = (args.query or "").casefold()
        if args.action in ("search", "plan") and not needle:
            print(json.dumps({"ok": False, "error": "QUERY_REQUIRED"}))
            return 2
        terms = needle.split()
        for entry in entries:
            if args.kind and entry["kind"] != args.kind:
                continue
            haystack = " ".join([entry["id"], entry["kind"], entry["title"],
                                 entry["source_path"]]).casefold()
            if all(term in haystack for term in terms):
                found.append(entry)
        if args.action == "plan":
            found = [e for e in found if e["decision"] != "REFERENCE_ONLY"]
            found.sort(key=lambda e: (e["kind"] not in ("skill", "agent_definition"),
                                      len(e["source_path"]), e["source_path"]))
        total = len(found)
        result = {
            "total": total, "offset": args.offset, "limit": args.limit,
            "definitions": found[args.offset:args.offset + args.limit],
            "plan_is_advisory": args.action == "plan",
            "active_tools": 0, "execution_authorized": False,
            "notes": "Source Git blobs only; no dynamic Ruflo execution implied.",
        }
    envelope = {"ok": True, "source": "ruflo", "catalog_version": cat["schema_version"],
                "upstream_commit": cat["pinned_commit"], "data": result}
    print(json.dumps(envelope, ensure_ascii=False, indent=2 if args.json else None))
    return 0


if __name__ == "__main__":
    sys.exit(main())
