"""S0-01 pinned constants — the ONE place the proof's expected values live.

Imported by check_acp_conformance.py (positive legs) and check_initialize.py (negative leg).
Every value here is an EXACT expectation: the checker compares with ==, never `in`/startswith.
Values were read from the PC on 2026-09-05 (sha256sum / readlink -f / the baseline manifest
summary); the baseline body itself is committed at
proofs/S0-01/evidence/golden/manifests/manifest-baseline.txt.gz and the digests below are
re-derived from it by the checker (a pin is integrity, the re-derivation is correctness).
"""
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
PINNED_BASELINE_DIGESTS = {
    "hermes-agent": "6087cfeffd1026f3f26752bd32eb8943bd63c733b3429fadbb1a1b9f31f4d777",
    "buzz": "a5614f3c1d904c145c26d5a49e670fa49fc9075b9e0e39ccbed93bc2771e1e95",
    "acp": "0039fb357d4170d9e67313210b8933726a6b82ea2f2882e17164c08c41603122",
    "venv-hermes": "c181f47c563cdc6edfbe4550352ac0cfc7221760e2ddf0396d6efed2a39ee523",
}
PINNED_BASELINE_FILE_COUNTS = {"hermes-agent": 11340, "buzz": 11665, "acp": 270, "venv-hermes": 10653}  # entries incl. symlinks (v2.2)
PINNED_BASELINE_GZ_SHA256 = "e8fd76015376f2db4ffca2c4f0fd632743df6ce6655df6986729122e9214381d"

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
PINNED_GOLDEN_SHA256 = None

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

      * line 1 beginning `#` CLAIMS to be an enumeration header: it must name a version this pin knows, else
        ValueError. A leg from a NEWER contract graded by an OLDER required set would pass while missing
        artefacts the newer contract requires, so this case is never defaulted.
      * anything else is the pre-header shape -> "v2.2". That includes an EMPTY scan file: the corpus's
        shutdown leg carries a 0-byte process-scan-after.txt (measured 2026-09-08), because the v2.2 scan on a
        clean shutdown wrote neither header nor rows.
      * no scan file at all -> "v2.2" as well: process-scan-after.txt is itself `required`, so the caller's own
        completeness gate names it, which is a better diagnosis than a version error.
    """
    scan = os.path.join(leg_dir, "process-scan-after.txt")
    if not os.path.isfile(scan):
        return "v2.2"
    with open(scan, encoding="utf-8", errors="replace") as fh:
        first = fh.readline().rstrip("\n")
    if not first.startswith("#"):
        return "v2.2"
    m = _SCAN_HEADER_VERSION_RE.match(first)
    if m is None or m.group(1) not in PINNED_SCAN_VERSIONS:
        raise ValueError(f"{scan}: unrecognised process-scan header version: {first[:90]!r}")
    return m.group(1)


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
