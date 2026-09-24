"""Closed per-question-type state schemas and the normalize / redact / bound transforms.

J1 contract (seeds/seed-laya-j1-v1.yaml; the pinned decisions in
tasks/laya-j1-breakdown.md; AMENDMENT 1, D-056; AMENDMENT 2, D-057 -- the sk
and bearer class forms; D-070 -- redact is ONE detection and a span union,
tasks/briefs/laya/J1-1-R4-REDESIGN-brief.md): state is a BOUNDED, CLOSED,
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

import bisect
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

# The detection (D-070; it replaces six sequential substitution passes, each
# reading the text the passes before it left, so that a match in one pass could
# eat a secret NAME that another pass needed: AF-AP-157). ONE detection reads
# the one normalized text. Each form is a HEAD and a VALUE. The head is found at
# EVERY start, a start inside another match of the same form included
# (re.finditer skips those: in "flask-tapasswd=aAPI_KEY : v" the head
# "API_KEY :" starts inside the first value). The value is greedy to its natural
# end, the first character outside its class, and never stops at another head:
# that head is detected on its own and the union covers both
# ("password: mykey=v" is hidden whole). No form sees another form's output, so
# no match can hide a name from another form. Where an envval or widened value
# meets another span, its end is read on the text as it reads after the
# replacement (_spans).
#   sk      "sk-" and 8+ of [A-Za-z0-9_-]. The span is the whole match.
#   bearer  "bearer" in any case, whitespace, 16+ of [A-Za-z0-9._~+/-] matched
#           without regard to case (so the letters also take U+0130, U+0131
#           and U+017F, which normalize keeps; NFC maps U+212A to K), then "="
#           padding. The span is the whole match.
#   envval  the upper-case NAME= (TOKEN included), then 1+ non-space.
#   token   (C-F3a) "token", "*_token" or "*_TOKEN" as a word, an optional
#           quote, then ONE space, or ":" / "=" with at most one space on each
#           side, an optional quote, and a 32+ run of [A-Za-z0-9+/] in any case
#           ("token = <run>", '"token": "<run>"', "AGENT_TOKEN: <run>"). A
#           whitespace RUN is no separator: it exists only before normalize has
#           collapsed it, which is what the order test discriminates.
#   wide    (C-F3b) the names in any case, TOKEN included, an optional quote, at
#           most one space around "=" or ":", an optional quote, then 8+
#           characters up to whitespace, a quote, "&", "," or ";" (the
#           transcript scrubber's floor, scripts/transcript_export.py:64, so
#           prose such as "key: sorted" stays).
# For envval, token and wide the span is the value: the name is kept. A name's
# prefix (SECRET_, db_, AWS_SECRET_ACCESS_) is left to the every-start scan, not
# to a pattern group: the text before a name is kept either way, and a nested
# group "(?:[A-Z][A-Z0-9_]*_)*" backtracked exponentially ("A_" * 26 took
# 8.6 s; J1-1-R1 report D-3).
_NAME = r"(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)"
# (form, class, head, value run, value floor, the span starts at the head)
_FORMS = (
    ("sk", "sk", r"sk-", r"[A-Za-z0-9_-]+", 8, True),
    ("bearer", "bearer", r"(?i:bearer)\s+", r"(?i:[A-Za-z0-9._~+/-])+", 16, True),
    ("envval", "envval", _NAME + r"=", r"\S+", 1, False),
    ("token", "token", r"(?i:(?:\b|(?<=_))token[\"']?(?: ?[:=] ?| )?[\"']?)", r"(?i:[A-Za-z0-9+/])+", 32, False),
    ("wide", "envval", r"(?i:" + _NAME + r")[\"']?\s?[:=]\s?[\"']?", r"[^\s\"'&,;]+", 8, False),
)
# Every start in linear time. A zero-width lookahead makes finditer try every
# position, and it matches only the HEAD (a few characters). The value is the
# rest of the maximal run of its class that holds the head's end: a greedy run
# ends at the first character outside its class, so every start inside one run
# shares that end, and the runs are found once per text. (Matching a whole form
# at every start re-reads a long value once per head inside it: 1.26 s for
# 20,000 characters of "API_KEY=", and four times as long per doubling.) The
# head alone ends where the whole form's head ends: its optional quotes,
# spaces, ":" and "=" are outside its value's class, and a required "=" or
# ":" stays in the head.
_DETECTORS = tuple(
    (form, cls, re.compile("(?=(" + head + "))"), re.compile(run), floor, from_head)
    for form, cls, head, run, floor, from_head in _FORMS
)
_PADDING = re.compile(r"=*")
# A private-key block -- the transcript scrubber's label family
# (scripts/transcript_export.py:57-62: PEM, OpenSSH and GnuPG armor) -- from a
# BEGIN line through the first END line that starts at or after its end, or
# through the end of the value when none does (VERIFY-J1-1 F-11). The whole
# block is one span. Every BEGIN line starts one, also a BEGIN line inside
# another block (a block glued to the END line before it shares its dashes).
_PRIVKEY_BEGIN = re.compile(r"(?=(-----BEGIN [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----))")
_PRIVKEY_END = re.compile(r"(?=(-----END [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----))")
# A whole placeholder already in the text is a span of its own class with the
# top rank, so redacting it again never relabels it.
_HELD = re.compile(r"<redacted:(sk|token|bearer|envval|privkey)>")
# Overlapping spans merge; the member with the earliest start names the merged
# span, and at the same start the lowest rank does.
_RANK = {"held": 0, "privkey": 1, "sk": 2, "bearer": 3, "envval": 4, "token": 5, "wide": 6}
# The forms whose value class takes every placeholder character (see _spans).
_THROUGH = ("envval", "wide")
_THROUGH_RANKS = {_RANK[form] for form in _THROUGH}


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


def _cut_placeholder(value: str, end: int, text: str) -> bool:
    # A value that is a proper prefix of a placeholder and ends the text is a
    # placeholder that bound cut: it is no span (the widened form's guard since
    # J1-1-R1). The upper-case NAME= form needs it too, as its value class also
    # takes "<": a whole placeholder after "KEY=" is kept in its own class, so
    # without the guard a cut inside it would become <redacted:envval> in a
    # second decision_state and be cut back to a different prefix.
    return end == len(text) and any(p != value and p.startswith(value) for p in PLACEHOLDERS.values())


def _matches(text: str):
    """Every form matched at every start, as (start, rank, end, class) spans;
    and for envval and wide, whose value class takes every placeholder
    character, every head as (value start, rank, run end, class, form, the
    value meets its floor), with the maximal runs of each such form's class."""
    spans = [(m.start(), _RANK["held"], m.end(), m.group(1)) for m in _HELD.finditer(text)]
    ends = [m.span(1) for m in _PRIVKEY_END.finditer(text)]
    end_starts = [start for start, _ in ends]
    for m in _PRIVKEY_BEGIN.finditer(text):
        i = bisect.bisect_left(end_starts, m.end(1))
        spans.append((m.start(1), _RANK["privkey"], ends[i][1] if i < len(ends) else len(text), "privkey"))
    heads, runs_of = [], {}
    for form, cls, head, run, floor, from_head in _DETECTORS:
        runs = runs_of[form] = [m.span() for m in run.finditer(text)]
        run_starts = [start for start, _ in runs]
        for m in head.finditer(text):
            start = m.end(1)
            i = bisect.bisect_right(run_starts, start) - 1
            end = runs[i][1] if i >= 0 and runs[i][1] > start else start
            ok = end - start >= floor
            if form in _THROUGH:
                ok = ok and not _cut_placeholder(text[start:end], end, text)
                heads.append((start, _RANK[form], end, cls, form, ok))
            elif ok and form == "bearer":
                end = _PADDING.match(text, end).end()
            if ok:
                spans.append((m.start(1) if from_head else start, _RANK[form], end, cls))
    return spans, heads, runs_of


