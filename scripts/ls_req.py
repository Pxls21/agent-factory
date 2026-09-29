#!/usr/bin/env python3
"""ls_req.py — the chat form (T2) of the stack runner: labeled request lines in the coordinator's chat, run by a Stop
hook through scripts/stack.py, each answered by exactly one receipt (task #364, D-108 item 6; the contract is
tasks/briefs/labeling/LS-B10-brief.md; the design is docs/research/findings/labeling/LS-DESIGN-v2-2026-09-28.md §3 with
the premortem's transport list A, tasks/briefs/labeling/LS-PREMORTEM-report.md, cited as PM Pn). Written 2026-09-29.

The coordinator ends a message with request lines instead of making a tool call. The Stop hook runs each through the
stack runner and hands the receipts back as blocking feedback (exit 2, the text on stderr: the channel of
.claude/hooks/turn-retro-gate.sh), so the coordinator continues with them. The tool-call form (T1,
`python3 scripts/stack.py <label> ...`) stays as it is; the stacks stay the runner's.

  prompt         UserPromptSubmit: reconcile the ended turn, mint this prompt's nonce, inject ONE line (and reports)
  session-start  SessionStart: a compaction inside a running query re-injects the current nonce (the compaction
                 drops it from the context); any other start reconciles the ended query and turns the form off
                 until the next prompt
  stop           Stop, the main thread only: run the unanswered request lines, answer each one
  defer-check    for .claude/hooks/turn-retro-gate.sh: prints `defer` (exit 0) when a text written since the last
                 Stop (or last_assistant_message) carries a current nonce, so this Stop answers requests; exit 1
                 otherwise and on any failure (a failure never defers the retro)
Each reads its hook payload, JSON, on stdin. Test-only options: --registry PATH and --log-dir PATH (passed to
stack.py), --tree PATH (the runner's tree, default this repository), --budget S, --catchup S.

THE GRAMMAR. It is a labeling scheme as well as a detector: a trained model may later replace this lexical parser,
reading the same lines, so every request, its place in the transcript and its result are kept (the ledger below).
  REQ <nonce> <id> <label> key=value ...
  - One request per line, at the line's start, single ASCII spaces between the tokens (trailing blanks ignored).
  - <nonce>: 12 lowercase hex digits, one the prompt hook injected for this turn. <id>: [a-z][a-z0-9]{0,15}, new for
    every request line of its nonce (r1, r2, ...; a re-issue takes a new id). <label>: a stack of scripts/stacks.toml.
    The parameters are the runner's own key=value tokens; a value holds no whitespace.
  - A long value (a command, a quote, a prompt) goes in a block: the token key=<<WORD opens it (WORD: 1 to 16 capitals,
    digits or _), and the lines after the request line are the value, verbatim, up to a line that is exactly WORD
    (trailing blanks ignored). Several blocks on one line follow one another. No value ever reaches a shell: each is
    one element of the runner's argument vector.
  - The request lines and their blocks close the text of their message (the text blocks of one API message, joined):
    after the first request line only request lines, their blocks and blank lines may follow, or every request of
    that message is refused as malformed.
  - The current nonce anywhere else (in markup, a code fence, beside a non-ASCII space, in any letter case) is
    intent: that line gets its own receipt, `refused: malformed (<why>)`, never silence.
A well-formed request line whose nonce is not in the turn's valid set never runs: `refused: stale nonce`.

THE BOX (task #380, D-111, D-113; the contract is tasks/briefs/labeling/LS-B11-brief.md): the second request head, the
form the owner confirmed. The label names a stack; the lines inside are a form that fills its parameters. A box is a
request as a REQ line is, on the same transport: the nonce, a new id, the duplicate-id, stale-nonce, cap and budget
rules, one receipt, one ledger row, the fallback's bind rows and the reconciler treat it alike. The REQ line stays as
the fallback.
  ┌─ find · r1 · <nonce>
  │ q: where does the scrubber hide bearer tokens
  └─
  - The top edge starts the line: `┌─ ` (U+250C, U+2500, a space), then <label> · <id> · <nonce>, one space on each side
    of each U+00B7, then optionally a space and one or more ─ (decoration); trailing blanks ignored. The label, the id
    and the nonce follow the REQ line's rules.
  - Every line inside starts with │ (U+2502): `│ ` and its text, or a bare `│` for an empty line; trailing blanks are
    removed. First the parameters, one `key: value` per line (the key is stack.py's NAME_RE, the value the rest of the
    line after `: `, spaces included); an empty line among them is skipped. Each value is ONE element of the runner's
    argument vector, never a shell word.
  - An optional divider `│ ┄┄┄` (three or more U+2504 and nothing else): every inside line after it, up to the bottom
    edge, is the BODY, each without its `│ ` (a bare `│` gives an empty line), joined with newlines. The body goes to
    the parameter the stack names as its `body` (scripts/stacks.toml). The runner's text type takes one line of at most
    500 characters: a body of several lines reaches the runner, which refuses it in its own words.
  - The bottom edge starts the line: `└─`, then optionally more ─; trailing blanks ignored. There is no right edge.
  - A box may sit in a fenced code block (a line of three backquotes, optionally followed by a language word), so the
    chat shows it as a box: in a message that holds a box, fence lines never break the closing rule. A message with no
    box keeps the REQ lines' closing rule exactly: there a fence line after a request line is text.
  - Malformed, with a current nonce: `refused: malformed (<why>)`, under the box's id when its top edge parses, else
    under `?`: a top edge that breaks the grammar; an unclosed box (no bottom edge before the message ends); an inside
    line that does not start with │ (the box ends before it, and it is read as the message's next line); an inside
    line with no space after │; a parameter line with no `: `, or a key that is not a parameter name; a second
    divider; a NUL in a value; text after the requests. Two body cases need the registry, so the Stop judges them when
    the request would run: a body for a stack that names no body, and a parameter line that sets the body parameter
    beside a body.
  - A box whose top edge carries no current nonce is not a request (an illustration): its lines are text, read as the
    REQ form reads text. The exception is a box well formed on its own grammar (the cases above, but the closing rule
    and the two body cases): it is a request with a stale nonce, `refused: stale nonce`, as a REQ line is.
  - Its ledger rows carry `form: "box"` (a REQ line's `form: "req"`) and its text: the box's lines, top edge to bottom
    edge; `line` is its top edge's.

RECEIPTS, exactly one per request line: `RES <nonce> <id> <status>`, the status `ran rc=<rc> run=<run id>` followed by
the runner's print (its own 9,000-character cap), or `refused: <reason>` (malformed, stale nonce, duplicate id, unknown
label, a parameter the runner refuses, cap, budget), or `unanswered: <why>` from the reconciler. A malformed line with
no parsable id is answered with the id `?`. The whole feedback is capped at FEEDBACK_CAP characters (UTF-16 units, as
the harness counts): every RES line stays whole and the runner prints are cut largest first, each cut naming the file
that holds the full print; past even that (about 30 long receipts in one round), the RES lines that do not fit are
carried to the next prompt's context as undelivered. Control tags in the feedback, and in the injected context, are
neutralized with scripts/handback_extract.py's rule, since the harness hands both to the model.

THE STOP HOOK. It collects request lines from EVERY assistant text block since its stored byte offset (never the whole
transcript, never only last_assistant_message: PM P3a, P3b), skips thinking records at the byte level without decoding
them (a record holding a thinking block beside a text block is skipped whole: measured, every assistant record holds
one block), and cross-checks last_assistant_message: the harness writes the transcript asynchronously (its hooks docs),
so when that text holds a nonce line the transcript does not show yet, the hook waits up to CATCHUP_S for the
transcript and then takes the text itself. Every line is matched by occurrence, never by text (VERIFY-LS-B10 F1): a
byte-identical repeat of a request line is a request of its own (`refused: duplicate id`). A line of that text belongs
to a message the transcript does not show yet (it is the final response's last block, PM P3a, so the transcript shows
it only in a record no earlier round answered or bound), so it is never "the same" as another line. Its ledger row has
no record uuid; it carries `fb` (a token) and `after` (the offset its round read up to), and when its record appears,
the first line of that request text in the same transcript, at or after `after`, that no row holds yet is tied to it
by a `bind` row (that record's uuid and line): a fallback receipt absorbs ONE transcript line, so its record is not
answered twice. The
round's requests run one after another under ROUND_BUDGET_S (the registration timeout is 300 s): a request is not
started with less than MIN_START_S left, and a run past the budget is stopped (SIGTERM to the runner, which kills its
steps' process groups; SIGKILL KILL_GRACE_S later); both answer `refused: budget`. It never keys execution on
stop_hook_active (PM P1). The harness ends a turn above CLAUDE_CODE_STOP_HOOK_BLOCK_CAP (default 8) consecutive
blocking Stops with no tool call between them and drops the pending feedback (PM P2); the hook counts them from the
transcript (a blocking stop_hook_summary adds one; a tool_use, a non-blocking summary or a new prompt record resets; a
compaction's summary record carries turnOrigin too and does not reset) and from its own blocks, takes the larger, and
from cap-1 on refuses every request of the round loudly (`continue with tool calls`) and runs nothing; above the cap,
where the harness would drop the feedback, it blocks nothing and writes nothing for it: the refusals stay undelivered
and the next prompt reports them (VERIFY-LS-B10 F4). A Stop with no current-nonce request line never blocks for a
request; the one block it can make then is the chain-end git report (PM P4): after a receipt round the harness git
check (/root/.claude/stop-hook-git-check.sh) stays silent for the rest of the turn, because stop_hook_active stays
true, so at the chain's end this hook runs that check's dirty and unpushed checks in the payload's cwd and reports the
first hit in its words, once per chain. That block is contract item 7's, by the coordinator's ruling on VERIFY-LS-B10
F11: item 7's specific wording governs, so the chain-end git report reports as the harness's own check would, once
per chain, and item 10's never-block rule covers request handling only.

THE NONCE. Every UserPromptSubmit mints a fresh nonce. The turn's valid set keeps the last KEEP_NONCES nonces while
the harness query is still running (UserPromptSubmit fires for messages absorbed mid-turn and, per the premortem,
for Stop feedback, PM P10; this session's transcript shows no prompt hook after Stop feedback) and resets to the new
nonce once the transcript shows the query ended (a non-blocking Stop, an interrupt or an API error; a SessionStart
other than a compaction inside a running query ends it too). A compaction's SessionStart re-injects the current
nonce. No nonce line in a turn means the chat form is off, and the coordinator uses tool calls (PM P13).

THE RECONCILER (PM P3d, P3b). On an ended turn's next UserPromptSubmit, and on a SessionStart that ends the query,
every request line of the ended window with no receipt in the ledger gets one, `unanswered: <how the turn ended>` (an
interrupt or an API error, with the transcript record that shows it, or unknown, naming a restart where a SessionStart
ended it), and is reported in the injected context. It never runs them:
an interrupt is the owner's stop; the coordinator re-issues a request that is still wanted. Receipts a Stop wrote
without blocking (a stale nonce alone never blocks) are reported there too.

STATE: <main>/.jev/req/ (the MAIN tree through git's common dir, as the stack runner finds its log; AF_REQ_STATE, read
once at start, replaces <main>/.jev for tests): ledger.jsonl (one row per receipt: the session, nonce, id, label,
status, the stack run id and its run dir, the transcript and the uuid of the record that carried the request, its form
(`req` or `box`) and its text (cut at LEDGER_TEXT_MAX characters; `sha` is the whole text's), so an
export can pair the chat before a request with its label and its result; plus one `bind` row, kind bind and status
bound, when the record of a last_assistant_message receipt appears: its uuid and line, and the receipt's `fb`, which
completes that receipt's pairing), sessions/<session>.json (the nonces and
the byte offsets), out/<session>/ (each runner print in full) and hooks.jsonl (one line per hook run: its time in ms
and the transcript bytes it read). OFF SWITCH: while <main>/.jev/req-off exists every subcommand exits at once and
injects nothing (defer-check exits 1). A hook error prints one line naming what failed and exits 0: a broken hook
never blocks and never stalls.
"""
import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
import re
import secrets
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STACK = os.path.join(HERE, "stack.py")
HANDBACK = os.path.join(HERE, "handback_extract.py")

