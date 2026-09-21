"""S0-01 pinned constants — the ONE place the proof's expected values live.

Imported by check_acp_conformance.py (positive legs) and check_initialize.py (negative leg).
Every value here is an EXACT expectation: the checker compares with ==, never `in`/startswith.
Values were read from the PC on 2026-09-05 (sha256sum / readlink -f / the baseline manifest
summary); the baseline body itself is committed at
proofs/S0-01/evidence/golden/manifests/manifest-baseline.txt.gz and the digests below are
re-derived from it by the checker (a pin is integrity, the re-derivation is correctness).
"""
import gzip
import json
import os
import re
import stat
import sys
from pathlib import Path


def require_regular_file(path: Path, what: str, failure_type: type[Exception] = ValueError) -> Path:
    """Return path only for a regular file, before any operation that could block on it."""
    candidate = Path(path)
    try:
        mode = os.stat(candidate, follow_symlinks=False).st_mode
    except OSError:
        raise failure_type(f"{what} absent") from None
    if not stat.S_ISREG(mode):
        raise failure_type(f"{what} is not a regular file: {candidate.name}")
    return candidate

# --- the pinned runtime (the isolated clones under /home/rocco/s0-01-pinned on the PC) ---
PINNED_BUZZ_ACP_EXE_REALPATH = "/home/rocco/s0-01-pinned/buzz/target/release/buzz-acp"
PINNED_BUZZ_ACP_SHA256 = "a5a17ffc0c7ef878648a506b9d5066120b91984d1158a60e6ce9664a39f88064"
PINNED_AGENT_REALPATH = "/home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp"
PINNED_AGENT_ENTRYPOINT_SHA256 = "f90a0cc333fa86d99495c7c984e4e11a1b83a7e3dc92883b7fd295ae70358ef1"
PINNED_AGENT_INTERPRETER_REALPATH = "/usr/bin/python3.13"
PINNED_AGENT_INTERPRETER_SHA256 = "8be0f8e534b7fe4ace77feaa47e2b6a15c3458523c76dab4582867727c286637"
PINNED_HERMES_HOME = "/home/rocco/s0-01-pinned/.hermes-home"
PINNED_RELAY_URL = "ws://127.0.0.1:3999"
PINNED_TEE_PATH = "/home/rocco/agent-factory/proofs/S0-01/tools/frame_tee.py"
PINNED_PATH = "/usr/bin:/bin"
PINNED_HOME = "/home/rocco"

# --- model egress: the scripted backend behind the managed OmniRoute (ADR 0002) ---
PINNED_UPSTREAM_HOST = "127.0.0.1:20201"
PINNED_ROUTE_PREFIX = "s0-01-scripted"
ALLOWED_UPSTREAM_GET = frozenset({("GET", "/models"), ("GET", "/v1/models")})  # OmniRoute discovery polls
UPSTREAM_POST_PATH = "/v1/chat/completions"

# --- buzz-acp configuration echo (docs/03 line 13: BUZZ_ACP_MAX_TURN_DURATION=3600) ---
PINNED_IDLE_TIMEOUT = "900s"
PINNED_MAX_TURN = "3600s"
PINNED_IDLE_TIMEOUT_ARG = "900"
PINNED_MAX_TURN_DURATION_ARG = "3600"
PINNED_SESSION_POLICY = "thread"
PINNED_LAUNCH_ARGV = [
    PINNED_BUZZ_ACP_EXE_REALPATH,
    "--relay-url", PINNED_RELAY_URL,
    "--agent-command", PINNED_TEE_PATH,
    "--agent-args", "",
    "--idle-timeout", PINNED_IDLE_TIMEOUT_ARG,
    "--max-turn-duration", PINNED_MAX_TURN_DURATION_ARG,
]
PINNED_ENV_KEYS = frozenset({
    "PATH", "HOME", "BUZZ_PRIVATE_KEY", "BUZZ_RELAY_URL", "BUZZ_ACP_AGENT_OWNER",
    "BUZZ_ACP_RESPOND_TO", "BUZZ_ACP_SESSION_POLICY", "HERMES_HOME", "OMNIROUTE_API_KEY",
    "PYTHONDONTWRITEBYTECODE", "S0_01_FRAMEDIR", "S0_01_AGENT",
})
ENV_ALLOWLIST_KEY = "BUZZ_ACP_RESPOND_TO_ALLOWLIST"  # present ONLY in the two-users leg
REDACTED_ENV_KEY_RE = r"(?i)(KEY|TOKEN|SECRET|PASSWORD|NSEC|PRIV)"

# --- the S0-02-only pinned extension (owner decision 2026-09-08, D-022; task #47 option a, task #52) ---
# The three buzz-acp-decided S0-02 legs are observable only through tracing::debug! lines, so buzz-acp must
# run with RUST_LOG=debug. S0-01's closed set is UNCHANGED: the extension is a second, separately pinned set
# the launcher selects only when asked for by name (`--env-set s0-02`), never implicitly — S0-01's golden
# corpus stays graded against PINNED_ENV_KEYS exactly as today.
PINNED_ENV_KEYS_S0_02 = PINNED_ENV_KEYS | frozenset({"RUST_LOG"})
PINNED_ENV_VALUES_S0_02 = {"RUST_LOG": "debug"}

