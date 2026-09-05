"""proofs/S0-01/tools/nostr_verify.py — BIP-340 Schnorr verification for NIP-01 Nostr events.

Tests:
  - All 19 official BIP-340 test vectors (verify + sign where applicable)
  - All 12 fixture events verify (id recomputes, signature valid)
  - Tampering content, sig, pubkey, or tags fails with exact reasons
  - sign_event -> verify_event round trip with throwaway keys
  - Non-ASCII NIP-01 id oracle test (node v22 independent computation)
  - Odd-y pubkey and odd-y nonce parity branch coverage
  - Length/type guard tests that catch deletion mutants
  - verify_event never raises on malformed JSON-typed input
  - _point_mul guard on k <= 0
  - sign_event strict hex validation and self-verification
"""
from __future__ import annotations

import copy
import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "proofs" / "S0-01" / "tools"
FIXTURES = ROOT / "proofs" / "S0-01" / "fixtures"

sys.path.insert(0, str(TOOLS))
import nostr_verify as nv  # noqa: E402


@pytest.fixture(scope="module")
def fixture_events():
    return json.loads((FIXTURES / "relay-events-2026-09-05.json").read_text())


# ---------------------------------------------------------------------------
# BIP-340 official test vectors (all 19) — closes V-a F1, F9
# ---------------------------------------------------------------------------
def _load_bip340_vectors():
    """Load all 19 BIP-340 test vectors from the committed CSV."""
    vectors = []
    csv_path = FIXTURES / "bip340-test-vectors.csv"
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            vectors.append({
                "index": int(row["index"]),
                "secret_key": row["secret key"],
                "public_key": row["public key"],
                "aux_rand": row["aux_rand"],
                "message": row["message"],
                "signature": row["signature"],
                "valid": row["verification result"] == "TRUE",
                "comment": row.get("comment", ""),
            })
    return vectors


BIP340_VECTORS = _load_bip340_vectors()

# Expected reasons for each vector, from the BIP-340 spec and verified independently.
BIP340_EXPECTED_REASONS = {
    0: "valid", 1: "valid", 2: "valid", 3: "valid", 4: "valid",
    5: "pubkey not on curve",
    6: "verification failed: R.y is odd",
    7: "verification failed: R.y is odd",
    8: "verification failed: R.x != r",
    9: "verification failed: R is infinity",
    10: "verification failed: R is infinity",
    11: "verification failed: R.x != r",
    12: "r >= p",
    13: "s >= n",
    14: "pubkey not on curve",
    15: "valid", 16: "valid", 17: "valid", 18: "valid",
}


class TestBIP340AllVectors:
    """All 19 official BIP-340 test vectors produce the specified verify verdicts.

    This kills the parity/infinity/range mutants (F1: vectors 6,9,10;
    F9: vectors 5,12,13,14) by asserting exact reasons.
    """

    @pytest.mark.parametrize(
        "vec",
        BIP340_VECTORS,
        ids=[f"vector-{v['index']}" for v in BIP340_VECTORS],
    )
    def test_verify_vector(self, vec):
        pubkey_bytes = bytes.fromhex(vec["public_key"])
        msg = bytes.fromhex(vec["message"]) if vec["message"] else b""
        sig_bytes = bytes.fromhex(vec["signature"])
        ok, reason = nv.schnorr_verify(pubkey_bytes, msg, sig_bytes)
        assert ok == vec["valid"], (
            f"vector {vec['index']}: expected valid={vec['valid']}, "
            f"got ok={ok}, reason={reason!r}"
        )
        assert reason == BIP340_EXPECTED_REASONS[vec["index"]], (
            f"vector {vec['index']}: expected reason "
            f"{BIP340_EXPECTED_REASONS[vec['index']]!r}, got {reason!r}"
        )


class TestBIP340SigningVectors:
    """Signing vectors 0-3 reproduce the exact signatures through schnorr_sign.

    Closes V-a F5 (sign_event byte-conformance).
    """

    @pytest.mark.parametrize(
        "vec",
        [v for v in BIP340_VECTORS if v["secret_key"]],
        ids=[f"sign-vector-{v['index']}" for v in BIP340_VECTORS if v["secret_key"]],
    )
    def test_sign_vector(self, vec):
        seckey = bytes.fromhex(vec["secret_key"])
        aux = bytes.fromhex(vec["aux_rand"])
        msg = bytes.fromhex(vec["message"]) if vec["message"] else b""
        sig = nv.schnorr_sign(seckey, msg, aux)
        assert sig.hex().upper() == vec["signature"], (
            f"vector {vec['index']}: signature mismatch"
        )


