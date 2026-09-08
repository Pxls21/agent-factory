"""S0-02 oracle: reason -> the OBSERVABLE the pinned stack produces for it.

Independent of ``check_buzz_authz.py``: this module imports nothing from the
checker and holds no checking logic, only the table and its accessors.  The
checker consults it; the table never consults the checker.

Every row is pinned to a `file:line` in a checked-out upstream source tree and
is re-verified against that tree by ``tests/test_s0_02_buzz_authz.py`` (env
``S0_02_BUZZ_SRC``, sandbox default ``/home/user/nerdherderdani/buzz``).

TWO upstream components decide S0-02's five negative classes, and that split is
the proof's central finding, not an implementation detail:

  * ``buzz-acp`` (the component S0-02 names) decides only REPLAY and
    SELF-AUTHORED for an ordinary kind-9 channel event.  Both emit a
    ``tracing::debug!`` line, so both are visible only at ``RUST_LOG=debug``.
  * ``buzz-relay`` decides SIGNATURE, MEMBERSHIP and FRESHNESS at publish
    (ingest) time.  Those events never reach ``buzz-acp`` at all, so no
    buzz-acp log line can exist for them; the observable is the relay's
    rejection text in the delivery receipt.

``buzz-acp`` at the pinned commit performs NO signature check and NO per-event
freshness check on a channel event.  See DISCREPANCIES below.
"""
from __future__ import annotations

BUZZ_COMMIT = "1c8321cd08feb597f8bcff5195c21148fb3e98ed"

# Where the checker must look for a row's observable.
EV_TIMELINE = "timeline"      # the tee's timeline.jsonl (ACP frames)
EV_BUZZACP_LOG = "buzzacp_log"  # buzz-acp's own tracing output, RUST_LOG=debug
EV_DELIVERY = "delivery"      # the relay's response to the publish (delivery.json)

# The five negative classes S0-02 must keep DISTINCT (seed:375-380 names four;
# docs/03_INTEGRATION_CONTRACTS.md:22 and FINDINGS-STAGE0-v1.md:43 add the fifth).
SEED_REASONS = (
    "denied: sender-not-in-allowlist",
    "denied: signature-invalid",
    "denied: event-replayed",
    "denied: event-stale",
)
FIFTH_REASON = "denied: self-authored"