# --- the pinned ACP handshake ---
PINNED_CLIENT_PROTOCOL_VERSION = 2
PINNED_AGENT_PROTOCOL_VERSION = 1
PINNED_AGENT_CAPABILITIES = {
    "loadSession": True,
    "promptCapabilities": {"image": True},
    "sessionCapabilities": {"fork": {}, "list": {}, "resume": {}},
}

# --- source immutability (manifest v2.2): typed entries `<sha256> <f|l> <mode4>  ./path[ -> target]` of the
# FOUR trees that constitute the executed code (hermes-agent editable install, buzz incl. the buzz-acp
# binary, the acp schema tree, and the hermes venv with the acp SDK + deps); symlinks listed with targets ---
MANIFEST_LINE_RE = r"^[0-9a-f]{64} [fl] [0-7]{4}  \./.+$"
MANIFEST_TREES = ("hermes-agent", "buzz", "acp", "venv-hermes")  # header order in the manifest body (v2.2: the venv is executed code too)
# RE-BASELINED 2026-09-21 (VB-F12 preflight, tasks/briefs/s0-01-vb-f12-recapture-v24.md §P4): the 2026-09-06 baseline
# pinned 26 bytecode caches inside hermes-agent (written by the pre-flag exploratory runs); a foreign 2026-09-18 run
# replaced that set (26 gone, 101 new) and left a root `.bytecode-fingerprint` (git:HEAD:<sha>), and two of the 26
# cannot be regenerated byte-identically under CPython 3.13.11 — byte-identity with the old baseline is unreachable.
# The tree is pinned AS MEASURED on 2026-09-21 (buzz/acp/venv-hermes unchanged, digests equal): every cache and the
# marker are pinned entries, so a later foreign write fails the manifest check LOUD (the correct outcome; the
# S0-01 launcher itself never writes bytecode — PYTHONDONTWRITEBYTECODE=1 in its env).
PINNED_BASELINE_DIGESTS = {
    "hermes-agent": "31843deb9602d5299c417fcca7c435edcf365e8523cdeb3dfec3db2c4c068e96",
    "buzz": "a5614f3c1d904c145c26d5a49e670fa49fc9075b9e0e39ccbed93bc2771e1e95",
    "acp": "0039fb357d4170d9e67313210b8933726a6b82ea2f2882e17164c08c41603122",
    "venv-hermes": "c181f47c563cdc6edfbe4550352ac0cfc7221760e2ddf0396d6efed2a39ee523",
}
PINNED_BASELINE_FILE_COUNTS = {"hermes-agent": 11441, "buzz": 11665, "acp": 270, "venv-hermes": 10653}  # entries incl. symlinks (v2.2 format; hermes-agent re-measured 2026-09-21)
PINNED_BASELINE_GZ_SHA256 = "ff6af5130361cb15fa61b74627c328b0e93fcd303581589b86eb8a3b4039ca12"

# --- legs, mentions, models ---
LEGS = ("run-1", "run-2", "cancel", "shutdown", "two-users")
MENTION_TEXT = "Reply with exactly the single word: pong"
EXPECTED_MODEL = {
    "run-1": "s0-01-pong", "run-2": "s0-01-pong",
    "cancel": "s0-01-slow",
    "shutdown": "s0-01-pong", "two-users": "s0-01-pong",
}
# (tag, identity_key, expected_content, replies_to_tag_or_None)
EXPECTED_MENTIONS = {
    "run-1": [("owner", "owner", MENTION_TEXT, None)],
    "run-2": [("owner", "owner", MENTION_TEXT, None)],
    "cancel": [("owner", "owner", MENTION_TEXT, None), ("cancel-cmd", "owner", "!cancel", "owner")],
    "shutdown": [("owner", "owner", MENTION_TEXT, None), ("shutdown-cmd", "owner", "!shutdown", "owner")],
    "two-users": [("owner", "owner", MENTION_TEXT, None), ("user2", "user2", MENTION_TEXT, None)],
}
MENTION_WINDOW_SLACK_S = 5       # relay created_at is whole seconds; the timeline is microseconds
UPSTREAM_WINDOW_SLACK_S = 5.0    # backend received_at vs the prompt/terminal frames

# --- the frozen golden: set to the sha256 of golden/golden.jsonl by the coordinator AFTER the
# first accepted v2 capture; None means "no golden pinned yet" and the checker FAILS on it. ---
# ASYNC_SESSION_UPDATES (owner decision (a), 2026-09-21 — AF-AP-107, docs/INCIDENT-LOG.md): the CLOSED
# set of session/update kinds the pinned hermes-acp emits from an INDEPENDENT task, so their position
# relative to the prompt's request/response stream is undefined by the protocol. The normalizer makes
# exactly these kinds order-free (placed right after the session/new response that introduced their
# session), so the golden is defined over the protocol-ordered sub-stream. Measured 2026-09-21 on
# run-1/run-2 of the real v2.4 bundle: session_info_update is the only async kind observed (run-1:
# before the reply chunk; run-2: after the end_turn result). A NEW kind is a pins change with its own
# measurement — this tuple is closed, not open.
ASYNC_SESSION_UPDATES = ("session_info_update",)
# Set under owner decision (a), 2026-09-21 (AF-AP-107), from the regenerated
# golden/golden.jsonl (order-free session_info_update, 11 lines). None was the pre-decision state: the
# checker failed on it. See the ASYNC_SESSION_UPDATES comment above for why the golden is defined this
# way; D-034 (no round-19 bypass fix) stands — this is a contract change the owner made, not a checker
# round that papers over the race.
# sha256 = sha256 of the regenerated golden.jsonl bytes (11 lines, new order-free normalizer).
PINNED_GOLDEN_SHA256 = "6225adb8ecc21a24d578696e2b9c25c81ebd5a82068c4411f780930c2fa54221"

