#!/usr/bin/env python3
"""Verify catalog coverage, provenance, source integrity and integration contracts.

No upstream source is imported as Python or executed. This is local consistency
verification, not proof of security or all advertised workflow behavior.
"""
from __future__ import annotations

import collections
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "extensions/ecc"
VENDOR = ROOT / "sources/upstream/ecc"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    spec = importlib.util.spec_from_file_location("sage_ecc_runtime", EXT / "sage_ecc.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    adapter = module.Catalog(ROOT)
    catalog = adapter.document
    entries = catalog["entries"]
    lock = read(EXT / "upstream-lock.json")
    check(lock["commit"] == catalog["sources"]["ECC"]["commit"], "ECC source pin differs")
    check(catalog["authority_granted"] is False and catalog["external_execution"] is False, "Catalog is not authority")
    selected = {row["path"]: row for row in lock["files"] if row["disposition"] == "VENDORED_SOURCE_ONLY"}
    check(len({row["path"] for row in lock["files"]}) == len(lock["files"]), "Duplicate upstream inventory path")
    actual = {p.relative_to(VENDOR).as_posix() for p in VENDOR.rglob("*") if p.is_file()}
    check(actual == set(selected), "Vendored tree differs from source inventory")
    for path, row in selected.items():
        target = VENDOR.joinpath(*module.relative_parts(path))
        module.reject_symlinks(target)
        data = target.read_bytes()
        check(len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"], f"Source hash mismatch: {path}")
    expected_skills = {p.parent.name for p in (VENDOR / "skills").glob("*/SKILL.md")}
    expected_agents = {p.stem for p in (VENDOR / "agents").glob("*.md")}
    check(len(expected_skills) == 311 and len(expected_agents) == 71, "Pinned canonical inventory changed")
    for kind, expected in (("skill", expected_skills), ("agent", expected_agents)):
        rows = [e for e in entries if e["origin"] == "ECC" and e["kind"] == kind]
        check({e["name"] for e in rows} == expected, f"Incomplete {kind} catalog")
        reviews = read(EXT / f"review/{kind}s.json")
        check({e["name"] for e in reviews} == expected and len(reviews) == len(expected), f"Incomplete {kind} reviews")
    native_names = {e["name"] for e in entries if e["origin"] == "SAGE" and e["kind"] == "skill"}
    check(len(native_names) == 26, "Native skill inventory must stay 8 + 18")
    check(sum(e["origin"] == "SAGE" and e["kind"] == "agent" for e in entries) == 17, "Native profiles changed")
    for entry in entries:
        adapter.verified_source(entry)
        check(set(entry["sage_targets"]) <= native_names, f"Unknown overlap target: {entry['id']}")
        check(entry["profile"] in ("engineering", "domain", "operations", "meta"), "Unknown profile")
        check(entry["rationale_fa"] and entry["improvement_fa"], f"Missing review rationale: {entry['id']}")
        if entry["decision"] == "ENHANCE":
            check(bool(entry["sage_targets"]), "Enhancement needs an existing target")
        if entry["origin"] == "ECC":
            check(entry["source"]["path"] in selected, "Catalog source is not vendored")
            check(entry["source"]["sha256"] == selected[entry["source"]["path"]]["sha256"], "Catalog/lock source mismatch")
            check(entry["license"] in ("MIT", "Apache-2.0", "CC-BY-SA-4.0"), "Unreviewed local license")
        for resource in entry.get("resources", []):
            adapter._content(resource["local_path"], resource["sha256"])
            check(resource["sha256"] == selected[resource["source_path"]]["sha256"], "Resource differs from lock")
    descriptors = read(EXT / "descriptors.json")["descriptors"]
    check({d["id"] for d in descriptors} == {e["id"] for e in entries}, "Portable descriptor coverage mismatch")
    by_id = {d["id"]: d for d in descriptors}
    for entry in entries:
        descriptor = by_id[entry["id"]]
        check(descriptor["permissions"]["granted"] == [] and not descriptor["native_bindings"]["installed"], "Descriptor grants implicit authority")
        check((descriptor["invocation_policy"] == "forbidden_in_environment") == (entry["decision"] == "REFERENCE_ONLY"), "Reference-only activation mismatch")
        check(descriptor["procedure_ref"] == entry["local_path"], "Procedure path mismatch")
    for path in (ROOT / "skills/registry.json", ROOT / "bundles/v0.8/core-engineering/bundle.json"):
        check("extensions/ecc/manifest.json" in read(path)["optional_extensions"], "Extension missing from SAGE discovery")
    check(len(read(ROOT / "skills/registry.json")["skills"]) == 8, "Core lifecycle changed")
    for notice in catalog["notices"]:
        adapter._content(notice["local_path"], notice["sha256"])
    scan = read(EXT / "review/static-scan.json")
    check(scan["files_scanned"] == len(scan["files"]) == sum(bool(r.get("text")) for r in selected.values()), "Static scan coverage mismatch")
    check(not scan["security_certified"] and not scan["upstream_scripts_executed"], "Review overclaims execution")
    summary = catalog["summary"]
    check(summary["definitions"] == len(entries), "Summary mismatch")
    check(summary["decisions"] == dict(collections.Counter(e["decision"] for e in entries)), "Decision counts mismatch")
    check(summary["execution_verified_definitions"] == 0, "Source presence is not runtime evidence")
    page = (ROOT / "docs/catalog/index.html").read_text(encoding="utf-8")
    check("__SAGE_CATALOG_DATA__" not in page, "Unbuilt web catalog")
    check('<html lang="fa" dir="rtl">' in page, "RTL page metadata missing")
    print(json.dumps({"status": "PASS", "definitions": len(entries), "ecc_skills": len(expected_skills),
                      "ecc_agents": len(expected_agents), "vendored_files_verified": len(selected),
                      "portable_descriptors": len(descriptors), "upstream_execution": False}, indent=2))


if __name__ == "__main__":
    main()
