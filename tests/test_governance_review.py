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

import inspect
import json
import os
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

from agent_factory.governance.packet import Packet, compile_canonical, governance_hash, load_packet
from agent_factory.governance.pin import GovernanceError, verify_pinned_fubuki
from agent_factory.governance.review import verify_review
import agent_factory.governance.review as review

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


# --- VERIFY-GOV2b regressions -------------------------------------------------------------------


def test_toctou_a_flip_after_verify_does_not_grant_review(tmp_path: Path, keys, monkeypatch) -> None:
    """F1: gpg must verify the SAME bytes that are parsed. Simulate the attacker flipping the record file
    the instant gpg finishes reading it — the bytes the signature covered (reviewed=false) must win over the
    unsigned flip (reviewed=true). On the pre-fix code the second read reparses the attacker's bytes."""
    owner = keys("owner")
    reviews = tmp_path / "reviews"
    _write_review(reviews, _H, owner, reviewed=False)  # a genuinely owner-signed record that says NOT reviewed
    attacker = json.dumps({"governance_hash": _H, "reviewed": True, "reviewer": "ATTACKER"}).encode("utf-8")
    real_run = subprocess.run

    def flipping_run(cmd, *args, **kwargs):
        result = real_run(cmd, *args, **kwargs)
        if isinstance(cmd, (list, tuple)) and "--verify" in cmd:
            (reviews / f"{_H}.json").write_bytes(attacker)  # flip AFTER gpg has read it, before any reparse
        return result

    monkeypatch.setattr(subprocess, "run", flipping_run)
    with pytest.raises(GovernanceError, match="^fubuki-packet-unreviewed"):
        verify_review(_H, reviews_dir=reviews, owner_key=_owner_key_file(tmp_path, owner))


def test_a_revoked_key_with_a_goodsig_notation_is_refused(tmp_path: Path, keys) -> None:
    """F2: gpg exits 0 with REVKEYSIG (no GOODSIG line) for a revoked key, and prints an attacker's notation
    verbatim on --status-fd. A record signed by a revoked key carrying a 'GOODSIG' notation must be refused —
    a substring is not a status line, and revocation is the owner's remedy after key theft."""
    thief = keys("thief")
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    record = reviews / f"{_H}.json"
    record.write_text(json.dumps({"governance_hash": _H, "reviewed": True}), encoding="utf-8")
    subprocess.run(
        ["gpg", "--batch", "--quiet", "--pinentry-mode", "loopback", "--passphrase", "",
         "-u", thief.fpr, "--sig-notation", "x@e.invalid=GOODSIG_not_a_status_line",
         "--detach-sign", "--armor", "--output", str(reviews / f"{_H}.json.asc"), str(record)],
        check=True, capture_output=True, text=True, timeout=60, env=thief.env,
    )
    rev_cert = thief.home / "openpgp-revocs.d" / f"{thief.fpr}.rev"
    cert = "\n".join(line[1:] if line.startswith(":") else line for line in rev_cert.read_text().splitlines())
    subprocess.run(["gpg", "--batch", "--quiet", "--import"], input=cert, check=True,
                   capture_output=True, text=True, timeout=30, env=thief.env)
    published = tmp_path / "revoked-owner.asc"
    published.write_text(
        subprocess.run(["gpg", "--batch", "--armor", "--export", thief.fpr], check=True,
                       capture_output=True, text=True, timeout=30, env=thief.env).stdout,
        encoding="utf-8",
    )
    with pytest.raises(GovernanceError, match="^fubuki-review-signature-invalid"):
        verify_review(_H, reviews_dir=reviews, owner_key=published)


def test_two_keys_in_the_owner_file_are_refused(tmp_path: Path, keys) -> None:
    """F6: the committed owner key file must hold exactly one key — a second key silently widens the trust root."""
    owner, other = keys("owner"), keys("other")
    two_keys = tmp_path / "two-keys.asc"
    two_keys.write_text(owner.pub + other.pub, encoding="utf-8")
    _write_review(tmp_path / "reviews", _H, owner)  # signed by one of the two keys — still refused
    with pytest.raises(GovernanceError, match="^fubuki-owner-key-ambiguous"):
        verify_review(_H, reviews_dir=tmp_path / "reviews", owner_key=two_keys)