# --- the negative control (audit 2026-09-05 P1 "negative execution"): the pinned hermes-acp REJECTS a
# malformed initialize (missing protocolVersion) with this JSON-RPC error — observed live on the PC
# 2026-09-05 17:57Z; the negative leg requires exactly this response, never a mere classification. ---
PINNED_NEGATIVE_ERROR_CODE = -32602
PINNED_NEGATIVE_ERROR_MESSAGE = "Invalid params"
NEGATIVE_REQUIRED_FILES = frozenset({"timeline.jsonl", "runtime-identity.json", "env.json", "agent-stderr.txt"})
NEGATIVE_IDENTITY_KEYS = frozenset({
    "probe_path", "probe_sha256", "agent_argv", "agent_realpath", "agent_entrypoint_sha256",
    "agent_child_pid", "agent_interpreter_realpath", "agent_interpreter_sha256",
    "python_dont_write_bytecode", "spawned_at_utc", "agent_exit_code",
})

# --- two-users leg (audit 2026-09-05 P1 "sequential users"): the production config BUZZ_ACP_AGENTS=1
# (docs/03) plus hermes' steering_supported=false make turn execution SERIAL by construction; the leg
# proves concurrency at the ingress (both mentions pending before the first terminal) and asserts the
# serialization it observes. These log lines must appear exactly once in the leg's buzzacp.log. ---
PINNED_LOG_LINES_TWO_USERS = (
    'agent initialized agent=0 name="hermes-agent" steering_supported=false',
    "agent_pool_ready agents=1",
)

# Startup-line pins consumed by check_config_echo (round 5, A26): the production configuration that the
# two-users serialization finding depends on (docs/03: BUZZ_ACP_AGENTS=1; buzz-acp echoes `dedup=Queue`).
# Read 2026-09-06 from a real capture's startup-line.txt (scratchpad/realleg/golden/run-1).
PINNED_STARTUP_AGENTS = "1"
PINNED_STARTUP_DEDUP = "Queue"
PINNED_STARTUP_IGNORE_SELF = "true"

# Startup-line pins for the checker's mcp_cmd / permission_mode tokens (A5f-F42; the checker's local `_PINS_PENDING`
# dict is retired by lane A5g). Re-resolved 2026-09-06 against the committed golden corpus
# (proofs/S0-01/evidence/golden/*/startup-line.txt): `mcp_cmd=` empty on 7/7 legs, `permission_mode=bypassPermissions`
# on every leg that carries the key (5/5). The value records what the pinned buzz-acp ECHOES in the proof configuration;
# it is not a governance ruling — effectful tools still pass the fail-closed pre_tool_call policy hook (standing rule 9).
PINNED_STARTUP_MCP_CMD = ""
PINNED_STARTUP_PERMISSION_MODE = "bypassPermissions"
# `respond_to` as buzz-acp echoes it (CK7-F42's last local literal, checker ~:1089): `owner-only` on run-1/run-2/cancel/shutdown,
# `allowlist(1)` on two-users — read 2026-09-06 from the same golden corpus (4 + 1 startup lines).
PINNED_STARTUP_RESPOND_TO = "owner-only"
PINNED_STARTUP_RESPOND_TO_TWO_USERS = "allowlist(1)"
# The remaining startup-line values (VERIFY-CK8 F6: 10 of 21 keys were unconstrained), read 2026-09-06 from the same golden
# corpus — identical on all five legs; `pubkey` stays per-capture (format-checked only). Consumed by lane A5g.
PINNED_STARTUP_SUBSCRIBE = "Mentions"
PINNED_STARTUP_CONTEXT_LIMIT = "12"
PINNED_STARTUP_MAX_TURNS_PER_SESSION = "0"
PINNED_STARTUP_HEARTBEAT = "0s"
PINNED_STARTUP_MEH = "Steer"
PINNED_STARTUP_MEMORY = "true"
PINNED_STARTUP_PRESENCE = "true"
PINNED_STARTUP_TYPING = "true"
PINNED_STARTUP_MODEL = "(agent default)"

# tee-status.json (A21d) key set — ONE pin for the three consumers (the tee test, the checker; the tee itself stays
# a standalone tool whose own key set a test asserts EQUAL to this pin — R6-B5b-F16, AF-AP-42 "no local copy").
# Order = the tee's write order (proofs/S0-01/tools/frame_tee.py _write_status, read 2026-09-06).
PINNED_TEE_STATUS_KEYS = (
    "final", "agent_returncode", "drained", "stdin_reader_done",
    "recorded_c2a", "recorded_a2c", "forwarded_c2a", "forwarded_a2c",
    "write_errors", "exit_code", "updated_seq", "updated_utc",
)

