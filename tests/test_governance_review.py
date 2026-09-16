"""GOV2b — the reviewed bit comes from a first-party, owner-signed review record keyed by the governance hash.

VERIFY-GOV1 F2: `load_packet` failed closed on every real packet because the pinned upstream emits no review
field, and the old path read the packet's OWN (forgeable) `reviewed` field. Review now comes from a detached
signature over `docs/governance/reviews/<hash>.json`, verified against the committed owner key in an isolated
keyring. These tests use throwaway keys (the accepted-proof anchor's pattern, tests/test_proof_status.py).

The un-forgeable property is the point: a record signed by any key OTHER than the committed owner key is
refused (so a first-party store on its own is not enough to forge a review), and a record binds review to the
EXACT governance hash (a review for one packet never authorizes another).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from agent_factory.governance.packet import Packet, compile_canonical, governance_hash, load_packet
from agent_factory.governance.pin import GovernanceError, verify_pinned_fubuki
from agent_factory.governance.review import verify_review

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "upstream.lock.yaml"
PACKAGE = ROOT / "tests" / "fixtures" / "governance" / "package"
_H = "a" * 64  # a syntactically valid governance hash for the unit tests that need no compiled packet


@pytest.fixture(autouse=True)
def pinned_fubuki():
    """FUBUKI_OS_ROOT (a declared input) reaches the tests only through the production pin (AF-AP-81)."""
    value = os.environ.get("FUBUKI_OS_ROOT")
    if not value:
        pytest.fail("FUBUKI_OS_ROOT is a declared GOV1 test input")
    return verify_pinned_fubuki(Path(value).resolve(), LOCK)


class _Key:
    """A throwaway OpenPGP signing key in a SHORT GNUPGHOME (gpg-agent's socket exceeds sun_path under the
    long session basetemp — so the keyring lives under /tmp, never tmp_path)."""

    def __init__(self, name: str) -> None:
        self.home = Path(tempfile.mkdtemp(prefix=f"afgr-{name}-", dir="/tmp"))
        self.home.chmod(0o700)
        self.env = dict(os.environ, GNUPGHOME=str(self.home))
        subprocess.run(
            ["gpg", "--batch", "--quiet", "--pinentry-mode", "loopback", "--passphrase", "",
             "--quick-generate-key", f"{name} <{name}@example.invalid>", "ed25519", "sign", "0"],
            check=True, capture_output=True, text=True, timeout=120, env=self.env,
        )
        listing = subprocess.run(["gpg", "--batch", "--with-colons", "--list-secret-keys"],
                                 check=True, capture_output=True, text=True, timeout=30, env=self.env).stdout
        self.fpr = next(line.split(":")[9] for line in listing.splitlines() if line.startswith("fpr:"))
        self.pub = subprocess.run(["gpg", "--batch", "--armor", "--export", self.fpr],
                                  check=True, capture_output=True, text=True, timeout=30, env=self.env).stdout

    def sign(self, data: Path, sig: Path) -> None:
        subprocess.run(
            ["gpg", "--batch", "--quiet", "--pinentry-mode", "loopback", "--passphrase", "",
             "-u", self.fpr, "--detach-sign", "--armor", "--output", str(sig), str(data)],
            check=True, capture_output=True, text=True, timeout=60, env=self.env,
        )

    def close(self) -> None:
        subprocess.run(["gpgconf", "--kill", "all"], env=self.env, capture_output=True)
        shutil.rmtree(self.home, ignore_errors=True)


@pytest.fixture
def keys():
    made: list[_Key] = []

    def make(name: str) -> _Key:
        key = _Key(name)
        made.append(key)
        return key

    yield make
    for key in made:
        key.close()


def _owner_key_file(tmp_path: Path, key: _Key) -> Path:
    path = tmp_path / "owner-signing-key.asc"
    path.write_text(key.pub, encoding="utf-8")
    return path


def _write_review(reviews_dir: Path, hash_key: str, key: _Key, *,
                  record_hash: str | None = None, reviewed: object = True, tamper: bool = False) -> None:
    reviews_dir.mkdir(parents=True, exist_ok=True)
    record = reviews_dir / f"{hash_key}.json"
    sig = reviews_dir / f"{hash_key}.json.asc"
    body = {"governance_hash": hash_key if record_hash is None else record_hash,
            "reviewed": reviewed, "reviewer": "owner", "date": "2026-09-16T00:00:00Z"}
    record.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    key.sign(record, sig)
    if tamper:  # rewrite the record AFTER signing — the detached signature must no longer verify
        record.write_text(json.dumps({**body, "note": "rewritten after signing"}) + "\n", encoding="utf-8")


# --- verify_review unit tests --------------------------------------------------------------------


def test_valid_owner_signed_review_passes(tmp_path: Path, keys) -> None:
    owner = keys("owner")
    _write_review(tmp_path / "reviews", _H, owner)
    verify_review(_H, reviews_dir=tmp_path / "reviews", owner_key=_owner_key_file(tmp_path, owner))  # no raise


def test_absent_review_refuses(tmp_path: Path, keys) -> None:
    owner = keys("owner")
    (tmp_path / "reviews").mkdir()
    with pytest.raises(GovernanceError, match="^fubuki-packet-unreviewed"):
        verify_review(_H, reviews_dir=tmp_path / "reviews", owner_key=_owner_key_file(tmp_path, owner))


def test_review_signed_by_non_owner_is_refused(tmp_path: Path, keys) -> None:
    owner, other = keys("owner"), keys("other")
    _write_review(tmp_path / "reviews", _H, other)  # a valid signature, but from the WRONG key
    with pytest.raises(GovernanceError, match="^fubuki-review-signature-invalid"):
        verify_review(_H, reviews_dir=tmp_path / "reviews", owner_key=_owner_key_file(tmp_path, owner))


def test_review_naming_a_different_hash_does_not_authorize(tmp_path: Path, keys) -> None:
    owner = keys("owner")
    _write_review(tmp_path / "reviews", _H, owner, record_hash="b" * 64)  # owner-signed, but names another hash
    with pytest.raises(GovernanceError, match="^fubuki-review-hash-mismatch"):
        verify_review(_H, reviews_dir=tmp_path / "reviews", owner_key=_owner_key_file(tmp_path, owner))


def test_tampered_record_is_refused(tmp_path: Path, keys) -> None:
    owner = keys("owner")
    _write_review(tmp_path / "reviews", _H, owner, tamper=True)
    with pytest.raises(GovernanceError, match="^fubuki-review-signature-invalid"):
        verify_review(_H, reviews_dir=tmp_path / "reviews", owner_key=_owner_key_file(tmp_path, owner))


def test_reviewed_false_refuses(tmp_path: Path, keys) -> None:
    owner = keys("owner")
    _write_review(tmp_path / "reviews", _H, owner, reviewed=False)
    with pytest.raises(GovernanceError, match="^fubuki-packet-unreviewed"):
        verify_review(_H, reviews_dir=tmp_path / "reviews", owner_key=_owner_key_file(tmp_path, owner))


def test_a_review_for_one_hash_does_not_authorize_another(tmp_path: Path, keys) -> None:
    owner = keys("owner")
    _write_review(tmp_path / "reviews", _H, owner)  # valid record for _H only
    with pytest.raises(GovernanceError, match="^fubuki-packet-unreviewed"):
        verify_review("c" * 64, reviews_dir=tmp_path / "reviews", owner_key=_owner_key_file(tmp_path, owner))


def test_a_non_hex_hash_is_refused(tmp_path: Path, keys) -> None:
    owner = keys("owner")
    with pytest.raises(GovernanceError, match="^fubuki-review-hash-invalid"):
        verify_review("../etc/passwd", reviews_dir=tmp_path / "reviews", owner_key=_owner_key_file(tmp_path, owner))


# --- load_packet end-to-end: the reviewed bit comes ONLY from the record, never the packet body --


def test_load_packet_with_a_valid_review_returns_reviewed(tmp_path: Path, keys) -> None:
    owner = keys("owner")
    packet_hash = governance_hash(compile_canonical(PACKAGE))
    _write_review(tmp_path / "reviews", packet_hash, owner)
    packet = load_packet(PACKAGE, reviews_dir=tmp_path / "reviews", owner_key=_owner_key_file(tmp_path, owner))
    assert isinstance(packet, Packet)
    assert packet.reviewed is True
    assert packet.hash == packet_hash


def test_load_packet_without_a_record_refuses(tmp_path: Path, keys) -> None:
    # The compiled packet has no say: review is external. With no signed record for its hash, it refuses —
    # the same PACKAGE that passes above (verify_review takes no packet body, so a packet cannot self-assert).
    owner = keys("owner")
    with pytest.raises(GovernanceError, match="^fubuki-packet-unreviewed"):
        load_packet(PACKAGE, reviews_dir=tmp_path / "empty-reviews", owner_key=_owner_key_file(tmp_path, owner))