def test_a_non_object_record_raises_a_governance_error(tmp_path: Path, keys) -> None:
    """F7: an owner-signed record whose JSON top level is a list must raise GovernanceError, not AttributeError."""
    owner = keys("owner")
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    record = reviews / f"{_H}.json"
    record.write_text("[1, 2, 3]", encoding="utf-8")  # valid JSON, but not an object
    owner.sign(record, reviews / f"{_H}.json.asc")
    with pytest.raises(GovernanceError, match="^fubuki-review-record-invalid"):
        verify_review(_H, reviews_dir=reviews, owner_key=_owner_key_file(tmp_path, owner))


def test_gpg_absent_raises_a_governance_error(tmp_path: Path, keys, monkeypatch) -> None:
    """F7: gpg absent from every fixed _GPG_PATHS entry raises a stable reason, not FileNotFoundError.
    GOV2d: the resolution is the module's fixed tuple, so the monkeypatch targets it — never PATH."""
    owner = keys("owner")
    _write_review(tmp_path / "reviews", _H, owner)
    monkeypatch.setattr(review, "_GPG_PATHS", (str(tmp_path / "no-gpg"),))
    with pytest.raises(GovernanceError, match="^fubuki-review-gpg-unavailable"):
        verify_review(_H, reviews_dir=tmp_path / "reviews", owner_key=_owner_key_file(tmp_path, owner))


def test_a_symlinked_record_is_refused(tmp_path: Path, keys) -> None:
    """F8: a symlinked record must not be followed (O_NOFOLLOW), matching packet.py's symlink discipline."""
    owner = keys("owner")
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    real = tmp_path / "elsewhere.json"
    real.write_text(json.dumps({"governance_hash": _H, "reviewed": True}), encoding="utf-8")
    owner.sign(real, reviews / f"{_H}.json.asc")
    (reviews / f"{_H}.json").symlink_to(real)
    with pytest.raises(GovernanceError, match="^fubuki-review-record-invalid"):
        verify_review(_H, reviews_dir=reviews, owner_key=_owner_key_file(tmp_path, owner))


# --- GOV2d: the gpg executable is a FIXED trust decision; a non-regular FD is refused, never a hang ---


def _hostile_path(tmp_path: Path, monkeypatch) -> Path:
    """A scratch gpg FIRST on the caller's PATH — the one that lies about the signature (B item 5).
    Its sentinel proves whether it was ever executed. It is never installed and lives only in tmp_path."""
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    fake = fake_bin / "gpg"
    fake.write_text(
        "#!/bin/bash\ntouch \"$(dirname \"$0\")/RAN\"\ncase \"$*\" in\n"
        "*--import*) exit 0 ;;\n"
        "*--list-keys*) printf 'pub:u:255:22:0123456789ABCDEF:::::::::\\nfpr:::::::::0123456789ABCDEF0123456789ABCDEF01234567:\\n' ;;\n"
        "*--verify*) printf '[GNUPG:] GOODSIG 0123456789ABCDEF fake\\n"
        "[GNUPG:] VALIDSIG 0123456789ABCDEF0123456789ABCDEF01234567 2026-09-22 0 0 0 0 0 0 22 01 0123456789ABCDEF0123456789ABCDEF01234567\\n' ;;\n"
        "esac\nexit 0\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake_bin}:{os.environ['PATH']}")
    return fake_bin


def _guard(seconds: int) -> None:
    """A hard wall-time guard: a hang is a test failure (TimeoutError), never a killed session (F2)."""

    def on_alarm(signum, frame) -> None:
        raise TimeoutError("hung")

    signal.signal(signal.SIGALRM, on_alarm)
    signal.alarm(seconds)


def _unguard() -> None:
    signal.alarm(0)
    signal.signal(signal.SIGALRM, signal.SIG_DFL)


