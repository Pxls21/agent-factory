#!/usr/bin/env python3
"""Export a Claude Code session transcript into daily, SECRET-SCRUBBED markdown digests under
transcripts/sandbox/ (committed), so PC lanes and cheap curator models can read the chat history
the wiki/skills should be curated from (owner ask 2026-09-03: "a hook that every time you push it
sends a bit of the transcript to the repo").

Digest = user + assistant text only (tool results, hook noise and notifications stripped, same
rule as scripts/chat_tail.py --export), each turn capped, one file per UTC day, rewritten in
full each run (idempotent). Scrubbing is STRUCTURAL and tested: every class in SECRET_PATTERNS is
replaced before a byte reaches disk, and tests/test_transcript_export.py plants one of each and
asserts none survives. Never widen what is exported without extending the scrubber test.
The shapes cannot prove a digest holds no secret, so a VALUE gate stands behind them (AF-AP-224):
before any file is written, the scrubbed text is checked for the values of the known secrets
(KNOWN_VALUE_SOURCES, counted as scripts/known_values_check.py counts them); on a hit nothing is
written.

Usage: transcript_export.py [--transcript <jsonl>] [--out transcripts/sandbox] [--cap 4000]
Default transcript: the newest *.jsonl under /root/.claude/projects/-home-user/.
Exit 0 = wrote/refreshed files (prints them), 3 = no transcript found, 4 = refused by the value
gate (a known secret value in the scrubbed text, or a known source present but unreadable or not
a regular file, or a source of an unknown kind): nothing written, and stderr names each source and
its counts, never a value.
"""
import argparse
import glob
import importlib.util
import json
import os
import re
import sys

# A secret NAME (a quoted name and a compound *_key name count, #187; the compound class starts only after a
# non-alphanumeric: unanchored, a long run re-scans itself, quadratic). A bare `_key` / `-key` also starts an assignment:
# that is where a value cut before such a name ends (below).
_NAME = (r"(?:AGENT_TOKEN|PC_BRIDGE_TOKEN|X-Agent-Token|(?<![A-Za-z0-9])[A-Za-z0-9]*[_-]key|[_-]key|api[_-]?key"
         r"|token|secret|password|passwd|passphrase|Authorization)")
# Inside a value a name is read at its shortest -- a secret word, or `_key` / `-key` without the compound's alphanumeric
# prefix, which may be the value's own tail (`passwd=QZJ8my_key: v` keeps `QZJ8my` a value) -- and a HEAD is that name, an
# optional quote, `:` or `=`.
_WORD = (r"(?:AGENT_TOKEN|PC_BRIDGE_TOKEN|X-Agent-Token|[_-]key|api[_-]?key|token|secret|password|passwd|passphrase"
         r"|Authorization)")
_HEAD = _WORD + r"[\"']?\s*[:=]"
# Where the Bearer rule matches (case as written; its token comes after whitespace), and where a bridge link starts.
_BEARER = r"(?-i:Bearer)\s+[A-Za-z0-9._\-]{8}"
_LINK = r"(?i:https?://[a-z0-9\-]+\.trycloudflare\.com)"
_V = r"[^\s\"'&,;]"    # a value character
_L = r"[^\s)\"']"       # a bridge link's tail character (the link rule's own class)
# A value (AF-AP-157: a value that ran over the next name and its separator hid that name from this rule, and the name's
# value reached disk). It keeps an in-run head (a name, `:` or `=`, then a value character) as a name; it stops before
# any other head (a quote or whitespace after the name or the separator, or the run ends at the separator) and before a
# Bearer match, which the next match and the Bearer rule take; it takes a bridge link whole, past `&`, `,` and `;` (a
# value that ended inside a link left the link rule nothing to match).
_VALUE = (r"(?:" + _WORD + r"[:=](?=" + _V + r")"
          r"|" + _LINK + r"(?:" + _WORD + r"[:=](?=" + _L + r")|(?!" + _HEAD + r"|" + _BEARER + r")" + _L + r")*"
          r"|(?!" + _HEAD + r"|" + _BEARER + r"|" + _LINK + r")" + _V + r")*")