# --- the ONE producer/consumer file list for a captured leg (P5a; SWEEP-prod rows #1/#27/#28) ---
# The checker's private `_LEG_REQUIRED_FILES` (20 names) and what the PC capture pipeline actually writes had
# drifted apart: the real corpus leg run-1 carries 8 names that allowlist REJECTS (backend-healthz-before.json,
# backend-healthz-after.json, hermes-config.sha256, launch.exited, launch.ready, manifest-pre.done,
# manifest-post.done, teardown.txt) and lacks 2 it REQUIRES. This mapping is the ONE list both sides read; the
# rejected alternative was extending the checker's private set, which is how the two drifted in the first place.
#
# Status vocabulary — what a COLLECTED leg (proofs/S0-01/evidence/golden/<leg>, built by tools/pc/collect_leg.sh
# out of the PC framedir) may and must contain:
#   "required"            present in every collected positive leg; a consumer REQUIRES it
#   "optional"            may be present; a consumer ADMITS it, never requires it
#   "excluded_on_collect" written into the PC framedir, dropped by collect_leg.sh's --exclude list; never collected
# THREE statuses, not four (VERIFY-P5a F10): `transient` claimed manifest-pre.txt / manifest-post.txt are
# "replaced in place before the leg closes", but nothing enforced it — collect_leg.sh's --exclude list did not
# match them, and the end-to-end tar test had to add them back to its expected set to pass, i.e. the real tar
# proved the opposite of the status name. The window is reachable: pc_manifest.sh can die between writing $OUT
# and gzipping it, and for the POST phase pc_post.sh waits 120 s and exits 0 anyway, so run_leg.sh collects a
# leg still carrying manifest-post.txt. collect_leg.sh now excludes `manifest-*.txt` and the two names are
# `excluded_on_collect` — a claim the tar test proves in both directions instead of a comment.
# Names beginning with "." are NOT here: they are atomic-write scratch (frame_tee.py's `.tee-status.tmp`), never
# a leg ENTRY — the writer renames them away, and one that survived a crash SHOULD be rejected by a consumer's
# entry allowlist as an unexpected entry, which is the right outcome for an incomplete capture.
# A consumer's entry allowlist is {required} | {optional} | PINNED_LEG_DIRS; {required} is what it demands.
# Every name names its producer below; a producer that starts writing a new framedir name must add it here
# (tests/test_s0_01_pc_tools.py parses the producers and fails on a name that is not in this mapping, and on a
# mapping name no producer writes). Derived 2026-09-08 by reading the producers and cross-checked against the
# real-leg corpus (S0_01_REAL_LEG_DIR, scripts/realleg_sync.sh).
#
# NOT here, deliberately: `agent-stderr.txt` — NO positive-leg producer writes it. It is written only by
# tools/acp_probe.py into the NEGATIVE leg and is already pinned by NEGATIVE_REQUIRED_FILES above. The checker's
# F20 "agent-stderr.txt is REQUIRED in every positive leg" is therefore unsatisfiable by the current pipeline;
# either the tee drains the agent's stderr to that name or the checker drops the requirement (both out of P5a).
PINNED_LEG_FILES = {
    # --- tools/pc/pc_launch.py ---
    "argv.txt": "required",
    "backend-healthz-before.json": "required",
    "buzz-acp.exit": "required",
    "buzz-acp.pid": "required",
    "buzzacp.raw.log": "excluded_on_collect",   # unmasked; the masked buzzacp.log is what travels
    "env.json": "required",
    "hermes-config.sha256": "required",
    "hermes-model.txt": "required",
    "launch.exited": "required",
    "launch.ready": "required",
    "manifest-pre.log": "excluded_on_collect",  # the detached pc_manifest.sh's stdout
    "owned-pids.json": "required",              # rewritten by pc_post.sh's `scan after`
    "runtime-identity.json": "required",        # created by frame_tee.py, merged by pc_launch.py
    "startup-line.txt": "required",
    # --- tools/pc/pc_post.sh ---
    "backend-healthz-after.json": "required",
    "buzzacp.log": "required",
    "manifest-post.log": "excluded_on_collect",
    "process-scan-after.txt": "required",
    "process-scan-teardown.txt": "required",
    "teardown.txt": "optional",                 # absent on the shutdown leg: buzz-acp exits on its own, so
                                                # pc_post.sh's teardown block is skipped (corpus: 3 of 4 legs)
    # --- tools/pc/pc_manifest.sh (PHASE=pre|post) ---
    "manifest-pre.done": "required",
    "manifest-pre.summary": "required",
    "manifest-pre.txt": "excluded_on_collect",  # gzip -9 -n -f replaces it with the .gz; a crash
                                                # between the two leaves it behind, so collect drops it
    "manifest-pre.txt.gz": "required",
    "manifest-pre.txt.gz.sha256": "optional",   # collected by collect_leg.sh, stripped from the real-leg corpus
                                                # by scripts/realleg_sync.sh pc-build — admit, never require
    "manifest-post.done": "required",
    "manifest-post.summary": "required",
    "manifest-post.txt": "excluded_on_collect",
    "manifest-post.txt.gz": "required",
    "manifest-post.txt.gz.sha256": "optional",
    # --- tools/frame_tee.py ---
    "frames-agent-to-client.jsonl": "required",
    "frames-client-to-agent.jsonl": "required",
    "tee-status.json": "required",              # v2.3+ captures only; a v2.2 corpus predates it
    "timeline.jsonl": "required",
    # --- tools/build_capture_record.py ---
    "capture.json": "optional",                 # human-reading record; the checker never trusts its content
}
# Names whose presence depends on the capture's contract version, with the version that introduced them. A
# consumer grading an OLDER corpus drops these from {required} instead of failing it (the checker's own
# `_corpus_version` rule, mirrored in tests/test_s0_01_pc_tools.py).
PINNED_LEG_FILES_SINCE = {"tee-status.json": "v2.3"}
PINNED_LEG_DIRS = {
    "mentions": "required",           # pc_launch.py creates it; pc_mention.sh writes <tag>.receipt.json/.err/.event.json
    "upstream-records": "required",   # pc_launch.py creates it; pc_post.sh copies the backend's records into it
}


