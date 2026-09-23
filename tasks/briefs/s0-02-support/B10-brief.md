# B10 — the S0-02 fixture signers follow D-037 and D-038 before the live capture (task #190)

PIN: 688b4bd (origin head at authoring; every file in the boundary is byte-identical to the B9-R1 landing 56a8f50, measured in the premise block).
LANE: s0-02-b10 (sandbox; agent `code-implementer`, in the SHARED tree, no worktree isolation). Venue: the PC's local route holds its two
long-context lanes (AF-AP-146), and this work needs no relay, no bridge and no host secret. Honey `ultra` Lever-2: your report is DATA:
files:lines, pasted counts, discrepancies, NOT-done. Do NOT spawn subagents.

WHY: the live eight-leg capture is next, and two committed fixtures still carry the signers from before D-037 and D-038.
`revoked.json` signs as `owner` (the identity buzz-acp answers to, `expected_pubkey` 2267fe91…). D-037 says the revoked leg removes a
SECOND fixture owner, `owner2`, so the removal never touches the owner every other leg uses and never removes the last owner. With the
fixture as it stands, the owner removes `owner2`, the runner still signs the revoked delivery as `owner` (a member), and the checker
refuses the leg (`membership.json removed_pubkey does not match the delivered sender`, `proofs/S0-02/check_buzz_authz.py:550-552`).
`neg-unauthorized.json` has `expected_pubkey: null`; D-038 fixed the non-member to ONE host-local identity whose absence from the channel
was measured, so the leg should bind to it. Both moves were written down as B9 inputs (`proofs/S0-02/fixtures/PROVENANCE.md:57-64`) and
never reached a brief. The builder's docstring still describes the retired per-leg non-member key (`build_fixtures.py:20-25`).