# ---------------------------------------------------------------------------
# Positive: all fixture events verify
# ---------------------------------------------------------------------------
class TestFixtureEventsVerify:
    def test_all_ids_recompute(self, fixture_events):
        for i, ev in enumerate(fixture_events):
            computed = nv.event_id(ev)
            assert computed == ev["id"], f"event {i}: id mismatch"

    def test_all_sigs_valid(self, fixture_events):
        for i, ev in enumerate(fixture_events):
            ok, reason = nv.verify_event(ev)
            assert ok, f"event {i} ({ev['id'][:12]}...): {reason}"

    def test_fixture_has_12_events(self, fixture_events):
        assert len(fixture_events) == 12


# ---------------------------------------------------------------------------
# NIP-01 non-ASCII event id — closes V-a F2
# ---------------------------------------------------------------------------
class TestNonAsciiNIP01:
    """Non-ASCII content produces the correct NIP-01 id.

    Expected id was computed by an independent oracle (node v22):
      /opt/node22/bin/node -e "
        const crypto = require('crypto');
        const pubkey = '2267fe91571e5c91e0ef0c5d4b585c3893a29e4a6ee13497baab2e1b4b82ddcd';
        const created_at = 1700000000;
        const kind = 1;
        const tags = [['t', 'test']];
        const content = 'pong \\U0001f41d caf\\u00e9';
        const serialized = JSON.stringify([0, pubkey, created_at, kind, tags, content]);
        const hash = crypto.createHash('sha256').update(serialized).digest('hex');
        console.log(hash);
      "
    The test must NOT shell out to node — the expected id is hardcoded.
    """
    EXPECTED_ID = "31440124ae50294808d8c84b6b24ef1b9d7065c92646e84de0921c6e77f393ae"

    def test_non_ascii_event_id(self):
        event = {
            "pubkey": "2267fe91571e5c91e0ef0c5d4b585c3893a29e4a6ee13497baab2e1b4b82ddcd",
            "created_at": 1700000000,
            "kind": 1,
            "tags": [["t", "test"]],
            "content": "pong \U0001f41d café",
        }
        computed = nv.event_id(event)
        assert computed == self.EXPECTED_ID, (
            f"NIP-01 id mismatch for non-ASCII content: {computed}"
        )

    def test_non_ascii_sign_verify_roundtrip(self):
        """A non-ASCII event round-trips through sign_event and verify_event."""
        key = "0000000000000000000000000000000000000000000000000000000000000005"
        fields = {
            "created_at": 1700000000,
            "kind": 1,
            "tags": [["t", "test"]],
            "content": "pong \U0001f41d café",
        }
        ev = nv.sign_event(key, fields)
        ok, reason = nv.verify_event(ev)
        assert ok, f"non-ASCII round-trip failed: {reason}"

    def test_ensure_ascii_false_matters(self):
        """Flipping ensure_ascii to True changes the id for non-ASCII content.

        This test catches the M12 mutant (ensure_ascii=True survives if all
        content is ASCII).
        """
        event = {
            "pubkey": "2267fe91571e5c91e0ef0c5d4b585c3893a29e4a6ee13497baab2e1b4b82ddcd",
            "created_at": 1700000000,
            "kind": 1,
            "tags": [["t", "test"]],
            "content": "pong \U0001f41d café",
        }
        # Compute the correct id
        correct_id = nv.event_id(event)
        # Compute what ensure_ascii=True would produce
        import hashlib
        wrong_serialized = json.dumps(
            [0, event["pubkey"], event["created_at"], event["kind"],
             event["tags"], event["content"]],
            separators=(",", ":"),
            ensure_ascii=True,
        )
        wrong_id = hashlib.sha256(wrong_serialized.encode("utf-8")).hexdigest()
        # They MUST differ for non-ASCII content
        assert correct_id != wrong_id, (
            "ensure_ascii=True produces the same id — the test content is ASCII-only"
        )


