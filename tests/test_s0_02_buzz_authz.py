"""S0-02 — Buzz authorization/freshness: fixtures, oracle table, checker.

Deterministic and LLM-free. Every test either reads committed bytes, reads the
pinned upstream source, or drives the checker over a bundle built from the
committed fixtures.

The pinned-source tests read ``S0_02_BUZZ_SRC`` (sandbox default
``/home/user/nerdherderdani/buzz``). Following the S0-01 corpus rule
(VERIFY-CK10 F-R10-25): venue set and the tree missing is a FAILURE, never a
skip; only an unset venue (CI) skips, and it skips by declaration.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PROOF = ROOT / "proofs" / "S0-02"
FIXTURES = PROOF / "fixtures"
PASS_BUNDLE = FIXTURES / "evidence-pass"
BLANKET_BUNDLE = FIXTURES / "evidence-blanket"
CHECKER = PROOF / "check_buzz_authz.py"
BUILDER = PROOF / "tools" / "build_fixtures.py"
RUNNER = PROOF / "tools" / "pc" / "run_s0_02_legs.sh"
DELIVER = PROOF / "tools" / "pc" / "deliver_event.py"
SPEC = PROOF / "spec.json"
S0_01_IDENTITIES = ROOT / "proofs" / "S0-01" / "fixtures" / "identities.json"
S0_02_IDENTITIES = FIXTURES / "identities-s0-02.json"

# The upstream tree the oracle rows are pinned to. Venue-declared, never guessed.
BUZZ_SRC_ENV = "S0_02_BUZZ_SRC"
BUZZ_SRC_DEFAULT = "/home/user/nerdherderdani/buzz"
BUZZ_PIN = "1c8321cd08feb597f8bcff5195c21148fb3e98ed"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


checker = _load("s0_02_check_buzz_authz", CHECKER)
builder = _load("s0_02_build_fixtures", BUILDER)
oracle = _load("s0_02_denial_table", PROOF / "oracle" / "denial_table.py")
nv = _load("s0_02_nostr_verify", ROOT / "proofs" / "S0-01" / "tools" / "nostr_verify.py")

FIXTURE_NAMES = ("pos-allowed",) + oracle.NEGATIVE_FIXTURES


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _bundle(tmp_path: Path, src: Path = PASS_BUNDLE) -> Path:
    """A writable copy of a committed bundle. Mutants NEVER touch the tree."""
    dst = tmp_path / src.name
    shutil.copytree(src, dst)
    return dst


def _run_checker(bundle_root: Path, legs: str = "legs"):
    """Drive the checker in-process against a bundle's own anchors."""
    anchors = checker.Anchors.from_synthetic_root(bundle_root)
    return checker.check_bundle(bundle_root / legs, anchors)


def _expect_failure(bundle_root: Path, needle: str, legs: str = "legs"):
    with pytest.raises(checker.Failure) as exc:
        _run_checker(bundle_root, legs)
    assert needle in str(exc.value), f"expected {needle!r} in {exc.value!r}"
    return str(exc.value)


def _leg(bundle_root: Path, name: str) -> Path:
    return bundle_root / "legs" / name


def _set_delivery_outcome(blob: dict, *, accepted: bool, status: int, echoed: bool) -> None:
    blob["accepted"] = accepted
    blob["http_status"] = status
    blob["event_id_echoed"] = echoed


def _set_delivery_event_id(blob: dict, event_id: str) -> None:
    blob["event_id"] = event_id
    if blob.get("accepted"):
        blob["event_id_echoed"] = True


def _rewrite(path: Path, mutate):
    blob = json.loads(path.read_text())
    mutate(blob)
    path.write_text(json.dumps(blob, indent=1, sort_keys=True) + "\n")


def _buzz_src() -> Path:
    """The pinned upstream tree, or a declared skip. Never a silent pass."""
    raw = os.environ.get(BUZZ_SRC_ENV)
    if raw is None:
        venue = os.environ.get("S0_01_VENUE")
        if venue in (None, "ci"):
            pytest.skip(
                f"{BUZZ_SRC_ENV} unset and venue={venue!r} — the pinned buzz "
                f"checkout is a DECLARED input; CI skips by declaration"
            )
        raw = BUZZ_SRC_DEFAULT
    path = Path(raw)
    assert path.is_dir(), (
        f"{BUZZ_SRC_ENV}={raw} is declared but absent — a declared input that is "
        f"missing is a FAILURE, never a skip"
    )
    return path


def test_buzz_src_gate_skips_in_ci_but_fails_on_explicit_absent(monkeypatch):
    """The venue gate contract: CI (venue 'ci' or unset, no explicit source)
    SKIPS by declaration; an explicit but absent S0_02_BUZZ_SRC FAILS loud, never
    a silent skip (the regression behind the stage0-ci `tests` job going red)."""
    # CI shape: venue declared 'ci', no explicit source -> skip by declaration
    monkeypatch.delenv(BUZZ_SRC_ENV, raising=False)
    monkeypatch.setenv("S0_01_VENUE", "ci")
    with pytest.raises(pytest.skip.Exception):
        _buzz_src()
    # no venue declared, no explicit source -> also a declared skip
    monkeypatch.delenv("S0_01_VENUE", raising=False)
    with pytest.raises(pytest.skip.Exception):
        _buzz_src()
    # an EXPLICIT but absent source is a FAILURE, never a skip (anti-hollow-green)
    monkeypatch.setenv(BUZZ_SRC_ENV, "/nonexistent/buzz-src-xyzzy")
    with pytest.raises(AssertionError):
        _buzz_src()


# ---------------------------------------------------------------------------
# 1. the fixture builder: determinism and the offline preconditions
# ---------------------------------------------------------------------------
def test_committed_fixtures_equal_a_fresh_build():
    """FIXTURE-DRIFT: the committed bytes are exactly what the builder emits."""
    rc = builder.main([str(BUILDER), "--check"])
    assert rc == 0, "committed fixtures differ from a fresh deterministic build"


def test_fixture_build_is_byte_identical_across_two_runs():
    a = {k: builder._serialise(v) for k, v in builder.build_all().items()}
    b = {k: builder._serialise(v) for k, v in builder.build_all().items()}
    assert a == b, "the builder is not deterministic across two runs in one process"


def test_every_bundle_delivery_uses_the_real_producer_normalizer():
    for bundle in (PASS_BUNDLE, BLANKET_BUNDLE):
        for path in sorted((bundle / "legs").rglob("delivery.json")):
            receipt = json.loads(path.read_text())
            expected = builder.deliver_event._normalise(
                receipt["http_status"],
                builder._raw_delivery_response(
                    accepted=receipt["accepted"],
                    event_id=receipt["event_id"],
                    message=receipt["message"],
                ),
                receipt["event_id"],
            )
            # The receipt was built FROM the raw body, so round-tripping it
            # through the raw synthesizer and the live normalizer must be the
            # identity. For a refusal whose message was the api_error body the
            # synthesized raw wraps it once more; unwrap that single layer.
            if not receipt["accepted"] and receipt["message"].startswith("{\"error\":"):
                inner = json.loads(receipt["message"])["error"]
                expected = builder.deliver_event._normalise(
                    receipt["http_status"],
                    builder._raw_delivery_response(
                        accepted=False, event_id=receipt["event_id"], message=inner,
                    ),
                    receipt["event_id"],
                )
            assert receipt == expected, f"{path} drifted from deliver_event._normalise"


def test_every_named_fixture_exists_and_names_itself():
    for name in FIXTURE_NAMES:
        blob = json.loads((FIXTURES / f"{name}.json").read_text())
        assert blob["fixture"] == name
        assert blob["buzz_commit"] == BUZZ_PIN


def test_positive_specimen_verifies():
    pos = json.loads((FIXTURES / "pos-allowed.json").read_text())
    ok, reason = nv.verify_event(pos["event"])
    assert ok, reason
    assert pos["expected"]["turns"] == 1
    assert pos["expected"]["failure_reason"] is None


def test_bad_signature_specimen_is_rejected_by_verify_event():
    """SIGNATURE-FLIP-UNDETECTED: the offline precondition for the reason."""
    bad = json.loads((FIXTURES / "neg-bad-signature.json").read_text())
    ok, _reason = nv.verify_event(bad["event"])
    assert not ok, "the bad-signature specimen still verifies"


def test_bad_signature_specimen_differs_from_positive_only_in_the_signature():
    pos = json.loads((FIXTURES / "pos-allowed.json").read_text())["event"]
    bad = json.loads((FIXTURES / "neg-bad-signature.json").read_text())["event"]
    assert bad["sig"] != pos["sig"]
    for key in ("id", "pubkey", "kind", "tags", "content", "created_at"):
        assert bad[key] == pos[key], f"{key} differs — the leg would not isolate the signature"


def test_replayed_specimen_is_the_positive_event_id():
    pos = json.loads((FIXTURES / "pos-allowed.json").read_text())["event"]
    rep = json.loads((FIXTURES / "neg-replayed.json").read_text())
    assert rep["event"]["id"] == pos["id"]
    assert rep["replay_of"] == "pos-allowed"
    assert rep["expected"]["replay_of_event_id"] == pos["id"]


def test_stale_specimen_created_at_clears_the_relay_window():
    """STALE-WINDOW-UNPINNED: the offset must clear buzz-relay's +/-900s window."""
    stale = json.loads((FIXTURES / "neg-stale.json").read_text())
    offset = stale["template"]["created_at_offset_s"]
    assert offset < 0
    assert abs(offset) > checker.RELAY_DRIFT_WINDOW_S, (
        f"offset {offset}s does not clear the {checker.RELAY_DRIFT_WINDOW_S}s window"
    )


def test_self_authored_specimen_names_the_agent_identity():
    ids = json.loads((ROOT / "proofs" / "S0-01" / "fixtures" / "identities.json").read_text())
    blob = json.loads((FIXTURES / "neg-self-authored.json").read_text())
    assert blob["signer"]["role"] == "agent"
    assert blob["signer"]["expected_pubkey"] == ids["agent"]


def test_unauthorized_specimen_is_not_a_known_identity():
    """D-038 (B10): the leg binds to ONE host-local nonmember, the S0-02 file's
    value, which is none of the S0-01 identities and not owner2. Checked in the
    committed fixture the PC runner reads and in a fresh build."""
    ids = json.loads((ROOT / "proofs" / "S0-01" / "fixtures" / "identities.json").read_text())
    s0_02 = json.loads(S0_02_IDENTITIES.read_text())
    blob = json.loads((FIXTURES / "neg-unauthorized.json").read_text())
    known = {v for k, v in ids.items() if k != "relay_url"}
    for signer in (blob["signer"], builder.build_all()["neg-unauthorized"]["signer"]):
        assert signer["role"] == "nonmember"
        assert signer["expected_pubkey"] == s0_02["nonmember"]
        assert signer["expected_pubkey"] not in known
        assert signer["expected_pubkey"] != s0_02["owner2"]
    assert blob["event"]["pubkey"] not in known


def test_no_committed_fixture_carries_a_private_key():
    """A 64-hex value in a fixture is a pubkey, an event id or a signature.
    A secret would arrive under a KEY, so the key names are screened (prose that
    merely says "secret store" is not a secret)."""
    banned = ("privkey", "private_key", "nsec", "seckey", "secret_key", "sk")

    def walk(node, where):
        if isinstance(node, dict):
            for k, v in node.items():
                assert k.lower() not in banned, f"{where}: key {k!r} looks like a secret"
                walk(v, f"{where}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{where}[{i}]")

    for path in sorted(FIXTURES.glob("*.json")):
        walk(json.loads(path.read_text()), path.name)


def test_every_negative_fixture_carries_its_own_expected_failure_block():
    """seed:376-380 - the reason lives IN the fixture so it cannot drift."""
    for name in oracle.NEGATIVE_FIXTURES:
        blob = json.loads((FIXTURES / f"{name}.json").read_text())
        assert blob["expected"]["turns"] == 0
        assert blob["expected"]["failure_reason"] == oracle.row(name)["reason"]
        assert blob["expected"]["mechanism"].count(":") == 1


def test_the_four_seed_reasons_are_all_present():
    """AF-AP-27: the frozen seed contract's four reasons are not reshaped."""
    reasons = {json.loads((FIXTURES / f"{n}.json").read_text())["expected"]["failure_reason"]
               for n in oracle.NEGATIVE_FIXTURES}
    for seed_reason in oracle.SEED_REASONS:
        assert seed_reason in reasons, f"seed reason {seed_reason!r} missing"
    assert oracle.FIFTH_REASON in reasons
    assert oracle.SIXTH_REASON in reasons


def test_not_allowlisted_specimen_is_relay_accepted_user2():
    ids = json.loads((ROOT / "proofs" / "S0-01" / "fixtures" / "identities.json").read_text())
    blob = json.loads((FIXTURES / "neg-not-allowlisted.json").read_text())
    assert blob["signer"]["expected_pubkey"] == ids["user2"]
    assert blob["signer"]["role"] == "user2"
    assert blob["signer"]["specimen_pubkey"] != ids["user2"]
    assert oracle.row("neg-not-allowlisted")["evidence"] == oracle.EV_BUZZACP_LOG


def test_revoked_specimen_signs_as_the_second_fixture_owner():
    """D-037 (B10): the revoked leg removes owner2, a SECOND fixture owner, so it
    never touches the owner the other legs sign as. Role and expected_pubkey name
    owner2 (the S0-02 file's value, not the S0-01 owner) in the committed fixture
    the PC runner reads (role_for) and in a fresh build."""
    ids = json.loads(S0_01_IDENTITIES.read_text())
    s0_02 = json.loads(S0_02_IDENTITIES.read_text())
    committed = json.loads((FIXTURES / "revoked.json").read_text())["signer"]
    for signer in (committed, builder.build_all()["revoked"]["signer"]):
        assert signer["role"] == "owner2"
        assert signer["expected_pubkey"] == s0_02["owner2"]
        assert signer["expected_pubkey"] != ids["owner"]


def test_every_fixture_signer_is_pinned():
    """B10: only the revoked and unauthorized signers moved; the other six keep
    their role and key. Committed bytes and a fresh build."""
    ids = json.loads(S0_01_IDENTITIES.read_text())
    s0_02 = json.loads(S0_02_IDENTITIES.read_text())
    want = {
        "pos-allowed": ("owner", ids["owner"]),
        "neg-unauthorized": ("nonmember", s0_02["nonmember"]),
        "neg-bad-signature": ("owner", ids["owner"]),
        "neg-replayed": ("owner", ids["owner"]),
        "neg-stale": ("owner", ids["owner"]),
        "neg-self-authored": ("agent", ids["agent"]),
        "neg-not-allowlisted": ("user2", ids["user2"]),
        "revoked": ("owner2", s0_02["owner2"]),
    }
    assert set(want) == set(FIXTURE_NAMES)
    fresh = builder.build_all()
    for name in FIXTURE_NAMES:
        committed = json.loads((FIXTURES / f"{name}.json").read_text())["signer"]
        for signer in (committed, fresh[name]["signer"]):
            assert (signer["role"], signer["expected_pubkey"]) == want[name], name


def test_s0_02_identity_file_is_the_provenance_record():
    """B10: exactly owner2 and nonmember, in canonical bytes (two-space indent,
    sorted keys, trailing newline), each value the public key PROVENANCE.md
    records, and no key shared with the S0-01 file."""
    raw = S0_02_IDENTITIES.read_text()
    s0_02 = json.loads(raw)
    assert sorted(s0_02) == ["nonmember", "owner2"]
    assert raw == json.dumps(s0_02, indent=2, sort_keys=True) + "\n"
    prov = (FIXTURES / "PROVENANCE.md").read_text()
    for role, pub in s0_02.items():
        assert f"`{role}` `{pub}`" in prov, f"{role} is not the PROVENANCE record"
    assert not set(s0_02) & set(json.loads(S0_01_IDENTITIES.read_text()))


def _point_identities(monkeypatch, tmp_path: Path, s0_02: dict) -> tuple[Path, Path]:
    """Point the builder's two identity paths at temporary files: a byte copy of
    the S0-01 file and the given S0-02 map. The committed files are never touched."""
    s0_01_path = tmp_path / "identities.json"
    s0_01_path.write_bytes(S0_01_IDENTITIES.read_bytes())
    s0_02_path = tmp_path / "identities-s0-02.json"
    s0_02_path.write_text(json.dumps(s0_02, indent=2, sort_keys=True) + "\n")
    monkeypatch.setattr(builder, "IDENTITIES", s0_01_path)
    monkeypatch.setattr(builder, "IDENTITIES_S0_02", s0_02_path)
    return s0_01_path, s0_02_path


def test_identities_merges_both_files_and_writes_neither(tmp_path, monkeypatch):
    """B10, the normal path: the S0-01 map plus the S0-02 keys, read from wherever
    the two paths point (the temporary values differ from the committed ones), and
    neither file written."""
    s0_01 = json.loads(S0_01_IDENTITIES.read_text())
    real = builder._identities()
    assert real == {**s0_01, **json.loads(S0_02_IDENTITIES.read_text())}
    assert set(real) - set(s0_01) == {"owner2", "nonmember"}
    extra = {"nonmember": "c" * 64, "owner2": "d" * 64}
    paths = _point_identities(monkeypatch, tmp_path, extra)
    before = [(p.read_bytes(), p.stat().st_mtime_ns) for p in paths]
    assert builder._identities() == {**s0_01, **extra}
    assert [(p.read_bytes(), p.stat().st_mtime_ns) for p in paths] == before


@pytest.mark.parametrize("key,value", [
    ("owner", None),        # None = the S0-01 file's own value: agreeing is still a collision
    ("owner", "e" * 64),    # a different value would re-point every owner leg
    ("channel", "e" * 64),  # any S0-01 key, not only the pubkey roles
])
def test_identities_refuses_a_key_in_both_files(tmp_path, monkeypatch, key, value):
    """B10: a key present in both files is refused, and the message names it."""
    if value is None:
        value = json.loads(S0_01_IDENTITIES.read_text())[key]
    _point_identities(monkeypatch, tmp_path, {"nonmember": "c" * 64, key: value})
    with pytest.raises(SystemExit) as exc:
        builder._identities()
    assert str(exc.value) == (
        f"identities: key {key!r} is in both identities.json and identities-s0-02.json"
    )


@pytest.mark.parametrize("value", [
    "A" * 64,         # uppercase
    "a" * 63,         # short
    "a" * 65,         # long: an unanchored match would take its prefix
    "g" * 64,         # not hex
    "a" * 64 + "\n",  # a trailing newline: a '$'-anchored match would accept it
    64,               # not a string
    None,
])
def test_identities_refuses_a_malformed_s0_02_value(tmp_path, monkeypatch, value):
    """B10: an S0-02 value that is not 64 lowercase hex is refused, and the
    message names its key."""
    _point_identities(monkeypatch, tmp_path, {"nonmember": value, "owner2": "d" * 64})
    with pytest.raises(SystemExit) as exc:
        builder._identities()
    assert str(exc.value) == (
        "identities: identities-s0-02.json value for 'nonmember' is not 64 lowercase hex"
    )


@pytest.mark.parametrize("name", ["pass", "blanket"])
def test_committed_bundle_equals_a_fresh_build(tmp_path, name):
    """Issue #45 VF-1: --check compares the eight top-level fixtures only, so a
    builder mutant that changes only a bundle (VERIFY-B9-R1's M18 and M19)
    survived T2. A fresh build_bundle must equal the committed tree, file for
    file and byte for byte."""
    committed = FIXTURES / f"evidence-{name}"
    fresh = tmp_path / f"evidence-{name}"
    builder.build_bundle(name, fresh)

    def tree(root: Path) -> dict:
        return {p.relative_to(root).as_posix(): p.read_bytes()
                for p in sorted(root.rglob("*")) if p.is_file()}

    want, got = tree(committed), tree(fresh)
    assert sorted(got) == sorted(want), f"evidence-{name}: the file sets differ"
    drift = [rel for rel in sorted(want) if got[rel] != want[rel]]
    assert drift == [], f"evidence-{name}: committed bytes differ from a fresh build: {drift}"


# ---------------------------------------------------------------------------
# 2. the oracle table against the pinned upstream source
# ---------------------------------------------------------------------------
def test_pinned_tree_is_the_locked_commit():
    src = _buzz_src()
    proc = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"],
                          capture_output=True, text=True)
    assert proc.returncode == 0, (
        f"{BUZZ_SRC_ENV}={src} is not a git checkout: "
        f"{(proc.stderr or proc.stdout).strip()}"
    )
    head = proc.stdout.strip()
    assert head == BUZZ_PIN, f"buzz checkout is {head}, upstream.lock.yaml pins {BUZZ_PIN}"


def test_pinned_tree_non_git_path_is_a_named_failure(tmp_path, monkeypatch):
    fake = tmp_path / "buzz"
    fake.mkdir()
    monkeypatch.setenv(BUZZ_SRC_ENV, str(fake))
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    with pytest.raises(AssertionError, match="is not a git checkout"):
        test_pinned_tree_is_the_locked_commit()


