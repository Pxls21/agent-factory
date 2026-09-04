#!/usr/bin/env python3
"""Structured review-status guard (AF-AP-32).

A proof the owner reopened for review is REVIEW-PENDING until the OWNER accepts
it; the coordinator never records its own closure. This parses the CANONICAL,
machine-readable per-proof status markers in `todo/BUILD-TASKLIST.md`:

    <!-- PROOF-STATUS S0-11 REVIEW-PENDING -->

and enforces, as a STATE check (not a vocabulary blacklist):

  * exactly one marker per proof id (a conflicting duplicate row fails);
  * the status is REVIEW-PENDING or ACCEPTED — any other word (DONE, CLOSED,
    re-closed, …) fails, so a coordinator-authored closure cannot pass;
  * ACCEPTED requires a committed owner-acceptance record
    `proofs/<id>/OWNER-ACCEPTED` — the owner adds it; the coordinator only ever
    sets REVIEW-PENDING;
  * every proof under active owner review (REQUIRED_REVIEW) has a marker, so
    deleting the REVIEW-PENDING marker also fails.

Exit 0 when the status state is clean; exit 1 (with reasons on stderr) otherwise.
"""
import re
import sys
from pathlib import Path

MARKER = re.compile(r"<!--\s*PROOF-STATUS\s+(S0-[0-9]{2})\s+([A-Za-z-]+)\s*-->")
VALID_STATUS = {"REVIEW-PENDING", "ACCEPTED"}
# Proofs under active owner review that MUST carry a status marker. A reopened
# proof stays here until the owner records acceptance and closes the review.
REQUIRED_REVIEW = {"S0-11"}


def check(repo_root):
    repo_root = Path(repo_root)
    tasklist = repo_root / "todo" / "BUILD-TASKLIST.md"
    errors = []
    try:
        markers = MARKER.findall(tasklist.read_text())
    except OSError as error:
        return [f"cannot read {tasklist}: {error}"]

    seen = {}
    for proof_id, status in markers:
        if proof_id in seen:
            errors.append(
                f"{proof_id}: conflicting PROOF-STATUS markers "
                f"({seen[proof_id]} and {status}) — exactly one canonical row per proof"
            )
        seen[proof_id] = status
        if status not in VALID_STATUS:
            errors.append(
                f"{proof_id}: PROOF-STATUS is {status}; only REVIEW-PENDING or ACCEPTED are "
                f"valid — the coordinator never self-records closure (AF-AP-32)"
            )
        elif status == "ACCEPTED":
            record = repo_root / "proofs" / proof_id / "OWNER-ACCEPTED"
            if not record.exists():
                errors.append(
                    f"{proof_id}: marked ACCEPTED but no owner-acceptance record "
                    f"proofs/{proof_id}/OWNER-ACCEPTED exists — only the owner records acceptance"
                )

    for proof_id in sorted(REQUIRED_REVIEW):
        if proof_id not in seen:
            errors.append(
                f"{proof_id}: no PROOF-STATUS marker — a proof under owner review must be "
                f"REVIEW-PENDING until the owner accepts it"
            )
    return errors


def main(argv):
    repo_root = argv[1] if len(argv) > 1 else "."
    errors = check(repo_root)
    for error in errors:
        print(f"proof-status: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