ROUND_BUDGET_S = 240.0     # the runs of one Stop round; the registration timeout is 300 s
KILL_GRACE_S = 10.0        # SIGTERM to a runner past the budget, then SIGKILL this much later
MIN_START_S = 5.0          # a request is not started with less than this left of the round's budget
CATCHUP_S = 3.0            # the wait for the transcript to show what last_assistant_message holds
CATCHUP_POLL_S = 0.1
FEEDBACK_CAP = 9500        # UTF-16 units: 500 under the harness's 10,000-character swap of hook text (AF-AP-183)
DEFAULT_CAP = 8            # the harness's CLAUDE_CODE_STOP_HOOK_BLOCK_CAP default (PM P2)
KEEP_NONCES = 4            # the valid set while a query runs
DEFER_TAIL_BYTES = 2 * 1024 * 1024   # defer-check reads at most this much of the transcript's end
REASON_MAX = 240           # characters of one refusal reason in a RES line
LOG_MAX_BYTES = 4_000_000  # then hooks.jsonl moves to hooks.jsonl.1
GIT_TIMEOUT_S = 20

HEAD_RE = re.compile(r"REQ ([0-9a-f]{12}) ([a-z][a-z0-9]{0,15}) ([a-z][a-z0-9-]{1,23})((?: [^\s]+)*)")
ID_RE = re.compile(r"[a-z][a-z0-9]{0,15}")
LABEL_RE = re.compile(r"[a-z][a-z0-9-]{1,23}")        # stack.py's LABEL_RE
PARAM_RE = re.compile(r"([a-z][a-z0-9_]{0,23})=(.*)", re.S)   # the key is stack.py's NAME_RE
WORD_RE = re.compile(r"[A-Z][A-Z0-9_]{0,15}")
RUN_LINE_RE = re.compile(r"stack ([a-z][a-z0-9-]{1,23}) · run (s-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{6}) · exit ([0-9]+)")
SESSION_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")
NONCE_RE = re.compile(r"[0-9a-f]{12}")
# THE BOX, its characters escaped here (U+250C ┌, U+2500 ─, U+00B7 ·, U+2502 │, U+2504 ┄, U+2514 └)
TOP_RE = re.compile("\u250c\u2500 ([a-z][a-z0-9-]{1,23}) \u00b7 ([a-z][a-z0-9]{0,15}) \u00b7 ([0-9a-f]{12})"
                    "(?: \u2500+)?")                  # the label (LABEL_RE), the id (ID_RE), the nonce, decoration
BOTTOM_RE = re.compile("\u2514\u2500+")
DIVIDER_RE = re.compile("\u2504{3,}")               # after an inside line's `│ `
NAME_RE = re.compile(r"[a-z][a-z0-9_]{0,23}")       # stack.py's NAME_RE: a parameter line's key
FENCE_RE = re.compile(r"```[A-Za-z0-9_+.#-]*")      # a fence line: three backquotes, optionally a language word
BAR = "\u2502"
BOX_LINE = ("\u250c", "\u2502", "\u2514")           # a line of a box's shape starts with one of these
LEDGER_TEXT_MAX = 4000                              # characters of a request's text kept in its ledger row

# Transcript records, told apart by byte patterns before any decoding (the compact form measured exact on 14,003
# records of this session's transcript, 2026-09-29: every assistant record holds one content block). Each pattern
# also takes JSON's spaced form (`"type": "text"`), so a writer that spaces its JSON cannot blind the hook silently.


def _pat(key, value):
    return (b'"%s":"%s' % (key, value), b'"%s": "%s' % (key, value))


P_ASSISTANT = _pat(b"type", b'assistant"')
P_THINKING = _pat(b"type", b'thinking"')
P_TEXT = _pat(b"type", b'text"')
P_TOOL_USE = _pat(b"type", b'tool_use"')
P_USER = _pat(b"type", b'user"')
P_SUMMARY = _pat(b"subtype", b'stop_hook_summary"')
P_API_ERROR = _pat(b"subtype", b'api_error"')
P_INTERRUPT = (b"[Request interrupted",)
P_TURN = _pat(b"turnOrigin", b"")


def has(raw, pats):
    return any(p in raw for p in pats)

NONCE_LINE = ("Chat form (LS-B10) nonce {n}: to run a stack without a tool call, end your message with one box per "
              "request, such as the three lines `┌─ find · r1 · {n}`, `│ q: who calls "
              "parse_message`, `└─` (a label of scripts/stacks.toml, a new id per box, a `│ key: "
              "value` line per parameter; below a `│ ┄┄┄` line, the stack's body, verbatim), "
              "nothing after them and the nonce nowhere else; fallback, one line: `REQ {n} <id> <label> "
              "key=value ...`. A Stop hook runs each through scripts/stack.py and answers `RES {n} <id> <status>`.")

GIT_UNCOMMITTED = ("There are uncommitted changes in the repository. Please commit and push these changes to the "
                   "remote branch.")
GIT_UNTRACKED = ("There are untracked files in the repository. Please commit and push these changes to the remote "
                 "branch.")


class HookError(Exception):
    """A failure the hook reports in one line."""


# ---------------------------------------------------------------- small helpers

def utc(fmt="%Y-%m-%dT%H:%M:%SZ"):
    return datetime.datetime.now(datetime.timezone.utc).strftime(fmt)


def u16(text):
    return len(text.encode("utf-16-le")) // 2


def cut16(text, n):
    """The longest prefix of text that is at most n UTF-16 units (a surrogate pair is never split)."""
    return text.encode("utf-16-le", "surrogatepass")[:2 * max(n, 0)].decode("utf-16-le", "ignore")


