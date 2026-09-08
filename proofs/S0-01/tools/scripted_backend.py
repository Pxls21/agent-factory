#!/usr/bin/env python3
"""S0-01 deterministic scripted model backend — the golden's upstream, BEHIND real OmniRoute.

Owner-sanctioned 2026-09-04 ("a deterministic scripted backend behind a dedicated OmniRoute test
route"), needed because two live runs proved the model route's ACP event structure non-reproducible
(proofs/S0-01/evidence/determinism-live-route.json). Everything under test stays REAL — buzz-acp,
hermes-acp, OmniRoute's routing and credential handling; only the model upstream is scripted.
Not S0-03 evidence. Stdlib only; runs on the PC by absolute path.

OpenAI-compatible surface (what OmniRoute's `openai-compatible` provider speaks):
  GET  /v1/models                -> the two scripted models
  POST /v1/chat/completions      -> `s0-01-pong`: reply "pong" (stream or not), never a tool call
                                    `s0-01-slow`: the same reply streamed as 4 chunks with a delay
                                    between them (the cancellation leg needs a turn that is still
                                    running when session/cancel arrives)
Auth: every request must carry `Authorization: Bearer <token>`; the token is read from
`--token-file` (a 0600 file with `UPSTREAM_TOKEN=...`), never from argv. A request without it gets
401 — this proves the call came through OmniRoute carrying the connection's configured credential.
Authorization equality is == (Bearer <token>X -> 401; Bearer <token> extra -> 401).
/healthz matches the exact path only (/healthzXYZ -> 401 + record).

Framing gate (_framing_gate, first statement of do_GET and do_POST):
  1. headers.defects non-empty (parse error, e.g. 'Content-Length : N') -> 400 + close.
  1b. Header value containing CR/LF (obs-fold, RFC 9112 §5.2) -> 400 + close.
  2. Transfer-Encoding present (any value, any count) -> 411 + close.
  3. Duplicate Content-Length -> 400 + close.
  4. Single Content-Length must match [0-9]+ (no sign, underscore, exponent);
     leading OWS in the field value is stripped by the parser
     (Content-Length:  5 -> "5", accepted); trailing OWS is rejected (stricter
     than RFC 9110 §5.5, fail-closed).
     POST with int > MAX_CONTENT_LENGTH -> 400 + close;
     GET with int > 0 -> read min(int, MAX) bytes, 400 + close;
     GET with int == 0 -> accepted.
  5. Expect header present (any value, including empty) -> 417 + close
     (prevents interim 100-continue).
  Unsupported methods (not GET/POST) receive 501 from http.server's
  handle_one_request before dispatch (proven safe: no tail served,
  Connection: close sent).
  Every rejection sends Connection: close and never parses a tail as a second request.

Credential screen (_normal_forms / _carries_secret): breadth-first closure of
  {unquote, unquote_plus, lower, utf8_redecode_lenient, strip_invis}
  applied to each item, deduplicated, bounded at depth 5.
  _normal_forms returns (forms, saturated); if saturated is False (bound
  exceeded) the screen fails closed (True) — the depth bound affects
  false-positive breadth, not detection.
  strip_invis drops every code point in _INVIS_PINNED — a frozenset parsed
  once at import from the committed range string _INVIS_RANGES (generated from
  UCD 15.1.0, /usr/bin/python3.13 on this sandbox; 4315 code points; categories
  {Cf, Cs, Cc, Mn, Me, Zs, Zl, Zp} plus _INVISIBLE_EXTRA).  Unassigned code
  points (Cn) are OUT of the class EXCEPT ten permanently-reserved BMP slots
  (U+2065 and U+FFF0-U+FFF8) that sit inside Default_Ignorable runs, render
  as nothing, and can never be assigned to a visible character (D5k item 3).
  All other Cn: render as tofu (visible); a future assignment enters through
  table regeneration, never silently (D5i-F11 ruling).
  The table is a property of the repo, not the runtime (D5i-F3).
  unicodedata is NOT imported at runtime.  This subsumes the former
  strip_ws, strip_zwc, and strip_ctl ops (all fully redundant, removed D5i).
  utf8_redecode_lenient (errors="ignore") is the sole re-decode path in
  both closure and oracle; it handles valid UTF-8 byte-view recovery and
  junk bytes between token halves in already-decoded JSON leaves (D5i).
  unquote_drop / unquote_plus_drop (errors="ignore") are the percent-decode
  paths; they drop invalid UTF-8 percent-encoded bytes instead of replacing
  them with U+FFFD (which would survive strip_invis as category So).
  The op count stays at 5 (they replace the default-errors variants).
  _has_invalid_utf8_bytes rejects the request (fail closed) when the latin-1
  view of a BYTE-VIEW field (path, header names, header values, raw body)
  contains bytes >= 0x80 that are not part of a valid UTF-8 sequence (D5h-F1).
  It does NOT run on parsed-JSON leaves or on the serialized body_str when
  the parsed body is already a str (byte_view=False, D5i item 1) — those
  strings are already decoded and re-encoding them manufactures bytes that
  were never on the wire.
  Confusable substitution (homoglyphs) is out of contract — the token's
  bytes are then not in the record.
  Accepted risk (D5d-F12, restored): junk like %25252541 triggers the
  bound-exceeded path and blanks the record (false positive).
  Bounded worst case, per vector and per venue (cost_probe.py, min of 5 at
  1000 KB): the named vector is a MAX_CONTENT_LENGTH (1 MiB) body carrying a
  bound-exceeding token (column `bound-body`) — 1.86 s on the PC, 1.03 s in the
  sandbox.  An ordinary 1 MiB body (column `ordinary`) costs 0.72 s / 0.39 s.
  Harness style is not the factor: a raw socket and http.client agree within
  0.99-1.06x over three runs of both vectors in one sandbox window (D5m).
  It remains bounded by handler timeout (30 s) and ThreadingHTTPServer (one
  slow request does not block others).  A DoS budget is the owner's call.
  The screen is applied per item (path, header names, header values, serialized
  JSON body, every parsed JSON string — keys AND values — and raw body);
  cross-sink splits are out of contract by design.
  A body the parser cannot decode gets 400 + close.
  F11: records are written with allow_nan=False after coercing non-finite
  floats to the string "<non-finite>". F10: _read_body refuses a JSON nesting
  deeper than MAX_JSON_DEPTH (32) before parsing (400 + close, no record, on
  every interpreter) and _iter_json_strings is iterative to avoid the same.

Not recorded: GET /healthz (operational, pre-auth); any gate rejection (TE, dup CL,
  malformed CL, oversized CL, GET with CL > 0, defects, obs-fold, Expect,
  JSON depth > MAX_JSON_DEPTH, short body). These all close the connection.  Duplicate non-framing headers collapse to the last value in
  the record (email.message.Message.items() yields all, but dict() takes the last --
  documented, not a defect; the dropped duplicate values are discarded and
  unrecoverable from the record).
Determinism: identical request bodies -> byte-identical responses (fixed ids, timestamps, usage).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
import re
import stat
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, unquote_plus

MODELS = ("s0-01-pong", "s0-01-slow")
REPLY = "pong"
SLOW_CHUNKS = ("po", "n", "g", "")  # "" = the final content-less finish chunk
FIXED_CREATED = 1788566400  # 2026-09-05T00:00:00Z, frozen
FIXED_USAGE = {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
MAX_CONTENT_LENGTH = 1_048_576
# Deepest JSON nesting a body may carry. CPython's C decoder accepts depth 1000 on 3.12/3.13 (only 3.11 raised
# RecursionError there), so a depth bomb then crashed the handler in the record serializer with NO response
# (CI runs 87-89, 2026-09-06). The gate is a linear scan of the raw bytes, interpreter-independent.
MAX_JSON_DEPTH = 32
# Sentinel object for _read_body control flow (L3: never a bare string — a client
# POSTing the JSON document "BAD_CL" must not collide with the sentinel).
_BAD_CL = object()
# D5m-F7: the ONE spelling of the unusable-record-slot reason — the 500 body, the JSON
# log line and the test all read this constant, so the message cannot drift between them.
_RECORD_SLOT_REASON = "record slot is not a regular file"
# Credential-bearing header names (lowercased) to drop from records (V-c F10).
_CREDENTIAL_HEADERS = frozenset({
    "authorization", "proxy-authorization", "x-api-key", "api-key",
    "x-auth-token", "cookie",
})
# The invisible/zero-width class, pinned to UCD 15.1.0: every code point whose
# category is in {Cf, Cs, Cc, Mn, Me, Zs, Zl, Zp} plus _INVISIBLE_EXTRA
# (Lo/So fillers: U+115F, U+1160, U+3164, U+FFA0, U+2800, U+180E;
#  permanently-reserved BMP: U+2065, U+FFF0-FFF8).
# Generated by: /usr/bin/python3.13 (generator recorded verbatim in
# _parse_invis_ranges docstring).
# (the full generator is recorded in the docstring of _parse_invis_ranges).
# Cn (unassigned) is OUT except 10 permanently-reserved BMP slots in _INVISIBLE_EXTRA.
_INVIS_CATEGORIES = frozenset({"Cf", "Cs", "Cc", "Mn", "Me", "Zs", "Zl", "Zp"})
_INVISIBLE_EXTRA = frozenset({
    0x115F, 0x1160, 0x3164, 0xFFA0, 0x2800, 0x180E,
    # Permanently-reserved BMP slots inside Default_Ignorable runs, rendered
    # as nothing by several engines, never assignable to a visible character
    # (D5j-F15 / D5k item 3):
    0x2065,  # inside U+2060-U+2064 invisible-operator run
    0xFFF0, 0xFFF1, 0xFFF2, 0xFFF3, 0xFFF4,  # U+FFF0-FFF8
    0xFFF5, 0xFFF6, 0xFFF7, 0xFFF8,
})
_INVIS_RANGES = (
    "0000-0020 007F-00A0 00AD 0300-036F 0483-0489 0591-05BD 05BF 05C1-05C2 "
    "05C4-05C5 05C7 0600-0605 0610-061A 061C 064B-065F 0670 06D6-06DD "
    "06DF-06E4 06E7-06E8 06EA-06ED 070F 0711 0730-074A 07A6-07B0 07EB-07F3 "
    "07FD 0816-0819 081B-0823 0825-0827 0829-082D 0859-085B 0890-0891 "
    "0898-089F 08CA-0902 093A 093C 0941-0948 094D 0951-0957 0962-0963 0981 "
    "09BC 09C1-09C4 09CD 09E2-09E3 09FE 0A01-0A02 0A3C 0A41-0A42 0A47-0A48 "
    "0A4B-0A4D 0A51 0A70-0A71 0A75 0A81-0A82 0ABC 0AC1-0AC5 0AC7-0AC8 0ACD "
    "0AE2-0AE3 0AFA-0AFF 0B01 0B3C 0B3F 0B41-0B44 0B4D 0B55-0B56 0B62-0B63 "
    "0B82 0BC0 0BCD 0C00 0C04 0C3C 0C3E-0C40 0C46-0C48 0C4A-0C4D 0C55-0C56 "
    "0C62-0C63 0C81 0CBC 0CBF 0CC6 0CCC-0CCD 0CE2-0CE3 0D00-0D01 0D3B-0D3C "
    "0D41-0D44 0D4D 0D62-0D63 0D81 0DCA 0DD2-0DD4 0DD6 0E31 0E34-0E3A "
    "0E47-0E4E 0EB1 0EB4-0EBC 0EC8-0ECE 0F18-0F19 0F35 0F37 0F39 0F71-0F7E "
    "0F80-0F84 0F86-0F87 0F8D-0F97 0F99-0FBC 0FC6 102D-1030 1032-1037 "
    "1039-103A 103D-103E 1058-1059 105E-1060 1071-1074 1082 1085-1086 108D "
    "109D 115F-1160 135D-135F 1680 1712-1714 1732-1733 1752-1753 1772-1773 "
    "17B4-17B5 17B7-17BD 17C6 17C9-17D3 17DD 180B-180F 1885-1886 18A9 "
    "1920-1922 1927-1928 1932 1939-193B 1A17-1A18 1A1B 1A56 1A58-1A5E 1A60 "
    "1A62 1A65-1A6C 1A73-1A7C 1A7F 1AB0-1ACE 1B00-1B03 1B34 1B36-1B3A 1B3C "
    "1B42 1B6B-1B73 1B80-1B81 1BA2-1BA5 1BA8-1BA9 1BAB-1BAD 1BE6 1BE8-1BE9 "
    "1BED 1BEF-1BF1 1C2C-1C33 1C36-1C37 1CD0-1CD2 1CD4-1CE0 1CE2-1CE8 1CED "
    "1CF4 1CF8-1CF9 1DC0-1DFF 2000-200F 2028-202F 205F-206F "
    "20D0-20F0 2800 2CEF-2CF1 2D7F 2DE0-2DFF 3000 302A-302D 3099-309A 3164 "
    "A66F-A672 A674-A67D A69E-A69F A6F0-A6F1 A802 A806 A80B A825-A826 A82C "
    "A8C4-A8C5 A8E0-A8F1 A8FF A926-A92D A947-A951 A980-A982 A9B3 A9B6-A9B9 "
    "A9BC-A9BD A9E5 AA29-AA2E AA31-AA32 AA35-AA36 AA43 AA4C AA7C AAB0 "
    "AAB2-AAB4 AAB7-AAB8 AABE-AABF AAC1 AAEC-AAED AAF6 ABE5 ABE8 ABED "
    "D800-DFFF FB1E FE00-FE0F FE20-FE2F FEFF FFA0 FFF0-FFFB 101FD 102E0 "
    "10376-1037A 10A01-10A03 10A05-10A06 10A0C-10A0F 10A38-10A3A 10A3F "
    "10AE5-10AE6 10D24-10D27 10EAB-10EAC 10EFD-10EFF 10F46-10F50 10F82-10F85 "
    "11001 11038-11046 11070 11073-11074 1107F-11081 110B3-110B6 110B9-110BA "
    "110BD 110C2 110CD 11100-11102 11127-1112B 1112D-11134 11173 11180-11181 "
    "111B6-111BE 111C9-111CC 111CF 1122F-11231 11234 11236-11237 1123E 11241 "
    "112DF 112E3-112EA 11300-11301 1133B-1133C 11340 11366-1136C 11370-11374 "
    "11438-1143F 11442-11444 11446 1145E 114B3-114B8 114BA 114BF-114C0 "
    "114C2-114C3 115B2-115B5 115BC-115BD 115BF-115C0 115DC-115DD 11633-1163A "
    "1163D 1163F-11640 116AB 116AD 116B0-116B5 116B7 1171D-1171F 11722-11725 "
    "11727-1172B 1182F-11837 11839-1183A 1193B-1193C 1193E 11943 119D4-119D7 "
    "119DA-119DB 119E0 11A01-11A0A 11A33-11A38 11A3B-11A3E 11A47 11A51-11A56 "
    "11A59-11A5B 11A8A-11A96 11A98-11A99 11C30-11C36 11C38-11C3D 11C3F "
    "11C92-11CA7 11CAA-11CB0 11CB2-11CB3 11CB5-11CB6 11D31-11D36 11D3A "
    "11D3C-11D3D 11D3F-11D45 11D47 11D90-11D91 11D95 11D97 11EF3-11EF4 "
    "11F00-11F01 11F36-11F3A 11F40 11F42 13430-13440 13447-13455 16AF0-16AF4 "
    "16B30-16B36 16F4F 16F8F-16F92 16FE4 1BC9D-1BC9E 1BCA0-1BCA3 "
    "1CF00-1CF2D 1CF30-1CF46 1D167-1D169 1D173-1D182 1D185-1D18B 1D1AA-1D1AD "
    "1D242-1D244 1DA00-1DA36 1DA3B-1DA6C 1DA75 1DA84 1DA9B-1DA9F 1DAA1-1DAAF "
    "1E000-1E006 1E008-1E018 1E01B-1E021 1E023-1E024 1E026-1E02A 1E08F "
    "1E130-1E136 1E2AE 1E2EC-1E2EF 1E4EC-1E4EF 1E8D0-1E8D6 1E944-1E94A "
    "E0001 E0020-E007F E0100-E01EF"
)


def _parse_invis_ranges(s: str) -> frozenset[int]:
    """Parse the hex range string into a frozenset of code points.

    Generator (run under /usr/bin/python3.13, unicodedata.unidata_version 15.1.0):
        import unicodedata
        cats = frozenset({'Cf','Cs','Cc','Mn','Me','Zs','Zl','Zp'})
        extra = {0x115F, 0x1160, 0x3164, 0xFFA0, 0x2800, 0x180E,
                 0x2065, 0xFFF0, 0xFFF1, 0xFFF2, 0xFFF3, 0xFFF4,
                 0xFFF5, 0xFFF6, 0xFFF7, 0xFFF8}
        members = set()
        for cp in range(0x110000):
            if unicodedata.category(chr(cp)) in cats or cp in extra:
                members.add(cp)
        srt = sorted(members)
        ranges, start, end = [], srt[0], srt[0]
        for cp in srt[1:]:
            if cp == end + 1:
                end = cp
            else:
                ranges.append((start, end))
                start = end = cp
        ranges.append((start, end))
        parts = []
        for s, e in ranges:
            parts.append(f'{s:04X}' if s == e else f'{s:04X}-{e:04X}')
        print(' '.join(parts))
    """
    result = set()
    for part in s.split():
        if '-' in part:
            lo, hi = part.split('-')
            for cp in range(int(lo, 16), int(hi, 16) + 1):
                result.add(cp)
        else:
            result.add(int(part, 16))
    return frozenset(result)


_INVIS_PINNED = _parse_invis_ranges(_INVIS_RANGES)


class _ParseError(Exception):
    """Raised by _read_body when JSON parsing fails; carries the raw bytes."""
    def __init__(self, raw: bytes):
        self.raw = raw


def _has_invalid_utf8_bytes(s: str) -> bool:
    """True if *s* contains bytes >= 0x80 (in its latin-1 view) that do not
    form a valid UTF-8 sequence.

    Called ONLY on byte-view sinks (headers, path/query, raw body) where
    ``http.server`` hands over a latin-1 view of wire bytes.  Invalid UTF-8
    in those fields has no legitimate producer (this fixture serves ONE
    pinned client through OmniRoute).  NOT called on parsed-JSON leaves
    (``json.loads`` has already decoded them — re-encoding manufactures
    bytes that were never on the wire; D5h-F1 / D5i item 1).
    A string that cannot latin-1-encode is not a byte view and passes.
    """
    try:
        raw = s.encode("latin-1")
    except UnicodeEncodeError:
        return False  # not a byte view — passes
    if not any(b >= 0x80 for b in raw):
        return False  # pure ASCII — no invalid UTF-8 possible
    try:
        raw.decode("utf-8")
        return False  # valid UTF-8
    except UnicodeDecodeError:
        return True   # invalid UTF-8 bytes present


def _normal_forms(s: str) -> tuple[frozenset[str], bool]:
    """Breadth-first closure of {unquote, unquote_plus, lower,
    utf8_redecode_lenient, strip_invis}.

    Returns (forms, saturated).  *saturated* is True when the frontier was
    exhausted (all reachable forms found); False when the depth bound (5) was
    exceeded — the caller fails closed on ``not saturated``.

    Accepted risk (D5d-F12, restored): junk like ``%25252541`` triggers the
    bound-exceeded path and blanks the record (false positive).

    strip_invis subsumes the former strip_ws, strip_zwc, and strip_ctl ops —
    all three are fully redundant under its pinned table and were removed
    (D5i).  utf8_redecode_lenient (errors="ignore") is the sole re-decode
    path in both closure and oracle; the strict utf8_redecode was removed
    (D5i follow-up: subsumed, no test could pin it).
    unquote_drop / unquote_plus_drop replace the default-errors variants
    so that an invalid percent-encoded UTF-8 byte (e.g. %80) is DROPPED
    rather than replaced with U+FFFD (which would survive strip_invis as
    category So).  Strictly wider in the token-found arm; the saturation
    arm is not monotone: dropping bytes shortens forms and can let a
    closure saturate that previously exceeded the bound — measured 105 of
    20 000 percent-dense vectors move from fail-closed to served, the
    depth-6 oracle confirms the token absent in all of them (D5j-F6).
    """
    def strip_invis(x):
        """Drop every code point in _INVIS_PINNED (the committed UCD-15.1
        table).  The C1 arm (U+0080-U+009F) is doubly covered: strip_invis
        catches it at depth 1, and utf8_redecode_lenient recovers the token
        through the lone 0x80 byte at depth 2 (D5i CTL_PARTIAL_noC1
        equivalence)."""
        return "".join(c for c in x if ord(c) not in _INVIS_PINNED)
    def utf8_redecode_lenient(x):
        """latin-1 re-decode (lenient, errors="ignore"): recovers real
        Unicode from byte-view latin-1 chars and drops invalid bytes.
        Sole re-decode path in both closure and oracle (D5i follow-up)."""
        try:
            return x.encode("latin-1").decode("utf-8", errors="ignore")
        except UnicodeEncodeError:
            return x
    def unquote_drop(x):
        """Percent-decode (errors="ignore"): drops invalid UTF-8 percent-
        encoded bytes instead of replacing them with U+FFFD (D5i-F2)."""
        return unquote(x, errors="ignore")
    def unquote_plus_drop(x):
        """Percent-decode with + as space (errors="ignore"): same drop
        semantics as unquote_drop (D5i-F2)."""
        return unquote_plus(x, errors="ignore")
    ops = (unquote_drop, unquote_plus_drop, str.lower, utf8_redecode_lenient, strip_invis)
    frontier = {s}
    seen = {s}
    for _depth in range(5):
        new_frontier = set()
        for form in frontier:
            for op in ops:
                v = op(form)
                if v not in seen:
                    seen.add(v)
                    new_frontier.add(v)
        if not new_frontier:
            return frozenset(seen), True      # saturated
        frontier = new_frontier
    return frozenset(seen), False             # bound exceeded — keep what we found


def _json_nesting_depth(raw: bytes) -> int:
    """Maximum bracket nesting of a JSON document, counted on the raw bytes outside strings.

    Runs BEFORE json.loads so the bound does not depend on the interpreter's recursion behaviour.
    A malformed document still gets a number; json.loads decides validity afterwards.
    """
    depth = max_depth = 0
    in_string = escaped = False
    for b in raw:
        if in_string:
            if escaped:
                escaped = False
            elif b == 0x5C:      # backslash
                escaped = True
            elif b == 0x22:      # closing quote
                in_string = False
        elif b == 0x22:
            in_string = True
        elif b in (0x5B, 0x7B):  # [ {
            depth += 1
            if depth > max_depth:
                max_depth = depth
        elif b in (0x5D, 0x7D):  # ] }
            depth -= 1
    return max_depth


def _iter_json_strings(obj):
    """Yield every string leaf (keys and values) from a parsed JSON value.

    F1: json.dumps re-escapes whitespace chars (tab -> \\t, etc.), hiding a
    whitespace-split token.  Walking the parsed values preserves the actual
    whitespace characters that json.loads decoded.
    """
    stack = [obj]
    while stack:
        item = stack.pop()
        if isinstance(item, str):
            yield item
        elif isinstance(item, dict):
            for k, v in item.items():
                stack.append(v)
                yield k
        elif isinstance(item, list):
            stack.extend(item)


def _refuse_non_regular(path: Path) -> bool:
    """True when *path* names something that exists but is not a regular file.

    D5m-F2/F7, the AF-AP-30 read class: the backend must never open a path it has
    not classified first — an open() on a FIFO blocks forever, and write_text()
    through a dangling symlink creates a file somewhere the caller did not name.
    lstat answers "does this NAME exist" (a dangling symlink does); stat follows,
    so a symlink to a regular file is accepted and a dangling one is refused.
    Neither call opens the path, so a FIFO cannot block here.
    """
    try:
        os.lstat(path)
    except OSError:
        return False                       # nothing there: the caller creates it
    try:
        return not stat.S_ISREG(os.stat(path).st_mode)
    except OSError:
        return True                        # dangling symlink, ELOOP, unreadable target


class _RecordSlotError(Exception):
    """Raised by State.record when the next record slot is not a regular file."""
    def __init__(self, path: Path):
        super().__init__(str(path))
        self.path = path


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def load_token(path: Path) -> str:
    for line in path.read_text().splitlines():
        if line.startswith("UPSTREAM_TOKEN="):
            token = line.split("=", 1)[1].strip().strip('"')
            if token:
                return token
    raise SystemExit(f"scripted_backend: no UPSTREAM_TOKEN= line in {path}")


def _validate_slow_delay(s):
    """type= callable for --slow-delay: finite non-negative float (R5-D5-F7)."""
    try:
        v = float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid float: {s!r}")
    if not (math.isfinite(v) and v >= 0):
        print(f"scripted_backend: --slow-delay {v} "
              f"must be a finite number >= 0", file=sys.stderr)
        raise SystemExit(2)
    return v


def _json_safe(o):
    """F11: coerce non-finite floats to the string "<non-finite>" before
    serialising with allow_nan=False, so the record is always valid JSON.
    Iterative (F10): no recursion risk regardless of nesting depth.
    F12: copy-on-write — never mutates the caller's object."""
    if isinstance(o, float) and not math.isfinite(o):
        return "<non-finite>"
    if not isinstance(o, (dict, list)):
        return o
    root = dict(o) if isinstance(o, dict) else list(o)
    stack = [root]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            for k in list(item):
                v = item[k]
                if isinstance(v, float) and not math.isfinite(v):
                    item[k] = "<non-finite>"
                elif isinstance(v, dict):
                    c = dict(v); item[k] = c; stack.append(c)
                elif isinstance(v, list):
                    c = list(v); item[k] = c; stack.append(c)
        elif isinstance(item, list):
            for i in range(len(item)):
                v = item[i]
                if isinstance(v, float) and not math.isfinite(v):
                    item[i] = "<non-finite>"
                elif isinstance(v, dict):
                    c = dict(v); item[i] = c; stack.append(c)
                elif isinstance(v, list):
                    c = list(v); item[i] = c; stack.append(c)
    return root