def _regions(spans) -> list[list[int]]:
    """The union of the spans: sorted, disjoint [start, end] intervals. Spans
    that only touch stay apart."""
    regions: list[list[int]] = []
    for start, _rank, end, _cls in sorted(spans):
        if regions and start < regions[-1][1]:
            regions[-1][1] = max(regions[-1][1], end)
        else:
            regions.append([start, end])
    return regions


def _stops(runs, regions, n: int) -> list[tuple[int, int]]:
    """Where a value of one class ends once every region reads as its
    placeholder: a position outside every region and outside the class, or
    the end of the text (n). Sorted, disjoint (start, end) intervals."""
    gaps, prev = [], 0
    for start, end in runs:
        if start > prev:
            gaps.append((prev, start))
        prev = end
    if prev < n:
        gaps.append((prev, n))
    gaps.append((n, n + 1))
    stops, j = [], 0
    for g0, g1 in gaps:
        while j < len(regions) and regions[j][1] <= g0:
            j += 1
        k, cur = j, g0
        while k < len(regions) and regions[k][0] < g1:
            if regions[k][0] > cur:
                stops.append((cur, regions[k][0]))
            cur = max(cur, regions[k][1])
            k += 1
        if cur < g1:
            stops.append((cur, g1))
    return stops


def _spans(text: str) -> list[tuple[int, int, int, str]]:
    """Every span of text, as (start, rank, end, class), with rule 5 read on
    the text as it reads after the replacement."""
    # A placeholder holds no delimiter, and envval's and wide's value classes
    # take all of its characters. So an envval or widened value that meets
    # another span -- one holding a delimiter (a bearer's whitespace, a key
    # block, an upper-case value's quote) or a value under the floor that runs
    # into one -- runs through it and on, as it will read after the
    # replacement, and meets its floor there (a placeholder is longer than
    # either floor). Every head counts, one inside another span too: in
    # "PASSWD=v1bearer <run>'x|key=v2" the upper-case value runs through the
    # bearer and takes v2, as the NAME= pass of d556c9b and fdac751 did. The
    # replacement's output is then its own redaction (idempotence, C3): the
    # value of a head it keeps ends where a placeholder ends. The spans only
    # grow, so the loop ends (J1-1-R4 report: the rounds measured).
    spans, heads, runs_of = _matches(text)
    fixed = [span for span in spans if span[1] not in _THROUGH_RANKS]
    n = len(text)
    while True:
        regions = _regions(spans)
        region_starts = [start for start, _ in regions]
        stops = {form: _stops(runs_of[form], regions, n) for form in _THROUGH}
        grown = list(fixed)
        for start, rank, _end, cls, form, ok in heads:
            i = bisect.bisect_right(stops[form], (start, n + 1)) - 1
            end = start if i >= 0 and stops[form][i][1] > start else stops[form][i + 1][0]
            j = bisect.bisect_right(region_starts, start) - 1
            meets = (j >= 0 and regions[j][1] > start) or (j + 1 < len(regions) and regions[j + 1][0] < end)
            if meets or ok:
                grown.append((start, rank, end, cls))
        if sorted(grown) == sorted(spans):
            return spans
        spans = grown


def _redact_str(text: str) -> str:
    # The union: overlapping spans merge (spans that only touch do not), and
    # each merged span becomes ONE placeholder, of the class of its member with
    # the earliest start (a tie by _RANK). Text outside every span is kept.
    merged: list[list] = []
    for start, _rank, end, cls in sorted(_spans(text)):
        if merged and start < merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end, cls])
    out, pos = [], 0
    for start, end, cls in merged:
        out += [text[pos:start], PLACEHOLDERS[cls]]
        pos = end
    out.append(text[pos:])
    return "".join(out)


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
    when the cut lands inside a placeholder: redact takes no value that is a
    cut placeholder at the end of the text, so the cut prefix stays. (One known
    exception, J1-1-R1 report D-2: a v1 lane whose cut exposes a PIN-shaped
    suffix, which normalize strips on the next pass.)"""
    return bound(question_id, redact(normalize(question_id, state, root)))
