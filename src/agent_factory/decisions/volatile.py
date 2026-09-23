"""Closed per-question-type state schemas and the normalize / redact transforms.

J1 contract (seeds/seed-laya-j1-v1.yaml; the pinned decisions in
tasks/laya-j1-breakdown.md): state is a BOUNDED, CLOSED, per-question-type
extraction -- never verbatim bytes. Line numbers, timestamps, absolute paths,
run ids and PIN SHAs are never state keys; they belong to source_ref.locator
(J1-2's).

Two transforms, two jobs, one fixed order (normalize -> redact):
  normalize -- the STABILITY mechanism: repo-relativize (root-bound), NFC,
      collapse whitespace runs to one space and strip, sort list keys,
      case-fold enum values to the schema's case, truncate bounded fields
      on a character boundary.
  redact    -- the SECURITY mechanism only: every secret class -> a fixed
      placeholder. Applied AFTER normalize. It never contributes to stability
      and stability never relies on it.
"""

from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass

EXCERPT_LIMIT = 400            # ap.violates_row.action_excerpt, wf.drift.observed/expected
MSG_LIMIT = 200               # b1.finding_sev / b1.finding_kind msg (bounded, not verbatim)
FINDING_KIND_OPTIONS_MAX = 8  # b1.finding_kind: open slug closed to <= 8 by the harvest

#: Fixed redaction placeholder per secret class. A fixture's clean form
#: CONTAINS the placeholder, so a secret-bearing state and the secret-free
#: state redact to the same bytes and hash to the same digest.
PLACEHOLDERS = {
    "sk": "<redacted:sk>",
    "token": "<redacted:token>",
    "bearer": "<redacted:bearer>",
    "envval": "<redacted:envval>",
    "privkey": "<redacted:privkey>",
}

_BEARER = re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/-]{16,}=*")
_SK = re.compile(r"sk-[A-Za-z0-9_-]{8,}")
# A 32+ hex/base64 run after the word "token" with a SINGLE separator
# (one space, or ":" optionally followed by one space). A whitespace-RUN
# separator (e.g. "token:  <run>") is NOT matched here: it is only caught
# once normalize has collapsed the run to one space -- that asymmetry is what
# discriminates the normalize -> redact order in the order test.
_TOKEN = re.compile(r"(?i)\btoken(?:[:=] ?| )?([A-Za-z0-9+/]{32,})")
# KEY=/TOKEN=/SECRET=/PASSWORD=(API_KEY) assignments: the name is kept, the
# value part is replaced. Applied before the bare token rule so an
# assignment wins its own class.
_ENVVAL = re.compile(
    r"(?P<name>(?:[A-Z][A-Z0-9_]*_)*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY))=\S+"
)
# A private-key block, BEGIN ... END (the whole block becomes one placeholder).
_PRIVKEY = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
    re.S,
)


class DecisionStateError(RuntimeError):
    """A fail-closed state boundary refusal with a stable reason string."""

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        self.detail = detail
        message = reason if not detail else f"{reason}: {detail}"
        super().__init__(message)


@dataclass(frozen=True)
class _Field:
    """One closed state key and its normalization rules."""

    kind: str  # "str" | "path" | "list" | "target"
    limit: int | None = None
    case: str | None = None  # "lower" | "upper" | None (open slug: untouched)
    enum: tuple[str, ...] | None = None  # a closed option set (canonical case)
    strip_pin: bool = False


def _strip_pin_suffix(value: str) -> str:
    """Strip only the harness lane suffix ``--<7..40 hex PIN>``.

    The PIN belongs to ``source_ref.locator`` (J1-2), never stable state.
    A literal ``--`` elsewhere in a lane name is not a PIN and is preserved.
    """
    return re.sub(r"--[0-9a-fA-F]{7,40}$", "", value)


def _nfc_collapse(value: str) -> str:
    """NFC-normalize, collapse whitespace runs to one space, strip."""
    s = unicodedata.normalize("NFC", str(value))
    return re.sub(r"\s+", " ", s).strip()


def _path(key: str, value: str, root: str | os.PathLike | None) -> str:
    """A repo-relative path. An absolute path under `root` is relativized;
    an absolute path outside the root (or with no root bound) is refused,
    never silently relativized."""
    s = _nfc_collapse(value)
    if s.startswith("/") or s.startswith("~"):
        if root is None:
            raise DecisionStateError("decision-state-abs-path", key)
        r = os.path.normpath(os.fspath(root))
        p = os.path.normpath(s)
        if p == r or p.startswith(r + os.sep):
            rel = os.path.relpath(p, r).replace(os.sep, "/")
            return rel if not rel.startswith("..") else _refuse_path(key, s)
        return _refuse_path(key, s)
    rel = s.replace(os.sep, "/")
    if rel.startswith("..") or "/../" in rel:
        return _refuse_path(key, s)
    return rel


def _refuse_path(key: str, original: str) -> str:
    raise DecisionStateError("decision-state-abs-path", key)


def _apply_case(s: str, case: str | None) -> str:
    if case == "lower":
        return s.lower()
    if case == "upper":
        return s.upper()
    return s


def _normalize_field(f: _Field, key: str, value, root):
    if f.kind == "list":
        # A sorted list of repo-relative paths: normalize + relativize each
        # item, then sort. The order of the input list never matters.
        if not isinstance(value, list):
            raise DecisionStateError("decision-state-bad-type", key)
        items = [_path(key, str(v), root) for v in value]
        return sorted(items)
    s = _nfc_collapse(value)
    if f.strip_pin:
        s = _strip_pin_suffix(s)
    s = _apply_case(s, f.case)
    if f.limit is not None:
        s = s[: f.limit]
    if f.kind == "path":
        return _path(key, s, root)
    if f.kind == "target":
        return _path(key, s.split()[0] if s.split() else s, root)
    return s