@pytest.mark.parametrize("row", oracle.ROWS, ids=[r["fixture"] for r in oracle.ROWS])
def test_oracle_row_line_still_carries_its_pattern(row):
    """ORACLE-LINE-DRIFT: every cited file:line really holds the cited text."""
    src = _buzz_src()
    path = src / row["src"]
    assert path.is_file(), f"{row['src']} absent from the pinned tree"
    lines = path.read_text().splitlines()
    assert row["line"] <= len(lines), f"{row['src']} has {len(lines)} lines, row cites {row['line']}"
    line = lines[row["line"] - 1]
    assert row["src_pattern"] in line, (
        f"{row['src']}:{row['line']} is {line.strip()!r}, "
        f"which does not carry {row['src_pattern']!r}"
    )


def test_oracle_secondary_silent_drop_row_is_pinned_too():
    src = _buzz_src()
    row = oracle.row("neg-stale")["silent_drop_secondary"]
    line = (src / row["src"]).read_text().splitlines()[row["line"] - 1]
    assert row["src_pattern"] in line


def test_oracle_replay_defense_in_depth_line_is_pinned_too():
    """D-036 keeps buzz-acp's own drop line as the replay row's defense-in-depth
    field, pinned to its upstream line the same way the rows are."""
    src = _buzz_src()
    row = oracle.row("neg-replayed")["defense_in_depth"]
    line = (src / row["src"]).read_text().splitlines()[row["line"] - 1]
    assert row["src_pattern"] in line, line
    assert row["observable"] in row["src_pattern"]
    assert (row["decided_by"], row["evidence"]) == ("buzz-acp", oracle.EV_BUZZACP_LOG)


def test_replay_row_is_the_relay_duplicate_receipt():
    """D-036 clause 2 at its source: the replay row names the relay, and the
    pinned kind-9 duplicate branch returns exactly the receipt the row names
    (ingest.rs:3192-3197); the bridge answers it as {event_id, accepted,
    message} (bridge.rs:963-968), the body deliver_event._normalise reads."""
    src = _buzz_src()
    row = oracle.row("neg-replayed")
    assert (row["decided_by"], row["evidence"], row["observable"]) == (
        "buzz-relay", oracle.EV_DELIVERY, "duplicate:")
    assert f'"{row["observable"]}"' in row["src_pattern"]
    lines = (src / row["src"]).read_text().splitlines()
    block = [ln.strip() for ln in lines[row["line"] - 5:row["line"] + 1]]
    assert block == [
        "if !was_inserted {", "return Ok(IngestResult {", "event_id: event_id_hex,",
        "accepted: true,", 'message: "duplicate:".into(),', "});",
    ], block
    bridge = (src / "crates/buzz-relay/src/api/bridge.rs").read_text().splitlines()
    assert [ln.strip() for ln in bridge[964:967]] == [
        '"event_id": result.event_id,', '"accepted": result.accepted,',
        '"message": result.message,',
    ], bridge[962:968]


def test_oracle_prose_file_line_references_exist():
    src = _buzz_src()
    fields = ("discrepancy", "note")
    refs = []
    for row in oracle.ROWS:
        for field in fields:
            text = row.get(field) or ""
            refs.extend((row["fixture"], field, name, int(line))
                        for name, line in re.findall(r"([\w-]+\.rs):(\d+)", text))
    assert refs, "control: oracle prose contains no source references"
    rust_files = {}
    for path in src.rglob("*.rs"):
        rust_files.setdefault(path.name, []).append(path)
    for fixture, field, name, line in refs:
        assert name in rust_files, f"{fixture}.{field}: {name} absent from pinned source"
        candidates = rust_files[name]
        assert any(line <= len(path.read_text().splitlines()) for path in candidates), (
            f"{fixture}.{field}: {name}:{line} outside every pinned {name}"
        )


def _rust_code_lines(text: str) -> list[tuple[int, str]]:
    """Return production Rust lines with comments and cfg(test) items removed.

    This small structural scanner tracks comments, strings and brace depth. It
    is deliberately not a Rust parser; the negative controls below pin the only
    syntax classes this proof relies on.
    """
    lines = text.splitlines()
    clean = []
    in_block_comment = False
    in_string = False
    in_char = False
    escaped = False
    for raw in lines:
        out = []
        i = 0
        while i < len(raw):
            pair = raw[i:i + 2]
            ch = raw[i]
            if in_block_comment:
                if pair == "*/":
                    in_block_comment = False
                    i += 2
                else:
                    i += 1
                continue
            if in_string or in_char:
                out.append(" " if ch in "{}" else ch)
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif in_string and ch == '"':
                    in_string = False
                elif in_char and ch == "'":
                    in_char = False
                i += 1
                continue
            if pair == "/*":
                in_block_comment = True
                i += 2
                continue
            if pair == "//":
                break
            out.append(ch)
            if ch == '"':
                in_string = True
            elif ch == "'":
                in_char = True
            i += 1
        clean.append("".join(out))

    excluded = set()
    pending_test_attr = False
    item_start = None
    item_depth = 0
    for idx, line in enumerate(clean):
        stripped = line.strip()
        if pending_test_attr:
            excluded.add(idx)
            if "{" in line:
                item_start = idx
                item_depth = line.count("{") - line.count("}")
                pending_test_attr = False
                if item_depth <= 0:
                    item_start = None
            continue
        if stripped == "#[cfg(test)]":
            excluded.add(idx)
            pending_test_attr = True
            continue
        if item_start is not None:
            excluded.add(idx)
            item_depth += line.count("{") - line.count("}")
            if item_depth <= 0:
                item_start = None

    return [(i + 1, line) for i, line in enumerate(clean) if i not in excluded]


def _production_verify_sites() -> list[str]:
    """Every verify_event/.verify()/aliased verify call in production Rust."""
    src = _buzz_src() / "crates" / "buzz-acp" / "src"
    sites = []
    for rs in sorted(src.glob("*.rs")):
        code = _rust_code_lines(rs.read_text())
        aliases = set()
        for _line_no, line in code:
            match = re.search(r"\bverify_event\s+as\s+([A-Za-z_][A-Za-z0-9_]*)", line)
            if match:
                aliases.add(match.group(1))
        for line_no, line in code:
            direct = "verify_event(" in line or ".verify()" in line
            aliased = any(re.search(rf"\b{re.escape(alias)}\s*\(", line) for alias in aliases)
            if direct or aliased:
                sites.append(f"{rs.name}:{line_no}")
    return sites


def _channel_event_region(relay_text: str) -> tuple[int, int]:
    """Derive the RelayMessage EVENT match-arm range by brace depth."""
    lines = relay_text.splitlines()
    start = next(i for i, line in enumerate(lines, 1)
                 if '"EVENT" => {' in line)
    region = _rust_code_lines("\n".join(lines[start - 1:]))
    depth = 0
    for relative, line in region:
        line_no = start + relative - 1
        depth += line.count("{") - line.count("}")
        if line_no > start and depth == 0:
            return start, line_no
    raise AssertionError("relay EVENT match arm did not close")


def _copy_buzz_acp_src(tmp_path: Path) -> Path:
    src = _buzz_src()
    dst = tmp_path / "buzz"
    shutil.copytree(src / "crates" / "buzz-acp" / "src",
                    dst / "crates" / "buzz-acp" / "src")
    return dst


def test_verify_site_scan_rejects_a_channel_path_plant(tmp_path, monkeypatch):
    src = _copy_buzz_acp_src(tmp_path)
    relay_path = src / "crates" / "buzz-acp" / "src" / "relay.rs"
    text = relay_path.read_text()
    marker = '"EVENT" => {'
    assert marker in text
    relay_path.write_text(text.replace(marker, marker + "\nverify_event(&event);", 1))
    monkeypatch.setenv(BUZZ_SRC_ENV, str(src))
    sites = _production_verify_sites()
    assert any(site.startswith("relay.rs:") for site in sites), sites
    start, end = _channel_event_region(relay_path.read_text())
    planted = [site for site in sites if site.startswith("relay.rs:")
               and start <= int(site.split(":")[1]) <= end]
    assert planted, "control: the channel-path mutant was not observed"


def test_verify_site_scan_finds_an_aliased_call(tmp_path, monkeypatch):
    src = _copy_buzz_acp_src(tmp_path)
    relay_path = src / "crates" / "buzz-acp" / "src" / "relay.rs"
    relay_path.write_text(
        "use buzz_core::verify_event as v;\nfn probe(event: &Event) { v(event); }\n"
        + relay_path.read_text()
    )
    monkeypatch.setenv(BUZZ_SRC_ENV, str(src))
    sites = _production_verify_sites()
    assert "relay.rs:2" in sites, sites


def test_verify_site_scan_ignores_cfg_test_items_and_comments(tmp_path, monkeypatch):
    src = _copy_buzz_acp_src(tmp_path)
    relay_path = src / "crates" / "buzz-acp" / "src" / "relay.rs"
    relay_path.write_text(
        "#[cfg(test)]\nmod early_tests {\n"
        "  fn fake(event: &Event) { verify_event(event); event.verify(); }\n}\n"
        "/* verify_event(event); event.verify(); */\n"
        + relay_path.read_text()
    )
    monkeypatch.setenv(BUZZ_SRC_ENV, str(src))
    sites = set(_production_verify_sites())
    assert not {"relay.rs:3", "relay.rs:5"} & sites, sites
    assert len(sites) == 6, sites


def test_buzz_acp_performs_no_signature_check_on_a_channel_event():
    """The exact whole-file site set and the channel EVENT path are pinned."""
    known = {
        "engram_fetch.rs:122",
        "lib.rs:256",
        "lib.rs:1574",
        "lib.rs:6082",
        "pool.rs:3385",
        "pool.rs:3495",
    }
    actual = set(_production_verify_sites())
    assert actual == known, (
        f"buzz-acp signature-check sites changed: added={sorted(actual - known)}, "
        f"gone={sorted(known - actual)}"
    )
    relay = (_buzz_src() / "crates" / "buzz-acp" / "src" / "relay.rs").read_text()
    start, end = _channel_event_region(relay)
    channel_sites = [site for site in actual
                     if site.startswith("relay.rs:")
                     and start <= int(site.split(":")[1]) <= end]
    assert not channel_sites, (
        f"buzz-acp verifies a channel event inside relay.rs:{start}-{end}: {channel_sites}"
    )


def test_buzz_acp_has_no_per_event_freshness_constant_for_channel_events():
    """The DISCREPANCY behind neg-stale, asserted against the source."""
    src = _buzz_src() / "crates" / "buzz-acp" / "src"
    consts = []
    for rs in sorted(src.glob("*.rs")):
        for i, line in enumerate(rs.read_text().splitlines(), 1):
            s = line.strip()
            if s.startswith("const ") and ("FRESHNESS" in s or "MAX_AGE" in s or "STALE" in s):
                consts.append(f"{rs.name}:{i}:{s}")
    assert len(consts) == 1 and consts[0].startswith("lib.rs:1563:"), (
        f"buzz-acp's freshness constants changed: {consts}"
    )
    assert "OBSERVER_CONTROL_FRESHNESS_SECS" in consts[0]


def _is_wall_clock_freshness_rule(line: str) -> bool:
    """A same-expression created_at/wall-clock comparison, not mere co-occurrence."""
    created_at = r"(?:\bcreated_at\b|\.created_at\b)"
    wall_clock = (
        r"(?:\bnow\b|\bSystemTime\b|\bInstant\b|\belapsed\s*\(|"
        r"\bsaturating_(?:add|sub)\s*\()"
    )
    relation = r"(?:[<>]=?|checked_(?:add|sub)|duration_since|saturating_(?:add|sub))"
    return bool(re.search(
        rf"(?:{created_at}[^;\n]*{relation}[^;\n]*{wall_clock}|"
        rf"{wall_clock}[^;\n]*{relation}[^;\n]*{created_at})",
        line,
    ))


def test_buzz_acp_has_no_wall_clock_freshness_rule_on_the_channel_event_path():
    """created_at can reach config, but the default channel path has no clock comparison.

    DOCUMENTED LIMIT (B3 item 4): the scanner's class is the DIRECT same-line
    comparison; a rule split across statements (as in VERIFY-B1's three-statement
    plant) is outside it (see the negative control below, which pins the limit
    so the claim can never silently widen).
    """
    src = _buzz_src() / "crates" / "buzz-acp" / "src"
    relay = (src / "relay.rs").read_text()
    start, end = _channel_event_region(relay)
    region = "\n".join(line for _n, line in _rust_code_lines(
        "\n".join(relay.splitlines()[start - 1:end])
    ))
    offenders = [line.strip() for line in region.splitlines()
                 if _is_wall_clock_freshness_rule(line)]
    assert not offenders, (
        f"relay channel EVENT region relay.rs:{start}-{end} gained a wall-clock "
        f"created_at comparison: {offenders}"
    )


def test_wall_clock_freshness_scan_rejects_an_inline_rule():
    assert _is_wall_clock_freshness_rule(
        "if event.created_at < SystemTime::now() - MAX_AGE { return; }"
    )
    assert _is_wall_clock_freshness_rule(
        "if Instant::now().duration_since(event.created_at) > freshness { return; }"
    )
    # VERIFY-B1's exact M-B plant: a local `now` value and saturating arithmetic
    # must not evade the rule scanner merely because no `now()` call is inline.
    assert _is_wall_clock_freshness_rule(
        "if now.saturating_sub(event.created_at.as_u64()) > 600 { return Err(RelayError::Stale); }"
    )


def test_wall_clock_freshness_scan_documented_limit_is_not_silently_widened():
    """The three-statement plant (VERIFY-B1) is OUTSIDE the direct-expression
    class; assert the NOT-caught result so the limit stays honest forever."""
    plant = (
        "let now = SystemTime::now();\n"
        "let now_instant = Instant::now();\n"
        "let age = now_instant.duration_since(event.created_at);\n"
        "if age > maximum_age { return; }\n"
    )
    lines = plant.splitlines()
    caught = [ln for ln in lines if _is_wall_clock_freshness_rule(ln)]
    # The scanner's DIRECT class: NO single line here is a complete rule. The
    # third line carries created_at and duration_since but the wall clock is
    # only the `now_instant` variable, not a now()/SystemTime/Instant call —
    # and it is NOT the direct same-expression comparison the class defines.
    # That is the documented limit this control pins.
    assert not caught, (
        f"the documented three-statement limit was silently widened: {caught}"
    )
    assert "created_at" in plant and "duration_since" in plant


def test_shipped_respond_to_and_subscription_rule_defaults_do_not_reference_timestamp():
    """D8 exactly: timestamp gating is config-reachable, but no shipped default uses it."""
    src = _buzz_src() / "crates" / "buzz-acp" / "src"
    filter_text = (src / "filter.rs").read_text()
    assert "timestamp: event.created_at.as_secs()" in filter_text
    assert '.set_value("timestamp"' in filter_text

    config_text = (src / "config.rs").read_text()
    code = "\n".join(line for _n, line in _rust_code_lines(config_text))
    default_filter_exprs = re.findall(
        r"filter\s*:\s*(?:Some\s*\(\s*)?[\"r#]*([^\"\n]*)", code
    )
    assert all("timestamp" not in expression for expression in default_filter_exprs), (
        default_filter_exprs
    )
    for config in sorted(_buzz_src().rglob("*.toml")):
        if "/.git/" in str(config):
            continue
        blob = config.read_text(errors="replace")
        assert not re.search(r"(?m)^\s*(?:filter|respond_to)\s*=.*timestamp", blob), config


def test_relay_drift_window_matches_the_checker_constant():
    src = _buzz_src() / "crates" / "buzz-relay" / "src" / "handlers" / "ingest.rs"
    text = src.read_text()
    match = re.search(r"const\s+MAX_TIMESTAMP_DRIFT_SECS:\s*i64\s*=\s*(\d+)\s*;", text)
    assert match, "MAX_TIMESTAMP_DRIFT_SECS integer declaration absent"
    assert int(match.group(1)) == checker.RELAY_DRIFT_WINDOW_S, match.group(0)


def test_debug_canary_line_exists_in_the_pinned_source():
    """The canary must be a line buzz-acp really emits at DEBUG on every start."""
    src = _buzz_src() / "crates" / "buzz-acp" / "src" / "relay.rs"
    line = src.read_text().splitlines()[1715]
    assert checker.DEBUG_LEVEL_CANARY in line, line
    assert line.strip().startswith("debug!("), line


def test_process_start_banner_is_buzz_acp_s_single_entry_point_line():
    """D-036 clause 3 counts this banner in the replay leg's ONE log, so it must
    be buzz-acp's once-per-process INFO line: the crate emits it at exactly one
    site, lib.rs:2454, in its entry point."""
    crate = _buzz_src() / "crates" / "buzz-acp" / "src"
    hits = []
    for path in sorted(crate.rglob("*.rs")):
        for i, ln in enumerate(path.read_text().splitlines(), 1):
            if checker.PROCESS_START_BANNER in ln:
                hits.append((str(path.relative_to(crate)), i, ln.strip()))
    assert hits == [("lib.rs", 2454, 'tracing::info!("buzz-acp starting: {}", config.summary());')], hits


def test_every_negative_row_has_a_distinct_observable_key():
    keys = [oracle.observable_key(f) for f in oracle.DISTINCT_FIXTURES]
    assert len(set(keys)) == len(keys) == 6, keys


def test_revoked_row_declares_its_shared_text_as_a_discrepancy():
    """A reason with no distinguishing observable is stated, never papered over."""
    revoked = oracle.row("revoked")
    unauth = oracle.row("neg-unauthorized")
    assert revoked["observable"] == unauth["observable"]
    assert "revoked" not in oracle.DISTINCT_FIXTURES
    assert revoked["discrepancy"] and "STRUCTURALLY" in revoked["discrepancy"]


@pytest.mark.parametrize("fixture", [r["fixture"] for r in oracle.ROWS if r["buzz_acp_observable"] is None])
def test_rows_without_a_buzz_acp_observable_say_so(fixture):
    row = oracle.row(fixture)
    assert row["discrepancy"], f"{fixture} has no buzz-acp observable and no stated discrepancy"


# ---------------------------------------------------------------------------
# 3. the checker over the committed bundles
# ---------------------------------------------------------------------------
def test_pass_bundle_passes():
    line = _run_checker(PASS_BUNDLE)
    assert line == (
        "PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; "
        "replay refused by the relay's duplicate: receipt (buzz-acp drop line absent, "
        "defense-in-depth only); "
        "+1 revocation leg (assertion 2); removal evidence: coordinator-supplied receipt "
        "(unauthenticated; ordering and fields verified; not an end-to-end revocation proof)"
    ), line


def test_missing_revoked_leg_fails_before_the_removal_summary(tmp_path):
    """The bundle contract requires revoked, so no summary fallback is reachable."""
    bundle = _bundle(tmp_path)
    shutil.rmtree(_leg(bundle, "revoked"))
    _expect_failure(bundle, "revoked: revoked leg directory absent")
    source = CHECKER.read_text()
    assert "removal_line = removal_note\n" in source
    assert "removal_line = removal_note or" not in source


def test_removal_summary_uses_only_the_revoked_leg_note(tmp_path, monkeypatch):
    """No fallback may supply a removal label when the revoked leg returns none."""
    bundle = _bundle(tmp_path)
    real_check_leg = checker._check_leg

    def drop_revoked_note(leg_dir, leg, fixture_name, identities, anchors):
        found, delivery, note = real_check_leg(
            leg_dir, leg, fixture_name, identities, anchors
        )
        return found, delivery, None if fixture_name == "revoked" else note

    monkeypatch.setattr(checker, "_check_leg", drop_revoked_note)
    line = _run_checker(bundle)
    assert line.endswith("; None"), line


def test_removal_receipt_is_labelled_coordinator_supplied_in_checker_output():
    """F5 (B3 item 5): the checker's revoked-leg summary line says the removal
    evidence is a coordinator-supplied, unauthenticated receipt — no signature
    or end-to-end revocation proof is pretended."""
    line = _run_checker(PASS_BUNDLE)
    assert "removal evidence: coordinator-supplied receipt" in line
    assert "unauthenticated" in line
    assert "ordering and fields verified" in line
    assert "not an end-to-end revocation proof" in line


def test_removal_receipt_label_is_pinned_in_spec_and_fixture_provenance():
    """The same sentence travels into spec.json's limits text and the fixtures'
    PROVENANCE.md, so the label is part of the proof's declared contract."""
    spec = json.loads(SPEC.read_text())
    assert "coordinator-supplied receipt" in spec["limits"]["removal_receipt"]
    assert "unauthenticated" in spec["limits"]["removal_receipt"]
    prov = (FIXTURES / "PROVENANCE.md").read_text()
    assert "coordinator-supplied receipt" in prov
    assert "not an end-to-end revocation proof" in prov


def test_blanket_bundle_is_a_blanket_rejection():
    """BLANKET-ACCEPTED: the seed's 'one blanket rejection fails the proof'."""
    msg = _expect_failure(BLANKET_BUNDLE, "blanket-rejection:")
    assert "collapsed to 1 observable(s)" in msg


