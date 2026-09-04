#!/usr/bin/env python3
"""Consistency guard for the visible proof-review status (AF-AP-32).

This is a CONSISTENCY check, not an acceptance authenticator. It verifies that
the one authoritative, VISIBLE status line for each tracked proof —
`PROOF-STATUS: <id> = <status>` in todo/BUILD-TASKLIST.md — agrees with the one
canonical task row for that proof, and it rejects the ledger-divergence attacks
the owner reproduced over cycles 6-8:

  * a HIDDEN HTML-comment PROOF-STATUS marker that silently diverges from the
    visible ledger a human reads;
  * a task row keyed by a BARE proof id (`| S0-11 | ... |`) asserting a status;
  * a CANONICAL slug row whose status cell CONTRADICTS the PROOF-STATUS line
    (the cycle-8 bypass: a `| s0-18-s0-11-eval-hardening | ... | DONE |` row
    slipped through because the guard only rejected bare-id rows, never the
    slug-keyed row's own status cell);
  * a DUPLICATE or MISSING canonical row for a tracked proof.

The proof -> canonical-slug map is EXACT, never a substring: the S0-10 task row
is keyed `s0-11-s0-10-gbrain-adr`, whose text contains "s0-11" but is NOT the
S0-11 row — a substring match would bind the wrong row's status.

What this guard does NOT do — and does not claim to do — is AUTHENTICATE
acceptance. While the implementation agent pushes under the repo owner's own
GitHub identity, no in-repo signal can be structurally owner-only: any status
the coordinator can write, it can forge. So `ACCEPTED` here records an explicit
HUMAN PROCESS DECISION (the owner's review), NOT a machine-enforced guarantee.
Making acceptance owner-verifiable needs IDENTITY SEPARATION (a dedicated bot
identity + protected `main` + the owner's native GitHub review on the head SHA);
that is tracked as the separate AF-AP-32 governance task, not built here. This
guard's job is only to keep the visible status surfaces from contradicting each
other.

Exit 0 when the visible status is internally consistent; exit 1 (with reasons on
stderr) otherwise.
"""
import re
import sys
from pathlib import Path

# proof id -> its ONE canonical task-row slug. EXACT, never a substring match
# (`s0-11-s0-10-gbrain-adr` is the S0-10 row; a substring would misbind it).
TRACKED = {"S0-11": "s0-18-s0-11-eval-hardening"}
# The ledger's status vocabulary. ACCEPTED records an owner process decision
# (see the module docstring); DONE/CLOSED/other are not the governance words and
# must not appear as an authoritative status.
KNOWN_STATUSES = {"REVIEW-PENDING", "ACCEPTED"}

VISIBLE_MARKER = re.compile(r"^PROOF-STATUS:\s+(S0-[0-9]{2})\s*=\s*([A-Za-z-]+)\s*$", re.MULTILINE)
HIDDEN_MARKER = re.compile(r"<!--\s*PROOF-STATUS\b")
BARE_PROOF_ID = re.compile(r"^S0-[0-9]{2}$")
# Column index of the status cell in the task table
# (header: slug | increment | status | blocked-by | gate).
STATUS_COLUMN = 2
# Leading status token of a status cell, ignoring an optional **bold** wrapper:
# "**ACCEPTED** (owner...)" -> ACCEPTED, "DONE 2026-09-04 — ..." -> DONE.
LEADING_STATUS = re.compile(r"^\**\s*([A-Za-z][A-Za-z-]*)")


def _row_cells(line):
    r"""Cells of a Markdown table row, split on UNESCAPED pipes (`\|` is literal).

    Returns None for a non-row line. Border empties are dropped so cells[0] is
    the first content cell.
    """
    if "|" not in line:
        return None
    parts = re.split(r"(?<!\\)\|", line.rstrip("\n"))
    cells = [cell.strip() for cell in parts]
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return cells or None


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

    # The one authoritative visible status per proof.
    status_of = {}
    for proof_id, status in VISIBLE_MARKER.findall(text):
        if proof_id in status_of:
            errors.append(
                f"{proof_id}: more than one PROOF-STATUS line ({status_of[proof_id]} and "
                f"{status}) — exactly one authoritative status per proof"
            )
        status_of[proof_id] = status
        if status not in KNOWN_STATUSES:
            errors.append(
                f"{proof_id}: PROOF-STATUS is {status}; the ledger vocabulary is "
                f"{sorted(KNOWN_STATUSES)} (ACCEPTED records an explicit owner process "
                f"decision — never a DONE/CLOSED self-closure) (AF-AP-32)"
            )

    # One scan of the task rows: reject bare-id rows, collect canonical-slug rows.
    slug_to_proof = {slug.lower(): proof_id for proof_id, slug in TRACKED.items()}
    canonical_rows = {proof_id: [] for proof_id in TRACKED}
    for line in text.splitlines():
        cells = _row_cells(line)
        if not cells:
            continue
        first = cells[0]
        if BARE_PROOF_ID.match(first):
            errors.append(
                f"a task row is keyed by the bare proof id {first!r}: a visible row must not "
                f"assert a status; the authoritative status is the single PROOF-STATUS line "
                f"bound to the one canonical slug row (AF-AP-32)"
            )
        proof_id = slug_to_proof.get(first.lower())
        if proof_id is not None:
            canonical_rows[proof_id].append(cells)

    # Every tracked proof: a status line, exactly one canonical row, and that
    # row's status cell bound to the authoritative value.
    for proof_id in sorted(TRACKED):
        slug = TRACKED[proof_id]
        rows = canonical_rows[proof_id]
        if proof_id not in status_of:
            errors.append(
                f"{proof_id}: no PROOF-STATUS line — a tracked proof must carry a single "
                f"visible authoritative status"
            )
        if len(rows) != 1:
            errors.append(
                f"{proof_id}: found {len(rows)} task rows keyed {slug!r}, expected exactly one "
                f"— the status is bound to a SINGLE canonical row (AF-AP-32)"
            )
            continue
        if proof_id not in status_of:
            continue
        want = status_of[proof_id]
        cells = rows[0]
        if len(cells) <= STATUS_COLUMN:
            errors.append(f"{proof_id}: canonical row {slug!r} has no status column")
            continue
        match = LEADING_STATUS.match(cells[STATUS_COLUMN])
        got = match.group(1) if match else None
        if got != want:
            errors.append(
                f"{proof_id}: canonical row {slug!r} status cell leads with {got!r}, but the "
                f"authoritative PROOF-STATUS is {want!r} — the visible row must not contradict "
                f"the status line (AF-AP-32)"
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
