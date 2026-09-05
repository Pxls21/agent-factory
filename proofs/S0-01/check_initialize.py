#!/usr/bin/env python3
"""S0-01 initialize-frame checker (assertion 1 + the negative control). Schema-layer, LLM-free.

Validates ACP `initialize` frames against the PINNED protocol schema
`proofs/S0-01/fixtures/acp-schema-v1.json` (agent-client-protocol@37a7d4f8, `schema/v1/schema.json`;
v1 is ACP's stable wire version). The seed's negative control is enforced HERE because the pinned
hermes-acp's own `initialize` handler is lenient (a missing `protocolVersion` defaults instead of
erroring), so a missing required field is a violation of the pinned CONTRACT, caught at the schema layer.

CLI:  check_initialize.py request  <frame.jsonl | params.json>
      check_initialize.py response <frame.jsonl | result.json>
Prints the classification; exit 0 on `ok`, 1 on `protocol-violation: …`, 2 on usage/input errors.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
SCHEMA = HERE / "fixtures" / "acp-schema-v1.json"
MISSING_REQUIRED = "protocol-violation: missing required initialize field"


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


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in ("request", "response"):
        print(__doc__.strip().splitlines()[-4].strip(), file=sys.stderr)
        return 2
    kind, path = argv[1], Path(argv[2])
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