def _swap_to_fifo(path: Path) -> None:
    """The attacker's move: between the pathname pre-check (t0) and the open (t1), replace a regular
    file with a mode-0600 FIFO that no writer will ever feed."""
    os.unlink(path)
    os.mkfifo(path, 0o600)


def test_gpg_is_never_resolved_from_the_callers_path(tmp_path: Path, keys, monkeypatch) -> None:
    """F1 (B item 5): the caller's PATH never picks the verifier. A hostile gpg FIRST on PATH that lies
    about the signature must be neither used nor executed; the record is unsigned (8 bytes of garbage)
    and the fixed real gpg refuses it with fubuki-review-signature-invalid."""
    owner = keys("owner")
    fake_bin = _hostile_path(tmp_path, monkeypatch)
    _write_review(tmp_path / "reviews", _H, owner)
    (tmp_path / "reviews" / f"{_H}.json.asc").write_bytes(b"XXXXXXXX")  # unsigned: 8 bytes of garbage
    with pytest.raises(GovernanceError) as excinfo:
        verify_review(_H, reviews_dir=tmp_path / "reviews", owner_key=_owner_key_file(tmp_path, owner))
    assert excinfo.value.reason == "fubuki-review-signature-invalid"
    assert not (fake_bin / "RAN").exists(), "the caller's PATH picked the verifier (F1)"


def test_a_hostile_path_does_not_break_the_real_gpg(tmp_path: Path, keys, monkeypatch) -> None:
    """Positive control: with a hostile caller PATH, a genuinely owner-signed record is still accepted —
    the fixed child PATH suffices for the real gpg. (Green at the PIN too, where the fake was the trusted
    one — the B item-5 tautology; after the fix /usr/bin/gpg is the only possible executor.)"""
    owner = keys("owner")
    _hostile_path(tmp_path, monkeypatch)
    _write_review(tmp_path / "reviews", _H, owner)
    verify_review(_H, reviews_dir=tmp_path / "reviews", owner_key=_owner_key_file(tmp_path, owner))  # no raise