# The seven closed state schemas. Incumbent answers (role/severity/class/
# verdict) are row provenance in J1-2, not state keys here.
SCHEMAS: dict[str, dict[str, _Field]] = {
    "b2.hit_role": {
        "sym": _Field("str", limit=120),
        "file": _Field("path"),
        "snippet": _Field("str", limit=EXCERPT_LIMIT),
    },
    "b1.finding_sev": {
        "file": _Field("path"),
        "kind": _Field("str", limit=80),
        "msg": _Field("str", limit=MSG_LIMIT),
    },
    "b1.finding_kind": {
        "file": _Field("path"),
        "kind": _Field("str", limit=80),
        "msg": _Field("str", limit=MSG_LIMIT),
    },
    "d1.bug_echo_scores": {
        "class_slug": _Field("str", limit=80),
        "finding_title": _Field("str", limit=120),
    },
    "v1.finding_class": {
        "lane": _Field("str", limit=80, strip_pin=True),
        "finding_id": _Field("str", limit=80),
        "title": _Field("str", limit=120),
        "paths": _Field("list"),
        "disposition": _Field(
            "str",
            limit=40,
            case="upper",
            enum=("BLOCKING", "NON-BLOCKING"),
        ),
    },
    "ap.violates_row": {
        "action_kind": _Field(
            "str",
            limit=20,
            case="lower",
            enum=("edit", "command", "brief", "report"),
        ),
        "action_target": _Field("target"),
        "action_excerpt": _Field("str", limit=EXCERPT_LIMIT),
        "row_id": _Field("str", limit=40),
        "row_title": _Field("str", limit=120),
    },
    "wf.drift": {
        "step_id": _Field(
            "str",
            limit=40,
            case="lower",
            enum=(
                "verify-seam-first",
                "one-increment-code-test-commit",
                "negative-control",
                "count-pasted",
                "timestamp-pasted",
                "commit-before-dispatch",
                "impact-before-edit",
                "premise-measured",
                "report-lint-floor",
                "boundary-respected",
            ),
        ),
        "expected": _Field("str", limit=EXCERPT_LIMIT),
        "observed": _Field("str", limit=EXCERPT_LIMIT),
        "drift_kind": _Field(
            "str",
            limit=40,
            case="lower",
            enum=("skipped-step", "out-of-boundary", "substituted-step", "mirror-test", "prose-claim"),
        ),
    },
}

#: Options maxima recorded by the schema (b1.finding_kind is the open slug
#: closed to <= 8 by the harvest; d1.bug_echo_scores is six sub-questions of
#: five levels each).
OPTIONS_MAX = {
    "b1.finding_kind": FINDING_KIND_OPTIONS_MAX,
    "d1.bug_echo_scores": 6 * 5,
}


def schema_keys(question_id: str) -> tuple[str, ...]:
    """The ordered allowed keys for a question type; unknown type is refused."""
    if question_id not in SCHEMAS:
        raise DecisionStateError("decision-question-unknown", question_id)
    return tuple(SCHEMAS[question_id])


def normalize(question_id: str, state: dict, root: str | os.PathLike | None = None) -> dict:
    """The STABILITY transform: closed-schema check + per-key normalization.

    Order inside: question type, then per-key (normalize first), then the
    unknown-key sweep, then the closed-enum check on the raw value. Redaction
    is a separate transform (redact) and never happens here.
    """
    if question_id not in SCHEMAS:
        raise DecisionStateError("decision-question-unknown", question_id)
    fields = SCHEMAS[question_id]
    if not isinstance(state, dict):
        raise DecisionStateError("decision-state-not-mapping", question_id)
    out: dict = {}
    for key, spec in fields.items():
        if key not in state:
            raise DecisionStateError("decision-state-missing-key", f"{question_id}.{key}")
        out[key] = _normalize_field(spec, key, state[key], root)
    for key in state:
        if key not in fields:
            raise DecisionStateError("decision-state-unknown-key", f"{question_id}.{key}")
    for key, spec in fields.items():
        if spec.enum is None or key not in state:
            continue
        raw = state[key]
        if not isinstance(raw, str) or out[key] not in spec.enum:
            raise DecisionStateError("decision-state-bad-enum", f"{question_id}.{key}={raw}")
    return out


def redact(state: dict) -> dict:
    """The SECURITY transform only: every secret class -> its fixed
    placeholder. Applied AFTER normalize (a whitespace-run-split token is
    caught only once normalize has collapsed it). Never a stability input."""
    out: dict = {}
    for key, value in state.items():
        if isinstance(value, str):
            out[key] = _redact_str(value)
        elif isinstance(value, list):
            out[key] = [_redact_str(v) if isinstance(v, str) else v for v in value]
        else:
            out[key] = value
    return out


def _redact_str(text: str) -> str:
    # Order: the private-key block first (so it is not split), then sk, then
    # bearer, then the env-assignment (which wins over the bare token rule for
    # a NAME=value form), then the bare 32+ token run.
    text = _PRIVKEY.sub(PLACEHOLDERS["privkey"], text)
    text = _SK.sub(PLACEHOLDERS["sk"], text)
    text = _BEARER.sub(PLACEHOLDERS["bearer"], text)
    text = _ENVVAL.sub(lambda m: f"{m.group('name')}={PLACEHOLDERS['envval']}", text)
    text = _TOKEN.sub(lambda m: m.group(0).replace(m.group(1), PLACEHOLDERS["token"]), text)
    return text
