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
import hashlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# proof id -> its ONE canonical task-row slug. EXACT, never a substring match
# (`s0-11-s0-10-gbrain-adr` is the S0-10 row; a substring would misbind it).
TRACKED = {
    "S0-11": "s0-18-s0-11-eval-hardening",
    # S0-01 proof run recorded 2026-09-05 (pc-bridge venue); REVIEW-PENDING until the owner accepts.
    "S0-01": "s0-07-s0-01-acp-conformance",
    # S0-07 minted 2026-09-07 23:46Z by the real runner (sandbox venue); REVIEW-PENDING until the owner accepts.
    "S0-07": "s0-09-s0-07-fubuki",
}
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

# The owner-verifiable ACCEPTED anchor (owner decision 2026-09-08, task #30 option a). A proof whose
# PROOF-STATUS is ACCEPTED must carry a SIGNED annotated tag `accepted/<proof-id>` whose signature
# verifies against the owner's public key committed at OWNER_KEY_REL (an isolated keyring built from
# that one file at check time — never the host keyring), whose commit is in this branch's history and
# holds a `proofs/<id>/result.json` byte-identical to the current one: an attested-input regeneration
# makes a NEW artifact, and a new artifact must be re-accepted (AF-AP-56). Until the owner signs, the
# ledger carries a VISIBLE `PROOF-ANCHOR: <id> = PENDING-OWNER-TAG …` declaration: reported as a
# WARNING, never counted as owner-verifiable. A tag AND a pending declaration together are a stale
# ledger and an error. The coordinator can write the declaration; it cannot write the signature.
OWNER_KEY_REL = Path("docs") / "governance" / "owner-signing-key.asc"
# The signed tag OBJECT also travels inside the branch as a committed file (this sandbox's git proxy refuses
# tag pushes with HTTP 403 and CI clones without tags): `git cat-file tag accepted/<id>` bytes, content-addressed —
# importing the file with `git hash-object -w -t tag` reproduces the very object the owner signed, so the signature
# verifies wherever the branch lands. When both the ref and the file exist they must be the same object.
TAG_FILE_REL = "docs/governance/tags/accepted-{proof_id}.tag"
ANCHOR_TAG = "accepted/{proof_id}"
PENDING_ANCHOR = re.compile(r"^PROOF-ANCHOR:\s+(S0-[0-9]{2})\s*=\s*PENDING-OWNER-TAG\b.*$", re.MULTILINE)


def _git(repo_root, *args, env=None, binary=False):
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True, text=not binary, timeout=30, env=env, check=False,
    )