# ---------------------------------------------------------------------------
# Negative: tampered events fail — closes V-a F7 (tightened assertions)
# ---------------------------------------------------------------------------
class TestTamperFails:
    def test_tampered_content(self, fixture_events):
        ev = copy.deepcopy(fixture_events[0])
        ev["content"] = "tampered"
        ok, reason = nv.verify_event(ev)
        assert not ok
        assert reason.startswith("id mismatch: computed ")

    def test_tampered_sig(self, fixture_events):
        """Flip a byte in the signature — reaches schnorr_verify."""
        ev = copy.deepcopy(fixture_events[0])
        sig = ev["sig"]
        flipped = ("00" if sig[:2] != "00" else "ff") + sig[2:]
        ev["sig"] = flipped
        ok, reason = nv.verify_event(ev)
        assert not ok
        # Exact reason depends on the mutation; it always starts with "verification failed:"
        assert reason.startswith("verification failed:"), (
            f"expected a verification failure reason, got {reason!r}"
        )

    def test_tampered_pubkey_reaches_schnorr(self, fixture_events):
        """Substitute the user2 pubkey AND recompute the id, so only BIP-340 catches it.

        Closes V-a F7: the old test_tampered_pubkey only hit 'id mismatch'
        because the id wasn't recomputed. This test reaches schnorr_verify.
        """
        ev = copy.deepcopy(fixture_events[0])
        identities = json.loads((FIXTURES / "identities.json").read_text())
        ev["pubkey"] = identities["user2"]
        # Recompute id so the id check passes — only BIP-340 catches the mismatch.
        ev["id"] = nv.event_id(ev)
        ok, reason = nv.verify_event(ev)
        assert not ok
        assert reason.startswith("verification failed:") or reason == "pubkey not on curve", (
            f"expected a schnorr-level failure, got {reason!r}"
        )

    def test_tampered_pubkey_id_mismatch(self, fixture_events):
        """Changing pubkey without recomputing id gives 'id mismatch'."""
        ev = copy.deepcopy(fixture_events[0])
        identities = json.loads((FIXTURES / "identities.json").read_text())
        ev["pubkey"] = identities["user2"]
        ok, reason = nv.verify_event(ev)
        assert not ok
        assert reason.startswith("id mismatch: computed ")

    def test_tampered_tags(self, fixture_events):
        ev = copy.deepcopy(fixture_events[0])
        ev["tags"] = [["h", "bogus"]]
        ok, reason = nv.verify_event(ev)
        assert not ok
        assert reason.startswith("id mismatch: computed ")


# ---------------------------------------------------------------------------
# Negative: malformed inputs — closes V-a F7 (exact length reasons),
# F8 (never raises), F10 (whitespace/uppercase hex rejection)
# ---------------------------------------------------------------------------
class TestMalformedInputs:
    def test_missing_field(self):
        ok, reason = nv.verify_event({"id": "a", "pubkey": "b"})
        assert not ok
        assert reason == "missing field: created_at"

    def test_bad_pubkey_length(self, fixture_events):
        """Short pubkey with recomputed id — catches the length-guard deletion mutant."""
        ev = copy.deepcopy(fixture_events[0])
        ev["pubkey"] = "abcd"
        ev["id"] = nv.event_id(ev)  # recompute so id check passes
        ok, reason = nv.verify_event(ev)
        assert not ok
        assert reason == "pubkey length 4, expected 64"

    def test_bad_sig_length(self, fixture_events):
        """Short sig — catches the sig-length-guard deletion mutant."""
        ev = copy.deepcopy(fixture_events[0])
        ev["sig"] = "abcd"
        # sig is not part of the id, so no recomputation needed
        ok, reason = nv.verify_event(ev)
        assert not ok
        assert reason == "sig length 4, expected 128"

    def test_pubkey_whitespace_rejected(self, fixture_events):
        """Pubkey hex with spaces is rejected (F10: bytes.fromhex skips whitespace)."""
        ev = copy.deepcopy(fixture_events[0])
        # 64 chars total: 31 hex pairs (62 chars) + space + 'a' = 64 chars
        ev["pubkey"] = "ab" * 31 + " a"  # exactly 64 chars but not clean hex
        ev["id"] = nv.event_id(ev)
        ok, reason = nv.verify_event(ev)
        assert not ok
        assert reason == "pubkey not lowercase hex"

    def test_sig_whitespace_rejected(self, fixture_events):
        """Sig hex with spaces is rejected (F10)."""
        ev = copy.deepcopy(fixture_events[0])
        # 128 chars total: 63 hex pairs (126 chars) + space + 'a' = 128 chars
        ev["sig"] = "ab" * 63 + " a"  # exactly 128 chars but not clean hex
        ok, reason = nv.verify_event(ev)
        assert not ok
        assert reason == "sig not lowercase hex"

    def test_pubkey_uppercase_rejected(self, fixture_events):
        """Uppercase pubkey hex is rejected."""
        ev = copy.deepcopy(fixture_events[0])
        ev["pubkey"] = ev["pubkey"].upper()
        ev["id"] = nv.event_id(ev)
        ok, reason = nv.verify_event(ev)
        assert not ok
        assert reason == "pubkey not lowercase hex"

    def test_sig_uppercase_rejected(self, fixture_events):
        """Uppercase sig hex is rejected."""
        ev = copy.deepcopy(fixture_events[0])
        ev["sig"] = ev["sig"].upper()
        ok, reason = nv.verify_event(ev)
        assert not ok
        assert reason == "sig not lowercase hex"