# --- the ONE list, exported as FUNCTIONS (VERIFY-P5a F2 + its item-13 design ruling) ---
# F2 was a SHAPE defect, not a typo. `build_capture_record.py` re-derived the required set straight off the
# mapping and never learned PINNED_LEG_FILES_SINCE, so it hard-failed every leg the pipeline has ever produced
# (`run-1: missing required leg files: tee-status.json`) while the TEST mirror, which did know the rule, stayed
# green: the version rule had been written twice and only one copy was right. Exporting the DERIVED sets as
# functions is what makes a second copy impossible — the tool in both modes, this repo's tests and the checker
# all call these, and a rule change lands in one place.
PINNED_SCAN_VERSIONS = ("v2.3", "v2.4")   # the capture-contract versions whose process-scan-after.txt carries an
                                          # enumeration header; a v2.2 leg's line 1 is a body row, or the file is
                                          # empty (a clean v2.2 shutdown scan wrote no rows at all)
_SCAN_HEADER_VERSION_RE = re.compile(r"^# process-scan (v\d+\.\d+) ")

# The FULL strict header grammars (the checker's own `_SCAN_HEADER_RE`, check_acp_conformance.py:158-161,
# mirrored here so the table's `scan-headed` kind and the strict detector can reject trailing fields / CRLF /
# wrong counters / second headers): every later line must be a `<pid> <ppid> <etimes> <cmd...>` body row.
# v2.4 adds `table_rows` (A20: the full-table counter, distinct from the body counter); v2.3 does not carry
# it. P5c pinned the strict decision over a sniffer.
_SCAN_HEADER_FULL_RE = {
    "v2.4": re.compile(
        r"^# process-scan v2\.4 mode=(after|teardown) rows=(\d+) buzz_acp_pid=(\d+|none) buzz_present=([01]) "
        r"owned=(\d+) owned_present=(\d+) pinned_present=(\d+) owned_zombies=(\d+) table_rows=(\d+) "
        r"utc=(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)$"),
    "v2.3": re.compile(
        r"^# process-scan v2\.3 mode=(after|teardown) rows=(\d+) buzz_acp_pid=(\d+|none) buzz_present=([01]) "
        r"owned=(\d+) owned_present=(\d+) pinned_present=(\d+) owned_zombies=(\d+) "
        r"utc=(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)$"),
}

# --- F4: the per-(version, name) content constraint for every REQUIRED artifact (P5c, AMENDMENT-2) ---
# presence is not content (VERIFY-P5b F4). `build_capture_record.py` validates each present required file
# against `content_constraint(corpus_version(leg), name)` BEFORE constructing capture.json. The table is
# written row by rule below and completed programmatically, so a new required name without a rule is NOT
# possible silently: `content_constraint(version, name)` raises for an unnamed file, and a test asserts the
# key set equals `required_files(version)` for every known version.
#
# The kinds, closed:
#   json-object / json-array     json.loads and the top-level shape IS dict / list (a `[]` where an object is
#                                required is NAMED as wrong shape, not accepted)
#   jsonl-nonempty               >= 1 line, every line valid JSON
#   gzip-text-nonempty           valid gzip whose decompressed body is non-empty UTF-8 text
#   text-nonempty                valid UTF-8, non-empty
#   utf8-text-maybe-empty        valid UTF-8, empty allowed  (v2.2 scan artifacts: a clean v2.2 shutdown scan
#                                wrote no rows at all — corpus shutdown leg has a 0-byte process-scan-after.txt)
#   int-exit-code                one integer (buzz-acp.exit)
#   empty-marker                 exactly 0 bytes (manifest-pre/post.done: `.done` markers touched after the
#                                gzip and digest are complete — any content is foreign or corrupt)
#   scan-headed                  non-empty, line 1 full-matches the version's strict header grammar
#                                (_SCAN_HEADER_FULL_RE[version]), every later line a
#                                `<pid> <ppid> <etimes> <cmd>` body row with no second header
CONTENT_CONSTRAINT_KINDS = (
    "json-object", "json-array", "jsonl-nonempty", "gzip-text-nonempty", "text-nonempty",
    "int-exit-code", "empty-marker", "utf8-text-maybe-empty", "scan-headed",
)