def _anchor_findings(repo_root, proof_id, pending):
    """(errors, warnings) for one ACCEPTED proof's anchor tag."""
    errors, warnings = [], []
    tag = ANCHOR_TAG.format(proof_id=proof_id)
    if _git(repo_root, "rev-parse", "--git-dir").returncode != 0:
        return [f"{proof_id}: ACCEPTED but {repo_root} is not a git repository — the anchor tag {tag} "
                f"cannot be verified (AF-AP-32)"], []
    tag_file = Path(repo_root) / TAG_FILE_REL.format(proof_id=proof_id)
    ref_exists = _git(repo_root, "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}").returncode == 0
    if ref_exists and tag_file.is_file():
        ref_bytes = _git(repo_root, "cat-file", "tag", tag, binary=True).stdout
        if ref_bytes != tag_file.read_bytes():
            errors.append(f"{proof_id}: the committed tag object {TAG_FILE_REL.format(proof_id=proof_id)} is not the "
                          f"object the ref {tag} names — the two must be one signed object")
            return errors, warnings
    if not ref_exists and tag_file.is_file():
        imported = _git(repo_root, "hash-object", "-w", "-t", "tag", str(tag_file))
        if imported.returncode != 0:
            errors.append(f"{proof_id}: the committed tag object {TAG_FILE_REL.format(proof_id=proof_id)} is not a git "
                          f"tag object: {' '.join(imported.stderr.split())[:160]}")
            return errors, warnings
        tag = imported.stdout.strip()  # verify the imported object itself; the ref name is not needed
        ref_exists = True
    if not ref_exists:
        if pending:
            warnings.append(f"{proof_id}: ACCEPTED with the anchor PENDING the owner's signed tag {tag} "
                            f"(declared in the ledger) — not owner-verifiable yet")
            return errors, warnings
        errors.append(f"{proof_id}: ACCEPTED but no signed tag {tag} and no visible "
                      f"`PROOF-ANCHOR: {proof_id} = PENDING-OWNER-TAG` declaration — an acceptance the owner "
                      f"cannot verify (AF-AP-32)")
        return errors, warnings
    if pending:
        errors.append(f"{proof_id}: the tag {tag} exists but the ledger still declares PROOF-ANCHOR "
                      f"PENDING — a stale declaration (remove it)")
    if _git(repo_root, "cat-file", "-t", tag).stdout.strip() != "tag":
        errors.append(f"{proof_id}: {tag} is a lightweight tag — the anchor must be a SIGNED annotated tag "
                      f"(`git tag -s`)")
        return errors, warnings
    key = Path(repo_root) / OWNER_KEY_REL
    if not key.is_file():
        errors.append(f"{proof_id}: the owner's public key is not committed at {OWNER_KEY_REL} — {tag} "
                      f"cannot be verified")
        return errors, warnings
    with tempfile.TemporaryDirectory() as home:
        os.chmod(home, 0o700)
        env = dict(os.environ, GNUPGHOME=home)
        imported = subprocess.run(["gpg", "--batch", "--quiet", "--import", str(key)],
                                  capture_output=True, text=True, timeout=30, env=env, check=False)
        if imported.returncode != 0:
            errors.append(f"{proof_id}: the committed owner key {OWNER_KEY_REL} does not import: "
                          f"{imported.stderr.strip()[:200]}")
            return errors, warnings
        # gpg.format is forced: a host configured for SSH signing (this sandbox is) would otherwise look for
        # an allowed-signers file instead of the OpenPGP keyring built above.
        verified = _git(repo_root, "-c", "gpg.format=openpgp", "-c", "gpg.program=gpg", "verify-tag", tag, env=env)
    if verified.returncode != 0:
        reason = " ".join(verified.stderr.split())[:200]
        errors.append(f"{proof_id}: the signature on {tag} does not verify against the committed owner key "
                      f"{OWNER_KEY_REL} (AF-AP-32): {reason}")
        return errors, warnings
    commit = _git(repo_root, "rev-parse", f"{tag}^{{commit}}").stdout.strip()
    if _git(repo_root, "merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:
        errors.append(f"{proof_id}: {tag} points at {commit[:12]}, which is not in this branch's history")
        return errors, warnings
    rel = f"proofs/{proof_id}/result.json"
    tagged = _git(repo_root, "cat-file", "-p", f"{commit}:{rel}", binary=True)
    if tagged.returncode != 0:
        errors.append(f"{proof_id}: {tag}'s commit {commit[:12]} holds no {rel} — the acceptance must point "
                      f"at the minted result")
        return errors, warnings
    current = Path(repo_root) / rel
    if not current.is_file():
        errors.append(f"{proof_id}: {rel} is absent from the working tree while {tag} accepts one")
        return errors, warnings
    if hashlib.sha256(tagged.stdout).hexdigest() != hashlib.sha256(current.read_bytes()).hexdigest():
        errors.append(f"{proof_id}: the minted {rel} changed since {tag} (regenerated after acceptance) — "
                      f"re-accept with a new signed tag (AF-AP-56)")
    return errors, warnings


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


def check(repo_root, anchors=True, warnings=None):
    repo_root = Path(repo_root)
    if warnings is None:
        warnings = []
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

    # The owner-verifiable anchor of every ACCEPTED proof (see OWNER_KEY_REL above).
    pending_of = set(PENDING_ANCHOR.findall(text))
    for proof_id in sorted(pending_of):
        if status_of.get(proof_id) != "ACCEPTED":
            errors.append(
                f"{proof_id}: a PROOF-ANCHOR PENDING declaration for a proof whose PROOF-STATUS is "
                f"{status_of.get(proof_id)!r}, not ACCEPTED — remove it"
            )
    if anchors:
        for proof_id, status in sorted(status_of.items()):
            if status != "ACCEPTED":
                continue
            found, warned = _anchor_findings(repo_root, proof_id, proof_id in pending_of)
            errors.extend(found)
            warnings.extend(warned)
    return errors


def main(argv):
    flags = {argument for argument in argv[1:] if argument.startswith("--")}
    positional = [argument for argument in argv[1:] if not argument.startswith("--")]
    unknown = sorted(flags - {"--no-anchors"})
    if unknown:
        print(f"proof-status: unknown option(s) {unknown}; the one option is --no-anchors", file=sys.stderr)
        return 2
    repo_root = positional[0] if positional else "."
    warnings = []
    errors = check(repo_root, anchors="--no-anchors" not in flags, warnings=warnings)
    if "--no-anchors" in flags:
        print("proof-status: ACCEPTED anchor verification SKIPPED (--no-anchors) — the status logic "
              "alone is checked; this is never the CI or coordinator invocation", file=sys.stderr)
    for warning in warnings:
        print(f"proof-status: WARNING {warning}", file=sys.stderr)
    for error in errors:
        print(f"proof-status: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
