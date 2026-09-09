"""Small, dependency-free projections of SAGE contract checks."""

import json
from pathlib import Path
from typing import Any, Dict, List


def load_json(path: str) -> Any:
    """Load a UTF-8 JSON artifact without executing anything."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_deployment_contract(contract: Dict[str, Any]) -> List[str]:
    """Return deterministic issues; an empty list means structurally valid."""
    required = ("deployment_id", "artifact_ref", "provider", "environment", "trigger", "gates", "rollback_ref")
    issues = ["missing deployment field: " + field for field in required if not contract.get(field)]
    if not isinstance(contract.get("gates"), list) or not contract.get("gates"):
        issues.append("deployment requires operations gates")
    if contract.get("environment") in ("STAGING", "PRODUCTION") and not contract.get("image_digest"):
        issues.append("staging/production requires image_digest")
    return issues