def test_spec_negative_leg_reason_is_the_exact_observed_line():
    """AF-AP-29: the canonical contract is at least as strong as the test."""
    spec = json.loads(SPEC.read_text())
    neg = [leg for leg in spec["legs"] if leg["leg"] == "negative"]
    assert len(neg) == 1
    want = neg[0]["expect"]["failure_reason"]
    proc = subprocess.run([sys.executable, str(CHECKER)] + neg[0]["cmd"][2:],
                          cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode == neg[0]["expect"]["exit_code"]
    matched = [ln for ln in (proc.stdout + proc.stderr).splitlines() if want in ln]
    assert matched, f"spec reason {want!r} not in output:\n{proc.stdout}{proc.stderr}"
    assert matched[0] == f"failure_reason: {want}", matched[0]


def test_spec_validates_against_the_repo_schema():
    import jsonschema

    jsonschema.validate(json.loads(SPEC.read_text()),
                        json.loads((ROOT / "proofs" / "schemas" / "spec.schema.json").read_text()))


def test_spec_positive_leg_points_at_the_real_evidence_root():
    spec = json.loads(SPEC.read_text())
    pos = [leg for leg in spec["legs"] if leg["leg"] == "positive"][0]
    # The WHOLE command is pinned, not its tail (sweep class 3): the positive leg
    # must be the plain checker against the real evidence root and real anchors.
    assert pos["cmd"] == [
        "python3", "proofs/S0-02/check_buzz_authz.py", "proofs/S0-02/evidence"
    ], pos["cmd"]


def test_deferred_when_the_evidence_root_is_absent(tmp_path):
    """DEFERRED-AS-PASS: an uncaptured proof exits 2, never 0."""
    proc = subprocess.run([sys.executable, str(CHECKER), str(tmp_path / "nope")],
                          capture_output=True, text=True)
    assert proc.returncode == 2
    assert proc.stdout.strip() == "deferred: S0-02 evidence not captured"


def test_real_evidence_root_is_not_a_passing_bundle_today():
    """A partial live capture fails; an absent capture defers; neither passes."""
    proc = subprocess.run([sys.executable, str(CHECKER), "proofs/S0-02/evidence"],
                          cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode in (1, 2)
    assert "PASS:" not in proc.stdout
    if proc.returncode == 1:
        assert "leg directory absent" in proc.stdout
    else:
        assert "deferred: S0-02 evidence not captured" in proc.stdout


def test_all_timelines_removed_defers_and_never_passes(tmp_path):
    """AF-AP-40: the deferral is presence-gated by design, so pin what the gate
    can and cannot do — deleting every timeline WITHHOLDS a verdict (exit 2); it
    can never turn a failing bundle into a passing one."""
    bundle = _bundle(tmp_path, BLANKET_BUNDLE)
    for tl in bundle.rglob("timeline.jsonl"):
        tl.unlink()
    with pytest.raises(checker.Deferred):
        _run_checker(bundle)
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--synthetic-root", str(bundle), str(bundle / "legs")],
        capture_output=True, text=True)
    assert proc.returncode == 2 and proc.returncode != 0


def test_deferral_stops_once_any_leg_carries_a_timeline(tmp_path):
    """Half a bundle is a FAILURE, not a deferral."""
    bundle = _bundle(tmp_path)
    for name in ("neg-unauthorized", "neg-bad-signature", "neg-stale",
                 "neg-self-authored", "neg-not-allowlisted", "revoked"):
        shutil.rmtree(_leg(bundle, name))
    _expect_failure(bundle, "neg-unauthorized")


# ---------------------------------------------------------------------------
# 4. one observable removed at a time -> the named failure
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", oracle.DISTINCT_FIXTURES)
def test_removing_a_legs_observable_fails_that_leg(tmp_path, name):
    """OBSERVABLE-MISSING-ACCEPTED, five ways."""
    bundle = _bundle(tmp_path)
    row = oracle.row(name)
    leg_dir = _leg(bundle, name) / "second" if name == "neg-replayed" else _leg(bundle, name)
    if row["evidence"] == oracle.EV_DELIVERY:
        _rewrite(leg_dir / "delivery.json", lambda b: b.__setitem__("message", "quietly nothing"))
        needle = "carries ANY known denial observable"
    else:
        text = (leg_dir / "buzzacp.log").read_text().replace(row["observable"], "redacted")
        (leg_dir / "buzzacp.log").write_text(text)
        needle = "carries ANY known denial observable"
    _expect_failure(bundle, needle)


@pytest.mark.parametrize("name", oracle.DISTINCT_FIXTURES)
def test_swapping_a_legs_observable_for_another_legs_fails(tmp_path, name):
    """A leg that fires for the WRONG named reason is not a pass."""
    bundle = _bundle(tmp_path)
    row = oracle.row(name)
    other = next(r for r in oracle.ROWS
                 if r["leg"] == "negative" and r["observable"] != row["observable"]
                 and r["evidence"] == oracle.EV_DELIVERY)
    leg_dir = _leg(bundle, name) / "second" if name == "neg-replayed" else _leg(bundle, name)
    _rewrite(leg_dir / "delivery.json",
             lambda b: b.__setitem__("message", other["observable"]))
    if row["evidence"] == oracle.EV_BUZZACP_LOG:
        text = (leg_dir / "buzzacp.log").read_text().replace(row["observable"], "redacted")
        (leg_dir / "buzzacp.log").write_text(text)
    with pytest.raises(checker.Failure) as exc:
        _run_checker(bundle)
    msg = str(exc.value)
    assert ("does not carry the oracle observable" in msg
            or "blanket-rejection:" in msg), msg


def test_bad_signature_leg_delivering_a_VALID_event_fails(tmp_path):
    """SIGNATURE-FLIP-UNDETECTED (mutant survivor, round 1).

    The bad-signature leg's whole meaning is that the delivered event does NOT
    verify. A leg that delivers a perfectly valid event and merely claims the
    relay called it invalid proves nothing, so the checker asserts the negative
    side too — not just "the valid legs verify".
    """
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "neg-bad-signature")
    good = json.loads((_leg(bundle, "pos-allowed") / "delivered-event.json").read_text())
    ok, _reason = nv.verify_event(good)
    assert ok, "control: the substituted event must be a VALID one"
    (leg_dir / "delivered-event.json").write_text(json.dumps(good, indent=1, sort_keys=True) + "\n")
    _rewrite(leg_dir / "delivery.json", lambda b: _set_delivery_event_id(b, good["id"]))
    _expect_failure(bundle, "this leg must carry an invalid signature")


def test_two_legs_with_swapped_observables_fail_the_named_check(tmp_path):
    """NAMED-OBSERVABLE-OFF (mutant survivor, round 1).

    Swapping two legs' reasons keeps the observable SET at five distinct keys,
    so the distinctness gate is silent — only the per-leg "this leg fired for
    ITS OWN reason" check can catch it. Without this case that check could be
    deleted and the whole suite stayed green.
    """
    bundle = _bundle(tmp_path)
    unauth = _leg(bundle, "neg-unauthorized") / "delivery.json"
    stale = _leg(bundle, "neg-stale") / "delivery.json"
    a = json.loads(unauth.read_text())["message"]
    b = json.loads(stale.read_text())["message"]
    assert a != b
    _rewrite(unauth, lambda blob: blob.__setitem__("message", b))
    _rewrite(stale, lambda blob: blob.__setitem__("message", a))
    msg = _expect_failure(bundle, "does not carry the oracle observable")
    assert "blanket-rejection" not in msg, (
        "the distinctness gate fired instead — this case must reach the named check"
    )


def test_a_buzz_acp_leg_showing_only_a_relay_reason_fails_the_named_check(tmp_path):
    """The same hole, across channels: a leg decided by buzz-acp that shows only
    a relay-side text has not fired for its own reason."""
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "neg-self-authored")
    log = leg_dir / "buzzacp.log"
    # A key no other leg holds (relay text in the LOG channel), so the leg stays
    # distinct and only the named check can reject it.
    log.write_text(log.read_text().replace(
        "dropping self-authored event", "restricted: not a channel member"))
    msg = _expect_failure(bundle, "does not carry the oracle observable")
    assert "neg-self-authored" in msg
    assert "blanket-rejection" not in msg


def test_wrong_channel_observables_are_rejected(tmp_path):
    for i, (leg, source, target, text) in enumerate((
        ("neg-self-authored", "buzzacp.log", "delivery.json", "dropping self-authored event"),
        ("neg-unauthorized", "delivery.json", "buzzacp.log", "restricted: not a channel member"),
    )):
        bundle = _bundle(tmp_path / f"channel-{i}")
        leg_dir = _leg(bundle, leg)
        if source == "buzzacp.log":
            log = leg_dir / source
            log.write_text(log.read_text().replace(text, "redacted"))
            _rewrite(leg_dir / target, lambda b, value=text: b.__setitem__("message", value))
        else:
            _rewrite(leg_dir / source, lambda b: b.__setitem__("message", "quietly nothing"))
            log = leg_dir / target
            log.write_text(log.read_text() + f"2026-09-08T00:00:01Z DEBUG {text}\n")
        _expect_failure(bundle, "does not carry the oracle observable")


def test_a_leg_with_two_denial_observables_is_not_counted_as_a_distinct_reason(tmp_path):
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "neg-self-authored")
    log = leg_dir / "buzzacp.log"
    log.write_text(
        log.read_text()
        + "2026-09-08T00:00:06Z DEBUG inbound author gate — dropping event\n"
    )
    _expect_failure(bundle, "carries 2 denial observables, expected exactly")


def test_a_negative_leg_that_produced_a_turn_fails(tmp_path):
    """TWO-TURNS-ACCEPTED, negative side: any turn on a denied event is a failure."""
    bundle = _bundle(tmp_path)
    good = (_leg(bundle, "pos-allowed") / "timeline.jsonl").read_text()
    (_leg(bundle, "neg-unauthorized") / "timeline.jsonl").write_text(good)
    _expect_failure(bundle, "neg-unauthorized: 1 ACP session/prompt turn(s), expected 0")


def test_a_positive_leg_with_two_turns_fails(tmp_path):
    """TWO-TURNS-ACCEPTED: 'exactly one' is a count, not 'at least one'."""
    bundle = _bundle(tmp_path)
    tl = _leg(bundle, "pos-allowed") / "timeline.jsonl"
    lines = tl.read_text().splitlines()
    dup = json.loads(lines[4])
    dup["seq"] = len(lines) + 1
    tl.write_text("\n".join(lines + [json.dumps(dup, sort_keys=True)]) + "\n")
    _expect_failure(bundle, "pos-allowed: 2 ACP session/prompt turn(s), expected 1")


def test_a_positive_leg_with_no_turn_fails(tmp_path):
    bundle = _bundle(tmp_path)
    empty = (_leg(bundle, "neg-unauthorized") / "timeline.jsonl").read_text()
    (_leg(bundle, "pos-allowed") / "timeline.jsonl").write_text(empty)
    _expect_failure(bundle, "pos-allowed: 0 ACP session/prompt turn(s), expected 1")


def test_a_positive_turn_without_the_fixture_nonce_fails(tmp_path):
    bundle = _bundle(tmp_path)
    tl = _leg(bundle, "pos-allowed") / "timeline.jsonl"
    text = tl.read_text().replace("S0-02 pos-allowed", "S0-02 something-else")
    tl.write_text(text)
    _expect_failure(bundle, "does not carry the fixture's nonce")


def test_positive_nonce_must_be_a_complete_json_token():
    nonce = "S0-02 pos-allowed"
    frame = {"params": {"prompt": nonce + "-suffix"}}
    blob = checker._prompt_text(frame)
    assert nonce in blob
    assert f'"{nonce}"' not in blob
    assert not re.search(rf'(?<![\w-]){re.escape(nonce)}(?![\w-])', blob)


def test_a_missing_debug_canary_fails_a_buzz_acp_leg(tmp_path):
    """A buzz-acp-decided leg captured at INFO cannot prove an absence."""
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "neg-self-authored")
    text = leg_dir / "buzzacp.log"
    text.write_text(text.read_text().replace(checker.DEBUG_LEVEL_CANARY, "watermark noted"))
    _expect_failure(bundle, "lacks the debug-level canary")


def test_an_info_level_canary_does_not_prove_debug_capture(tmp_path):
    bundle = _bundle(tmp_path)
    log = _leg(bundle, "neg-self-authored") / "buzzacp.log"
    log.write_text(log.read_text().replace(" DEBUG ", " INFO "))
    _expect_failure(bundle, "on a DEBUG line")


def test_relay_decided_leg_needs_no_debug_canary(tmp_path):
    """A real INFO-only corpus log is valid where the relay supplied the evidence."""
    venue = os.environ.get("S0_01_VENUE")
    if venue in (None, "ci"):
        pytest.skip(
            f"venue={venue!r} — the S0-01 real-leg corpus is a DECLARED input; "
            f"CI skips by declaration"
        )
    real_leg_dir = os.environ.get("S0_01_REAL_LEG_DIR")
    assert real_leg_dir, "S0_01_REAL_LEG_DIR must be set on a declared venue"
    bundle = _bundle(tmp_path)
    real_log = Path(real_leg_dir) / "run-1" / "buzzacp.log"
    assert checker.DEBUG_LEVEL_CANARY not in real_log.read_text()
    target = _leg(bundle, "neg-unauthorized") / "buzzacp.log"
    shutil.copy2(real_log, target)
    _run_checker(bundle)


def test_self_authored_leg_requires_ignore_self_true(tmp_path):
    """The drop arm at lib.rs:3257 is guarded by config.ignore_self."""
    bundle = _bundle(tmp_path)
    log = _leg(bundle, "neg-self-authored") / "buzzacp.log"
    log.write_text(log.read_text().replace("ignore_self=true", "ignore_self=false"))
    _expect_failure(bundle, "does not show ignore_self=true")


def test_unmasked_pubkey_in_the_log_fails(tmp_path):
    bundle = _bundle(tmp_path)
    log = _leg(bundle, "neg-self-authored") / "buzzacp.log"
    log.write_text(log.read_text().replace("pubkey=<HEX>", "pubkey=" + "a" * 64))
    _expect_failure(bundle, "unmasked 64-hex string")


# ---------------------------------------------------------------------------
# 5. the replay leg
# ---------------------------------------------------------------------------
def test_replay_second_delivery_with_a_turn_fails(tmp_path):
    """REPLAY-SECOND-TURN-ACCEPTED: the duplicate must not produce a turn."""
    bundle = _bundle(tmp_path)
    good = (_leg(bundle, "neg-replayed") / "first" / "timeline.jsonl").read_text()
    (_leg(bundle, "neg-replayed") / "second" / "timeline.jsonl").write_text(good)
    _expect_failure(bundle, "neg-replayed/second: 1 ACP turn(s), expected 0")


def test_replay_first_delivery_without_a_turn_fails(tmp_path):
    """A replay leg where NEITHER delivery turned proves nothing."""
    bundle = _bundle(tmp_path)
    empty = (_leg(bundle, "neg-unauthorized") / "timeline.jsonl").read_text()
    (_leg(bundle, "neg-replayed") / "first" / "timeline.jsonl").write_text(empty)
    _expect_failure(bundle, "neg-replayed/first: 0 ACP turn(s), expected exactly 1")


def test_replay_with_two_different_event_ids_fails(tmp_path):
    """WRONG-EVENT-ID-ACCEPTED: two different events are not a replay."""
    bundle = _bundle(tmp_path)
    second = _leg(bundle, "neg-replayed") / "second"
    other = json.loads((_leg(bundle, "neg-stale") / "delivered-event.json").read_text())
    (second / "delivered-event.json").write_text(json.dumps(other, indent=1, sort_keys=True) + "\n")
    _rewrite(second / "delivery.json", lambda b: _set_delivery_event_id(b, other["id"]))
    with pytest.raises(checker.Failure) as exc:
        _run_checker(bundle)
    assert ("this is not a replay" in str(exc.value)
            or "delivered content does not match" in str(exc.value)), str(exc.value)


# --- B9-R1: D-036 clauses 1-3 in the checker (VERIFY-B9 F-1, F-2, F-6, F-13) ---
_ONE_PROCESS = "not ONE continuous buzz-acp process (D-036 clause 3)"


def _replay(bundle: Path, sub: str) -> Path:
    return _leg(bundle, "neg-replayed") / sub


def _checker_text(bundle: Path) -> str:
    with pytest.raises(checker.Failure) as exc:
        _run_checker(bundle)
    return str(exc.value)


def _first_records() -> list[dict]:
    """The committed first sub-leg: initialize, result, session/new, result,
    session/prompt, session/update, result (seq 1..7)."""
    return [json.loads(ln) for ln in
            (_replay(PASS_BUNDLE, "first") / "timeline.jsonl").read_text().splitlines()]


def _write_records(path: Path, records: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records))


def _drop_line(bundle: Path) -> str:
    """buzz-acp's own dedup line (relay.rs:2387), the replay row's defense-in-depth."""
    chan = json.loads((bundle / "identities.json").read_text())["channel"]
    return f"2026-09-08T00:00:05.000000Z DEBUG buzz_acp::relay: dropping duplicate event for channel {chan}\n"


def _append_to_both_logs(bundle: Path, line: str) -> None:
    """ONE process leaves ONE masked log, copied into both sub-legs (R:305-306)."""
    for sub in ("first", "second"):
        log = _replay(bundle, sub) / "buzzacp.log"
        log.write_text(log.read_text() + line)


def test_replay_same_content_new_event_id_fails_on_the_id_check(tmp_path):
    """D-036 clause 1 (VERIFY-B9 F-6, cm1): the same content under a NEW event id,
    signed by the bundle's labelled pass owner key, passes every earlier check
    and is refused by the id check itself — never earlier at the content check."""
    bundle = _bundle(tmp_path)
    first = json.loads((_replay(bundle, "first") / "delivered-event.json").read_text())
    ev = nv.sign_event(builder._bundle_privkey("pass", "owner"), {
        "created_at": first["created_at"] + 1, "kind": first["kind"],
        "tags": first["tags"], "content": first["content"],
    })
    assert ev["id"] != first["id"] and ev["pubkey"] == first["pubkey"], "control: a new id, the same signer"
    second = _replay(bundle, "second")
    (second / "delivered-event.json").write_text(json.dumps(ev, indent=1, sort_keys=True) + "\n")
    _rewrite(second / "delivery.json", lambda b: b.__setitem__("event_id", ev["id"]))
    assert _checker_text(bundle) == (
        f"neg-replayed: the two deliveries carry different event ids "
        f"({first['id'][:12]} vs {ev['id'][:12]}) — this is not a replay"
    )


_RECEIPT_CASES = (
    ("http_status", 400, "the relay answers a duplicate with HTTP 200, got http_status 400"),
    ("http_status", True, "the relay answers a duplicate with HTTP 200, got http_status True"),
    ("accepted", False, "the relay's duplicate receipt must carry accepted=true (a bool), got False"),
    ("accepted", "true", "the relay's duplicate receipt must carry accepted=true (a bool), got 'true'"),
    ("event_id_echoed", False,
     "the relay's duplicate receipt must echo the event id (event_id_echoed=true), got False"),
    ("message", "duplicate: already processed",
     "the relay receipt message is 'duplicate: already processed', expected exactly 'duplicate:' "
     "— the relay did not refuse the second delivery as a duplicate (a forwarded duplicate "
     "fails even when buzz-acp dropped it)"),
)


@pytest.mark.parametrize("field,value,text", _RECEIPT_CASES,
                         ids=[f"{c[0]}={c[1]!r}" for c in _RECEIPT_CASES])
def test_replay_duplicate_receipt_fields_each_have_a_named_refusal(tmp_path, field, value, text):
    """D-036 clause 2 (VERIFY-B9 F-1): the relay's duplicate receipt is bound to
    the second delivery field by field. The committed receipt passes (control:
    test_pass_bundle_passes); each single-field violation is its own refusal. A
    'duplicate: …' text with a suffix is another kind's answer (ingest.rs:3080),
    not the kind-9 duplicate (ingest.rs:3196)."""
    bundle = _bundle(tmp_path)
    _rewrite(_replay(bundle, "second") / "delivery.json", lambda b: b.__setitem__(field, value))
    assert _checker_text(bundle) == f"neg-replayed/second: {text}"


def test_replay_duplicate_receipt_must_name_the_first_delivery(tmp_path):
    bundle = _bundle(tmp_path)
    first_id = json.loads((_replay(bundle, "first") / "delivered-event.json").read_text())["id"]
    _rewrite(_replay(bundle, "second") / "delivery.json",
             lambda b: b.__setitem__("event_id", "f" * 64))
    assert _checker_text(bundle) == (
        f"neg-replayed/second: the duplicate receipt names event ffffffffffff, not the first "
        f"delivery's {first_id[:12]} — the receipt is not bound to this replay"
    )


def test_replay_forwarded_duplicate_fails_even_when_buzz_acp_dropped_it(tmp_path):
    """The OLD synthetic shape (VERIFY-B9 F-1/F-7): buzz-acp's drop line is in the
    log but the relay's receipt is a NEW acceptance (message ''). The drop line
    never substitutes for the receipt."""
    bundle = _bundle(tmp_path)
    _append_to_both_logs(bundle, _drop_line(bundle))
    _rewrite(_replay(bundle, "second") / "delivery.json", lambda b: b.__setitem__("message", ""))
    assert _checker_text(bundle) == (
        "neg-replayed/second: the relay receipt message is '', expected exactly 'duplicate:' "
        "— the relay did not refuse the second delivery as a duplicate (a forwarded duplicate "
        "fails even when buzz-acp dropped it)"
    )


