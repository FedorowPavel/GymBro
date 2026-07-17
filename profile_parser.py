"""Parse body-weight update messages from Telegram chat."""

from __future__ import annotations

import re

_BODY_WEIGHT_RE = re.compile(
    r"^(?:поставь|обнови|запиши|установи|измени)?\s*"
    r"(?:мой\s+)?(?:телесн\w*\s+)?вес\b"
    r"(?:\s*(?:в|на|до|=|:))?\s*"
    r"(?P<weight>\d+(?:[.,]\d+)?)\s*(?:кг|kg)?\s*\.?$",
    re.IGNORECASE,
)

_MIN_KG = 30.0
_MAX_KG = 250.0


def try_parse_body_weight_kg(text: str) -> float | None:
    """Return body weight in kg when message is a profile weight update."""
    text = text.strip()
    if not text:
        return None

    match = _BODY_WEIGHT_RE.match(text.replace("ё", "е").replace("Ё", "Е"))
    if not match:
        return None

    weight = float(match.group("weight").replace(",", "."))
    if not (_MIN_KG <= weight <= _MAX_KG):
        return None
    return weight