def test_the_child_path_is_fixed(tmp_path: Path, keys, monkeypatch) -> None:
    """The child gpg process runs under a FIXED PATH literal (/usr/bin:/bin), never the caller's: an
    explicitly passed scratch gpg dumps the PATH it sees; even with a hostile caller PATH, the dump
    must read exactly '/usr/bin:/bin'."""
    owner = keys("owner")
    script = tmp_path / "dump-path-gpg"
    script.write_text(
        "#!/usr/bin/env python3\nimport os, sys\n"
        "open(sys.argv[0] + '.dumppath', 'w').write(os.environ.get('PATH', ''))\n"
        "sys.exit(1)\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    _hostile_path(tmp_path, monkeypatch)
    _write_review(tmp_path / "reviews", _H, owner)
    with pytest.raises(GovernanceError) as excinfo:
        verify_review(_H, reviews_dir=tmp_path / "reviews", owner_key=_owner_key_file(tmp_path, owner), gpg=script)
    assert excinfo.value.reason.startswith("fubuki-")
    assert (tmp_path / "dump-path-gpg.dumppath").read_text(encoding="utf-8") == "/usr/bin:/bin"


def test_an_explicit_gpg_must_be_an_absolute_regular_file(tmp_path: Path, keys, monkeypatch) -> None:
    """The explicit gpg= parameter (tests only) is a code decision: a bare name, a missing path, or a
    directory is refused with fubuki-review-gpg-unavailable before anything runs. An existing relative
    file is the discriminator for the is_absolute() half; is_file() alone would accept its shape."""
    owner = keys("owner")
    _write_review(tmp_path / "reviews", _H, owner)
    for bad in ("gpg", tmp_path / "missing", tmp_path):
        with pytest.raises(GovernanceError) as excinfo:
            verify_review(_H, reviews_dir=tmp_path / "reviews", owner_key=_owner_key_file(tmp_path, owner), gpg=bad)
        assert excinfo.value.reason == "fubuki-review-gpg-unavailable"

    # A relative name that exists in cwd passes Path.is_file(); it must still fail is_absolute(). If that
    # half is removed, subprocess resolves bare "gpg" through the fixed child PATH and the valid review passes.
    (tmp_path / "gpg").write_text("not executable — its existence is the discriminator\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(GovernanceError) as excinfo:
        verify_review(_H, reviews_dir=tmp_path / "reviews", owner_key=_owner_key_file(tmp_path, owner), gpg="gpg")
    assert excinfo.value.reason == "fubuki-review-gpg-unavailable"


def test_a_fifo_swapped_in_after_the_precheck_is_refused_not_hung(tmp_path: Path, keys, monkeypatch) -> None:
    """F2 (B item 6): a FIFO swapped in for the record between the pathname pre-check and the open is
    refused (fubuki-review-record-invalid: 'review record is not a regular file'), never a hang."""
    owner = keys("owner")
    reviews = tmp_path / "reviews"
    _write_review(reviews, _H, owner)
    record = reviews / f"{_H}.json"
    original = Path.is_file
    state = {"armed": False}

    def wrapper(self, *a, **kw):
        ans = original(self, *a, **kw)
        if not state["armed"] and self == record:
            state["armed"] = True
            _swap_to_fifo(record)
        return ans

    monkeypatch.setattr(Path, "is_file", wrapper)
    _guard(10)
    started = time.monotonic()
    try:
        with pytest.raises(GovernanceError) as excinfo:
            verify_review(_H, reviews_dir=reviews, owner_key=_owner_key_file(tmp_path, owner))
    finally:
        _unguard()
    assert excinfo.value.reason == "fubuki-review-record-invalid"
    assert excinfo.value.detail == "review record is not a regular file"
    assert (time.monotonic() - started) < 5


def test_a_fifo_swapped_in_for_the_signature_is_refused_not_hung(tmp_path: Path, keys, monkeypatch) -> None:
    """F2 (F8 symmetry): the same non-regular-FD refusal applies to the signature file, not just the
    record — the read primitive proves a regular file on the FD for every one of the three reads."""
    owner = keys("owner")
    reviews = tmp_path / "reviews"
    _write_review(reviews, _H, owner)
    sig = reviews / f"{_H}.json.asc"
    original = Path.is_file
    state = {"armed": False}

    def wrapper(self, *a, **kw):
        ans = original(self, *a, **kw)
        if not state["armed"] and self == sig:
            state["armed"] = True
            _swap_to_fifo(sig)
        return ans

    monkeypatch.setattr(Path, "is_file", wrapper)
    _guard(10)
    started = time.monotonic()
    try:
        with pytest.raises(GovernanceError) as excinfo:
            verify_review(_H, reviews_dir=reviews, owner_key=_owner_key_file(tmp_path, owner))
    finally:
        _unguard()
    assert excinfo.value.reason == "fubuki-review-record-invalid"
    assert excinfo.value.detail == "review record is not a regular file"
    assert (time.monotonic() - started) < 5


def test_a_fifo_at_the_record_path_is_unreviewed(tmp_path: Path, keys) -> None:
    """Two-level taxonomy: a non-regular NAME at the pre-check (t0) is fubuki-packet-unreviewed; a
    non-regular FD at the open (t1) is fubuki-review-record-invalid. A plain FIFO at the record path,
    no race, is the t0 case. (Green at the PIN too — it pins the t0 half.)"""
    owner = keys("owner")
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    os.mkfifo(reviews / f"{_H}.json", 0o600)  # a FIFO where the record must be; the .asc is absent too
    with pytest.raises(GovernanceError) as excinfo:
        verify_review(_H, reviews_dir=reviews, owner_key=_owner_key_file(tmp_path, owner))
    assert excinfo.value.reason == "fubuki-packet-unreviewed"


def test_the_read_primitive_proves_the_fd_not_the_path() -> None:
    """AF-AP-80 pairing (declared limit, not a behavioral proof): a non-regular file swapped between
    os.fstat(fd) and the read cannot be forced by these tests, so the source shape is pinned: the
    regular-file proof must be on the FD (os.fstat(fd)), never on the path (os.stat)."""
    src = inspect.getsource(review)
    assert "os.fstat(fd)" in src
    assert "os.stat(" not in src
