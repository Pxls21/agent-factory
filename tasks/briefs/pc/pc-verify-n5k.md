# PC continuation — VERIFY-N5k (the adversarial grade of S0-01 ACP probe round 14 ARM A, landed b9b6134, plus the comparative grade of ARM B v3)

PIN: 3277373

Role: adversarial-verifier. Route: `agentfactory-verify-local` (the local Qwen3.8-27B at `xhigh` — D-028). Venue: `tasks/briefs/pc/VENUE-MAP.md`
— read it first; it maps every sandbox path in the brief.

## CONTINUATION (read second)
This lane is the FIRST run of the grade — nothing precedes it; start at item 0.

**The brief governs**: `tasks/briefs/s0-01-n5j-support/VERIFY-N5k-brief.md` — READ IT WHOLE and follow it item by item (0-11). Your
worktree IS `git archive 3277373` plus the lane patch (the brief, this file, the pack `VERIFY-N5k-pack.md`, arm B v3's
`N5k-xhigh-report.md` and `N5k-xhigh-v3.diff`); arm A's report `tasks/briefs/s0-01-n5j-support/N5k-report.md`, the N5k build brief with its
two amendments, and VERIFY-N5j's report are IN the archive. Save your report at
`tasks/briefs/s0-01-n5j-support/VERIFY-N5k-report.md` inside your tree, draft after EACH item (the incremental rule), and return it whole
as your final message.

Venue notes specific to this grade:
- You are on the PC: run `tests/test_s0_01_acp_probe.py` directly with the venue exports (`S0_01_VENUE=pc
  S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`), `/home/rocco/venv-agent-factory/bin`
  FIRST on PATH, a SHORT absolute `--basetemp` under your lane's scratch dir (`mkdir -p` its parent first), ONE foreground call per run,
  counts pasted verbatim. The xdist four-file run of item 5 is ONE call with `-n 4` (about 200 s).
- Item 8's reconstruction of arm B v3 uses the PC clone's history: `git -C /home/rocco/agent-factory archive c6c384a | tar -x -C <scratch>`
  then `git -C <scratch> init -q && git -C <scratch> apply --check tasks/briefs/s0-01-n5j-support/N5k-xhigh-v3.diff` (copy the diff in first)
  — or plain `patch -p1`. Never apply it to your lane tree.
- The real corpus `/home/rocco/s0-01-pinned/realleg/golden` is READ-ONLY: copy a leg under your scratch dir (`cp -a`) before any mutation.
  You never launch buzz-acp, hermes-acp, Hermes, the tee or the relay.
- Every FIFO/hang probe under `timeout` and standalone, never through pytest; kill only what you start, by pid.
- Code intel FIRST (the standing rule): the pack is attached; `graft ask` / `graft skeleton` in your tree, `scripts/ripwire_review.sh for
  <symbol>` from your TREE's own wrapper, `node /home/rocco/agent-factory/.gitnexus/run.cjs impact "<symbol>" --direction upstream --repo
  /home/rocco/agent-factory` (clone HEAD line numbers), `python3 scripts/ap_screen.py <file>`, `python3 scripts/report_lint.py` — before any
  grep or whole-file read.
- Any other Stage 0 lane sharing this host: never touch its tree, `proofs/`, or `tests/test_s0_*` outside your own private copy; every
  mutant on a scratch copy of your archive.
