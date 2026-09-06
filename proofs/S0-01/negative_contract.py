"""The S0-01 negative-control contract — ONE strict validator shared by both consumers.

`check_initialize.py request <dir>` (the spec's negative leg) and `check_acp_conformance.py` (which
embeds the negative leg in the positive bundle) both call `validate_negative_dir`. The audit of
08a4a7d (2026-09-05, P1 "negative execution can be absent or explicitly failed while the checker
passes") showed the two consumers matching a JSON-RPC id without requiring a valid RESPONSE envelope,
a delivered request, a healthy probe, or the pinned agent's actual rejection. This module is the
fix: everything below is required, and a Failure names the exact reason.

What a valid negative capture proves: the PINNED hermes-acp (identity pinned) received the malformed
initialize EXACTLY as committed in the fixture (deep-equal params, delivered), and answered it with
the pinned JSON-RPC error (`pins.PINNED_NEGATIVE_ERROR_CODE` / `_MESSAGE`) — the runtime's own
rejection, observed live, not a local schema classification.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import re
from pathlib import Path

import pins

HERE = Path(__file__).resolve().parent
ISO_RE = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{6}Z$")


class NegativeFailure(Exception):
    """A negative capture that does not meet the contract; str(exc) is the reason (no prefix)."""


class NegativeDeferred(Exception):
    """No negative capture at all (the directory or its timeline is absent)."""


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _raise_constant(name):
    raise ValueError(f"non-finite JSON constant {name}")


def _parse_float_strict(s):
    v = float(s)
    if v != v or v in (float("inf"), float("-inf")):
        raise ValueError("non-finite float")
    return v


def _load_timeline(path: Path):
    entries = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise NegativeFailure(f"timeline.jsonl line {lineno} is blank")
        try:
            e = json.loads(line, parse_constant=_raise_constant, parse_float=_parse_float_strict)
        except ValueError as exc:
            raise NegativeFailure(f"timeline.jsonl line {lineno} is not strict JSON: {exc}") from None
        if not isinstance(e, dict):
            raise NegativeFailure(f"timeline.jsonl line {lineno} is not an object")
        entries.append(e)
    return entries


def _is_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _parse_utc(s: str) -> datetime.datetime:
    if not isinstance(s, str) or not ISO_RE.match(s):
        raise NegativeFailure(f"timestamp {s!r} does not match YYYY-MM-DDTHH:MM:SS.ffffffZ")
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.timezone.utc)


def validate_negative_dir(neg_dir: Path, fixtures_dir: Path | None = None) -> str:
    """Return the observed line (`observed: error code=<code> message=<message>`) or raise."""
    fixtures_dir = fixtures_dir or (HERE / "fixtures")
    if not neg_dir.is_dir() or not (neg_dir / "timeline.jsonl").exists():
        raise NegativeDeferred("negative probe not captured")
    present = {p.name for p in neg_dir.iterdir()}
    if present != set(pins.NEGATIVE_REQUIRED_FILES):
        missing = sorted(set(pins.NEGATIVE_REQUIRED_FILES) - present)
        extra = sorted(present - set(pins.NEGATIVE_REQUIRED_FILES))
        if missing:
            raise NegativeFailure(f"{missing[0]} absent")
        raise NegativeFailure(f"unexpected entry {extra[0]}")
    fixture_path = fixtures_dir / "neg-malformed-initialize.json"
    if not fixture_path.exists():
        raise NegativeFailure("fixtures/neg-malformed-initialize.json absent")
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

    entries = _load_timeline(neg_dir / "timeline.jsonl")
    if not entries:
        raise NegativeFailure("timeline.jsonl is empty")
    for i, e in enumerate(entries):
        if set(e) - {"seq", "dir", "t_utc", "t_mono_ns", "frame", "raw", "raw_b64", "delivered"}:
            raise NegativeFailure(f"timeline entry {i + 1} has unexpected keys")
        if not _is_int(e.get("seq")) or e["seq"] != i + 1:
            raise NegativeFailure(f"timeline seq not 1..N at index {i}")
        if e.get("dir") not in ("c2a", "a2c"):
            raise NegativeFailure(f"timeline seq {i + 1} has an invalid dir")
        if not _is_int(e.get("t_mono_ns")):
            raise NegativeFailure(f"timeline seq {i + 1} t_mono_ns is not an int")
        _parse_utc(e.get("t_utc"))
        if i and entries[i - 1]["t_mono_ns"] > e["t_mono_ns"]:
            raise NegativeFailure(f"t_mono_ns decreases at seq {i + 1}")
    first = entries[0]
    if first["dir"] != "c2a":
        raise NegativeFailure("seq 1 is not a c2a frame")
    req = first.get("frame")
    if not isinstance(req, dict) or req.get("method") != "initialize" or "id" not in req:
        raise NegativeFailure("seq 1 is not an initialize request")
    if first.get("delivered") is False:
        raise NegativeFailure("initialize request was not delivered to the agent")
    if req.get("params") != fixture:
        raise NegativeFailure("initialize params != fixture")
    req_id = req["id"]

    responses = []
    for e in entries[1:]:
        f = e.get("frame")
        if e["dir"] == "c2a":
            raise NegativeFailure(f"unexpected second c2a frame at seq {e['seq']}")
        if not isinstance(f, dict):
            raise NegativeFailure(f"non-JSON agent frame at seq {e['seq']}")
        if "id" in f and "method" in f:
            raise NegativeFailure(f"agent sent a request (method {f['method']!r}) instead of a response at seq {e['seq']}")
        if "id" in f:
            if f["id"] == req_id:
                responses.append(f)
            else:
                raise NegativeFailure(f"agent response id {f['id']!r} does not match the request id at seq {e['seq']}")
        elif "method" not in f:
            raise NegativeFailure(f"agent frame at seq {e['seq']} is neither a response nor a notification")
    if not responses:
        raise NegativeFailure("no agent response captured")
    if len(responses) != 1:
        raise NegativeFailure(f"{len(responses)} agent responses carry the request id (expected exactly one)")
    resp = responses[0]
    if resp.get("jsonrpc") != "2.0" or ("result" in resp) == ("error" in resp):
        raise NegativeFailure("agent response is not a valid JSON-RPC envelope (exactly one of result/error)")
    if "result" in resp:
        pv = resp["result"].get("protocolVersion") if isinstance(resp["result"], dict) else None
        raise NegativeFailure(f"pinned agent accepted a malformed initialize (result protocolVersion={pv})")
    err = resp["error"]
    if not isinstance(err, dict) or not _is_int(err.get("code")):
        raise NegativeFailure("agent error envelope has no integer code")
    if err["code"] != pins.PINNED_NEGATIVE_ERROR_CODE or err.get("message") != pins.PINNED_NEGATIVE_ERROR_MESSAGE:
        raise NegativeFailure(
            f"agent error is code={err['code']} message={err.get('message')!r}, expected "
            f"code={pins.PINNED_NEGATIVE_ERROR_CODE} message={pins.PINNED_NEGATIVE_ERROR_MESSAGE!r}")

    rid = json.loads((neg_dir / "runtime-identity.json").read_text(encoding="utf-8"))
    if not isinstance(rid, dict):
        raise NegativeFailure("runtime-identity.json is not an object")
    if rid.get("probe_error") not in (None, ""):
        raise NegativeFailure(f"probe reported an error: {rid['probe_error']}")
    missing = sorted(set(pins.NEGATIVE_IDENTITY_KEYS) - set(rid))
    if missing:
        raise NegativeFailure(f"runtime identity key {missing[0]} absent")
    probe_file = HERE / "tools" / "acp_probe.py"
    if not probe_file.exists():
        raise NegativeFailure("tools/acp_probe.py absent")
    # probe_path is venue-specific (the PC clone path); probe_sha256 is the pin.
    if rid.get("probe_sha256") != _sha256_file(probe_file):
        raise NegativeFailure("probe_sha256 mismatch")
    if rid.get("agent_argv") != [pins.PINNED_AGENT_REALPATH]:
        raise NegativeFailure("agent_argv mismatch")
    for key, pin in (("agent_realpath", pins.PINNED_AGENT_REALPATH),
                     ("agent_entrypoint_sha256", pins.PINNED_AGENT_ENTRYPOINT_SHA256),
                     ("agent_interpreter_realpath", pins.PINNED_AGENT_INTERPRETER_REALPATH),
                     ("agent_interpreter_sha256", pins.PINNED_AGENT_INTERPRETER_SHA256)):
        if rid.get(key) != pin:
            raise NegativeFailure(f"{key} mismatch")
    if not _is_int(rid.get("agent_child_pid")) or rid["agent_child_pid"] <= 0:
        raise NegativeFailure("agent_child_pid is not a positive int")
    if rid.get("python_dont_write_bytecode") is not True:
        raise NegativeFailure("python_dont_write_bytecode is not True")
    if rid.get("agent_exit_code") != 0 or isinstance(rid.get("agent_exit_code"), bool):
        raise NegativeFailure(f"agent_exit_code is {rid.get('agent_exit_code')!r}, expected 0")
    spawned = _parse_utc(rid.get("spawned_at_utc"))
    if spawned > _parse_utc(first["t_utc"]):
        raise NegativeFailure("spawned_at_utc is later than the first frame")

    env = json.loads((neg_dir / "env.json").read_text(encoding="utf-8"))
    if not isinstance(env, dict):
        raise NegativeFailure("env.json is not an object")
    for key, pin in (("HERMES_HOME", pins.PINNED_HERMES_HOME), ("PYTHONDONTWRITEBYTECODE", "1"),
                     ("S0_01_AGENT", pins.PINNED_AGENT_REALPATH)):
        if env.get(key) != pin:
            raise NegativeFailure(f"env {key} mismatch")
    omni = env.get("OMNIROUTE_API_KEY")
    if not (isinstance(omni, dict) and omni.get("redacted") is True and _is_int(omni.get("len")) and omni["len"] > 0):
        raise NegativeFailure("env OMNIROUTE_API_KEY not redacted or empty")
    return f"observed: error code={err['code']} message={err['message']}"
