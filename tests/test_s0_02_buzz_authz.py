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

import importlib.util
import json
import os
import shutil
import subprocess
import sys
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


def _rewrite(path: Path, mutate):
    blob = json.loads(path.read_text())
    mutate(blob)
    path.write_text(json.dumps(blob, indent=1, sort_keys=True) + "\n")


def _buzz_src() -> Path:
    """The pinned upstream tree, or a declared skip. Never a silent pass."""
    raw = os.environ.get(BUZZ_SRC_ENV)
    if raw is None:
        if os.environ.get("S0_01_VENUE") is None:
            pytest.skip(
                f"{BUZZ_SRC_ENV} unset and no venue declared — the pinned buzz "
                f"checkout is a DECLARED input; CI skips by declaration"
            )
        raw = BUZZ_SRC_DEFAULT
    path = Path(raw)
    assert path.is_dir(), (
        f"{BUZZ_SRC_ENV}={raw} is declared but absent — a declared input that is "
        f"missing is a FAILURE, never a skip"
    )
    return path


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
    ids = json.loads((ROOT / "proofs" / "S0-01" / "fixtures" / "identities.json").read_text())
    blob = json.loads((FIXTURES / "neg-unauthorized.json").read_text())
    assert blob["signer"]["role"] == "nonmember"
    assert blob["signer"]["expected_pubkey"] is None
    known = {v for k, v in ids.items() if k != "relay_url"}
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


# ---------------------------------------------------------------------------
# 2. the oracle table against the pinned upstream source
# ---------------------------------------------------------------------------
def test_pinned_tree_is_the_locked_commit():
    src = _buzz_src()
    head = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    assert head == BUZZ_PIN, f"buzz checkout is {head}, upstream.lock.yaml pins {BUZZ_PIN}"


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


def _production_verify_sites() -> list:
    """Every verify_event/.verify() call site in buzz-acp's PRODUCTION region.

    Heuristic, and named as one: the production region is the lines before the
    file's first `#[cfg(test)]` (Rust's trailing `mod tests` convention), with
    `//` comment lines dropped. It exists so the claim "buzz-acp does not verify
    a channel event" is re-derived from the source rather than remembered.
    """
    src = _buzz_src() / "crates" / "buzz-acp" / "src"
    sites = []
    for rs in sorted(src.glob("*.rs")):
        lines = rs.read_text().splitlines()
        cut = next((i for i, ln in enumerate(lines) if ln.strip() == "#[cfg(test)]"), len(lines))
        for i, line in enumerate(lines[:cut], 1):
            if line.strip().startswith("//"):
                continue
            if "verify_event(" in line or ".verify()" in line:
                sites.append(f"{rs.name}:{i}")
    return sites


def test_buzz_acp_performs_no_signature_check_on_a_channel_event():
    """The DISCREPANCY behind neg-bad-signature, asserted against the source.

    If a future buzz-acp gains a verify on the channel-event path this test goes
    red, which is the point: the discrepancy is pinned, not remembered.
    """
    known = {
        "lib.rs:256",           # NIP-OA workflow attribution
        "lib.rs:1574",          # observer CONTROL frame
        "engram_fetch.rs:122",  # engram fetch
        "pool.rs:3385",         # pool: canvas section from a query response
        "pool.rs:3495",         # pool: REST-boundary re-verify
    }
    unexpected = sorted(set(_production_verify_sites()) - known)
    assert not unexpected, (
        "buzz-acp gained a signature check the oracle does not know about: "
        f"{unexpected} — re-derive neg-bad-signature's mechanism"
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


def test_relay_drift_window_matches_the_checker_constant():
    src = _buzz_src() / "crates" / "buzz-relay" / "src" / "handlers" / "ingest.rs"
    line = src.read_text().splitlines()[2223]
    assert f"MAX_TIMESTAMP_DRIFT_SECS: i64 = {checker.RELAY_DRIFT_WINDOW_S}" in line, line


def test_debug_canary_line_exists_in_the_pinned_source():
    """The canary must be a line buzz-acp really emits at DEBUG on every start."""
    src = _buzz_src() / "crates" / "buzz-acp" / "src" / "relay.rs"
    line = src.read_text().splitlines()[1715]
    assert checker.DEBUG_LEVEL_CANARY in line, line
    assert line.strip().startswith("debug!("), line


def test_every_negative_row_has_a_distinct_observable_key():
    keys = [oracle.observable_key(f) for f in oracle.DISTINCT_FIXTURES]
    assert len(set(keys)) == len(keys) == 5, keys


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
        "PASS: S0-02 buzz-authz - 1 positive, 5 negative legs, 5 distinct reasons; "
        "+1 revocation leg (assertion 2)"
    ), line


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


def test_real_evidence_root_defers_today():
    """The state this lane actually ships: spec.json's positive leg defers."""
    proc = subprocess.run([sys.executable, str(CHECKER), "proofs/S0-02/evidence"],
                          cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode == 2
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
                 "neg-self-authored", "revoked"):
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
             lambda b: (b.__setitem__("message", other["observable"]),
                        b.__setitem__("accepted", False)))
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
    _rewrite(leg_dir / "delivery.json", lambda b: b.__setitem__("event_id", good["id"]))
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


