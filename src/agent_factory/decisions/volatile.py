"""Closed per-question-type state schemas and the normalize / redact / bound transforms.

J1 contract (seeds/seed-laya-j1-v1.yaml; the pinned decisions in
tasks/laya-j1-breakdown.md; AMENDMENT 1, D-056; AMENDMENT 2, D-057 -- the sk
and bearer class forms): state is a BOUNDED, CLOSED,
per-question-type extraction -- never verbatim bytes. Line numbers, timestamps,
absolute paths, run ids and PIN SHAs are never state keys; they belong to
source_ref.locator (J1-2's).

Three transforms, three jobs, one fixed order (normalize -> redact -> bound),
composed by ONE public function, decision_state:
  normalize -- the STABILITY mechanism: repo-relativize (root-bound), NFC,
      collapse whitespace runs to one space and strip, sort list keys,
      case-fold enum values to the schema's case. It never cuts.
  redact    -- the SECURITY mechanism only: every secret class -> a fixed
      placeholder. Applied AFTER normalize. It never contributes to stability
      and stability never relies on it.
  bound     -- the SIZE mechanism: each bounded field is cut at its limit on a
      code-point boundary, then its trailing whitespace is stripped. Applied
      AFTER redact, so no cut splits a secret before a pattern sees it.
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

# sk and bearer (AMENDMENT 2, D-057; VERIFY-J1-1-R1 V-1): each fires where its
# PIN form fires -- "sk-" then 8+ run characters; "bearer", whitespace, 16+ --
# so its prefix is always replaced and a second pass finds nothing to redact
# there, even after bound's cut. The run it replaces ends before a secret
# assignment that a later class redacts (_YIELD): the name stays for that
# class and its value is redacted. At the PIN "task-password: v" gave
# "ta<redacted:sk>: v" and v reached the ledger. The run does not yield when
# that value holds another assignment head: the value would swallow the second
# name and free ITS value (the widened value's chain gap, which the PIN's
# swallow hid), so the run keeps its PIN form. A run holds at most one name
# that a separator follows (a separator ends the run), and the value checks
# stop at the value's end or at the first head, so the cost stays linear.
_SECRET_NAME = r"(?i:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)"
# The start of an assignment a later class could take: a name, an optional
# quote and "=" or ":" (the widened form; the upper-case NAME= is one of them),
# or "token" and a quote or whitespace (the token class's other separators).
_ASSIGNMENT_HEAD = _SECRET_NAME + r"[\"']?\s?[:=]|(?i:(?:\b|(?<=_))token)[\"'\s]"
_ENVVAL_HEAD = r"(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)="
# The assignments sk and bearer yield to, each with the value its class takes:
# _ENVVAL (upper-case NAME=, any value but base64 "=" padding), _ENVVAL_WIDE
# (8+ value characters; an upper-case NAME= is _ENVVAL's, whose \S+ value runs
# further) and _TOKEN (a quote or one space, then a 32+ run).
_YIELD = (
    _ENVVAL_HEAD + r"(?=[^\s=])(?!\S*?(?:" + _ASSIGNMENT_HEAD + r"))"
    r"|(?!" + _ENVVAL_HEAD + r")" + _SECRET_NAME + r"[\"']?\s?[:=]\s?[\"']?"
    r"(?=[^\s\"'&,;]{8})(?![^\s\"'&,;]*?(?:" + _ASSIGNMENT_HEAD + r"))"
    r"|(?i:(?:\b|(?<=_))token)(?=[\"' ])[\"']? ?[\"']?"
    r"(?=[A-Za-z0-9+/]{32})(?![A-Za-z0-9+/]*?(?:" + _ASSIGNMENT_HEAD + r"))"
)
_BEARER = re.compile(
    r"(?i:bearer)\s+(?=[A-Za-z0-9._~+/-]{16})(?:(?!" + _YIELD + r")[A-Za-z0-9._~+/-])*=*"
)
_SK = re.compile(r"sk-(?=[A-Za-z0-9_-]{8})(?:(?!" + _YIELD + r")[A-Za-z0-9_-])*")
# A 32+ hex/base64 run after "token", "*_token" or "*_TOKEN" (C-F3a): an
# optional quote after the name, then ONE space, or ":" / "=" with at most one
# space on each side, then an optional quote ("token = <run>",
# '"token": "<run>"', "AGENT_TOKEN: <run>"). A whitespace-RUN separator (e.g.
# "token:  <run>") is NOT matched here: it is only caught once normalize has
# collapsed the run to one space -- that asymmetry is what discriminates the
# normalize -> redact order in the order test.
_TOKEN = re.compile(r"(?i)(?:\b|(?<=_))token[\"']?(?: ?[:=] ?| )?[\"']?([A-Za-z0-9+/]{32,})")
# The env assignments: the name is kept, the value part is replaced. Two
# forms in two passes, in the class order of the D-1 ruling:
#   _ENVVAL      -- the upper-case NAME=value (any value), TOKEN included, as
#       at the PIN. It runs BEFORE the token class, so an upper-case
#       assignment wins its own class (PC_BRIDGE_TOKEN=<run> -> envval).
#   _ENVVAL_WIDE -- (C-F3b) the names matched without regard to case, TOKEN
#       included, with at most one space around "=" or ":" and an optional
#       quote after the name and before the value, whose value must have 8+
#       characters (the transcript scrubber's floor,
#       scripts/transcript_export.py:33, so prose such as "key: sorted"
#       stays). It runs AFTER the token class, so a 32+ run after a TOKEN
#       name keeps the token placeholder, and its guard (_envval_wide) never
#       replaces a value that already is a placeholder. At most one space: a
#       whitespace RUN is never bridged, which keeps the order test's
#       normalize -> redact discriminator (a run exists only before normalize).
# A name's prefix (SECRET_, db_, AWS_SECRET_ACCESS_) is matched by the scan,
# not by a pattern group: the text before the name is kept either way, and
# the nested group "(?:[A-Z][A-Z0-9_]*_)*" backtracked exponentially
# ("A_" * 26 took 8.6 s; J1-1-R1 report D-3).
_ENVVAL = re.compile(r"(?P<name>(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)=)\S+")
_ENVVAL_WIDE = re.compile(
    r"(?P<wide>(?i:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)[\"']?\s?[:=]\s?[\"']?)"
    r"(?P<value>[^\s\"'&,;]{8,})"
)
# A private-key block -- the transcript scrubber's label family
# (scripts/transcript_export.py:29-31: PEM, OpenSSH and GnuPG armor) -- BEGIN
# through END, or through the end of the value when the END line is missing
# (VERIFY-J1-1 F-11). The whole block becomes one placeholder.
_PRIVKEY = re.compile(
    r"-----BEGIN [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----.*?"
    r"(?:-----END [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----|\Z)",
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


def _envval_wide(m: re.Match) -> str:
    # The guard: a value that already is a placeholder -- whole, or cut by
    # bound -- is never replaced again, so no class is relabelled (a 32+ run
    # after a TOKEN name ends as <redacted:token> only). Any other value,
    # including a placeholder followed by more of the value (a base64url
    # tail after a token run), becomes envval whole.
    if any(p.startswith(m.group("value")) for p in PLACEHOLDERS.values()):
        return m.group(0)
    return m.group("wide") + PLACEHOLDERS["envval"]


def _redact_str(text: str) -> str:
    # Order (the D-1 ruling; each pass sees the text the earlier passes left):
    # the private-key block first (so it is not split), then sk, then bearer,
    # then the upper-case env assignment (which wins over the token rule for
    # a NAME=value form), then the token class (a 32+ run after a TOKEN
    # name), then the widened env assignment for the rest (guarded).
    text = _PRIVKEY.sub(PLACEHOLDERS["privkey"], text)
    text = _SK.sub(PLACEHOLDERS["sk"], text)
    text = _BEARER.sub(PLACEHOLDERS["bearer"], text)
    text = _ENVVAL.sub(lambda m: m.group("name") + PLACEHOLDERS["envval"], text)
    text = _TOKEN.sub(lambda m: m.group(0).replace(m.group(1), PLACEHOLDERS["token"]), text)
    text = _ENVVAL_WIDE.sub(_envval_wide, text)
    return text


def bound(question_id: str, state: dict) -> dict:
    """The SIZE transform, applied AFTER redact: each bounded field is cut at
    its limit on a code-point boundary, then its trailing whitespace is
    stripped (a cut right after a space would leave one: VERIFY-J1-1 F-3).
    Lists and unbounded fields pass unchanged. Because it runs after redact,
    a secret that straddles a limit is replaced whole before any cut."""
    if question_id not in SCHEMAS:
        raise DecisionStateError("decision-question-unknown", question_id)
    fields = SCHEMAS[question_id]
    out: dict = {}
    for key, value in state.items():
        spec = fields.get(key)
        if spec is not None and spec.limit is not None and isinstance(value, str):
            value = value[: spec.limit].rstrip()
        out[key] = value
    return out


def decision_state(question_id: str, state: dict, root: str | os.PathLike | None = None) -> dict:
    """The ONE public composition, bound(redact(normalize(state))) (D-056):
    state_digest and both ledger call sites use it. It is idempotent on its
    own output -- the ledger's fixed-point check depends on that -- including
    when the cut lands inside a placeholder: redact can only complete a cut
    placeholder again, and bound cuts it back to the same prefix. (One known
    exception, J1-1-R1 report D-2: a v1 lane whose cut exposes a PIN-shaped
    suffix, which normalize strips on the next pass.)"""
    return bound(question_id, redact(normalize(question_id, state, root)))
