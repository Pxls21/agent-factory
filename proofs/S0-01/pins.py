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

# --- source immutability: recursive sha256 manifests of the three pinned trees ---
MANIFEST_TREES = ("hermes-agent", "buzz", "acp")  # header order in the manifest body
PINNED_BASELINE_DIGESTS = {
    "hermes-agent": "1e11d5dcdf3c38ff26a972c839547c532c91dd2ec942324e75bd310def2b87cb",
    "buzz": "f00e3463f75d6b0716a3f89913de1b06db37af7c8d3433330590022e94a7d987",
    "acp": "5579023c865ec10ecc026ddaa0947f9a2104ad0e2e92ed870989a7d5d66c80d8",
}
PINNED_BASELINE_FILE_COUNTS = {"hermes-agent": 11340, "buzz": 11612, "acp": 269}
PINNED_BASELINE_GZ_SHA256 = "a3f5732eceab3da83382a75ac1e78a02c431727f0d48d862428ccd08f48ead68"

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