def test_replay_drop_line_is_recorded_when_present_and_never_required(tmp_path):
    """D-036 keeps buzz-acp's drop line as defense-in-depth: present, the PASS
    line records it; absent (the committed bundle), the leg still passes."""
    bundle = _bundle(tmp_path)
    _append_to_both_logs(bundle, _drop_line(bundle))
    line = _run_checker(bundle)
    assert "(buzz-acp drop line present, defense-in-depth only)" in line, line
    assert "(buzz-acp drop line absent, defense-in-depth only)" in _run_checker(PASS_BUNDLE)


def test_replay_other_denial_observables_beside_the_receipt_fail(tmp_path):
    bundle = _bundle(tmp_path)
    _append_to_both_logs(bundle, "2026-09-08T00:00:06.000000Z DEBUG buzz_acp::relay: "
                                 "inbound author gate — dropping event\n")
    assert _checker_text(bundle) == (
        "neg-replayed/second: evidence carries denial observables "
        "['buzzacp_log::inbound author gate'] beside the relay's duplicate receipt"
    )


def _restart_cases():
    r = _first_records()
    return (
        ("initialize-continuing-seq", [{**r[0], "seq": 8}],
         f"neg-replayed/second: the delta holds an ACP initialize frame (seq 8) — the agent "
         f"restarted: a second process, {_ONE_PROCESS}"),
        ("b9-case-A-restart", r[0:2],
         f"neg-replayed/second: the delta holds an ACP initialize frame (seq 1) — the agent "
         f"restarted: a second process, {_ONE_PROCESS}"),
        ("h1a-restart-with-session", r[0:4],
         f"neg-replayed/second: the delta holds an ACP initialize frame (seq 1) — the agent "
         f"restarted: a second process, {_ONE_PROCESS}"),
        ("seq-restart-without-initialize", [{**r[2], "seq": 1}, {**r[3], "seq": 2}],
         f"neg-replayed/second: delta record seq 1 does not continue the preceding seq 7 — the "
         f"frame tee restarted: a second process, {_ONE_PROCESS}"),
        ("seq-gap", [{**r[5], "seq": 9}],
         f"neg-replayed/second: delta record seq 9 does not continue the preceding seq 7 — the "
         f"frame tee restarted: a second process, {_ONE_PROCESS}"),
        ("seq-not-an-int", [{**r[5], "seq": "8"}],
         f"neg-replayed/second: delta record seq '8' does not continue the preceding seq 7 — the "
         f"frame tee restarted: a second process, {_ONE_PROCESS}"),
    )


@pytest.mark.parametrize("name,records,text", _restart_cases(),
                         ids=[c[0] for c in _restart_cases()])
def test_replay_second_delta_from_a_restarted_process_fails(tmp_path, name, records, text):
    """D-036 clause 3 (VERIFY-B9 F-2, H1): a delta that restarts the agent or the
    frame tee is a second process. Prompt-free on purpose, so only clause 3 can
    refuse it."""
    bundle = _bundle(tmp_path)
    _write_records(_replay(bundle, "second") / "timeline.jsonl", records)
    assert _checker_text(bundle) == text


def test_replay_continuing_delta_passes(tmp_path):
    """The positive control for clause 3: the first turn's terminal frames land
    in the delta (VERIFY-B9 h2a) with seq continuing 5 -> 6, 7 and no initialize."""
    bundle = _bundle(tmp_path)
    r = _first_records()
    _write_records(_replay(bundle, "first") / "timeline.jsonl", r[:5])
    _write_records(_replay(bundle, "second") / "timeline.jsonl", r[5:])
    assert _run_checker(bundle).startswith("PASS: S0-02 buzz-authz")


def test_replay_two_masked_logs_are_a_second_process(tmp_path):
    bundle = _bundle(tmp_path)
    log = _replay(bundle, "second") / "buzzacp.log"
    log.write_text(log.read_text() + "2026-09-08T00:00:06.000000Z  INFO buzz_acp: a second log\n")
    assert _checker_text(bundle) == (
        "neg-replayed: the first and second sub-legs carry different buzzacp.log bytes — two "
        f"masked logs: a second process, {_ONE_PROCESS}"
    )


@pytest.mark.parametrize("starts", [0, 2])
def test_replay_log_must_show_exactly_one_buzz_acp_start(tmp_path, starts):
    bundle = _bundle(tmp_path)
    for sub in ("first", "second"):
        log = _replay(bundle, sub) / "buzzacp.log"
        text = log.read_text()
        banner = next(ln for ln in text.splitlines(keepends=True) if checker.PROCESS_START_BANNER in ln)
        log.write_text(text.replace(banner, "") if starts == 0 else text + banner)
    assert _checker_text(bundle) == (
        f"neg-replayed: buzzacp.log shows {starts} buzz-acp start line(s) ('buzz-acp starting:'), "
        f"expected exactly 1 — {_ONE_PROCESS}"
    )


_TORN_JSON = b'{"dir":"a2c","frame":{"jsonrpc":"2.0","method":"session/update","params":{"text":"po'
_TORN_UTF8 = b'{"dir":"a2c","frame":{"text":"' + "—".encode()[:1]


@pytest.mark.parametrize("where,label,torn", [
    (("neg-replayed", "second"), "neg-replayed/second", _TORN_JSON),
    (("neg-replayed", "second"), "neg-replayed/second", _TORN_UTF8),
    (("pos-allowed",), "pos-allowed", _TORN_JSON),
], ids=["replay-second-json", "replay-second-utf8", "pos-allowed-json"])
def test_a_torn_timeline_record_is_a_named_cli_failure(tmp_path, where, label, torn):
    """F-13: a torn record (the live writer mid-line at the final read) must be
    the CLI's failure_reason line (exit contract), never a traceback."""
    bundle = _bundle(tmp_path)
    tl = bundle.joinpath("legs", *where, "timeline.jsonl")
    tl.write_bytes(tl.read_bytes() + torn)
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--synthetic-root", str(bundle), str(bundle / "legs")],
        capture_output=True, text=True, timeout=60)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "Traceback" not in proc.stderr, proc.stderr
    lines = proc.stdout.splitlines()
    assert len(lines) == 1 and lines[0].startswith(
        f"failure_reason: {label}: a timeline record is not valid JSON or UTF-8 — a torn or "
        f"partial line ("), proc.stdout


# ---------------------------------------------------------------------------
# 6. identity, freshness and delivery binding
# ---------------------------------------------------------------------------
def test_replay_second_subleg_uses_only_the_wider_replay_tolerance(tmp_path):
    bundle = _bundle(tmp_path)
    second = _leg(bundle, "neg-replayed") / "second"
    _rewrite(second / "t0.json", lambda b: b.__setitem__(
        "t0_epoch_s", b["t0_epoch_s"] + checker.LEG_CLOCK_TOLERANCE_S + 1
    ))
    _run_checker(bundle)

    too_far = _bundle(tmp_path / "too-far")
    second = _leg(too_far, "neg-replayed") / "second"
    _rewrite(second / "t0.json", lambda b: b.__setitem__(
        "t0_epoch_s", b["t0_epoch_s"] + checker.REPLAY_CLOCK_TOLERANCE_S + 1
    ))
    _expect_failure(too_far, "outside the")


def test_delivery_receipt_for_a_different_event_id_fails(tmp_path):
    """WRONG-EVENT-ID-ACCEPTED: the receipt must name the delivered event."""
    bundle = _bundle(tmp_path)
    _rewrite(_leg(bundle, "pos-allowed") / "delivery.json",
             lambda b: b.__setitem__("event_id", "f" * 64))
    _expect_failure(bundle, "delivery.json event_id")


def test_a_tampered_delivered_event_id_fails(tmp_path):
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "pos-allowed")
    ev = json.loads((leg_dir / "delivered-event.json").read_text())
    ev["content"] = ev["content"] + " tampered"
    (leg_dir / "delivered-event.json").write_text(json.dumps(ev, indent=1, sort_keys=True) + "\n")
    _expect_failure(bundle, "does not match the id computed from its fields")


def test_a_delivered_event_from_the_wrong_identity_fails(tmp_path):
    """IDENTITY-UNPINNED (mutant survivor, round 2).

    The substituted event is IDENTICAL on kind, tags, content and freshness and
    differs ONLY in who signed it, so every other check passes and the sender
    binding is the only thing that can reject it. Substituting a whole different
    event instead would have been caught by the content check, which is why the
    first version of this test let the mutant live.
    """
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "pos-allowed")
    ev = json.loads((leg_dir / "delivered-event.json").read_text())
    wrong_signer = builder._bundle_privkey(bundle.name.replace("evidence-", ""), "user2")
    forged = nv.sign_event(wrong_signer, {"created_at": ev["created_at"], "kind": ev["kind"],
                                          "tags": ev["tags"], "content": ev["content"]})
    assert forged["pubkey"] != ev["pubkey"]
    for key in ("kind", "tags", "content", "created_at"):
        assert forged[key] == ev[key], "control: only the signer may differ"
    (leg_dir / "delivered-event.json").write_text(
        json.dumps(forged, indent=1, sort_keys=True) + "\n")
    _rewrite(leg_dir / "delivery.json", lambda b: _set_delivery_event_id(b, forged["id"]))
    _expect_failure(bundle, "delivered sender is not the owner identity")


def test_a_nonmember_leg_signed_by_a_known_identity_fails(tmp_path):
    """F21, the other arm of the same binding: a null expected_pubkey binds the
    sender only by exclusion, so a sender that is one of the four known
    identities fails. Since B10 (D-038) no committed fixture is null, so this
    test nulls neg-unauthorized's expected_pubkey in BOTH copies the checker
    compares (the leg's fixture.json and the bundle's fixtures/ anchor) to keep
    the arm covered."""
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "neg-unauthorized")
    for path in (leg_dir / "fixture.json", bundle / "fixtures" / "neg-unauthorized.json"):
        _rewrite(path, lambda b: b["signer"].__setitem__("expected_pubkey", None))
    # Control: the null arm alone passes the bundle's own nonmember sender, so the
    # failure below is the forged sender's.
    assert _run_checker(bundle).startswith("PASS: S0-02 buzz-authz")
    ev = json.loads((leg_dir / "delivered-event.json").read_text())
    owner_key = builder._bundle_privkey(bundle.name.replace("evidence-", ""), "owner")
    forged = nv.sign_event(owner_key, {"created_at": ev["created_at"], "kind": ev["kind"],
                                       "tags": ev["tags"], "content": ev["content"]})
    (leg_dir / "delivered-event.json").write_text(
        json.dumps(forged, indent=1, sort_keys=True) + "\n")
    _rewrite(leg_dir / "delivery.json", lambda b: _set_delivery_event_id(b, forged["id"]))
    _expect_failure(bundle, "must not be one of the known S0-01 identities")


@pytest.mark.parametrize("signer", ["owner", "unmeasured"])
def test_a_nonmember_leg_binds_to_the_one_measured_nonmember(tmp_path, signer):
    """D-038 (B10): neg-unauthorized binds to ONE nonmember identity by its exact
    pubkey. A known identity (the owner) fails, and so does a fresh key that is no
    identity at all: the null binding (F21) accepts any key outside the four
    known identities, the exact binding accepts only the measured one."""
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "neg-unauthorized")
    ev = json.loads((leg_dir / "delivered-event.json").read_text())
    if signer == "owner":
        key = builder._bundle_privkey(bundle.name.replace("evidence-", ""), "owner")
    else:
        key = hashlib.sha256(b"B10/an-unmeasured-non-member").hexdigest()
    forged = nv.sign_event(key, {"created_at": ev["created_at"], "kind": ev["kind"],
                                 "tags": ev["tags"], "content": ev["content"]})
    assert forged["pubkey"] != ev["pubkey"]
    (leg_dir / "delivered-event.json").write_text(
        json.dumps(forged, indent=1, sort_keys=True) + "\n")
    _rewrite(leg_dir / "delivery.json", lambda b: _set_delivery_event_id(b, forged["id"]))
    _expect_failure(bundle, "neg-unauthorized: delivered sender is not the nonmember identity")


def test_a_revoked_leg_signed_by_the_first_owner_fails(tmp_path):
    """D-037 (B10): the revoked leg is signed by owner2, the owner the removal
    targets. A delivery signed by the owner the other legs use (the pre-B10
    shape), with a removal receipt naming that sender, fails the sender binding.
    Only the signer differs from the committed leg."""
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "revoked")
    ev = json.loads((leg_dir / "delivered-event.json").read_text())
    owner_key = builder._bundle_privkey(bundle.name.replace("evidence-", ""), "owner")
    forged = nv.sign_event(owner_key, {"created_at": ev["created_at"], "kind": ev["kind"],
                                       "tags": ev["tags"], "content": ev["content"]})
    assert forged["pubkey"] != ev["pubkey"]
    (leg_dir / "delivered-event.json").write_text(
        json.dumps(forged, indent=1, sort_keys=True) + "\n")
    _rewrite(leg_dir / "delivery.json", lambda b: _set_delivery_event_id(b, forged["id"]))
    _rewrite(leg_dir / "membership.json",
             lambda b: b.__setitem__("removed_pubkey", forged["pubkey"]))
    _expect_failure(bundle, "revoked: delivered sender is not the owner2 identity")


def test_the_committed_specimen_key_cannot_be_delivered(tmp_path):
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "pos-allowed")
    fixture = json.loads((leg_dir / "fixture.json").read_text())
    ev = json.loads((leg_dir / "delivered-event.json").read_text())
    fixture["signer"]["specimen_pubkey"] = ev["pubkey"]
    fixture["signer"]["expected_pubkey"] = ev["pubkey"]
    (leg_dir / "fixture.json").write_text(json.dumps(fixture, indent=1, sort_keys=True) + "\n")
    (bundle / "fixtures" / "pos-allowed.json").write_text(
        json.dumps(fixture, indent=1, sort_keys=True) + "\n")
    _expect_failure(bundle, "the committed specimen key was delivered")


def _resign_at(bundle: Path, leg: str, role: str, created_at: int) -> dict:
    """Re-sign a leg's delivered event at a new created_at with the bundle's own
    role key, so the freshness arm is reached instead of the signature arm."""
    leg_dir = _leg(bundle, leg)
    ev = json.loads((leg_dir / "delivered-event.json").read_text())
    priv = builder._bundle_privkey(bundle.name.replace("evidence-", ""), role)
    fresh = nv.sign_event(priv, {"created_at": created_at, "kind": ev["kind"],
                                 "tags": ev["tags"], "content": ev["content"]})
    (leg_dir / "delivered-event.json").write_text(
        json.dumps(fresh, indent=1, sort_keys=True) + "\n")
    _rewrite(leg_dir / "delivery.json", lambda b: _set_delivery_event_id(b, fresh["id"]))
    return fresh


def test_a_stale_event_inside_the_relay_window_is_not_stale(tmp_path):
    """MEMBERSHIP-BY-CREATED_AT / STALE-WINDOW-UNPINNED: the age is MEASURED,
    not declared. A 'stale' leg whose event is fresh fails."""
    bundle = _bundle(tmp_path)
    t0 = json.loads((_leg(bundle, "neg-stale") / "t0.json").read_text())["t0_epoch_s"]
    _resign_at(bundle, "neg-stale", "owner", t0 - 10)
    _expect_failure(bundle, "inside the relay's")


def test_stale_event_exactly_at_relay_boundary_is_not_stale(tmp_path):
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "neg-stale")
    t0 = json.loads((leg_dir / "t0.json").read_text())["t0_epoch_s"]
    _resign_at(bundle, "neg-stale", "owner", t0 - checker.RELAY_DRIFT_WINDOW_S)
    _expect_failure(bundle, "inside the relay's")


def test_a_far_future_t0_cannot_make_a_fresh_event_look_stale(tmp_path):
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "neg-stale")
    _rewrite(leg_dir / "t0.json",
             lambda b: b.__setitem__("t0_epoch_s", b["t0_epoch_s"] + 5000))
    _expect_failure(bundle, "outside the")


def test_a_fresh_leg_delivered_outside_the_window_fails(tmp_path):
    """The other direction: a 'fresh' leg cannot silently be a stale one."""
    bundle = _bundle(tmp_path)
    t0 = json.loads((_leg(bundle, "pos-allowed") / "t0.json").read_text())["t0_epoch_s"]
    _resign_at(bundle, "pos-allowed", "owner", t0 - 5000)
    _expect_failure(bundle, "outside the")


def test_a_retimestamped_event_that_is_not_resigned_fails_on_the_signature(tmp_path):
    """The ordering that makes the freshness arm safe: created_at cannot be
    edited without the role key, because the signature is checked first."""
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "neg-stale")
    ev = json.loads((leg_dir / "delivered-event.json").read_text())
    t0 = json.loads((leg_dir / "t0.json").read_text())["t0_epoch_s"]
    ev["created_at"] = t0 - 10
    ev["id"] = nv.event_id(ev)
    (leg_dir / "delivered-event.json").write_text(json.dumps(ev, indent=1, sort_keys=True) + "\n")
    _rewrite(leg_dir / "delivery.json", lambda b: _set_delivery_event_id(b, ev["id"]))
    _expect_failure(bundle, "failed signature verification")


def test_a_relay_decided_leg_must_show_accepted_false(tmp_path):
    bundle = _bundle(tmp_path)
    _rewrite(_leg(bundle, "neg-stale") / "delivery.json",
             lambda b: _set_delivery_outcome(b, accepted=True, status=200, echoed=True))
    _expect_failure(bundle, "accepted must be false")


def test_a_buzz_acp_decided_leg_must_show_accepted_true(tmp_path):
    bundle = _bundle(tmp_path)
    _rewrite(_leg(bundle, "neg-self-authored") / "delivery.json",
             lambda b: _set_delivery_outcome(b, accepted=False, status=400, echoed=False))
    _expect_failure(bundle, "the relay must have ACCEPTED the event")


def test_delivery_receipt_requires_the_exact_producer_shape(tmp_path):
    bundle = _bundle(tmp_path)
    path = _leg(bundle, "pos-allowed") / "delivery.json"
    for i, mutation in enumerate((
        lambda b: b.pop("http_status"),
        lambda b: b.__setitem__("mention_pubkeys", []),
    )):
        case = _bundle(tmp_path / f"shape-{i}")
        _rewrite(_leg(case, "pos-allowed") / "delivery.json", mutation)
        _expect_failure(case, "wrong producer shape")
    delivery = json.loads(path.read_text())
    assert set(delivery) == {
        "accepted", "event_id", "event_id_echoed", "http_status", "message"
    }


def test_delivery_receipt_grades_http_status_and_echo_semantics(tmp_path):
    cases = (
        ("pos-allowed", lambda b: b.__setitem__("http_status", 201), "http_status must be 200"),
        ("neg-stale", lambda b: b.__setitem__("http_status", 401), "http_status must be 400"),
        ("pos-allowed", lambda b: b.__setitem__("http_status", True), "http_status is not an int"),
        ("pos-allowed", lambda b: b.__setitem__("event_id_echoed", False),
         "event_id_echoed must be true"),
        ("neg-stale", lambda b: b.__setitem__("event_id_echoed", True),
         "event_id_echoed must be false"),
    )
    for i, (leg, mutation, needle) in enumerate(cases):
        bundle = _bundle(tmp_path / f"delivery-{i}")
        _rewrite(_leg(bundle, leg) / "delivery.json", mutation)
        _expect_failure(bundle, needle)


def test_a_leg_fixture_that_drifts_from_the_committed_one_fails(tmp_path):
    """FIXTURE-DRIFT at capture time: the leg must carry the committed fixture."""
    bundle = _bundle(tmp_path)
    _rewrite(_leg(bundle, "neg-stale") / "fixture.json",
             lambda b: b["expected"].__setitem__("turns", 1))
    _expect_failure(bundle, "differs from the committed")


def test_revoked_leg_requires_a_membership_removal_receipt(tmp_path):
    bundle = _bundle(tmp_path)
    (_leg(bundle, "revoked") / "membership.json").unlink()
    _expect_failure(bundle, "revoked: missing ['membership.json']")


def test_revoked_leg_receipt_must_name_the_delivered_sender(tmp_path):
    bundle = _bundle(tmp_path)
    _rewrite(_leg(bundle, "revoked") / "membership.json",
             lambda b: b.__setitem__("removed_pubkey", "b" * 64))
    _expect_failure(bundle, "removed_pubkey does not match the delivered sender")


def test_revoked_leg_receipt_must_record_a_COMPLETED_removal(tmp_path):
    """MEMBERSHIP-RECEIPT-OFF (mutant survivor).

    A receipt that names the right pubkey but records the removal as NOT done
    proves nothing: the sender may still have been a member when the event was
    delivered, which is exactly the state this leg has to rule out. The whole
    falsy/near-miss domain is exercised, not just False (AF-AP-47).
    """
    for i, bad in enumerate((False, None, "true", 1)):
        bundle = _bundle(tmp_path / f"case{i}")
        _rewrite(_leg(bundle, "revoked") / "membership.json",
                 lambda blob: blob.__setitem__("removed", bad))
        _expect_failure(bundle, "does not record a completed removal")


def test_revoked_leg_receipt_must_precede_delivery(tmp_path):
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "revoked")
    t0 = json.loads((leg_dir / "t0.json").read_text())["t0_epoch_s"]
    _rewrite(leg_dir / "membership.json", lambda b: b.__setitem__("at_epoch_s", t0))
    _expect_failure(bundle, "at or after the delivery t0")


