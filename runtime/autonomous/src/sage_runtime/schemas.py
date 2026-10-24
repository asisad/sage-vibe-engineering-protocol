"""Small, closed JSON contracts for model output; no model-generated commands."""
from __future__ import annotations

import math
from .safety import SageError


def text(maximum=8000):
    return {"type": "string", "maxLength": maximum}


def array(item, maximum=24):
    return {"type": "array", "items": item, "maxItems": maximum}


def record(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


PROFILES = ("python-stdlib", "node-stdlib", "static-web")
PLAN_SCHEMA = record({
    "status": {"type": "string", "enum": ["READY", "NEEDS_CLARIFICATION", "UNSUPPORTED"]},
    "summary": text(), "questions": array(text(1000), 12),
    "profile": {"type": "string", "enum": [*PROFILES, ""]},
    "risk": {"type": "string", "enum": ["R1", "R2", "R3", "R4"]},
    "technology_rationale": text(), "architecture_mermaid": text(16000),
    "tasks": array(record({"id": text(80), "description": text(2000),
                            "paths": array(text(240), 64)}), 16),
    "acceptance": array(text(2000), 16),
    "dependencies": array(text(400), 24),
    "external_actions": array(text(400), 24),
})
FILES_SCHEMA = record({
    "summary": text(),
    "files": array(record({"path": text(240), "content": text(131072)}), 64),
    "notes": array(text(2000), 16),
})
REVIEW_SCHEMA = record({"accepted": {"type": "boolean"},
                        "summary": text(), "findings": array(text(2000), 24)})


def validate(value, schema, label="result", depth=0):
    """Validate the deliberately small schema vocabulary used above."""
    if depth > 20:
        raise SageError("INVALID_MODEL_OUTPUT", "Model result nesting is excessive.")
    expected = schema.get("type")
    correct = {"object": isinstance(value, dict), "array": isinstance(value, list),
               "string": isinstance(value, str), "boolean": type(value) is bool,
               "integer": type(value) is int,
               "number": type(value) is int or (type(value) is float and math.isfinite(value))}
    if expected not in correct or not correct[expected]:
        raise SageError("INVALID_MODEL_OUTPUT", f"{label} must be {expected}.")
    if "enum" in schema and value not in schema["enum"]:
        raise SageError("INVALID_MODEL_OUTPUT", f"{label} has an unsupported value.")
    if expected == "object":
        properties = schema["properties"]
        if set(value) != set(properties):
            raise SageError("INVALID_MODEL_OUTPUT", f"{label} has missing or unknown fields.")
        for key, child in properties.items():
            validate(value[key], child, label + "." + key, depth + 1)
    elif expected in ("string", "array"):
        if expected == "string":
            try:
                value.encode("utf-8")
            except UnicodeError:
                raise SageError("INVALID_MODEL_OUTPUT", f"{label} is not valid UTF-8 text.") from None
        maximum = schema.get("maxLength" if expected == "string" else "maxItems", 1000000)
        if len(value) > maximum:
            raise SageError("INVALID_MODEL_OUTPUT", f"{label} exceeds its limit.")
        if expected == "array":
            for item in value:
                validate(item, schema["items"], label + "[]", depth + 1)
    return value
