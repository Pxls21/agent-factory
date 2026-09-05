"""S0-01 initialize-frame checker (assertion 1 + the negative control). Schema-layer, LLM-free.

Validates ACP `initialize` frames against the PINNED protocol schema
`proofs/S0-01/fixtures/acp-schema-v1.json` (agent-client-protocol@37a7d4f8, `schema/v1/schema.json`;
v1 is ACP's stable wire version). The seed's negative control is enforced HERE because the pinned
hermes-acp's own `initialize` handler is lenient (a missing `protocolVersion` defaults instead of
erroring), so a missing required field is a violation of the pinned CONTRACT, caught at the schema layer.

CLI:  check_initialize.py request  <frame.jsonl | params.json>
      check_initialize.py response <frame.jsonl | result.json>
      check_initialize.py request  <probe-capture-dir>   (negative probe: validates capture + classifies)
      check_initialize.py response <probe-capture-dir>   (classifies the a2c response's result)
Prints the classification; exit 0 on `ok`, 1 on `protocol-violation: …` or `failure_reason: …`, 2 on deferred.
Directory mode `request <dir>`: validates the negative probe capture (params == fixture, identity pins,
a2c response present) then classifies the request and prints the observed agent response on line 2.
Directory mode `response <dir>`: classifies the a2c response's result against InitializeResponse.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
SCHEMA = HERE / "fixtures" / "acp-schema-v1.json"
FIXTURE = HERE / "fixtures" / "neg-malformed-initialize.json"
MISSING_REQUIRED = "protocol-violation: missing required initialize field"

# Import pins for runtime-identity checks in directory mode.
# S0-01 is not a valid Python package name, so use sys.path.
sys.path.insert(0, str(HERE))
import pins  # noqa: E402


def load_schema(path: Path = SCHEMA) -> dict:
    return json.loads(Path(path).read_text())


def validator_for(schema: dict, definition: str) -> Draft202012Validator:
    if definition not in schema["$defs"]:
        raise KeyError(f"pinned schema has no definition {definition!r}")
    wrapper = {"$schema": schema["$schema"], "$ref": f"#/$defs/{definition}", "$defs": schema["$defs"]}
    return Draft202012Validator(wrapper)


def _classify(obj: object, schema: dict, definition: str) -> str:
    errors = sorted(validator_for(schema, definition).iter_errors(obj), key=lambda e: (list(e.path), e.message))
    if not errors:
        return "ok"
    for err in errors:
        if err.validator == "required" and "protocolVersion" in err.message and not list(err.path):
            return MISSING_REQUIRED
    first = errors[0]
    where = "/".join(str(p) for p in first.path) or "<root>"
    return f"protocol-violation: {where}: {first.message}"


def classify_request(params: object, schema: dict | None = None) -> str:
    """Classify an `initialize` request's `params` against v1 InitializeRequest."""
    return _classify(params, schema or load_schema(), "InitializeRequest")


def classify_response(result: object, schema: dict | None = None) -> str:
    """Classify an `initialize` response's `result` against v1 InitializeResponse."""
    return _classify(result, schema or load_schema(), "InitializeResponse")


def load_payload(path: Path, kind: str) -> object:
    """Accept a raw JSON-RPC frame file (first line) or a bare params/result JSON document."""
    text = Path(path).read_text()
    first = text.splitlines()[0] if path.suffix == ".jsonl" else text
    obj = json.loads(first)
    if isinstance(obj, dict) and obj.get("jsonrpc") == "2.0":
        if kind == "request":
            if obj.get("method") != "initialize":
                raise ValueError(f"frame method is {obj.get('method')!r}, not 'initialize'")
            return obj.get("params")
        if "error" in obj:
            raise ValueError(f"frame is a JSON-RPC error: {obj['error']}")
        return obj.get("result")
    return obj


def _format_observed(resp: dict) -> str:
    """Format the observed agent response line from an a2c JSON-RPC frame."""
    if "error" in resp:
        err = resp["error"]
        if isinstance(err, dict):
            code = err.get("code", "?")
            message = err.get("message", str(err))
        else:
            code = "?"
            message = str(err)
        return f"observed: error code={code} message={message}"
    if "result" in resp:
        result = resp.get("result") or {}
        pv = result.get("protocolVersion")
        caps = json.dumps(result.get("agentCapabilities"), separators=(",", ":"))
        return f"observed: result protocolVersion={pv} agentCapabilities={caps}"
    return "observed: none: unparseable response"


