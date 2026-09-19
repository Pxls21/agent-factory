# VERIFY-S004 — adversarial verify of the MINTED S0-04 compression contract

PIN: commit 5e2a541 (S0-04 MINTED). Role: adversarial-verifier. Contract: seed-stage0-v1.yaml
S0-04 block (A1/A2/A3) + proofs/S0-04/spec.json (two legs). This is a MINTED execution_proof;
your job is to try to break it, then emit a GATE RECOMMENDATION (MERGE-READY /
MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID) — NOT a verdict. Per D-034 the
coordinator triages your findings to verify-followup issues unless one is CORE-BLOCKING (the
headline capability — the compression-off directive honoured end-to-end through real OmniRoute to
the real scripted upstream with request preservation — is actually fake).

## Boundary (attack only these)
- proofs/S0-04/check_compression.py (the oracle)
- proofs/S0-04/spec.json (the two legs)
- proofs/S0-04/hermes/config.yaml (the Option-B proof-owned config the config leg reads)
- proofs/S0-04/tools/pc/{run_s0_04_legs.sh, capture_leg.py} (the producer — RUNS ON PC ONLY)
- proofs/S0-04/evidence/** (the committed real bundle) + proofs/S0-04/result.json (minted)
- proofs/S0-04/fixtures/** (golden + negative bundles)
- tests/test_s0_04_compression.py (74 passed x2)

## What is claimed PROVEN LIVE (reproduce, don't adopt)
Real OmniRoute :20128 + real S0-01 scripted backend :20201, both request legs HTTP 200:
- A1: request.json == committed fixture byte-for-byte; sent x-omniroute-compression: off.
- A2: response x-omniroute-compression = `off; source=request-header` (state off asserted AND
  source=request-header asserted — the structural signature that OmniRoute honoured OUR request
  directive, not a default; anti-hollow-green #7).
- A3: upstream-record.json byte-preserves the sent request (content-length + canonical body;
  the S0-01 backend keeps parsed body sort_keys, so length + canonical-value, not raw bytes — D1).
- config leg: hermes-provider.json (from proofs/S0-04/hermes/config.yaml, provider s0-04-omniroute)
  carries base_url :20128/v1, api_mode, key_env (NAME only), extra_headers.x-omniroute-compression off.

## Known design decisions / concerns to attack HARD (the likely hollow greens)
1. **CONFIG-LEG-AS-MIRROR (the biggest one).** Option B: the config leg reads a committed config
   we wrote, then asserts it carries the compression header — is this a tautology/hollow green? The
   LIVE mechanism is meant to be carried by the request legs (A1 sent + A2 source=request-header)
   and by S0-03's live Hermes run with the same schema. Judge whether the config leg adds real
   signal or is a self-referential lint; if the latter, is it declared honestly (it is, in
   LIVE-CAPTURE-FINDINGS.md + the config.yaml header) — a declared limit, not a blocker, unless it
   inflates the headline claim.
2. **A2 source assertion robustness.** Can a bundle with state off but a DIFFERENT source (default/
   config) pass? (Tests: a bare off and off;source=default both fail compression-source-unexpected.)
   Attack the parse (`;`-split, strip). Is `source=request-header` deterministic/real (both legs
   show it live) or could OmniRoute emit it spuriously?
3. **find-record baseline (AF-AP-106).** The pre-POST --max-seq + --after-seq: can a stale
   same-nonce record from a prior run still be reused if the POST fails? (Test:
   stale-only-after-baseline fails loud.) Attack the seq monotonicity assumption.
4. **Fabricated-bundle resistance.** Can a hand-built evidence bundle (no real OmniRoute) pass the
   checker? The request legs pin url=:20128 + argv; the upstream record is the S0-01 backend's own.
   Try to mint a green without real OmniRoute in the loop.
5. **Negative controls fail for the RIGHT reason** (evidence-header-missing → compression-header-
   missing; evidence-body-diff → request-not-preserved; field mutations; inline api_key → credential).

## Method
Load the contract + this brief; reproduce every load-bearing claim through the real path where you
can (the checker over the committed bundle + the fixtures — venue-independent; the PC capture you
cannot re-run, so grade the committed evidence + the runner's logic statically). Run a mutation
audit on check_compression.py (scratchpad-copy restore ONLY, never git-restore the shared tree).
Report EVERY finding with file:line; apply the blocking predicate; emit the GATE RECOMMENDATION.
