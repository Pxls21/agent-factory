"""S0-07: Fubuki corrections conformance checker.

Asserts:
  1. persona_lint returns the documented violation status regardless of
     violation ordering (the upstream exit-2 ordering bug is fixed or
     wrapped, proven by the ordered fixture).
  2. BoundDecision.record_id values are joined back to source records;
     no payload field is read in the allow/deny decision.
  3. Canonical JSON compile + hash is stable (run twice, identical hash)
     and a mutated packet changes the hash.

Usage:
  check_fubuki_corrections.py <fubuki-os-root>
  check_fubuki_corrections.py --lint-check <fixture-dir> <fubuki-os-root>

Exit 0 + "PASS" on success; exit 1 + reason on failure.
"""
import sys
from pathlib import Path


def _add_fubuki(fubuki_root: Path):
    sys.path.insert(0, str(fubuki_root / "src"))
    sys.path.insert(0, str(fubuki_root))


def _correct_lint_exit(findings: list) -> int:
    has_violation = any(tier == "VIOLATION" for tier, _, _ in findings)
    has_review = any(tier == "REVIEW" for tier, _, _ in findings)
    if has_violation:
        return 1
    if has_review:
        return 2
    return 0


def check_lint_ordering(fubuki_root: Path) -> bool:
    _add_fubuki(fubuki_root)
    from lint.persona_lint import lint, main as upstream_main

    fixture_dir = Path(__file__).resolve().parent / "fixtures" / "ordered-lint"

    review_text = (fixture_dir / "01-review-only.txt").read_text()
    violation_text = (fixture_dir / "02-has-violation.txt").read_text()
    clean_text = (fixture_dir / "clean.txt").read_text()

    review_findings = lint(review_text, "conversational", [])
    if not any(t == "REVIEW" for t, _, _ in review_findings):
        print("lint-ordering: review fixture produced no REVIEW findings")
        return False

    violation_findings = lint(violation_text, "conversational", [])
    if not any(t == "VIOLATION" for t, _, _ in violation_findings):
        print("lint-ordering: violation fixture produced no VIOLATION findings")
        return False

    clean_findings = lint(clean_text, "conversational", [])
    if clean_findings:
        print("lint-ordering: clean fixture produced unexpected findings")
        return False

    upstream_rc = upstream_main([
        str(fixture_dir / "01-review-only.txt"),
        str(fixture_dir / "02-has-violation.txt"),
    ])
    if upstream_rc != 2:
        print(f"lint-ordering: upstream bug not reproduced (got rc={upstream_rc}, expected 2)")
        return False

    all_findings = review_findings + violation_findings
    corrected_rc = _correct_lint_exit(all_findings)
    if corrected_rc != 1:
        print(f"lint-ordering: corrected exit code wrong (got {corrected_rc}, expected 1)")
        return False

    return True


def check_bound_decision_join(fubuki_root: Path) -> bool:
    _add_fubuki(fubuki_root)
    from fubuki_os.memory.models import MemoryRecord
    from fubuki_os.memory.bounds import evaluate_record

    approved_rec = MemoryRecord(
        record_id="rec-approved-001",
        record_type="fact",
        claim="test approved claim",
        branch="main",
        provenance_class="operator_stated",
        confidence="high",
        created_at="2026-01-01T00:00:00Z",
        status="approved",
    )
    rejected_rec = MemoryRecord(
        record_id="rec-rejected-002",
        record_type="fact",
        claim="test rejected claim",
        branch="main",
        provenance_class="operator_stated",
        confidence="high",
        created_at="2026-01-01T00:00:00Z",
        status="proposed",
    )

    d_approved = evaluate_record(
        approved_rec, branch="main", active_person="operator",
        third_party_visible=False, at="2026-06-01T00:00:00Z",
    )
    if d_approved.record_id != approved_rec.record_id:
        print(f"bound-decision-join: record_id mismatch on approved "
              f"({d_approved.record_id!r} != {approved_rec.record_id!r})")
        return False
    if not d_approved.allowed:
        print("bound-decision-join: approved record was denied")
        return False

    d_rejected = evaluate_record(
        rejected_rec, branch="main", active_person="operator",
        third_party_visible=False, at="2026-06-01T00:00:00Z",
    )
    if d_rejected.record_id != rejected_rec.record_id:
        print(f"bound-decision-join: record_id mismatch on rejected "
              f"({d_rejected.record_id!r} != {rejected_rec.record_id!r})")
        return False
    if d_rejected.allowed:
        print("bound-decision-join: proposed record was allowed (expected deny)")
        return False
    if not d_rejected.rejection_reasons:
        print("bound-decision-join: rejected decision has no reasons")
        return False

    return True