def test_revoked_leg_receipt_must_name_the_delivered_channel(tmp_path):
    bundle = _bundle(tmp_path)
    _rewrite(_leg(bundle, "revoked") / "membership.json",
             lambda b: b.__setitem__("channel", "wrong-channel"))
    _expect_failure(bundle, "is not the delivered event's channel")


def test_revoked_leg_receipt_must_record_a_successful_relay_response(tmp_path):
    for i, bad in enumerate((None, True, 0, 199, 300, "200")):
        bundle = _bundle(tmp_path / f"status-{i}")
        receipt = _leg(bundle, "revoked") / "membership.json"
        _rewrite(receipt, lambda b, value=bad: b.__setitem__("http_status", value))
        _expect_failure(bundle, "records no successful relay removal response")


def test_revoked_leg_event_must_be_fresh(tmp_path):
    """Assertion 2: revocation is independent of created_at, so the revoked
    leg's event must be INSIDE the freshness window — otherwise the leg could
    be passing because the event was stale."""
    fixture = json.loads((FIXTURES / "revoked.json").read_text())
    assert fixture["template"]["created_at_offset_s"] == 0


# ---------------------------------------------------------------------------
# 7. structural: FIFO reads, reuse-not-copy, no LLM in the gate
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", ["timeline.jsonl", "delivery.json", "buzzacp.log",
                                  "fixture.json", "delivered-event.json", "t0.json",
                                  "membership.json"])
def test_a_fifo_in_place_of_a_leg_file_is_named_not_read(tmp_path, name):
    """FIFO-HANG: every read goes through the S_ISREG guard, so a FIFO is a
    named failure instead of a blocking open."""
    bundle = _bundle(tmp_path)
    leg = "revoked" if name == "membership.json" else "neg-stale"
    target = _leg(bundle, leg) / name
    target.unlink()
    os.mkfifo(target)
    with pytest.raises(checker.Failure) as exc:
        _run_checker(bundle)
    assert "is not a regular file" in str(exc.value), str(exc.value)


def test_unknown_root_entries_are_rejected(tmp_path):
    for i, kind in enumerate(("directory", "file")):
        bundle = _bundle(tmp_path / f"extra-{i}")
        extra = bundle / "legs" / "garbage-leg"
        if kind == "directory":
            extra.mkdir()
        else:
            extra.write_text("garbage\n")
        _expect_failure(bundle, "unexpected leg directories or files")


# --- B3 item 1: closure is containment, root AND leg -------------------------
def test_leg_replaced_by_a_symlink_to_an_outside_copy_is_refused(tmp_path):
    """LEG-SYMLINK (VERIFY-B2 F1's exact attack): the expected leg directory
    legs/neg-stale replaced by a symlink to a complete OUTSIDE copy."""
    bundle = _bundle(tmp_path)
    target = _leg(bundle, "neg-stale")
    outside = tmp_path / "outside-neg-stale"
    target.rename(outside)
    os.symlink(outside, target, target_is_directory=True)
    msg = _expect_failure(bundle, "is a symlink")
    assert "neg-stale" in msg


def test_evidence_root_replaced_by_a_symlink_is_refused(tmp_path):
    """ROOT-SYMLINK."""
    bundle = _bundle(tmp_path)
    moved = tmp_path / "moved-legs"
    (bundle / "legs").rename(moved)
    os.symlink(moved, bundle / "legs", target_is_directory=True)
    msg = _expect_failure(bundle, "is a symlink")
    assert "evidence root" in msg


def test_replay_subleg_replaced_by_a_symlink_is_refused(tmp_path):
    bundle = _bundle(tmp_path)
    target = _leg(bundle, "neg-replayed") / "second"
    outside = tmp_path / "outside-second"
    target.rename(outside)
    os.symlink(outside, target, target_is_directory=True)
    _expect_failure(bundle, "neg-replayed/second: second sub-leg directory is a symlink")


def test_extra_regular_file_inside_a_leg_is_refused(tmp_path):
    """LEG-EXTRA-FILE."""
    bundle = _bundle(tmp_path)
    (_leg(bundle, "neg-stale") / "garbage.txt").write_text("unaccounted\n")
    _expect_failure(bundle, "neg-stale: unexpected entries ['garbage.txt']")


def test_missing_required_file_inside_a_leg_is_named(tmp_path):
    bundle = _bundle(tmp_path)
    (_leg(bundle, "neg-stale") / "t0.json").unlink()
    _expect_failure(bundle, "neg-stale: missing ['t0.json']")


def test_replay_leg_must_carry_exactly_the_two_subleg_directories(tmp_path):
    bundle = _bundle(tmp_path)
    (_leg(bundle, "neg-replayed") / "third").mkdir()
    _expect_failure(bundle, "neg-replayed: expected exactly the sub-leg directories")


def _runner_output_writes(text: str) -> tuple[set[str], list[str]]:
    """Parse the bounded grammar permitted to write a literal ``$out`` path.

    Recognised writers are cp, tee, shell redirection (including a heredoc), mv,
    and Python write_text/open-with-write-mode. Dynamic ``$out`` assignments and
    writers targeting an unresolved shell variable are refused. Other executable
    lines that name ``"$out/..."`` must match one of the runner's bounded
    read/call/remove forms or is refused as unrecognised rather than silently
    omitted.
    """
    writes = set()
    unrecognised = []
    static_roots = {
        match.group(1)
        for raw in text.splitlines()
        if (match := re.match(r"^\s*([A-Za-z_]\w*)=([^#]*)$", raw))
        and "$out" not in match.group(2)
    }
    variable_path = r'"\$([A-Za-z_]\w*)[^\"]*"'
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        dynamic_out_assignment = re.search(r"\b\w+=[^#]*\$out\b", line)
        variable_target = (
            re.search(rf'(?:^|\s)\d*>>?\s*{variable_path}', line)
            or (
                re.search(r"(?:^|\|)\s*tee(?:\s+-\S+)*\s+", line)
                and re.search(variable_path, line)
            )
            or (
                re.match(r"(?:cp|mv)\b", line)
                and re.search(rf'{variable_path}\s*$', line)
            )
            or (
                ("write_text" in line or re.search(
                    r"\bopen\([^)]*,\s*['\"][wax][bt+]*['\"]", line
                ))
                and re.search(variable_path, line)
            )
        )
        unresolved_variable_target = (
            variable_target
            and variable_target.group(1) != "out"
            and variable_target.group(1) not in static_roots
        )
        if unresolved_variable_target or (
            dynamic_out_assignment
            and "local_first_t0=$(" not in line
            and "first_bytes=$(" not in line
        ):
            unrecognised.append(f"line {lineno}: {line}")
            continue

        paths = re.findall(r'"\$out/([^"]+)"', line)
        if not paths:
            continue

        if re.match(r"cp\b", line):
            target = re.search(r'"\$out/([^"]+)"\s*$', line)
            if target:
                writes.add(target.group(1))
                continue
        elif re.search(r"(?:^|\|)\s*tee(?:\s+-\S+)*\s+", line):
            writes.update(paths)
            continue
        elif re.search(r'(?:^|\s)\d*>>?\s*"\$out/[^"]+"', line):
            writes.update(
                match.group(1)
                for match in re.finditer(r'\d*>>?\s*"\$out/([^"]+)"', line)
            )
            continue
        elif re.match(r"mv\b", line):
            target = re.search(r'"\$out/([^"]+)"\s*$', line)
            if target:
                writes.add(target.group(1))
                continue
        elif "write_text" in line or re.search(
            r"\bopen\([^)]*,\s*['\"][wax][bt+]*['\"]", line
        ):
            writes.update(paths)
            continue

        if (
            re.match(r"(?:if\s+)?grep\b", line)
            or re.match(r"rm\s+-", line)
            or re.match(r"mkdir\s+-", line)
            or re.match(r"(?:if\s+!)?\s*cmp\b", line)
            or re.match(r"(?:deliver|collect_leg|collect_masked)\b", line)
            or line.startswith("--reuse ")
            or "local_first_t0=$(" in line
        ):
            continue
        unrecognised.append(f"line {lineno}: {line}")
    return writes, unrecognised


def test_runner_output_writes_refuses_variable_root_assignment():
    line = 'out2="$out"'
    writes, unrecognised = _runner_output_writes(line)
    assert writes == set()
    assert unrecognised == [f"line 1: {line}"]


def test_runner_output_writes_refuses_assignment_and_indirect_redirect():
    text = 'f="$out"\n: > "$f/x-indirect"'
    writes, unrecognised = _runner_output_writes(text)
    assert writes == set()
    assert unrecognised == [
        'line 1: f="$out"',
        'line 2: : > "$f/x-indirect"',
    ]


@pytest.mark.parametrize("line", (
    'tee "$g/y"',
    'cp x "$g/y"',
    'mv x "$g/y"',
    ': >> "$g/y"',
    'Path("$g/y").write_text("x")',
    'open("$g/y", "w").write("x")',
))
def test_runner_output_writes_refuses_variable_target_writers(line):
    writes, unrecognised = _runner_output_writes(line)
    assert writes == set()
    assert unrecognised == [f"line 1: {line}"]


def test_runner_output_writes_preserves_static_non_output_roots():
    text = 'MARKERS=/tmp/markers\n: > "$MARKERS/launch.log"'
    assert _runner_output_writes(text) == (set(), [])


def test_leg_file_table_matches_the_runner_writes():
    """Every final runner output is in the checker's exact closure table."""
    text = RUNNER.read_text()
    deliver_text = DELIVER.read_text()

    direct_writes, unrecognised = _runner_output_writes(text)
    assert not unrecognised, f"unrecognised $out path grammar: {unrecognised}"
    producer_writes = set(re.findall(
        r'leg_dir / "([^"]+)"\)\.write_text', deliver_text
    ))
    revoked_only = {"membership.json"}

    # The replay leg's per-delivery DELTA model (issue #17 / M-B) writes its
    # timelines under the $out/<sub-leg>/ prefix (first snapshot via head,
    # second delta via tail). Those two sub-leg paths must not count as
    # top-level bundle leaves: split direct_writes by the sub-leg component.
    subleg_paths = {p for p in direct_writes if "/" in p}
    assert (
        {p.split("/", 1)[0] for p in subleg_paths} <= set(checker.REPLAY_SUBLEGS)
    ), subleg_paths
    top_writes = direct_writes - subleg_paths

    # Root-level leg outputs = the plain closure set (plus membership.json only
    # for the revoked leg); the sub-leg timelines are sub-leg paths, not leaves.
    assert producer_writes | (top_writes - revoked_only) == checker._LEG_FILES_PLAIN
    assert producer_writes | top_writes == checker._LEG_FILES_REVOKED

    # Each sub-leg holds EXACTLY the plain closure set: the deliver-produced
    # files (fixture/delivered-event/delivery/t0) + the runner's snapshot and
    # delta timelines + the collect_masked log. The mirror records only the
    # root `buzzacp.log` from the cp inside collect_masked, but the same masked
    # log is copied into BOTH sub-legs, so add it to the sub-leg set here.
    subleg_files = (
        {p.split("/", 1)[1] for p in subleg_paths}
        | {n for n in producer_writes if n not in revoked_only}
        | {"buzzacp.log"}
    )
    assert subleg_files == set(checker._LEG_FILES_PLAIN), subleg_files

    nested_writers = set(re.findall(
        r'^\s*(?:deliver|collect_leg)\b[^\n]*"\$out/([^"/]+)"', text, re.MULTILINE
    ))
    removed_nested = set(re.findall(
        r'^\s*rm -rf "\$out/([^"/]+)"', text, re.MULTILINE
    ))
    assert removed_nested == {".probe"}
    assert nested_writers - removed_nested == set(checker.REPLAY_SUBLEGS)

    # Keep the producer and cp shape checks: the set equality above is the
    # closure gate; these assertions preserve a precise failure for a moved seam.
    for name in checker._LEG_FILES_PLAIN - {"timeline.jsonl", "buzzacp.log"}:
        assert f'"{name}"' in deliver_text, f"{name} has no producer in deliver_event.py"
    assert 'cp "$FD/timeline.jsonl" "$out/timeline.jsonl"' in text
    assert 'cp "$FD/buzzacp.log" "$out/buzzacp.log"' in text
    assert 'cp "$MEMBERSHIP" "$out/membership.json"' in text


def test_checker_wall_clock_timeout_names_a_blocking_fifo(tmp_path):
    bundle = _bundle(tmp_path)
    fifo = _leg(bundle, "neg-stale") / "timeline.jsonl"
    fifo.unlink()
    os.mkfifo(fifo)
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--synthetic-root", str(bundle),
         str(bundle / "legs")],
        capture_output=True, text=True, timeout=5,
    )
    assert proc.returncode == 1
    assert "is not a regular file" in proc.stdout


def test_checker_reuses_the_s0_01_timeline_reader_and_does_not_duplicate_it():
    """The brief's rule: reuse by import, never copy."""
    src = CHECKER.read_text()
    assert "_load_timeline_raw = s0_01._load_timeline_raw" in src
    assert "_require_file = s0_01._require_file" in src
    assert checker._load_timeline_raw is checker.s0_01._load_timeline_raw
    assert checker._require_file is checker.s0_01._require_file
    # No re-implementation: the only timeline READ is the S0-01 reader. The
    # checker may test a timeline path for existence (the deferral rule) but must
    # never open one.
    # Strip the module docstring and comments; only executable lines are screened.
    import ast

    tree = ast.parse(src)
    body = tree.body[1:] if (tree.body and isinstance(tree.body[0], ast.Expr)
                             and isinstance(tree.body[0].value, ast.Constant)) else tree.body
    code_lines = set()
    for node in body:
        for sub in ast.walk(node):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                continue
            if hasattr(sub, "lineno"):
                code_lines.add(sub.lineno)
    lines = src.splitlines()
    for lineno in sorted(code_lines):
        line = lines[lineno - 1]
        if "timeline.jsonl" in line:
            # Post-B3 the deferral gate's existence test is lstat() (F1:
            # containment after the root guard, never through a symlink); the
            # pre-B3 wording required .exists(). The tuple expression is the
            # lstat call's operand on the next line.
            assert (".exists()" in line or "lstat(" in line
                    or 'timeline.jsonl",) + tuple' in line
                    or "for sub in REPLAY_SUBLEGS" in line), (
                f"checker touches a timeline directly: {line.strip()}"
            )
    assert "_load_timeline_raw(leg_dir, leg)" in src


def test_no_llm_or_network_in_the_gate_spine():
    """The no-LLM-judge rule, mechanically."""
    banned = ("openai", "anthropic", "requests.post", "urllib.request", "socket.",
              "subprocess.run", "LLM", "gpt-")
    for path in (CHECKER, PROOF / "oracle" / "denial_table.py"):
        text = path.read_text()
        for word in banned:
            assert word not in text, f"{path.name} references {word!r}"


def test_checker_exits_64_on_a_usage_error():
    proc = subprocess.run([sys.executable, str(CHECKER)], capture_output=True, text=True)
    assert proc.returncode == 64
    assert "usage:" in proc.stderr


def test_synthetic_root_is_a_command_line_parameter_not_an_env_channel():
    """AF-AP-23/os.environ-is-not-a-config-channel: the anchors cannot be set
    from the environment, so a bundle cannot select what it is judged against."""
    src = CHECKER.read_text()
    assert "os.environ" not in src and "getenv" not in src
    proc = subprocess.run([sys.executable, str(CHECKER), str(PASS_BUNDLE / "legs")],
                          cwd=ROOT, capture_output=True, text=True,
                          env={**os.environ, "S0_02_SYNTHETIC_ROOT": str(PASS_BUNDLE)})
    assert proc.returncode == 1, proc.stdout + proc.stderr


def test_pc_runner_parses_and_never_kills_by_name():
    """AF-AP-34: no pkill/killall/name match anywhere in the PC runner."""
    assert subprocess.run(["bash", "-n", str(RUNNER)]).returncode == 0
    text = RUNNER.read_text()
    code = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
    for word in ("pkill", "killall", "pgrep"):
        assert word not in code, f"{word} in the PC runner's executable lines"
    assert 'readlink "/proc/$pid/exe"' in code


def test_pc_runner_preserves_membership_receipt_across_the_leg_wipe():
    text = RUNNER.read_text()
    assert 'MEMBERSHIP=${S0_02_MEMBERSHIP:-$DEST/revoked-membership.json}' in text
    wipe = text.index('rm -rf "$out"')
    copy = text.index('cp "$MEMBERSHIP" "$out/membership.json"')
    assert wipe < copy
    assert 'if [ ! -f "$MEMBERSHIP" ]' in text
    assert '"http_status":NNN' in text


def test_pc_runner_replay_window_and_nip98_guard_are_pinned():
    text = RUNNER.read_text()
    replay = text[text.index("neg-replayed)"):text.index("neg-bad-signature)")]
    assert "sleep 1" in replay
    assert "NIP-98 same-second" in replay
    assert '"$out/first/t0.json"' in replay
    assert '--t0 "$local_first_t0"' in replay
    # issue #17 / M-B (D-036): the per-delivery DELTA model and the dual
    # sub-leg masked log. Each pin below is paired with a behavioural control:
    #   cmp -n   -> item 6a (prefix-mismatch control, the named code + text)
    #   tail -c  -> item 6b (mid-line snapshot; first + delta == final)
    #   collect_masked "$out/first" / "$out/second" -> item 5 (the integration
    #   test runs the real main for neg-replayed and the real checker requires
    #   buzzacp.log in BOTH sub-legs and nothing at the leg root, C:569-574).
    # A source-text pin alone is a mirror (AF-AP-80): the controls above close
    # the loop.
    delta = text[text.index("delta_timeline() {"):text.index("collect_masked() {")]
    assert 'cmp -n "$first_bytes" "$out/first/timeline.jsonl" "$FD/timeline.jsonl"' in delta
    assert 'tail -c +$((first_bytes + 1)) "$FD/timeline.jsonl" > "$out/second/timeline.jsonl"' in delta
    assert 'S0-02: neg-replayed final timeline does not extend the first snapshot (prefix mismatch)' in delta
    assert "return \"$S0_02_REPLAY_PREFIX_MISMATCH\"" in delta
    assert "S0_02_REPLAY_PREFIX_MISMATCH=8" in text
    assert 'collect_masked "$out/first"' in text
    assert 'collect_masked "$out/second"' in text
    # the masked log lands in BOTH sub-legs and NOT at the leg root for the
    # replay leg (the main-tail branch, item 5 / M-B). Split the branch into
    # the then (replay leg) and else (every other leg) arms: the then arm must
    # write the two sub-leg copies and NOT the root copy, the else arm keeps the
    # single root copy.
    main_tail = text[text.index('if [ "$leg" = "neg-replayed" ]'):text.index('done', text.index('if [ "$leg" = "neg-replayed" ]'))]
    then_branch = main_tail[:main_tail.index("else")]
    else_branch = main_tail[main_tail.index("else"):]
    assert 'collect_masked "$out/first"' in then_branch
    assert 'collect_masked "$out/second"' in then_branch
    assert 'collect_masked "$out"\n' not in then_branch, (
        "the replay leg must not keep the root masked-log copy"
    )
    assert 'collect_masked "$out"\n' in else_branch, (
        "every other leg must keep its single root masked-log copy"
    )
    assert checker.REPLAY_CLOCK_TOLERANCE_S > 100 + 30
    assert checker.LEG_CLOCK_TOLERANCE_S < checker.REPLAY_CLOCK_TOLERANCE_S
    assert (
        checker.REPLAY_CLOCK_TOLERANCE_S + checker.LEG_CLOCK_TOLERANCE_S
        < checker.RELAY_DRIFT_WINDOW_S
    ), "the replay tolerance plus ordinary-leg slack must stay inside relay drift"
    turn_wait = re.search(
        r"^TURN_WAIT_S=\$\{S0_02_TURN_WAIT_S:-(\d+)\}$", text, re.MULTILINE
    )
    assert turn_wait, "runner TURN_WAIT_S default must remain a literal integer"
    assert int(turn_wait.group(1)) <= checker.REPLAY_CLOCK_TOLERANCE_S, (
        "runner replay wait must fit inside the checker's replay tolerance"
    )


def test_pc_runner_names_user2_for_the_not_allowlisted_leg():
    text = RUNNER.read_text()
    assert "neg-not-allowlisted" in text
    fixture = json.loads((FIXTURES / "neg-not-allowlisted.json").read_text())
    assert fixture["signer"]["role"] == "user2"
    assert 'role_for "$leg"' in text


def test_pc_runner_preflights_and_selects_the_s0_02_env_set():
    """The runner proves and selects the pinned RUST_LOG=debug extension."""
    text = RUNNER.read_text()
    preflight = text[
        text.index("if ! grep -Eq"):text.index("mkdir -p \"$DEST\"")
    ]
    assert "exit 3" in preflight and "RUST_LOG=debug" in preflight
    assert "PINNED_ENV_KEYS_S0_02" in preflight
    assert "PINNED_ENV_VALUES_S0_02" in preflight
    assert "grep -Eq '^PINNED_ENV_KEYS_S0_02" in preflight
    assert "grep -Fqx 'PINNED_ENV_VALUES_S0_02" in preflight

    pins = (ROOT / "proofs" / "S0-01" / "pins.py").read_text()
    assert 'PINNED_ENV_KEYS_S0_02 = PINNED_ENV_KEYS | frozenset({"RUST_LOG"})' in pins
    assert 'PINNED_ENV_VALUES_S0_02 = {"RUST_LOG": "debug"}' in pins

    launch = text[text.index("launch_leg() {"):text.index("stop_leg() {")]
    assert '--env-set s0-02' in launch


