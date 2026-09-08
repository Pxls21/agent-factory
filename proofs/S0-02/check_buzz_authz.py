#!/usr/bin/env python3
"""S0-02 checker — Buzz authorization and freshness over captured legs.

    python3 proofs/S0-02/check_buzz_authz.py <evidence-root>

Exit codes: 0 PASS / 1 ``failure_reason: <reason>`` / 2 ``deferred: <reason>``.

DEFERRAL RULE (S0-01's, deliberately): exit 2 iff the root is absent or NO leg
directory carries ``timeline.jsonl``.  Once ANY leg carries a timeline, every
later absence is a Failure, never a deferral — a half-captured bundle must not
read as "not captured yet".

The proof this checker gates (seed:362-381):
  1. an allowed fresh signed event produces exactly one ACP session/turn;
  2. membership removal revokes access independent of NIP-OA ``created_at``;
  3. duplicate delivery does not duplicate a completed turn.
Plus the seed's negative-control rule: FOUR DISTINCT reasons are required and
"one blanket rejection fails the proof".  Six are asserted here (docs/03
§1 acceptance test 2 adds self-authored; neg-not-allowlisted adds the sixth
buzz-acp-decided reason); the distinctness gate is what turns that rule into a
gate — six legs whose observables collapse to fewer than six keys fail with
``blanket-rejection:``.

Every observable comes from ``oracle/denial_table.py``, which is pinned to the
upstream sources by ``tests/test_s0_02_buzz_authz.py``.  The checker never
decides what an observable IS; it only looks for the one the oracle names.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
S0_01_CHECKER = ROOT / "proofs" / "S0-01" / "check_acp_conformance.py"
NOSTR_VERIFY = ROOT / "proofs" / "S0-01" / "tools" / "nostr_verify.py"
IDENTITIES = ROOT / "proofs" / "S0-01" / "fixtures" / "identities.json"

sys.path.insert(0, str(HERE / "oracle"))
import denial_table as oracle  # noqa: E402

# The two anchors a bundle is judged against: the identity set that says which
# pubkey is "the owner"/"the agent", and the committed fixture set each leg's
# fixture.json must equal. Production legs use the repo's real anchors.
#
# --synthetic-root names ONE directory carrying BOTH (identities.json +
# fixtures/) so a committed SYNTHETIC bundle can be graded end to end. It is a
# closed parameter, not a config channel: it can only be set on the command
# line, spec.json pins that command line verbatim, and validate-ledger binds
# every recorded run to the attested spec's cmd (scripts/validate-ledger:275-306)
# — a bundle cannot select its own anchors.
DEFAULT_IDENTITIES = IDENTITIES
DEFAULT_FIXTURES = HERE / "fixtures"

# The identity keys to select from identities.json — positive selection (F21).
IDENTITY_ROLES = ("owner", "agent", "relay", "user2")


class Anchors:
    def __init__(self, identities_path: Path, fixtures_dir: Path, synthetic: bool):
        self.identities_path = identities_path
        self.fixtures_dir = fixtures_dir
        self.synthetic = synthetic

    @classmethod
    def default(cls):
        return cls(DEFAULT_IDENTITIES, DEFAULT_FIXTURES, False)

    @classmethod
    def from_synthetic_root(cls, root: Path):
        return cls(root / "identities.json", root / "fixtures", True)


def _load_by_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# REUSED, never copied: the S0-01 timeline reader, its S_ISREG guards, its
# NaN/blank-line rejection, its masking regex, its wall-clock cap, and its
# Failure/Deferred types.
s0_01 = _load_by_path("s0_01_check_acp_conformance", S0_01_CHECKER)
nv = _load_by_path("s0_01_nostr_verify", NOSTR_VERIFY)

Failure = s0_01.Failure
Deferred = s0_01.Deferred
_require_file = s0_01._require_file
_require_dir = s0_01._require_dir
_load_timeline_raw = s0_01._load_timeline_raw
_HEX64 = s0_01._HEX64_ANYWHERE_RE
_check_with_timeout = s0_01._check_with_timeout

# buzz-relay refuses any event whose created_at is more than this far from
# server time (MAX_TIMESTAMP_DRIFT_SECS, crates/buzz-relay/src/handlers/ingest.rs:2224).
RELAY_DRIFT_WINDOW_S = 900
# Slack between the leg's recorded t0 and the runner's signing clock. Small on
# purpose: it must never be wide enough to let a stale event read as fresh.
LEG_CLOCK_TOLERANCE_S = 120
# Replay reuses an event after one complete turn wait. This wider tolerance is
# confined to that second sub-leg; every ordinary leg keeps the tight bound.
REPLAY_CLOCK_TOLERANCE_S = 150
# buzz-acp emits this at DEBUG on every startup (crates/buzz-acp/src/relay.rs:1716).
# A leg whose log lacks it was not captured at RUST_LOG=debug, so an absent
# buzz-acp observable would prove nothing. Assert the instrument fired.
# The canary is LEVEL-AWARE (F9): only a line carrying a DEBUG level token
# satisfies the claim "captured at RUST_LOG=debug".
DEBUG_LEVEL_CANARY = "startup watermark set to"

LEG_NAMES = ("pos-allowed",) + oracle.NEGATIVE_FIXTURES
REPLAY_SUBLEGS = ("first", "second")


def _read_json(path: Path, leg: str, name: str):
    _require_file(path, leg, name)
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise Failure(f"{leg}: {name} is not valid JSON ({exc})")


def _prompt_frames(entries, leg):
    """c2a session/prompt and session/new frames, from the S0-01 timeline shape."""
    prompts, news = [], []
    for e in entries:
        if e.get("dir") != "c2a":
            continue
        frame = e.get("frame") or {}
        method = frame.get("method")
        if method == "session/prompt":
            prompts.append(frame)
        elif method == "session/new":
            news.append(frame)
    return prompts, news


def _prompt_text(frame) -> str:
    """Flatten a session/prompt params blob to text. Shape-tolerant by design:
    the nonce check must not depend on which content block carries it."""
    return json.dumps(frame.get("params", {}), sort_keys=True)


def _check_masking(log_text: str, leg: str):
    if _HEX64.search(log_text):
        raise Failure(f"{leg}: buzzacp.log contains unmasked 64-hex string")


def _check_delivered_event(leg_dir: Path, leg: str, fixture: dict, identities: dict) -> dict:
    """The delivered instance is a real signed event that matches the fixture."""
    delivered = _read_json(leg_dir / "delivered-event.json", leg, "delivered-event.json")
    for key in ("id", "pubkey", "sig", "kind", "tags", "content", "created_at"):
        if key not in delivered:
            raise Failure(f"{leg}: delivered-event.json missing {key!r}")

    computed = nv.event_id(delivered)
    if computed != delivered["id"]:
        raise Failure(
            f"{leg}: delivered event id {delivered['id'][:12]} does not match the "
            f"id computed from its fields ({computed[:12]})"
        )

    ok, reason = nv.verify_event(delivered)
    want_valid = fixture["fixture"] != "neg-bad-signature"
    if want_valid and not ok:
        raise Failure(f"{leg}: delivered event failed signature verification ({reason})")
    if not want_valid and ok:
        raise Failure(f"{leg}: delivered event verifies, but this leg must carry an invalid signature")

    tpl = fixture["template"]
    if delivered["kind"] != tpl["kind"]:
        raise Failure(f"{leg}: delivered kind {delivered['kind']} != fixture kind {tpl['kind']}")
    if delivered["tags"] != tpl["tags"]:
        raise Failure(f"{leg}: delivered tags do not match the fixture's")
    if delivered["content"] != tpl["content"]:
        raise Failure(f"{leg}: delivered content does not match the fixture's")

    role = fixture["signer"]["role"]
    expected_pubkey = fixture["signer"]["expected_pubkey"]
    if expected_pubkey is not None:
        if delivered["pubkey"] != expected_pubkey:
            raise Failure(
                f"{leg}: delivered sender is not the {role} identity "
                f"({delivered['pubkey'][:12]} != {expected_pubkey[:12]})"
            )
    else:
        # F21: positive selection of identity keys, not a denylist.
        known = {identities[k] for k in IDENTITY_ROLES if k in identities}
        if delivered["pubkey"] in known:
            raise Failure(
                f"{leg}: the {role} sender must not be one of the known S0-01 identities"
            )
    if delivered["pubkey"] == fixture["signer"]["specimen_pubkey"]:
        raise Failure(
            f"{leg}: the committed specimen key was delivered — the leg must be signed "
            f"with the {role} key on the host, not with the fixture key"
        )
    return delivered


def _check_freshness(leg_dir: Path, leg: str, fixture: dict, delivered: dict):
    """created_at must satisfy the fixture's policy relative to the leg's own t0.

    This is the assertion that makes the stale leg mean something: it is not
    "the offset was configured", it is "the delivered event really was older
    than the relay's window at delivery time".
    """
    t0_blob = _read_json(leg_dir / "t0.json", leg, "t0.json")
    t0 = t0_blob.get("t0_epoch_s")
    if type(t0) is not int:
        raise Failure(f"{leg}: t0.json t0_epoch_s is not an int")
    offset = fixture["template"]["created_at_offset_s"]
    tolerance = (REPLAY_CLOCK_TOLERANCE_S
                 if leg == "neg-replayed/second" else LEG_CLOCK_TOLERANCE_S)
    age = t0 - delivered["created_at"]
    if offset < 0:
        # F12: prove both parts independently. Check the relay window first so
        # an event that is actually fresh is named as such; then bind the stale
        # specimen to its declared offset to reject a far-future t0.
        if age <= RELAY_DRIFT_WINDOW_S:
            raise Failure(
                f"{leg}: delivered event is {age}s old at t0, inside the relay's "
                f"{RELAY_DRIFT_WINDOW_S}s window — it is not stale"
            )
        if abs(age - (-offset)) > tolerance:
            raise Failure(
                f"{leg}: delivered created_at is {age}s from t0, outside the "
                f"{tolerance}s tolerance for offset {offset}"
            )
    else:
        if abs(age - (-offset)) > tolerance:
            raise Failure(
                f"{leg}: delivered created_at is {age}s from t0, outside the "
                f"{tolerance}s tolerance for offset {offset}"
            )
        if abs(age) >= RELAY_DRIFT_WINDOW_S:
            raise Failure(
                f"{leg}: delivered event is {age}s from t0 — a leg that must be FRESH "
                f"cannot sit at or beyond the relay's {RELAY_DRIFT_WINDOW_S}s window"
            )


def _check_delivery(
    leg_dir: Path,
    leg: str,
    delivered: dict,
    fixture: dict,
    expected_accepted: "bool | None" = None,
) -> dict:
    delivery = _read_json(leg_dir / "delivery.json", leg, "delivery.json")
    expected_keys = {"http_status", "event_id", "accepted", "message", "event_id_echoed"}
    if set(delivery) != expected_keys:
        missing = sorted(expected_keys - set(delivery))
        extra = sorted(set(delivery) - expected_keys)
        raise Failure(
            f"{leg}: delivery.json has the wrong producer shape "
            f"(missing={missing}, extra={extra})"
        )
    if delivery["event_id"] != delivered["id"]:
        raise Failure(
            f"{leg}: delivery.json event_id {str(delivery['event_id'])[:12]} != the "
            f"delivered event id {delivered['id'][:12]}"
        )
    accepted = delivery["accepted"]
    if type(accepted) is not bool:
        raise Failure(f"{leg}: delivery.json accepted is not a bool")
    if expected_accepted is None:
        expected_accepted = (
            fixture["expected"]["evidence"] == oracle.EV_BUZZACP_LOG
            or leg == "pos-allowed"
        )
    if accepted is not expected_accepted:
        if expected_accepted:
            raise Failure(
                f"{leg}: buzz-acp decides this leg, so the relay must have ACCEPTED the "
                f"event (delivery.json accepted=true), got {accepted!r}"
            )
        raise Failure(
            f"{leg}: the relay decides this leg, so delivery.json accepted must be "
            f"false, got {accepted!r}"
        )
    # F14: grade the producer's actual HTTP contract. Accepted publish responses
    # are 200 (bridge.rs:964-968); relay-decided refusals are 400
    # (api_error, bridge.rs:985).
    expected_status = 200 if expected_accepted else 400
    status = delivery["http_status"]
    if type(status) is not int:
        raise Failure(f"{leg}: delivery.json http_status is not an int")
    if status != expected_status:
        raise Failure(
            f"{leg}: delivery.json http_status must be {expected_status} for "
            f"accepted={str(expected_accepted).lower()}, got {status!r}"
        )
    event_id_echoed = delivery["event_id_echoed"]
    if type(event_id_echoed) is not bool:
        raise Failure(f"{leg}: delivery.json event_id_echoed is not a bool")
    if expected_accepted and not event_id_echoed:
        raise Failure(
            f"{leg}: delivery.json event_id_echoed must be true for an accepted response"
        )
    if not expected_accepted and event_id_echoed:
        raise Failure(
            f"{leg}: delivery.json event_id_echoed must be false for a relay rejection"
        )
    return delivery


# Every observable any row names, searched in BOTH channels. The scan reports
# what a leg ACTUALLY shows; it never assumes the leg shows its own reason.
ALL_OBSERVABLES = tuple(sorted({r["observable"] for r in oracle.ROWS if r["leg"] == "negative"}))


def _observe_all(leg_dir: Path, leg: str, delivery: dict, fixture_name: str) -> frozenset:
    """The set of oracle observables this leg's evidence actually carries.

    An OBSERVATION, not an assertion. Writing this as "assert the oracle's text
    is present" would make the distinctness gate a tautology — every leg would
    return its own key by construction and five legs could never collapse. The
    blanket-rejection case is exactly the case where each leg carries some OTHER
    leg's text (or one shared text), so the scan has to be able to see that.
    """
    message = str(delivery.get("message", ""))
    # F13: guard the log read through _require_file (was unguarded at :351).
    log_path = _require_file(leg_dir / "buzzacp.log", leg, "buzzacp.log")
    log_text = log_path.read_text()
    _check_masking(log_text, leg)
    # F9b: the DEBUG canary is demanded only for legs whose oracle row says
    # evidence == EV_BUZZACP_LOG. Relay-decided legs need no buzz-acp log
    # evidence — their observable is in the delivery receipt.
    row = oracle.row(fixture_name)
    if row["evidence"] == oracle.EV_BUZZACP_LOG:
        # F9: the canary must appear on a line carrying a DEBUG level token.
        if not any(re.search(r"\bDEBUG\b", ln) and DEBUG_LEVEL_CANARY in ln
                   for ln in log_text.splitlines()):
            raise Failure(
                f"{leg}: buzzacp.log lacks the debug-level canary {DEBUG_LEVEL_CANARY!r} "
                f"on a DEBUG line — the leg was not captured at RUST_LOG=debug, so an "
                f"absent buzz-acp observable would prove nothing"
            )
    found = set()
    for text in ALL_OBSERVABLES:
        if text in message:
            found.add(f"{oracle.EV_DELIVERY}::{text}")
        if text in log_text:
            found.add(f"{oracle.EV_BUZZACP_LOG}::{text}")
    if not found:
        raise Failure(
            f"{leg}: neither delivery.json nor buzzacp.log carries ANY known denial "
            f"observable — the leg produced no turn and no named reason"
        )
    return frozenset(found)


def _observed_key(found: frozenset) -> str:
    """The distinctness key: everything the leg shows, order-independent."""
    return "|".join(sorted(found))


def _check_named_observable(leg: str, fixture_name: str, found: frozenset, delivery: dict):
    """The leg fired for ITS OWN named reason, in the channel the oracle names."""
    row = oracle.row(fixture_name)
    want = f"{row['evidence']}::{row['observable']}"
    if want not in found:
        raise Failure(
            f"{leg}: evidence does not carry the oracle observable {row['observable']!r} "
            f"in the {row['evidence']} channel (found {sorted(found)}); "
            f"mechanism {row['src']}:{row['line']}"
        )
    if len(found) != 1:
        raise Failure(
            f"{leg}: evidence carries {len(found)} denial observables, expected exactly "
            f"the named one {want!r} (found {sorted(found)})"
        )
    # F10: reject wrong-channel observables. The oracle names the channel where
    # this leg's observable CAN be produced; finding it in the wrong channel is
    # not evidence of the named mechanism.
    for chan_text in found:
        chan, text = chan_text.split("::", 1)
        # Find which oracle row(s) can produce this text.
        matching_rows = [r for r in oracle.ROWS if r["observable"] == text and r["leg"] == "negative"]
        if matching_rows:
            expected_channels = {r["evidence"] for r in matching_rows}
            if chan not in expected_channels:
                raise Failure(
                    f"{leg}: {text!r} appears in the {chan} channel, but the oracle says "
                    f"it can only be produced in {sorted(expected_channels)}"
                )
    if row["evidence"] == oracle.EV_DELIVERY:
        if delivery.get("accepted") is not False:
            raise Failure(
                f"{leg}: the relay decides this leg, so delivery.json accepted must be "
                f"false, got {delivery.get('accepted')!r}"
            )


def _turns(leg_dir: Path, leg: str):
    entries = _load_timeline_raw(leg_dir, leg)
    prompts, news = _prompt_frames(entries, leg)
    return entries, prompts, news


def _check_leg(leg_dir: Path, leg: str, fixture_name: str, identities: dict, anchors: "Anchors"):
    """One captured leg. Returns the observed distinctness key (None for the positive)."""
    _require_dir(leg_dir, leg, f"{fixture_name} leg directory")
    fixture = _read_json(leg_dir / "fixture.json", leg, "fixture.json")
    if fixture.get("fixture") != fixture_name:
        raise Failure(
            f"{leg}: fixture.json names {fixture.get('fixture')!r}, expected {fixture_name!r}"
        )
    committed = _read_json(anchors.fixtures_dir / f"{fixture_name}.json", leg, "committed fixture")
    if fixture != committed:
        raise Failure(
            f"{leg}: fixture.json differs from the committed "
            f"{anchors.fixtures_dir}/{fixture_name}.json"
        )

    delivered = _check_delivered_event(leg_dir, leg, fixture, identities)
    _check_freshness(leg_dir, leg, fixture, delivered)
    delivery = _check_delivery(leg_dir, leg, delivered, fixture)

    _entries, prompts, news = _turns(leg_dir, leg)
    want_turns = fixture["expected"]["turns"]
    if len(prompts) != want_turns:
        raise Failure(
            f"{leg}: {len(prompts)} ACP session/prompt turn(s), expected {want_turns}"
        )

    if want_turns:
        if len(news) != 1:
            raise Failure(f"{leg}: {len(news)} session/new frame(s), expected exactly 1")
        nonce = fixture["template"]["content"]
        # F19: the nonce must sit on a JSON string boundary, not as a substring
        # of a longer token.
        blob = _prompt_text(prompts[0])
        if f'"{nonce}"' not in blob and not re.search(
            rf'(?<![\w-]){re.escape(nonce)}(?![\w-])', blob
        ):
            raise Failure(f"{leg}: the ACP turn does not carry the fixture's nonce")
        log_path = _require_file(leg_dir / "buzzacp.log", leg, "buzzacp.log")
        _check_masking(log_path.read_text(), leg)
        return None

    found = _observe_all(leg_dir, leg, delivery, fixture_name)
    if fixture_name == "neg-self-authored":
        # F13: use _require_file instead of bare read_text (was unguarded).
        log_text = _require_file(leg_dir / "buzzacp.log", leg, "buzzacp.log").read_text()
        if "ignore_self=true" not in log_text:
            raise Failure(
                f"{leg}: buzzacp.log does not show ignore_self=true — the self-authored "
                f"drop arm (crates/buzz-acp/src/lib.rs:3257) is not live in this run"
            )
    if fixture_name == "revoked":
        membership = _read_json(leg_dir / "membership.json", leg, "membership.json")
        if membership.get("removed_pubkey") != delivered["pubkey"]:
            raise Failure(
                f"{leg}: membership.json removed_pubkey does not match the delivered sender"
            )
        if membership.get("removed") is not True:
            raise Failure(f"{leg}: membership.json does not record a completed removal")
        # F3: the removal must precede the delivery.
        at = membership.get("at_epoch_s")
        if type(at) is not int:
            raise Failure(f"{leg}: membership.json at_epoch_s is not an int")
        t0_blob = _read_json(leg_dir / "t0.json", leg, "t0.json (for removal ordering)")
        t0 = t0_blob.get("t0_epoch_s")
        if type(t0) is not int:
            raise Failure(f"{leg}: t0.json t0_epoch_s is not an int")
        if at >= t0:
            raise Failure(
                f"{leg}: the removal is recorded at {at}, at or after the delivery t0 "
                f"{t0} — this cannot prove removal revoked access"
            )
        # F3: the removal must concern this channel.
        h_tags = [t[1] for t in delivered["tags"] if t and t[0] == "h"]
        if membership.get("channel") not in h_tags:
            raise Failure(
                f"{leg}: membership.json channel {membership.get('channel')!r} is not the "
                f"delivered event's channel {h_tags}"
            )
        # F3: the removal must record a successful relay response.
        http_st = membership.get("http_status")
        if type(http_st) is not int or not (200 <= http_st < 300):
            raise Failure(
                f"{leg}: membership.json records no successful relay removal response "
                f"(http_status={http_st!r})"
            )
    return found, delivery


def _check_replay(root: Path, identities: dict, anchors: "Anchors"):
    """The replayed leg is two deliveries of ONE event id in one directory.

    The proof is comparative: the FIRST delivery produced a turn and the SECOND
    produced none. A leg where neither produced a turn proves nothing.
    """
    leg_dir = root / "neg-replayed"
    _require_dir(leg_dir, "neg-replayed", "neg-replayed leg directory")
    ids = []
    turns = []
    key = None
    for sub in REPLAY_SUBLEGS:
        sub_dir = leg_dir / sub
        leg = f"neg-replayed/{sub}"
        _require_dir(sub_dir, leg, f"{sub} sub-leg directory")
        fixture_name = "pos-allowed" if sub == "first" else "neg-replayed"
        fixture = _read_json(sub_dir / "fixture.json", leg, "fixture.json")
        if fixture.get("fixture") != fixture_name:
            raise Failure(
                f"{leg}: fixture.json names {fixture.get('fixture')!r}, expected {fixture_name!r}"
            )
        committed = _read_json(
            anchors.fixtures_dir / f"{fixture_name}.json", leg, "committed fixture"
        )
        if fixture != committed:
            raise Failure(
                f"{leg}: fixture.json differs from the committed "
                f"{anchors.fixtures_dir}/{fixture_name}.json"
            )
        delivered = _check_delivered_event(sub_dir, leg, fixture, identities)
        _check_freshness(sub_dir, leg, fixture, delivered)
        delivery = _check_delivery(
            sub_dir,
            leg,
            delivered,
            fixture,
            expected_accepted=True,
        )
        ids.append(delivered["id"])
        _entries, prompts, _news = _turns(sub_dir, leg)
        turns.append(len(prompts))
        if sub == "second":
            key = (_observe_all(sub_dir, leg, delivery, fixture_name), delivery)
    if ids[0] != ids[1]:
        raise Failure(
            "neg-replayed: the two deliveries carry different event ids "
            f"({ids[0][:12]} vs {ids[1][:12]}) — this is not a replay"
        )
    if turns[0] != 1:
        raise Failure(
            f"neg-replayed/first: {turns[0]} ACP turn(s), expected exactly 1 — a replay "
            "leg proves nothing unless the first delivery produced a turn"
        )
    if turns[1] != 0:
        raise Failure(
            f"neg-replayed/second: {turns[1]} ACP turn(s), expected 0 — the duplicate "
            "delivery produced a second turn"
        )
    return key


def _has_any_timeline(root: Path) -> bool:
    for leg in LEG_NAMES:
        d = root / leg
        if (d / "timeline.jsonl").exists():
            return True
        for sub in REPLAY_SUBLEGS:
            if (d / sub / "timeline.jsonl").exists():
                return True
    return False


def _check_bundle_uncapped(root: Path, anchors: "Anchors") -> str:
    if not root.is_dir():
        raise Deferred("S0-02 evidence not captured")
    if not _has_any_timeline(root):
        raise Deferred("S0-02 evidence not captured")

    identities = json.loads(
        _require_file(anchors.identities_path, "bundle", "identities.json").read_text()
    )
    # F11: root closure — exactly the named legs, no extra entries. A garbage
    # file is just as unaccounted-for as an extra directory.
    expected_entries = set(LEG_NAMES)
    actual_entries = {p.name for p in root.iterdir()}
    extra = actual_entries - expected_entries
    if extra:
        raise Failure(f"bundle: unexpected leg directories or files {sorted(extra)}")

    observed: dict = {}
    for leg in LEG_NAMES:
        if leg == "neg-replayed":
            observed[leg] = _check_replay(root, identities, anchors)
            continue
        result = _check_leg(root / leg, leg, leg, identities, anchors)
        if result is not None:
            observed[leg] = result

    # DISTINCTNESS FIRST (seed:380 "one blanket rejection fails the proof"): a
    # stack that denies everything for one reason must fail as a blanket
    # rejection, not as six separate "wrong reason" failures.
    distinct_legs = list(oracle.DISTINCT_FIXTURES)
    keys = [_observed_key(observed[f][0]) for f in distinct_legs]
    # The two counts below are over the SAME population by construction; assert
    # it rather than assume it (sweep class 15: two counters compared as if they
    # ranged over one set).
    if len(keys) != len(distinct_legs):
        raise Failure(f"internal: {len(keys)} observed keys for {len(distinct_legs)} legs")
    if len(set(keys)) != len(distinct_legs):
        collapsed = sorted({k for k in set(keys)})
        raise Failure(
            f"blanket-rejection: reasons {collapsed} not distinct — "
            f"{len(distinct_legs)} negative legs collapsed to {len(set(keys))} observable(s)"
        )
    for fixture_name in oracle.NEGATIVE_FIXTURES:
        found, delivery = observed[fixture_name]
        leg = "neg-replayed/second" if fixture_name == "neg-replayed" else fixture_name
        _check_named_observable(leg, fixture_name, found, delivery)
    # The brief pins this line's prefix. The revocation leg (assertion 2) is a
    # SEVENTH negative leg that is separated structurally rather than by a
    # distinct observable, so it is counted separately instead of being folded
    # into "6 negative legs" — the count stays true to what the gate measured.
    n_extra = len(oracle.NEGATIVE_FIXTURES) - len(distinct_legs)
    return (
        f"PASS: S0-02 buzz-authz - 1 positive, {len(distinct_legs)} negative legs, "
        f"{len(set(keys))} distinct reasons; +{n_extra} revocation leg (assertion 2)"
    )


def check_bundle(root: Path, anchors: "Anchors | None" = None) -> str:
    anchors = anchors or Anchors.default()
    # F13b: wall-clock cap adopted from S0-01.
    return _check_with_timeout(90, _check_bundle_uncapped, root, anchors)


def main(argv) -> int:
    args = list(argv[1:])
    anchors = Anchors.default()
    if args[:1] == ["--synthetic-root"]:
        if len(args) != 3:
            print(
                "usage: check_buzz_authz.py [--synthetic-root <dir>] <evidence-root>",
                file=sys.stderr,
            )
            return 64
        anchors = Anchors.from_synthetic_root(Path(args[1]))
        args = args[2:]
    if len(args) != 1:
        print(
            "usage: check_buzz_authz.py [--synthetic-root <dir>] <evidence-root>",
            file=sys.stderr,
        )
        return 64
    root = Path(args[0])
    try:
        print(check_bundle(root, anchors))
        return 0
    except Deferred as exc:
        print(f"deferred: {exc}")
        return 2
    except Failure as exc:
        print(f"failure_reason: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