# Inside a matched value: the in-run heads and the pieces between them (no piece starts a head).
_CUT = re.compile(r"(" + _WORD + r"[:=])|(?:(?!" + _HEAD + r").)+", re.I | re.S)


def _redact_run(m):
    """Keep the assignment's head and each in-run head; redact every value piece, whatever its length."""
    return m.group(1) + _CUT.sub(lambda p: p.group(1) or "<redacted>", m.group(2))


# The provider-key rules' anchors (their comment below says why): before a key no ASCII letter or digit, unless it is a
# JSON escape's own letter; after it no ASCII letter or digit.
_KEY_L = r"(?:(?<![A-Za-z0-9])|(?<=\\[nrtbf])|(?<=\\u[0-9A-Fa-f]{4}))"
_KEY_R = r"(?![A-Za-z0-9])"

SECRET_PATTERNS = [
    # a private-key block, BEGIN through END: PEM and OpenSSH (`… PRIVATE KEY`) and GnuPG's armor
    # (`PGP PRIVATE KEY BLOCK`, the PGP 2.x `PGP SECRET KEY BLOCK`); a block with no END line (cut
    # at its source) is redacted to the end of the text. First, so no later rule leaves pieces of it
    # behind (a credential rule that ran earlier would eat the BEGIN line and strand the body).
    (re.compile(r"-----BEGIN [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----.*?"
                r"(?:-----END [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----|\Z)", re.S),
     "<private-key-redacted>"),
    # the same block with malformed header lines (3 or more dashes, spaces beside them; VERIFY-SCRUB1 F14), from BEGIN
    # through END. Unlike the rule above it needs the END line: without one, a line of prose about these headers hid
    # the rest of a tool result (SCRUB2 measured up to 15,522 characters on this session's transcripts).
    (re.compile(r"-{3,}[ \t]*BEGIN [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?[ \t]*-{3,}.*?"
                r"-{3,}[ \t]*END [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?[ \t]*-{3,}", re.S),
     "<private-key-redacted>"),
    # explicit credential assignments / headers: the head is kept, the value (_VALUE) replaced. The 8-character floor reads
    # the whole run after the separator (the lookahead). Every piece of the value is redacted whatever its length: the run
    # was one value before AF-AP-157, so a floor on a piece would show bytes that were hidden. A head that is not in-run
    # ends the match before its name; the next match takes it with its own floor.
    (re.compile(r"(" + _NAME + r"[\"']?\s*[:=]\s*[\"']?)(?=" + _V + r"{8})(" + _VALUE + r")", re.I), _redact_run),
    # a Bearer token (case as written): the floor reads the whole run; the token stops before a following Bearer match and
    # a bridge link, which their rules take (a token that ate `Bearer` or `https` freed what followed: AF-AP-157)
    (re.compile(r"(Bearer\s+)(?=[A-Za-z0-9._\-]{8})(?:(?!" + _BEARER + r"|" + _LINK + r")[A-Za-z0-9._\-])+"),
     r"\1<redacted>"),
    # SCRUB2 (VERIFY-SCRUB1 F14), each shape measured on this session's transcripts before it went in (SCRUB2-report.md):
    # a Cookie header, from its head to the end of the line or a quote, when a `name=value` of 8+ characters is in it
    (re.compile(r"((?i:\b(?:set-)?cookie)[\"']?\s*:\s*[\"']?)(?=[^\r\n\"']*=[^\s;\"']{8})[^\r\n\"']+"), r"\1<redacted>"),
    # an Authorization header's credential after a known scheme (a bearer in any case too). Any word as the scheme took
    # prose after this repo's `AUTHORIZATION:` brief headings.
    (re.compile(r"((?i:authorization)[\"']?\s*:\s*[\"']?(?i:token|basic|bearer|digest|negotiate|ntlm|apikey|api-key|key"
                r"|ssws)\s+)(?=[A-Za-z0-9._~+/=\-]{8})[A-Za-z0-9._~+/=\-]+"), r"\1<redacted>"),
    # `pwd` and `credentials` assigned a value that is not a path or a reference (it starts with none of / ~ . $ \). As
    # names of the credential rule both took paths (`PWD=/home/...`), and `credentials` took Python annotations
    # (`credentials: LoginRequest`), so `credentials` needs `=` or a quoted key.
    (re.compile(r"((?<![A-Za-z0-9])(?i:pwd)[\"']?\s*[:=]\s*[\"']?)(?![/~.$\\])(?=[^\s\"'&,;]{8})[^\s\"'&,;]+"),
     r"\1<redacted>"),
    (re.compile(r"((?<![A-Za-z0-9])(?i:credentials)(?:[\"']\s*:|\s*=)\s*[\"']?)(?![/~.$\\])(?=[^\s\"'&,;]{8})"
                r"[^\s\"'&,;]+"), r"\1<redacted>"),
    # provider-shaped keys. The left anchor is `(?<![A-Za-z0-9])`, not `\b` (AF-AP-224): `\b` wants a non-word character
    # before the key, so a key glued to an `_` (`mcp__srv__sk-...`, `my_sk-...`) passed whole. An `_` now separates; a
    # letter or a digit still does not. SCRUB1 measured no left anchor at all on this session's transcripts: 17,692 more
    # redactions, all but 6 of them ordinary words (`<task-notification>` first), and no known secret among them.
    # SCRUB2: a key right after a JSON escape (`\n`, `\r`, `\t`, `\b`, `\f`, `\uXXXX`) counts as separated too, for a
    # writer that scrubs raw JSON (session_export writes a tool input as JSON, `\n` before each line); the escape stays,
    # so the JSON stays valid. The right anchor is `(?![A-Za-z0-9])`, not `\b`: `\b` never holds between an ASCII letter
    # and a non-ASCII one (`é`, `の`), and before an `_` the gh rule found no end (the key passed whole) while the xox rule
    # ended at its last hyphen (the token's secret last segment stayed). Each rule now takes the key's whole run.
    (re.compile(_KEY_L + r"sk-[A-Za-z0-9_\-]{12,}" + _KEY_R), "sk-<redacted>"),
    (re.compile(_KEY_L + r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}" + _KEY_R), "gh<redacted>"),
    (re.compile(_KEY_L + r"AIza[0-9A-Za-z_\-]{30,}" + _KEY_R), "AIza<redacted>"),
    (re.compile(_KEY_L + r"xox[abprs]-[A-Za-z0-9\-]{10,}" + _KEY_R), "xox-<redacted>"),
    # ephemeral bridge links (the token often rides in the URL's session)
    (re.compile(r"https?://[a-z0-9\-]+\.trycloudflare\.com[^\s)\"']*", re.I), "https://<bridge-link-redacted>"),
    # long opaque tokens (40+ url-safe chars) — coarse, deliberately. Each end is `\b` or its ASCII form: `\b` alone never
    # holds next to a non-ASCII letter, so a token glued to `é` or `の` passed (VERIFY-SCRUB1 F12); with both forms every
    # match `\b` made stays a match.
    (re.compile(r"(?:\b|(?a:\b))[A-Za-z0-9_\-]{40,}(?:\b|(?a:\b))"), "<opaque-redacted>"),
]


def scrub(text: str) -> str:
    for pat, rep in SECRET_PATTERNS:
        text = pat.sub(rep, text)
    return text


# SESSION-EXPORT (task #252, D-086, the brief's D-2): tool payloads carry shapes `scrub` does not take. `scrub` stays as it
# is, so every consumer that imports it keeps its output; `scrub_payload` runs scrub's rules and these (the order is in its
# docstring), and it is the scrubber scripts/session_export.py runs on every text. Each rule matches only what scrub's named
# rules left. A name that ends in PASS, in capitals as an env name spells it (DB_PASS, SMTP_PASS): the real transcripts
# hold thousands of code variables such as `first_pass = ...`. PASSWD and PASSWORD are in _NAME already, in any case.
_PASS = r"(?<![A-Za-z0-9])(?:[A-Za-z0-9]*[_-])?(?-i:PASS)"
_VQ = r"(?:[^\s\"'&,;\\]|\\(?![\"']))"      # a value character (_V's), and a backslash only when no quote follows it
PAYLOAD_PATTERNS = [
    # a bridge host with no scheme or under another scheme (the link rule wants http(s)://), every label of it
    (re.compile(r"(?<![A-Za-z0-9\-])(?:[A-Za-z0-9\-]+\.)+trycloudflare\.com", re.I), "<bridge-link-redacted>"),
    # the tail of a Bearer token in the b64token characters `~+/=`, where the Bearer rule's class stops
    (re.compile(r"((?-i:Bearer)\s+<redacted>)[~+/=][A-Za-z0-9._~+/=\-]*"), r"\1"),
    # HTTP Basic credentials in an Authorization header, also as a JSON member, quoted or behind escaped quotes (R-1)
    (re.compile(r"((?i:authorization)(?:\\*[\"'])?\s*:\s*(?:\\*[\"'])?(?i:basic)\s+)[A-Za-z0-9+/]{8,}=*"), r"\1<redacted>"),
    # R1 (VERIFY-SESSION-EXPORT F-1): a named credential whose value sits behind a JSON-escaped quote. The exporter writes a
    # tool input, a hook, an attachment or a system record as canonical JSON, so `NAME="v"` inside a string becomes
    # `NAME=\"v\"`, and the credential rule cannot take the backslash as its quote. Any depth of escaping; the value stops
    # at a backslash, a quote or whitespace, so the escaping stays whole.
    (re.compile(r"((?:" + _NAME + r"|" + _PASS + r")(?:\\+[\"'])?\s*[:=]\s*\\+[\"'])(?=[^\\\"'\s]{8})[^\\\"'\s]+", re.I),
     r"\1<redacted>"),
    # a password in a URL's userinfo (scheme://user:password@host), up to the last `@` before the host (F-6: a password
    # with a raw `@` in it)
    (re.compile(r"(\b[A-Za-z][A-Za-z0-9+.\-]*://[^\s/:@'\"<>]+:)[^\s/'\"<>]+@"), r"\1<redacted>@"),
    # R1 R-3 (F-5): a Bearer token after a `bearer` in any case: in an Authorization header, or anywhere when the token
    # holds a digit (so prose such as "bearer tokens" stays)
    (re.compile(r"((?i:authorization)(?:\\*[\"'])?\s*[:=]\s*(?:\\*[\"'])?(?i:bearer)\s+"
                r"|(?i:bearer)\s+(?=[A-Za-z0-9._~+/=\-]*[0-9]))(?=[A-Za-z0-9._~+/=\-]{8})[A-Za-z0-9._~+/=\-]+"),
     r"\1<redacted>"),
    # R-3: the password of curl's `-u user:pass` or `--user user:pass` (within 2,000 characters of `curl`, before a pipe or
    # a command separator); a `$` reference stays. Any `-u` alone took `date -u +%H:%M:%S` thousands of times.
    (re.compile(r"((?<![A-Za-z0-9_.\-])curl\b[^\n|;&]{0,2000}?\s(?:-u\s*|--user[\s=]+)(?:\\*[\"'])?[^\s:\"'\\]*:)(?!\$)"
                r"[^\s\"'\\]+"), r"\1<redacted>"),
    # R-3: a value assigned to a name that ends in PASS (see _PASS); a bare PASS needs `=`, so a `PASS: <test name>` line
    # stays; a `$` reference stays (`PASS=$((PASS+1))`). The value takes a backslash only when no quote follows it, so the
    # escape of a closing `\"` stays and the canonical JSON stays valid (scrub's own class, _V, takes that backslash).
    (re.compile(r"((?<![A-Za-z0-9])(?:[A-Za-z0-9]*[_-]PASS[\"']?\s*[:=]|PASS\s*=)\s*[\"']?)(?!\$)(?=" + _VQ + r"{8})" + _VQ
                + r"+"), r"\1<redacted>"),
    # R-3: a credential alone in a URL's userinfo (scheme://token@host): 8 or more characters with a letter and a digit.
    # The scheme starts where no scheme character precedes it (`\b` let every `.` restart it: quadratic on `a.a.a...`).
    (re.compile(r"((?<![A-Za-z0-9+.\-])[A-Za-z][A-Za-z0-9+.\-]*://)(?=[^\s/:@'\"<>]*[0-9])(?=[^\s/:@'\"<>]*[A-Za-z])"
                r"[^\s/:@'\"<>]{8,}@"), r"\1<redacted>@"),
]


OPAQUE_MARK = "<opaque-redacted>"      # the marker of scrub's coarse opaque-run rule


def scrub_payload(text: str, opaque=None) -> str:
    """The extended scrubber for tool payloads: scrub's named rules, then PAYLOAD_PATTERNS, then scrub's coarse opaque-run
    rule, whose match becomes `opaque(match)` when a callable is given (session_export.py's stable pseudonyms, AMENDMENT 1
    G6) or its marker. The named rules run first, so a value one of them takes never reaches `opaque`, however long."""
    for pat, rep in SECRET_PATTERNS:
        if rep != OPAQUE_MARK:
            text = pat.sub(rep, text)
    for pat, rep in PAYLOAD_PATTERNS:
        text = pat.sub(rep, text)
    for pat, rep in SECRET_PATTERNS:
        if rep == OPAQUE_MARK:
            text = pat.sub(rep if opaque is None else opaque, text)
    return text


# The strict pass (D-2), for the output of a command that names a secret file: scrub_payload, then every assignment value
# on a line (an env file, `grep -n` over one, a curl config), every run of 20+ key characters that holds a letter and a
# digit, and every line that is one token of 12+ such characters (a key file printed raw). It over-redacts ordinary output
# on purpose: it runs only where a secret file was named.
_ASSIGN_LINE = re.compile(r"(?m)^([ \t]*(?:\d+[:-]|[^\s:=]+:\d+[:-])?[ \t]*(?:export[ \t]+|declare[ \t]+-x[ \t]+)?"
                          r"[A-Za-z_][A-Za-z0-9_]*[ \t]*=[ \t]*)(\S.*)$")
_KEY_RUN = re.compile(r"[A-Za-z0-9_\-+/=]{20,}")
_TOKEN = r"[A-Za-z0-9_\-+/=.~:]"
_TOKEN_LINE = re.compile(r"(?m)^([ \t]*)(" + _TOKEN + r"{12,})([ \t]*)$")
_LETTER, _DIGIT = re.compile(r"[A-Za-z]"), re.compile(r"[0-9]")

# AMENDMENT 3 (the R1 brief): a run of one of these shapes -- the opaque rule's, the strict pass's key run and its token --
# that a file tracked by the repo holds verbatim is committed text, not a secret. session_export.py collects the runs of the
# tracked files; the opaque rule's callable and scrub_strict's `keep` leave such a run as it is. Named rules still run first.
RUN_SHAPES = tuple([p for p, r in SECRET_PATTERNS if r == OPAQUE_MARK] + [_KEY_RUN, re.compile(_TOKEN + r"{12,}")])


def _keylike(s):
    return bool(_LETTER.search(s) and _DIGIT.search(s))


_HEAD_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")


def _committed(s, keep):
    """AMENDMENT 3: `s` is in `keep`, or is `NAME=<a value in keep>` (a key run and a token take an assignment's name
    with its value; the name was never redacted)."""
    m = _HEAD_NAME.match(s)
    return s in keep or bool(m) and s[m.end():] in keep


def scrub_strict(text: str, opaque=None, keep=()) -> str:
    """scrub_payload (with the same `opaque`), then every assignment value, long mixed run and lone token line (above),
    except a committed one (AMENDMENT 3: `keep` holds session_export.py's runs of the repo's tracked files)."""
    text = _ASSIGN_LINE.sub(lambda m: m.group(0) if m.group(2).rstrip() in keep else m.group(1) + "<redacted>",
                            scrub_payload(text, opaque))
    text = _KEY_RUN.sub(lambda m: "<redacted>" if _keylike(m.group(0)) and not _committed(m.group(0), keep)
                        else m.group(0), text)
    return _TOKEN_LINE.sub(lambda m: m.group(1) + "<redacted>" + m.group(3)
                           if _keylike(m.group(2)) and not _committed(m.group(2), keep) else m.group(0), text)


def turns(path):
    with open(path, errors="replace") as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = e.get("type")
            if t not in ("user", "assistant"):
                continue
            c = (e.get("message") or {}).get("content")
            if isinstance(c, str):
                txt = c
            elif isinstance(c, list):
                txt = "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
            else:
                continue
            txt = txt.strip()
            if not txt or txt.startswith("[{"):
                continue
            if t == "user" and txt.startswith(("Stop hook feedback:", "<task-notification>", "<system-reminder>", "[SYSTEM NOTIFICATION")):
                continue
            yield t, e.get("timestamp", "?"), txt


# THE VALUE GATE (AF-AP-224, task #280). The rules above know secret SHAPES, and a secret in a shape they lack passes them.
# Before export() writes a byte, it counts the VALUES of the known secrets in the scrubbed text, as
# scripts/known_values_check.py counts them (a value whole, a URL's host, each 8-byte window of a token-like value, a raw
# key's printed forms), and refuses on any hit with the source's name and the counts, never a value. The sources are named
# here and only here: (kind, where, keys that hold no secret). A hostname is not a secret: TYPESAFE_BASE_URL is a public
# base URL, so its value and its host are skipped. main() reads this tuple when it runs and hands it on; export() and
# known_values() have no default (VERIFY-SCRUB1 F1: a default bound when export() was defined sent every test that ran
# main() to the real sources, whatever the test replaced).
_HERE = os.path.dirname(os.path.abspath(__file__))
KNOWN_VALUE_SOURCES = (
    ("env-file", os.path.normpath(os.path.join(_HERE, os.pardir, ".pc-bridge.env")), ()),
    ("env-file", "/root/.codiv/api.env", ("TYPESAFE_BASE_URL",)),
    ("raw-file", "/root/.config/session-export/pseudonym.key", ()),
    ("env", "GH_TOKEN", ()),
    ("env", "GITHUB_TOKEN", ()),
)


class KnownValueRefusal(Exception):
    """The value gate refused; args[0] is the list of lines to print (source names and counts only)."""


def known_values(sources):
    """[(label, form, value, its 8-byte windows or [])] of every source present. known_values_check.py is loaded by path
    here, not at import: the scrubber's importers need only the rules, and some load this file with no scripts/ on
    sys.path. A missing source (no file, an unset or short variable, no value of 8+ characters) is skipped with one line
    on stderr; a source that is present but cannot be read, or is not a regular file (a FIFO would block the read), and a
    source of a kind other than env, env-file and raw-file raise KnownValueRefusal (the gate fails closed)."""
    for kind, where, _ in sources:
        if kind not in ("env", "env-file", "raw-file"):
            raise KnownValueRefusal(["value gate: the source %s has an unknown kind %r" % (os.path.basename(where), kind)])
    spec = importlib.util.spec_from_file_location("transcript_export_known_values",
                                                  os.path.join(_HERE, "known_values_check.py"))
    kv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kv)
    out = []
    for kind, where, skip in sources:
        name = "env:" + where if kind == "env" else os.path.basename(where)
        try:
            if kind == "env":        # the variable is where the secret lives (known_values_check --env), not a setting
                v = os.environ.get(where, "").encode()
                forms = [(name, f, b, w) for f, b, w in kv._forms(where, v)] if len(v) >= kv.MIN_VALUE else []
            elif not os.path.exists(where):
                forms = []
            elif kind == "env-file":
                forms = [("%s:%s" % (name, k), f, b, w) for k, v in kv._env_values(where, set(skip))
                         for f, b, w in kv._forms(k, v)]
            else:                    # raw-file
                data = kv._read_regular(where)
                forms = [(name + ":raw", f, b, w) for f, b, w in kv._raw_forms(data)] if len(data) >= kv.MIN_VALUE else []
        except OSError as e:
            raise KnownValueRefusal(["value gate: cannot read the source %s (%s)" % (name, type(e).__name__)])
        if not forms:
            print("transcript_export: value gate: source %s missing or empty, skipped" % (
                  name if kind == "env" else where), file=sys.stderr)
        out += [(label, f, b, kv._windows(b) if w else []) for label, f, b, w in forms]
    return out


