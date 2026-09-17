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

VERIFY-GOV2b hardening: the record and its signature are read ONCE (O_NOFOLLOW), copied into the isolated
keyring, and both verified AND parsed from that one snapshot — gpg must check the same bytes we trust, or an
attacker who can write the store flips the file between two reads and an unsigned record wins (F1). The
signature is accepted only on a real `[GNUPG:] GOODSIG` status line whose signer is the one committed owner
key (F2/F6): a `GOODSIG` substring anywhere in gpg's output — e.g. an attacker-chosen notation — is not a
status line, and a revoked or expired key emits `REVKEYSIG`/`EXPKEYSIG` and no `GOODSIG`, so revocation (the
owner's remedy after key theft) is honoured. gpg runs by absolute path with `--no-options` and a minimal
environment, so an ambient `gpg.conf` or a PATH-shadowed `gpg` is not a trust channel (F5).
"""

from __future__ import annotations

import json
import os
import shutil
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
_MAX_RECORD_BYTES = 1 << 20  # a review record is a few hundred bytes; refuse anything absurd


def _is_governance_hash(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in _HEX for c in value)


def _read_no_symlink(path: Path) -> bytes:
    """Read a file's bytes, refusing to follow a symlink at the final component (O_NOFOLLOW). Raises OSError."""
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            total += len(chunk)
            if total > _MAX_RECORD_BYTES:
                raise OSError("review record too large")
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def _keyring_shape(gpg_base: list[str], env: dict[str, str]) -> tuple[int, set[str]]:
    """Return (number of primary keys, all fingerprints) in the isolated keyring."""
    listing = subprocess.run(
        [*gpg_base, "--with-colons", "--list-keys"],
        capture_output=True, text=True, timeout=30, env=env, check=False,
    )
    primary = 0
    fingerprints: set[str] = set()
    for line in listing.stdout.splitlines():
        if line.startswith("pub:"):
            primary += 1
        elif line.startswith("fpr:"):
            parts = line.split(":")
            if len(parts) > 9 and parts[9]:
                fingerprints.add(parts[9])
    return primary, fingerprints


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
    # detail-free so it reads identically whether the upstream emits no review field or a record is missing.
    if not record_path.is_file() or not sig_path.is_file():
        raise GovernanceError("fubuki-packet-unreviewed")
    if not owner_key.is_file():
        raise GovernanceError("fubuki-owner-key-missing", str(owner_key))

    gpg = shutil.which("gpg")
    if gpg is None:
        raise GovernanceError("fubuki-review-gpg-unavailable", "gpg is not on PATH")

    # Read the record, its signature, and the owner key ONCE, refusing a symlink (F1/F8). gpg then verifies a
    # COPY of exactly these bytes and we parse the SAME record bytes, so the verified bytes are the trusted
    # bytes — no second read for an attacker to race.
    try:
        record_bytes = _read_no_symlink(record_path)
        sig_bytes = _read_no_symlink(sig_path)
        owner_key_bytes = _read_no_symlink(owner_key)
    except OSError as exc:
        raise GovernanceError("fubuki-review-record-invalid", str(exc)) from exc

    with tempfile.TemporaryDirectory() as home:
        os.chmod(home, 0o700)
        rec_copy = Path(home) / "record.json"
        sig_copy = Path(home) / "record.json.asc"
        rec_copy.write_bytes(record_bytes)
        sig_copy.write_bytes(sig_bytes)
        # A minimal, hostile-free environment: gpg by absolute path, no ambient options file, C locale, only
        # GNUPGHOME + PATH forwarded (F5). The owner key is imported from the snapshot via stdin.
        env = {"GNUPGHOME": home, "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C"}
        base = [gpg, "--batch", "--quiet", "--no-options"]
        try:
            imported = subprocess.run(
                [*base, "--import"], input=owner_key_bytes,
                capture_output=True, timeout=30, env=env, check=False,
            )
            if imported.returncode != 0:
                raise GovernanceError("fubuki-owner-key-invalid", imported.stderr.decode("utf-8", "replace")[:200])
            primary, owner_fingerprints = _keyring_shape(base, env)
            verified = subprocess.run(
                [*base, "--status-fd", "1", "--verify", str(sig_copy), str(rec_copy)],
                capture_output=True, text=True, timeout=30, env=env, check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise GovernanceError("fubuki-review-gpg-unavailable", str(exc)) from exc

    # The committed owner key file must hold EXACTLY ONE key; a second key silently widens the trust root (F6).
    if primary != 1:
        raise GovernanceError("fubuki-owner-key-ambiguous", f"{primary} keys in {owner_key}")
    # Accept only a real GOODSIG status LINE whose VALIDSIG fingerprint is the committed owner's (F2/F6). A
    # revoked/expired key emits REVKEYSIG/EXPKEYSIG and no GOODSIG; a notation carrying the text "GOODSIG" is a
    # NOTATION_DATA line, not a GOODSIG line.
    status = verified.stdout.splitlines()
    good = any(line.startswith("[GNUPG:] GOODSIG ") for line in status)
    validsig = next((line.split() for line in status if line.startswith("[GNUPG:] VALIDSIG ")), None)
    signer = validsig[2] if validsig is not None and len(validsig) > 2 else None
    if verified.returncode != 0 or not good or signer is None or signer not in owner_fingerprints:
        raise GovernanceError("fubuki-review-signature-invalid", governance_hash)

    # Parse the SAME bytes gpg verified (never a re-read). Every malformed shape fails closed with a reason.
    try:
        record = json.loads(record_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GovernanceError("fubuki-review-record-invalid", str(exc)) from exc
    if not isinstance(record, dict):
        raise GovernanceError("fubuki-review-record-invalid", "record is not a JSON object")
    # The signature covers the record bytes; the record must name THIS hash and assert review.
    if record.get("governance_hash") != governance_hash:
        raise GovernanceError(
            "fubuki-review-hash-mismatch", f"record names {record.get('governance_hash')!r}, packet is {governance_hash}"
        )
    if record.get("reviewed") is not True:
        raise GovernanceError("fubuki-packet-unreviewed")