# ---------------------------------------------------------------------------
# verify_event never raises on malformed input — closes V-a F8
# ---------------------------------------------------------------------------
class TestVerifyEventNeverRaises:
    """verify_event returns (False, reason) for every JSON-typed input, never raises."""

    def test_sig_is_list(self, fixture_events):
        ev = copy.deepcopy(fixture_events[0])
        ev["sig"] = ["ab"] * 128
        ok, reason = nv.verify_event(ev)
        assert not ok
        assert reason == "sig: expected str, got list"

    def test_sig_is_none(self, fixture_events):
        ev = copy.deepcopy(fixture_events[0])
        ev["sig"] = None
        ok, reason = nv.verify_event(ev)
        assert not ok
        assert reason == "sig: expected str, got NoneType"

    def test_pubkey_is_int(self, fixture_events):
        ev = copy.deepcopy(fixture_events[0])
        ev["pubkey"] = 42
        # Recompute id so the id check passes and we reach the isinstance guard
        ev["id"] = nv.event_id(ev)
        ok, reason = nv.verify_event(ev)
        assert not ok
        assert reason == "pubkey: expected str, got int"

    def test_content_surrogate(self, fixture_events):
        ev = copy.deepcopy(fixture_events[0])
        ev["content"] = "test \ud800 surrogate"
        ok, reason = nv.verify_event(ev)
        assert not ok
        assert reason.startswith("malformed event: UnicodeEncodeError:")

    def test_tags_non_serializable(self, fixture_events):
        ev = copy.deepcopy(fixture_events[0])
        ev["tags"] = [[object()]]
        ok, reason = nv.verify_event(ev)
        assert not ok
        assert reason.startswith("malformed event: TypeError:")

    def test_event_is_not_dict(self):
        ok, reason = nv.verify_event("not a dict")
        assert not ok
        assert reason == "event is not a dict"

    def test_event_is_list(self):
        ok, reason = nv.verify_event([1, 2, 3])
        assert not ok
        assert reason == "event is not a dict"