_CONTENT_BY_EXT = (                                       # (predicate, kind) — first match wins
    (lambda n: n.endswith(".json"), "json-object"),
    (lambda n: n.endswith(".jsonl"), "jsonl-nonempty"),
    (lambda n: n.endswith(".txt.gz"), "gzip-text-nonempty"),
    (lambda n: n.endswith(".sha256"), "text-nonempty"),
    (lambda n: n.endswith(".log"), "text-nonempty"),
    (lambda n: n.endswith(".summary"), "text-nonempty"),
    (lambda n: n.endswith(".txt"), "text-nonempty"),
    # no-extension required names: an exit code (one int), a pid (one int), or a UTC timestamp
    (lambda n: n == "buzz-acp.exit", "int-exit-code"),
    (lambda n: n == "buzz-acp.pid", "int-exit-code"),
    (lambda n: n in ("launch.ready", "launch.exited"), "text-nonempty"),
)
_CONTENT_CONSTRAINTS = {
    # v2.2: no header; line 1 (if any) is a body row, and the file may be EMPTY (a clean shutdown scan
    # wrote no rows at all — the corpus shutdown leg carries a 0-byte process-scan-after.txt)
    ("v2.2", "process-scan-after.txt"): "utf8-text-maybe-empty",
    ("v2.2", "process-scan-teardown.txt"): "utf8-text-maybe-empty",
    # v2.3/v2.4 scan artifacts carry the enumeration header
    ("v2.3", "process-scan-after.txt"): "scan-headed",
    ("v2.3", "process-scan-teardown.txt"): "scan-headed",
    ("v2.4", "process-scan-after.txt"): "scan-headed",
    ("v2.4", "process-scan-teardown.txt"): "scan-headed",
}
_KNOWN_CORPUS_VERSIONS = ("v2.2",) + PINNED_SCAN_VERSIONS     # the versions the table is written for
for _v in _KNOWN_CORPUS_VERSIONS:
    for _n in (n for n, s in PINNED_LEG_FILES.items() if s == "required"):
        if (_v, _n) in _CONTENT_CONSTRAINTS:
            continue
        if _n in ("manifest-pre.done", "manifest-post.done"):
            _CONTENT_CONSTRAINTS[(_v, _n)] = "empty-marker"
        elif _n == "buzz-acp.exit":
            _CONTENT_CONSTRAINTS[(_v, _n)] = "int-exit-code"
        elif _n == "tee-status.json" and _v == "v2.2":
            continue                               # required only from v2.3 (PINNED_LEG_FILES_SINCE)
        else:
            _CONTENT_CONSTRAINTS[(_v, _n)] = next(k for pred, k in _CONTENT_BY_EXT if pred(_n))


def _version_key(version):
    return tuple(int(part) for part in version[1:].split("."))


def required_files(version):
    """The `required` leg-file names a capture of contract `version` must carry.

    A name introduced LATER than the leg's own version is dropped, never failed (PINNED_LEG_FILES_SINCE): that
    is the whole difference between grading the corpus and rejecting it. An unknown version RAISES — silently
    grading an unrecognised capture by some default set is the drift this list exists to end.
    """
    if version != "v2.2" and version not in PINNED_SCAN_VERSIONS:
        raise ValueError(f"required_files: unknown capture-contract version {version!r}")
    names = {n for n, s in PINNED_LEG_FILES.items() if s == "required"}
    for name, since in PINNED_LEG_FILES_SINCE.items():
        if _version_key(version) < _version_key(since):
            names.discard(name)
    return frozenset(names)


def entry_allowlist():
    """Every entry name a consumer ADMITS in a collected leg: required | optional | the required dirs.

    Anything else found in a leg directory is an unexpected entry — including a `.`-prefixed atomic-write
    scratch file that survived a crash, which is the right outcome for an incomplete capture.
    """
    return frozenset({n for n, s in PINNED_LEG_FILES.items() if s in ("required", "optional")}
                     | set(PINNED_LEG_DIRS))