CONTRACT SOURCES (read them whole before you design): `proofs/S0-02/fixtures/PROVENANCE.md` §Host-local fixture identities (D-037,
D-038 and their measured public keys) · `docs/08_DECISION_LOG.md` D-037 and D-038 · `proofs/S0-02/tools/build_fixtures.py` (the builder)
· `proofs/S0-02/check_buzz_authz.py:225-258` (the signer binding: an exact `expected_pubkey`, else the F21 "not a known S0-01 identity"
branch) and `:545-560` (the revoked leg's receipt binding) · issue #45 VF-1 ("no test compares the committed bundles with a fresh build,
so M18/M19 survive").

BOUNDARY (exact): MODIFY `proofs/S0-02/tools/build_fixtures.py` (B), `tests/test_s0_02_buzz_authz.py` (T2),
`proofs/S0-02/fixtures/PROVENANCE.md` (the two plan sentences at :57-59 and :63-64 become records of what landed); the committed files
`build_fixtures.py` regenerates (the eight fixtures under `proofs/S0-02/fixtures/*.json` and the two synthetic bundles
`proofs/S0-02/fixtures/evidence-pass/` and `proofs/S0-02/fixtures/evidence-blanket/`): regenerate them by RUNNING the builder
(`--write`, then `--bundles`), never by hand. CREATE `proofs/S0-02/fixtures/identities-s0-02.json` (content below, copy it, do not
redesign) and `tasks/briefs/s0-02-support/B10-report.md` (write it incrementally from the start).
READ-ONLY: `proofs/S0-02/check_buzz_authz.py`, `proofs/S0-02/oracle/`, `proofs/S0-02/tools/pc/` (the runner signs with
`$SEC/<signer.role>.env` through `role_for`, so it follows the fixture with no edit), `proofs/S0-02/spec.json`, `proofs/S0-01/**` (S0-01 is
ACCEPTED and its files are attested: adding keys to `proofs/S0-01/fixtures/identities.json` would re-mint S0-01 and void the owner's
signed tag, which is why the two new public keys get their own S0-02 file), `scripts/`, `.github/`, `.claude/`. A line you cannot meet
without another file is a DISCREPANCY, never a silent edit.

Three other sandbox agents work in this tree on disjoint files (`scripts/no_laya_in_gates.py`, `tests/test_no_laya_in_gates.py`,
`tasks/briefs/laya/`, `tasks/briefs/s0-05-support/`, `/tmp/j10r5`, `/tmp/vj11r1`, `/tmp/ve3r1`): never touch, run or revert them.
Never run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push`. No outward-facing action; no PC or
bridge use; no live relay or host secret. DISK: the sandbox has about 1.7 GB free. Every pytest `--basetemp` and every mutant copy lives
under `/tmp/b10/` and is removed after use; copy only the files a mutant run needs (a full tree copy is 191 MB).

CODE INTEL FIRST: `graft ask` before any grep for code questions; `scripts/lane_context.sh -q 'how are the S0-02 fixture signers built
and checked' -s _identities -s _bundle_identities -s build_one -s build_bundle -o /tmp/b10/pack.md proofs/S0-02/tools/build_fixtures.py
proofs/S0-02/check_buzz_authz.py tests/test_s0_02_buzz_authz.py`.

## The contract (build to it; the HOW is yours)

1. **Premise first.** Re-measure the premise block on the tree. On a mismatch in the boundary, stop CONTRACT-INVALID and report what
   differs.
2. **The S0-02 identity file.** CREATE `proofs/S0-02/fixtures/identities-s0-02.json` with exactly this content (two-space indent,
   sorted keys, a trailing newline; the public halves only, as measured on the PC):
   ```json
   {
     "nonmember": "f5aa4962136f829d80cd01966d437eba54d8f1ca97b7d2073d3c5560367dd816",
     "owner2": "82f440d16985a59efd88ffcbbf186fe27ecde5db2a39773f50c354a08e8cd2b2"
   }
   ```
3. **The builder reads both identity files.** `_identities()` returns the S0-01 identities merged with the S0-02 file. It refuses, with
   a message naming the key, (a) a key present in both files and (b) an S0-02 value that is not 64 lowercase hex. It never writes either
   file.
4. **The revoked leg signs as `owner2`.** The `revoked` spec's role becomes `owner2`, so its fixture carries `signer.role = owner2` and
   `expected_pubkey = 82f440d1…`. No other leg's signer changes (the premise table lists all eight).
5. **The unauthorized leg binds to `nonmember`.** With item 3 in place, `neg-unauthorized.json` carries `expected_pubkey = f5aa4962…`.
6. **The synthetic bundles follow.** `_bundle_identities` gives `owner2` and `nonmember` their own synthetic keys, as it does for the
   four S0-01 roles, so the pass bundle's revoked and unauthorized legs are signed by the bundle's own keys and the pass bundle still
   grades rc 0 through the real checker. Regenerate both bundles with `--bundles`.
7. **Comments that the change falsifies are fixed in the same change**: the builder docstring at `:18-25` (the per-leg non-member key is
   retired; name both identity files) and the two PROVENANCE plan sentences (now records, dated, naming B10).
8. **Tests (T2).** Normal, failure and boundary behavior:
   - the revoked fixture names `owner2`: role, `expected_pubkey` equal to the S0-02 file's value, and not equal to the S0-01 `owner`;
   - the unauthorized fixture binds to the S0-02 `nonmember` value, which is none of the S0-01 identities and not `owner2`;
   - the merge refusals of item 3, each with its exact message (a collision, a malformed value), through the real `_identities()` with
     the two paths pointed at temporary files;
   - VF-1: a fresh `build_bundle` of both bundles into a temporary directory equals the committed bundle bytes, file for file;
   - the existing tests that encode the old signers follow the new contract. `test_unauthorized_specimen_is_not_a_known_identity`
     (`:242`) and `test_a_nonmember_leg_signed_by_a_known_identity_fails` (`:1425`) encode `expected_pubkey: null`. The F21 branch
     (`check_buzz_authz.py:248-253`) stays in the checker. After this change no committed fixture reaches it, so keep it covered: one
     test sets the synthetic bundle's `neg-unauthorized` `expected_pubkey` to null in BOTH copies (the leg's `fixture.json` and the
     bundle's `fixtures/neg-unauthorized.json`), forges a delivery signed by a known identity and expects the F21 message. List every
     changed assertion in the report with the reason.

## Mutants (run each on a scratch copy under `/tmp/b10/`; a mutant must compile and collect, AF-AP-78)

m1 the revoked role back to `owner` · m2 `_bundle_identities` without `owner2` · m3 the collision refusal removed · m4 the S0-02 file
left out of the merge. For each: the named T2 test that reds and its failure line, pasted. A mutant no test kills is a finding in your
report, never a silent pass.

## Gates (paste every command with its output)

- `python3 proofs/S0-02/tools/build_fixtures.py --check` → `fixture-drift: none (8 fixtures match a fresh build)`, rc 0.
- The pass bundle through the real checker: `python3 proofs/S0-02/check_buzz_authz.py --synthetic-root
  proofs/S0-02/fixtures/evidence-pass proofs/S0-02/fixtures/evidence-pass/legs` → rc 0.
- The spec's negative leg, verbatim from `proofs/S0-02/spec.json` → rc 1 with its exact `failure_reason`.
- T2 twice, counts identical: `python3 -m pytest tests/test_s0_02_buzz_authz.py -q -p no:cacheprovider --basetemp /tmp/b10/bt`
  (`mkdir -p /tmp/b10` first). The baseline at the PIN is `182 passed, 24 skipped` (set a5de0beef100); the new tests add to it and no
  existing test is skipped or deleted.
- `python3 scripts/lint_delta.py` (pyflakes delta: 0 new hits) and `python3 scripts/validate-ledger integrity --root .` (S0-02 ABSENT,
  rc 0: nothing minted changes).
- `git status --short` shows only boundary paths (and the other lanes' files, which you name and do not touch).

## Report (`tasks/briefs/s0-02-support/B10-report.md`)

The premise re-measurement; every changed file with its line ranges; the regenerated-file list (`git status --short proofs/S0-02/`); the
changed assertions and why; the mutant table; every gate pasted; DISCREPANCIES; NOT-done. State plainly what this does NOT prove: no live
leg ran, and the owner's removal of `owner2` (D-037) is still ahead.

NOT IN SCOPE (report, do not build): re-adding `owner2` at fixture setup for a REPEAT capture (a relay membership write; the coordinator
runs the idempotent add command in PROVENANCE by hand when a prior capture removed it); any checker or runner change; issue #45's other
rows.

## PREMISE — MEASURED at authoring (2026-09-23 13:15Z, sandbox @ 688b4bd; the PC probe 13:1xZ)

```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short HEAD
2026-09-23T13:15Z
688b4bd

$ git log -1 --format="%h %s" -- proofs/S0-02/ tests/test_s0_02_buzz_authz.py
56a8f50 B9-R1 landed (task #168): the S0-02 replay leg is graded by the relay's duplicate: receipt and ONE continuous buzz-acp process (D-036), and a 

$ git hash-object (each file)
2d74933a169ddc60ae9384fdb5702a12b2b14c3f  proofs/S0-02/tools/build_fixtures.py
7b875de37dce43047e39411a6c9ba75194a23be3  proofs/S0-02/check_buzz_authz.py
044b32b5880b3c62e4d1b1de1c6bda4afc444f83  tests/test_s0_02_buzz_authz.py
81ef691a387cf59ac827ef0a7463969666d97452  proofs/S0-02/fixtures/PROVENANCE.md
090e5154a706a46c20b20064a20252c9f9f4a8bf  proofs/S0-02/fixtures/revoked.json
125b81ebe032de441aeca89f1b8d9806609a1b0a  proofs/S0-02/fixtures/neg-unauthorized.json

$ grep -n "^IDENTITIES\|^def _identities\|return json.loads(IDENTITIES\|^def _bundle_identities\|for role in (" proofs/S0-02/tools/build_fixtures.py
47:IDENTITIES = ROOT / "proofs" / "S0-01" / "fixtures" / "identities.json"
88:def _identities() -> dict:
89:    return json.loads(IDENTITIES.read_text())
287:def _bundle_identities(bundle: str) -> dict:
290:    for role in ("owner", "agent", "relay", "user2"):

$ sed -n "164,172p" proofs/S0-02/tools/build_fixtures.py   # the revoked spec
    {
        "name": "revoked",
        "role": "owner",
        "created_at_offset_s": 0,
        "content": "S0-02 revoked: reply with exactly the single word: pong",
        "turns": 0,
        "failure_reason": "denied: membership-revoked",
        "requires_membership_removal": True,
    },

$ sed -n "18,26p" proofs/S0-02/tools/build_fixtures.py   # the docstring the change falsifies
the committed seed below.  It is NOT any of the four S0-01 identities and is
NOT a credential: the repository holds no private key for owner, agent, relay
or user2 (``proofs/S0-01/fixtures/identities.json`` is pubkey-only), and the
non-member key used against the LIVE relay is generated on the PC at leg time
with its private half never leaving that host.  ``signer.role`` names the key
the PC runner signs the delivered instance with; ``signer.expected_pubkey`` is
the real pubkey that instance must carry (from identities.json), or null for
the non-member role, whose pubkey is recorded in the leg instead.

$ python3 -c (print the signer role/expected_pubkey of every committed fixture)
neg-bad-signature.json owner 2267fe91571e5c9166ddf1a80176e988bdd00b9023edcc33375e1be85928000c
neg-not-allowlisted.json user2 fec645734c4bdd1a6867ab061b0a7aca7f8128d98ace364707814043b090ea22
neg-replayed.json owner 2267fe91571e5c9166ddf1a80176e988bdd00b9023edcc33375e1be85928000c
neg-self-authored.json agent ff4d48deaa326bcae60687e64cca48dd7f70099933fbda0ae40d2561485f4ce1
neg-stale.json owner 2267fe91571e5c9166ddf1a80176e988bdd00b9023edcc33375e1be85928000c
neg-unauthorized.json nonmember None
pos-allowed.json owner 2267fe91571e5c9166ddf1a80176e988bdd00b9023edcc33375e1be85928000c
revoked.json owner 2267fe91571e5c9166ddf1a80176e988bdd00b9023edcc33375e1be85928000c

$ python3 proofs/S0-02/tools/build_fixtures.py --check
fixture-drift: none (8 fixtures match a fresh build)
rc=0

$ (a tree copy of HEAD) python3 proofs/S0-02/tools/build_fixtures.py --bundles; diff -r <committed> <fresh>, per bundle
pass bundle: fresh build byte-identical
blanket bundle: fresh build byte-identical

$ grep -n "expected_pubkey\|IDENTITY_ROLES = \|must not be one of the known\|removed_pubkey" proofs/S0-02/check_buzz_authz.py
61:IDENTITY_ROLES = ("owner", "agent", "relay", "user2")
240:    expected_pubkey = fixture["signer"]["expected_pubkey"]
241:    if expected_pubkey is not None:
242:        if delivered["pubkey"] != expected_pubkey:
245:                f"({delivered['pubkey'][:12]} != {expected_pubkey[:12]})"
252:                f"{leg}: the {role} sender must not be one of the known S0-01 identities"
550:        if membership.get("removed_pubkey") != delivered["pubkey"]:
552:                f"{leg}: membership.json removed_pubkey does not match the delivered sender"

$ grep -n (the tests that encode the current signers) tests/test_s0_02_buzz_authz.py
235:def test_self_authored_specimen_names_the_agent_identity():
242:def test_unauthorized_specimen_is_not_a_known_identity():
246:    assert blob["signer"]["expected_pubkey"] is None
289:def test_not_allowlisted_specimen_is_relay_accepted_user2():
1425:def test_a_nonmember_leg_signed_by_a_known_identity_fails(tmp_path):
1437:    _expect_failure(bundle, "must not be one of the known S0-01 identities")

$ grep -n "owner2\|nonmember" proofs/S0-02/tools/pc/run_s0_02_legs.sh proofs/S0-02/tools/pc/deliver_event.py proofs/S0-02/check_buzz_authz.py | wc -l
0

$ sed -n "173,183p" proofs/S0-02/tools/pc/run_s0_02_legs.sh   # the runner signs with the fixture role key
deliver() {  # deliver <fixture> <leg-dir> <role> [extra deliver_event.py args...]
  local fixture=$1 legdir=$2 role=$3; shift 3
  ( set -a; . "$SEC/$role.env"; set +a
    exec /usr/bin/python3 "$DELIVER" --fixture "$fixture" --leg-dir "$legdir" \
      --secret "$SEC/$role.env" --relay-http "$RELAY_HTTP" --t0 "$(date +%s)" "$@" )
}

role_for() {
  /usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["signer"]["role"])' \
    "$REPO/proofs/S0-02/fixtures/$1.json"
}

$ python3 scripts/validate-ledger integrity --root . | grep -E "S0-02|INVALID"
S0-02 ABSENT
rc=0

$ bash scripts/pc_suite.sh set-id -- tests/test_s0_02_buzz_authz.py
1 files set=a5de0beef100
$ python3 -m pytest tests/test_s0_02_buzz_authz.py -q -p no:cacheprovider -x
182 passed, 24 skipped in 118.62s (0:01:58)

# the PC, read-only (13:1xZ): the public halves and the secret files' modes (never their contents)
== pubs
owner 2267fe91571e5c9166ddf1a80176e988bdd00b9023edcc33375e1be85928000c
owner2 82f440d16985a59efd88ffcbbf186fe27ecde5db2a39773f50c354a08e8cd2b2
nonmember f5aa4962136f829d80cd01966d437eba54d8f1ca97b7d2073d3c5560367dd816
agent ff4d48deaa326bcae60687e64cca48dd7f70099933fbda0ae40d2561485f4ce1
user2 fec645734c4bdd1a6867ab061b0a7aca7f8128d98ace364707814043b090ea22
== env modes
  owner.env	600 82
  owner2.env	600 82
  nonmember.env	600 82
  agent.env	600 82
  user2.env	600 82
```
