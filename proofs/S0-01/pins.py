"""S0-01 pinned constants — the ONE place the proof's expected values live.

Imported by check_acp_conformance.py (positive legs) and check_initialize.py (negative leg).
Every value here is an EXACT expectation: the checker compares with ==, never `in`/startswith.
Values were read from the PC on 2026-09-05 (sha256sum / readlink -f / the baseline manifest
summary); the baseline body itself is committed at
proofs/S0-01/evidence/golden/manifests/manifest-baseline.txt.gz and the digests below are
re-derived from it by the checker (a pin is integrity, the re-derivation is correctness).
"""

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
