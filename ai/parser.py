# ai/parser.py
"""Utility helpers for parsing AI responses."""

import json
import re


def extract_json(text: str) -> dict | None:
    """Try to extract a JSON object from an AI response string.

    Handles cases where the model wraps JSON in markdown code fences
    or includes extra text before/after the JSON.
    """
    if not text or text.startswith("[ERROR]"):
        return None

    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text, strict=False)
    except (json.JSONDecodeError, TypeError):
        pass

    # Try extracting from markdown code fences
    fence_pattern = r"```(?:json)?\s*\n?(.*?)\n?```"
    match = re.search(fence_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip(), strict=False)
        except (json.JSONDecodeError, TypeError):
            pass

    # Try finding JSON object boundaries
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        try:
            return json.loads(text[brace_start : brace_end + 1], strict=False)
        except (json.JSONDecodeError, TypeError):
            pass

    # Try finding JSON array boundaries
    bracket_start = text.find("[")
    bracket_end = text.rfind("]")
    if bracket_start != -1 and bracket_end != -1 and bracket_end > bracket_start:
        try:
            return json.loads(text[bracket_start : bracket_end + 1], strict=False)
        except (json.JSONDecodeError, TypeError):
            pass

    return None


def safe_get(data: dict, key: str, default="Not Found") -> str:
    """Safely get a value from a dict, returning default for missing/empty values."""
    if not isinstance(data, dict):
        return default
    val = data.get(key)
    if val is None or val == "":
        return default
    return val
