"""Canonical serialization and the state digest: canonical -> sha256.

J1 contract: canonical(obj) = sorted keys, ensure_ascii=False, separators
(",", ":"), NFC, no newline, and only integers / strings / lists / dicts
(a float is refused). The full pipeline is

    state_digest = sha256(canonical(redact(normalize(state))))

normalize (volatile) is the STABILITY mechanism; redact (volatile) is the
SECURITY mechanism, applied AFTER normalize. Neither is defined here.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata

from agent_factory.decisions.volatile import (  # noqa: F401 (re-exported)
    DecisionStateError,
    normalize,
    redact,
)


def _canon_str(value) -> str:
    """A string or dict-key to its NFC JSON form (ensure_ascii=False)."""
    s = unicodedata.normalize("NFC", str(value))
    if "\n" in s or "\r" in s:
        raise DecisionStateError("decision-canonical-newline", s[:32])
    return json.dumps(s, ensure_ascii=False)


def canonical(obj) -> str:
    """A canonical JSON form: sorted keys, no ASCII-escaping, tight
    separators, NFC, newline-free. Only integers, strings, lists and dicts
    are accepted; anything else (a float, a bool, a None) is refused with
    its key's path."""
    return _canon(obj, "$")


def _canon(value, path: str) -> str:
    if isinstance(value, dict):
        if not value:
            return "{}"
        parts = []
        for k in sorted(value, key=lambda key: str(key)):
            kcanon = _canon_str(k)
            parts.append(kcanon + ":" + _canon(value[k], path + "." + str(k)))
        return "{" + ",".join(parts) + "}"
    if isinstance(value, list):
        if not value:
            return "[]"
        parts = [_canon(item, f"{path}[{i}]") for i, item in enumerate(value)]
        return "[" + ",".join(parts) + "]"
    if isinstance(value, bool):
        # bool subclasses int: refuse it explicitly, never let it print true.
        raise DecisionStateError("decision-canonical-float", path)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        raise DecisionStateError("decision-canonical-float", path)
    if value is None:
        raise DecisionStateError("decision-canonical-float", path)
    if isinstance(value, str):
        return _canon_str(value)
    raise DecisionStateError("decision-canonical-type", path)


def state_digest(question_id: str, state: dict, root: str | None = None) -> str:
    """sha256(canonical(redact(normalize(state)))), hex. The pipeline is
    normalize -> redact -> canonical -> sha256; the order is load-bearing
    (a whitespace-run-split secret is caught only after normalize)."""
    normed = normalize(question_id, state, root)
    redacted = redact(normed)
    text = canonical(redacted)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
