#!/usr/bin/env python3
"""S0-03 Hermes -> OmniRoute live round trip — the identity-asserting checker.

Grades an evidence bundle captured on the PC by `tools/pc/run_s0_03_legs.sh` against the three
seed assertions (`seeds/seed-stage0-v1.yaml:382-405`):

  A1  a `/v1/responses` request through REAL OmniRoute streams text and completes a REAL Hermes
      tool-call round trip
      -> conjunct (i) over `direct/direct.json` (leg A) and conjunct (iv) over
         `hermes/timeline.jsonl` (leg B, the S0-01 capture path).
  A2  the pass asserts UPSTREAM MODEL IDENTITY (response model id + a non-stub fingerprint),
      never a bare 200
      -> conjuncts (ii) and (iii), the second over an INDEPENDENT instrument.
  A3  Hermes holds no upstream provider key, and OmniRoute failure does not trigger direct
      fallback
      -> conjunct (vi) (deny-by-default env allowlist) and the credential-absent kill switch.

WHY CONJUNCT (iii) IS THE LOAD-BEARING IDENTITY ASSERTION, AND (ii) ALONE IS NOT
-------------------------------------------------------------------------------
Read from the pinned OmniRoute source (`488f57e9`, READ-ONLY at
/home/user/nerdherderdani/OmniRoute):

  * By DEFAULT the `/v1/responses` response `model` field carries the UPSTREAM-RESOLVED model id.
    The translator copies it off the upstream chunk —
    `open-sse/translator/response/openai-responses.ts:199-200` sets `state.model` from
    `chunk.model`, and `:217` / `:229` stamp it into the `response.created` /
    `response.in_progress` payloads.
  * BUT that field is REWRITTEN to the CLIENT-REQUESTED id whenever any of three conditions
    holds (`open-sse/handlers/chatCore.ts:1022-1026`): the global `echoRequestedModelName`
    setting is on (default off), OR the caller looks like the Codex CLI, OR it looks like Claude
    Code. The Codex test is header-only —
    `open-sse/config/codexIdentity.ts:537-538` returns true when `originator` OR `user-agent`
    starts with "codex" — so it is under the CALLER's control, not the route's.

Consequence: if the echo fires, `response.model` is a MIRROR of the request and conjunct (ii)
degenerates into a tautology that a stub route would also satisfy. That is precisely the
stub-drift hollow green the council named (COUNCIL-VERDICT §Socrates). The independent
instrument is therefore REQUIRED, and it is conjunct (iii): OmniRoute's own `call_logs` row for
each request, which records `provider` (the provider CONNECTION that served it), `model` (the
resolved model) and `requested_model` (what the client asked for) as separate columns
(`src/lib/usage/callLogs.ts:564-572`). A stub route is visible there and nowhere in the response
body. The two legs' probes are also built NOT to send a Codex-shaped `originator`/`user-agent`
(see tools/pc/direct_responses_probe.py), so the default upstream-id behaviour is the one under
test — but the checker does not depend on that holding.

WHAT THIS CHECKER CANNOT SEE, STATED PLAINLY
--------------------------------------------
  * The value of OmniRoute's global `echoRequestedModelName` setting. If it is ON, conjunct (ii)
    compares the requested id with itself. (iii) still discriminates.
  * Whether the network could have reached a provider directly. S0-05 owns the network-level
    egress proof; this proof asserts only the ENV precondition (no upstream key to fall back to)
    plus the observed failure behaviour in the credential-absent leg.
  * Anything about a leg that was never captured — see the DEFERRAL RULE below.

BUNDLE LAYOUT (a bundle root; the PC runner writes the positive bundle at `evidence/` and the
negative bundle at `evidence/credential-absent/`, which has this same internal shape):

    <evidence-root>/
      direct/direct.json          leg A: the /v1/responses record (events verbatim)
      hermes/timeline.jsonl       leg B: the ACP timeline written by the S0-01 tee
      hermes/hermes-env-names.json   env NAMES only for the hermes-acp process (never values)
      hermes/profile.yaml         the proof-owned provider profile as launched, key-free
      hermes/leg.json             leg B's nonce2 + prompt
      omniroute-requests.json     the correlation instrument: one call_logs row per request

DEFERRAL RULE: exit 2 iff the evidence root is absent or carries neither leg directory. Once
either leg directory exists, EVERY absence of a required file is a Failure naming the file
(AF-AP-40) — never a deferral.

Exit codes: 0 PASS / 1 `failure_reason: <reason>` / 2 `deferred: <reason>` / 64 usage error.

Usage: check_omniroute_roundtrip.py --route-id ID --expected-model-id ID
                                    --stub-route ID [--stub-route ID ...] <evidence-root>
"""
from __future__ import annotations