def test_deliver_event_never_puts_a_secret_in_argv():
    """AF-AP-39: the key comes from the environment, the file name from argv."""
    text = DELIVER.read_text()
    assert 'os.environ.get("BUZZ_PRIVATE_KEY"' in text
    assert "--secret" in text
    before_key_read = text.split("def main", 1)[1].split("privkey = _privkey()", 1)[0]
    assert "args.secret" not in before_key_read
    # The secret file is only ever NAMED, never read or printed by this tool.
    assert "read_text()" not in text.split("--secret", 1)[1].split("--relay-http", 1)[0]


def test_deliver_normalizer_exposes_echo_provenance():
    normalise = builder.deliver_event._normalise
    event_id = "a" * 64
    accepted = normalise(
        200,
        json.dumps({"event_id": event_id, "accepted": True, "message": ""}),
        event_id,
    )
    rejected = normalise(400, json.dumps({"error": "invalid"}), event_id)
    assert accepted == {
        "accepted": True, "event_id": event_id, "event_id_echoed": True,
        "http_status": 200, "message": "",
    }
    # The relay names an "error" field, not "message"; the malformed-accepted
    # reason must not be clobbered. The raw body is the message.
    assert rejected["accepted"] is False
    assert rejected["event_id"] == event_id
    assert rejected["event_id_echoed"] is False
    assert rejected["http_status"] == 400
    assert rejected["message"] == json.dumps({"error": "invalid"})


# --- B3 item 2: accepted is a bool or the receipt says why -------------------
def test_normalise_takes_accepted_only_when_upstream_is_bool():
    """AF-AP-72 (VERIFY-B2 F2): the truthiness leak is closed. A relay response
    {"accepted":"false"} is stored as accepted=false WITH the reason, never as
    the truthy true."""
    normalise = builder.deliver_event._normalise
    event_id = "b" * 64
    for raw_accepted, type_name in (
        ("false", "str"), ("true", "str"),
        (0, "int"), (1, "int"),
        (1.0, "float"),
        (None, "NoneType"),
        ([], "list"),
    ):
        raw = json.dumps({"event_id": event_id, "accepted": raw_accepted})
        receipt = normalise(200, raw, event_id)
        assert receipt["accepted"] is False, f"{raw_accepted!r} stored accepted truthy"
        assert f"malformed relay response: accepted is {type_name} {raw_accepted!r}"\
            in receipt["message"], receipt["message"]
        assert receipt["http_status"] == 200
    absent = normalise(200, json.dumps({"event_id": event_id}), event_id)
    assert absent["accepted"] is False
    assert absent["message"] == json.dumps(
        {"event_id": event_id}
    ), "the raw body is the message when the blob names no message and no malformed reason"
    for truthy in (True, False):
        receipt = normalise(200, json.dumps({"event_id": event_id, "accepted": truthy}),
                            event_id)
        assert receipt["accepted"] is truthy
        assert receipt["message"] == json.dumps(
            {"event_id": event_id, "accepted": truthy}
        ), f"a well-typed accepted={truthy!r} must not drag a malformed reason"


def test_privkey_normalises_then_refuses_before_any_network_action():
    """F3: whitespace-only and malformed-shape keys die in _privkey, BEFORE the
    signing or delivery code can touch them."""

    # The signed event for the expired auth tag with a valid throwaway key: the
    # AST scan below proves the shape check sits before the network use.
    src = DELIVER.read_text()
    before_post = src.split("def _post", 1)[0]
    assert "BUZZ_PRIVATE_KEY is not a valid key shape" in before_post
    assert "exactly 64 lowercase hex" in before_post
    authed = DELIVER.read_text().split("def _privkey", 1)[1].split("def _nip98_header", 1)[0]
    assert 'os.environ.get("BUZZ_PRIVATE_KEY", "").strip().lower()' in authed


# --- B6 (issue #3, VERIFY-B4 F3 / B4-05): the refusal EXECUTED, not scanned ---
# The F3 test above proves the source shape (the guard sits before _post in the
# file). A shape-guard bypass mutant (the hex check weakened to a length-only
# check, the refusal message kept) SURVIVES it, because nothing there runs the
# CLI: the real downstream then refuses a 64-char non-hex key at the signer
# (nv.sign_event) before _post, and the behaviour is still correct but
# untested at the boundary. These tests close that gap: they run the REAL CLI
# against an OWNED 127.0.0.1 listener and count connections — a zero that can
# become a one (item 3 is the positive control that makes the zero meaningful).

# The shape-refusal SystemExit text, verbatim from deliver_event.py `_privkey`
# (D = the production file; this string is the contract the CLI must keep
# emitting).
REFUSE_TEXT = (
    "BUZZ_PRIVATE_KEY is not a valid key shape (exactly 64 lowercase hex "
    "characters, as nv.sign_event requires)"
)
# The source names the exit: both refusals are `raise SystemExit(...)` with a
# str payload, and Python exits 1 on a str SystemExit — D:80 and D:85.
REFUSE_RC = 1
B8_SCALAR_REFUSE_TEXT = (
    "BUZZ_PRIVATE_KEY is outside the secp256k1 scalar range "
    "1..n-1 (n is the curve order, as nv.sign_event requires)"
)
T0 = 1700000000


class _OwnedListener:
    """A 127.0.0.1-only HTTP endpoint that counts every accepted connection
    and returns a minimal 200 so a connecting client completes its exchange.
    The test process owns both ends; the listener is stopped at test exit."""

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("127.0.0.1", 0))
        self.server.listen(8)
        self.port = self.server.getsockname()[1]
        self.count = 0
        self.requests = []
        self._stop = False
        self._thread = threading.Thread(
            target=self._serve, name="b6-owned-listener", daemon=True)

    def _serve(self):
        # Accept with a timeout so the thread exits when the test stops it.
        self.server.settimeout(0.25)
        while not self._stop:
            try:
                conn, _addr = self.server.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            self.count += 1
            try:
                conn.settimeout(10)
                data = b""
                while b"\r\n\r\n" not in data:
                    chunk = conn.recv(65536)
                    if not chunk:
                        break
                    data += chunk
                self.requests.append(data)
                conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\n{}")
            except OSError:
                pass
            finally:
                conn.close()

    def start(self):
        self._thread.start()
        return self

    def stop(self):
        self._stop = True
        self.server.close()
        self._thread.join(timeout=1)


