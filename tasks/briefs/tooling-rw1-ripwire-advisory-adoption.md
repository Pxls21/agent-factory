# Lane RW1 — ripwire v0.4.0 as an ADVISORY code-intel instrument (sandbox-only tooling → `code-implementer`)

**Owner ask (2026-09-07):** "might be worth adding this to the quartet and have it integrated into our workflow"
(https://github.com/redhat-et/ripwire). Standing: the SIXTH instrument, ADVISORY like slopo/sentrux — never a gate.
**Task key:** `code-intel-ripwire-adoption` (task DB #43). **PIN:** the HEAD this brief is committed in.

## Boundary (disjoint from every live lane — never touch anything in `.lanes-live`, `proofs/`, `tests/test_s0_01_*`)
`upstream.lock.yaml` (add `advisory_tooling.ripwire`) · `scripts/setup.sh` (install block after sentrux's) ·
NEW `scripts/ripwire_review.sh` · NEW `tests/test_ripwire_review.py` · `sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md`
(new section) · `.claude/skills/code-intel-trio/SKILL.md` + `.agents/skills/code-intel-trio/SKILL.md` (same hunk, then
`bash harness-ports/bin/sync-lane-skills.sh`) · `CLAUDE.md` (one clause on the "Advisory instruments" bullet).

## Facts the coordinator verified 2026-09-07 (primary sources; re-verify what you rely on)
- `git ls-remote --tags`: `v0.4.0` = tag object `e5d6205c11995ff27587fff5895ebd5a5255140f` → commit
  `e663ca8f8a9340ffc38c777138c24825509a87d2` (latest tag; earlier v0.3.5-v0.3.8).
- Asset `https://github.com/redhat-et/ripwire/releases/download/v0.4.0/ripwire-0.4.0-linux-x64.tar.gz`
  (6 417 961 bytes) sha256 `fd0bd0fa849c0e08db59a6a7e5c2d3e9bc062d3089b54196daf9332cd21bbfc8` = the published
  `.tar.gz.sha256` (INTEGRITY ONLY — unsigned; say so in the docs). The direct download URL works through the proxy;
  `releases/latest` returns 403 — never resolve "latest" at runtime, pin the tag.
- Tarball root `ripwire-0.4.0-linux-x64/`: ELF `ripwire` (x86-64, dynamic: libstdc++/libm/libgcc_s/libc; sha256
  `6a1957b829f74e29b16caf550e90ea5504afa3ebd200c0b253f2f3afaae76aa3`; `ripwire --version` → `ripwire 0.4.0 (Release, GNU 14.2.1, built_from=unknown)`), `README.md`,
  `LICENSE` (Apache-2.0), `skills/` (18 SKILL dirs + `install.sh`, which SYMLINKS into `~/.claude/skills`) and
  `hooks/` (5 shell hooks for claude/codex). **RULE: install ONLY the binary to `/root/.local/bin/ripwire`; never run
  `skills/install.sh`; never copy the hooks; state this in setup.sh and in both docs.**
- Runtime on this repo: `ripwire . --exclude=sandbox-kit --exclude=/.claude --exclude=/graft --exclude=/.agents
  --exclude=harness-ports/ports` — cold 1.6 s, `est_tokens="2766"` at `--top-k=60`; warm graph verbs ~0.1 s;
  `--for="<question>"` ~7 s / ~4.1k tokens (BM25 route, confidence=low, still the right two hits first). Flat verbs
  (`--callers/--impact/--exercises/--test-gate/--edit-check`) REJECT `--top-k` (exit 1) — use `--limit=N`;
  `--for` ignores `--top-k`. Writes nothing into the repo (per-root cache under TMPDIR; `--no-cache` = cold).
  `--skipped`: 98 unsupported-ext (`.txt/.jsonl/.summary/.done`, extension-less `scripts/proof-runner`), 5 ignored-dir.
- **KNOWN BLIND SPOT — record it, never paper over it:** this repo's proof tools are exercised through subprocess
  (`Popen([sys.executable, TEE])`). `--exercises=tests/test_s0_01_frame_tee.py` lists checker symbols
  (`check_tee_status`, `_load_timeline_raw`, …) but NOT `frame_tee.main`; `--test-gate=proofs/S0-01/tools/frame_tee.py`
  reports `tests="0" impacted="0"`. The call graph cannot see subprocess edges (the tool says so: `counts_floor="1"`,
  `harness=script`). A ripwire zero is never "untested"; the two-instrument rule for DORMANT claims stands.

## Deliverables
1. **`upstream.lock.yaml`** — `advisory_tooling.ripwire`: repository, release_tag `v0.4.0`, commit, asset name,
   asset_sha256, binary_sha256, license `Apache-2.0`, role, `adopted: "2026-09-07 (owner ask; advisory, never a gate;
   binary only — bundled skills/hooks NOT installed)"`, telemetry line stating what you CHECKED (`strings` / `--help`
   for any phone-home; the binary is documented offline — verify, do not assume).
2. **`scripts/setup.sh`** — a block mirroring sentrux's: skip when `/root/.local/bin/ripwire` matches
   `binary_sha256`; else download the tarball to a temp dir, verify `asset_sha256`, extract ONLY the binary, verify
   `binary_sha256`, `install -m 0755`; `warn` (never fail setup) when the network or a digest fails. Idempotent.
3. **`scripts/ripwire_review.sh`** — modes: `map [--top-k=N]` · `for "<question>"` · `callers SYM` · `impact SYM`
   · `exercises TESTFILE` · `test-gate FILE…` · `edit-check SYM` · `skipped`; the exclude set baked in; flat verbs get
   `--limit=${RIPWIRE_LIMIT:-20}`, never `--top-k`; `RIPWIRE_BIN` override (default `/root/.local/bin/ripwire`);
   usage error → exit 64 BEFORE the binary probe (the sentrux lesson, 2026-09-06); missing binary + valid mode → exit 0
   with one line `ripwire_review: <bin> missing — run scripts/setup.sh (pinned install)`; otherwise pass the tool's
   exit code through. Header comment = the same shape as `scripts/sentrux_review.sh` (what it is, why advisory, quirks,
   the blind spot).
4. **`tests/test_ripwire_review.py`** — deterministic, LLM-free, NO network, no real binary needed: (a) bogus mode with
   `RIPWIRE_BIN=/nonexistent` → 64; (b) valid mode with a missing binary → 0 and the exact "missing" line; (c) a FAKE
   binary (a tmp shell script that prints its argv, one per line) proves for EVERY mode the exact argv the wrapper
   builds (the five `--exclude` flags, the verb, `--limit` on flat verbs, `--top-k` only on `map`); (d) the fake's
   exit code (e.g. 4 from `test-gate`) is passed through unchanged. Negative control: a mode that omits an exclude fails
   the argv assertion (prove by a one-line mutant on a scratch copy — paste the red line).
5. **Docs** — `sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md`: "## ripwire (github.com/redhat-et/ripwire) — ADOPTED
   2026-09-07 as an ADVISORY instrument (owner ask)" with provenance (tag/commit/digests), the unsigned-asset caveat, the
   skills/hooks-not-installed rule, the subprocess blind spot, the flag quirks, the PC install step (owner-run:
   the same digest-verified tarball → `~/.local/bin/ripwire`; NOT done here). `code-intel-trio` skill (both copies):
   "## ripwire — the sixth, ADVISORY instrument" after the sentrux section — which questions go to it (cold orientation
   map; `for` as a SECOND opinion after `graft ask`, never instead; `test-gate`/`edit-check` before a commit as an
   advisory line; `exercises` as a second instrument for a DORMANT claim ONLY when the edge is a direct call, never for
   subprocess-exercised tools) + the exact wrapper invocations. `CLAUDE.md`: extend the "Advisory instruments" bullet
   with one clause naming ripwire and `scripts/ripwire_review.sh`.
6. **Gate** — real run pasted: `bash scripts/ripwire_review.sh map --top-k=5` (first 3 lines) and
   `bash scripts/ripwire_review.sh callers _write_status` (expect main/pump_fd/pump_pipe);
   `bash scripts/test_summary.sh tests/test_ripwire_review.py` TWICE (paste both `pytest-summary:` lines verbatim);
   `python3 scripts/lint_delta.py --base origin/claude/soundbox-kit-migration-iz1jwf` clean on your files;
   `bash scripts/setup.sh` re-run once → the ripwire lines idempotent (paste them); `bash harness-ports/bin/sync-lane-skills.sh`.

## Report (Lever-2, data): DONE table (deliverable · file:line · proof line), the two digests, NOT_DONE, DISCREPANCIES,
SELF-ATTACK. No commits, no pushes, no outward actions, never `git stash/checkout/restore/reset` (shared tree; other
lanes hold uncommitted edits). The scratch assets (tarball, `help.txt`, maps) are under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ripwire/` — reuse the tarball, do not re-download.