class State:
    def __init__(self, token: str, record_dir: Path, slow_delay: float):
        self.token = token
        self.record_dir = record_dir
        self.slow_delay = slow_delay
        self.seq = 0
        self.lock = threading.Lock()

    def _carries_secret(self, s: str, *, byte_view: bool) -> bool:
        """True if the configured token appears in ANY normal form of *s*,
        or if the closure did not saturate (fail closed), or — when
        *byte_view* is True — if *s* contains invalid UTF-8 bytes in its
        latin-1 view (fail closed — D5h-F1).

        *byte_view* is True for strings ``http.server`` hands over as a
        latin-1 view of wire bytes (header names, header values, path/query,
        the raw body): there the invalid-UTF-8 precheck is correct.
        *byte_view* is False for strings ``json.loads`` has already decoded
        (the parsed-JSON leaf walk): re-encoding them to latin-1 manufactures
        bytes that were never on the wire, and rejects ordinary accented text
        such as ``cafe`` + U+00E9 (D5h-F1 / D5i item 1).

        Confusable substitution (homoglyphs) is out of contract — the
        token's bytes are then not in the record.
        """
        if byte_view and _has_invalid_utf8_bytes(s):
            return True                       # fail closed on invalid UTF-8
        t = self.token
        forms, saturated = _normal_forms(s)
        if any(t in f for f in forms):
            return True
        return not saturated                  # actually fail closed

    def record(self, method: str, path: str, headers, body,
               remote_addr: str, bearer_token: str | None,
               *, raw_body: bytes | None = None) -> tuple[int, bool]:
        with self.lock:
            self.seq += 1
            n = self.seq
        now = datetime.datetime.now(datetime.timezone.utc)
        received_at = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond:06d}Z"
        mono_ns = time.monotonic_ns()
        # P1/V5/AF-AP-35: credential-leak check at the ONE recording boundary.
        # _carries_secret checks: the closure of {unquote, unquote_plus, lower,
        # utf8_redecode_lenient, strip_invis} at depth 5; fails closed when
        # the bound is exceeded.
        # Keyed on the configured secret, not the request-supplied bearer,
        # so a request without Authorization is still screened (4-F1/6-F3).
        # M12: exempts ONLY 'authorization' by name.
        leaked = False
        if path and self._carries_secret(path, byte_view=True):
            leaked = True
        for k, v in headers.items():
            if k.lower() != "authorization":
                if self._carries_secret(str(k), byte_view=True) or self._carries_secret(str(v), byte_view=True):
                    leaked = True
        if body is not None:
            body_str = body if isinstance(body, str) else json.dumps(body)
            # byte_view=False: body_str is either a decoded str from json.loads
            # (top-level JSON string) or ASCII from json.dumps — neither is a
            # latin-1 view of wire bytes (D5i-F1).
            if self._carries_secret(body_str, byte_view=False):
                leaked = True
            # F1: json.dumps re-escapes whitespace chars to \t \n etc., hiding
            # a whitespace-split token. Walk parsed string values directly.
            # byte_view=False: json.loads already decoded these; the precheck
            # must NOT re-encode them (D5h-F1 / D5i item 1).
            if not leaked and not isinstance(body, str):
                for s in _iter_json_strings(body):
                    if self._carries_secret(s, byte_view=False):
                        leaked = True
                        break
        if raw_body and self._carries_secret(raw_body.decode("latin-1"), byte_view=True):
            leaked = True
        if leaked:
            rec_path = None
            clean = {}
            rec_body = {"credential_in_unexpected_location": True}
            auth_fp = None
        else:
            rec_path = path
            # V-c F3: lowercase keys; V-c F10: drop all credential-bearing headers
            clean = {k.lower(): v for k, v in headers.items()
                     if k.lower() not in _CREDENTIAL_HEADERS}
            rec_body = body
            auth_fp = hashlib.sha256(bearer_token.encode()).hexdigest() if bearer_token else None
        self.record_dir.mkdir(parents=True, exist_ok=True)
        # D5m-F7: the next slot name is fully predictable, so anything already at it is
        # attacker-chosen. write_text() on a FIFO blocks the handler thread forever
        # (VERIFY-D5l F7: client TimeoutError, no response, no record, a gap in seq).
        # Classify without opening; the handler turns this into a 500 + one JSON log line.
        slot = self.record_dir / f"{n:06d}.json"
        if _refuse_non_regular(slot):
            raise _RecordSlotError(slot)
        slot.write_text(json.dumps(
            {"seq": n, "method": method, "path": rec_path, "headers": clean,
             "body": _json_safe(rec_body), "received_at": received_at, "t_mono_ns": mono_ns,
             "remote_addr": remote_addr, "authorization_fingerprint": auth_fp},
            indent=2, sort_keys=True, allow_nan=False) + "\n")
        return n, leaked