import importlib.util
import json
import re
import stat as _stat
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --- the S0-01 timeline reader, imported (never copied) --------------------------------------
# Item: "parse the timeline with S0-01's reader by IMPORT, never a copy". `_load_timeline_raw`
# already applies the S_ISREG guard and rejects NaN/Infinity; reimplementing it here would be a
# MIRROR of the code under test rather than a use of it.
_S0_01_CHECKER = HERE.parent / "S0-01" / "check_acp_conformance.py"


_S0_01_MODULE_NAME = "s0_01_check_acp_conformance"


def _load_s0_01_module():
    cached = sys.modules.get(_S0_01_MODULE_NAME)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(_S0_01_MODULE_NAME, _S0_01_CHECKER)
    if spec is None or spec.loader is None:  # pragma: no cover - packaging accident only
        raise Failure("bundle: cannot import the S0-01 timeline reader")
    module = importlib.util.module_from_spec(spec)
    # Registered BEFORE exec so the module is importable by name: without this the functions it
    # defines have no resolvable module and `inspect.getmodule` returns None, which would make
    # "this is S0-01's reader, not a copy of it" untestable by identity.
    sys.modules[_S0_01_MODULE_NAME] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(_S0_01_MODULE_NAME, None)
        raise
    return module


# --- the ONE reason table ---------------------------------------------------------------------
# Values are format TEMPLATES; every non-usage exit renders one through `_reason()`. The rendered
# string is what the spec pins and what the tests assert, so the canonical contract is exactly as
# strong as the strongest test of the same claim (AF-AP-29).
REASONS = {
    # The seed's kill switch (`seeds/seed-stage0-v1.yaml:400`) — EXACT, no placeholder.
    "credential_absent": "blocked: credential_absent",
    "direct_stream": "direct: {}",
    "identity_model": "identity: response model {!r} != declared upstream model {!r}",
    "identity_route": "identity: request routed to the sanctioned stub route {!r}, not an upstream model",
    "roundtrip": "roundtrip: {}",
    "transport": "transport: profile api_mode {!r} != 'codex_responses' (ADR 0002)",
    "env_provider_key": "env: upstream provider key {} present in the Hermes environ",
}

# Deny-by-default (AF-AP-23): a CLOSED EXACT allow-list, never a prefix and never a blacklist.
# Every environment NAME that looks like a credential must be an EXACT member of this set.
ENV_CREDENTIAL_ALLOWLIST = frozenset({"OMNIROUTE_API_KEY"})

# The screen is SEGMENT-based, not an anchored suffix. An anchored `(_API_KEY|_TOKEN|_SECRET|
# _KEY)$` reads well and is wrong: `OMNIROUTE_API_KEY_2` does not end in any of those, so it is
# never screened at all and a second, unaudited credential rides in beside the allowed one.
# Splitting on `_` and testing each segment catches the `_2` suffix, `OPENAI_KEY_OLD`,
# `ANTHROPIC_TOKEN_BACKUP` and every other decoration of the same names, while leaving ordinary
# names alone (`KEYBOARD` is one segment and is not `KEY`; `HERMES_HOME` has no marker segment).
CREDENTIAL_SEGMENTS = frozenset({"KEY", "KEYS", "TOKEN", "TOKENS", "SECRET", "SECRETS",
                                 "PASSWORD", "PASSWD", "CREDENTIAL", "CREDENTIALS", "APIKEY"})


def is_credential_name(name: str) -> bool:
    return any(segment in CREDENTIAL_SEGMENTS for segment in name.upper().split("_"))

