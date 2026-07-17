"""Parse body-weight update requests from chat."""

from __future__ import annotations

import re

_PROFILE_WEIGHT_RE = re.compile(
    r"(?:"
    r"(?:можешь\s+)?(?:постав(?:ь|ить)|обнов(?:и|ить)|измени(?:ть)?|запиши|установи)"
    r"|(?:мой|текущий)\s+вес"
    r")\s+"
    r"(?:текущий\s+)?вес\s*"
    r"(?:как|на|до|равен|=)?\s*"
    r"(?P<weight>\d+(?:[.,]\d+)?)\s*(?:кг|kg)?"
    r"|"
    r"(?:текущий\s+)?вес\s*(?:как|на|до|равен|=)\s*"
    r"(?P<weight2>\d+(?:[.,]\d+)?)\s*(?:кг|kg)?"
    r"|"
    r"мой\s+вес\s*(?P<weight3>\d+(?:[.,]\d+)?)\s*(?:кг|kg)?",
    re.IGNORECASE,
)

_MIN_BODY_WEIGHT_KG = 40.0
_MAX_BODY_WEIGHT_KG = 200.0


def try_parse_body_weight_update(text: str) -> float | None:
    """Return new body weight in kg when message asks to update profile weight."""
    norm = text.lower().replace("ё", "е").strip()
    if not norm:
        return None

    if "вес" not in norm:
        return None

    match = _PROFILE_WEIGHT_RE.search(norm)
    if not match:
        return None

    raw = match.group("weight") or match.group("weight2") or match.group("weight3")
    if not raw:
        return None

    weight = float(raw.replace(",", "."))
    if not (_MIN_BODY_WEIGHT_KG <= weight <= _MAX_BODY_WEIGHT_KG):
        return None

    return weight
