"""First-party, owner-signed review records bind a packet's reviewed bit to its governance hash.

VERIFY-GOV1 F2: the reviewed bit must NOT come from the packet's own self-asserted field. The pinned
Fubuki upstream emits no review field at all, and a field a packet carries about itself is forgeable by
whoever shapes the sources. GOV2b sources review from a FIRST-PARTY record, keyed by the governance hash
and signed by the owner's committed key — the same trust root as the accepted-proof anchor (task #54),
applied to a runtime hash rather than a git object, so the vehicle is a detached signature over a small
record file rather than a signed tag.

The record binds review to EXACT content: the governance hash is sha256 over the canonical compiled packet,
so a one-byte change to the reviewed sources changes the hash and no prior review record applies (fail
closed). Only a signature that verifies against the committed owner key, in an isolated keyring, is
accepted — a record signed by any other key is refused, so the store being first-party is not enough on
its own to forge a review.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

from .pin import GovernanceError

# governance package = <repo>/src/agent_factory/governance/; the first-party review store and the owner's
# committed public key live under <repo>/docs/governance/ (parents[3] is the agent-factory repo root).
_REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REVIEWS_DIR = _REPO_ROOT / "docs" / "governance" / "reviews"
DEFAULT_OWNER_KEY = _REPO_ROOT / "docs" / "governance" / "owner-signing-key.asc"

_HEX = set("0123456789abcdef")


def _is_governance_hash(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in _HEX for c in value)


def verify_review(
    governance_hash: str,
    *,
    reviews_dir: str | Path | None = None,
    owner_key: str | Path | None = None,
) -> None:
    """Return if a first-party, owner-signed review record attests THIS governance hash; else fail closed.

    Raises GovernanceError with a stable reason. The caller (load_packet) computes the hash over the
    canonical packet bytes and passes it here BEFORE trusting any reviewed bit.
    """
    reviews_dir = Path(reviews_dir) if reviews_dir is not None else DEFAULT_REVIEWS_DIR
    owner_key = Path(owner_key) if owner_key is not None else DEFAULT_OWNER_KEY

    if not _is_governance_hash(governance_hash):
        raise GovernanceError("fubuki-review-hash-invalid", str(governance_hash))

    record_path = reviews_dir / f"{governance_hash}.json"
    sig_path = reviews_dir / f"{governance_hash}.json.asc"
    # Absence is never approval: no record OR no signature for this exact hash refuses. The reason is kept
    # detail-free so it reads identically whether the upstream emits no review field or a record is missing
    # (the packet's own body has no say either way — the caller knows which hash it asked about).
    if not record_path.is_file() or not sig_path.is_file():
        raise GovernanceError("fubuki-packet-unreviewed")
    if not owner_key.is_file():
        raise GovernanceError("fubuki-owner-key-missing", str(owner_key))

    # Verify the detached signature against ONLY the committed owner key, in an isolated keyring. A key not
    # in this keyring yields NO_PUBKEY / a non-zero exit, so a signature from any other key is refused.
    with tempfile.TemporaryDirectory() as home:
        os.chmod(home, 0o700)
        env = dict(os.environ, GNUPGHOME=home)
        imported = subprocess.run(
            ["gpg", "--batch", "--quiet", "--import", str(owner_key)],
            capture_output=True, text=True, timeout=30, env=env, check=False,
        )
        if imported.returncode != 0:
            raise GovernanceError("fubuki-owner-key-invalid", imported.stderr.strip()[:200])
        verified = subprocess.run(
            ["gpg", "--batch", "--quiet", "--status-fd", "1", "--verify", str(sig_path), str(record_path)],
            capture_output=True, text=True, timeout=30, env=env, check=False,
        )
    if verified.returncode != 0 or "GOODSIG" not in verified.stdout:
        raise GovernanceError("fubuki-review-signature-invalid", governance_hash)

    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GovernanceError("fubuki-review-record-invalid", str(exc)) from exc
    # The signature covers the record bytes; the record must name THIS hash and assert review. A record
    # signed for a different hash cannot authorize this packet even though its signature is valid.
    if record.get("governance_hash") != governance_hash:
        raise GovernanceError(
            "fubuki-review-hash-mismatch", f"record names {record.get('governance_hash')!r}, packet is {governance_hash}"
        )
    if record.get("reviewed") is not True:
        raise GovernanceError("fubuki-packet-unreviewed")