# ---------------------------------------------------------------------------
# sign_event -> verify_event round trip — closes V-a F5, F6
# ---------------------------------------------------------------------------
class TestSignVerifyRoundTrip:
    THROWAWAY_KEY_EVEN_Y = "0000000000000000000000000000000000000000000000000000000000000005"
    THROWAWAY_KEY_ODD_Y = "0000000000000000000000000000000000000000000000000000000000000006"

    def test_roundtrip(self):
        fields = {
            "created_at": 1700000000,
            "kind": 1,
            "tags": [["t", "test"]],
            "content": "round trip test",
        }
        ev = nv.sign_event(self.THROWAWAY_KEY_EVEN_Y, fields)
        assert "id" in ev
        assert "sig" in ev
        assert "pubkey" in ev
        assert len(ev["sig"]) == 128
        assert len(ev["pubkey"]) == 64
        ok, reason = nv.verify_event(ev)
        assert ok, f"round-trip verify failed: {reason}"

    def test_roundtrip_tamper_fails(self):
        fields = {
            "created_at": 1700000000,
            "kind": 1,
            "tags": [],
            "content": "tamper test",
        }
        ev = nv.sign_event(self.THROWAWAY_KEY_EVEN_Y, fields)
        ev["content"] = "changed"
        ok, reason = nv.verify_event(ev)
        assert not ok

    def test_roundtrip_odd_y_pubkey(self):
        """seckey 6 produces an odd-y pubkey — exercises the d-negation branch.

        Closes V-a F6: the committed key (5) has an even-y pubkey, so the
        `d = n - d_prime` branch was never taken.
        """
        fields = {
            "created_at": 1700000000,
            "kind": 1,
            "tags": [["t", "test"]],
            "content": "round trip test",
        }
        # Verify the key actually has odd-y pubkey before signing
        d_prime = int(self.THROWAWAY_KEY_ODD_Y, 16)
        P = nv._point_mul(d_prime, nv.G)
        assert P[1] % 2 != 0, "seckey 6 should produce an odd-y pubkey"

        ev = nv.sign_event(self.THROWAWAY_KEY_ODD_Y, fields)
        ok, reason = nv.verify_event(ev)
        assert ok, f"odd-y pubkey round-trip failed: {reason}"

    def test_roundtrip_odd_y_nonce(self):
        """Content chosen to produce an odd-y nonce R — exercises the k-negation branch.

        Both seckey 6 (odd-y pubkey) and content 'odd nonce test' produce an
        odd-y R, so BOTH negation branches are taken in a single sign_event call.
        Closes V-a F6.
        """
        fields = {
            "created_at": 1700000000,
            "kind": 1,
            "tags": [["t", "test"]],
            "content": "odd nonce test",
        }
        # Verify both branches will be taken
        d_prime = int(self.THROWAWAY_KEY_ODD_Y, 16)
        P = nv._point_mul(d_prime, nv.G)
        assert P[1] % 2 != 0, "seckey 6 should produce an odd-y pubkey"

        # Compute nonce R to verify it has odd y (pre-condition for the test)
        d = nv.n - d_prime  # negated because odd-y pubkey
        d_bytes = d.to_bytes(32, "big")
        pubkey_hex = format(P[0], "064x")
        event = {"pubkey": pubkey_hex, "created_at": 1700000000, "kind": 1,
                 "tags": [["t", "test"]], "content": "odd nonce test"}
        eid = nv.event_id(event)
        msg = bytes.fromhex(eid)
        aux = b"\x00" * 32
        t = bytes(a ^ b for a, b in zip(d_bytes, nv._tagged_hash("BIP0340/aux", aux)))
        pk_bytes = P[0].to_bytes(32, "big")
        rand = nv._tagged_hash("BIP0340/nonce", t + pk_bytes + msg)
        k_prime = int.from_bytes(rand, "big") % nv.n
        R = nv._point_mul(k_prime, nv.G)
        assert R[1] % 2 != 0, (
            "nonce R should have odd y for this content — "
            "choose a different content if this fails"
        )

        ev = nv.sign_event(self.THROWAWAY_KEY_ODD_Y, fields)
        ok, reason = nv.verify_event(ev)
        assert ok, f"odd-y nonce round-trip failed: {reason}"


