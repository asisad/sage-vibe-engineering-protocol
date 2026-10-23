"""Reuse the attributed ECC catalog without installing or executing its sources."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from .safety import SageError, reject_links


STAGE_SKILLS = {
    "planner": ("sage-intake", "sage-discover", "sage-plan"),
    "implementer": ("sage-implement",),
    "repairer": ("sage-implement", "sage-verify"),
    "reviewer": ("sage-verify",),
}


class Discovery:
    def __init__(self, kit_root):
        self.root = Path(kit_root).absolute()
        reject_links(self.root)
        module_path = self.root / "extensions/ecc/sage_ecc.py"
        reject_links(module_path)
        if not module_path.is_file():
            raise SageError("KIT_UNAVAILABLE", "The SAGE/ECC capability resources are missing.")
        # This is the SAGE-authored adapter, not code from sources/upstream.
        spec = importlib.util.spec_from_file_location("sage_runtime_catalog", module_path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            self.catalog = module.Catalog(self.root)
        except Exception as exc:
            raise SageError("KIT_INVALID", "Capability catalog could not be validated.") from exc

    def select(self, idea, stage, maximum):
        identifiers = ["sage.skill." + name for name in STAGE_SKILLS[stage]]
        candidates = self.catalog.search(idea, limit=3, active=True)
        identifiers.extend(entry["id"] for entry in candidates)
        if stage == "reviewer" and "ecc.agent.code-reviewer" in self.catalog.entries:
            identifiers.append("ecc.agent.code-reviewer")
        selected, omitted, sections = [], [], []
        size = 0
        for identifier in dict.fromkeys(identifiers):
            try:
                entry = self.catalog.get(identifier, active=True)
                value = self.catalog.show(identifier)
            except Exception as exc:
                raise SageError("SOURCE_INTEGRITY", "A selected capability failed source verification.") from exc
            envelope = {key: value[key] for key in ("id", "source", "boundaries", "license") if key in value}
            section = json.dumps(envelope, ensure_ascii=False) + "\n" + value["source_content"]
            section_size = len(section.encode("utf-8"))
            if size + section_size > maximum:
                if identifier.startswith("sage.skill.sage-"):
                    raise SageError("CONTEXT_LIMIT", "Core lifecycle instructions exceed the context budget.")
                omitted.append({"id": identifier, "reason": "source_context_budget"})
                continue
            size += section_size
            sections.append(section)
            selected.append(envelope)
        return {"selected": selected, "omitted": omitted,
                "source_pins": self.catalog.document["sources"],
                "context": "\n\n--- REFERENCE SOURCE ---\n".join(sections),
                "authority_granted": False}