def short(text, n=REASON_MAX):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[:n - 1] + "…"


def main_tree(root):
    """The main tree of `root` (git's common dir's parent), or None."""
    try:
        r = subprocess.run(["git", "-C", root, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                           capture_output=True, text=True, timeout=GIT_TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return os.path.dirname(os.path.realpath(r.stdout.strip())) if r.returncode == 0 and r.stdout.strip() else None


class Ctx:
    """What a run resolves once: the .jev dir, the state dir, the options."""

    def __init__(self, opts, env):
        given = env.get("AF_REQ_STATE")
        if given:
            self.jev = os.path.realpath(given)
        else:
            main = main_tree(ROOT)
            if main is None:
                raise HookError("the main tree of %s did not resolve (git rev-parse --git-common-dir)" % ROOT)
            self.jev = os.path.join(main, ".jev")
        self.sdir = os.path.join(self.jev, "req")
        self.off = os.path.lexists(os.path.join(self.jev, "req-off"))   # a dangling link counts too
        self.opts = opts
        cap = env.get("CLAUDE_CODE_STOP_HOOK_BLOCK_CAP", "") or ""
        valid = re.fullmatch(r"[0-9]{1,4}", cap.strip()) is not None
        self.cap = int(cap.strip()) if valid else DEFAULT_CAP
        self.cap_note = "" if valid or not cap else (" (CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=%r is not a non-negative "
                                                     "integer: the default %d applies)" % (cap[:20], DEFAULT_CAP))

    def path(self, *parts):
        return os.path.join(self.sdir, *parts)


def hook_log(ctx, rec):
    """One JSON line per hook run in <state>/hooks.jsonl; never the text; a failed write loses the line only."""
    try:
        os.makedirs(ctx.sdir, mode=0o700, exist_ok=True)
        path = ctx.path("hooks.jsonl")
        try:
            if os.path.getsize(path) > LOG_MAX_BYTES:
                os.replace(path, path + ".1")
        except FileNotFoundError:
            pass
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
        try:
            os.write(fd, (json.dumps({"t": utc(), **rec}, sort_keys=True) + "\n").encode())
        finally:
            os.close(fd)
    except Exception:
        pass


def payload_fields(payload, need_transcript=True):
    """(session, transcript) from a hook payload; HookError when either is unusable."""
    if not isinstance(payload, dict):
        raise HookError("the hook payload is not a JSON object")
    session = payload.get("session_id")
    if not (isinstance(session, str) and SESSION_RE.fullmatch(session)):
        raise HookError("the payload's session_id is missing or malformed")
    transcript = payload.get("transcript_path")
    if not need_transcript:
        return session, transcript if isinstance(transcript, str) else None
    if not (isinstance(transcript, str) and os.path.isabs(transcript) and os.path.isfile(transcript)):
        raise HookError("the payload's transcript_path is missing or not a file")
    return session, transcript


# ---------------------------------------------------------------- the per-session state

STATE_TYPES = {"v": int, "session": str, "transcript": str, "nonces": list, "turn_start": int, "read": int,
               "t_blocks": int, "o_blocks": int, "chain_open": bool, "undelivered": list}


def state_path(ctx, session):
    return ctx.path("sessions", session + ".json")


def load_state(ctx, session):
    """The session's state, or None when it has none; HookError when the file is unreadable or malformed."""
    path = state_path(ctx, session)
    try:
        with open(path, "rb") as fh:
            st = json.loads(fh.read())
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as e:
        raise HookError("the state %s is unreadable (%s)" % (path, type(e).__name__))
    bad = [k for k, t in STATE_TYPES.items() if type(st.get(k) if isinstance(st, dict) else None) is not t]
    if bad or not all(isinstance(n, str) and NONCE_RE.fullmatch(n) for n in st["nonces"]):
        raise HookError("the state %s is malformed (%s)" % (path, ", ".join(bad) or "nonces"))
    return st


def new_state(session, transcript, start):
    return {"v": 1, "session": session, "transcript": transcript or "", "nonces": [], "turn_start": start,
            "read": start, "t_blocks": 0, "o_blocks": 0, "chain_open": False, "undelivered": []}


def save_state(ctx, st):
    d = ctx.path("sessions")
    os.makedirs(d, mode=0o700, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".state.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(st, fh, sort_keys=True)
        os.replace(tmp, state_path(ctx, st["session"]))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------- the transcript

class Rec:
    __slots__ = ("kind", "off", "uuid", "msg", "text", "blocking")

    def __init__(self, kind, off, uuid=None, msg=None, text=None, blocking=False):
        self.kind, self.off, self.uuid, self.msg, self.text, self.blocking = kind, off, uuid, msg, text, blocking


def classify(raw, off):
    """One transcript line as a Rec, or None. A thinking record is recognised by its bytes and skipped undecoded; of a
    decoded record only `text` blocks are read (a thinking block in another spelling is decoded, never read)."""
    if has(raw, P_ASSISTANT):
        if has(raw, P_THINKING) or not (has(raw, P_TEXT) or has(raw, P_TOOL_USE)):
            return None
    elif has(raw, P_USER):
        if not (has(raw, P_INTERRUPT) or has(raw, P_TURN)):
            return None
    elif not (has(raw, P_SUMMARY) or has(raw, P_API_ERROR)):
        return None
    try:
        obj = json.loads(raw)
    except ValueError:
        return None
    if not isinstance(obj, dict) or obj.get("isSidechain") is True:
        return None
    # every transcript line has an identity (known() matches by occurrence): a record with no uuid, never measured, is
    # known by its byte offset
    kind = obj.get("type")
    uuid = obj.get("uuid") if isinstance(obj.get("uuid"), str) and obj.get("uuid") else "@%d" % off
    if kind == "assistant":
        msg = obj.get("message") if isinstance(obj.get("message"), dict) else {}
        blocks = [b for b in (msg.get("content") or []) if isinstance(b, dict)] if isinstance(msg.get("content"),
                                                                                            list) else []
        # a thinking block whose bytes the skip above did not match is decoded here, but only `text` blocks are read
        if obj.get("isApiErrorMessage") is True:
            return Rec("error", off, uuid)
        if any(b.get("type") == "tool_use" for b in blocks):
            return Rec("tool_use", off, uuid)
        texts = [b["text"] for b in blocks if b.get("type") == "text" and isinstance(b.get("text"), str)]
        if not texts:
            return None
        mid = msg.get("id") if isinstance(msg.get("id"), str) else None
        return Rec("text", off, uuid, mid or uuid or "@%d" % off, "\n".join(texts))
    if kind == "user":
        c = (obj.get("message") or {}).get("content") if isinstance(obj.get("message"), dict) else None
        first = c if isinstance(c, str) else next((b.get("text") for b in c if isinstance(b, dict)
                                                   and b.get("type") == "text"), None) if isinstance(c, list) else None
        if isinstance(first, str) and first.startswith("[Request interrupted"):
            return Rec("interrupt", off, uuid)
        if obj.get("isCompactSummary") is True:
            return None                  # a compaction's summary carries turnOrigin too, but no new query starts there
        if isinstance(obj.get("turnOrigin"), str) and obj.get("turnOrigin"):
            return Rec("turn", off, uuid)
        return None
    if kind == "system" and obj.get("subtype") == "stop_hook_summary":
        errs = obj.get("hookErrors")
        return Rec("stop", off, uuid, blocking=isinstance(errs, list) and len(errs) > 0)
    if kind == "system" and obj.get("subtype") == "api_error":
        return Rec("error", off, uuid)
    return None


def scan(path, start, align=False):
    """(records, end, bytes read) of the transcript from byte `start` to its last complete line. align: `start` may
    be inside a line, whose rest is skipped."""
    recs, off = [], start
    with open(path, "rb") as fh:
        fh.seek(start)
        if align and start > 0:
            off += len(fh.readline())
        for raw in fh:
            if not raw.endswith(b"\n"):
                break                    # a line still being written: the next scan reads it whole
            rec = classify(raw, off)
            off += len(raw)
            if rec is not None:
                recs.append(rec)
    return recs, off, off - start


def line_floor(path):
    """The file's size, minus a last line still being written."""
    with open(path, "rb") as fh:
        size = fh.seek(0, os.SEEK_END)
        if size == 0:
            return 0
        fh.seek(max(0, size - 65536))
        tail = fh.read()
    cut = tail.rfind(b"\n")
    return size if tail.endswith(b"\n") else (size - len(tail) + cut + 1 if cut >= 0 else max(0, size - len(tail)))


def message_groups(recs):
    """[(message id, [(uuid, text, offset)])]: each API message's text blocks, in file order."""
    order, groups = [], {}
    for r in recs:
        if r.kind == "text":
            if r.msg not in groups:
                groups[r.msg] = []
                order.append(r.msg)
            groups[r.msg].append((r.uuid, r.text, r.off))
    return [(m, groups[m]) for m in order]


# ---------------------------------------------------------------- the grammar

class Cand:
    """One request line or box (kind "request": its head is well formed) or one malformed line that carries a current
    nonce (kind "malformed"). reason: why it is refused as malformed, or None. form: "req" or "box"; body: a box's text
    below its divider, or None."""
    __slots__ = ("kind", "nonce", "id", "label", "params", "reason", "uuid", "line", "off", "text", "sha", "source",
                 "form", "body")

    def __init__(self, kind, nonce, cid, label, uuid, line, off, source):
        self.kind, self.nonce, self.id, self.label = kind, nonce, cid, label
        self.params, self.reason, self.text, self.sha = [], None, "", ""
        self.uuid, self.line, self.off, self.source = uuid, line, off, source
        self.form, self.body = "req", None


def why_malformed(line, nonce):
    """Why a line that carries the nonce is not a request line."""
    s = line.rstrip(" \t\r")
    odd = sorted({"U+%04X" % ord(c) for c in s if c.isspace() and c != " "})
    if odd:
        return "a whitespace character other than the ASCII space in the line (%s); use single ASCII spaces" % (
            ", ".join(odd))
    if s.startswith("RES "):
        return "a receipt quoted with the nonce: quote receipts without it"
    if s.startswith("┌"):
        return why_top(s, nonce)
    if "┌─" in s and "REQ " not in s:
        return "text or markup before ┌─: a box's top edge starts the line, bare"
    if not s.startswith("REQ "):
        if "REQ " in s:
            return "text or markup before REQ: a request line starts with REQ at the line's start, bare"
        return "the nonce outside a request line: write it only in request lines"
    parts = s.split(" ")
    if "" in parts:
        return "tokens are separated by one ASCII space"
    if len(parts) < 4:
        return "a request line is REQ <nonce> <id> <label> key=value ..."
    if parts[1] != nonce:
        return "the nonce is written %r: it is 12 lowercase hex digits" % parts[1][:24]
    if not ID_RE.fullmatch(parts[2]):
        return "the id %r: an id is [a-z][a-z0-9]{0,15}, such as r1" % parts[2][:24]
    if not LABEL_RE.fullmatch(parts[3]):
        return "the label %r is not a stack label" % parts[3][:32]
    return "the line breaks the request grammar"


def why_top(s, nonce):
    """Why a line that starts with ┌ and carries the nonce is not a box's top edge (s: trailing blanks removed)."""
    if not s.startswith("┌─ "):
        return "a box's top edge starts with ┌─ and a space, then <label> · <id> · <nonce>"
    parts = s[3:].split(" · ")
    if len(parts) != 3:
        return ("a box's top edge is ┌─ <label> · <id> · <nonce>, one space on each side of each "
                "·; found %r" % s[:60])
    if not LABEL_RE.fullmatch(parts[0]):
        return "the label %r is not a stack label" % parts[0][:32]
    if not ID_RE.fullmatch(parts[1]):
        return "the id %r: an id is [a-z][a-z0-9]{0,15}, such as r1" % parts[1][:24]
    if parts[2][:12] != nonce:
        return "the nonce is written %r: it is 12 lowercase hex digits" % parts[2].split(" ")[0][:24]
    return "after the nonce a box's top edge holds only a space and ─ (decoration); found %r" % parts[2][12:][:40]


def parse_box(lines, k, top, source):
    """(the box whose top edge is lines[k], the index of the line after it): THE BOX. It ends at its bottom edge, at
    the message's end (unclosed), or before a line that does not start with │ (the caller reads that line next)."""
    u, i, ln, off = lines[k]
    c = Cand("request", top.group(3), top.group(2), top.group(1), u, i, off, source)
    c.form, text, body = "box", [ln], None
    j = k + 1
    while True:
        if j >= len(lines):
            c.reason = c.reason or "an unclosed box: no bottom edge └─ before the end of the message"
            break
        s = lines[j][2].rstrip(" \t\r")
        if BOTTOM_RE.fullmatch(s):
            text.append(lines[j][2])
            j += 1
            break
        if not s.startswith(BAR):
            c.reason = c.reason or ("an inside line that does not start with │ (found %r): a box's lines start "
                                    "with │ up to its bottom edge └─" % s[:40])
            break
        text.append(lines[j][2])
        j += 1
        if s != BAR and not s.startswith(BAR + " "):
            c.reason = c.reason or ("an inside line is │, a space and its text, or a bare │; found %r"
                                    % s[:40])
            continue
        inner = s[2:]
        if DIVIDER_RE.fullmatch(inner):
            if body is not None:
                c.reason = c.reason or ("a second ┄┄┄ divider: a box has one, and its body runs from "
                                        "there to the bottom edge")
            body = [] if body is None else body
        elif body is not None:
            body.append(inner)
        elif inner:                      # an empty line among the parameters is skipped
            key, sep, value = inner.partition(": ")
            if not sep:
                c.reason = c.reason or ("a parameter line is key: value (a colon and a space after the key); found %r"
                                        % inner[:40])
            elif not NAME_RE.fullmatch(key):
                c.reason = c.reason or "a parameter's key is [a-z][a-z0-9_]{0,23}; found %r" % key[:32]
            else:
                c.params.append([key, value])
    if body is not None:
        c.body = "\n".join(body)
    if any("\x00" in v for _k, v in c.params) or "\x00" in (c.body or ""):
        c.reason = c.reason or "a value holds a NUL character"
    c.text = "\n".join(text)
    c.sha = hashlib.sha256(c.text.encode("utf-8", "surrogatepass")).hexdigest()
    return c, j


def parse_message(blocks, nonces, source):
    """The candidates of one message. blocks: [(uuid, text, offset)] in order; nonces: the current set."""
    lines = [(u, i, ln, off) for u, text, off in blocks for i, ln in enumerate(text.split("\n"))]
    out, reqs, after = [], [], []        # after: each line of text after the first request: is it a fence line
    k = 0
    while k < len(lines):
        u, i, ln, off = lines[k]
        s = ln.rstrip(" \t\r")
        top = TOP_RE.fullmatch(s)
        if top is not None:
            c, end = parse_box(lines, k, top, source)
            if c.nonce in nonces or c.reason is None:   # else an illustration: its lines are text, read below
                out.append(c)
                reqs.append(c)
                k = end
                continue
        m = HEAD_RE.fullmatch(s)
        if m is None:
            if reqs and s.strip():
                after.append(FENCE_RE.fullmatch(s) is not None)
            low = s.lower()
            hit = next((n for n in nonces if n in low), None)
            if hit is not None:
                c = Cand("malformed", hit, "?", None, u, i, off, source)
                c.reason, c.text = why_malformed(ln, hit), ln
                c.form = "box" if s.startswith(BOX_LINE) else "req"
                c.sha = hashlib.sha256(ln.encode("utf-8", "surrogatepass")).hexdigest()
                out.append(c)
            k += 1
            continue
        c = Cand("request", m.group(1), m.group(2), m.group(3), u, i, off, source)
        blocks_open = []                 # (index into c.params, end word)
        for tok in m.group(4).split(" ")[1:]:
            pm = PARAM_RE.fullmatch(tok)
            if pm is None:
                c.reason = c.reason or "a parameter is key=value with a lowercase key; found %r" % tok[:40]
                continue
            key, val = pm.groups()
            if val.startswith("<<"):
                if not WORD_RE.fullmatch(val[2:]):
                    c.reason = c.reason or ("a block opens with key=<<WORD (WORD: 1 to 16 capitals, digits or _); "
                                            "found %r" % tok[:40])
                    continue
                blocks_open.append((len(c.params), val[2:]))
                c.params.append([key, ""])
            else:
                c.params.append([key, val])
        text = [ln]
        k += 1
        for idx, word in blocks_open:
            body = []
            while k < len(lines) and lines[k][2].rstrip(" \t\r") != word:
                body.append(lines[k][2])
                k += 1
            c.params[idx][1] = "\n".join(body)
            text += body
            if k >= len(lines):
                c.reason = c.reason or "an unclosed block: no line %s before the end of the message" % word
                break
            text.append(lines[k][2])
            k += 1
        if any("\x00" in v for _k, v in c.params):
            c.reason = c.reason or "a value holds a NUL character"
        c.text = "\n".join(text)
        c.sha = hashlib.sha256(c.text.encode("utf-8", "surrogatepass")).hexdigest()
        out.append(c)
        reqs.append(c)
    # the closing rule: text after the first request refuses them all; a fence line is text only in a message that
    # holds no box (the REQ lines' rule, unchanged)
    boxed = any(c.form == "box" for c in reqs)
    if any(not (fence and boxed) for fence in after):
        for c in reqs:
            c.reason = c.reason or "text after the request lines: they close the message's text"
    return out


def lam_missing(lam, recs, nonces, earlier=()):
    """True when last_assistant_message holds a request line or a current-nonce line that no text record of the
    window holds: the transcript has not caught up. A record in `earlier` (one an earlier round answered or bound) does
    not count: that text is the final response's last block (PM P3a), newer than any such record, so a byte-identical
    line there is another occurrence (VERIFY-LS-B10 F1)."""
    if not lam:
        return False
    want = [s for s in (ln.rstrip(" \t\r") for ln in lam.split("\n"))
            if HEAD_RE.fullmatch(s) or TOP_RE.fullmatch(s) or any(n in s.lower() for n in nonces)]
    if not want:
        return False
    have = {ln.rstrip(" \t\r") for r in recs if r.kind == "text" and r.uuid not in earlier for ln in r.text.split("\n")}
    return any(w not in have for w in want)


def collect(recs, lam, nonces):
    """Every candidate of the window, in transcript order; the last_assistant_message fallback (lam) last."""
    out = []
    for _mid, blocks in message_groups(recs):
        out += parse_message(blocks, nonces, "transcript")
    if lam:
        out += parse_message([(None, lam, None)], nonces, "last_assistant_message")
    return out


# ---------------------------------------------------------------- the ledger

def read_ledger(ctx):
    """The ledger's bytes (empty before its first row); HookError when it cannot be read."""
    try:
        with open(ctx.path("ledger.jsonl"), "rb") as fh:
            return fh.read()
    except FileNotFoundError:
        return b""
    except OSError as e:                  # never read as empty: every answered request would look unanswered
        raise HookError("the ledger %s is unreadable (%s)" % (ctx.path("ledger.jsonl"), type(e).__name__))


def ledger_index(ctx, session, nonces, data=None):
    """{(nonce, id): [row]} of this session's rows for these nonces (bad lines are counted, never trusted); `data`: the
    ledger's bytes, when the caller read them already (read_ledger)."""
    idx, bad = {}, 0
    if data is None:
        data = read_ledger(ctx)
    needles = [n.encode() for n in nonces]
    sneedle = session.encode()
    for raw in data.split(b"\n"):
        if not raw.strip() or sneedle not in raw or not any(n in raw for n in needles):
            continue
        try:
            row = json.loads(raw)
        except ValueError:
            bad += 1
            continue
        if isinstance(row, dict) and row.get("session") == session and row.get("nonce") in nonces:
            idx.setdefault((row["nonce"], row.get("id")), []).append(row)
    return idx, bad


def append_rows(ctx, rows):
    """The rows appended to ledger.jsonl in ONE write, under flock of ledger.lock."""
    if not rows:
        return
    data = b"".join((json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n").encode() for r in rows)
    os.makedirs(ctx.sdir, mode=0o700, exist_ok=True)
    lock = os.open(ctx.path("ledger.lock"), os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX)
        fd = os.open(ctx.path("ledger.jsonl"), os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            if os.write(fd, data) != len(data):
                raise OSError("a short write to the ledger")
        finally:
            os.close(fd)
    finally:
        os.close(lock)


def known(c, idx, seen, path):
    """How a line stands against the ledger and this run's earlier lines (`seen`), matched by occurrence, never by text
    (VERIFY-LS-B10 F1): "same" when a row carries its record and line (its receipt, or the `bind` row of a
    last_assistant_message receipt); the fallback row itself when this transcript line is the record of that receipt (a
    row with no uuid, carrying `fb`): the first such row of the same request text, in ledger order, from this
    transcript, whose round read up to at or before this line's record (`after`) and that no bind row holds yet, so a
    fallback receipt absorbs ONE transcript line (the caller binds them); "dup" when another line holds its (nonce, id);
    else None. A last_assistant_message line (no uuid) is a line of a message the transcript does not show yet: a new
    occurrence, never "same" as another line, a byte-identical one included."""
    rows = idx.get((c.nonce, c.id), []) + seen.get((c.nonce, c.id), [])
    if c.uuid is not None:
        for row in rows:
            if row.get("uuid") == c.uuid and row.get("line") == c.line:
                return "same"
        held = {row.get("binds") for row in rows}
        for row in rows:
            if (row.get("fb") and row["fb"] not in held and row.get("sha") == c.sha and row.get("transcript") == path
                    and type(row.get("after")) is int and c.off >= row["after"]):
                return row
    if c.kind == "request" and rows:
        return "dup"
    return None


def row_of(ctx, session, transcript, c, status, reason, delivered, **extra):
    row = {"v": 1, "ts": utc(), "session": session, "nonce": c.nonce, "id": c.id, "label": c.label, "kind": c.kind,
           "status": status, "reason": reason, "uuid": c.uuid, "line": c.line, "sha": c.sha, "source": c.source,
           "transcript": transcript, "delivered": delivered, "form": c.form,
           "text": c.text if len(c.text) <= LEDGER_TEXT_MAX else c.text[:LEDGER_TEXT_MAX - 1] + "…"}
    row.update(extra)
    return row


def bind_row(ctx, session, transcript, c, fbrow):
    """The row that ties a transcript line to the last_assistant_message receipt it is the record of: the line's record
    and line, and the receipt's `fb` (item 6's pairing for that receipt). It is not a receipt: its status is `bound`."""
    return row_of(ctx, session, transcript, c, "bound", None, None, kind="bind", binds=fbrow["fb"])


def receipt_of(c, status, reason=None, rc=None, run=None):
    if status == "ran":
        return "RES %s %s ran rc=%s run=%s" % (c.nonce, c.id, rc, run or "none")
    return "RES %s %s %s: %s" % (c.nonce, c.id, status, short(reason))


# ---------------------------------------------------------------- running a request

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stack_labels(ctx):
    """({label: the stack's body parameter or None}, labels sorted; None) or (None, why the registry did not load),
    through the runner's own loader."""
    try:
        runner = load_module("ls_req_stack", STACK)
        _tools, stacks = runner.load_registry(ctx.opts.get("registry") or runner.DEFAULT_REGISTRY)
        return {label: stacks[label].body for label in sorted(stacks)}, None
    except Exception as e:  # a Refusal, or the runner missing
        return None, short("%s" % e if type(e).__name__ == "Refusal" else "%s: %s" % (type(e).__name__, e))


LIVE = []                  # the runner now running: a SIGTERM, SIGINT or SIGHUP to this hook passes on to it as a
                           # SIGTERM (it kills its steps)


def killpg(pid, sig):
    try:
        os.killpg(pid, sig)
    except (ProcessLookupError, PermissionError):
        pass


def on_term(signum, _frame):
    for p in list(LIVE):
        killpg(p.pid, signal.SIGTERM)
    raise SystemExit(128 + signum)


def run_request(ctx, c, deadline, body_key=None):
    """(status, reason, rc, run id, the runner's print) of one request run through scripts/stack.py. body_key: the
    parameter a box's body fills."""
    left = deadline - time.monotonic()
    if left < MIN_START_S:
        return "refused", "budget (%.0f s of the %.0f s round budget left: not started)" % (
            max(left, 0), ctx.opts["budget"]), None, None, ""
    argv = [sys.executable, STACK]
    for opt in ("registry", "log_dir"):
        if ctx.opts.get(opt):
            argv += ["--" + opt.replace("_", "-"), ctx.opts[opt]]
    params = c.params + ([[body_key, c.body]] if c.body is not None else [])
    argv += ["--", c.label] + ["%s=%s" % (k, v) for k, v in params]
    t0 = time.monotonic()
    try:
        proc = subprocess.Popen(argv, cwd=ctx.opts["tree"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, start_new_session=True)
    except (OSError, ValueError) as e:
        return "refused", "the runner did not start: %s" % e, None, None, ""
    LIVE.append(proc)
    try:
        out, err = proc.communicate(timeout=left)
    except subprocess.TimeoutExpired:
        killpg(proc.pid, signal.SIGTERM)          # the runner kills its steps' process groups on SIGTERM
        try:
            out, err = proc.communicate(timeout=KILL_GRACE_S)
        except subprocess.TimeoutExpired:
            killpg(proc.pid, signal.SIGKILL)
            out, err = proc.communicate()
        text = (out + err).decode("utf-8", "replace")
        return "refused", "budget (stopped after %.0f s, at the %.0f s round budget; the runner exited %s)" % (
            time.monotonic() - t0, ctx.opts["budget"], proc.returncode), proc.returncode, None, text
    finally:
        LIVE.remove(proc)
    out_s, err_s = out.decode("utf-8", "replace"), err.decode("utf-8", "replace")
    m = RUN_LINE_RE.match(out_s)
    if proc.returncode in (0, 1) and m:
        return "ran", None, proc.returncode, m.group(2), out_s + (("--- stderr ---\n" + err_s) if err_s else "")
    msg = short(err_s.strip().replace("stack: ", "", 1) or out_s.strip() or "no output")
    if proc.returncode == 2:
        return "refused", msg, 2, None, out_s + err_s
    if proc.returncode == 3:
        return "refused", "runner error: " + msg, 3, None, out_s + err_s
    return "ran", None, proc.returncode, None, out_s + err_s


# ---------------------------------------------------------------- the feedback

def neutralizer():
    """(scripts/handback_extract.py's neutralize, None) or (the identity, why it did not load)."""
    try:
        return load_module("ls_req_handback", HANDBACK).neutralize, None
    except Exception as e:
        return (lambda text: (text, 0)), "%s: %s" % (type(e).__name__, e)


def cut_body(body, keep, saved):
    """body cut to about `keep` characters (its head and its tail) around a marker naming the saved file."""
    head, tail = body[:keep // 2], body[len(body) - (keep - keep // 2):] if keep - keep // 2 else ""
    marker = "… %d characters cut; in full: %s" % (len(body) - len(head) - len(tail),
                                                 os.path.basename(saved) if saved else "not saved")
    return "\n".join(x for x in (head, marker, tail) if x)


def assemble(head, sections, outdir, cap=FEEDBACK_CAP):
    """(the feedback text, how many RES lines it shows). head: lines; sections: (RES line, body, saved path); outdir:
    the directory of the saved prints. Over `cap` the largest bodies are cut first (one level L: every body longer than
    L keeps about L characters, and a marker names its saved file) and every RES line stays whole. When even the RES
    lines with their markers are over the cap, no print is shown and the RES lines that do not fit are left out: the
    caller reports those at the next prompt."""
    def render(bodies, note):
        out = list(head) + ([note] if note else [])
        for (res, _b, _s), body in zip(sections, bodies):
            out.append(res)
            if body:
                out.append(body)
        return "\n".join(out) + "\n"

    text = render([b for _r, b, _s in sections], None)
    if u16(text) <= cap:
        return text, len(sections)
    note = "(the feedback is capped at %s characters: a cut print is saved in full in %s/, under the name its cut " \
           "gives)" % (format(cap, ","), outdir)
    lo, hi, best = 0, max(len(b) for _r, b, _s in sections), None
    while lo <= hi:
        level = (lo + hi) // 2
        attempt = render([cut_body(b, level, s) if len(b) > level else b for _r, b, s in sections], note)
        if u16(attempt) <= cap:
            best, lo = attempt, level + 1
        else:
            hi = level - 1
    if best is not None:
        return best, len(sections)
    lines = list(head) + ["(the feedback is capped at %s characters: no print fits beside the receipts; each is saved "
                          "in full in %s/ as <nonce>-<id>.txt)" % (format(cap, ","), outdir)]
    shown = 0
    for res, _b, _s in sections:
        if u16("\n".join(lines + [res])) + 200 > cap:
            break
        lines.append(res)
        shown += 1
    if shown < len(sections):
        lines.append("… %d more receipts: the next prompt's context carries them" % (len(sections) - shown))
    return "\n".join(lines) + "\n", shown


def save_print(ctx, session, c, text):
    """The runner's full print saved under out/<session>/; its path, or None when it could not be saved."""
    try:
        d = ctx.path("out", session)
        os.makedirs(d, mode=0o700, exist_ok=True)
        path = os.path.join(d, "%s-%s.txt" % (c.nonce, c.id))
        with open(path, "w", encoding="utf-8", errors="replace") as fh:
            fh.write(text)
        return path
    except OSError:
        return None


# ---------------------------------------------------------------- the chain-end git report

def git_report(cwd):
    """The harness git check's first dirty or unpushed hit in its own words, or None (its signing check is not
    repeated: it is neither a dirty nor an unpushed check)."""
    def g(*args):
        try:
            return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=GIT_TIMEOUT_S)
        except (OSError, subprocess.TimeoutExpired):
            return None

    r = g("rev-parse", "--git-dir")
    if r is None or r.returncode != 0:
        return None
    r = g("remote")
    if r is None or not r.stdout.strip():
        return None
    for args in (("diff", "--quiet"), ("diff", "--cached", "--quiet")):
        r = g(*args)
        if r is None or r.returncode != 0:
            return GIT_UNCOMMITTED
    r = g("ls-files", "--others", "--exclude-standard")
    if r is not None and r.stdout.strip():
        return GIT_UNTRACKED
    r = g("branch", "--show-current")
    branch = r.stdout.strip() if r is not None and r.returncode == 0 else ""
    if not branch:
        return None
    r = g("rev-parse", "origin/" + branch)
    upstream = "origin/" + branch if r is not None and r.returncode == 0 else "origin/HEAD"
    r = g("rev-list", upstream + "..HEAD", "--count")
    unpushed = int(r.stdout.strip()) if r is not None and r.returncode == 0 and r.stdout.strip().isdigit() else 0
    if unpushed > 0:
        if upstream == "origin/" + branch:
            return ("There are %d unpushed commit(s) on branch '%s'. Please push these changes to the remote "
                    "repository." % (unpushed, branch))
        return ("Branch '%s' has %d unpushed commit(s) and no remote branch. Please push these changes to the remote "
                "repository." % (branch, unpushed))
    return None


# ---------------------------------------------------------------- the reconciler

def how_ended(recs, c, restart=None):
    """How the turn after the candidate's record ended, where the transcript shows it. restart: the SessionStart
    source when a new process ends the query."""
    for r in recs:
        if c.off is not None and r.off <= c.off:
            continue
        if r.kind == "interrupt":
            return "an interrupt, transcript record %s" % (r.uuid or "@%d" % r.off)
        if r.kind == "error":
            return "an API error, transcript record %s" % (r.uuid or "@%d" % r.off)
    if restart:
        return "unknown: the session restarted (SessionStart, source %s) before a Stop answered it" % short(restart, 20)
    return "unknown: no interrupt or error after it in the transcript, and no Stop answered it"


def ended(recs):
    """True when the window's last end marker ends the harness query: a non-blocking Stop, an interrupt or an error.
    A blocking Stop, tool work or nothing at all: the query is still running."""
    state = False
    for r in recs:
        if r.kind == "stop":
            state = not r.blocking
        elif r.kind in ("interrupt", "error"):
            state = True
        elif r.kind in ("text", "tool_use") and state:
            state = False
    return state


def reconcile(ctx, st, recs=None, restart=None):
    """(report lines, rows, bytes read) for the window [turn_start, EOF) of the state's transcript (`recs` when the
    caller scanned it already): a receipt for every request line there that has none, and the state's undelivered
    receipts. restart: see how_ended."""
    lines, rows, nbytes = ["delivered late: " + u for u in st["undelivered"] if isinstance(u, str)], [], 0
    st["undelivered"] = []
    path = st["transcript"]
    if not st["nonces"] or not path:
        return lines, rows, 0
    if recs is None:
        try:
            recs, _end, nbytes = scan(path, st["turn_start"])
        except OSError as e:
            lines.append("the last turn's transcript could not be read (%s): its requests cannot be checked" % (
                type(e).__name__))
            return lines, rows, 0
    cands = collect(recs, None, st["nonces"])
    idx, _bad = ledger_index(ctx, st["session"], sorted({c.nonce for c in cands}))
    seen = {}
    for c in cands:
        k = known(c, idx, seen, path)
        if isinstance(k, dict):                   # the record of a last_assistant_message receipt: tied to it, once
            rows.append(bind_row(ctx, st["session"], path, c, k))
            seen.setdefault((c.nonce, c.id), []).append(rows[-1])
            continue
        if k == "same":
            continue
        if c.kind == "request" and c.nonce not in st["nonces"]:
            status, reason = "refused", "stale nonce (not a nonce of that turn)"
        elif k == "dup":
            status, reason = "refused", "duplicate id (%s is taken for nonce %s)" % (c.id, c.nonce)
        else:
            status, reason = "unanswered", how_ended(recs, c, restart)
        rows.append(row_of(ctx, st["session"], path, c, status, reason, "context"))
        seen.setdefault((c.nonce, c.id), []).append(rows[-1])
        what = c.label if c.kind == "request" else "(a line with the nonce: %s)" % short(c.text, 60)
        lines.append("%s: %s %s (%s)" % (status, c.id, what, short(reason, 200)) if status == "unanswered" else
                     receipt_of(c, status, reason))
    return lines, rows, nbytes


def context_text(report, nonce):
    """The injected context: the reconciler's report (its lines neutralized, then capped; the ledger holds every
    receipt), then the nonce line."""
    tail = NONCE_LINE.format(n=nonce) if nonce else ""
    head = ""
    if report:
        neutralize, neut_error = neutralizer()
        lines = ["Chat form (LS-B10): receipts of the last turn you have not seen (`unanswered`: it did not run; "
                 "re-issue any still wanted, with a new id):"] + [neutralize(x)[0] for x in report]
        if neut_error:
            lines.append("(control tags NOT neutralized: scripts/handback_extract.py did not load: %s)" % short(
                neut_error))
        head = "\n".join(lines)
        room = FEEDBACK_CAP - u16(tail) - 100
        if u16(head) > room:
            head = cut16(head, room) + "\n… cut here: the ledger holds every receipt"
    return "\n".join(x for x in (head, tail) if x)


def emit_context(event, text):
    if text:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))


# ---------------------------------------------------------------- the subcommands

def cmd_prompt(ctx, payload):
    session, transcript = payload_fields(payload)
    t0 = time.monotonic()
    report, rows, nbytes, was_ended, recs = [], [], 0, True, None
    try:
        st = load_state(ctx, session)
    except HookError as e:                        # said once, then a fresh state: a broken file must not keep the
        st = None                                 # chat form off for good
        report.append("%s: the last turn's requests cannot be checked; a fresh state starts now" % e)
    size = line_floor(transcript)
    if st is not None and st["transcript"] == transcript and st["turn_start"] <= size:
        recs, _e, nbytes = scan(transcript, st["turn_start"])
        was_ended = ended(recs)
    if st is not None and was_ended:
        lines, rows, more = reconcile(ctx, st, recs)
        report += lines
        nbytes += more
    elif st is not None:                          # the query runs on: its requests are the next Stop's
        report += ["delivered late: " + u for u in st["undelivered"] if isinstance(u, str)]
        st["undelivered"] = []
    append_rows(ctx, rows)
    nonce = secrets.token_hex(6)
    if st is None or was_ended:
        st = new_state(session, transcript, size)
        st["nonces"] = [nonce]
    else:
        st["nonces"] = (st["nonces"] + [nonce])[-KEEP_NONCES:]
    save_state(ctx, st)
    emit_context("UserPromptSubmit", context_text(report, nonce))
    hook_log(ctx, {"event": "prompt", "session": session, "ms": round((time.monotonic() - t0) * 1000, 1),
                   "bytes": nbytes, "ended": was_ended, "reported": len(report), "nonces": len(st["nonces"])})
    return 0


def cmd_session_start(ctx, payload):
    """A compaction inside a running query keeps the query's window, counts and chain (its pending requests are the
    next Stop's) and re-injects the current nonce, which the compaction dropped from the context. Any other start (a
    new process: startup, resume, clear; or a compaction after the query ended) ends the query: its requests are
    reconciled, and the chat form stays off until the next prompt mints a nonce."""
    session, transcript = payload_fields(payload, need_transcript=False)
    t0 = time.monotonic()
    st = load_state(ctx, session)
    if st is None:
        return 0
    source = payload.get("source") if isinstance(payload.get("source"), str) else ""
    here = transcript if isinstance(transcript, str) and os.path.isfile(transcript) else None
    recs, nbytes = None, 0
    if source == "compact" and here is not None and st["transcript"] == here and st["turn_start"] <= line_floor(here):
        recs, _end, nbytes = scan(here, st["turn_start"])
    running = recs is not None and not ended(recs)
    if running:
        report = ["delivered late: " + u for u in st["undelivered"] if isinstance(u, str)]
        st["undelivered"] = []
        nonce = st["nonces"][-1] if st["nonces"] else None
    else:
        report, rows, more = reconcile(ctx, st, recs, restart=None if source == "compact" else (source or "unknown"))
        append_rows(ctx, rows)
        nbytes += more
        base = here or (st["transcript"] if st["transcript"] and os.path.isfile(st["transcript"]) else None)
        st = new_state(session, base, line_floor(base) if base else 0)
        nonce = None
    save_state(ctx, st)
    emit_context("SessionStart", context_text(report, nonce))
    hook_log(ctx, {"event": "session-start", "session": session, "source": source, "bytes": nbytes,
                   "ms": round((time.monotonic() - t0) * 1000, 1), "reported": len(report), "running": running})
    return 0


def cmd_defer(ctx, payload):
    """`defer` when a text written since the last Stop (the harness writes a Stop's summary record after its hooks end,
    so this Stop's own is not there yet), or last_assistant_message, carries a current nonce: the texts this Stop's
    round answers. Content only, never the ledger, which the Stop hook writes at the same time."""
    session, transcript = payload_fields(payload)
    st = load_state(ctx, session)
    if st is None or not st["nonces"] or st["transcript"] != transcript:
        return 1
    size = os.path.getsize(transcript)
    start = max(st["turn_start"], size - DEFER_TAIL_BYTES)
    recs, _end, _n = scan(transcript, start, align=start > st["turn_start"])
    last_stop = max((i for i, r in enumerate(recs) if r.kind == "stop"), default=-1)
    texts = [r.text for r in recs[last_stop + 1:] if r.kind == "text"]
    lam = payload.get("last_assistant_message")
    if isinstance(lam, str):
        texts.append(lam)
    if any(n in t.lower() for t in texts for n in st["nonces"]):
        print("defer")
        return 0
    return 1


def cmd_stop(ctx, payload):
    session, transcript = payload_fields(payload)
    if isinstance(payload.get("agent_id"), str) and payload.get("agent_id"):
        return 0                                  # the main thread only
    t0 = time.monotonic()
    st = load_state(ctx, session)
    if st is None or not st["nonces"]:
        return 0                                  # no nonce this turn: the chat form is off
    nonces = st["nonces"]
    start, align, reanchored = max(st["read"], st["turn_start"]), False, False
    size = os.path.getsize(transcript)
    if st["transcript"] != transcript or size < start:
        # a transcript this state did not follow, or one that shrank: read its end only, never the whole file
        start = max(0, size - DEFER_TAIL_BYTES)
        align, reanchored = start > 0, True
        st.update(transcript=transcript, turn_start=start, read=start)
    recs, end, nbytes = scan(transcript, start, align=align)
    lam = payload.get("last_assistant_message") if isinstance(payload.get("last_assistant_message"), str) else ""
    ledger = read_ledger(ctx)                     # read once: the catch-up wait judges the window against it

    def earlier():
        """The uuids of the window's records that an earlier round answered or bound (see lam_missing)."""
        cs = collect(recs, None, nonces)
        idx, seen, out = ledger_index(ctx, session, sorted({c.nonce for c in cs}), ledger)[0], {}, set()
        for c in cs:
            k = known(c, idx, seen, transcript)
            if isinstance(k, dict):
                seen.setdefault((c.nonce, c.id), []).append({"uuid": c.uuid, "line": c.line, "binds": k["fb"]})
            if isinstance(k, dict) or k == "same":
                out.add(c.uuid)
        return out

    def missing():
        return lam_missing(lam, recs, nonces, earlier() if lam else ())
    waited, use_lam = 0.0, False
    if missing():
        stop_at = time.monotonic() + ctx.opts["catchup"]
        while time.monotonic() < stop_at and missing():
            time.sleep(CATCHUP_POLL_S)
            recs, end, nbytes = scan(transcript, start, align=align)
        waited = time.monotonic() - t0
        use_lam = missing()
    # the consecutive blocking Stops with no tool call between them, as the harness counts them (PM P2)
    t_blocks, o_blocks = st["t_blocks"], st["o_blocks"]
    for r in recs:
        if r.kind in ("tool_use", "turn") or (r.kind == "stop" and not r.blocking):
            t_blocks = o_blocks = 0
        elif r.kind == "stop":
            t_blocks += 1
    count = max(t_blocks, o_blocks)
    cands = collect(recs, lam if use_lam else None, nonces)
    idx, bad_rows = ledger_index(ctx, session, sorted({c.nonce for c in cands}), ledger)
    pending, seen, binds = [], {}, []
    for c in cands:
        k = known(c, idx, seen, transcript)
        if isinstance(k, dict):                   # the record of a last_assistant_message receipt: tied to it, once
            binds.append(bind_row(ctx, session, transcript, c, k))
            seen.setdefault((c.nonce, c.id), []).append(binds[-1])
            continue
        if k == "same":
            continue
        pending.append((c, k))
        seen.setdefault((c.nonce, c.id), []).append({"uuid": c.uuid, "line": c.line, "sha": c.sha})

    def lam_fields(c):                            # a fallback row: the token its record's bind row names, and the
        return {"fb": secrets.token_hex(8), "after": end} if c.uuid is None else {}   # offset its record lands after
    current = [(c, k) for c, k in pending if c.nonce in nonces]
    st.update(read=end, t_blocks=t_blocks, o_blocks=o_blocks)
    log = {"event": "stop", "session": session, "bytes": nbytes, "candidates": len(cands), "pending": len(pending),
           "count": count, "waited_s": round(waited, 2), "lam": use_lam, "bad_ledger_rows": bad_rows,
           "reanchored": reanchored}
    if not current:
        # stale lines alone never block (a quoted old line must not continue the turn): their receipts wait for the
        # next prompt's report
        rows = [row_of(ctx, session, transcript, c, "refused", "stale nonce (not this turn's)", "no", **lam_fields(c))
                for c, _k in pending]
        append_rows(ctx, binds + rows)            # a bind is written before `read` passes its record
        st["undelivered"] += [receipt_of(c, "refused", "stale nonce (not this turn's)") for c, _k in pending]
        message = None
        if st["chain_open"]:
            st["chain_open"] = False
            if payload.get("stop_hook_active") is True and count + 1 < ctx.cap - 1:
                cwd = payload.get("cwd") if isinstance(payload.get("cwd"), str) else ""
                message = git_report(cwd) if cwd and os.path.isdir(cwd) else None
        if message:
            st["o_blocks"] = count + 1
        save_state(ctx, st)
        hook_log(ctx, dict(log, ms=round((time.monotonic() - t0) * 1000, 1), outcome="git" if message else "pass"))
        if message:
            sys.stderr.write("Chat form (LS-B10), the chain's end: the harness git check is silent for the rest of "
                             "this turn (stop_hook_active), so this hook ran its dirty and unpushed checks in %s:\n%s\n"
                             % (cwd, message))
            return 2
        return 0
    # a request round: from here on every receipt is delivered, whatever else fails; a signal that ends this hook
    # ends its runner too (the runner is in its own session, so a signal to this hook's group never reaches it)
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, on_term)
    n = count + 1
    at_cap = n >= ctx.cap - 1
    over = n > ctx.cap                            # above the cap the harness drops a blocking Stop's feedback (PM P2)
    labels, registry_error = (None, None) if at_cap else stack_labels(ctx)
    deadline = t0 + ctx.opts["budget"]
    runs_base = ctx.opts["log_dir"] or os.path.join(main_tree(ctx.opts["tree"]) or ctx.opts["tree"], ".jev", "stacks")
    sections, ran, failures = [], 0, []
    if not over:
        st.update(o_blocks=n, chain_open=True)
    try:
        append_rows(ctx, binds)                   # before any save of the state moves `read` past their records
    except OSError as e:
        failures.append("the bind rows (%s)" % e)
    for c, k in pending:
        status, reason, rc, run, text = "refused", None, None, None, ""
        if c.kind == "malformed":
            reason = "malformed (%s)" % c.reason
        elif c.nonce not in nonces:
            reason = "stale nonce (not this turn's)"
        elif k == "dup":
            reason = "duplicate id (%s is taken for this nonce: every request line takes a new id)" % c.id
        elif c.reason:
            reason = "malformed (%s)" % c.reason
        elif over:                                # the advice first, as below
            reason = ("cap: nothing ran; continue with tool calls (python3 scripts/stack.py %s ...): this was Stop %d "
                      "in a row with no tool call, above the harness's cap of %d, where it drops a Stop hook's "
                      "feedback, so this receipt waited for the next prompt%s" % (c.label, n, ctx.cap, ctx.cap_note))
        elif at_cap:                              # the advice first: a long cap_note is cut at REASON_MAX, never it
            reason = ("cap: nothing ran; continue with tool calls (python3 scripts/stack.py %s ...): this is blocking "
                      "Stop %d in a row with no tool call, and above %d the harness ends the turn%s" % (
                          c.label, n, ctx.cap, ctx.cap_note))
        elif labels is None:
            reason = "the registry did not load: %s" % registry_error
        elif c.label not in labels:
            reason = "unknown label %r (the stacks: %s)" % (c.label, ", ".join(labels))
        elif c.body is not None and labels[c.label] is None:          # THE BOX's two body cases, the registry's
            reason = ("malformed (a body below ┄┄┄, but stack %s names no body parameter: give its "
                      "parameters as key: value lines)" % c.label)
        elif c.body is not None and any(k == labels[c.label] for k, _v in c.params):
            reason = ("malformed (the parameter line %s: sets the body parameter of stack %s, which the body below "
                      "┄┄┄ sets too)" % (labels[c.label], c.label))
        else:
            status, reason, rc, run, text = run_request(ctx, c, deadline, labels[c.label])
            ran += status == "ran"
        saved = save_print(ctx, session, c, text) if text else None
        res = receipt_of(c, status, reason, rc, run)
        try:
            append_rows(ctx, [row_of(ctx, session, transcript, c, status, reason, "no" if over else "feedback", rc=rc,
                                     run=run, run_dir=os.path.join(runs_base, run) if run else None, out=saved,
                                     receipt=res, **lam_fields(c))])
        except OSError as e:
            failures.append("the ledger row of %s (%s)" % (c.id, e))
        sections.append((res, text.rstrip("\n"), saved))
        # undelivered until the feedback is written: a hook killed mid-round leaves it for the next prompt's report
        st["undelivered"].append(res)
        try:
            save_state(ctx, st)
        except OSError as e:
            if not any(f.startswith("the session state") for f in failures):
                failures.append("the session state (%s)" % e)
    if over and not any(f.startswith("the session state") for f in failures):
        # above the cap nothing is written for the harness to drop and nothing blocks: the refusals stay undelivered
        # in the saved state, and the next prompt reports them (VERIFY-LS-B10 F4); a state that could not be saved
        # cannot carry them, so then they go out below as at the cap
        hook_log(ctx, dict(log, ms=round((time.monotonic() - t0) * 1000, 1), outcome="over-cap", ran=ran,
                           receipts=len(sections), shown=0))
        return 0
    neutralize, neut_error = neutralizer()
    head = ["Chat form (LS-B10) receipts, one per request line (%d; nonce %s%s):" % (
        len(sections), nonces[-1], ", the last_assistant_message fallback" if use_lam else "")]
    if at_cap:
        head.append("REFUSED AT THE CAP: this is blocking Stop %d in a row with no tool call between; above %d the "
                    "harness ends the turn and drops this text. Nothing ran. Continue with tool calls." % (n, ctx.cap))
    if reanchored:
        head.append("(the transcript changed under this session's state: only its last %d bytes were read)" % (
            DEFER_TAIL_BYTES))
    if failures:
        head.append("NOT WRITTEN: %s; the next prompt's report may list these requests as unanswered, though they ran "
                    "as below" % short("; ".join(failures), 400))
    if neut_error:
        head.append("(control tags NOT neutralized: scripts/handback_extract.py did not load: %s)" % short(neut_error))
    # every piece is neutralized BEFORE the cap is applied (the rule lengthens text), and a cut cannot form a tag:
    # the pieces are joined by newlines and a cut marker, and a tag needs `<` right before its name
    text, shown = assemble([neutralize(x)[0] for x in head],
                           [(neutralize(res)[0], neutralize(body)[0], saved and neutralize(saved)[0])
                            for res, body, saved in sections],
                           neutralize(ctx.path("out", session))[0])
    sys.stderr.write(text)
    sys.stderr.flush()
    base = len(st["undelivered"]) - len(sections)
    del st["undelivered"][base:base + shown]      # this round's, now written; any past the cap wait for the next prompt
    try:
        save_state(ctx, st)
    except OSError:
        pass                                      # the next prompt then reports them once more: a double, not a loss
    hook_log(ctx, dict(log, ms=round((time.monotonic() - t0) * 1000, 1), outcome="cap" if at_cap else "round",
                       ran=ran, receipts=len(sections), shown=shown))
    return 2


COMMANDS = {"prompt": cmd_prompt, "session-start": cmd_session_start, "stop": cmd_stop, "defer-check": cmd_defer}


def main(argv=None, env=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    env = os.environ if env is None else env
    opts = {"registry": None, "log_dir": None, "tree": ROOT, "budget": ROUND_BUDGET_S, "catchup": CATCHUP_S}
    command = argv.pop(0) if argv else None
    fail_rc = 1 if command == "defer-check" else 0
    try:
        while argv:
            flag = argv.pop(0)
            key = {"--registry": "registry", "--log-dir": "log_dir", "--tree": "tree", "--budget": "budget",
                   "--catchup": "catchup"}.get(flag)
            if key is None or not argv:
                raise HookError("usage: ls_req.py {%s} [test options]; %r is not one" % ("|".join(COMMANDS), flag))
            value = argv.pop(0)
            opts[key] = float(value) if key in ("budget", "catchup") else os.path.realpath(value)
        if command not in COMMANDS:
            raise HookError("usage: ls_req.py {%s}" % "|".join(COMMANDS))
        ctx = Ctx(opts, env)
        if ctx.off:
            return fail_rc
        raw = sys.stdin.buffer.read()
        try:
            payload = json.loads(raw.decode("utf-8")) if raw.strip() else {}
        except ValueError:
            raise HookError("the hook payload is not JSON")
        return COMMANDS[command](ctx, payload)
    except Exception as e:                        # fail loud in one line, never block, never stall
        why = short("%s" % e if isinstance(e, HookError) else "%s: %s" % (type(e).__name__, e), 300)
        line = "ls_req %s: %s (the chat form did not act; use tool calls)" % (command or "?", why)
        if command in ("prompt", "session-start"):
            emit_context("UserPromptSubmit" if command == "prompt" else "SessionStart", line)
        else:
            sys.stderr.write(line + "\n")
        return fail_rc


if __name__ == "__main__":
    sys.exit(main())
