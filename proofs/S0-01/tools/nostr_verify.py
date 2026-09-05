#!/usr/bin/python3
"""BIP-340 Schnorr verification over secp256k1 for NIP-01 Nostr events.

Public API:
    event_id(event)                  -> hex str
    verify_event(event)              -> (ok: bool, reason: str)
    sign_event(privkey_hex, fields)  -> event dict   (TEST/FIXTURE use only)

Pure Python, stdlib only.  Deterministic aux = 32 zero bytes for signing.
"""
import hashlib
import json

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
# BIP-340 Schnorr verify (internal)
# ---------------------------------------------------------------------------
def _schnorr_verify(pubkey_bytes, msg, sig_bytes):
    """Returns (ok, reason)."""
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

    R = _point_add(_point_mul(s, G), _point_mul(n - e, P))

    if R is None:
        return (False, "verification failed: R is infinity")
    if R[1] % 2 != 0:
        return (False, "verification failed: R.y is odd")
    if R[0] != r:
        return (False, "verification failed: R.x != r")

    return (True, "valid")


# ---------------------------------------------------------------------------
# Public: verify_event
# ---------------------------------------------------------------------------
def verify_event(event):
    """Verify a NIP-01 Nostr event: recompute id, BIP-340-verify signature.

    Returns (ok: bool, reason: str).
    """
    for field in ("id", "pubkey", "created_at", "kind", "tags", "content", "sig"):
        if field not in event:
            return (False, f"missing field: {field}")

    computed = event_id(event)
    if computed != event["id"]:
        return (False, f"id mismatch: computed {computed}")

    pubkey_hex = event["pubkey"]
    if len(pubkey_hex) != 64:
        return (False, f"pubkey length {len(pubkey_hex)}, expected 64")
    try:
        pubkey_bytes = bytes.fromhex(pubkey_hex)
    except ValueError:
        return (False, "pubkey not valid hex")

    sig_hex = event["sig"]
    if len(sig_hex) != 128:
        return (False, f"sig length {len(sig_hex)}, expected 128")
    try:
        sig_bytes = bytes.fromhex(sig_hex)
    except ValueError:
        return (False, "sig not valid hex")

    msg = bytes.fromhex(event["id"])
    return _schnorr_verify(pubkey_bytes, msg, sig_bytes)


# ---------------------------------------------------------------------------
# Public: sign_event  (TEST/FIXTURE use only)
# ---------------------------------------------------------------------------
def sign_event(privkey_hex, fields):
    """BIP-340 sign a Nostr event.  TEST/FIXTURE use only.

    Deterministic aux = 32 zero bytes.
    *fields*: dict with created_at, kind, tags, content.
    Returns the complete event dict (id, pubkey, sig filled in).
    """
    d_prime = int(privkey_hex, 16)
    if d_prime == 0 or d_prime >= n:
        raise ValueError("invalid private key")

    P = _point_mul(d_prime, G)
    pubkey_hex_out = format(P[0], "064x")

    d = d_prime if P[1] % 2 == 0 else n - d_prime

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

    d_bytes = d.to_bytes(32, "big")
    t = bytes(a ^ b for a, b in zip(d_bytes, _tagged_hash("BIP0340/aux", aux)))

    pk_bytes = P[0].to_bytes(32, "big")
    rand = _tagged_hash("BIP0340/nonce", t + pk_bytes + msg)
    k_prime = int.from_bytes(rand, "big") % n
    if k_prime == 0:
        raise ValueError("nonce is zero")

    R = _point_mul(k_prime, G)
    k = k_prime if R[1] % 2 == 0 else n - k_prime

    e_hash = _tagged_hash("BIP0340/challenge",
                          R[0].to_bytes(32, "big") + pk_bytes + msg)
    e = int.from_bytes(e_hash, "big") % n

    sig = R[0].to_bytes(32, "big") + ((k + e * d) % n).to_bytes(32, "big")
    event["sig"] = sig.hex()

    return event