# ---------------------------------------------------------------------------
# BIP-340 vector 0: exact signature test — closes V-a F5
# ---------------------------------------------------------------------------
class TestBIP340Vector0:
    SECKEY = "0000000000000000000000000000000000000000000000000000000000000003"
    PUBKEY = "F9308A019258C31049344F85F89D5229B531C845836F99B08601F113BCE036F9"
    MSG = b"\x00" * 32
    SIG = ("E907831F80848D1069A5371B402410364BDF1C5F8307B0084C55F1CE2DCA8215"
           "25F66A4A85EA8B71E482A74F382D2CE5EBEEE8FDB2172F477DF4900D310536C0")

    def test_verify(self):
        """The known BIP-340 vector verifies (raw schnorr, not an event)."""
        pubkey_bytes = bytes.fromhex(self.PUBKEY)
        sig_bytes = bytes.fromhex(self.SIG)
        ok, reason = nv.schnorr_verify(pubkey_bytes, self.MSG, sig_bytes)
        assert ok, f"BIP-340 vector 0 failed: {reason}"

    def test_sign_matches(self):
        """Signing 32 zero bytes with seckey 3 produces the known signature.

        Closes V-a F5: the old test only checked the pubkey, not the signature.
        """
        seckey = bytes.fromhex(self.SECKEY)
        aux = b"\x00" * 32
        sig = nv.schnorr_sign(seckey, self.MSG, aux)
        assert sig.hex().upper() == self.SIG, (
            f"vector 0 sig mismatch: got {sig.hex().upper()}"
        )

    def test_sign_pubkey(self):
        """seckey 3 derives the correct public key."""
        d_prime = int(self.SECKEY, 16)
        P = nv._point_mul(d_prime, nv.G)
        assert format(P[0], "064x").upper() == self.PUBKEY

    def test_wrong_vector_fails(self):
        """A deliberately wrong message fails verification."""
        pubkey_bytes = bytes.fromhex(self.PUBKEY)
        sig_bytes = bytes.fromhex(self.SIG)
        wrong_msg = b"\x01" + b"\x00" * 31
        ok, reason = nv.schnorr_verify(pubkey_bytes, wrong_msg, sig_bytes)
        assert not ok, "wrong message should fail"

    def test_wrong_sig_fails(self):
        """A deliberately wrong signature fails verification."""
        pubkey_bytes = bytes.fromhex(self.PUBKEY)
        sig_bytes = bytes.fromhex("00" * 64)
        ok, reason = nv.schnorr_verify(pubkey_bytes, self.MSG, sig_bytes)
        assert not ok, "zero signature should fail"


# ---------------------------------------------------------------------------
# _point_mul guard — closes V-a F11
# ---------------------------------------------------------------------------
class TestPointMulGuard:
    def test_k_zero_raises(self):
        with pytest.raises(ValueError, match="scalar out of range"):
            nv._point_mul(0, nv.G)

    def test_k_negative_raises(self):
        with pytest.raises(ValueError, match="scalar out of range"):
            nv._point_mul(-1, nv.G)

    def test_k_positive_works(self):
        """k=1 returns the generator point itself."""
        result = nv._point_mul(1, nv.G)
        assert result == nv.G


# ---------------------------------------------------------------------------
# sign_event strict validation — closes V-a F12
# ---------------------------------------------------------------------------
class TestSignEventValidation:
    def test_rejects_0x_prefix(self):
        with pytest.raises(ValueError, match="exactly 64 lowercase hex"):
            nv.sign_event("0x" + "00" * 31, {
                "created_at": 1, "kind": 1, "tags": [], "content": "",
            })

    def test_rejects_whitespace(self):
        with pytest.raises(ValueError, match="exactly 64 lowercase hex"):
            nv.sign_event(" " * 2 + "00" * 31, {
                "created_at": 1, "kind": 1, "tags": [], "content": "",
            })

    def test_rejects_underscores(self):
        with pytest.raises(ValueError, match="exactly 64 lowercase hex"):
            nv.sign_event("3_3" + "0" * 61, {
                "created_at": 1, "kind": 1, "tags": [], "content": "",
            })

    def test_rejects_uppercase(self):
        with pytest.raises(ValueError, match="exactly 64 lowercase hex"):
            nv.sign_event("00" * 31 + "0A", {
                "created_at": 1, "kind": 1, "tags": [], "content": "",
            })

    def test_rejects_short_key(self):
        with pytest.raises(ValueError, match="exactly 64 lowercase hex"):
            nv.sign_event("03", {
                "created_at": 1, "kind": 1, "tags": [], "content": "",
            })

    def test_rejects_zero_key(self):
        with pytest.raises(ValueError, match="invalid private key"):
            nv.sign_event("00" * 32, {
                "created_at": 1, "kind": 1, "tags": [], "content": "",
            })

    def test_rejects_non_string(self):
        with pytest.raises(ValueError, match="exactly 64 lowercase hex"):
            nv.sign_event(3, {
                "created_at": 1, "kind": 1, "tags": [], "content": "",
            })
