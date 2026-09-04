#!/usr/bin/env python3
"""Structured review-status guard (AF-AP-32).

A proof the owner reopened for review is REVIEW-PENDING until the OWNER accepts
it. The coordinator can record ONLY REVIEW-PENDING; it has no in-repo path to
ACCEPTED, because any acceptance file the coordinator can write, it can forge
(file existence is not authentication). Genuine acceptance is an OWNER action on
owner-controlled infrastructure (a merge to `main`, or a protected GitHub
review) that the coordinator structurally cannot produce; wiring an in-repo
ACCEPTED status to such an anchor is an owner decision, pending here.

This enforces, as a STATE check over a SINGLE, VISIBLE source of truth:

  * the authoritative status is a VISIBLE line `PROOF-STATUS: <id> = <status>`
    in todo/BUILD-TASKLIST.md — NOT a hidden HTML comment (a hidden marker can
    silently diverge from the visible task ledger a human reads);
  * exactly one status line per proof (a duplicate/conflicting line fails);
  * the only status the coordinator may record is REVIEW-PENDING — DONE, CLOSED,
    ACCEPTED or any other word fails (the coordinator never self-accepts);
  * no Markdown TASK ROW may be keyed by a bare proof id (`| S0-11 | … |`) — that
    is the shape of a visible row asserting a status that contradicts the
    authoritative line; real task rows are keyed by descriptive slugs;
  * every proof under active review (REQUIRED_REVIEW) has a status line.

Exit 0 when the status state is clean; exit 1 (with reasons on stderr) otherwise.
"""
import re
import sys
from pathlib import Path

VISIBLE_MARKER = re.compile(r"^PROOF-STATUS:\s+(S0-[0-9]{2})\s*=\s*([A-Za-z-]+)\s*$", re.MULTILINE)
HIDDEN_MARKER = re.compile(r"<!--\s*PROOF-STATUS\b")
TABLE_ROW_FIRST_CELL = re.compile(r"^\s*\|\s*([^|]+?)\s*\|")
BARE_PROOF_ID = re.compile(r"^S0-[0-9]{2}$")
# The coordinator may record ONLY this. ACCEPTED is not a coordinator-writable
# status: it requires an owner-verifiable anchor the coordinator cannot forge.
COORDINATOR_STATUS = "REVIEW-PENDING"
# Proofs under active owner review that MUST carry a status line.
REQUIRED_REVIEW = {"S0-11"}


def check(repo_root):
    repo_root = Path(repo_root)
    tasklist = repo_root / "todo" / "BUILD-TASKLIST.md"
    try:
        text = tasklist.read_text()
    except OSError as error:
        return [f"cannot read {tasklist}: {error}"]

    errors = []

    if HIDDEN_MARKER.search(text):
        errors.append(
            "a hidden HTML-comment PROOF-STATUS marker is present; the authoritative status "
            "must be a VISIBLE `PROOF-STATUS: <id> = <status>` line so it cannot diverge from "
            "the task ledger a human reads (AF-AP-32)"
        )

    # A task row keyed by a bare proof id is the contradictory-visible-row attack:
    # a real task row is keyed by a descriptive slug, never a bare S0-NN.
    for line in text.splitlines():
        match = TABLE_ROW_FIRST_CELL.match(line)
        if match and BARE_PROOF_ID.match(match.group(1).strip()):
            errors.append(
                f"a task row is keyed by the bare proof id {match.group(1).strip()!r}: a visible "
                f"row must not assert a status; the authoritative status is the single "
                f"PROOF-STATUS line (AF-AP-32)"
            )

    seen = {}
    for proof_id, status in VISIBLE_MARKER.findall(text):
        if proof_id in seen:
            errors.append(
                f"{proof_id}: more than one PROOF-STATUS line ({seen[proof_id]} and {status}) — "
                f"exactly one authoritative status per proof"
            )
        seen[proof_id] = status
        if status != COORDINATOR_STATUS:
            errors.append(
                f"{proof_id}: PROOF-STATUS is {status}; the coordinator records ONLY "
                f"{COORDINATOR_STATUS}. Acceptance is an owner action on owner-controlled "
                f"infrastructure (a merge to main, or a protected review), never a "
                f"coordinator-written status or file (AF-AP-32)"
            )

    for proof_id in sorted(REQUIRED_REVIEW):
        if proof_id not in seen:
            errors.append(
                f"{proof_id}: no PROOF-STATUS line — a proof under owner review must be "
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
