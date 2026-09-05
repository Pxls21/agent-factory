"""BIP-340 Schnorr verification over secp256k1 for NIP-01 Nostr events.

Public API:
    event_id(event)                  -> hex str
    verify_event(event)              -> (ok: bool, reason: str)
    sign_event(privkey_hex, fields)  -> event dict   (TEST/FIXTURE use only)
    schnorr_verify(pubkey32, msg32, sig64) -> (ok: bool, reason: str)
    schnorr_sign(seckey32, msg32, aux32)   -> bytes (64-byte signature)

Pure Python, stdlib only.  Deterministic aux = 32 zero bytes for signing.
"""
import hashlib
import json
import re

# ---------------------------------------------------------------------------
# secp256k1 constants
# ---------------------------------------------------------------------------
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)


# ---------------------------------------------------------------------------
# Elliptic-curve arithmetic (None = point at infinity)
# ---------------------------------------------------------------------------
def _point_add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2:
        if y1 != y2:
            return None
        lam = (3 * x1 * x1 * pow(2 * y1, p - 2, p)) % p
    else:
        lam = ((y2 - y1) * pow(x2 - x1, p - 2, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def _point_mul(k, P):
    """Scalar multiplication k*P (double-and-add)."""
    if k <= 0:
        raise ValueError("scalar out of range")
    R = None
    Q = P
    while k > 0:
        if k & 1:
            R = _point_add(R, Q)
        Q = _point_add(Q, Q)
        k >>= 1
    return R


def _lift_x(x):
    """Lift an x-only coordinate to the point with even y, or None."""
    if x >= p:
        return None
    y_sq = (pow(x, 3, p) + 7) % p
    y = pow(y_sq, (p + 1) // 4, p)
    if y * y % p != y_sq:
        return None
    if y % 2 != 0:
        y = p - y
    return (x, y)


# ---------------------------------------------------------------------------
# BIP-340 tagged hash
# ---------------------------------------------------------------------------
def _tagged_hash(tag, msg):
    """SHA256(SHA256(tag) || SHA256(tag) || msg)."""
    tag_hash = hashlib.sha256(tag.encode("utf-8")).digest()
    return hashlib.sha256(tag_hash + tag_hash + msg).digest()


# ---------------------------------------------------------------------------
# NIP-01 event id
# ---------------------------------------------------------------------------
def event_id(event):
    """NIP-01 event id: SHA-256 hex of [0, pubkey, created_at, kind, tags, content]."""
    serialized = json.dumps(
        [0, event["pubkey"], event["created_at"], event["kind"],
         event["tags"], event["content"]],
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# BIP-340 Schnorr verify (public)
# ---------------------------------------------------------------------------
def schnorr_verify(pubkey_bytes, msg, sig_bytes):
    """BIP-340 Schnorr verification.  Returns (ok: bool, reason: str)."""
    P = _lift_x(int.from_bytes(pubkey_bytes, "big"))
    if P is None:
        return (False, "pubkey not on curve")

    r = int.from_bytes(sig_bytes[:32], "big")
    s = int.from_bytes(sig_bytes[32:], "big")

    if r >= p:
        return (False, "r >= p")
    if s >= n:
        return (False, "s >= n")

    e_hash = _tagged_hash("BIP0340/challenge",
                          sig_bytes[:32] + pubkey_bytes + msg)
    e = int.from_bytes(e_hash, "big") % n

    # s=0 is valid per BIP-340 (0 < n); s*G = infinity in that case.
    sG = None if s == 0 else _point_mul(s, G)
    R = _point_add(sG, _point_mul(n - e, P))

    if R is None:
        return (False, "verification failed: R is infinity")
    if R[1] % 2 != 0:
        return (False, "verification failed: R.y is odd")
    if R[0] != r:
        return (False, "verification failed: R.x != r")

    return (True, "valid")


# Keep the private name as an alias so existing callers (if any) don't break.
_schnorr_verify = schnorr_verify


# ---------------------------------------------------------------------------
# BIP-340 Schnorr sign (public, raw bytes)
# ---------------------------------------------------------------------------
def schnorr_sign(seckey32, msg32, aux32):
    """BIP-340 Schnorr sign.  Returns 64-byte signature.

    *seckey32*: 32-byte secret key.
    *msg32*: 32-byte message.
    *aux32*: 32-byte auxiliary randomness (deterministic aux = zeros).
    """
    d_prime = int.from_bytes(seckey32, "big")
    if d_prime == 0 or d_prime >= n:
        raise ValueError("invalid private key")

    P = _point_mul(d_prime, G)
    d = d_prime if P[1] % 2 == 0 else n - d_prime

    d_bytes = d.to_bytes(32, "big")
    t = bytes(a ^ b for a, b in zip(d_bytes, _tagged_hash("BIP0340/aux", aux32)))

    pk_bytes = P[0].to_bytes(32, "big")
    rand = _tagged_hash("BIP0340/nonce", t + pk_bytes + msg32)
    k_prime = int.from_bytes(rand, "big") % n
    if k_prime == 0:
        raise ValueError("nonce is zero")

    R = _point_mul(k_prime, G)
    k = k_prime if R[1] % 2 == 0 else n - k_prime

    e_hash = _tagged_hash("BIP0340/challenge",
                          R[0].to_bytes(32, "big") + pk_bytes + msg32)
    e = int.from_bytes(e_hash, "big") % n

    return R[0].to_bytes(32, "big") + ((k + e * d) % n).to_bytes(32, "big")


# ---------------------------------------------------------------------------
# Public: verify_event
# ---------------------------------------------------------------------------
def verify_event(event):
    """Verify a NIP-01 Nostr event: recompute id, BIP-340-verify signature.

    Returns (ok: bool, reason: str).  Never raises on JSON-typed input.
    """
    if not isinstance(event, dict):
        return (False, "event is not a dict")

    for field in ("id", "pubkey", "created_at", "kind", "tags", "content", "sig"):
        if field not in event:
            return (False, f"missing field: {field}")

    try:
        computed = event_id(event)
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        return (False, f"malformed event: {type(exc).__name__}: {exc}")

    if computed != event["id"]:
        return (False, f"id mismatch: computed {computed}")

    pubkey_hex = event["pubkey"]
    if not isinstance(pubkey_hex, str):
        return (False, f"pubkey: expected str, got {type(pubkey_hex).__name__}")
    if len(pubkey_hex) != 64:
        return (False, f"pubkey length {len(pubkey_hex)}, expected 64")
    if not re.fullmatch(r'[0-9a-f]{64}', pubkey_hex):
        return (False, "pubkey not lowercase hex")
    pubkey_bytes = bytes.fromhex(pubkey_hex)

    sig_hex = event["sig"]
    if not isinstance(sig_hex, str):
        return (False, f"sig: expected str, got {type(sig_hex).__name__}")
    if len(sig_hex) != 128:
        return (False, f"sig length {len(sig_hex)}, expected 128")
    if not re.fullmatch(r'[0-9a-f]{128}', sig_hex):
        return (False, "sig not lowercase hex")
    sig_bytes = bytes.fromhex(sig_hex)

    msg = bytes.fromhex(event["id"])
    return schnorr_verify(pubkey_bytes, msg, sig_bytes)


# ---------------------------------------------------------------------------
# Public: sign_event  (TEST/FIXTURE use only)
# ---------------------------------------------------------------------------
def sign_event(privkey_hex, fields):
    """BIP-340 sign a Nostr event.  TEST/FIXTURE use only.

    Deterministic aux = 32 zero bytes.
    *privkey_hex*: exactly 64 lowercase hex characters.
    *fields*: dict with created_at, kind, tags, content.
    Returns the complete event dict (id, pubkey, sig filled in).
    """
    if not isinstance(privkey_hex, str) or not re.fullmatch(r'[0-9a-f]{64}', privkey_hex):
        raise ValueError("private key must be exactly 64 lowercase hex characters")

    d_prime = int(privkey_hex, 16)
    if d_prime == 0 or d_prime >= n:
        raise ValueError("invalid private key")

    P = _point_mul(d_prime, G)
    pubkey_hex_out = format(P[0], "064x")

    event = {
        "pubkey": pubkey_hex_out,
        "created_at": fields["created_at"],
        "kind": fields["kind"],
        "tags": fields["tags"],
        "content": fields["content"],
    }
    eid = event_id(event)
    event["id"] = eid

    msg = bytes.fromhex(eid)
    aux = b"\x00" * 32
    seckey32 = bytes.fromhex(privkey_hex)

    sig = schnorr_sign(seckey32, msg, aux)
    event["sig"] = sig.hex()

    # Self-verify before returning.
    ok, reason = verify_event(event)
    if not ok:
        raise ValueError(f"self-verification failed: {reason}")

    return event