def _check_request_directory(dirpath: Path) -> int:
    """Validate a negative probe capture directory for `request <dir>`.

    Contract: exit 2 if directory or timeline absent; exit 1 with `failure_reason: negative: ...`
    on any validation failure; exit 1 with the classification on line 1 and the observed agent
    response on line 2 when the capture is valid.
    """
    if not dirpath.is_dir():
        print("deferred: negative probe not captured")
        return 2
    tl_path = dirpath / "timeline.jsonl"
    if not tl_path.exists():
        print("deferred: negative probe not captured")
        return 2

    entries = []
    for line in tl_path.read_text().splitlines():
        if line.strip():
            entries.append(json.loads(line))

    c2a = [e for e in entries if e["dir"] == "c2a"]
    a2c = [e for e in entries if e["dir"] == "a2c"]

    # seq-1 must be a c2a initialize request
    if not c2a:
        print("failure_reason: negative: no c2a frames in timeline")
        return 1
    init_req = c2a[0]["frame"]
    if init_req.get("method") != "initialize":
        print(f"failure_reason: negative: first c2a frame is {init_req.get('method')!r}, not initialize")
        return 1

    # params must deep-equal the fixture JSON
    params = init_req.get("params")
    fixture = json.loads(FIXTURE.read_text())
    if params != fixture:
        print("failure_reason: negative: params != fixture")
        return 1

    # Runtime identity pins
    rid_path = dirpath / "runtime-identity.json"
    if not rid_path.exists():
        print("failure_reason: negative: runtime-identity.json absent")
        return 1
    rid = json.loads(rid_path.read_text())
    pin_checks = [
        ("agent_realpath", pins.PINNED_AGENT_REALPATH),
        ("agent_entrypoint_sha256", pins.PINNED_AGENT_ENTRYPOINT_SHA256),
        ("agent_interpreter_realpath", pins.PINNED_AGENT_INTERPRETER_REALPATH),
        ("agent_interpreter_sha256", pins.PINNED_AGENT_INTERPRETER_SHA256),
    ]
    for field, expected in pin_checks:
        if rid.get(field) != expected:
            print(f"failure_reason: negative: {field} mismatch")
            return 1
    if rid.get("python_dont_write_bytecode") is not True:
        print("failure_reason: negative: python_dont_write_bytecode is not True")
        return 1

    # Must have an a2c response to the request id
    req_id = init_req.get("id")
    matching_responses = [e for e in a2c if e["frame"] is not None and e["frame"].get("id") == req_id]
    if not matching_responses:
        print("failure_reason: negative: no agent response captured")
        return 1

    # Classify the request params
    verdict = classify_request(params)
    print(verdict)
    # Print the observed agent response
    resp = matching_responses[0]["frame"]
    print(_format_observed(resp))
    return 1


def _check_response_directory(dirpath: Path) -> int:
    """Classify the a2c response's result for `response <dir>`.

    Reads the timeline, finds the first a2c response, and classifies its result
    against InitializeResponse. Distinct output from request <dir>.
    """
    if not dirpath.is_dir():
        print("deferred: negative probe not captured")
        return 2
    tl_path = dirpath / "timeline.jsonl"
    if not tl_path.exists():
        print("deferred: negative probe not captured")
        return 2

    entries = []
    for line in tl_path.read_text().splitlines():
        if line.strip():
            entries.append(json.loads(line))

    a2c = [e for e in entries if e["dir"] == "a2c"]
    if not a2c:
        print("failure_reason: negative: no a2c response to classify")
        return 1

    resp = a2c[0]["frame"]
    if resp is None:
        print("failure_reason: negative: a2c frame is null (non-JSON)")
        return 1
    if "error" in resp:
        err = resp["error"]
        if isinstance(err, dict):
            code = err.get("code", "?")
            message = err.get("message", str(err))
        else:
            code = "?"
            message = str(err)
        print(f"error code={code} message={message}")
        return 1
    result = resp.get("result")
    verdict = classify_response(result)
    print(verdict)
    return 0 if verdict == "ok" else 1


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in ("request", "response"):
        print("usage: check_initialize.py request|response <file|dir>", file=sys.stderr)
        return 2
    kind, path = argv[1], Path(argv[2])
    # directory mode: probe capture (existing dir, or path with no file extension)
    if path.is_dir() or (not path.exists() and path.suffix not in (".json", ".jsonl")):
        if kind == "request":
            return _check_request_directory(path)
        return _check_response_directory(path)
    try:
        payload = load_payload(path, kind)
    except (OSError, ValueError, json.JSONDecodeError, IndexError) as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2
    verdict = classify_request(payload) if kind == "request" else classify_response(payload)
    print(verdict)
    return 0 if verdict == "ok" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