def make_handler(state: State):
    class Handler(BaseHTTPRequestHandler):
        server_version = "s0-01-scripted/1"
        protocol_version = "HTTP/1.1"
        timeout = 30  # L4: bound handler threads so an incomplete body cannot block forever

        def log_message(self, fmt, *args):  # quiet; the record dir is the log
            return

        # -- framing gate (allow-list) ----------------------------------------
        def _reject(self, code: int):
            """Send a bare rejection response with Connection: close."""
            self.send_response(code)
            self.send_header("Connection", "close")
            self.end_headers()

        def _framing_gate(self) -> bool:
            """Unified allow-list framing gate.  Returns True if rejected
            (response sent, connection closed).  Called as the FIRST statement
            of do_GET and do_POST."""
            # 1. Header parse defects (e.g. 'Content-Length : N' with space before colon)
            if self.headers.defects:
                self._reject(400)
                return True
            # 1b. Obs-fold (RFC 9112 §5.2): any header value with CR/LF is a
            #     framing defect — a folded CL/TE is invisible to later arms.
            for _k, _v in self.headers.items():
                if '\r' in _v or '\n' in _v:
                    self._reject(400)
                    return True
            # 2. Transfer-Encoding present (any value, any count)
            if self.headers.get_all("Transfer-Encoding"):
                self._reject(411)
                return True
            # 3. Duplicate Content-Length
            cls = self.headers.get_all("Content-Length") or []
            if len(cls) > 1:
                self._reject(400)
                return True
            # 4. Single Content-Length: must be [0-9]+ and within bounds
            if len(cls) == 1:
                cl = cls[0]
                if not re.fullmatch(r"[0-9]+", cl):
                    self._reject(400)
                    return True
                n = int(cl)
                if self.command == "POST":
                    if n > MAX_CONTENT_LENGTH:
                        self._reject(400)
                        return True
                else:  # GET
                    if n > 0:
                        self.rfile.read(min(n, MAX_CONTENT_LENGTH))
                        self._reject(400)
                        return True
            # 5. Expect header present (any value, including empty — F21/F2)
            if self.headers.get_all("Expect") is not None:
                self._reject(417)
                return True
            # Unsupported methods (not GET/POST) receive 501 from http.server's
            # handle_one_request before dispatch (proven safe: no tail served,
            # Connection: close sent). No gate arm needed here.
            return False

        def handle_expect_100(self):
            """Override: suppress 100-continue interim response;
            _framing_gate sends 417 instead."""
            return True  # proceed to do_ method; gate will reject

        # -- helpers -------------------------------------------------------
        def _send_json(self, code: int, obj, extra=None):
            data = (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(data)

        def _error(self, code: int, message: str, err_type: str, err_code: str):
            self._send_json(code, {"error": {"message": message, "type": err_type, "code": err_code}},
                            extra={"Connection": "close"})

        def _authorized(self) -> bool:
            auth = self.headers.get("Authorization", "")
            return auth == f"Bearer {state.token}"

        def _bearer_token(self):
            auth = self.headers.get("Authorization", "")
            return auth[7:] if auth.startswith("Bearer ") else None

        def _record(self, *args, **kwargs):
            """state.record() at the single boundary, with the unusable-slot path named.

            D5m-F7: returns (seq, leaked), or None when the next record slot is not a
            regular file — in that case a 500 naming the reason has already been sent and
            one JSON line has been logged.  Never blocks, never skips silently.
            """
            try:
                return state.record(*args, **kwargs)
            except _RecordSlotError as e:
                print(json.dumps({"event": "record_slot_refused",
                                  "reason": _RECORD_SLOT_REASON,
                                  "path": str(e.path)}, sort_keys=True),
                      file=sys.stderr, flush=True)
                self._error(500, _RECORD_SLOT_REASON, "server_error", "record_slot_unusable")
                return None

        def _read_body(self):
            self._last_raw_body = None
            cl_raw = self.headers.get("Content-Length")
            if cl_raw is None:
                return None
            # Defense-in-depth: gate already validated, but keep for safety
            if not re.fullmatch(r"[0-9]+", cl_raw or ""):
                return _BAD_CL
            length = int(cl_raw)
            if length < 0 or length > MAX_CONTENT_LENGTH:
                return _BAD_CL
            raw = self.rfile.read(length) if length else b""
            # A18: short body (client hung up early) -> _BAD_CL -> 400, no record
            if length and len(raw) < length:
                return _BAD_CL
            self._last_raw_body = raw if raw else None
            if not raw:
                return None
            # F10 (venue-independent): a nesting deeper than MAX_JSON_DEPTH is refused BEFORE parsing —
            # 400 + close, no record — on every interpreter.
            if _json_nesting_depth(raw) > MAX_JSON_DEPTH:
                return _BAD_CL
            try:
                return json.loads(raw.decode())
            except (ValueError, UnicodeDecodeError) as e:
                raise _ParseError(raw) from e

        # -- routes --------------------------------------------------------
        def do_GET(self):
            if self._framing_gate():
                return
            if self.path.split("?", 1)[0] == "/healthz":
                with state.lock:
                    count = state.seq
                return self._send_json(200, {"ok": True, "models": list(MODELS), "records": count})
            bearer = self._bearer_token()
            body = None
            # Record at the single boundary; credential leak handled inside record()
            rec = self._record("GET", self.path, self.headers, body,
                               self.client_address[0], bearer, raw_body=None)
            if rec is None:
                return
            _seq, leaked = rec
            if leaked:
                return self._error(400, "credential in unexpected location",
                                   "invalid_request_error", "bad_request")
            if not self._authorized():
                return self._error(401, "missing or invalid upstream bearer", "authentication_error", "unauthorized")
            if self.path.split("?", 1)[0] == "/v1/models":
                return self._send_json(200, {"object": "list", "data": [
                    {"id": m, "object": "model", "created": FIXED_CREATED, "owned_by": "s0-01-scripted"} for m in MODELS]})
            return self._error(404, f"no route {self.path}", "invalid_request_error", "not_found")

        def do_POST(self):
            if self._framing_gate():
                return
            bearer = self._bearer_token()
            try:
                body = self._read_body()
            except _ParseError as e:
                rec = self._record(
                    "POST", self.path, self.headers, "<invalid json>",
                    self.client_address[0], bearer, raw_body=e.raw)
                if rec is None:
                    return
                _seq, leaked = rec
                if leaked:
                    return self._error(400, "credential in unexpected location",
                                       "invalid_request_error", "bad_request")
                return self._error(400, "body is not JSON", "invalid_request_error", "bad_request")
            # L3: sentinels are module-level objects compared with `is`
            if body is _BAD_CL:
                self._reject(400)
                return
            # Record at the single boundary; credential leak handled inside record()
            rec = self._record("POST", self.path, self.headers, body,
                               self.client_address[0], bearer,
                               raw_body=self._last_raw_body)
            if rec is None:
                return
            _seq, leaked = rec
            if leaked:
                return self._error(400, "credential in unexpected location",
                                   "invalid_request_error", "bad_request")
            if not self._authorized():
                return self._error(401, "missing or invalid upstream bearer", "authentication_error", "unauthorized")
            if self.path.split("?", 1)[0] != "/v1/chat/completions":
                return self._error(404, f"no route {self.path}", "invalid_request_error", "not_found")
            if not isinstance(body, dict) or not isinstance(body.get("messages"), list):
                return self._error(400, "messages: Expected array", "invalid_request_error", "bad_request")
            model = body.get("model")
            if model not in MODELS:
                return self._error(404, f"model {model!r} is not served here", "invalid_request_error", "model_not_found")
            if body.get("stream"):
                return self._stream(model)
            return self._send_json(200, {
                "id": "chatcmpl-s0-01", "object": "chat.completion", "created": FIXED_CREATED, "model": model,
                "choices": [{"index": 0, "message": {"role": "assistant", "content": REPLY}, "finish_reason": "stop"}],
                "usage": FIXED_USAGE})

        def _stream(self, model: str):
            chunks = SLOW_CHUNKS if model == "s0-01-slow" else (REPLY, "")
            delay = state.slow_delay if model == "s0-01-slow" else 0.0
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()

            def emit(obj):
                self.wfile.write(b"data: " + json.dumps(obj, sort_keys=True, separators=(",", ":")).encode() + b"\n\n")
                self.wfile.flush()

            base = {"id": "chatcmpl-s0-01", "object": "chat.completion.chunk", "created": FIXED_CREATED, "model": model}
            emit({**base, "choices": [{"index": 0, "delta": {"role": "assistant", "content": ""}, "finish_reason": None}]})
            for i, piece in enumerate(chunks):
                if delay and i:
                    time.sleep(delay)
                if piece == "":
                    emit({**base, "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}], "usage": FIXED_USAGE})
                else:
                    emit({**base, "choices": [{"index": 0, "delta": {"content": piece}, "finish_reason": None}]})
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
            # Connection: close header at _stream:704 already sets
            # close_connection (CPython http.server; D5i-F7).

    return Handler


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bind", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=20201)
    ap.add_argument("--token-file", required=True, type=Path)
    ap.add_argument("--record-dir", required=True, type=Path)
    ap.add_argument("--slow-delay", type=_validate_slow_delay, default=2.0, help="seconds between s0-01-slow chunks")
    ap.add_argument("--pidfile", type=Path)
    ap.add_argument("--allow-existing-records", action="store_true")
    args = ap.parse_args(argv)
    # V17/A18: port range validation
    if not (1 <= args.port <= 65535):
        print(f"scripted_backend: --port {args.port} is outside the valid range 1-65535",
              file=sys.stderr)
        return 2
    # V-d F21: check existence before stat
    if not args.token_file.exists():
        print(f"scripted_backend: token file not found: {args.token_file}",
              file=sys.stderr)
        return 2
    st = args.token_file.stat()
    if not stat.S_ISREG(st.st_mode):
        print(f"scripted_backend: token file is not a regular file: {args.token_file}",
              file=sys.stderr)
        return 2
    mode = st.st_mode & 0o7777
    # V-c F15: accept 0600 and 0400 (no group/other bits)
    if mode & 0o077:
        print(f"scripted_backend: token file mode is {oct(mode)}, "
              f"must have no group/other bits (0o600 or 0o400)",
              file=sys.stderr)
        return 2
    token = load_token(args.token_file)
    if args.record_dir.is_symlink() and not args.record_dir.exists():
        print(f"scripted_backend: --record-dir {args.record_dir} is a dangling symlink",
              file=sys.stderr)
        return 2
    # V-c F13: refuse when record-dir exists but is not a directory
    if args.record_dir.exists() and not args.record_dir.is_dir():
        print(f"scripted_backend: --record-dir {args.record_dir} exists but is not a directory",
              file=sys.stderr)
        return 2
    if args.record_dir.is_dir() and any(args.record_dir.iterdir()):
        if not args.allow_existing_records:
            print(f"scripted_backend: --record-dir {args.record_dir} is non-empty; "
                  f"pass --allow-existing-records to override", file=sys.stderr)
            return 2
    # D5m-F2: --pidfile is the THIRD path this opens at startup, and the whole block now runs
    # BEFORE the bind, so a refusal leaves the port unbound (VERIFY-D5l F2: a FIFO here hung
    # the process forever with the socket already listening — a supervisor waits on a port
    # that never serves; a directory gave an uncaught traceback and rc 1, not a named
    # refusal).  Writing the pid before the bind also makes a bind failure visible to a
    # launcher's failure-aware wait (run_s0_04_legs.sh reads /proc/<pid> from this file)
    # instead of burning its whole readiness deadline.
    if args.pidfile:
        if _refuse_non_regular(args.pidfile):
            print(f"scripted_backend: --pidfile is not a regular file: {args.pidfile}",
                  file=sys.stderr)
            return 2
        args.pidfile.write_text(f"{os.getpid()}\n")
    state = State(token, args.record_dir, args.slow_delay)
    server = ThreadingHTTPServer((args.bind, args.port), make_handler(state))
    print(f"scripted_backend: listening on http://{args.bind}:{server.server_address[1]}/v1 "
          f"models={','.join(MODELS)} record_dir={args.record_dir} token_fp={_fingerprint(token)}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
