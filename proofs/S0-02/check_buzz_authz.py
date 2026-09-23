#!/usr/bin/env python3
"""S0-02 checker — Buzz authorization and freshness over captured legs.

    python3 proofs/S0-02/check_buzz_authz.py <evidence-root>
    python3 proofs/S0-02/check_buzz_authz.py --denial <fixture> <evidence-root>

Exit codes: 0 PASS / 1 ``failure_reason: <reason>`` / 2 ``deferred: <reason>``.

``--denial <fixture>`` (B11) grades ONE negative leg exactly as the bundle
grades it and reads no sibling leg. A proven denial exits 1 with
``failure_reason: <the reason of the oracle row the leg's evidence matched>``,
the shape a spec negative leg expects; any other failure of the leg exits 1
with its own line, which never carries ``denied:``.

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
import os
import re
import stat
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
_load_timeline_raw = s0_01._load_timeline_raw
_HEX64 = s0_01._HEX64_ANYWHERE_RE
_check_with_timeout = s0_01._check_with_timeout


def _require_real_dir(path: Path, leg: str, name: str) -> Path:
    """S0-02's own real-directory requirement (B3): the node must BE a
    directory, not merely resolve to one. A symlinked leg (or sub-leg) is an
    evidence-outside-the-bundle channel: the bytes the checker reads then do
    not live under the evidence root at all. ``_require_dir`` (S0-01's) follows
    symlinks via ``Path.is_dir`` and is deliberately NOT reused here — the
    containment claim is this checker's to make."""
    try:
        st = os.lstat(path)
    except OSError:
        raise Failure(f"{leg}: {name} absent") from None
    if stat.S_ISLNK(st.st_mode):
        raise Failure(f"{leg}: {name} is a symlink, not a real directory")
    if not stat.S_ISDIR(st.st_mode):
        raise Failure(f"{leg}: {name} is not a directory")
    return path

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
# buzz-acp logs this at INFO once per process, in its entry point
# (crates/buzz-acp/src/lib.rs:2454); the S0-01 launcher keys its start line on
# the same text (proofs/S0-01/tools/pc/pc_launch.py:401). Measured 2026-09-23 on
# the S0-01 real-leg corpus: exactly one per masked log (run-1, run-2,
# two-users, cancel, shutdown). D-036 clause 3 counts it in the replay leg's log.
PROCESS_START_BANNER = "buzz-acp starting:"

LEG_NAMES = ("pos-allowed",) + oracle.NEGATIVE_FIXTURES
REPLAY_SUBLEGS = ("first", "second")

# Per-leg closure: the EXACT file set the runner writes per leg kind, derived
# from run_s0_02_legs.sh (delivered-event.json/job.json/garbage.txt are NOT
# written by this runner; only the files below are). A closure guard is the
# only way to catch a removed file AND a smuggled one with one rule — an extra
# entry is just as unaccounted-for as a missing one.
_LEG_FILES_PLAIN = frozenset({
    "fixture.json",
    "delivered-event.json",
    "delivery.json",
    "t0.json",
    "timeline.jsonl",
    "buzzacp.log",
})
# The revoked leg additionally writes the membership removal receipt.
_LEG_FILES_REVOKED = _LEG_FILES_PLAIN | {"membership.json"}


def _leg_closure(leg_dir: Path, leg: str, expected: frozenset):
    """Closure INSIDE a leg: exactly the names the runner writes (a garbage file
    is just as unaccounted-for as a missing one; a missing required name is
    named separately so the failure says WHY). Both checks are on the lstat
    name set; the real-dir guard (B3) already refused symlinked legs, so an
    entry here is a regular node under the evidence root."""
    names = {p.name for p in leg_dir.iterdir()}
    extra = names - expected
    if extra:
        raise Failure(f"{leg}: unexpected entries {sorted(extra)}")
    missing = expected - names
    if missing:
        raise Failure(f"{leg}: missing {sorted(missing)}")


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


def _read_receipt(leg_dir: Path, leg: str) -> dict:
    """delivery.json in the producer's exact key set (deliver_event._normalise).
    Shared by _check_delivery and by the replay's second sub-leg, whose outcome
    fields D-036 clause 2 grades separately (_check_duplicate_receipt)."""
    delivery = _read_json(leg_dir / "delivery.json", leg, "delivery.json")
    expected_keys = {"http_status", "event_id", "accepted", "message", "event_id_echoed"}
    if set(delivery) != expected_keys:
        missing = sorted(expected_keys - set(delivery))
        extra = sorted(set(delivery) - expected_keys)
        raise Failure(
            f"{leg}: delivery.json has the wrong producer shape "
            f"(missing={missing}, extra={extra})"
        )
    return delivery


def _check_delivery(
    leg_dir: Path,
    leg: str,
    delivered: dict,
    fixture: dict,
    expected_accepted: "bool | None" = None,
) -> dict:
    delivery = _read_receipt(leg_dir, leg)
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
# It also sees a row's defense-in-depth text (the replay row's buzz-acp drop
# line, D-036), so that line's presence is RECORDED; it is never required and
# never substitutes for the row's own observable (_check_duplicate_receipt).
ALL_OBSERVABLES = tuple(sorted(
    {r["observable"] for r in oracle.ROWS if r["leg"] == "negative"}
    | {r["defense_in_depth"]["observable"] for r in oracle.ROWS if "defense_in_depth" in r}
))


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


def _load_timeline(leg_dir: Path, leg: str):
    """F-13 (VERIFY-B9): S0-01's reader parses each line with a bare json.loads
    (s0_01._reject_nan), so a torn record escapes as JSONDecodeError (or as
    UnicodeDecodeError when the cut splits a UTF-8 sequence) and the CLI dies
    with a traceback and no ``failure_reason:`` line, which breaks the exit
    contract in the module docstring. Name it here; S0-01's attested reader
    stays untouched."""
    try:
        return _load_timeline_raw(leg_dir, leg)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Failure(
            f"{leg}: a timeline record is not valid JSON or UTF-8 — a torn or "
            f"partial line ({exc})"
        ) from None


def _turns(leg_dir: Path, leg: str):
    entries = _load_timeline(leg_dir, leg)
    prompts, news = _prompt_frames(entries, leg)
    return entries, prompts, news


def _check_leg(leg_dir: Path, leg: str, fixture_name: str, identities: dict, anchors: "Anchors"):
    """One captured leg. Returns (found, delivery, removal_note) — the note is
    None for every leg but the revoked one."""
    _require_real_dir(leg_dir, leg, f"{fixture_name} leg directory")
    _leg_closure(
        leg_dir, leg,
        _LEG_FILES_REVOKED if fixture_name == "revoked" else _LEG_FILES_PLAIN,
    )
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
        return None, None, None

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
    # F5 (B3 item 5): the removal evidence is a coordinator-supplied receipt —
    # there is no membership READ route on the pinned relay (api/mod.rs
    # check_relay_membership/enforce_relay_membership are INTERNAL enforcement
    # only), so no independent post-removal observation can be captured. The
    # checker says so in the summary line, and neither pretends a signature.
    removal_note = None
    if fixture_name == "revoked":
        removal_note = (
            "removal evidence: coordinator-supplied receipt "
            "(unauthenticated; ordering and fields verified; not an end-to-end revocation proof)"
        )
    return found, delivery, removal_note


def _check_one_process(leg_dir: Path, first: list, second: list):
    """D-036 clause 3: ONE continuous buzz-acp process spans both deliveries.

    The mechanism follows what the real producers write (measured 2026-09-23):
      * the frame tee numbers every record from ONE per-process counter
        (proofs/S0-01/tools/frame_tee.py:178, :363-364) and appends to one file
        (:337), so a restarted agent restarts at seq 1 with `initialize`. Every
        real S0-01 timeline is consecutive from seq 1, with `initialize` only at
        seq 1. A second `session/new` inside ONE process is normal (two-users,
        seq 12), so it is not a restart signal;
      * the launcher wipes the frame dir and opens a fresh raw log per launch
        (pc_launch.py:308, :354); pc_post.sh:107 masks it once after exit, and
        the runner copies that ONE masked log into both sub-legs
        (run_s0_02_legs.sh:305-306). buzz-acp logs PROCESS_START_BANNER once
        per process.
    So the second delta holds no `initialize` and continues the first
    snapshot's seq, both sub-legs carry the same log bytes, and that log shows
    exactly one start. An empty delta (the relay dropped the duplicate) passes
    the timeline half trivially; the log half still applies."""
    for rec in second:
        if rec.get("dir") == "c2a" and (rec.get("frame") or {}).get("method") == "initialize":
            raise Failure(
                f"neg-replayed/second: the delta holds an ACP initialize frame (seq "
                f"{rec.get('seq')!r}) — the agent restarted: a second process, not ONE "
                f"continuous buzz-acp process (D-036 clause 3)"
            )
    prev = first[-1].get("seq")
    for rec in second:
        seq = rec.get("seq")
        if type(prev) is not int or type(seq) is not int or seq != prev + 1:
            raise Failure(
                f"neg-replayed/second: delta record seq {seq!r} does not continue the "
                f"preceding seq {prev!r} — the frame tee restarted: a second process, "
                f"not ONE continuous buzz-acp process (D-036 clause 3)"
            )
        prev = seq
    logs = [
        _require_file(leg_dir / sub / "buzzacp.log", f"neg-replayed/{sub}", "buzzacp.log").read_bytes()
        for sub in REPLAY_SUBLEGS
    ]
    if logs[0] != logs[1]:
        raise Failure(
            "neg-replayed: the first and second sub-legs carry different buzzacp.log "
            "bytes — two masked logs: a second process, not ONE continuous buzz-acp "
            "process (D-036 clause 3)"
        )
    banner = PROCESS_START_BANNER.encode()
    starts = sum(1 for ln in logs[1].splitlines() if banner in ln)
    if starts != 1:
        raise Failure(
            f"neg-replayed: buzzacp.log shows {starts} buzz-acp start line(s) "
            f"({PROCESS_START_BANNER!r}), expected exactly 1 — not ONE continuous "
            f"buzz-acp process (D-036 clause 3)"
        )


def _check_replay(root: Path, identities: dict, anchors: "Anchors"):
    """The replayed leg is two deliveries of ONE event id in one directory.

    The proof is comparative: the FIRST delivery produced a turn and the SECOND
    produced none. A leg where neither produced a turn proves nothing.

    D-036 clause by clause: 1 the same event id, 4 one prompt in total and 5
    zero prompts in the second delta (below); 3 ONE continuous buzz-acp process
    (_check_one_process, after the turn counts so a restarted delta that ALSO
    carries a turn keeps its turn-count text); 2 the relay's `duplicate:`
    receipt bound to the second delivery (_check_duplicate_receipt, graded
    AFTER the distinctness gate because that receipt IS this leg's observable:
    a blanket-rejection bundle must reach the gate first, spec.json's blanket
    leg). Returns (found, the second receipt, the first delivery's event id).
    """
    leg_dir = root / "neg-replayed"
    _require_real_dir(leg_dir, "neg-replayed", "neg-replayed leg directory")
    if {p.name for p in leg_dir.iterdir()} != set(REPLAY_SUBLEGS):
        raise Failure(
            f"neg-replayed: expected exactly the sub-leg directories "
            f"{sorted(REPLAY_SUBLEGS)}, got "
            f"{sorted(p.name for p in leg_dir.iterdir())}"
        )
    ids = []
    turns = []
    entries = []
    found = delivery = None
    for sub in REPLAY_SUBLEGS:
        sub_dir = leg_dir / sub
        leg = f"neg-replayed/{sub}"
        _require_real_dir(sub_dir, leg, f"{sub} sub-leg directory")
        _leg_closure(sub_dir, leg, _LEG_FILES_PLAIN)
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
        if sub == "first":
            delivery = _check_delivery(
                sub_dir,
                leg,
                delivered,
                fixture,
                expected_accepted=True,
            )
        else:
            # Only the producer shape here: D-036 clause 2 grades this
            # receipt's outcome (_check_duplicate_receipt, after the gate).
            delivery = _read_receipt(sub_dir, leg)
        ids.append(delivered["id"])
        sub_entries, prompts, _news = _turns(sub_dir, leg)
        entries.append(sub_entries)
        turns.append(len(prompts))
        if sub == "second":
            found = _observe_all(sub_dir, leg, delivery, fixture_name)
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
    _check_one_process(leg_dir, entries[0], entries[1])
    return found, delivery, ids[0]


def _check_duplicate_receipt(found: frozenset, delivery: dict, first_id: str) -> bool:
    """D-036 clause 2: the relay's `duplicate:` receipt, BOUND to the second
    delivery. The pinned relay answers a kind-9 event id it already stored
    BEFORE dispatch (crates/buzz-relay/src/handlers/ingest.rs:3192-3197) with
    {event_id, accepted: true, message: "duplicate:"}; the bridge returns it as
    a 200 (crates/buzz-relay/src/api/bridge.rs:963-968), and
    deliver_event._normalise turns that into the receipt graded here. Each
    field is its own refusal. Returns whether the buzz-acp drop line (the
    row's defense-in-depth, relay.rs:2387) was ALSO seen: recorded in the
    summary, never required, never a substitute for this receipt."""
    leg = "neg-replayed/second"
    row = oracle.row("neg-replayed")
    status = delivery["http_status"]
    if type(status) is not int or status != 200:
        raise Failure(
            f"{leg}: the relay answers a duplicate with HTTP 200, got http_status {status!r}"
        )
    if delivery["accepted"] is not True:
        raise Failure(
            f"{leg}: the relay's duplicate receipt must carry accepted=true (a bool), "
            f"got {delivery['accepted']!r}"
        )
    if delivery["event_id_echoed"] is not True:
        raise Failure(
            f"{leg}: the relay's duplicate receipt must echo the event id "
            f"(event_id_echoed=true), got {delivery['event_id_echoed']!r}"
        )
    if delivery["event_id"] != first_id:
        raise Failure(
            f"{leg}: the duplicate receipt names event {str(delivery['event_id'])[:12]}, "
            f"not the first delivery's {first_id[:12]} — the receipt is not bound to "
            f"this replay"
        )
    if delivery["message"] != row["observable"]:
        raise Failure(
            f"{leg}: the relay receipt message is {delivery['message']!r}, expected "
            f"exactly {row['observable']!r} — the relay did not refuse the second "
            f"delivery as a duplicate (a forwarded duplicate fails even when buzz-acp "
            f"dropped it)"
        )
    dind = row["defense_in_depth"]
    dind_key = f"{dind['evidence']}::{dind['observable']}"
    extra = found - {f"{row['evidence']}::{row['observable']}", dind_key}
    if extra:
        raise Failure(
            f"{leg}: evidence carries denial observables {sorted(extra)} beside the "
            f"relay's duplicate receipt"
        )
    return dind_key in found


def _has_any_timeline(root: Path) -> bool:
    """Deferral gate, AFTER the root guard: lstat-based, never .exists() through
    a symlink, never descending a symlinked leg or sub-leg."""
    for leg in LEG_NAMES:
        d = root / leg
        try:
            if not stat.S_ISDIR(os.lstat(d).st_mode):
                continue
        except OSError:
            continue
        for p in (d / "timeline.jsonl",) + tuple(
            d / sub / "timeline.jsonl" for sub in REPLAY_SUBLEGS
        ):
            try:
                st = os.lstat(p)
            except OSError:
                continue
            if not stat.S_ISLNK(st.st_mode):
                return True
    return False


def _open_bundle(root: Path, anchors: "Anchors"):
    """The anchors and the root closure, shared by the bundle mode and the
    per-leg denial mode (B11 item 3): the root guard, the deferral gate, the
    identity anchor and the root closure. Returns (the resolved root, the
    identities)."""
    # The root itself must be a real directory, not a symlink: resolve() would
    # happily re-anchor every later containment check under the symlink target.
    try:
        root_mode = os.lstat(root).st_mode
    except OSError:
        raise Deferred("S0-02 evidence not captured") from None
    if stat.S_ISLNK(root_mode) or not stat.S_ISDIR(root_mode):
        raise Failure("bundle: the evidence root is a symlink or not a regular directory")
    root = root.resolve()
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
    return root, identities


def _check_bundle_uncapped(root: Path, anchors: "Anchors") -> str:
    root, identities = _open_bundle(root, anchors)

    observed: dict = {}
    removal_note = None
    replay_first_id = None
    for leg in LEG_NAMES:
        if leg == "neg-replayed":
            found, delivery, replay_first_id = _check_replay(root, identities, anchors)
            observed[leg] = (found, delivery)
            continue
        result = _check_leg(root / leg, leg, leg, identities, anchors)
        found, delivery, note = result
        if note is not None:
            removal_note = note
        observed[leg] = (found, delivery)

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
    replay_dind = None
    for fixture_name in oracle.NEGATIVE_FIXTURES:
        if fixture_name == "revoked":
            # The revoked leg is the SEVENTH, structurally-separate leg; its
            # observable (membership.json) is asserted inside _check_leg, and
            # its removal receipt is coordinator-supplied (F5).
            continue
        found, delivery = observed[fixture_name]
        if fixture_name == "neg-replayed":
            # D-036 clause 2: the relay decides this leg with an accepted=true
            # receipt, so the generic relay rule (accepted must be false) does not
            # apply; the receipt is graded field by field instead.
            replay_dind = _check_duplicate_receipt(found, delivery, replay_first_id)
            continue
        _check_named_observable(fixture_name, fixture_name, found, delivery)
    # The brief pins this line's prefix. The revocation leg (assertion 2) is a
    # SEVENTH negative leg that is separated structurally rather than by a
    # distinct observable, so it is counted separately instead of being folded
    # into "6 negative legs" — the count stays true to what the gate measured.
    # The replay segment records whether buzz-acp's own drop line (optional
    # defense-in-depth, D-036) was seen beside the relay's receipt.
    n_extra = len(oracle.NEGATIVE_FIXTURES) - len(distinct_legs)
    removal_line = removal_note
    replay_line = (
        "replay refused by the relay's duplicate: receipt (buzz-acp drop line "
        f"{'present' if replay_dind else 'absent'}, defense-in-depth only)"
    )
    return (
        f"PASS: S0-02 buzz-authz - 1 positive, {len(distinct_legs)} negative legs, "
        f"{len(set(keys))} distinct reasons; {replay_line}; "
        f"+{n_extra} revocation leg (assertion 2); {removal_line}"
    )


def check_bundle(root: Path, anchors: "Anchors | None" = None) -> str:
    anchors = anchors or Anchors.default()
    # F13b: wall-clock cap adopted from S0-01.
    return _check_with_timeout(90, _check_bundle_uncapped, root, anchors)


def _observed_row(leg: str, found: frozenset, removal_receipt: bool) -> dict:
    """B11 item 4: the oracle row the OBSERVED denial matches. The leg must show
    exactly one row's (channel, text) key; the replay row's defense-in-depth
    line is no row's key, so it neither counts nor matches. neg-unauthorized
    and revoked share one key by design (the oracle's revoked row): the
    membership receipt separates them — _check_leg verified it on the revoked
    leg, and the leg closure keeps it off every other leg."""
    negative = [r for r in oracle.ROWS if r["leg"] == "negative"]
    keys = found & {oracle.observable_key(r["fixture"]) for r in negative}
    if len(keys) != 1:
        raise Failure(
            f"{leg}: the evidence carries {len(keys)} oracle row observable(s) "
            f"{sorted(keys)}, expected exactly one"
        )
    rows = [r for r in negative if oracle.observable_key(r["fixture"]) in keys]
    if len(rows) > 1:
        rows = [r for r in rows if (r["fixture"] == "revoked") == removal_receipt]
    if len(rows) != 1:
        raise Failure(f"internal: the observation {sorted(keys)} matches {len(rows)} oracle rows")
    return rows[0]


def _check_denial_uncapped(root: Path, fixture_name: str, anchors: "Anchors") -> str:
    """B11 items 3-4: ONE negative leg, graded exactly as the bundle grades it —
    the anchors and the root closure, the leg's own checks, then that leg's
    denial grading. No sibling leg is read, so a broken sibling cannot change
    this verdict, and no cross-leg gate (distinctness) applies. Returns the
    reason of the oracle row the OBSERVED denial matched, never one chosen from
    the argument."""
    root, identities = _open_bundle(root, anchors)
    if fixture_name == "neg-replayed":
        leg, leg_dir = "neg-replayed/second", root / "neg-replayed" / "second"
        found, delivery, first_id = _check_replay(root, identities, anchors)
        _check_duplicate_receipt(found, delivery, first_id)
    else:
        leg, leg_dir = fixture_name, root / fixture_name
        found, delivery, _note = _check_leg(leg_dir, leg, fixture_name, identities, anchors)
        if fixture_name != "revoked":
            # As the bundle: the revoked leg is graded structurally inside
            # _check_leg and never by the named-observable check.
            _check_named_observable(leg, fixture_name, found, delivery)
    row = _observed_row(leg, found, os.path.lexists(leg_dir / "membership.json"))
    if row["fixture"] != fixture_name:
        raise Failure(
            f"{leg}: the observed denial matches the oracle's {row['fixture']} row, "
            f"not {fixture_name}'s"
        )
    return row["reason"]


def check_denial(root: Path, fixture_name: str, anchors: "Anchors | None" = None) -> str:
    anchors = anchors or Anchors.default()
    # F13b: the bundle mode's wall-clock cap.
    return _check_with_timeout(90, _check_denial_uncapped, root, fixture_name, anchors)


USAGE = "usage: check_buzz_authz.py [--synthetic-root <dir>] [--denial <fixture>] <evidence-root>"


def _denial_main(root: Path, fixture_name: str, anchors: "Anchors") -> int:
    """B11 item 4's exit contract. A proven denial prints the observed row's
    reason and exits 1, as a spec negative leg expects; any failure of the leg
    exits 1 with its own line; the evidence-absent path defers (2)."""
    try:
        reason = check_denial(root, fixture_name, anchors)
    except Deferred as exc:
        print(f"deferred: {exc}")
        return 2
    except Failure as exc:
        # scripts/proof-runner:194-197 reads a negative leg as proven when ANY
        # output line CONTAINS the spec's reason, and a failure text can quote
        # evidence bytes (a relay message, a file name). So no failure line in
        # this mode carries `denied:`; only a proven denial does.
        text = str(exc).replace("denied:", "denied\\x3a")
        print(f"failure_reason: {text}")
        return 1
    print(f"failure_reason: {reason}")
    return 1


def main(argv) -> int:
    args = list(argv[1:])
    anchors = Anchors.default()
    if args[:1] == ["--synthetic-root"]:
        if len(args) < 3:
            print(USAGE, file=sys.stderr)
            return 64
        anchors = Anchors.from_synthetic_root(Path(args[1]))
        args = args[2:]
    denial = None
    if args[:1] == ["--denial"]:
        # B11 item 2: only an oracle negative fixture names a leg to grade;
        # pos-allowed, an empty value or a missing one is a usage refusal.
        if len(args) != 3 or args[1] not in oracle.NEGATIVE_FIXTURES:
            print(USAGE, file=sys.stderr)
            return 64
        denial = args[1]
        args = args[2:]
    if len(args) != 1:
        print(USAGE, file=sys.stderr)
        return 64
    root = Path(args[0])
    if denial is not None:
        return _denial_main(root, denial, anchors)
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
