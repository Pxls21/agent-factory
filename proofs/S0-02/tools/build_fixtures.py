#!/usr/bin/env python3
"""Deterministic builder for the six S0-02 fixtures.

    python3 proofs/S0-02/tools/build_fixtures.py --write      # regenerate in place
    python3 proofs/S0-02/tools/build_fixtures.py --check      # committed == fresh build?

WHAT A FIXTURE IS (and is not)
------------------------------
A fixture is the deterministic SPEC of one leg plus a signed SPECIMEN of the
event that leg delivers:

    {"template": {...},           # kind/tags/content/created_at policy
     "signer":   {...},           # the ROLE the PC runner must sign as
     "event":    {...},           # a signed kind-9 event in the relay-events format
     "expected": {"turns": 0|1, "failure_reason": ..., "mechanism": ...}}

The specimen in ``event`` is signed with a per-fixture FIXTURE key derived from
the committed seed below.  It is NOT any of the four S0-01 identities and is
NOT a credential: the repository holds no private key for owner, agent, relay
or user2 (``proofs/S0-01/fixtures/identities.json`` is pubkey-only), and the
non-member key used against the LIVE relay is generated on the PC at leg time
with its private half never leaving that host.  ``signer.role`` names the key
the PC runner signs the delivered instance with; ``signer.expected_pubkey`` is
the real pubkey that instance must carry (from identities.json), or null for
the non-member role, whose pubkey is recorded in the leg instead.

The specimen exists so the offline preconditions are checkable with no relay:
the bad-signature specimen really fails ``verify_event``; the replayed specimen
really carries the positive specimen's id; the stale specimen's ``created_at``
really sits below the freshness window; the self-authored specimen's sender
really is the agent role.  ``tests/test_s0_02_buzz_authz.py`` runs exactly those.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROOF_DIR = HERE.parent
ROOT = PROOF_DIR.parent.parent
FIXTURE_DIR = PROOF_DIR / "fixtures"
IDENTITIES = ROOT / "proofs" / "S0-01" / "fixtures" / "identities.json"
NOSTR_VERIFY = ROOT / "proofs" / "S0-01" / "tools" / "nostr_verify.py"
DELIVER_EVENT = PROOF_DIR / "tools" / "pc" / "deliver_event.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_nostr_verify():
    """Import the S0-01 signer/verifier BY PATH. Never copied, never vendored."""
    return _load_module("s0_01_nostr_verify", NOSTR_VERIFY)


nv = _load_nostr_verify()
deliver_event = _load_module("s0_02_deliver_event", DELIVER_EVENT)

# --- deterministic constants (change one and --check goes red) ---------------
# A fixed epoch so the committed specimens never drift. It is deliberately in
# the past: the specimen is never delivered, only the run-time instance is.
BASE_CREATED_AT = 1788700000
# The committed specimen-key seed. Labelled, non-secret, and used for nothing
# but signing the specimens in this directory.
SPECIMEN_SEED = "agent-factory/S0-02/specimen-key/v1"
KIND_CHANNEL_MESSAGE = 9
# One signature byte is flipped for neg-bad-signature: the LAST byte, so the
# event id (computed over the fields, not the sig) stays valid and buzz-relay's
# verify_id arm passes before the signature arm fires.
SIG_FLIP_BYTE_INDEX = -1


def _specimen_privkey(fixture_name: str) -> str:
    """A deterministic 64-hex fixture key. Not an identity; not a credential."""
    return hashlib.sha256(f"{SPECIMEN_SEED}/{fixture_name}".encode()).hexdigest()


def _identities() -> dict:
    return json.loads(IDENTITIES.read_text())


# --- the seven legs ----------------------------------------------------------
# created_at_offset_s is applied by the PC runner to the leg's t0. The stale
# offset must clear buzz-relay's +/-900s ingest window (ingest.rs:2224) by a
# wide margin so a slow leg cannot drift the class.
SPECS = (
    {
        "name": "pos-allowed",
        "role": "owner",
        "created_at_offset_s": 0,
        "content": "S0-02 pos-allowed: reply with exactly the single word: pong",
        "turns": 1,
        "failure_reason": None,
    },
    {
        "name": "neg-unauthorized",
        "role": "nonmember",
        "created_at_offset_s": 0,
        "content": "S0-02 neg-unauthorized: reply with exactly the single word: pong",
        "turns": 0,
        "failure_reason": "denied: sender-not-in-allowlist",
    },
    {
        "name": "neg-bad-signature",
        "role": "owner",
        "created_at_offset_s": 0,
        "content": "S0-02 pos-allowed: reply with exactly the single word: pong",
        "turns": 0,
        "failure_reason": "denied: signature-invalid",
        # Built from the positive specimen with one signature byte flipped, so
        # the ONLY difference from a passing event is the signature.
        "derive_from": "pos-allowed",
        "mutate": "flip-signature-byte",
    },
    {
        "name": "neg-replayed",
        "role": "owner",
        "created_at_offset_s": 0,
        "content": "S0-02 pos-allowed: reply with exactly the single word: pong",
        "turns": 0,
        "failure_reason": "denied: event-replayed",
        # The SAME event as the positive leg, delivered a second time.
        "derive_from": "pos-allowed",
        "mutate": "identity",
        "replay_of": "pos-allowed",
    },
    {
        "name": "neg-stale",
        "role": "owner",
        "created_at_offset_s": -86400,
        "content": "S0-02 neg-stale: reply with exactly the single word: pong",
        "turns": 0,
        "failure_reason": "denied: event-stale",
    },
    {
        "name": "neg-self-authored",
        "role": "agent",
        "created_at_offset_s": 0,
        "content": "S0-02 neg-self-authored: reply with exactly the single word: pong",
        "turns": 0,
        "failure_reason": "denied: self-authored",
    },
    {
        # The sixth distinct observable: a channel MEMBER the relay accepts
        # and buzz-acp's author gate drops (lib.rs:389/550). user2 from
        # identities.json is a channel member under respond_to=owner-only.
        "name": "neg-not-allowlisted",
        "role": "user2",
        "created_at_offset_s": 0,
        "content": "S0-02 neg-not-allowlisted: reply with exactly the single word: pong",
        "turns": 0,
        "failure_reason": "denied: not-allowlisted",
    },
    {
        "name": "revoked",
        "role": "owner",
        "created_at_offset_s": 0,
        "content": "S0-02 revoked: reply with exactly the single word: pong",
        "turns": 0,
        "failure_reason": "denied: membership-revoked",
        "requires_membership_removal": True,
    },
)


def _oracle():
    sys.path.insert(0, str(PROOF_DIR / "oracle"))
    import denial_table  # noqa: E402  (path set immediately above)

    return denial_table


def _tags(ids: dict) -> list:
    """The S0-01 relay-events tag shape: h = channel, p = mentioned agent."""
    return [["h", ids["channel"]], ["p", ids["agent"]]]


def build_one(spec: dict, ids: dict, built: dict) -> dict:
    d = _oracle()
    row = d.row(spec["name"])
    derive = spec.get("derive_from")
    if derive is not None:
        event = copy.deepcopy(built[derive]["event"])
        if spec["mutate"] == "flip-signature-byte":
            sig = bytearray.fromhex(event["sig"])
            sig[SIG_FLIP_BYTE_INDEX] ^= 0x01
            event["sig"] = sig.hex()
            ok, _reason = nv.verify_event(event)
            if ok:
                raise SystemExit("neg-bad-signature specimen still verifies — build aborted")
        elif spec["mutate"] != "identity":
            raise SystemExit(f"unknown mutate {spec['mutate']!r}")
    else:
        event = nv.sign_event(
            _specimen_privkey(spec["name"]),
            {
                "created_at": BASE_CREATED_AT + spec["created_at_offset_s"],
                "kind": KIND_CHANNEL_MESSAGE,
                "tags": _tags(ids),
                "content": spec["content"],
            },
        )

    expected_pubkey = ids.get(spec["role"]) if spec["role"] in ids else None
    fixture = {
        "fixture": spec["name"],
        "buzz_commit": d.BUZZ_COMMIT,
        "template": {
            "kind": KIND_CHANNEL_MESSAGE,
            "tags": _tags(ids),
            "content": spec["content"],
            "created_at_offset_s": spec["created_at_offset_s"],
            "specimen_created_at": BASE_CREATED_AT + spec["created_at_offset_s"],
        },
        "signer": {
            "role": spec["role"],
            "expected_pubkey": expected_pubkey,
            "specimen_pubkey": event["pubkey"],
            "note": (
                "The PC runner signs the delivered instance with the role key from "
                "the host secret store; specimen_pubkey belongs to the committed "
                "fixture key and is never delivered."
            ),
        },
        "event": event,
        "expected": {
            "turns": spec["turns"],
            "failure_reason": spec["failure_reason"],
            "mechanism": f"{row['src']}:{row['line']}",
            "decided_by": row["decided_by"],
            "evidence": row["evidence"],
            "observable": row["observable"],
        },
    }
    if "replay_of" in spec:
        fixture["replay_of"] = spec["replay_of"]
        fixture["expected"]["replay_of_event_id"] = built[spec["replay_of"]]["event"]["id"]
    if spec.get("requires_membership_removal"):
        fixture["requires_membership_removal"] = True
    if row.get("discrepancy"):
        fixture["expected"]["discrepancy"] = row["discrepancy"]
    return fixture


def build_all(ids: dict | None = None) -> dict:
    ids = ids if ids is not None else _identities()
    built: dict = {}
    for spec in SPECS:
        built[spec["name"]] = build_one(spec, ids, built)
    return built


def _serialise(fixture: dict) -> str:
    return json.dumps(fixture, indent=1, sort_keys=True) + "\n"


# --- synthetic evidence bundles ---------------------------------------------
# These are SYNTHETIC. They exercise the checker's structure and its
# distinctness gate; they do NOT exercise buzz-acp or buzz-relay. The real
# proof is the PC legs (proofs/S0-02/tools/pc/run_s0_02_legs.sh), NOT run here.
#
# They exist because a fully-valid bundle needs a signature under the owner and
# agent pubkeys, and the repository holds no private key for either
# (identities.json is pubkey-only). Rather than weaken the checker's identity
# binding so a keyless bundle can pass, the bundle carries its own anchors and
# the checker is pointed at them with the closed --synthetic-root parameter that
# spec.json pins.
BUNDLE_T0 = 1788800000
CHANNEL_UUID_KEY = "channel"
SESSION_ID = "5f1c9d2a-0e63-4f7b-9c21-6a8d4e0b7c35"


def _bundle_privkey(bundle: str, role: str) -> str:
    return hashlib.sha256(f"{SPECIMEN_SEED}/bundle/{bundle}/{role}".encode()).hexdigest()


def _bundle_identities(bundle: str) -> dict:
    base = _identities()
    ids = dict(base)
    for role in ("owner", "agent", "relay", "user2"):
        priv = _bundle_privkey(bundle, role)
        ev = nv.sign_event(priv, {"created_at": BUNDLE_T0, "kind": 1, "tags": [], "content": role})
        ids[role] = ev["pubkey"]
    return ids


def _iso(offset_ms: int) -> str:
    import datetime

    dt = datetime.datetime.fromtimestamp(BUNDLE_T0, datetime.timezone.utc)
    dt += datetime.timedelta(milliseconds=offset_ms)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


def _timeline(with_turn: bool, prompt_text: str) -> str:
    """S0-01-shaped frames. Modelled on the real capture
    (/root/s0-01-realleg/golden/run-1/timeline.jsonl): initialize + result
    always; session/new, session/prompt, an agent_message_chunk and a
    stopReason terminal only when a turn happened."""
    frames = [
        ("c2a", {"id": 0, "jsonrpc": "2.0", "method": "initialize",
                 "params": {"clientInfo": {"name": "buzz-acp", "version": "0.1.0"},
                            "protocolVersion": 2}}),
        ("a2c", {"jsonrpc": "2.0", "id": 0,
                 "result": {"agentInfo": {"name": "hermes-agent", "version": "0.21.0"},
                            "protocolVersion": 1}}),
    ]
    if with_turn:
        frames += [
            ("c2a", {"id": 1, "jsonrpc": "2.0", "method": "session/new",
                     "params": {"cwd": "/home/rocco", "mcpServers": []}}),
            ("a2c", {"jsonrpc": "2.0", "id": 1, "result": {"sessionId": SESSION_ID}}),
            ("c2a", {"id": 2, "jsonrpc": "2.0", "method": "session/prompt",
                     "params": {"prompt": [{"text": prompt_text, "type": "text"}],
                                "sessionId": SESSION_ID}}),
            ("a2c", {"jsonrpc": "2.0", "method": "session/update",
                     "params": {"sessionId": SESSION_ID,
                                "update": {"content": {"text": "pong", "type": "text"},
                                           "sessionUpdate": "agent_message_chunk"}}}),
            ("a2c", {"jsonrpc": "2.0", "id": 2, "result": {"stopReason": "end_turn"}}),
        ]
    lines = []
    for i, (direction, frame) in enumerate(frames, 1):
        lines.append(json.dumps({
            "seq": i, "dir": direction, "t_utc": _iso(i * 100),
            "t_mono_ns": 4689461162919584 + i * 100_000_000, "frame": frame,
        }, sort_keys=True))
    return "\n".join(lines) + "\n"


def _log(extra_lines) -> str:
    """A masked buzz-acp log. The canary line is what buzz-acp emits at DEBUG on
    every startup (crates/buzz-acp/src/relay.rs:1716); without it an absent
    observable would prove nothing, so the checker requires it."""
    head = [
        "2026-09-08T00:00:00.100000Z  INFO buzz_acp: buzz-acp starting: relay=ws://127.0.0.1:3999 "
        "pubkey=<HEX> idle_timeout=900s max_turn=3600s agents=1 session_policy=thread "
        "ignore_self=true respond_to=owner-only",
        f"2026-09-08T00:00:00.200000Z DEBUG buzz_acp::relay: startup watermark set to {BUNDLE_T0}",
        "2026-09-08T00:00:00.300000Z  INFO buzz_acp: agent_pool_ready agents=1",
    ]
    return "\n".join(head + list(extra_lines)) + "\n"


def _raw_delivery_response(*, accepted: bool, event_id: str, message: str) -> str:
    if accepted:
        return json.dumps({"event_id": event_id, "accepted": True, "message": message})
    return json.dumps({"error": message})


def _write_leg(leg_dir: Path, fixture: dict, ids: dict, bundle: str, *,
               accepted: bool, message: str, with_turn: bool, log_extra,
               membership: dict | None = None):
    leg_dir.mkdir(parents=True, exist_ok=True)
    role = fixture["signer"]["role"]
    priv = _bundle_privkey(bundle, role)
    created_at = BUNDLE_T0 + fixture["template"]["created_at_offset_s"]
    delivered = nv.sign_event(priv, {
        "created_at": created_at,
        "kind": fixture["template"]["kind"],
        "tags": fixture["template"]["tags"],
        "content": fixture["template"]["content"],
    })
    (leg_dir / "fixture.json").write_text(_serialise(fixture))
    (leg_dir / "delivered-event.json").write_text(
        json.dumps(delivered, indent=1, sort_keys=True) + "\n")
    (leg_dir / "t0.json").write_text(
        json.dumps({"t0_epoch_s": BUNDLE_T0, "leg": fixture["fixture"]},
                   indent=1, sort_keys=True) + "\n")
    # F14: build the synthetic receipt through the real producer normaliser so
    # its exact key set and 200/400 response semantics cannot drift.
    http_status = 200 if accepted else 400
    raw = _raw_delivery_response(
        accepted=accepted,
        event_id=delivered["id"],
        message=message,
    )
    receipt = deliver_event._normalise(http_status, raw, delivered["id"])
    (leg_dir / "delivery.json").write_text(
        json.dumps(receipt, indent=1, sort_keys=True) + "\n"
    )
    (leg_dir / "timeline.jsonl").write_text(
        _timeline(with_turn, fixture["template"]["content"]))
    (leg_dir / "buzzacp.log").write_text(_log(log_extra))
    if membership is not None:
        (leg_dir / "membership.json").write_text(
            json.dumps(membership, indent=1, sort_keys=True) + "\n")
    return delivered


BLANKET_MESSAGE = "restricted: not a channel member"


def _tamper(leg_dir: Path, pos_delivered: dict) -> None:
    bad = json.loads(json.dumps(pos_delivered))
    sig = bytearray.fromhex(bad["sig"])
    sig[SIG_FLIP_BYTE_INDEX] ^= 0x01
    bad["sig"] = sig.hex()
    ok, _reason = nv.verify_event(bad)
    if ok:
        raise SystemExit("bundle neg-bad-signature leg still verifies — build aborted")
    (leg_dir / "delivered-event.json").write_text(
        json.dumps(bad, indent=1, sort_keys=True) + "\n")
    delivery = json.loads((leg_dir / "delivery.json").read_text())
    delivery["event_id"] = bad["id"]
    (leg_dir / "delivery.json").write_text(
        json.dumps(delivery, indent=1, sort_keys=True) + "\n")


def build_bundle(bundle: str, root: Path) -> None:
    """bundle == 'pass'    -> six distinct observables, checker exits 0.
       bundle == 'blanket' -> one shared observable, checker exits 1."""
    ids = _bundle_identities(bundle)
    fixtures = build_all(ids)
    if root.exists():
        import shutil

        shutil.rmtree(root)
    (root / "fixtures").mkdir(parents=True)
    (root / "identities.json").write_text(json.dumps(ids, indent=1, sort_keys=True) + "\n")
    for name, fixture in fixtures.items():
        (root / "fixtures" / f"{name}.json").write_text(_serialise(fixture))
    legs = root / "legs"
    chan = ids[CHANNEL_UUID_KEY]
    dup_line = (
        "2026-09-08T00:00:05.000000Z DEBUG buzz_acp::relay: "
        f"dropping duplicate event for channel {chan}"
    )
    self_line = (
        "2026-09-08T00:00:05.000000Z DEBUG buzz_acp: "
        f"dropping self-authored event channel_id={chan}"
    )
    blanket = bundle == "blanket"

    def leg(name):
        return legs / name

    pos_delivered = _write_leg(leg("pos-allowed"), fixtures["pos-allowed"], ids, bundle,
                               accepted=True, message="", with_turn=True, log_extra=[])
    _write_leg(leg("neg-unauthorized"), fixtures["neg-unauthorized"], ids, bundle,
               accepted=False, message=BLANKET_MESSAGE, with_turn=False, log_extra=[])
    _write_leg(leg("neg-bad-signature"), fixtures["neg-bad-signature"], ids, bundle,
               accepted=False,
               message=BLANKET_MESSAGE if blanket else "invalid: invalid schnorr signature",
               with_turn=False, log_extra=[])
    # The bad-signature leg delivers the POSITIVE event with one signature byte
    # flipped: the only difference from a passing event is the signature, which
    # is what makes the leg name its own reason and nothing else.
    _tamper(leg("neg-bad-signature"), pos_delivered)
    _write_leg(leg("neg-replayed") / "first", fixtures["pos-allowed"], ids, bundle,
               accepted=True, message="", with_turn=True, log_extra=[])
    _write_leg(leg("neg-replayed") / "second", fixtures["neg-replayed"], ids, bundle,
               accepted=True,
               message=BLANKET_MESSAGE if blanket else "",
               with_turn=False, log_extra=[] if blanket else [dup_line])
    _write_leg(leg("neg-stale"), fixtures["neg-stale"], ids, bundle,
               accepted=False,
               message=BLANKET_MESSAGE if blanket
               else "invalid: event timestamp too far from server time",
               with_turn=False, log_extra=[])
    _write_leg(leg("neg-self-authored"), fixtures["neg-self-authored"], ids, bundle,
               accepted=True,
               message=BLANKET_MESSAGE if blanket else "",
               with_turn=False, log_extra=[] if blanket else [self_line])
    # The neg-not-allowlisted leg: user2 is a channel member the relay accepts;
    # buzz-acp's author gate drops (lib.rs:550). The observable is the DEBUG
    # "inbound author gate" line.
    gate_line = (
        "2026-09-08T00:00:05.000000Z DEBUG buzz_acp::relay: "
        "inbound author gate \xe2\x80\x94 dropping event"
    )
    _write_leg(leg("neg-not-allowlisted"), fixtures["neg-not-allowlisted"], ids, bundle,
               accepted=True,
               message=BLANKET_MESSAGE if blanket else "",
               with_turn=False, log_extra=[] if blanket else [gate_line])
    revoked = _write_leg(leg("revoked"), fixtures["revoked"], ids, bundle,
                         accepted=False, message=BLANKET_MESSAGE, with_turn=False,
                         log_extra=[], membership={"removed": True, "removed_pubkey": None})
    (leg("revoked") / "membership.json").write_text(json.dumps({
        "removed": True, "removed_pubkey": revoked["pubkey"],
        "channel": ids[CHANNEL_UUID_KEY], "at_epoch_s": BUNDLE_T0 - 60,
        "http_status": 200,
    }, indent=1, sort_keys=True) + "\n")
    # The replayed leg is one event delivered twice: rewrite the second delivery
    # so both sub-legs carry the SAME id, which is what makes it a replay.
    first = json.loads((leg("neg-replayed") / "first" / "delivered-event.json").read_text())
    second_dir = leg("neg-replayed") / "second"
    (second_dir / "delivered-event.json").write_text(
        json.dumps(first, indent=1, sort_keys=True) + "\n")
    delivery = json.loads((second_dir / "delivery.json").read_text())
    delivery["event_id"] = first["id"]
    (second_dir / "delivery.json").write_text(
        json.dumps(delivery, indent=1, sort_keys=True) + "\n")


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--bundles", action="store_true",
                   help="regenerate the two committed SYNTHETIC evidence bundles")
    args = ap.parse_args(argv[1:])

    if args.bundles:
        for bundle, name in (("pass", "evidence-pass"), ("blanket", "evidence-blanket")):
            build_bundle(bundle, FIXTURE_DIR / name)
            print(f"wrote synthetic bundle {FIXTURE_DIR / name}")
        return 0

    built = build_all()
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    drift = []
    for name, fixture in built.items():
        path = FIXTURE_DIR / f"{name}.json"
        text = _serialise(fixture)
        if args.write:
            path.write_text(text)
        else:
            if not path.exists():
                drift.append(f"{name}: absent")
            elif path.read_text() != text:
                drift.append(f"{name}: committed bytes differ from a fresh build")
    if args.write:
        print(f"wrote {len(built)} fixtures to {FIXTURE_DIR}")
        return 0
    if drift:
        for line in drift:
            print(f"fixture-drift: {line}")
        return 1
    print(f"fixture-drift: none ({len(built)} fixtures match a fresh build)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