# Domain floors: a nonce that is not a fresh 16-hex token cannot make the text assertions
# vacuous (an empty or one-character nonce is "in" every text).
NONCE_RE = re.compile(r"^[0-9a-f]{16}$")

REQUIRED_API_MODE = "codex_responses"
COMPRESSION_REQUEST_HEADER = "x-omniroute-compression"
COMPRESSION_OFF = "off"


class Failure(Exception):
    """A graded failure: its str() is the exact reason line the runner records."""


class Deferred(Exception):
    """Nothing was captured — the venue could not run the legs."""


def _reason(key: str, *args) -> str:
    return REASONS[key].format(*args)


def _fail(key: str, *args):
    raise Failure(_reason(key, *args))


# --- bounded, typed reads ---------------------------------------------------------------------
def _require_file(path: Path, name: str) -> Path:
    """Reject a non-regular file (FIFO, directory, socket, device) with a named reason BEFORE any
    read: opening a FIFO blocks forever, so existence alone is not enough."""
    if not path.exists():
        raise Failure(f"bundle: {name} absent")
    if not _stat.S_ISREG(path.lstat().st_mode):
        raise Failure(f"bundle: {name} is not a regular file")
    return path


def _read_json(path: Path, name: str):
    _require_file(path, name)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise Failure(f"bundle: {name} is not valid JSON ({exc.__class__.__name__})")


def _read_yaml(path: Path, name: str):
    _require_file(path, name)
    import yaml

    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        raise Failure(f"bundle: {name} is not valid YAML ({exc.__class__.__name__})")


def _obj(value, name: str) -> dict:
    if not isinstance(value, dict):
        raise Failure(f"bundle: {name} is not a JSON object")
    return value