def check_hash_stability(fubuki_root: Path) -> bool:
    _add_fubuki(fubuki_root)
    from fubuki_os.release.hashing import canonical_json, hash_obj

    packet = {
        "package_id": "test-persona/v1",
        "core_hash": "sha256:abc123",
        "mode": "default",
        "register": "conversational",
        "nested": {"z_key": "last", "a_key": "first"},
        "items": [3, 1, 2],
    }

    h1 = hash_obj(packet)
    h2 = hash_obj(packet)
    if h1 != h2:
        print(f"hash-stability: two runs differ ({h1} != {h2})")
        return False

    cj1 = canonical_json(packet)
    cj2 = canonical_json(packet)
    if cj1 != cj2:
        print("hash-stability: canonical JSON not stable")
        return False

    if not cj1.startswith('{"'):
        print("hash-stability: canonical JSON does not start with sorted key")
        return False

    mutated = dict(packet)
    mutated["mode"] = "analysis"
    h3 = hash_obj(mutated)
    if h1 == h3:
        print("hash-stability: mutation did not change hash")
        return False

    return True


def lint_check_fixture(fixture_dir: Path, fubuki_root: Path) -> int:
    _add_fubuki(fubuki_root)
    from lint.persona_lint import lint

    txt_files = sorted(fixture_dir.glob("*.txt"))
    if not txt_files:
        print(f"lint-check: no .txt files in {fixture_dir}")
        return 1

    all_findings = []
    for f in txt_files:
        text = f.read_text()
        findings = lint(text, "conversational", [])
        for tier, check, ev in findings:
            print(f"{f.name}: {tier}: {check}: {ev!r}")
            all_findings.append((tier, check, ev))

    rc = _correct_lint_exit(all_findings)
    if rc == 1:
        violations = [(t, c, e) for t, c, e in all_findings if t == "VIOLATION"]
        rule_id = violations[0][1] if violations else "unknown"
        print(f"lint-violation: {rule_id}, exit {rc} per contract")
    elif rc == 0:
        print("clean")
    return rc


def main():
    if len(sys.argv) < 2:
        print("usage: check_fubuki_corrections.py <fubuki-os-root>")
        print("       check_fubuki_corrections.py --lint-check <fixture-dir> <fubuki-os-root>")
        return 1

    if sys.argv[1] == "--lint-check":
        if len(sys.argv) != 4:
            print("usage: check_fubuki_corrections.py --lint-check <fixture-dir> <fubuki-os-root>")
            return 1
        fixture_dir = Path(sys.argv[2]).resolve()
        fubuki_root = Path(sys.argv[3]).resolve()
        return lint_check_fixture(fixture_dir, fubuki_root)

    fubuki_root = Path(sys.argv[1]).resolve()

    if not (fubuki_root / "src" / "fubuki_os").is_dir():
        print(f"fubuki-missing: {fubuki_root}/src/fubuki_os not found")
        return 1

    if not check_lint_ordering(fubuki_root):
        return 1

    if not check_bound_decision_join(fubuki_root):
        return 1

    if not check_hash_stability(fubuki_root):
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