def corpus_version(leg_dir):
    """The capture-contract version ONE collected leg was produced by — the ONE detector, from the leg's own
    process-scan-after.txt, which is the only versioned artefact a leg carries.

    STRICT (the pinned decision from P5c): a header-shaped line is the ONLY version evidence, and it is
    parsed, not sniffed — `_SCAN_HEADER_VERSION_RE` must full-match line 1 against ONE of the pinned
    grammars. A second header line, a header deeper in the body, trailing fields, CRLF →
    `process-scan header malformed: <reason>` from here, never a guessed version.
    A line with no `#` at all is the v2.2 pre-header shape (line 1 is a body row) or an empty file, both
    of which the pipeline really produces — but only when NO later-only required name is present (a
    headerless leg carrying tee-status.json is a dropped v2.4 header, refused by name).
    """
    scan = os.path.join(leg_dir, "process-scan-after.txt")
    if not os.path.isfile(scan):
        return "v2.2"
    with open(scan, "rb") as fh:
        raw = fh.read()
    if b"\r" in raw:
        raise ValueError(f"{scan}: process-scan header malformed: CRLF line ending")
    text = raw.decode("utf-8", errors="replace")
    if not text.splitlines():
        return "v2.2"
    lines = text.splitlines()
    first = lines[0]
    if first.startswith("#"):
        # a `#` line is a CLAIMED enumeration header: parse it STRICTLY — one pinned version grammar, full
        # match, no trailing fields, no second header line anywhere, no CRLF (checked above). A full grammar
        # line is only ever a header, so a `#` anywhere in the body is a smeared scan, never v2.2.
        if len(lines) > 1 and any(l.startswith("#") for l in lines[1:]):
            raise ValueError(f"{scan}: process-scan header malformed: a header line in the body")
        m = _SCAN_HEADER_VERSION_RE.match(first)
        if m is None:
            raise ValueError(f"{scan}: process-scan header malformed: {first[:90]!r}")
        version = m.group(1)
        strict = _SCAN_HEADER_FULL_RE.get(version)
        if strict is None or not strict.match(first):
            if version not in PINNED_SCAN_VERSIONS:
                raise ValueError(f"{scan}: process-scan header malformed: unknown version {version!r}")
            raise ValueError(f"{scan}: process-scan header malformed: {first[:90]!r}")
        return version
    # no `#` on line 1: the v2.2 pre-header shape (a body row or empty) — but ONLY when no header-shaped
    # line hides in the body and no later-only required name is present (a dropped v2.4 header must not
    # smear the leg into v2.2: refuse it by name, never mint).
    if any(l.startswith("#") for l in lines[1:]):
        raise ValueError(f"{scan}: process-scan header malformed: a header line in the body")
    later_only = {n for n, since in PINNED_LEG_FILES_SINCE.items()
                  if _version_key("v2.2") < _version_key(since)}
    present = {n for n in os.listdir(leg_dir) if os.path.isfile(os.path.join(leg_dir, n))}
    stray = sorted(later_only & present)
    if stray:
        scan_name = os.path.basename(scan)
        raise ValueError(f"{scan_name}: process-scan header missing but {stray[0]} present: not a v2.2 leg")
    return "v2.2"


def content_constraint(version, name):
    """The content kind for `(version, name)` — the ONE table beside `required_files()`.

    Raises `ValueError` for an unknown version or a name `required_files(version)` does not carry — the
    closed-table guarantee: a NEW required name lands in `required_files` and is missing here, and the
    matching test (the key-set equality) is red until it is added.
    """
    if version not in _KNOWN_CORPUS_VERSIONS:
        raise ValueError(f"content_constraint: unknown capture-contract version {version!r}")
    if name not in required_files(version):
        raise ValueError(f"content_constraint: {name} is not a required file of {version}")
    return _CONTENT_CONSTRAINTS[(version, name)]


def validate_artifact(leg_dir, name, version):
    """Validate ONE required artifact's content against its constraint. Returns None or raises a
    `ConstraintFailure` carrying the exact `<name>: <reason>` line (the named-refusal contract).

    `leg_dir` is used only to read the file's bytes; the CALLER prefixes the leg name (the tools print
    `{leg}: {exc}`), so this raises `<name> is empty`, `<name> is a completion marker ...`, or
    `<name> is not valid <kind>: <reason>` — never a raw traceback.
    """
    kind = content_constraint(version, name)
    path = os.path.join(leg_dir, name)
    size = os.path.getsize(path)

    if kind == "empty-marker":
        if size != 0:
            raise ConstraintFailure(
                f"{name} is a completion marker and must be empty ({size} bytes)")
        return
    if kind == "utf8-text-maybe-empty":
        # empty is VALID for this kind (v2.2 scan artifacts may carry no rows); only non-empty bytes
        # must be valid UTF-8
        if size == 0:
            return
        with open(path, "rb") as fh:
            data = fh.read()
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ConstraintFailure(f"{name} is not valid {kind}: invalid UTF-8: {exc}")
        return
    if size == 0:
        raise ConstraintFailure(f"{name} is empty")

    with open(path, "rb") as fh:
        data = fh.read()

    def _utf8(b):
        try:
            return b.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ConstraintFailure(f"{name} is not valid {kind}: invalid UTF-8: {exc}")

    if kind == "text-nonempty":
        _utf8(data)
        return
    if kind == "int-exit-code":
        try:
            int(_utf8(data).strip())
        except ValueError:
            raise ConstraintFailure(f"{name} is not valid {kind}: not an integer")
        return
    if kind == "json-object":
        try:
            obj = json.loads(_utf8(data))
        except ValueError as exc:
            raise ConstraintFailure(f"{name} is not valid {kind}: {exc}")
        if not isinstance(obj, dict):
            raise ConstraintFailure(f"{name} is not valid {kind}: not a JSON object ({type(obj).__name__})")
        return
    if kind == "json-array":
        try:
            obj = json.loads(_utf8(data))
        except ValueError as exc:
            raise ConstraintFailure(f"{name} is not valid {kind}: {exc}")
        if not isinstance(obj, list):
            raise ConstraintFailure(f"{name} is not valid {kind}: not a JSON array ({type(obj).__name__})")
        return
    if kind == "jsonl-nonempty":
        for lineno, line in enumerate(_utf8(data).splitlines(), 1):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except ValueError as exc:
                raise ConstraintFailure(f"{name} is not valid {kind}: line {lineno}: {exc}")
        return
    if kind == "gzip-text-nonempty":
        try:
            body = gzip.decompress(data)
        except (OSError, EOFError) as exc:
            raise ConstraintFailure(f"{name} is not valid {kind}: bad gzip: {exc}")
        if not body:
            raise ConstraintFailure(f"{name} is not valid {kind}: empty decompressed body")
        try:
            body.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ConstraintFailure(f"{name} is not valid {kind}: invalid UTF-8: {exc}")
        return
    if kind == "scan-headed":
        lines = _utf8(data).splitlines()
        if not lines:
            raise ConstraintFailure(f"{name} has no enumeration header")
        strict = _SCAN_HEADER_FULL_RE.get(version)
        if strict is None or not strict.match(lines[0]):
            raise ConstraintFailure(f"{name} has unrecognised header: {lines[0][:90]!r}")
        for lineno, line in enumerate(lines[1:], 2):
            if line.startswith("#"):
                raise ConstraintFailure(
                    f"{name} process-scan header malformed: a header line in the body")
            parts = line.split(None, 3)
            if len(parts) < 4:
                raise ConstraintFailure(
                    f"{name} is not valid {kind}: body line {lineno} unparsable: {line!r}")
            try:
                int(parts[0]); int(parts[1]); int(parts[2])
            except ValueError:
                raise ConstraintFailure(
                    f"{name} is not valid {kind}: body line {lineno} unparsable: {line!r}")
        return
    raise ConstraintFailure(f"{name} is not valid: unknown constraint kind {kind!r}")