def _run_deliver_cli(tmp_path: Path, listener, env_extra=None):
    """Run the REAL deliver_event.py CLI in a subprocess with a closed
    environment (AF-AP-39: the key travels only via env, never argv)."""
    env = dict(env_extra or {})
    for name in ("B8_MUTANT_D",):
        if name in os.environ:
            env[name] = os.environ[name]
    proc = subprocess.run(
        [
            sys.executable, str(DELIVER),
            "--fixture", "pos-allowed",
            "--leg-dir", str(tmp_path / "leg"),
            "--secret", "role.env",
            "--relay-http", f"http://127.0.0.1:{listener.port}",
            "--t0", str(T0),
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
    )
    return proc


def test_cli_refuses_a_malformed_key_before_any_connection(tmp_path: Path):
    """B6 item 2 — the F3 refusal EXECUTED through the real CLI. A 64-char
    NON-hex key (64 x 'z') must die in _privkey BEFORE any network action:
    the CLI exits with the source-named SystemExit rc (1), prints the
    exact refusal text on stderr, and the owned listener sees ZERO
    connections. (The F3-KEY-SHAPE-BYPASS mutant of item 1 passes the old
    source-shape test but is killed here: with the hex check weakened the CLI
    reaches the signer, which refuses with a different rc (traceback, rc 1 but
    a different stderr) — and if the signer were absent the connection count
    would be 1, which this assert forbids.)"""
    listener = _OwnedListener().start()
    try:
        proc = _run_deliver_cli(
            tmp_path, listener,
            env_extra={"BUZZ_PRIVATE_KEY": "z" * 64},
        )
        assert proc.returncode == REFUSE_RC, (
            f"rc={proc.returncode} stderr={proc.stderr.decode()[:400]!r}")
        assert proc.stderr.decode("utf-8").strip() == REFUSE_TEXT, (
            f"wrong refusal text: {proc.stderr.decode('utf-8')[:400]!r}")
        assert listener.count == 0, (
            f"refusal attempted a connection (count={listener.count}) — "
            "a pre-network refusal must never touch the relay")
    finally:
        listener.stop()


def _throwaway_secp256k1_key() -> str:
    """Return a deterministic well-formed test-only scalar for secp256k1.

    Hashing a public label keeps the test reproducible and avoids any real key
    material. Reduce into 1..n-1, where n is the curve order consumed by the
    real signer.
    """
    curve_n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    candidate = int.from_bytes(hashlib.sha256(b"S0-02-B6-test-only-key").digest(), "big")
    return f"{candidate % (curve_n - 1) + 1:064x}"


def test_cli_with_a_valid_key_reaches_the_owned_listener(tmp_path: Path):
    """B6 item 3 — the PAIRED POSITIVE CONTROL. The same CLI, same listener,
    but with a WELL-FORMED throwaway key (a deterministic test-only SHA-256
    derivation reduced into secp256k1's 1..n-1 scalar range, never a real key):
    the CLI must sign and POST, so the owned listener must see exactly ONE
    connection and the request must arrive. This is what makes the item-2
    zero meaningful: a listener that could never observe a connection would
    make the zero tautological."""
    privkey = _throwaway_secp256k1_key()
    assert len(privkey) == 64 and all(c in "0123456789abcdef" for c in privkey)
    listener = _OwnedListener().start()
    try:
        proc = _run_deliver_cli(
            tmp_path, listener,
            env_extra={"BUZZ_PRIVATE_KEY": privkey},
        )
        # The CLI completes the exchange (200 from our listener) and writes
        # its leg files — it is a full delivery, not an error path.
        assert proc.returncode == 0, (
            f"rc={proc.returncode} stderr={proc.stderr.decode()[:400]!r}")
        assert listener.count == 1, (
            f"expected exactly one connection, saw {listener.count}")
        # The request actually reached the listener: an HTTP POST to /events
        # with a NIP-98 Authorization header.
        assert len(listener.requests) == 1
        req = listener.requests[0].decode("latin-1")
        assert req.startswith("POST /events HTTP/1.1"), req[:80]
        assert "Authorization:" in req and "Nostr " in req
        assert "Content-Type: application/json" in req
    finally:
        listener.stop()

# --- B8: runner follow-up + issue #15 behavioural regressions ----------------
# These tests use only scratch trees, throwaway keys, closed loopback ports, and
# labelled launcher/post-step doubles. They never start the real launcher or
# touch the pinned relay, harness, or secrets.

B8_EMPTY_REFUSE_TEXT = (
    "BUZZ_PRIVATE_KEY is not in the environment — source the role secret "
    "file before calling (set -a; . <role>.env; set +a)"
)


def _b8_function_source(source: Path, name: str) -> str:
    """Extract one shell function verbatim by balanced braces."""
    lines = source.read_text().splitlines(keepends=True)
    start = next(
        i for i, line in enumerate(lines)
        if re.match(rf"^{re.escape(name)}\(\) \{{\s*$", line)
    )
    depth = 0
    for end in range(start, len(lines)):
        code = lines[end].split("#", 1)[0]
        depth += code.count("{") - code.count("}")
        if end > start and depth == 0:
            return "".join(lines[start:end + 1])
    raise AssertionError(f"unterminated shell function {name}")


def _b8_shell_function(
    source: Path,
    name: str,
    body: str,
    *,
    env: dict[str, str],
    timeout: int = 15,
):
    script = "set -euo pipefail\n" + _b8_function_source(source, name) + "\n" + body
    return subprocess.run(
        ["bash", "-c", script],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _b8_runner_env(tmp_path: Path, launcher: Path | None = None) -> dict[str, str]:
    frame = tmp_path / "frame"
    frame.mkdir(parents=True, exist_ok=True)
    env = {
        **os.environ,
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "FD": str(frame),
        "MARKERS": str(frame),
        "S0_02_PINNED": str(tmp_path / "pinned"),
        "HOST_LEG": "run-1",
        "POLL_S": "0.05",
        "TURN_WAIT_S": "1",
    }
    if launcher is not None:
        env["LAUNCHER"] = str(launcher)
    return env


def _b8_write_launcher(path: Path, *, ready: bool) -> None:
    """Create a labelled launcher double for sourced-function tests only."""
    body = [
        "#!/usr/bin/env python3",
        "# B8 labelled launcher double: no service or network access.",
        "from pathlib import Path",
        "import os",
        "frame = Path(os.environ['S0_02_PINNED']) / '.markers' / 'v2-run-1'",
    ]
    if ready:
        body.append("frame.joinpath('launch.ready').write_text('ready\\n')")
    else:
        body.append("pass")
    path.write_text("\n".join(body) + "\n")
    path.chmod(0o755)


def _b8_preflight_tree(
    tmp_path: Path, pins_text: str
) -> tuple[Path, Path, Path, dict[str, str]]:
    repo = tmp_path / "repo"
    pinned = tmp_path / "pinned"
    pins = repo / "proofs" / "S0-01" / "pins.py"
    pins.parent.mkdir(parents=True)
    pins.write_text(pins_text)
    fixtures = repo / "proofs" / "S0-02" / "fixtures"
    fixtures.mkdir(parents=True)
    (fixtures / "pos-allowed.json").write_text(
        json.dumps({"signer": {"role": "owner"}}) + "\n"
    )
    deliver = repo / "proofs" / "S0-02" / "tools" / "pc" / "deliver_event.py"
    deliver.parent.mkdir(parents=True)
    deliver.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "import os\n"
        "Path(os.environ['B8_TRACE']).write_text(\n"
        "    Path(os.environ['B8_TRACE']).read_text() + 'deliver'\n"
        "    if Path(os.environ['B8_TRACE']).exists() else 'deliver'\n"
        ")\n"
        "raise SystemExit('B8_NAMED_DELIVER_REFUSAL: no key in scratch environment')\n"
    )
    deliver.chmod(0o755)
    launcher = repo / "proofs" / "S0-01" / "tools" / "pc" / "pc_launch.py"
    launcher.parent.mkdir(parents=True)
    _b8_write_launcher(launcher, ready=True)
    (pinned / ".markers" / "v2-run-1").mkdir(parents=True)
    (pinned / ".secrets").mkdir(parents=True)
    dest = tmp_path / "dest"
    trace = tmp_path / "trace"
    post = repo / "proofs" / "S0-01" / "tools" / "pc" / "pc_post.sh"
    post.parent.mkdir(parents=True, exist_ok=True)
    post.write_text(
        "#!/usr/bin/env bash\n"
        "printf 'masked log\\n' > \"$FD/buzzacp.log\"\n"
        "printf post >> \"$B8_POST_TRACE\"\n"
    )
    post.chmod(0o755)
    env = {
        **os.environ,
        "B8_TRACE": str(trace),
        "B8_POST_TRACE": str(trace),
        "S0_02_REPO": str(repo),
        "S0_02_PINNED": str(pinned),
        "S0_02_RELAY_HTTP": "http://127.0.0.1:1",
        "S0_02_TURN_WAIT_S": "0",
    }
    return dest, pinned, trace, env


def test_wait_turn_window_handles_absent_zero_and_n_matches(tmp_path):
    """D1: absent, zero-match, and N-match timelines yield numeric counts."""
    env = _b8_runner_env(tmp_path)
    frame = Path(env["FD"])
    function = _b8_function_source(RUNNER, "wait_turn_window")
    cases = (
        ("absent", None, 0),
        ("zero", '{"method":"session/update"}\n', 0),
        (
            "three",
            ''.join('{"method":"session/prompt"}\n' for _ in range(3)),
            3,
        ),
    )
    for label, content, expected in cases:
        timeline = frame / "timeline.jsonl"
        timeline.unlink(missing_ok=True)
        if content is not None:
            timeline.write_text(content)
        proc = subprocess.run(
            ["bash", "-c", function + "\nwait_turn_window 0"],
            env=env,
            capture_output=True,
            text=True,
            timeout=5,
        )
        # The exact value is established by the same count expression R uses.
        count = subprocess.run(
            ["bash", "-c", (
                "n=$(grep -c '\"method\":\"session/prompt\"' \"$FD/timeline.jsonl\" "
                "2>/dev/null || true); n=${n:-0}; printf '%s' \"$n\""
            )],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        assert count.stdout == str(expected), (label, count.stdout, count.stderr)
        assert proc.returncode == 0, (label, proc.stderr)
        assert "integer expression expected" not in proc.stderr, (label, proc.stderr)
        # The N-match arm also proves the function takes its immediate-success
        # branch: a mutated fixed count of zero would exceed this subprocess
        # timeout rather than return from the count condition.
        if label == "three":
            immediate = {**env, "TURN_WAIT_S": "5", "POLL_S": "1"}
            hit = subprocess.run(
                ["bash", "-c", function + "\nwait_turn_window 3"],
                env=immediate,
                capture_output=True,
                text=True,
                timeout=2,
            )
            assert hit.returncode == 0, hit.stderr


def test_collect_leg_succeeds_before_masked_log_exists(tmp_path):
    """D2: turn-window collection copies timeline before the post-step log."""
    env = _b8_runner_env(tmp_path)
    frame = Path(env["FD"])
    (frame / "timeline.jsonl").write_text('{"method":"session/update"}\n')
    out = tmp_path / "out"
    proc = _b8_shell_function(
        RUNNER,
        "collect_leg",
        'collect_leg "$OUT"',
        env={**env, "OUT": str(out)},
    )
    assert proc.returncode == 0, proc.stderr
    assert (out / "timeline.jsonl").read_text() == '{"method":"session/update"}\n'
    assert not (out / "buzzacp.log").exists()


def test_collect_masked_waits_for_post_step_and_keeps_refusal(tmp_path):
    """D2: post-stop collection waits for the real producer condition."""
    env = _b8_runner_env(tmp_path)
    env["TURN_WAIT_S"] = "2"
    frame = Path(env["FD"])
    out = tmp_path / "out"
    out.mkdir()
    producer = subprocess.Popen(
        [sys.executable, "-c", (
            "import pathlib,time; time.sleep(.2); "
            f"p=pathlib.Path({str(frame)!r}); "
            "p.joinpath('buzz-acp.exit').write_text('0\\n'); "
            "p.joinpath('buzzacp.log').write_text('masked log\\n')"
        )]
    )
    try:
        proc = _b8_shell_function(
            RUNNER,
            "collect_masked",
            'collect_masked "$OUT"',
            env={**env, "OUT": str(out), "POLL_S": "0.05"},
        )
    finally:
        producer.wait(timeout=5)
    assert proc.returncode == 0, proc.stderr
    assert (out / "buzzacp.log").read_text() == "masked log\n"

    (frame / "buzzacp.log").write_text("0" * 64 + "\n")
    refusal = _b8_shell_function(
        RUNNER,
        "collect_masked",
        'collect_masked "$OUT"',
        env={**env, "OUT": str(out), "POLL_S": "0.05"},
    )
    assert refusal.returncode == 7, refusal.stderr
    assert "REFUSING to keep" in refusal.stderr
    assert not (out / "buzzacp.log").exists()


def test_post_leg_invokes_the_scratch_post_after_exit(tmp_path):
    """D2: actual post_leg calls the post producer after the exit marker."""
    env = _b8_runner_env(tmp_path)
    frame = Path(env["FD"])
    frame.joinpath("buzz-acp.exit").write_text("0\n")
    repo = tmp_path / "post-repo"
    post = repo / "proofs" / "S0-01" / "tools" / "pc" / "pc_post.sh"
    post.parent.mkdir(parents=True)
    trace = tmp_path / "post.trace"
    observed_fd = tmp_path / "post.fd"
    post.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s' \"$FD\" > \"$B8_POST_FD\"\n"
        "printf post > \"$B8_POST_TRACE\"\n"
        "printf 'masked log\\n' > \"$FD/buzzacp.log\"\n"
    )
    post.chmod(0o755)
    proc = _b8_shell_function(
        RUNNER,
        "post_leg",
        "post_leg",
        env={
            **env,
            "REPO": str(repo),
            "B8_POST_TRACE": str(trace),
            "B8_POST_FD": str(observed_fd),
        },
    )
    assert proc.returncode == 0, proc.stderr
    assert trace.read_text() == "post"
    assert observed_fd.read_text() == str(frame)
    assert (frame / "buzzacp.log").read_text() == "masked log\n"


def test_main_orders_stop_post_and_masked_collection(tmp_path):
    """D2: real R's main loop runs stop, post, then masked collection."""
    exact = (
        'PINNED_ENV_KEYS_S0_02 = PINNED_ENV_KEYS | frozenset({"RUST_LOG"})\n'
        'PINNED_ENV_VALUES_S0_02 = {"RUST_LOG": "debug"}\n'
    )
    dest, _pinned, _trace, env = _b8_preflight_tree(tmp_path, exact)
    order = tmp_path / "order"
    script = """
source "$R"
launch_leg() { printf L >> "$B8_ORDER"; }
deliver() { printf D >> "$B8_ORDER"; }
role_for() { printf owner; }
wait_turn_window() { printf W >> "$B8_ORDER"; }
collect_leg() { printf C >> "$B8_ORDER"; }
stop_leg() { printf S >> "$B8_ORDER"; }
post_leg() { printf P >> "$B8_ORDER"; }
collect_masked() { printf M >> "$B8_ORDER"; }
main "$DEST" pos-allowed
"""
    proc = subprocess.run(
        ["bash", "-c", script],
        cwd=ROOT,
        env={
            **env,
            "R": str(RUNNER),
            "DEST": str(dest),
            "B8_ORDER": str(order),
        },
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert proc.returncode == 0, proc.stderr
    assert order.read_text() == "LDWCSPM"


def test_launch_leg_removes_only_stale_owned_markers_before_launcher(tmp_path):
    """D3: stale ready/exit/pid markers cannot satisfy a new launch."""
    launcher = tmp_path / "never-ready.py"
    _b8_write_launcher(launcher, ready=False)
    env = _b8_runner_env(tmp_path, launcher)
    frame = Path(env["FD"])
    for name in ("launch.ready", "buzz-acp.exit", "buzz-acp.pid"):
        (frame / name).write_text("stale\n")
    survivor = frame / "must-survive"
    survivor.write_text("owned evidence\n")
    proc = _b8_shell_function(
        RUNNER,
        "launch_leg",
        "launch_leg",
        env=env,
        timeout=5,
    )
    assert proc.returncode == 4, proc.stderr
    for name in ("launch.ready", "buzz-acp.exit", "buzz-acp.pid"):
        assert not (frame / name).exists(), name
    assert survivor.read_text() == "owned evidence\n"


def _b8_load_deliver(source: Path):
    """Load a named scratch delivery source without executing its CLI entrypoint."""
    return _load("s0_02_b8_deliver", source)


def test_privkey_refuses_scalar_outside_range_before_signing(monkeypatch):
    """#15 row 1: direct guard has named refusal for both scalar boundaries."""
    for candidate in ("0" * 64, "f" * 64):
        monkeypatch.setenv("BUZZ_PRIVATE_KEY", candidate)
        with pytest.raises(SystemExit) as exc:
            _b8_load_deliver(DELIVER)._privkey()
        assert str(exc.value) == B8_SCALAR_REFUSE_TEXT


def test_cli_normalises_padded_and_uppercase_keys_before_connecting(tmp_path):
    """#15 row 2: CLI coverage kills a dropped .strip() or .lower()."""
    key = _throwaway_secp256k1_key()
    for label, candidate in (("padded", f"  {key}\n"), ("uppercase", key.upper())):
        listener = _OwnedListener().start()
        try:
            proc = _run_deliver_cli(
                tmp_path / label,
                listener,
                env_extra={"BUZZ_PRIVATE_KEY": candidate},
            )
        finally:
            listener.stop()
        assert proc.returncode == 0, proc.stderr.decode()
        assert listener.count == 1


def test_cli_refuses_empty_and_out_of_range_keys_before_connecting(tmp_path):
    """#15 rows 1-2: named refusals replace the consumer traceback."""
    for label, candidate, text in (
        ("empty", " \t\n ", B8_EMPTY_REFUSE_TEXT),
        ("zero", "0" * 64, B8_SCALAR_REFUSE_TEXT),
        ("above-order", "f" * 64, B8_SCALAR_REFUSE_TEXT),
    ):
        listener = _OwnedListener().start()
        try:
            proc = _run_deliver_cli(
                tmp_path / label,
                listener,
                env_extra={"BUZZ_PRIVATE_KEY": candidate},
            )
        finally:
            listener.stop()
        stderr = proc.stderr.decode("utf-8")
        assert proc.returncode == 1, (label, stderr)
        assert text in stderr, (label, stderr)
        assert "Traceback" not in stderr, (label, stderr)
        assert listener.count == 0, label


def test_real_runner_rejects_commented_pin_before_creating_dest(tmp_path):
    """#15 rows 3-4: exact-line preflight is behavioural and ordered."""
    commented = (
        'PINNED_ENV_KEYS_S0_02 = {"RUST_LOG"} # not the pinned expression\n'
        'PINNED_ENV_VALUES_S0_02 = {"RUST_LOG": "debug"} # commented suffix\n'
    )
    dest, _pinned, _trace, env = _b8_preflight_tree(tmp_path, commented)
    proc = subprocess.run(
        ["bash", str(RUNNER), str(dest), "pos-allowed"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert proc.returncode == 3, proc.stderr
    assert "BLOCKER: pins.PINNED_ENV_KEYS_S0_02" in proc.stderr
    assert not dest.exists()


def test_real_runner_passes_exact_pins_then_stops_at_labelled_deliver(tmp_path):
    """#15 row 4 positive arm: preflight passes without a real launch."""
    exact = (
        'PINNED_ENV_KEYS_S0_02 = PINNED_ENV_KEYS | frozenset({"RUST_LOG"})\n'
        'PINNED_ENV_VALUES_S0_02 = {"RUST_LOG": "debug"}\n'
    )
    dest, pinned, trace, env = _b8_preflight_tree(tmp_path, exact)
    (pinned / ".secrets" / "owner.env").write_text(
        "# B8 labelled empty secret; no real key material\n"
    )
    proc = subprocess.run(
        ["bash", str(RUNNER), str(dest), "pos-allowed"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert dest.exists(), proc.stderr
    assert (pinned / ".markers" / "v2-run-1" / "launch.ready").exists()
    assert proc.returncode == 1, proc.stderr
    assert "B8_NAMED_DELIVER_REFUSAL" in proc.stderr
    assert trace.read_text() == "deliver"
    assert not (dest / "pos-allowed" / "timeline.jsonl").exists()

# ---------------------------------------------------------------------------
# B9 (issue #17 / D-036) -- the per-delivery DELTA model in the runner, the
# masked log into BOTH sub-legs, and the producer->consumer integration.
# The sourced replay portion runs with a FAKE process (launcher/post) and a
# FAKE deliver (the deliver CLI's leg files + what the live process appends);
# the REAL stop_leg, wait_turn_window, snapshot_timeline, delta_timeline,
# collect_masked and main are unchanged. The no-space timeline is the real
# producer's wire format (frame_tee.py:369). B9-R1 (VERIFY-B9 F-7): each
# delivery's receipt is deliver_event's REAL _normalise over the pinned relay's
# 200 body for it, and the masked log is ONE process's, built here -- neither is
# copied from the synthetic fixture's second sub-leg.
# ---------------------------------------------------------------------------
B9_SUB_FIRST = PASS_BUNDLE / "legs" / "neg-replayed" / "first"
B9_PASS_LINE = (
    "PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; "
    "replay refused by the relay's duplicate: receipt (buzz-acp drop line absent, "
    "defense-in-depth only); "
    "+1 revocation leg (assertion 2); removal evidence: coordinator-supplied receipt "
    "(unauthenticated; ordering and fields verified; not an end-to-end revocation proof)"
)
# A labelled double of ONE buzz-acp process's masked log (pc_post.sh:107): one
# start banner (lib.rs:2454), the DEBUG canary (relay.rs:1716), the pool line.
B9_ONE_PROCESS_LOG = (
    "2026-09-23T00:00:00.100000Z  INFO buzz_acp: buzz-acp starting: relay=ws://127.0.0.1:1 "
    "pubkey=<HEX> agents=1 ignore_self=true respond_to=owner-only (B9-R1 test double)\n"
    "2026-09-23T00:00:00.200000Z DEBUG buzz_acp::relay: startup watermark set to 1788800000\n"
    "2026-09-23T00:00:00.300000Z  INFO buzz_acp: agent_pool_ready agents=1\n"
)
# Two prompt-free records that continue the committed first timeline (seq 8, 9)
# on the builder's own clock.
B9_DELTA = "".join(
    json.dumps({"dir": "a2c", "frame": {"jsonrpc": "2.0", "method": "session/update", "params": {}},
                "seq": s, "t_mono_ns": 4689461162919584 + s * 100_000_000,
                "t_utc": builder._iso(s * 100)}, separators=(",", ":")) + "\n"
    for s in (8, 9)
)


def _b9_ns(txt: str) -> str:
    """The producer wire format: compact (no-space) JSON, one frame per line.
    wait_turn_window greps no-space; the checker's JSON parser is agnostic."""
    return "".join(json.dumps(json.loads(l), separators=(",", ":")) + "\n"
                   for l in txt.splitlines() if l.strip())


def _b9_tree(tmp_path: Path) -> tuple[Path, Path, Path]:
    """The runner preflight's scratch tree (B8's pattern): pins + fixtures +
    .markers + .secrets, with a fresh frame dir as $FD."""
    repo = tmp_path / "repo"
    pinned = tmp_path / "pinned"
    pins = repo / "proofs" / "S0-01" / "pins.py"
    pins.parent.mkdir(parents=True)
    pins.write_text(
        'PINNED_ENV_KEYS_S0_02 = PINNED_ENV_KEYS | frozenset({"RUST_LOG"})\n'
        'PINNED_ENV_VALUES_S0_02 = {"RUST_LOG": "debug"}\n'
    )
    fx = repo / "proofs" / "S0-02" / "fixtures"
    fx.mkdir(parents=True)
    (fx / "pos-allowed.json").write_text(json.dumps({"signer": {"role": "owner"}}) + "\n")
    (fx / "neg-replayed.json").write_text(json.dumps({"signer": {"role": "owner"}}) + "\n")
    (pinned / ".markers").mkdir(parents=True)
    (pinned / ".secrets").mkdir(parents=True)
    # R sets FD=$PINNED/.markers/v2-run-1 when sourced (it ignores a caller's
    # FD); create exactly that frame dir so the sourced production bytes run.
    frame = pinned / ".markers" / "v2-run-1"
    frame.mkdir()
    return repo, pinned, frame


def _b9_env(tmp_path: Path, runner: Path, turn_wait: str = "0") -> dict[str, str]:
    """The sourced runner's environment. TURN_WAIT_S is read when R is sourced
    (R:34); POLL_S and FD are NOT (R:35 and R:33 overwrite them, VERIFY-B9 I-4):
    FD here only names the frame dir R computes, and the driver sets POLL_S from
    B9_POLL_S after the source."""
    repo, pinned, frame = _b9_tree(tmp_path)
    return {
        **os.environ,
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "S0_02_REPO": str(repo),
        "S0_02_PINNED": str(pinned),
        "S0_02_RELAY_HTTP": "http://127.0.0.1:1",
        "S0_02_TURN_WAIT_S": turn_wait,
        "FD": str(frame),
        "MARKERS": str(pinned / ".markers"),
        "B9_R": str(runner),
        "B9_DEST": str(tmp_path / "dest"),
        "B9_POLL_S": "0.01",
    }


def _b9_records() -> list[str]:
    """The committed first sub-leg's seven records in the producer's no-space
    wire format: initialize, result, session/new, result, session/prompt,
    session/update, result (seq 1..7)."""
    return _b9_ns((B9_SUB_FIRST / "timeline.jsonl").read_text()).splitlines(keepends=True)


def _b9_record(line: str, **changes) -> str:
    rec = json.loads(line)
    rec.update(changes)
    return json.dumps(rec, separators=(",", ":")) + "\n"


def _b9_receipt(event_id: str, message: str) -> str:
    """deliver_event's REAL _normalise (the producer module, loaded by path)
    over the pinned relay's 200 body {event_id, accepted, message}
    (bridge.rs:963-968), serialised as deliver_event.main writes delivery.json.
    message '' = a NEW kind-9 event (ingest.rs:3270-3274); 'duplicate:' = an
    id the relay already stored (ingest.rs:3192-3197)."""
    raw = json.dumps({"event_id": event_id, "accepted": True, "message": message})
    receipt = builder.deliver_event._normalise(200, raw, event_id)
    return json.dumps(receipt, indent=1, sort_keys=True) + "\n"


def _b9_run(tmp_path: Path, runner: Path, *, first: str, second: str = "",
            first_late: str = "", second_late: str = "",
            second_message: str = "duplicate:", log: str = B9_ONE_PROCESS_LOG,
            turn_wait: str = "0", extra: str = "",
            ) -> tuple[subprocess.CompletedProcess, Path, list[str]]:
    """Drive the runner's real main for neg-replayed. launch_leg/deliver/post
    are labelled fakes; the real stop_leg sees no fake pidfile, takes its
    no-pidfile path, and returns 0. Each delivery appends `first`/`second` to the
    live timeline at once and ARMS `*_late`, which the next sleep appends (the
    live window's latency, deterministic). The first receipt is the relay's
    new-event answer, the second's message is `second_message`; the post step
    leaves `log` as the ONE masked log. `extra` (if any) is inserted after the
    source and before main so it overrides a production definition. Returns
    (proc, the leg, the trace of delivers and late appends)."""
    env = _b9_env(tmp_path, runner, turn_wait)
    work = tmp_path / "b9"
    work.mkdir(parents=True, exist_ok=True)
    event = B9_SUB_FIRST / "delivered-event.json"
    event_id = json.loads(event.read_text())["id"]
    for name, text in (("append-first", first), ("late-first", first_late),
                       ("append-second", second), ("late-second", second_late),
                       ("buzzacp.log", log), ("armed", ""), ("trace", ""),
                       ("receipt-first.json", _b9_receipt(event_id, "")),
                       ("receipt-second.json", _b9_receipt(event_id, second_message))):
        (work / name).write_text(text)
    env.update({
        "B9_DIR": str(work),
        "B9_FIXTURES": str(PASS_BUNDLE / "fixtures"),
        "B9_EVENT": str(event),
        "B9_T0": str(json.loads((B9_SUB_FIRST / "t0.json").read_text())["t0_epoch_s"]),
    })
    script = _B9_DRIVER.replace(
        'main "$B9_DEST" neg-replayed',
        (extra + "\n" if extra else "") + 'main "$B9_DEST" neg-replayed',
    )
    proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=60)
    trace = (work / "trace").read_text().splitlines()
    return proc, Path(env["B9_DEST"]) / "neg-replayed", trace


def _b9_check(bundle_root: Path, leg: Path) -> str:
    """Swap the runner-produced leg into a copy of the committed bundle and run
    the REAL checker against it (exactly as the existing replay tests do)."""
    dst = bundle_root / "legs" / "neg-replayed"
    assert dst.exists(), "the committed pass bundle must include neg-replayed"
    shutil.rmtree(dst)
    shutil.copytree(leg, dst)
    return _run_checker(bundle_root)


def _b9_pin_runner(tmp_path: Path) -> Path:
    """The PIN's runner bytes (git show 71463f3:...) into a scratch file."""
    pin = subprocess.run(
        ["git", "show", "71463f3:proofs/S0-02/tools/pc/run_s0_02_legs.sh"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    p = tmp_path / "pin_runner.sh"
    p.write_text(pin)
    return p


_B9_DRIVER = r'''
# B9 driver: source the ENTIRE runner (real main, wait_turn_window,
# snapshot_timeline, delta_timeline, collect_masked, stop_leg) and override ONLY
# the process side (launch/post) and the delivery side (deliver). This is the
# exact replay portion of the runner, per issue #17's required test.
source "$B9_R"
# Sourcing set POLL_S=5 (R:35) and FD (R:33) over the caller's env (VERIFY-B9
# I-4), so the test's poll interval is applied here, AFTER the source.
POLL_S=$B9_POLL_S
# Latency without a race: a delivery ARMS bytes; the first sleep after that (a
# poll inside a live window, or R's NIP-98 spacing sleep) appends them.
sleep() {
  if [ -s "$B9_DIR/armed" ]; then
    cat "$B9_DIR/armed" >> "$FD/timeline.jsonl"; : > "$B9_DIR/armed"; echo late >> "$B9_DIR/trace"
  fi
  command sleep "$@"
}
launch_leg() { touch "$FD/launch.ready"; }
# stop_leg stays the production function. The fake process writes no pidfile, so
# the real stop_leg prints "no pidfile — nothing of ours to stop" and returns 0.
# The fake post step writes the exit marker and the ONE masked log of the one
# process (pc_post.sh's role; the real pc_post.sh never runs).
post_leg() { touch "$FD/buzz-acp.exit"; cp "$B9_DIR/buzzacp.log" "$FD/buzzacp.log"; }
# deliver <fixture> <leg-dir> <role> [--reuse <event.json>] [--t0 <epoch>]: the
# deliver CLI's leg files (fixture, the posted event -- the --reuse file verbatim
# for the second delivery --, t0, and the receipt the test built with the REAL
# _normalise), then what the live process appends to the timeline.
deliver() {
  local fixture=$1 legdir=$2 role=$3 which reuse="" t0=$B9_T0; shift 3
  while [ $# -gt 0 ]; do
    case "$1" in --reuse) reuse=$2; shift 2 ;; --t0) t0=$2; shift 2 ;; *) shift ;; esac
  done
  if [ "$fixture" = "pos-allowed" ]; then which=first; else which=second; fi
  echo "deliver $which" >> "$B9_DIR/trace"
  mkdir -p "$legdir"
  cp "$B9_FIXTURES/$fixture.json" "$legdir/fixture.json"
  cp "${reuse:-$B9_EVENT}" "$legdir/delivered-event.json"
  printf '{\n "leg": "%s",\n "signed_by_secret_file": "%s.env",\n "t0_epoch_s": %s\n}\n' \
    "$fixture" "$role" "$t0" > "$legdir/t0.json"
  cp "$B9_DIR/receipt-$which.json" "$legdir/delivery.json"
  cat "$B9_DIR/append-$which" >> "$FD/timeline.jsonl"
  cp "$B9_DIR/late-$which" "$B9_DIR/armed"
  return 0
}
main "$B9_DEST" neg-replayed
'''


# --- item 5: the producer->consumer integration (cases A, B, C) -------------

def test_replay_integration_runner_producer_into_real_checker(tmp_path):
    """ITEM 5 case A -- the issue #17 producer->consumer integration. The
    sourced replay portion (real main + real wait_turn_window +
    snapshot_timeline + delta_timeline + collect_masked, a fake process and a
    fake deliver) runs end-to-end for neg-replayed; its leg is swapped into a
    full copy of the evidence-pass bundle and the REAL checker must pass.
    B9-R1 (F-7): D-036's shape end to end -- the second receipt is the REAL
    _normalise over the relay's duplicate answer, ONE process, ONE log, and a
    NON-empty delta: the first turn's terminal frames (seq 6, 7) land after the
    boundary, at R's NIP-98 spacing sleep, continuing the snapshot's seq 5."""
    recs = _b9_records()
    # A live window (2 s): wait_turn_window 1 returns on the prompt count at
    # once (R:86), before any sleep, so the late frames arrive at R:236's sleep.
    proc, leg, trace = _b9_run(tmp_path, RUNNER, first="".join(recs[:5]),
                               first_late="".join(recs[5:]), turn_wait="2")
    assert proc.returncode == 0, proc.stderr
    assert trace == ["deliver first", "late", "deliver second"], trace
    assert "no pidfile" in proc.stdout, "the real stop_leg no-pidfile path must run"
    # the leg shape the checker requires (C:569-574, C:143-149):
    assert sorted(p.name for p in leg.iterdir()) == ["first", "second"]
    assert not (leg / "buzzacp.log").exists(), "the replay leg must keep no root masked log"
    for sub in ("first", "second"):
        subd = leg / sub
        assert sorted(p.name for p in subd.iterdir()) == [
            "buzzacp.log", "delivered-event.json", "delivery.json",
            "fixture.json", "t0.json", "timeline.jsonl"], sub
    # the DELTA model: first = 1-prompt snapshot, second = the post-boundary
    # delta (0 prompts); one continuous process -> one masked log, byte-
    # identical in both sub-legs (masking runs only after exit, pc_post.sh:107).
    first = (leg / "first" / "timeline.jsonl").read_text()
    second = (leg / "second" / "timeline.jsonl").read_text()
    assert first == "".join(recs[:5]) and second == "".join(recs[5:]), "first + delta split at seq 5"
    assert first.count('"method":"session/prompt"') == 1, "first must carry 1 prompt"
    assert second.count('"method":"session/prompt"') == 0, "second delta must carry 0 prompts"
    assert (leg / "first" / "buzzacp.log").read_text() == (
        leg / "second" / "buzzacp.log").read_text() == B9_ONE_PROCESS_LOG, "one masked log in both sub-legs"
    event_id = json.loads((leg / "second" / "delivered-event.json").read_text())["id"]
    assert json.loads((leg / "second" / "delivery.json").read_text()) == {
        "http_status": 200, "event_id": event_id, "accepted": True,
        "message": "duplicate:", "event_id_echoed": True}, "the relay's duplicate receipt"
    bundle = _bundle(tmp_path)
    line = _b9_check(bundle, leg)
    assert line == B9_PASS_LINE, line


def test_replay_integration_empty_delta_second_timeline_passes(tmp_path):
    """ITEM 5 case B -- D-036's core live shape: the relay refused the duplicate
    before dispatch, so the final timeline is the first snapshot and the
    post-boundary delta is EMPTY. The runner writes a zero-byte second timeline
    (it never fabricates lines); the real checker accepts it on the relay's
    duplicate receipt alone, with no buzz-acp drop line in the ONE log."""
    proc, leg, trace = _b9_run(tmp_path, RUNNER, first="".join(_b9_records()))
    assert proc.returncode == 0, proc.stderr
    assert trace == ["deliver first", "deliver second"], trace
    second = leg / "second" / "timeline.jsonl"
    assert second.exists() and second.stat().st_size == 0, "empty delta is a valid runner output"
    assert (leg / "second" / "buzzacp.log").read_text() == B9_ONE_PROCESS_LOG, "no drop line"
    bundle = _bundle(tmp_path)
    line = _b9_check(bundle, leg)
    assert line == B9_PASS_LINE, line


def test_replay_integration_pin_runner_reproduces_the_failure(tmp_path):
    """ITEM 5 case C -- the red-first reproduction. The SAME harness over the
    PIN's runner bytes (git show 71463f3:...) must be REFUSED by the real
    checker: the PIN's root-level masked log trips the replay closure first
    (M-B, C:569-574); with M-B alone repaired the cumulative second timeline
    trips the turn count (M-A, C:621-624). Both exact texts are asserted. The
    live timeline is the one-process D-036 shape (the whole first turn, nothing
    for the duplicate), so the PIN's cumulative second copy IS the first turn."""
    pin = _b9_pin_runner(tmp_path)
    proc, leg, _trace = _b9_run(tmp_path, pin, first="".join(_b9_records()))
    assert proc.returncode == 0, proc.stderr
    # M-B: the PIN wrote the masked log at the leg root (nothing in the sub-legs)
    assert (leg / "buzzacp.log").exists(), "PIN M-B: root-level masked log"
    bundle = _bundle(tmp_path)
    err = None
    try:
        _b9_check(bundle, leg)
    except checker.Failure as exc:
        err = str(exc)
    assert err == (
        "neg-replayed: expected exactly the sub-leg directories "
        "['first', 'second'], got ['buzzacp.log', 'first', 'second']"
    ), err
    # M-B alone repaired (dual sub-leg copy, cumulative second still present):
    # the closure passes and the cumulative second's 1 prompt trips C:621-624.
    mbsrc = pin.read_text().replace(
        '  stop_leg\n  post_leg\n  collect_masked "$out"\ndone',
        '  stop_leg\n  post_leg\n  if [ "$leg" = "neg-replayed" ]; then\n'
        '    collect_masked "$out/first"\n    collect_masked "$out/second"\n'
        '  else\n    collect_masked "$out"\n  fi\ndone')
    assert mbsrc != pin.read_text(), "the M-B fix did not apply to the PIN bytes"
    mb = tmp_path / "pin_mb_runner.sh"
    mb.write_text(mbsrc)
    proc2, leg2, _trace2 = _b9_run(tmp_path / "mb", mb, first="".join(_b9_records()))
    assert proc2.returncode == 0, proc2.stderr
    assert not (leg2 / "buzzacp.log").exists(), "M-B fixed: no root log"
    assert (leg2 / "second" / "buzzacp.log").exists(), "M-B fixed: sub-leg log"
    bundle2 = _bundle(tmp_path / "mbbundle")
    err2 = None
    try:
        _b9_check(bundle2, leg2)
    except checker.Failure as exc:
        err2 = str(exc)
    assert err2 == (
        "neg-replayed/second: 1 ACP turn(s), expected 0 — the duplicate "
        "delivery produced a second turn"
    ), err2


# --- item 6: the prefix-proof and boundary controls -------------------------

def _b9_boundary(tmp_path: Path, case: str, live: str) -> str:
    """A sourced R with the live timeline preloaded into $FD, then the named
    boundary case run against the REAL snapshot_timeline / delta_timeline."""
    env = _b9_env(tmp_path, RUNNER)
    outdir = tmp_path / "boundary"
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "live").write_text(live)
    env.update({"B9_CASE": case, "B9_OUT": str(outdir), "B9_LIVE": str(outdir / "live")})
    script = (
        'source "$B9_R"\n'
        'mkdir -p "$B9_OUT"\n'
        'cat "$B9_LIVE" > "$FD/timeline.jsonl"\n'
        'case "$B9_CASE" in\n'
        '  a)\n'
        '    first_bytes=$(snapshot_timeline "$B9_OUT")\n'
        '    printf X | dd of="$FD/timeline.jsonl" bs=1 seek=0 conv=notrunc status=none\n'
        '    set +e; delta_timeline "$B9_OUT" "$first_bytes" 2>"$B9_OUT/err"; rc=$?; set -e\n'
        '    echo "rc=$rc first=$first_bytes"\n'
        '    echo "second=$( [ -f "$B9_OUT/second/timeline.jsonl" ] && wc -c < "$B9_OUT/second/timeline.jsonl" || echo ABSENT)"\n'
        '    echo "err=$(cat "$B9_OUT/err")"\n'
        '    ;;\n'
        '  b)\n'
        '    first_bytes=$(snapshot_timeline "$B9_OUT")\n'
        '    last=$(tail -c 1 "$B9_OUT/first/timeline.jsonl" | od -An -tu1 | tr -d " \\n")\n'
        '    echo "first_last_byte=$last first_size=$(wc -c < "$B9_OUT/first/timeline.jsonl")"\n'
        '    printf %s "-DONE" >> "$FD/timeline.jsonl"\n'
        '    set +e; delta_timeline "$B9_OUT" "$first_bytes"; rc=$?; set -e\n'
        '    echo "rc=$rc first=$first_bytes"\n'
        '    cat "$B9_OUT/first/timeline.jsonl" "$B9_OUT/second/timeline.jsonl" > "$B9_OUT/concat"\n'
        '    if cmp -s "$B9_OUT/concat" "$FD/timeline.jsonl"; then echo "concat_ok=yes"; else echo "concat_ok=NO"; fi\n'
        '    ;;\n'
        '  c)\n'
        '    first_bytes=$(snapshot_timeline "$B9_OUT")\n'
        '    set +e; delta_timeline "$B9_OUT" "$first_bytes"; rc=$?; set -e\n'
        '    echo "rc=$rc first=$first_bytes"\n'
        '    echo "second=$( [ -f "$B9_OUT/second/timeline.jsonl" ] && wc -c < "$B9_OUT/second/timeline.jsonl" || echo ABSENT)"\n'
        '    ;;\n'
        'esac\n'
    )
    proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


def test_replay_prefix_proof_refuses_a_non_extension(tmp_path):
    """ITEM 6a -- the final live timeline is NOT an extension of the first
    snapshot (a byte inside the first region changed after the snapshot): the
    named code 8, the exact stderr text, and NO second timeline."""
    f = _b9_ns((B9_SUB_FIRST / "timeline.jsonl").read_text())
    live = f
    out = _b9_boundary(tmp_path, "a", live)
    assert "rc=8" in out, out
    assert "second=ABSENT" in out, "a prefix mismatch must write no second timeline"
    assert "final timeline does not extend the first snapshot (prefix mismatch)" in out, out


def test_replay_mid_line_snapshot_first_plus_delta_equals_final(tmp_path):
    """ITEM 6b -- the live file ends MID-LINE at snapshot time: the first
    snapshot ends at the last newline (the partial line never enters it), and
    first + delta == the final live timeline byte-for-byte. B9-R1 (VERIFY-B9
    B-2): the concatenation holds for ANY cut, so the cut itself is asserted --
    the snapshot ends with a newline and is exactly the complete lines' bytes."""
    f = _b9_ns((B9_SUB_FIRST / "timeline.jsonl").read_text())
    live = f + "PARTIAL-WRITER-BYTES"
    out = _b9_boundary(tmp_path, "b", live)
    assert "rc=0" in out, out
    complete = len(f.encode())
    assert f"first_last_byte=10 first_size={complete}\n" in out, out
    assert f"rc=0 first={complete}\n" in out, out
    assert "concat_ok=yes" in out, "first (cut at last nl) + delta must equal the final timeline byte-for-byte"


def test_replay_empty_delta_writes_zero_byte_second(tmp_path):
    """ITEM 6c -- the relay dropped the duplicate: the final timeline is the
    first snapshot, so the post-boundary delta is EMPTY. delta_timeline writes a
    zero-byte second timeline (the runner never fabricates lines)."""
    f = _b9_ns((B9_SUB_FIRST / "timeline.jsonl").read_text())
    out = _b9_boundary(tmp_path, "c", f)
    assert "rc=0" in out, out
    assert "second=0" in out, "the empty delta is a zero-byte file"


# --- item 7: the mutants (each run in place; the killer is the named test) ---

def test_replay_mutant_cumulative_second_is_rejected(tmp_path):
    """ITEM 7 m1 -- the PIN's behavior: the second sub-leg gets the CUMULATIVE
    live timeline (1 prompt, not the 0-prompt delta). The real checker must
    refuse at C:621-624. Only delta_timeline is overridden; main and the real
    snapshot_timeline stay production bytes."""
    override = ('delta_timeline() { local out=$1 first_bytes=$2; mkdir -p "$out/second"; '
                'cp "$FD/timeline.jsonl" "$out/second/timeline.jsonl"; }\n')
    _, leg, _trace = _b9_run(tmp_path, RUNNER, first="".join(_b9_records()), extra=override)
    bundle = _bundle(tmp_path)
    err = None
    try:
        _b9_check(bundle, leg)
    except checker.Failure as exc:
        err = str(exc)
    assert err == (
        "neg-replayed/second: 1 ACP turn(s), expected 0 — the duplicate "
        "delivery produced a second turn"
    ), err


def test_replay_mutant_no_prefix_proof_still_writes_second(tmp_path):
    """ITEM 7 m2 -- the cmp -n prefix proof is removed (the delta always
    writes). The final live is NOT an extension of the snapshot (a byte changed
    in the first region): the proof-less delta still writes the bad second (a
    second exists), while the REAL delta (the 6a boundary, proof ON) refuses the
    same input. The kill is 6a; this proves the proof is what refuses."""
    f = _b9_ns((B9_SUB_FIRST / "timeline.jsonl").read_text())
    s = B9_DELTA
    live = f + s
    override = ('delta_timeline() { local out=$1 first_bytes=$2; mkdir -p "$out/second"; '
                'tail -c +$((first_bytes + 1)) "$FD/timeline.jsonl" > "$out/second/timeline.jsonl"; }\n')
    env = _b9_env(tmp_path, RUNNER)
    (Path(env["FD"]) / "timeline.jsonl").write_text(live)
    outdir = tmp_path / "m2out"; outdir.mkdir(parents=True, exist_ok=True)
    env.update({"B9_OUT": str(outdir)})
    script = ('source "$B9_R"\n' + override +
              '\nfirst_bytes=$(snapshot_timeline "$B9_OUT")\n'
              'printf X | dd of="$FD/timeline.jsonl" bs=1 seek=0 conv=notrunc status=none\n'
              'set +e; delta_timeline "$B9_OUT" "$first_bytes"; rc=$?; set -e\n'
              'echo "rc=$rc second=$( [ -f "$B9_OUT/second/timeline.jsonl" ] && wc -c < "$B9_OUT/second/timeline.jsonl" || echo ABSENT)"\n')
    proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=30)
    assert "second=" in proc.stdout and "ABSENT" not in proc.stdout, proc.stdout
    # the REAL delta (proof ON) refuses the same input:
    out = _b9_boundary(tmp_path / "control", "a", live)
    assert "rc=8" in out, "the REAL delta (with the proof) must refuse this"


def test_replay_mutant_off_by_one_delta_breaks_concatenation(tmp_path):
    """ITEM 7 m3 -- the delta start is off by one (`tail -c +$first_bytes`
    instead of `+$((first_bytes + 1))`): GNU tail's 1-based offset begins one
    byte too early, so first + delta has a duplicated boundary byte and is not
    byte-for-byte the same as final. The real (correct) delta makes them equal."""
    f = _b9_ns((B9_SUB_FIRST / "timeline.jsonl").read_text())
    s = B9_DELTA
    live = f + s
    override = ('delta_timeline() { local out=$1 first_bytes=$2; mkdir -p "$out/second"; '
                'tail -c +$first_bytes "$FD/timeline.jsonl" > "$out/second/timeline.jsonl"; }\n')
    env = _b9_env(tmp_path, RUNNER)
    (Path(env["FD"]) / "timeline.jsonl").write_text(live)
    outdir = tmp_path / "m3out"; outdir.mkdir(parents=True, exist_ok=True)
    env.update({"B9_OUT": str(outdir)})
    script = ('source "$B9_R"\n' + override +
              '\nfirst_bytes=$(snapshot_timeline "$B9_OUT")\n'
              'set +e; delta_timeline "$B9_OUT" "$first_bytes"; rc=$?; set -e\n'
              'cat "$B9_OUT/first/timeline.jsonl" "$B9_OUT/second/timeline.jsonl" > "$B9_OUT/concat"\n'
              'if cmp -s "$B9_OUT/concat" "$FD/timeline.jsonl"; then echo "concat_ok=yes"; else echo "concat_ok=NO"; fi\n')
    proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=30)
    assert "concat_ok=NO" in proc.stdout, "off-by-one delta must break first+delta==final"


def test_replay_mutant_root_only_masked_log_is_rejected(tmp_path):
    """ITEM 7 m4 -- the PIN's M-B: the masked log lands at the leg root only.
    The real checker's replay closure refuses (C:569-574). The mutation is the
    PIN runner's unchanged main tail (`collect_masked "$out"`), exercised by the
    same process/delivery doubles as case C."""
    pin = _b9_pin_runner(tmp_path)
    _, leg, _trace = _b9_run(tmp_path, pin, first="".join(_b9_records()))
    assert (leg / "buzzacp.log").exists(), "m4: the log is at the leg root"
    bundle = _bundle(tmp_path)
    err = None
    try:
        _b9_check(bundle, leg)
    except checker.Failure as exc:
        err = str(exc)
    assert err == (
        "neg-replayed: expected exactly the sub-leg directories "
        "['first', 'second'], got ['buzzacp.log', 'first', 'second']"
    ), err


def test_replay_mutant_masked_log_first_only_fails_second_closure(tmp_path):
    """ITEM 7 m5 -- the masked log goes to the first sub-leg ONLY: the second
    sub-leg's closure is missing buzzacp.log."""
    override = ('collect_masked() { if [ "$1" = "$B9_DEST/neg-replayed/first" ]; then '
                'cp "$FD/buzzacp.log" "$1/buzzacp.log"; fi; }\n')
    _, leg, _trace = _b9_run(tmp_path, RUNNER, first="".join(_b9_records()), extra=override)
    assert not (leg / "second" / "buzzacp.log").exists(), "m5: no log in the second sub-leg"
    bundle = _bundle(tmp_path)
    err = None
    try:
        _b9_check(bundle, leg)
    except checker.Failure as exc:
        err = str(exc)
    assert err == "neg-replayed/second: missing ['buzzacp.log']", err


def test_replay_mutant_snapshot_not_cut_at_newline(tmp_path):
    """ITEM 7 m6 -- the first snapshot is NOT cut at the last newline (it takes
    the whole live file, including the mid-line partial). The snapshot therefore
    does not end on a newline, violating item 6b's boundary assertion. The delta
    prefix proof would still pass because this malformed snapshot is a byte
    prefix; the newline-boundary control is what kills this mutant."""
    f = _b9_ns((B9_SUB_FIRST / "timeline.jsonl").read_text())
    live = f + "PARTIAL"
    override = ('snapshot_timeline() { local out=$1; mkdir -p "$out/first"; '
                'cp "$FD/timeline.jsonl" "$out/first/timeline.jsonl"; '
                'printf %s "$(wc -c < "$FD/timeline.jsonl")"; }\n')
    env = _b9_env(tmp_path, RUNNER)
    (Path(env["FD"]) / "timeline.jsonl").write_text(live)
    outdir = tmp_path / "m6out"; outdir.mkdir(parents=True, exist_ok=True)
    env.update({"B9_OUT": str(outdir)})
    script = ('source "$B9_R"\n' + override +
              '\nfirst_bytes=$(snapshot_timeline "$B9_OUT")\n'
              'last=$(tail -c 1 "$B9_OUT/first/timeline.jsonl" | od -An -tu1 | tr -d " \\n")\n'
              'if [ "$last" = "10" ]; then echo "first_ends_nl=yes"; else echo "first_ends_nl=NO"; fi\n')
    proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=30)
    assert "first_ends_nl=NO" in proc.stdout, "m6: the snapshot is not cut at a newline"


# --- B9-R1: the live windows through the sourced main (VERIFY-B9 B-1, F-5, F-12) ---

def _b9_verdict(tmp_path: Path, leg: Path) -> str:
    """The real checker's verdict on a runner-produced leg: the PASS line or the
    Failure text."""
    try:
        return _b9_check(_bundle(tmp_path / "verdict"), leg)
    except checker.Failure as exc:
        return str(exc)


def test_replay_observation_window_catches_a_late_second_turn(tmp_path):
    """B-1 (replaces B9's m7 'EQUIVALENT' row): the observation window after the
    duplicate (R:241 `wait_turn_window 0`) is live -- S0_02_TURN_WAIT_S=2 and
    POLL_S small after the source -- and the duplicate's turn prompt lands INSIDE
    it, on the window's first poll. The runner must put that prompt in the delta
    and the real checker must refuse it. Deleting the window (m7) or making it
    `wait_turn_window 1` (M13) reads the delta before the prompt lands: an empty
    delta, and the checker's hollow PASS."""
    recs = _b9_records()
    proc, leg, trace = _b9_run(tmp_path, RUNNER, first="".join(recs),
                               second_late=_b9_record(recs[4], seq=8), turn_wait="2")
    assert proc.returncode == 0, proc.stderr
    assert trace == ["deliver first", "deliver second", "late"], trace
    assert (leg / "second" / "timeline.jsonl").read_text() == _b9_record(recs[4], seq=8)
    assert _b9_verdict(tmp_path, leg) == (
        "neg-replayed/second: 1 ACP turn(s), expected 0 — the duplicate delivery "
        "produced a second turn"
    )


def test_replay_first_delivery_that_turns_only_after_the_duplicate_fails(tmp_path):
    """F-5 (M11): the first delivery opened a session but produced no prompt
    inside its window; the turn came after the second delivery. The first
    snapshot must be taken BEFORE the second delivery, so the leg is refused."""
    recs = _b9_records()
    proc, leg, trace = _b9_run(tmp_path, RUNNER, first="".join(recs[:4]),
                               second="".join(recs[4:]), turn_wait="2")
    assert proc.returncode == 0, proc.stderr
    assert trace == ["deliver first", "deliver second"], trace
    assert _b9_verdict(tmp_path, leg) == (
        "neg-replayed/first: 0 ACP turn(s), expected exactly 1 — a replay leg proves "
        "nothing unless the first delivery produced a turn"
    )


def test_replay_slow_first_turn_is_waited_for_before_the_snapshot(tmp_path):
    """F-12 (M14): the first turn's prompt arrives on the first poll of the
    first delivery's window (R:227 `wait_turn_window 1`). The runner waits for
    it, so the snapshot holds the whole turn and the real checker passes."""
    recs = _b9_records()
    proc, leg, trace = _b9_run(tmp_path, RUNNER, first="".join(recs[:4]),
                               first_late="".join(recs[4:]), turn_wait="2")
    assert proc.returncode == 0, proc.stderr
    assert trace == ["deliver first", "late", "deliver second"], trace
    assert (leg / "first" / "timeline.jsonl").read_text() == "".join(recs)
    assert _b9_verdict(tmp_path, leg) == B9_PASS_LINE


def test_replay_runner_forwarded_duplicate_is_refused_on_the_receipt(tmp_path):
    """R6's negative (F-7): the old synthetic shape through the real runner --
    the relay accepted the second delivery as NEW (message '', the real
    _normalise over the relay's new-event answer) and buzz-acp's own drop line
    is in the ONE log. The drop line never substitutes for the receipt."""
    chan = json.loads((PASS_BUNDLE / "identities.json").read_text())["channel"]
    log = B9_ONE_PROCESS_LOG + (
        f"2026-09-23T00:00:05.000000Z DEBUG buzz_acp::relay: dropping duplicate event for channel {chan}\n")
    proc, leg, _trace = _b9_run(tmp_path, RUNNER, first="".join(_b9_records()),
                                second_message="", log=log)
    assert proc.returncode == 0, proc.stderr
    assert _b9_verdict(tmp_path, leg) == (
        "neg-replayed/second: the relay receipt message is '', expected exactly 'duplicate:' "
        "— the relay did not refuse the second delivery as a duplicate (a forwarded duplicate "
        "fails even when buzz-acp dropped it)"
    )


def test_replay_runner_restarted_process_is_refused(tmp_path):
    """F-2 (H1a) through the real runner: the second delivery reaches a
    restarted agent (initialize at seq 1, then session/new) -- a second process."""
    recs = _b9_records()
    proc, leg, _trace = _b9_run(tmp_path, RUNNER, first="".join(recs), second="".join(recs[:4]))
    assert proc.returncode == 0, proc.stderr
    assert _b9_verdict(tmp_path, leg) == (
        "neg-replayed/second: the delta holds an ACP initialize frame (seq 1) — the agent "
        "restarted: a second process, not ONE continuous buzz-acp process (D-036 clause 3)"
    )
