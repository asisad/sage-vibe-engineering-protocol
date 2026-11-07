#!/usr/bin/env python3
"""Discovery-only SAGE Omega Instagram specialist; no Instagram mutations.

Does not execute Skills or Python scripts, grant SAGE authority, or log into Instagram.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA = "sage-internet-eyes-instagram-specialist/0.1"
SKILL_NAMES = (
    "ig-reel", "ig-viral", "ig-caption", "ig-carousel", "ig-story",
    "ig-profile", "ig-plan", "ig-human", "ig-comment", "ig-reply",
    "ig-dm", "ig-repurpose", "ig-audit",
)
ROUTES = {
    "reel": ("ig-reel", "Scripting, hook scoring, timed beat sheet"),
    "viral-research": ("ig-viral", "Analyze consented, attributed Reel samples"),
    "caption": ("ig-caption", "Draft and lint captions"),
    "carousel": ("ig-carousel", "Draft carousel structure and copy"),
    "story": ("ig-story", "Draft story sequences"),
    "profile": ("ig-profile", "Review profile against a rubric"),
    "plan": ("ig-plan", "Plan content calendar"),
    "humanize": ("ig-human", "English-first local text heuristics"),
    "comment": ("ig-comment", "Draft comment; never send"),
    "reply": ("ig-reply", "Draft reply; never send"),
    "dm": ("ig-dm", "Draft DM; never send"),
    "repurpose": ("ig-repurpose", "Repurpose creator-provided content"),
    "audit": ("ig-audit", "Analyze creator-supplied Instagram Insights"),
}

def roots() -> list[Path]:
    home = Path.home()
    return [home / ".agents" / "skills", home / ".claude" / "skills"]

def installed(skill: str) -> list[str]:
    return [str(p / skill) for p in roots() if (p / skill / "SKILL.md").is_file()]

def route(intent: str, language: str) -> dict[str, Any]:
    skill, purpose = ROUTES[intent]
    paths = installed(skill)
    warnings: list[str] = []
    if intent == "viral-research":
        warnings.append(
            "Agent Reach Instagram searches users and reads profiles/post descriptions; "
            "it does not supply complete Reel views or official Instagram Insights."
        )
    if language.lower().startswith("fa") and intent in ("humanize", "caption", "reel"):
        warnings.append(
            "Upstream English heuristics are not validated for Persian; "
            "automatic ig-human removes U+200C Persian half-spaces and must not run."
        )
    return {
        "schema_version": SCHEMA,
        "status": "DISCOVERED" if paths else "NOT_INSTALLED_ON_THIS_HOST",
        "authority_granted": False,
        "external_execution": False,
        "instagram_mutation_allowed": False,
        "intent": intent,
        "skill": skill,
        "purpose": purpose,
        "installed_paths": paths,
        "data_source": "Internet Eyes / Agent Reach for accessible profiles and descriptions, or user-provided evidence",
        "next_stage": "SAGE Content Agent -> Evidence Engine -> Report Writer / existing Obsidian gateway",
        "warnings": warnings,
    }

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Discover Instagram skills without executing them")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    sub.add_parser("status")
    sel = sub.add_parser("route")
    sel.add_argument("--intent", choices=sorted(ROUTES), required=True)
    sel.add_argument("--language", default="fa")
    ns = p.parse_args(argv)
    if ns.command == "list":
        result = {"schema_version": SCHEMA, "skills": [{"name": n, "paths": installed(n)} for n in SKILL_NAMES]}
    elif ns.command == "status":
        present = {n: installed(n) for n in SKILL_NAMES}
        result = {
            "schema_version": SCHEMA,
            "status": "INSTALLED" if all(present.values()) else "PARTIAL_OR_NOT_INSTALLED",
            "skills_found": sum(bool(x) for x in present.values()),
            "skills_total": len(SKILL_NAMES),
            "installed": present,
            "agent_reach_instagram_live_test": "NOT_CHECKED",
            "instagram_authentication": "NOT_REQUESTED",
            "account_write": False,
        }
    else:
        result = route(ns.intent, ns.language)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
