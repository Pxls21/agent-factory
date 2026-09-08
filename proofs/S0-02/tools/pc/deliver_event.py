#!/usr/bin/env python3
"""Deliver one S0-02 fixture to the isolated Buzz relay and record the receipt.

    deliver_event.py --fixture <name> --leg-dir <dir> --secret <role.env> \
                     --relay-http <http://127.0.0.1:PORT> --t0 <epoch> [--reuse <event.json>]

NOT RUN IN THE SANDBOX. This runs on the PC beside the S0-01 relay stack; the
sandbox has no relay and no key material. Every external call it makes is listed
in the lane report.

WHY IT SIGNS RATHER THAN POSTING THE COMMITTED SPECIMEN
-------------------------------------------------------
The committed fixture's `event` is a SPECIMEN signed with a fixture key (see
tools/build_fixtures.py). Three things force a run-time signature:

  * buzz-relay refuses any event whose created_at is more than +/-900s from
    server time (MAX_TIMESTAMP_DRIFT_SECS, crates/buzz-relay/src/handlers/ingest.rs:2224),
    so a fixed committed timestamp cannot be delivered at all;
  * buzz-relay refuses any event whose pubkey differs from the NIP-98
    authenticated identity (crates/buzz-relay/src/handlers/ingest.rs:2242), so
    the delivered event must be signed by the ROLE key, which lives only on this
    host;
  * the repository holds no private key for owner, agent, relay or user2.

So the fixture supplies the deterministic TEMPLATE (kind, tags, content,
created_at offset) and the role key supplies the signature. `--reuse` posts a
previously delivered event VERBATIM, which is how the replay leg delivers one
id twice and how the bad-signature leg delivers the positive event with a byte
flipped.

The secret file is sourced by the CALLER into the environment (BUZZ_PRIVATE_KEY);
it is never passed in argv (AF-AP-39). --secret names the file only so the leg
record can say which role signed, and its contents are never printed.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROOF_DIR = HERE.parent.parent
ROOT = PROOF_DIR.parent.parent
NOSTR_VERIFY = ROOT / "proofs" / "S0-01" / "tools" / "nostr_verify.py"

KIND_NIP98 = 27235
SIG_FLIP_BYTE_INDEX = -1
HTTP_TIMEOUT_S = 20


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


nv = _load("s0_01_nostr_verify", NOSTR_VERIFY)


def _privkey() -> str:
    """Resolve the role key ONCE (AP-1: the environment is not a config channel
    to be re-read on a decision path). The caller threads the value explicitly."""
    key = os.environ.get("BUZZ_PRIVATE_KEY", "")
    if not key:
        raise SystemExit(
            "BUZZ_PRIVATE_KEY is not in the environment — source the role secret "
            "file before calling (set -a; . <role>.env; set +a)"
        )
    return key.strip().lower()


def _nip98_header(privkey: str, url: str, method: str, body: bytes) -> str:
    """NIP-98: a kind-27235 event tagged with the method and URL, base64 in the
    Authorization header. The payload tag binds the exact body bytes."""
    payload = hashlib.sha256(body).hexdigest()
    auth = nv.sign_event(privkey, {
        "created_at": int(time.time()),
        "kind": KIND_NIP98,
        "tags": [["u", url], ["method", method], ["payload", payload]],
        "content": "",
    })
    blob = json.dumps(auth, separators=(",", ":"), sort_keys=True).encode()
    return "Nostr " + base64.b64encode(blob).decode()


def _post(url: str, body: bytes, header: str) -> tuple:
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json", "Authorization": header},
    )
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")


def _normalise(status: int, raw: str, event_id: str) -> dict:
    """One receipt shape for every outcome.

    A 200 carries {"event_id","accepted","message"}
    (crates/buzz-relay/src/api/bridge.rs:965-967). A refusal before ingest is an
    api_error blob with a different shape, so it is normalised here — never
    dropped, because a leg with no receipt cannot be graded.
    """
    receipt = {"http_status": status, "event_id": event_id, "accepted": False, "message": ""}
    try:
        blob = json.loads(raw)
    except json.JSONDecodeError:
        receipt["message"] = raw.strip()
        return receipt
    if isinstance(blob, dict):
        if "accepted" in blob:
            receipt["accepted"] = bool(blob["accepted"])
        if blob.get("event_id"):
            receipt["event_id"] = blob["event_id"]
        for key in ("message", "error", "reason"):
            if isinstance(blob.get(key), str) and blob[key]:
                receipt["message"] = blob[key]
                break
    if not receipt["message"]:
        receipt["message"] = raw.strip()
    return receipt


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--leg-dir", required=True)
    ap.add_argument("--secret", required=True, help="role secret FILE (name recorded, never read here)")
    ap.add_argument("--relay-http", required=True)
    ap.add_argument("--t0", type=int, required=True)
    ap.add_argument("--reuse", help="post this already-signed event verbatim")
    ap.add_argument("--flip-signature", action="store_true",
                    help="flip one signature byte of the reused event (bad-signature leg)")
    args = ap.parse_args(argv[1:])

    fixture_path = PROOF_DIR / "fixtures" / f"{args.fixture}.json"
    fixture = json.loads(fixture_path.read_text())
    leg_dir = Path(args.leg_dir)
    leg_dir.mkdir(parents=True, exist_ok=True)

    privkey = _privkey()
    if args.reuse:
        event = json.loads(Path(args.reuse).read_text())
        if args.flip_signature:
            sig = bytearray.fromhex(event["sig"])
            sig[SIG_FLIP_BYTE_INDEX] ^= 0x01
            event["sig"] = sig.hex()
            ok, _reason = nv.verify_event(event)
            if ok:
                raise SystemExit("flipped event still verifies — refusing to deliver it")
    else:
        tpl = fixture["template"]
        event = nv.sign_event(privkey, {
            "created_at": args.t0 + tpl["created_at_offset_s"],
            "kind": tpl["kind"],
            "tags": tpl["tags"],
            "content": tpl["content"],
        })

    body = json.dumps(event, separators=(",", ":"), sort_keys=True).encode()
    url = args.relay_http.rstrip("/") + "/events"
    status, raw = _post(url, body, _nip98_header(privkey, url, "POST", body))
    receipt = _normalise(status, raw, event["id"])

    (leg_dir / "fixture.json").write_text(fixture_path.read_text())
    (leg_dir / "delivered-event.json").write_text(json.dumps(event, indent=1, sort_keys=True) + "\n")
    (leg_dir / "t0.json").write_text(
        json.dumps({"t0_epoch_s": args.t0, "leg": args.fixture,
                    "signed_by_secret_file": Path(args.secret).name},
                   indent=1, sort_keys=True) + "\n")
    (leg_dir / "delivery.json").write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n")
    print(
        f"deliver({args.fixture}) http={status} accepted={receipt['accepted']} "
        f"id={event['id'][:12]} message={receipt['message'][:80]!r}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