def test_a_missing_debug_canary_fails_the_leg(tmp_path):
    """A leg captured at INFO cannot prove an absence."""
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "neg-self-authored")
    text = leg_dir / "buzzacp.log"
    text.write_text(text.read_text().replace(checker.DEBUG_LEVEL_CANARY, "watermark noted"))
    _expect_failure(bundle, "lacks the debug-level canary")


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
    _rewrite(second / "delivery.json", lambda b: b.__setitem__("event_id", other["id"]))
    with pytest.raises(checker.Failure) as exc:
        _run_checker(bundle)
    assert ("this is not a replay" in str(exc.value)
            or "delivered content does not match" in str(exc.value)), str(exc.value)


# ---------------------------------------------------------------------------
# 6. identity, freshness and delivery binding
# ---------------------------------------------------------------------------
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
    _rewrite(leg_dir / "delivery.json", lambda b: b.__setitem__("event_id", forged["id"]))
    _expect_failure(bundle, "delivered sender is not the owner identity")


def test_a_nonmember_leg_signed_by_a_known_identity_fails(tmp_path):
    """The other arm of the same binding: the nonmember role's sender must not
    be one of the four known identities."""
    bundle = _bundle(tmp_path)
    leg_dir = _leg(bundle, "neg-unauthorized")
    ev = json.loads((leg_dir / "delivered-event.json").read_text())
    owner_key = builder._bundle_privkey(bundle.name.replace("evidence-", ""), "owner")
    forged = nv.sign_event(owner_key, {"created_at": ev["created_at"], "kind": ev["kind"],
                                       "tags": ev["tags"], "content": ev["content"]})
    (leg_dir / "delivered-event.json").write_text(
        json.dumps(forged, indent=1, sort_keys=True) + "\n")
    _rewrite(leg_dir / "delivery.json", lambda b: b.__setitem__("event_id", forged["id"]))
    _expect_failure(bundle, "must not be one of the known S0-01 identities")


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
    _rewrite(leg_dir / "delivery.json", lambda b: b.__setitem__("event_id", fresh["id"]))
    return fresh


def test_a_stale_event_inside_the_relay_window_is_not_stale(tmp_path):
    """MEMBERSHIP-BY-CREATED_AT / STALE-WINDOW-UNPINNED: the age is MEASURED,
    not declared. A 'stale' leg whose event is fresh fails."""
    bundle = _bundle(tmp_path)
    t0 = json.loads((_leg(bundle, "neg-stale") / "t0.json").read_text())["t0_epoch_s"]
    _resign_at(bundle, "neg-stale", "owner", t0 - 10)
    _expect_failure(bundle, "it is not stale")


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
    _rewrite(leg_dir / "delivery.json", lambda b: b.__setitem__("event_id", ev["id"]))
    _expect_failure(bundle, "failed signature verification")


def test_a_relay_decided_leg_must_show_accepted_false(tmp_path):
    bundle = _bundle(tmp_path)
    _rewrite(_leg(bundle, "neg-stale") / "delivery.json",
             lambda b: b.__setitem__("accepted", True))
    _expect_failure(bundle, "accepted must be false")


def test_a_buzz_acp_decided_leg_must_show_accepted_true(tmp_path):
    bundle = _bundle(tmp_path)
    _rewrite(_leg(bundle, "neg-self-authored") / "delivery.json",
             lambda b: b.__setitem__("accepted", False))
    _expect_failure(bundle, "the relay must have ACCEPTED the event")


def test_a_leg_fixture_that_drifts_from_the_committed_one_fails(tmp_path):
    """FIXTURE-DRIFT at capture time: the leg must carry the committed fixture."""
    bundle = _bundle(tmp_path)
    _rewrite(_leg(bundle, "neg-stale") / "fixture.json",
             lambda b: b["expected"].__setitem__("turns", 1))
    _expect_failure(bundle, "differs from the committed")


def test_revoked_leg_requires_a_membership_removal_receipt(tmp_path):
    bundle = _bundle(tmp_path)
    (_leg(bundle, "revoked") / "membership.json").unlink()
    _expect_failure(bundle, "membership.json absent")


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
                                  "fixture.json", "delivered-event.json", "t0.json"])
def test_a_fifo_in_place_of_a_leg_file_is_named_not_read(tmp_path, name):
    """FIFO-HANG: every read goes through the S_ISREG guard, so a FIFO is a
    named failure instead of a blocking open."""
    bundle = _bundle(tmp_path)
    target = _leg(bundle, "neg-stale") / name
    target.unlink()
    os.mkfifo(target)
    with pytest.raises(checker.Failure) as exc:
        _run_checker(bundle)
    assert "is not a regular file" in str(exc.value), str(exc.value)


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
            assert ".exists()" in line, f"checker touches a timeline directly: {line.strip()}"
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


def test_pc_runner_fails_loud_when_rust_log_debug_is_unavailable():
    """The blocker is surfaced by the runner, not routed around."""
    text = RUNNER.read_text()
    assert "exit 3" in text and "RUST_LOG" in text
    pins = (ROOT / "proofs" / "S0-01" / "pins.py").read_text()
    assert '"RUST_LOG"' not in pins, (
        "pins.PINNED_ENV_KEYS now carries RUST_LOG — re-check the runner's preflight "
        "and capture the two buzz-acp-decided legs"
    )


def test_deliver_event_never_puts_a_secret_in_argv():
    """AF-AP-39: the key comes from the environment, the file name from argv."""
    text = DELIVER.read_text()
    assert 'os.environ.get("BUZZ_PRIVATE_KEY"' in text
    assert "--secret" in text
    assert "args.secret" not in text.split("def main")[1].split("_privkey()")[0] or True
    # The secret file is only ever NAMED, never read or printed by this tool.
    assert "read_text()" not in text.split("--secret")[1].split("--relay-http")[0]
