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
Prints the classification; exit 0 on `ok`, 1 on `protocol-violation: …` or `failure_reason: …`,
2 on deferred, 64 on CLI usage error.
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
MISSING_REQUIRED = "protocol-violation: missing required initialize field"


# Import pins for runtime-identity checks in directory mode.
# S0-01 is not a valid Python package name, so use sys.path.
sys.path.insert(0, str(HERE))
import negative_contract as nc  # noqa: E402


def _nan_raising(x):
    """parse_constant callback that rejects NaN/Infinity in JSON (A11)."""
    raise ValueError(f"NaN/Infinity not allowed in timeline: {x!r}")


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


def _check_request_directory(dirpath: Path, fixtures_dir: Path = None) -> int:
    """Validate a negative probe capture directory for `request <dir>` via A22 shared validator.

    Contract: exit 2 if deferred; exit 1 with `failure_reason: negative: <reason>` on any
    validation failure; exit 1 with the classification on line 1 and the validator's observed
    line on line 2 when the capture is valid.
    """
    fixtures_dir = fixtures_dir or (HERE / "fixtures")
    try:
        observed = nc.validate_negative_dir(dirpath, fixtures_dir)
    except nc.NegativeDeferred as exc:
        print(f"deferred: {exc}")
        return 2
    except nc.NegativeFailure as exc:
        print(f"failure_reason: negative: {exc}")
        return 1
    # The validator passed — classify the request params.
    first_line = (dirpath / "timeline.jsonl").read_text(encoding="utf-8").splitlines()[0]
    params = json.loads(first_line)["frame"]["params"]
    schema = load_schema(fixtures_dir / "acp-schema-v1.json")
    verdict = classify_request(params, schema)
    print(verdict)
    print(observed)
    return 1


def _check_response_directory(dirpath: Path, fixtures_dir: Path = None) -> int:
    """Classify the a2c response's result for `response <dir>`.

    Reads the timeline, finds the a2c frame whose id == the request id,
    and classifies its result against InitializeResponse.
    Distinct output from request <dir> (V15: match by id, not a2c[0]).
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
            entries.append(json.loads(line, parse_constant=_nan_raising))

    # V15: find the c2a initialize request id, then match the a2c response by id
    c2a = [e for e in entries if e["dir"] == "c2a"]
    a2c = [e for e in entries if e["dir"] == "a2c"]
    if not c2a:
        print("failure_reason: negative: no c2a frames in timeline")
        return 1
    req_id = c2a[0]["frame"].get("id") if c2a[0]["frame"] is not None else None
    matching = [e for e in a2c if e["frame"] is not None and e["frame"].get("id") == req_id]
    if not matching:
        print("failure_reason: negative: no a2c response to classify")
        return 1

    resp = matching[0]["frame"]
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
    fixtures_dir = fixtures_dir or (HERE / "fixtures")
    schema = load_schema(fixtures_dir / "acp-schema-v1.json")
    verdict = classify_response(result, schema)
    print(verdict)
    return 0 if verdict == "ok" else 1


def main(argv: list[str]) -> int:
    # Parse --fixtures-dir (optional, default proofs/S0-01/fixtures)
    args = list(argv[1:])
    fixtures_dir = HERE / "fixtures"
    if "--fixtures-dir" in args:
        idx = args.index("--fixtures-dir")
        if idx + 1 >= len(args):
            print("usage: check_initialize.py request|response <file|dir> [--fixtures-dir <dir>]",
                  file=sys.stderr)
            return 64
        fixtures_dir = Path(args[idx + 1])
        args = args[:idx] + args[idx + 2:]
    if len(args) != 2 or args[0] not in ("request", "response"):
        print("usage: check_initialize.py request|response <file|dir> [--fixtures-dir <dir>]",
              file=sys.stderr)
        return 64  # A10: usage error exits 64 (EX_USAGE), never 2
    kind, path = args[0], Path(args[1])
    # directory mode: probe capture (existing dir, or path with no file extension)
    if path.is_dir() or (not path.exists() and path.suffix not in (".json", ".jsonl")):
        # 6-verify F13: wrap directory mode so any exception → failure_reason: malformed evidence
        try:
            if kind == "request":
                return _check_request_directory(path, fixtures_dir)
            return _check_response_directory(path, fixtures_dir)
        except Exception as exc:
            print(f"failure_reason: malformed evidence: {type(exc).__name__}: {exc}")
            return 1
    try:
        payload = load_payload(path, kind)
    except (OSError, ValueError, json.JSONDecodeError, IndexError) as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 64  # A10: input errors are usage-class
    schema = load_schema(fixtures_dir / "acp-schema-v1.json")
    verdict = classify_request(payload, schema) if kind == "request" else classify_response(payload, schema)
    print(verdict)
    return 0 if verdict == "ok" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