ROWS = (
    {
        "fixture": "pos-allowed",
        "reason": None,
        "leg": "positive",
        "decided_by": "buzz-acp",
        "src": "crates/buzz-acp/src/lib.rs",
        "line": 372,
        "src_pattern": "async fn author_allowed(",
        "evidence": EV_TIMELINE,
        "observable": "session/prompt",
        "buzz_acp_observable": "session/prompt reaches the agent",
        "discrepancy": None,
        "note": (
            "author_allowed (lib.rs:372-395) returns true for the configured "
            "RespondTo mode; authorize_listener_event (lib.rs:521-556) then "
            "yields AuthorizedListenerEvent and the pool issues session/new + "
            "session/prompt."
        ),
    },
    {
        "fixture": "neg-unauthorized",
        "reason": "denied: sender-not-in-allowlist",
        "leg": "negative",
        "decided_by": "buzz-relay",
        "src": "crates/buzz-relay/src/handlers/ingest.rs",
        "line": 770,
        "src_pattern": 'Err("restricted: not a channel member".to_string())',
        "evidence": EV_DELIVERY,
        "observable": "restricted: not a channel member",
        "buzz_acp_observable": None,
        "discrepancy": (
            "buzz-acp HAS an author gate that logs "
            "'inbound author gate - dropping event' (crates/buzz-acp/src/lib.rs:550), "
            "but it can only fire for a sender the RELAY already accepted. A "
            "non-member key cannot publish to the channel at all, so for this "
            "fixture the deciding component is buzz-relay and the buzz-acp line "
            "is unreachable. A member-but-not-allowlisted sender (e.g. user2 "
            "under respond_to=owner-only) would exercise the buzz-acp line "
            "instead; that fixture is NOT built here."
        ),
        "note": (
            "Also unreachable earlier: ingest.rs:2242 rejects an event whose "
            "pubkey does not match the authenticated identity, so a non-member "
            "event cannot be smuggled in under another identity's auth."
        ),
    },
    {
        "fixture": "neg-bad-signature",
        "reason": "denied: signature-invalid",
        "leg": "negative",
        "decided_by": "buzz-relay",
        "src": "crates/buzz-relay/src/handlers/ingest.rs",
        "line": 2213,
        "src_pattern": 'IngestError::Rejected(format!("invalid: {e}"))',
        "evidence": EV_DELIVERY,
        "observable": "invalid: invalid schnorr signature",
        "buzz_acp_observable": None,
        "discrepancy": (
            "NOT FOUND in buzz-acp " + BUZZ_COMMIT + " - DISCREPANCY. "
            "buzz-acp deserialises a relay EVENT frame with "
            "serde_json::from_value (crates/buzz-acp/src/relay.rs:3775) and "
            "never calls verify_event on it. Every verify_event call in the "
            "crate is on a different path: observer control frames "
            "(lib.rs:1574), NIP-OA workflow attribution (lib.rs:256), engram "
            "fetch (engram_fetch.rs:122), pool (pool.rs:3385, pool.rs:3495). "
            "The signature decision for a channel event is buzz-relay's alone."
        ),
        "note": (
            "Wire text is fixed: verify_event returns "
            "VerificationError::InvalidSignature, whose thiserror message is "
            "'invalid schnorr signature' "
            "(crates/buzz-core/src/error.rs:14), wrapped by ingest.rs:2213 as "
            "'invalid: {e}'. Flipping one signature byte leaves the event id "
            "valid, so verify_id passes first and the signature arm is the one "
            "that fires."
        ),
    },
    {
        "fixture": "neg-replayed",
        "reason": "denied: event-replayed",
        "leg": "negative",
        "decided_by": "buzz-acp",
        "src": "crates/buzz-acp/src/relay.rs",
        "line": 2387,
        "src_pattern": 'debug!("dropping duplicate event for channel {channel_id}");',
        "evidence": EV_BUZZACP_LOG,
        "observable": "dropping duplicate event for channel",
        "buzz_acp_observable": "dropping duplicate event for channel",
        "discrepancy": None,
        "note": (
            "The drop DECISION is silent at its own site: BgState::record_event "
            "(relay.rs:1258) returns false at relay.rs:1262 with no log. The "
            "CALL SITE logs: relay.rs:2344 branches on record_event and its "
            "else arm at relay.rs:2387 emits the debug line. The brief's "
            "hypothesis that the dedup is silent is therefore CORRECT at :1262 "
            "and WRONG for the observable - an observable exists at :2387."
        ),
    },
    {
        "fixture": "neg-stale",
        "reason": "denied: event-stale",
        "leg": "negative",
        "decided_by": "buzz-relay",
        "src": "crates/buzz-relay/src/handlers/ingest.rs",
        "line": 2229,
        "src_pattern": '"invalid: event timestamp too far from server time".into(),',
        "evidence": EV_DELIVERY,
        "observable": "invalid: event timestamp too far from server time",
        "buzz_acp_observable": None,
        "discrepancy": (
            "NO per-event freshness rule for a kind-9 channel event exists in "
            "buzz-acp " + BUZZ_COMMIT + " - DISCREPANCY. The crate's only "
            "freshness constant, OBSERVER_CONTROL_FRESHNESS_SECS = 300 "
            "(crates/buzz-acp/src/lib.rs:1563), is applied at lib.rs:1592 to "
            "observer CONTROL frames only. buzz-acp's freshness for ordinary "
            "events is a SUBSCRIPTION floor, not a rejection: startup_watermark "
            "(captured at lib.rs:2487, applied at relay.rs:1475/1711) feeds "
            "BgState::channel_since (relay.rs:1282) which sets `since` on the "
            "REQ, so a stale event is never sent to buzz-acp and buzz-acp "
            "emits nothing. That floor is a SILENT-DROP mechanism; the named, "
            "observable stale rule is buzz-relay's +/-900s ingest drift check "
            "(MAX_TIMESTAMP_DRIFT_SECS, ingest.rs:2224)."
        ),
        "note": (
            "The relay's window is the OUTER one and fires first, so it is the "
            "pinned observable. The buzz-acp `since` floor is recorded as the "
            "secondary silent mechanism; its alternative evidence is the "
            "delivery receipt for the event id plus zero turns in the leg."
        ),
        "silent_drop_secondary": {
            "src": "crates/buzz-acp/src/relay.rs",
            "line": 1282,
            "src_pattern": "fn channel_since(&self, channel_id: &Uuid) -> Option<u64> {",
            "alternative_evidence": "delivery receipt for the event id AND zero ACP turns in the leg",
        },
    },
    {
        "fixture": "neg-self-authored",
        "reason": FIFTH_REASON,
        "leg": "negative",
        "decided_by": "buzz-acp",
        "src": "crates/buzz-acp/src/lib.rs",
        "line": 3258,
        "src_pattern": 'tracing::debug!(channel_id = %buzz_event.channel_id, "dropping self-authored event");',
        "evidence": EV_BUZZACP_LOG,
        "observable": "dropping self-authored event",
        "buzz_acp_observable": "dropping self-authored event",
        "discrepancy": None,
        "note": (
            "Guarded by config.ignore_self at lib.rs:3257; the S0-01 startup "
            "line records ignore_self=true, so the arm is live in that "
            "configuration. With ignore_self=false the drop does not happen at "
            "all - the leg's buzzacp.log must therefore also show "
            "ignore_self=true, which the checker asserts."
        ),
    },
    {
        # Assertion 2 (seed:372). NOT one of the five distinct classes: its
        # relay text is identical to neg-unauthorized's by construction, and it
        # is separated by its own structural evidence instead.
        "fixture": "revoked",
        "reason": "denied: membership-revoked",
        "leg": "negative",
        "decided_by": "buzz-relay",
        "src": "crates/buzz-relay/src/handlers/ingest.rs",
        "line": 1201,
        "src_pattern": 'return Err("restricted: not a channel member".to_string());',
        "evidence": EV_DELIVERY,
        "observable": "restricted: not a channel member",
        "buzz_acp_observable": None,
        "discrepancy": (
            "Shares its rejection TEXT with neg-unauthorized (both are "
            "'restricted: not a channel member'), so it cannot join the "
            "five-distinct-reasons set on text alone. It is separated "
            "STRUCTURALLY instead: the revoked leg must carry membership.json "
            "(the removal receipt for THIS sender) and a created_at INSIDE the "
            "freshness window, which is exactly what makes it prove 'revocation "
            "is independent of NIP-OA created_at'. neg-unauthorized has no "
            "membership.json and its sender was never a member."
        ),
        "note": (
            "buzz-acp's own membership handling (lib.rs:3209, "
            "'membership notification: unsubscribing from channel') fires only "
            "when the AGENT is removed, not when a SENDER is; relay.rs's "
            "membership_dropped_since (relay.rs:1176) tracks BACKPRESSURE drops "
            "of membership notifications, not revocation. Neither is an "
            "observable for a revoked SENDER."
        ),
    },
)

BY_FIXTURE = {row["fixture"]: row for row in ROWS}
NEGATIVE_FIXTURES = tuple(r["fixture"] for r in ROWS if r["leg"] == "negative")
# The five that must stay distinct (excludes the structurally-separated revoked leg).
DISTINCT_FIXTURES = tuple(f for f in NEGATIVE_FIXTURES if f != "revoked")


def row(fixture: str) -> dict:
    """The oracle row for *fixture*. KeyError is deliberate: an unknown leg is a bug."""
    return BY_FIXTURE[fixture]


def observable_key(fixture: str) -> str:
    """The distinctness key for a negative fixture: (evidence channel, text).

    Two legs sharing this key are one blanket rejection wearing two names.
    """
    r = BY_FIXTURE[fixture]
    return f"{r['evidence']}::{r['observable']}"