class ConstraintFailure(ValueError):
    """A named content refusal from validate_artifact; subclasses ValueError so callers see both."""


def is_pinned_argv(argv):
    """Is this process row one of the proof's OWN pinned processes, judged by its ENTRY POINT?

    ONE function for three callers that must agree: the producer's scan heredoc (tools/pc/pc_post.sh), the
    checker's body predicates, and the tests. It was written three times before; a hand copy is AF-AP-42.

    The three shapes a captured leg's process-scan-after.txt actually carries (real corpus, run-1):
        <buzz-acp> --relay-url ...                      argv[0] IS the pinned binary
        python3 <frame_tee.py>                          an interpreter running the pinned tee
        <venv>/python3 <hermes-acp>                     an interpreter running the pinned agent
    VERIFY-P5a F4: `argv[1] in PINNED_SCRIPTS` alone counted ANY command whose first operand is a pinned
    script — `/usr/bin/cat <tee>`, `vim <tee>`, `sha256sum <agent>` — reproduced with a real process, which
    then entered the leg's evidence body and failed the leg at the checker for a bystander. The interpreter
    arm therefore requires argv[0]'s basename to start with `python`.

    DOCUMENTED LIMIT (F5): a pinned BINARY invoked through another path to the same file (a symlink, a bind
    mount) is NOT counted, and is dropped from the body. Resolving argv[0] through /proc/<pid>/exe would close
    it for the producer only: the checker computes this same predicate over a COLLECTED text file where no
    /proc exists, and two venues computing two different predicates over one body is precisely the drift this
    function removes. The escape is bounded elsewhere: pc_launch.alive_pinned_buzz reads /proc/<pid>/exe and
    refuses to launch while a pinned buzz-acp is alive, so it needs the pidfile to be gone as well.
    """
    if not argv:
        return False
    if argv[0] == PINNED_BUZZ_ACP_EXE_REALPATH:
        return True
    return (len(argv) > 1
            and argv[1] in (PINNED_TEE_PATH, PINNED_AGENT_REALPATH)
            and os.path.basename(argv[0]).startswith("python"))


def hermes_home():
    """The Hermes home a LAUNCH runs against: PINNED_HERMES_HOME, or $S0_01_HERMES_HOME when another proof
    declares its own tree (S0-03 leg B — tasks/briefs/s0-03-support/O1-report.md section 6).

    The override deliberately does NOT move PINNED_HERMES_HOME itself. check_acp_conformance.py:468 and
    negative_contract.py:210 compare a CAPTURED leg's env.json against that constant, and an environment
    variable that moved it would let a leg captured under a foreign Hermes home pass its own oracle — an
    env-var config channel opening a hole in the gate spine. Only the launcher reads this, once, at startup,
    and threads the value explicitly.

    Validated: an override that does not name an existing directory exits 64 rather than launching a capture
    against a tree that is not there.
    """
    override = os.environ.get("S0_01_HERMES_HOME")
    if override is None:
        return PINNED_HERMES_HOME
    if not os.path.isdir(override):
        print(f"pins: S0_01_HERMES_HOME={override!r} is not an existing directory", file=sys.stderr)
        raise SystemExit(64)
    return override