def _str(value, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise Failure(f"bundle: {name} is not a non-empty string")
    return value


# --- the declared inputs, carried by the spec's leg `cmd` --------------------------------------
# `proofs/schemas/spec.schema.json` sets `additionalProperties: false` over exactly
# {proof_id, legs}, so a proof's declarations cannot live in a sibling key of spec.json. They ride
# the leg's `cmd` instead: the spec still CARRIES them (the runner passes them verbatim, the
# validator attests the spec, and the tests read the stub list back out of spec.json rather than
# out of a literal in this file).
USAGE = ("usage: check_omniroute_roundtrip.py --route-id ID --expected-model-id ID "
         "--stub-route ID [--stub-route ID ...] <evidence-root>")


class Usage(Exception):
    """Malformed argv — exit 64, distinct from the exit 2 that means 'nothing was captured'."""


def parse_args(argv) -> dict:
    route_id = expected_model_id = None
    stub_routes: list = []
    positional: list = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--route-id", "--expected-model-id", "--stub-route"):
            if i + 1 >= len(argv):
                raise Usage(f"{arg} needs a value")
            value = argv[i + 1].strip()
            if not value:
                raise Usage(f"{arg} needs a non-empty value")
            if arg == "--route-id":
                route_id = value
            elif arg == "--expected-model-id":
                expected_model_id = value
            else:
                stub_routes.append(value)
            i += 2
            continue
        if arg.startswith("--"):
            raise Usage(f"unknown option {arg}")
        positional.append(arg)
        i += 1
    if len(positional) != 1:
        raise Usage(f"expected exactly 1 evidence root, got {len(positional)}")
    if not route_id or not expected_model_id or not stub_routes:
        raise Usage("--route-id, --expected-model-id and at least one --stub-route are required")
    return {
        "root": Path(positional[0]),
        "route_id": route_id,
        "expected_model_id": expected_model_id,
        "stub_routes": [s.lower() for s in stub_routes],
    }


def _is_stub(name: str, stub_routes) -> bool:
    """A provider-connection or model id is a stub when it equals a declared stub id, or when it
    is namespaced under one (`s0-01-scripted/s0-01-pong` under `s0-01-scripted`). Matching the
    NAMESPACE as well as the exact id closes the equivalent that an exact-only test would miss
    (AF-AP-30: fix the class, not the specimen)."""
    low = name.strip().lower()
    for stub in stub_routes:
        if low == stub or low.startswith(stub + "/"):
            return True
    return False


# --- the credential-absent kill switch (priority 0) -------------------------------------------
def check_credential_absent(bundle: dict):
    """The seed's kill switch: disable the credential -> RED `blocked: credential_absent`.

    Runs BEFORE every conjunct on purpose. The credential-absent leg necessarily fails conjunct
    (i) too (OmniRoute answers 401, so nothing streams); grading it as "no streamed answer" would
    report a SYMPTOM and lose the seed's pinned reason. Two independent signals, either of which
    is decisive:
      * the Hermes environ carries no OMNIROUTE_API_KEY (there is no credential to send), or
      * OmniRoute answered the direct leg 401 (the credential was refused at the gate:
        `src/server/authz/policies/clientApi.ts:77` / `:96`, both AUTH_002).
    """
    env = bundle.get("env_names")
    if env is not None and "OMNIROUTE_API_KEY" not in env:
        _fail("credential_absent")
    direct = bundle.get("direct")
    if direct is not None and direct.get("status") == 401:
        _fail("credential_absent")


# --- conjunct (i): a real streamed model answer -----------------------------------------------
def check_direct_stream(direct: dict):
    status = direct.get("status")
    if status != 200:
        _fail("direct_stream", f"status {status!r}, expected 200")

    nonce = _str(direct.get("nonce"), "direct.json nonce")
    if not NONCE_RE.match(nonce):
        _fail("direct_stream", f"nonce {nonce!r} is not a fresh 16-hex token")

    events = direct.get("events")
    if not isinstance(events, list) or not events:
        _fail("direct_stream", "no streamed events recorded")

    deltas = [e for e in events
              if isinstance(e, dict) and e.get("type") == "response.output_text.delta"]
    if not deltas:
        _fail("direct_stream", "no response.output_text.delta event")

    text = "".join(d.get("delta") for d in deltas if isinstance(d.get("delta"), str))
    if nonce not in text:
        _fail("direct_stream", f"nonce {nonce!r} absent from the streamed text")

    # The compression-off header must have been SENT (S0-04 owns whether it was HONOURED).
    sent = direct.get("request_headers_sent")
    if not isinstance(sent, dict):
        _fail("direct_stream", "request_headers_sent absent")
    value = None
    for key, val in sent.items():
        if isinstance(key, str) and key.lower() == COMPRESSION_REQUEST_HEADER:
            value = val
    if not isinstance(value, str) or value.strip().lower() != COMPRESSION_OFF:
        _fail("direct_stream", f"{COMPRESSION_REQUEST_HEADER} sent as {value!r}, expected 'off'")


# --- conjunct (ii): the response model id -----------------------------------------------------
def check_identity_model(direct: dict, spec: dict):
    model = _str(direct.get("model"), "direct.json model")
    if model != spec["expected_model_id"]:
        _fail("identity_model", model, spec["expected_model_id"])


# --- conjunct (iii): the independent request record -------------------------------------------
def check_identity_route(requests: dict, direct: dict, spec: dict):
    rows = requests.get("requests")
    if not isinstance(rows, list) or len(rows) < 2:
        raise Failure("bundle: omniroute-requests.json carries fewer than two request rows")

    legs = {}
    for i, row in enumerate(rows):
        row = _obj(row, f"omniroute-requests.json requests[{i}]")
        leg = _str(row.get("leg"), f"omniroute-requests.json requests[{i}].leg")
        legs[leg] = row
    for leg in ("direct", "hermes"):
        if leg not in legs:
            raise Failure(f"bundle: omniroute-requests.json has no row for the {leg} leg")

    models = set()
    for leg in ("direct", "hermes"):
        row = legs[leg]
        # Correlation first: a call_logs row for somebody else's request proves nothing about
        # ours. `requested_model` is the column that records what the CLIENT asked for
        # (`src/lib/usage/callLogs.ts:564-566`), so it is the one that binds the row to our route.
        requested = _str(row.get("requested_model"),
                         f"omniroute-requests.json {leg}.requested_model")
        if requested != spec["route_id"]:
            raise Failure(
                f"bundle: {leg} row requested_model {requested!r} != declared route "
                f"{spec['route_id']!r}"
            )
        provider = _str(row.get("provider"), f"omniroute-requests.json {leg}.provider")
        if _is_stub(provider, spec["stub_routes"]):
            _fail("identity_route", provider)
        model = _str(row.get("model"), f"omniroute-requests.json {leg}.model")
        if _is_stub(model, spec["stub_routes"]):
            _fail("identity_route", model)
        models.add(model)

    if len(models) != 1:
        raise Failure(
            "bundle: the two requests report different model ids " + repr(sorted(models))
        )
    recorded = models.pop()
    if recorded != direct.get("model"):
        raise Failure(
            f"bundle: call_logs model {recorded!r} != response model {direct.get('model')!r}"
        )
    return legs["direct"]["provider"]


# --- conjunct (iv): the Hermes tool-call round trip -------------------------------------------
def _updates(entries):
    """Yield every `session/update` payload in the agent->client direction."""
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("dir") != "a2c":
            continue
        frame = entry.get("frame")
        if not isinstance(frame, dict) or frame.get("method") != "session/update":
            continue
        params = frame.get("params")
        if not isinstance(params, dict):
            continue
        update = params.get("update")
        if isinstance(update, dict):
            yield update


def _agent_text(entries) -> str:
    parts = []
    for update in _updates(entries):
        if update.get("sessionUpdate") != "agent_message_chunk":
            continue
        content = update.get("content")
        if isinstance(content, dict) and isinstance(content.get("text"), str):
            parts.append(content["text"])
    return "".join(parts)


def check_roundtrip(entries, nonce2: str):
    """ACP shapes are read from the committed protocol schema
    (`proofs/S0-01/fixtures/acp-schema-v1.json`): `SessionUpdate` enumerates `tool_call` and
    `tool_call_update`, and `ToolCallStatus` enumerates pending/in_progress/completed/failed."""
    if not NONCE_RE.match(nonce2):
        _fail("roundtrip", f"nonce2 {nonce2!r} is not a fresh 16-hex token")

    prompts = [e for e in entries
               if isinstance(e, dict) and e.get("dir") == "c2a"
               and isinstance(e.get("frame"), dict)
               and e["frame"].get("method") == "session/prompt"]
    if len(prompts) != 1:
        _fail("roundtrip", f"{len(prompts)} session/prompt turns, expected exactly 1")

    # Structural bind: the nonce the checker looks for in the answer is the one the PROMPT asked
    # for, so a bundle cannot pass by carrying an answer to a different question.
    if nonce2 not in json.dumps(prompts[0]["frame"], ensure_ascii=False):
        _fail("roundtrip", f"nonce2 {nonce2!r} absent from the prompt frame")

    starts = [u for u in _updates(entries) if u.get("sessionUpdate") == "tool_call"]
    if not starts:
        _fail("roundtrip", "no tool_call update in the timeline")

    started_ids = {u.get("toolCallId") for u in starts if isinstance(u.get("toolCallId"), str)}
    completed = {
        u.get("toolCallId")
        for u in _updates(entries)
        if u.get("sessionUpdate") in ("tool_call", "tool_call_update")
        and u.get("status") == "completed"
        and isinstance(u.get("toolCallId"), str)
    }
    if not (started_ids & completed):
        _fail("roundtrip", "no tool_call reached status 'completed'")

    text = _agent_text(entries)
    if nonce2 not in text:
        _fail("roundtrip", f"nonce2 {nonce2!r} absent from the final agent text")


# --- conjunct (v): the transport the ADR pins -------------------------------------------------
def _provider_block(profile) -> dict:
    providers = _obj(profile, "profile.yaml").get("providers")
    providers = _obj(providers, "profile.yaml providers")
    if len(providers) != 1:
        raise Failure(
            f"bundle: profile.yaml declares {len(providers)} providers, expected exactly 1"
        )
    (_name, block), = providers.items()
    return _obj(block, "profile.yaml provider block")


def check_transport(profile):
    block = _provider_block(profile)
    api_mode = block.get("api_mode")
    if api_mode != REQUIRED_API_MODE:
        _fail("transport", api_mode)

    headers = block.get("extra_headers")
    if not isinstance(headers, dict):
        raise Failure("bundle: profile.yaml provider block has no extra_headers mapping")
    value = None
    for key, val in headers.items():
        if isinstance(key, str) and key.lower() == COMPRESSION_REQUEST_HEADER:
            value = val
    if not isinstance(value, str) or value.strip().lower() != COMPRESSION_OFF:
        raise Failure(
            f"bundle: profile.yaml {COMPRESSION_REQUEST_HEADER} is {value!r}, expected 'off'"
        )

    # The launched profile must never carry a key VALUE. Only the env NAME may appear.
    if "api_key" in block:
        raise Failure("bundle: profile.yaml carries an inline api_key")
    if block.get("key_env") != "OMNIROUTE_API_KEY":
        raise Failure(
            f"bundle: profile.yaml key_env is {block.get('key_env')!r}, expected 'OMNIROUTE_API_KEY'"
        )


# --- conjunct (vi): the deny-by-default env allowlist ------------------------------------------
def check_env(env_names):
    """AF-AP-23: an allow-list over the WHOLE name domain, not a blacklist of known providers and
    not a prefix. Every name whose SUFFIX marks it a credential must be an exact member of
    ENV_CREDENTIAL_ALLOWLIST; `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` and the one nobody listed all
    fail the same way."""
    offenders = sorted(
        name for name in env_names
        if is_credential_name(name) and name not in ENV_CREDENTIAL_ALLOWLIST
    )
    if offenders:
        _fail("env_provider_key", offenders[0])


# --- bundle assembly + the graded sequence -----------------------------------------------------
def load_bundle(root: Path) -> dict:
    direct_dir = root / "direct"
    hermes_dir = root / "hermes"
    if not root.is_dir() or not (direct_dir.is_dir() or hermes_dir.is_dir()):
        raise Deferred("S0-03 evidence not captured")

    direct = _obj(_read_json(direct_dir / "direct.json", "direct/direct.json"),
                  "direct/direct.json")
    env_record = _obj(
        _read_json(hermes_dir / "hermes-env-names.json", "hermes/hermes-env-names.json"),
        "hermes/hermes-env-names.json",
    )
    names = env_record.get("names")
    if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
        raise Failure("bundle: hermes/hermes-env-names.json names is not a list of strings")
    leg = _obj(_read_json(hermes_dir / "leg.json", "hermes/leg.json"), "hermes/leg.json")
    profile = _read_yaml(hermes_dir / "profile.yaml", "hermes/profile.yaml")

    s0_01 = _load_s0_01_module()
    _require_file(hermes_dir / "timeline.jsonl", "hermes/timeline.jsonl")
    try:
        entries = s0_01._load_timeline_raw(hermes_dir, "hermes")
    except s0_01.Failure as exc:
        raise Failure(f"bundle: {exc}")

    requests = _obj(_read_json(root / "omniroute-requests.json", "omniroute-requests.json"),
                    "omniroute-requests.json")
    return {
        "direct": direct,
        "env_names": names,
        "leg": leg,
        "profile": profile,
        "entries": entries,
        "requests": requests,
    }


def check_bundle(root: Path, spec: dict) -> str:
    bundle = load_bundle(root)

    # Priority 0, then conjuncts (i)..(vi) in the brief's order. First failure wins.
    check_credential_absent(bundle)
    check_direct_stream(bundle["direct"])
    check_identity_model(bundle["direct"], spec)
    provider = check_identity_route(bundle["requests"], bundle["direct"], spec)
    check_roundtrip(bundle["entries"], _str(bundle["leg"].get("nonce2"), "hermes/leg.json nonce2"))
    check_transport(bundle["profile"])
    check_env(bundle["env_names"])

    return (
        f"PASS: S0-03 omniroute-roundtrip - model {bundle['direct']['model']} "
        f"via {provider}, tool-call round trip, env clean"
    )


def main(argv) -> int:
    try:
        spec = parse_args(argv[1:])
    except Usage as exc:
        print(f"{USAGE}\nerror: {exc}", file=sys.stderr)
        return 64
    try:
        print(check_bundle(spec["root"], spec))
        return 0
    except Deferred as exc:
        print(f"deferred: {exc}")
        return 2
    except Failure as exc:
        print(f"failure_reason: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
