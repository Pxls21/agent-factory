**`DONE:` (build lane's self-graded report — a PROPOSAL until the sandbox-side adversarial-verifier lane grades it; I issue no gate verdict.)**

Route: LOCAL build route (vLLM default effort); **HYBRID** in practice — a cloud step served one turn when the local step refused with the chat-template 400. I claim nothing about which model wrote the code.

**Final state:** the 5 boundary files (`M`/`T`/`V`/`C`/`R`) are the only changes in the worktree. Full gate **51 passed in 28.57s** (3 runs: 23.27s / 23.22s / 28.57s). `--write` → `--check` **PASS** (9 roots). pyflakes clean (rc 0). no_laya clean (38 files).

## 1. Premise — verified by run at the PIN
The brief's premise reproduces exactly: the committed `C` has `129 first-party`; grouped, `47 aegis · 12 prism · 2 typesafe · 19 honey · 3 provenance-files · 46 other`. The 56 copy-eligible (blob under a declared kit root): `20 council · 19 honey · 13 llm-wiki · 4 output-styles`; **no path matches two roots**. The 12 remainder (9 non-PROVENANCE + 3 `PROVENANCE-*.md`) stays first-party. Provenance pins/sources all present. **No CONTRACT-INVALID.**

## 2. Class table before → after
| class | before | after |
|---|---:|---:|
| kit-verbatim | 2958 | 2958 |
| kit-adapted | 14 | 14 |
| first-party | 129 | **12** |
| copy: council / honey / llm-wiki / output-styles | — | **20 / 19 / 13 / 4** |
| vendored: aegis / prism / typesafe | — | **47 / 12 / 2** |

## 3–5. (V rows pasted in §3 of the report; RED→GREEN in §4; mutant battery in §5)
- **RED at PIN:** `-k k1h` = **6 failed, 45 deselected** (the 7th red, `test_real_claude_split`, is not `-k k1h`-named but is red at `T:379`). All 6 fail for their exact expected reason (no copy/set/verify rule yet); all 7 green after.
- **Mutants:** m1 (drop copy rule) → 1 fail; m2 (name-matched copies) → 5 fail; m3 (skip `verify_declared_sets` at `M:858`) → 6 fail; **m4 (sets after copies) → 0 fail, full 51 pass — a genuine no-op, exactly as the brief predicted** (no set file is a kit-root copy, so the order is unobservable); m5 (drop typesafe set) → 2 fail.

## 6. Key correction vs the previous draft's claims
The draft had claimed `verify_declared_sets` is called at the top of `claude_records` (`M:492`). **That was wrong.** The call is at **`M:858`, the top of `build_manifest_data`** (`M:492` is a symlink check; `claude_records` at `M:487` does not call it). The code is correct — both `--write` and `--check` flow through `build_manifest_data`, so both verify before writing; m3 confirms it's fail-closed. I corrected the report's §8/§10/§4 to match the actual line numbers (all re-verified against the live file).

## 7. DISCREPANCIES
1. `-k k1h` at PIN is 6 failed (not 7).
2. m4 is a no-op (equivalence, reported not chased).
3. m3 kills 6, m2 kills 5.
4. **report_lint (3 fix-hint rounds, the brief's cap): `32 refs — OK 15, NEAR 3, MISS 13, UNCHECKABLE 1, UNRESOLVED 0`** (trace 16→14→13). The 13 surviving MISSes are **range-citations** where the lint checks only the range's first line against a claim token on a later line — a known heuristic limit, not a factual error. `--min-refs 10` floor met (32 refs, all byte-verified against the live file).
5. `V:21` first-party digest is the *generated* 12-file value, not the 129-file pin.
6. **Adjacent untracked artifact (not mine, not fixed):** `downloaded_files/dashboard.lock` (0 bytes, mtime 13:55, after my edits, not at PIN) — outside the boundary; flagged so the coordinator doesn't mistake it for a lane output.

## 8. Self-attack (three most likely ways I'm wrong, ruled out)
1. Copy matched by name → m2 red (name-match breaks the honey byte-change control).
2. Provenance verification bypassed on a path → it's at the top of `build_manifest_data` (`M:858`), the one choke point both `--write` and `--check` pass through; m3 (call removed) is red.
3. Hollow digest (row present but over wrong files) → digests are over the `.claude/` copies themselves and asserted against the *regenerated* `V` (not a constant); `--check` re-derives them.

## 9. NOT-done
- **Independent adversarial verify** — separate lane; this is a PROPOSAL.
- **Commit** — the coordinator harvests (a lane never commits).
- The `.agents/` mirrors (out of scope).
- report_lint's 13 surviving range-citation MISSes (reported, not chased, per the 3-round cap).

Report + incremental draft: `/home/rocco/agent-factory/.lanes/pc-k1-h.md--74aa8c5/tree/tasks/briefs/kit-k1-support/K1-h-report.md` (draft mirrored at `.../report-draft.md`).
