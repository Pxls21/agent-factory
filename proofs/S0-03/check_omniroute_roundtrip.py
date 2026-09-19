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
negative bundle at `evidence/credential-absent/`):

    <evidence-root>/
      direct/direct.json          leg A: the /v1/responses record (events verbatim), including
                                  whether a credential was presented and the header NAMES sent
      hermes/timeline.jsonl       leg B: the ACP timeline written by the S0-01 tee
      hermes/hermes-env-names.json   env NAMES only for the hermes-acp process (never values),
                                  plus the pid, its /proc exe and the tee's agent_realpath
      hermes/profile.yaml         the profile the launcher LOADED (a per-leg copy of the
                                  proof-owned template carrying this leg's session tag), key-free
      hermes/leg.json             leg B's nonce2, prompt and the CLOSED window the runner
                                  recorded at both ends of the turn
      omniroute-requests.json     the correlation instrument: OmniRoute's own call_logs rows — the
                                  direct leg's row selected by the fresh nonce OmniRoute recorded in
                                  its artifact requestBody (exported as `recorded_input`), and every
                                  route row inside the hermes leg's window (session_tag == nonce2)

The negative bundle is DIRECT-LEG ONLY, and that is a producer fact, not an omission: the pinned
S0-01 launcher reads OMNIROUTE_API_KEY from the owner's env file, so a key-free Hermes leg cannot
be captured through it (the bundle's own NOT-CAPTURED.md names the seam that would be needed).
The credential verdicts are therefore graded on the direct leg's own evidence, BEFORE the hermes
half is required.

DEFERRAL RULE: exit 2 iff the evidence root is absent or carries neither leg directory. Once
either leg directory exists, EVERY absence of a required file is a Failure naming the file
(AF-AP-40) — never a deferral.

Exit codes: 0 PASS / 1 `failure_reason: <reason>` / 2 `deferred: <reason>` / 64 usage error.

Usage: check_omniroute_roundtrip.py --route-id ID --expected-model-id ID
                                    --stub-route ID [--stub-route ID ...] <evidence-root>
"""
from __future__ import annotations

import datetime as _dt
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
    # The seed's OTHER credential verdict (`:400-402`): "credential_rejected maps to proof-RED,
    # never to blocked". A key that was PRESENTED and refused is a red proof, not a deferral.
    "credential_rejected": "credential_rejected: OmniRoute refused the presented key (HTTP {})",
    "direct_stream": "direct: {}",
    "identity_model": "identity: response model {!r} != declared upstream model {!r}",
    "identity_route": "identity: request routed to the sanctioned stub route {!r}, not an upstream model",
    "identity_direct_nonce": "identity: direct leg nonce {!r} is not in OmniRoute's recorded request for the row",
    "identity_session_tag": "identity: hermes leg row session_tag {!r} != the leg's nonce2 {!r}",
    "identity_status": "identity: {} leg row status {!r}, expected 200",
    "identity_no_hermes_rows": "identity: 0 call_logs rows for the hermes leg's session_tag — unattributable",
    "roundtrip": "roundtrip: {}",
    "transport": "transport: profile api_mode {!r} is not in the permitted set",
    "transport_method": "transport: {} leg row method {!r}, expected 'POST'",
    "transport_path": "transport: {} leg row path {!r} is not a permitted transport path",
    "env_provider_key": "env: upstream provider key {} present in the Hermes environ",
    "env_process": "env: the environ record's {} is {!r}, not the pinned Hermes agent {!r}",
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
# PAT / AUTH / PW / BEARER are real credential-name shapes with no KEY|TOKEN|SECRET segment —
# `GITHUB_PAT`, `ANTHROPIC_AUTH` and `DB_PW` all rode straight through the earlier set
# (VERIFY-O1 F-12, mutants V7a-c).
# AUTHORIZATION (and Proxy-Authorization's second segment) is a header-IDENTITY credential: the
# AUTH segment above is a DIFFERENT token, so the split never matched the whole header name. An
# `Authorization: Token <x>` or opaque value therefore slipped the value-prefix screen entirely
# (VERIFY-O3 blocker, O4). By segment, the header is now flagged by NAME regardless of scheme.
# SESSION is deliberately NOT here, and that is a decision, not an omission: the launched agent's
# environment key set is PINNED at `proofs/S0-01/pins.py` PINNED_ENV_KEYS and contains
# `BUZZ_ACP_SESSION_POLICY`, so a SESSION segment would make conjunct (vi) impossible for any real
# capture to satisfy — an assertion no live leg can pass is not a stronger gate, it is a broken
# one. The residual the segment would have caught (`AWS_SESSION_TOKEN`) is already caught by TOKEN.
CREDENTIAL_SEGMENTS = frozenset({"KEY", "KEYS", "TOKEN", "TOKENS", "SECRET", "SECRETS",
                                 "PASSWORD", "PASSWD", "CREDENTIAL", "CREDENTIALS", "APIKEY",
                                 "PAT", "AUTH", "PW", "BEARER", "AUTHORIZATION"})


def is_credential_name(name: str) -> bool:
    """True when at least one segment of the name marks it a credential.

    Segments split on BOTH separators: environment names use `_` (`OPENAI_API_KEY`) and HTTP
    header names use `-` (`X-Api-Key`), and the same screen grades both — the provider block's
    `extra_headers` is exactly where Hermes documents custom auth.

    This is a screen over the WHOLE name domain followed by an exact allow-list, not a blacklist
    of known providers: `FOO_API_KEY`, `OMNIROUTE_API_KEY_2` and the provider nobody listed all
    fail the same way. The residual class it does NOT catch is a credential whose name carries no
    marker segment at all (`GH_ACCESS`, `NPM_RC`) — an environ has hundreds of benign names and
    screening every one of them is not a decidable test, so the boundary is stated here rather
    than implied by a docstring that claims more than the code does (F-12)."""
    return any(segment in CREDENTIAL_SEGMENTS
               for segment in re.split(r"[-_]", name.upper()))

# Domain floors: a nonce that is not a fresh 16-hex token cannot make the text assertions
# vacuous (an empty or one-character nonce is "in" every text).
NONCE_RE = re.compile(r"^[0-9a-f]{16}$")

PERMITTED_API_MODES = frozenset({"chat_completions", "codex_responses"})
PERMITTED_TRANSPORT_PATHS = ("/v1/responses", "/v1/chat/completions")
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


def _reject_constant(token: str):
    """`json.loads` accepts NaN/Infinity/-Infinity by default. A NaN in an evidence file is the
    fail-open wormhole class the incident log records twice: every comparison against it is
    False, so a guard written as `if value != expected: fail` passes. S0-01's timeline reader
    already rejects them; this is the same discipline on the S0-03 reads (F-17)."""
    raise ValueError(f"{token} is not permitted in evidence JSON")


def _read_json(path: Path, name: str):
    _require_file(path, name)
    try:
        return json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)
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


# --- the credential verdicts (priority 0) ------------------------------------------------------
REJECTING_STATUSES = (401, 403)


def _authorization_presented(direct: dict) -> bool:
    """Did THIS request carry a credential? The probe records the header NAMES it sent, with the
    Authorization VALUE redacted at the point of the write (`tools/pc/direct_responses_probe.py`
    build_headers + the headers_sent map), so presence is decidable from the artifact without any
    secret ever entering it. A missing or malformed record is a bundle failure, never a silent
    "no" — that would grade a broken capture as the seed's blocked outcome."""
    sent = direct.get("request_headers_sent")
    if not isinstance(sent, dict):
        raise Failure("bundle: direct/direct.json request_headers_sent absent")
    return any(isinstance(k, str) and k.lower() == "authorization" for k in sent)


def check_credential_at_the_gate(direct: dict):
    """The seed's two credential verdicts, decided on the DIRECT leg's own evidence.

    Runs BEFORE every conjunct on purpose. A refused or absent credential necessarily fails
    conjunct (i) too (OmniRoute answers 401, so nothing streams); grading that as "no streamed
    answer" would report a SYMPTOM and lose the seed's pinned reason.

    The split is the seed's (`seeds/seed-stage0-v1.yaml:400-402`: "credential_rejected maps to
    proof-RED, never to blocked") and it is decided from the request itself, not from a different
    artifact about a different process:
      * 401/403 with NO Authorization header sent -> the credential was never presented ->
        `blocked: credential_absent`. This is what `direct_responses_probe.py --no-credential`
        produces, and OmniRoute's no-bearer path answers it (AUTH_002 "Authentication required",
        `src/server/authz/policies/clientApi.ts:77`).
      * 401/403 WITH one -> the key was presented and refused -> RED `credential_rejected`
        (`clientApi.ts:96`, AUTH_002 "Invalid API key"). The earlier version graded this
        `blocked: credential_absent`, i.e. a rejected credential became a deferral (F-5).
    """
    status = direct.get("status")
    if status in REJECTING_STATUSES:
        if _authorization_presented(direct):
            _fail("credential_rejected", status)
        _fail("credential_absent")


def check_credential_in_the_environ(env_names):
    """The second, independent half of the kill switch: Hermes had nothing to send. Kept separate
    from the gate check because it is graded on a different artifact and can only be read once the
    hermes half of the bundle exists — the negative bundle a real `--no-credential` leg produces
    has no hermes half at all (its NOT-CAPTURED.md says why), and it must still grade as the
    seed's kill switch rather than as a short bundle."""
    if env_names is not None and "OMNIROUTE_API_KEY" not in env_names:
        _fail("credential_absent")


# --- conjunct (i): a real streamed model answer -----------------------------------------------
def check_direct_stream(direct: dict):
    status = direct.get("status")
    if status != 200:
        _fail("direct_stream", f"status {status!r}, expected 200")

    # The probe records a transport failure and STILL writes the record (a dropped artifact is
    # invisible evidence). A bundle carrying both `status: 200` and a transport error is
    # internally contradictory and was accepted (F-16, mutant V20): the recorded field was never
    # read by any conjunct.
    transport_error = direct.get("transport_error")
    if transport_error is not None:
        _fail("direct_stream", f"transport_error {transport_error!r} recorded beside status 200")

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
def _rows_by_leg(requests: dict) -> dict:
    """Group the exported rows by leg label, rejecting a repeated `direct` label.

    `legs[leg] = row` in a loop kept the LAST row with each label and discarded every earlier one
    ungraded, so a stub row could be shadowed by a clean one appended after it (F-2, mutant V2).
    The hermes leg legitimately exports MORE than one row — every route row inside its window —
    and that plurality is graded below, not silently resolved here."""
    rows = requests.get("requests")
    if not isinstance(rows, list) or not rows:
        raise Failure("bundle: omniroute-requests.json carries no request rows")
    grouped: dict = {}
    for i, row in enumerate(rows):
        row = _obj(row, f"omniroute-requests.json requests[{i}]")
        leg = _str(row.get("leg"), f"omniroute-requests.json requests[{i}].leg")
        grouped.setdefault(leg, []).append(row)
    for leg in ("direct", "hermes"):
        if leg not in grouped:
            raise Failure(f"bundle: omniroute-requests.json has no row for the {leg} leg")
    if len(grouped["direct"]) != 1:
        raise Failure("bundle: omniroute-requests.json has "
                      f"{len(grouped['direct'])} rows for the direct leg")
    return grouped


def check_row_counts(requests: dict):
    """The collector records how many rows it EXPORTED per leg (`collect_leg.sh:153-162`); this
    grades that the record matches the rows the checker actually consumes, per leg. Without it
    `row_counts` is an emitted-but-unchecked field — a hollow green (FU1): the collector could
    write `{"direct": 0, "hermes": 0}` over a full export and the proof would not notice. The two
    legs are checked SEPARATELY because the direct leg is a single-row correlation join while the
    hermes leg legitimately exports every window row (graded for uniqueness just below)."""
    recorded = requests.get("row_counts")
    if not isinstance(recorded, dict):
        raise Failure("bundle: omniroute-requests.json has no row_counts record")
    grouped = _rows_by_leg(requests)
    for leg in ("direct", "hermes"):
        expected = len(grouped[leg])
        value = recorded.get(leg)
        if isinstance(value, bool) or not isinstance(value, int) or value != expected:
            raise Failure(
                f"bundle: omniroute-requests.json row_counts[{leg!r}] is "
                f"{value!r}, expected {expected} exported {leg} row(s)")


def _instant(value, name: str):
    if not isinstance(value, str) or not value:
        raise Failure(f"bundle: {name} is not an RFC3339 stamp ({value!r})")
    try:
        parsed = _dt.datetime.fromisoformat(
            value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        raise Failure(f"bundle: {name} is not an RFC3339 stamp ({value!r})")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise Failure(
            f"bundle: {name} is not an RFC3339 stamp with an offset ({value!r})")
    return parsed.astimezone(_dt.timezone.utc)


def _require_in_window(row: dict, window: dict):
    start = _instant(window.get("start"), "hermes/leg.json window_start")
    end = _instant(window.get("end"), "hermes/leg.json window_end")
    stamp = _instant(row.get("timestamp"), "omniroute-requests.json hermes.timestamp")
    if not (start <= stamp <= end):
        raise Failure(
            f"bundle: hermes row timestamp {row.get('timestamp')!r} is outside the leg's window "
            f"{window.get('start')!r}..{window.get('end')!r}"
        )


def check_identity_route(requests: dict, direct: dict, leg_record: dict, spec: dict):
    """The load-bearing identity assertion — and the binding that makes it one.

    Realigned 2026-09-19 after the docs+measurement resolution (AF-AP-103 / Blocker 4,
    LIVE-CAPTURE-FINDINGS.md):
      direct  the fresh nonce `direct.json.nonce` is recorded by OmniRoute in the row's artifact
              requestBody; collect_leg.sh exports that record as `recorded_input`, and this binds
              `direct.json.nonce in recorded_input`. /v1/responses exposes no client-visible header
              or column that maps to call_logs on 3.8.50 (routing_decisions is empty; response_id is
              NULL for a streaming row; x-request-id / x-omniroute-request-id / correlation_id are
              distinct id-spaces). This mirrors the hermes binding: a fresh client nonce OmniRoute
              records independently.
      hermes  `call_logs.session_tag` == the leg's nonce2. The round trip logs MANY rows (>=1),
              all carrying the same tag. Each is validated; the old uniqueness rule is deleted.
    Route correlation: `combo_name == route_id` (not `requested_model`, which holds the
    resolved ref `codex/gpt-5.6-sol-ultra`, never the route id).
    Per-leg transport: the path is recorded and asserted in the permitted set, never a single
    pinned path.
    Model identity: conjunct (ii) pins `direct.json.model`; here every row's call_logs `model` must
    agree (the `models` set is size 1). The old `x-omniroute-model` header cross-check is dropped —
    a streaming /v1/responses returns no such header.
    """
    grouped = _rows_by_leg(requests)

    # The export's window must be the window the leg recorded.
    declared = {"start": leg_record.get("window_start"), "end": leg_record.get("window_end")}
    exported = _obj(requests.get("windows"), "omniroute-requests.json windows").get("hermes")
    if not isinstance(exported, dict) or exported != declared:
        raise Failure(
            f"bundle: omniroute-requests.json hermes window {exported!r} != the window "
            f"hermes/leg.json records {declared!r}"
        )

    # Hermes leg: >=1 rows, each validated. Zero is unattributable.
    if len(grouped["hermes"]) < 1:
        _fail("identity_no_hermes_rows")

    # Every hermes row must fall within the declared window (sanity bound).
    for hermes_row in grouped["hermes"]:
        _require_in_window(hermes_row, declared)

    nonce2 = _str(leg_record.get("nonce2"), "hermes/leg.json nonce2")

    # Direct leg binding (Blocker 4): the fresh nonce the direct leg sent, recorded by OmniRoute in
    # the row's artifact requestBody and exported by collect_leg.sh as `recorded_input`. The nonce
    # is a fresh 16-hex token (conjunct i floors it), so the row whose recorded request carries it
    # is unambiguously this leg's — the attribution is the nonce, mirroring the hermes session_tag.
    direct_nonce = _str(direct.get("nonce"), "direct.json nonce")

    observed_paths = {}
    models = set()

    # --- validate the single direct row ---
    row = grouped["direct"][0]
    combo = row.get("combo_name")
    if combo != spec["route_id"]:
        raise Failure(
            f"bundle: direct row combo_name {combo!r} != declared route {spec['route_id']!r}")
    recorded_input = _str(row.get("recorded_input"),
                          "omniroute-requests.json direct.recorded_input")
    if direct_nonce not in recorded_input:
        _fail("identity_direct_nonce", direct_nonce)
    if row.get("status") != 200:
        _fail("identity_status", "direct", row.get("status"))
    if row.get("method") != "POST":
        _fail("transport_method", "direct", row.get("method"))
    path = _str(row.get("path"), "omniroute-requests.json direct.path")
    if not any(path.endswith(p) for p in PERMITTED_TRANSPORT_PATHS):
        _fail("transport_path", "direct", path)
    observed_paths["direct"] = path
    provider = _str(row.get("provider"), "omniroute-requests.json direct.provider")
    if _is_stub(provider, spec["stub_routes"]):
        _fail("identity_route", provider)
    model = _str(row.get("model"), "omniroute-requests.json direct.model")
    if _is_stub(model, spec["stub_routes"]):
        _fail("identity_route", model)
    models.add(model)

    # --- validate every hermes row ---
    for i, row in enumerate(grouped["hermes"]):
        combo = row.get("combo_name")
        if combo != spec["route_id"]:
            raise Failure(
                f"bundle: hermes row[{i}] combo_name {combo!r} != declared route "
                f"{spec['route_id']!r}")
        tag = row.get("session_tag")
        if tag != nonce2:
            _fail("identity_session_tag", tag, nonce2)
        if row.get("status") != 200:
            _fail("identity_status", "hermes", row.get("status"))
        if row.get("method") != "POST":
            _fail("transport_method", "hermes", row.get("method"))
        path = _str(row.get("path"), f"omniroute-requests.json hermes[{i}].path")
        if not any(path.endswith(p) for p in PERMITTED_TRANSPORT_PATHS):
            _fail("transport_path", "hermes", path)
        observed_paths.setdefault("hermes", path)
        provider = _str(row.get("provider"), f"omniroute-requests.json hermes[{i}].provider")
        if _is_stub(provider, spec["stub_routes"]):
            _fail("identity_route", provider)
        model = _str(row.get("model"), f"omniroute-requests.json hermes[{i}].model")
        if _is_stub(model, spec["stub_routes"]):
            _fail("identity_route", model)
        models.add(model)

    if len(models) != 1:
        raise Failure(
            "bundle: the call_logs rows report different model ids " + repr(sorted(models))
        )
    # Every row's resolved model id agrees (the size-1 set above). Conjunct (ii) pins
    # direct.json.model to the expected id; the old x-omniroute-model header cross-check is dropped —
    # a streaming /v1/responses returns no such header (Blocker 4).
    return grouped["direct"][0]["provider"]


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


def _parse_tool_command(update) -> str:
    """Extract the terminal command from a real ACP tool_call (AF-AP-101).

    The real shape has the command in ``title`` (``terminal: printf <nonce>``)
    and in ``content[].content.text`` (``$ printf <nonce>``).  There is no ``rawInput``.
    """
    title = update.get("title", "")
    if isinstance(title, str) and title.startswith("terminal: "):
        return title[len("terminal: "):]
    content = update.get("content")
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                inner = block.get("content")
                if isinstance(inner, dict):
                    text = inner.get("text", "")
                    if isinstance(text, str) and text.startswith("$ "):
                        return text[len("$ "):]
    return ""


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

    prompt = prompts[0]["frame"]
    if nonce2 not in json.dumps(prompt, ensure_ascii=False):
        _fail("roundtrip", f"nonce2 {nonce2!r} absent from the prompt frame")
    expected_commands = {f"printf {nonce2}", f"printf '{nonce2}'", f'printf "{nonce2}"'}

    indexed_updates = list(enumerate(_updates(entries)))
    starts = [(index, update) for index, update in indexed_updates
              if update.get("sessionUpdate") == "tool_call"]
    if not starts:
        _fail("roundtrip", "no tool_call update in the timeline")

    exact_starts = [
        (index, update) for index, update in starts
        if update.get("kind") == "execute"
        and _parse_tool_command(update) in expected_commands
        and isinstance(update.get("toolCallId"), str)
    ]
    if len(exact_starts) != 1:
        _fail("roundtrip", f"no exact terminal tool_call for 'printf {nonce2}'")
    start_index, start = exact_starts[0]
    call_id = start["toolCallId"]

    completed = [
        (index, update) for index, update in indexed_updates
        if index > start_index
        and update.get("sessionUpdate") == "tool_call_update"
        and update.get("status") == "completed"
        and update.get("toolCallId") == call_id
    ]
    if not completed:
        _fail("roundtrip", "no tool_call that started reached status 'completed' after it started")

    # THE ROUND TRIP, not a coincidence of two facts: the ACP `tool_call` start carries
    # kind=execute and the command in title/content (AF-AP-101 real shape, no rawInput);
    # only a later completed update with the same toolCallId can prove that exact request ran.
    if not any(nonce2 in json.dumps(update.get("content"), ensure_ascii=False)
               for _index, update in completed):
        _fail("roundtrip",
              f"nonce2 {nonce2!r} absent from the completed tool call's output")

    text = _agent_text(entries)
    if nonce2 not in text:
        _fail("roundtrip", f"nonce2 {nonce2!r} absent from the final agent text")


# --- conjunct (v): the transport the ADR pins -------------------------------------------------
def _provider_block(profile) -> tuple[str, dict]:
    providers = _obj(profile, "profile.yaml").get("providers")
    providers = _obj(providers, "profile.yaml providers")
    if len(providers) != 1:
        raise Failure(
            f"bundle: profile.yaml declares {len(providers)} providers, expected exactly 1"
        )
    (name, block), = providers.items()
    return str(name), _obj(block, "profile.yaml provider block")


def _walk_credentials(node, path: str):
    """Reject credential-bearing names or values anywhere below a provider block."""
    if isinstance(node, dict):
        for key, value in node.items():
            child_path = f"{path}.{key}"
            key_is_allowed_env_name = (
                key == "key_env" and path.count(".") == 1 and path.startswith("providers."))
            if is_credential_name(key) and not key_is_allowed_env_name:
                raise Failure(
                    f"bundle: profile.yaml carries an inline credential under {child_path}")
            if (isinstance(value, str)
                    and value.lower().startswith(("bearer ", "basic ", "sk-", "sk_"))):
                raise Failure(
                    f"bundle: profile.yaml carries an inline credential under {child_path}")
            _walk_credentials(value, child_path)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _walk_credentials(value, f"{path}.{index}")


def check_transport(profile):
    provider_name, block = _provider_block(profile)
    # api_mode may be in the provider block (old layout) or in the model section (new layout,
    # AF-AP-103). Check both; the model section wins when both exist.
    model_section = _obj(profile, "profile.yaml").get("model")
    api_mode = None
    if isinstance(model_section, dict):
        api_mode = model_section.get("api_mode")
    if api_mode is None:
        api_mode = block.get("api_mode")
    if api_mode not in PERMITTED_API_MODES:
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

    # The launched profile must never carry a key VALUE. Only the exact provider-level env NAME
    # may appear. Walk mappings and lists recursively so nested custom headers cannot hide it.
    _walk_credentials(block, f"providers.{provider_name}")
    if block.get("key_env") != "OMNIROUTE_API_KEY":
        raise Failure(
            f"bundle: profile.yaml key_env is {block.get('key_env')!r}, expected 'OMNIROUTE_API_KEY'"
        )


# --- conjunct (vi): the deny-by-default env allowlist ------------------------------------------
def check_env(env_names):
    """AF-AP-23, as far as it goes: every name whose SEGMENTS mark it a credential
    (`is_credential_name`, which states its residual class) must be an EXACT member of
    ENV_CREDENTIAL_ALLOWLIST — never a prefix, never a blacklist of known providers, so
    `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OMNIROUTE_API_KEY_2` and the provider nobody listed
    all fail the same way. It is a screen over the whole name domain followed by an exact
    allow-list, not an allow-list over the whole domain: a name with no marker segment is not
    screened at all, and the docstring says so rather than claiming a boundary the code does not
    have (F-12)."""
    offenders = sorted(
        name for name in env_names
        if is_credential_name(name) and name not in ENV_CREDENTIAL_ALLOWLIST
    )
    if offenders:
        _fail("env_provider_key", offenders[0])


# --- conjunct (vi.b): WHICH process the environ belongs to --------------------------------------
def check_env_record(record: dict, leg: dict):
    """"HERMES holds no upstream provider key" is the assertion; "some process holds none" is what
    a name list alone proves. The record carries the pid it read, the `exe` symlink of that pid and
    the tee's own record of the binary it spawned — all three were written and none was ever read
    (F-11, mutant V15: `{"pid": 1, "exe": "/usr/bin/sleep"}` passed).

    Both pins come from S0-01's `pins` module through the SAME import the timeline reader uses, so
    a drift in the pinned runtime cannot leave this checker asserting a stale path:
      * `exe` is the INTERPRETER, not the entry point. `/proc/<agent_child_pid>/exe` of a python
        console-script resolves to the interpreter — the tee records exactly that value as
        `agent_interpreter_realpath` (`proofs/S0-01/tools/frame_tee.py`'s `agent_interpreter_realpath`), and in the committed
        real corpus it is `/usr/bin/python3.13`. Pinning `PINNED_AGENT_REALPATH` here would be an
        assertion no real capture could satisfy.
      * `agent_realpath` is the hermes-acp entry point the tee spawned
        (the tee's `agent_realpath` key), which is what makes the record Hermes' rather than any python
        process's. It is required: a record without it cannot support the assertion.
    """
    s0_01 = _load_s0_01_module()
    pid = record.get("pid")
    if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
        raise Failure(
            f"bundle: hermes/hermes-env-names.json pid is not a strict positive integer ({pid!r})")
    agent_child_pid = leg.get("agent_child_pid")
    if (isinstance(agent_child_pid, bool) or not isinstance(agent_child_pid, int)
            or agent_child_pid <= 0):
        raise Failure(
            "bundle: hermes/leg.json agent_child_pid is not a strict positive integer "
            f"({agent_child_pid!r})")
    if pid != agent_child_pid:
        raise Failure(
            f"bundle: hermes/hermes-env-names.json pid {pid} does not match "
            f"hermes/leg.json agent_child_pid {agent_child_pid}")
    exe = _str(record.get("exe"), "hermes/hermes-env-names.json exe")
    if exe != s0_01.PINNED_AGENT_INTERPRETER_REALPATH:
        _fail("env_process", "exe", exe, s0_01.PINNED_AGENT_INTERPRETER_REALPATH)
    agent = _str(record.get("agent_realpath"), "hermes/hermes-env-names.json agent_realpath")
    if agent != s0_01.PINNED_AGENT_REALPATH:
        _fail("env_process", "agent_realpath", agent, s0_01.PINNED_AGENT_REALPATH)


# --- bundle assembly + the graded sequence -----------------------------------------------------
def load_direct(root: Path) -> dict:
    """The direct leg alone. Read FIRST and separately because the credential verdicts are graded
    on it before the hermes half is required: the negative bundle a real `--no-credential` leg
    produces has no hermes half (the pinned S0-01 launcher injects OMNIROUTE_API_KEY from the
    owner's env file, so a key-free Hermes leg is not capturable — the bundle's NOT-CAPTURED.md
    says so), and it must still grade as the seed's kill switch rather than as a short bundle."""
    direct_dir = root / "direct"
    hermes_dir = root / "hermes"
    if not root.is_dir() or not (direct_dir.is_dir() or hermes_dir.is_dir()):
        raise Deferred("S0-03 evidence not captured")
    return _obj(_read_json(direct_dir / "direct.json", "direct/direct.json"),
                "direct/direct.json")


def load_bundle(root: Path, direct: dict) -> dict:
    hermes_dir = root / "hermes"
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
        "env_record": env_record,
        "env_names": names,
        "leg": leg,
        "profile": profile,
        "entries": entries,
        "requests": requests,
    }


def check_bundle(root: Path, spec: dict) -> str:
    direct = load_direct(root)

    # Priority 0 on the direct leg's own evidence, then the rest of the bundle, then the second
    # half of the kill switch, then conjuncts (i)..(vi) in the brief's order. First failure wins.
    check_credential_at_the_gate(direct)
    bundle = load_bundle(root, direct)
    check_credential_in_the_environ(bundle["env_names"])
    check_direct_stream(bundle["direct"])
    check_identity_model(bundle["direct"], spec)
    check_row_counts(bundle["requests"])
    provider = check_identity_route(bundle["requests"], bundle["direct"], bundle["leg"], spec)
    check_roundtrip(bundle["entries"], _str(bundle["leg"].get("nonce2"), "hermes/leg.json nonce2"))
    check_transport(bundle["profile"])
    check_env_record(bundle["env_record"], bundle["leg"])
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