def value_hits(datas, values):
    """['<label> <form> whole=N windows=H/T'] for each known value found in the byte strings `datas` (whole, and by the
    distinct 8-byte windows seen: known_values_check.py's count and its line)."""
    hits = []
    for label, form, b, wins in values:
        whole = sum(d.count(b) for d in datas)
        seen = sum(1 for w in wins if any(w in d for d in datas))
        if whole or seen:
            hits.append("%s %s whole=%d windows=%d/%d" % (label, form, whole, seen, len(wins)))
    return hits


def export(transcript: str, out: str, cap: int, *, sources) -> list:
    days = {}
    for role, ts, txt in turns(transcript):
        day = ts[:10] if ts != "?" else "undated"
        # Scrub, THEN cap (AF-AP-127): a cap first cuts a secret that straddles it below its
        # pattern's minimum length (or cuts a key block's END line off), and the stub survives.
        days.setdefault(day, []).append(f"## {role} @ {ts}\n\n{scrub(txt)[:cap]}\n")
    files = [(os.path.join(out, f"chat-{day}.md"),
              (f"# Conversation {day} (scrubbed digest, {len(days[day])} turns)\n\n" + "\n".join(days[day])).encode())
             for day in sorted(days)]
    # The value gate runs on the exact bytes to be written, before the first write (the out directory included).
    hits = value_hits([data for _, data in files], known_values(sources))
    if hits:
        raise KnownValueRefusal(hits)
    os.makedirs(out, exist_ok=True)
    written = []
    for p, data in files:
        with open(p, "wb") as fh:
            fh.write(data)
        written.append(p)
    return written


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript")
    ap.add_argument("--out", default="transcripts/sandbox")
    ap.add_argument("--cap", type=int, default=4000)
    a = ap.parse_args(argv)
    path = a.transcript
    if not path:
        cands = sorted(glob.glob("/root/.claude/projects/-home-user/*.jsonl"), key=os.path.getmtime)
        path = cands[-1] if cands else None
    if not path or not os.path.isfile(path):
        print("transcript_export: no transcript found", file=sys.stderr)
        return 3
    try:
        written = export(path, a.out, a.cap, sources=KNOWN_VALUE_SOURCES)     # the module's tuple as it is now
    except KnownValueRefusal as e:
        for line in e.args[0]:
            print("transcript_export: REFUSED, nothing written: " + line, file=sys.stderr)
        return 4
    for p in written:
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
