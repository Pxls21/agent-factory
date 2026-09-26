---
name: env-tool-quirks
description: This repo's measured shell, git, commit-helper, tool and test-gate quirks, and its ops scripts (moved verbatim from CLAUDE.md by CTX1, D-089). Load before a background job, a `pgrep` or `pkill`, a commit, a push, an anchor edit, a test gate or pasted count, a proof regeneration, a `vendored_manifest.py --write` or a worktree-isolated Agent dispatch; before using an ops script (resume-heal, orient, relaunch-suite, pc_suite, why, replay_transcript_edits, lint_delta, verify-planning-repo, anchor_edit); and when a shell or tool behaves unexpectedly. Append each new quirk here the moment it bites.
---

# Environment and tool quirks, measured on contact

CLAUDE.md was shortened losslessly (the owner, D-089, 2026-09-25): the text below left its "Environment & Tools" section
VERBATIM, and CLAUDE.md points here. PC bridge and PC lane quirks live in skill `pc-bridge-lanes`; the Ouroboros stdio
quirks in skill `ouroboros-stdio`. The quirk readers (`scripts/jev_context.py`, `scripts/hiccup_scan.py`,
`scripts/jev_locate.py`) index the dated quirk lines of this file with CLAUDE.md's.

## The ops scripts

Ephemeral container. `scripts/setup.sh` is the toolchain source of truth (the SessionStart hook
re-runs it every session; idempotent, tolerant). Commit and push anything worth keeping. The ops
scripts, all ported from the source repo and re-pointed at this one: `scripts/resume-heal.sh`
(the mechanical fresh-container resume in ONE command — ff-sync, hooks, venv, background
reindex; judgment steps stay yours) · `scripts/orient.sh` (three-layer startup orientation:
quartet liveness → chat intent via `chat_tail.py` → last commits → ready-to-run `graft ask`
suggestions; hooked at session start) · `scripts/relaunch-suite.sh` (the detached full suite,
`pytest proofs/ spikes/ tests/`, survives the Bash cap) · **`scripts/pc_suite.sh launch|wait|log` (the SAME suite on
the PC's 12 cores with 8 xdist workers, on the pushed head + the working tree as a sha-verified patch — the default
gate venue when the bridge is up; `spikes/` stays sandbox-only)** · `scripts/why.sh <file> [fn]`
(on-demand chronology from primary sources) · `scripts/replay_transcript_edits.py` (recover a
dead delegate's edits from its transcript) · `scripts/lint_delta.py` (the pre-commit pyflakes
DELTA gate: new hits only; `--base HEAD` reads tracked files only, so a lane's NEW files are linted by `pyflakes` directly until staged, JT1 DISC-1 2026-09-24) · `scripts/verify-planning-repo.sh` (the planning docs' own check) ·
**`scripts/anchor_edit.py` (ledger-plane
edits: every anchor validated unique BEFORE any write, all-or-nothing, rc 2 with the file untouched on a miss; `--replace OLD NEW` /
`--insert-after|--insert-before PREFIX TEXT`, `@file` values; it never commits — a mutation and a commit never share a call, bit twice 2026-09-08; a VALUE that begins with `@` is ALWAYS read as a file path — there is no escape — so a placeholder never starts with `@`, bit 2026-09-22 on an `@@FULL@@` placeholder; an `@file` OLD value carries the file's trailing newline, so an OLD anchor ends at a line boundary or is written without one — a mid-line OLD is refused with nothing written, bit 2026-09-22; an `@file` TEXT for `--insert-after|--insert-before` is split on newlines, so a file that ends in a newline inserts one EXTRA blank line: write it with `printf '%s'`, bit twice 2026-09-24, a wiki block and the D-070 row)**.

## Shell, git, commit-helper and tool quirks

**Document quirks on contact.** Hit a tooling quirk (wrong arg name, quoting, API mismatch) →
immediately append a one-line fix to this file. Don't defer.
**A `pgrep -f <pattern>` liveness/wait loop MUST exclude its own command line** — bracket the
first char (`pgrep -f '[p]ytest ...'`) or match the binary with `-x` (two self-matching waiters
spun for a whole lane in the source repo). **The bracket protects only the PATTERN: any other literal occurrence of the name in the same command line (a later `sed`/`nohup` argument naming the script) self-matches — a `pkill -f "[r]un_packs.sh"` killed the coordinator's own shell 2026-09-14 (rc 144); kill by pid, never by `pkill -f` inside a compound command that also names the target.**
**`safe_commit.sh` fills `{STAMP}` and `{DATESTAMP}` in the commit MESSAGE only, never inside a file** (VERIFY-S0-04-LEAK
F14, 2026-09-25: 16 ledger entries written with a literal `{DATESTAMP}` were committed that way; filled afterwards
from each line's commit time): a stamp in file text is substituted when the text is written (`$STAMP` from `date -u`).
**`scripts/safe_commit.sh -m "…"`: no backticks inside a double-quoted message** — bash runs them as command substitutions and the phrase vanishes from the commit (three `in …` phrases eaten on 2026-09-15); write the message to a file or single-quote it. **`git rev-parse --short REV1 REV2` fails ("Needed a single revision") in this container's
shell inside a compound command** — one rev-parse per call.
**While a lane holds `scripts/hooks/*`, every commit runs the lane's working copy of the git hooks** (AF-AP-222; INSTALL1's and L2a's post-commit, 2026-09-25): commit with HEAD's committed hooks instead, a temp dir of `git show HEAD:scripts/hooks/<name>` files made executable and `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=<dir> bash scripts/safe_commit.sh ...` (no hook locates a helper relative to itself, so the copies run as they are), or read the lane's hook diff before committing; task #279 makes safe_commit do it.
**push_clean can LOSE A RACE with the GitNexus banner rewriter:** AGENTS.md/CLAUDE.md index-stat
churn can regrow between its clean-check and filter-branch ("Cannot rewrite branches: You have
unstaged changes" → "N trailer(s) remain — ABORT"). Run `git checkout -- AGENTS.md CLAUDE.md &&
PUSH_BRANCH=<branch> bash scripts/push_clean.sh --no-delegates-live` as ONE compound command; on
that abort, re-check `git status` before suspecting real leftover trailers. It also REFUSES on a
dirty tree — commit or stash first (bit 2026-09-03). **`--lanes-live` with an EMPTY declared list refuses SILENTLY (rc 1, no
message; bit 2026-09-07 after the last lane landed) — once no lane is live, push the clean tree with
`--no-delegates-live`; the untracked `.lanes-live` file itself is gitignored and does not count as dirt. It also refuses a CLEAN tracked tree while lanes are declared (`tree is clean — use --no-delegates-live`, 2026-09-23): push that state with `--no-delegates-live`.**
*(Since CTX1, D-089, no automatic `gitnexus analyze` rewrites AGENTS.md or CLAUDE.md: the race above now needs
a manual analyze run without `--skip-agents-md`.)*
**push_clean REWRITES the unpushed range, so a lane brief's `PIN:` is the POST-PUSH SHA — read it from `git log origin/<branch>` AFTER the push, never from the local commit (bit 2026-09-21: the VB-F12-T2 brief pinned 592d9a8, which became 38ad46b on origin and did not exist on the PC clone; one extra commit to correct it).**
**A trailing `&` backgrounds the WHOLE `&&` list** (`rm -f pidfile && … && nohup lane.sh … &` ran the list in one background subshell: its own `rm -f` raced and deleted the pidfile the next line wrote, and `$!` was the subshell, bit 2026-09-21) — put the `nohup … &` on its own line. **A poller relaunched INSIDE a Monitor script dies with the monitor's expiry** (the harness kills the monitor's process group; `Terminated` at 20:17Z 2026-09-21): start long-lived pollers with `setsid nohup … </dev/null &` and locate them by `pgrep -f '[p]c_lane.sh\.[A-Za-z0-9]* <brief>'` — `$!` after setsid is its short-lived parent. **A PC-RESIDENT lane cannot run `scripts/pc_suite.sh`** (the sandbox's bridge launcher; `bridge_http_code=000` on the host, G1 2026-09-21): a PC brief's pytest gate is `python -m pytest -n 8 …` directly (xdist is installed on the PC), under the 420 s cap.
**A waiter on a background task's `.output` never ends when it reads the last lines (2026-09-25: one spun 53 minutes after
its target had finished):** the harness appends a blank line and `[exited with code N]` after the command's own output, so
`until grep … <(tail -2 <task>.output)` never sees the command's last line. The harness re-invokes the session when a
background task ends, so no waiter is needed; when one is, test the trailer line or the whole file, never the last N lines.
**The shell's cwd resets to `/home/user` after a container restart** — start every command chain
with `cd /home/user/agent-factory` (or absolute paths).
**`rsync` is absent in the sandbox** — copy trees with `tar` / `cp -a`.
**`scripts/vendored_manifest.py --write` hashes IGNORED files under `.claude/` too** (a plugin's `.claude/fast-jev-output/` drifted the `.claude/` row, 2026-09-25; task #232): move such plugin output aside before `--write`, put it back after. The pre-commit manifest check hashes the same working tree, so a commit that stages a path under a vendored root is blocked the same way (the P1 harvest, 2026-09-25 08:2xZ): move the output aside for that commit too, until task #232 hashes tracked files only.
**The Edit, Write and Bash tools turn a typed `\u2028` / `\u2029` escape into the LITERAL separator bytes** (K215 2026-09-24, then the coordinator's own Write probe: the file held `e2 80 a8`; a typed `\u0085` or `\t` stays as text) — AF-AP-132's second shape, written by the tool; VERIFY-K215 F-7 (2026-09-24) measured the Bash tool doing it through a quoted heredoc, and a typed backslash-u-0041 became `A` there, so the decoding is not limited to the separators. Build such a string in code (`chr(0x2028)`) and check every written file before a gate runs: `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` must print 0.
**`grep -c` exits 1 when it counts zero**, so the separator check above fails as a shell status exactly when it passes: never chain it with `&&` (2026-09-25 16:0xZ: a `for` loop of such checks ended on a count of 0 and stopped the anchor edits chained after it). Run it as its own command, or test the printed number.
**An Agent dispatch with `isolation: "worktree"` cannot work on this tree (bit 2026-09-23, J1-0-R3):** the agent's worktree was a partial checkout (mostly `.claude/skills/`, none of the brief's boundary files) and its Bash tool refused every command ("the working-directory isolation context for this agent was lost"); it returned with no work done. Dispatch a sandbox build agent WITHOUT worktree isolation (a disjoint file boundary in the shared tree; the coordinator commits through `safe_commit.sh`), or build small tooling in the main loop.
**`push_clean.sh --lanes-live` counts TRACKED dirty files only** (`git status --porcelain --untracked-files=no`): a live lane's new untracked files never block the push; a tracked file it changes outside `.lanes-live` does. At dispatch, declare every tracked path the brief lets the lane change, with "the tests of those" resolved to paths (2026-09-25: S1-L1 changed `tests/test_session_start_hook.py`, undeclared; caught by measuring before the push). The push runs from a clean detached worktree, so its pre-push manifest check sees no untracked or ignored file under `.claude/` (843b721 passed with S1-L1's untracked hooks and the ignored `.claude/fast-jev-output/` in the shared tree); only a `--no-delegates-live` push from the shared tree needs that output moved aside.
**push_when_green picks `--no-delegates-live` when the live lanes hold no tracked change**, and the pre-push manifest check then runs in the shared tree, where it hashes ignored output under `.claude/` (`.claude/fast-jev-output/`) and blocks the push (2026-09-25, the push of 9db6ac6): set that folder aside for the push, or push with `--lanes-live` once a lane has a tracked change (the check then runs in a clean worktree); task #273 ends it.
**`cmd | grep -q` under `set -o pipefail` reports failure when the check passed, if `cmd` writes again after the match** (AF-AP-225: grep exits at the match, the writer dies of SIGPIPE, rc 141; INSTALL1's `slopo --version | grep -qx` made setup.sh delete and rebuild a good venv, 2026-09-25): capture the output in a variable and compare it; a one-line writer (`echo`, `head -1`, one short `printf`) is safe.
**slopo 0.6.0 walks its whole `source_dir` before it excludes anything** (`slopo/indexing/scanner.py` `scan_directory`: `rglob("*")`, then a pathspec match per file), so a clone that holds big untracked trees makes every index slow: the PC clone's first index ran over 8 minutes where the whole sandbox sync took 130 s (2026-09-25); task #285 prunes the walk in our launcher, never in slopo's source.
**Claude Code's skill list has a character budget** (D-092, 2026-09-25): context x 4 x `skillListingBudgetFraction`
(default 0.01, about 30,000 characters here); past it, skills with recent use keep their descriptions and the rest (ties
in alphabetical order) are bare names. The owner keeps the list lean (D-093): the default stays, and the System-1
layer (Laya) picks the skills to inject; 0.07 would list all 488 (172,800 characters, about 35,000 more tokens per
request, measured on an Opus probe). A SKILL.md whose frontmatter is not valid YAML (an unquoted `: ` in the description) is
listed with no description whatever the budget; `tests/test_skill_frontmatter.py` guards it. To measure what a subagent
received: `python3 docs/research/findings/system1-context/inventory.py listing --listing-from <agent>.jsonl --listing-out
<file.json>` (it prints names, described and chars; without `--listing-out` it crashes).
**In a linked worktree `.git` is a one-line file, not a directory** (`gitdir: <repo>/.git/worktrees/<name>`; SLOPO2's
landing gate, 2026-09-25): a test that asserts something about a `.git` directory reds in the clean-worktree gate
and passes in the clone. Key such an assertion on `(ROOT / ".git").is_dir()`.
**The permission classifier refuses a sandbox lane's `python3 scripts/ledger-gen --root .` in the shared tree**
("Modify Shared Resources", S0-04-LEAK 2026-09-25) and its `scripts/pc_suite.sh set-id` call: a re-mint brief names
the ledger regeneration as a coordinator landing step, and the lane hands over the expected file (a `ledger-gen` over
a scratch copy) to compare with.

## Test gates and pasted counts

**A skip guard that stats a path under `/root` raises on CI instead of skipping (2026-09-26, stage0-ci run #1102):** the sandbox runs as root, CI's runner does not, and Python 3.12's `Path.exists()` swallows only ENOENT, ENOTDIR, EBADF and ELOOP, so `Path("/root/venv-laya-probe/bin/python").exists()` raised `PermissionError` and the test failed where it meant to skip (`tests/test_s1_synth.py`, SYNTH1). A guard for a sandbox-only resource uses `os.path.exists` (it returns False on any `OSError`) or catches `OSError`; a green in the sandbox proves nothing about a non-root runner.

**`tests/test_proof_status.py` needs a SHORT `--basetemp` (e.g. `/tmp/ps/bt`)** — the session scratchpad path exceeds gpg-agent's Unix-socket
length limit and the eleven throwaway-key anchor tests fail with `gpg … --quick-generate-key … exit status 2` (nine false reds on 2026-09-14);
the same tests are green with a short path. pytest creates only the LAST component of `--basetemp` — `mkdir -p` its parent first, or every test errors at setup with `FileNotFoundError` (bit 2026-09-14). A regenerated minted result (AF-AP-56) after an `accepted/<id>` tag exists fails three of its
committed-state tests BY DESIGN until the owner re-signs — read the assertion, never the count.
**A proof-status test in the CI shape (no tag refs) runs in `git clone --shared --no-tags <repo> <scratch>`, never by
touching the owner's `accepted/*` refs (2026-09-25, the F4 control):** the clone shares the objects (about 190 MB of working
tree) and holds no tags, as CI does; a linked worktree shares the refs, so it cannot show that state. Plant the state there
(a tag object removed, a PENDING line declared) and run the test in the clone.
**ATTESTED INPUTS (AF-AP-56, CI runs 106-110 red 2026-09-06):** every minted `proofs/<id>/result.json` hashes its tooling — `proofs/schemas/*`, `scripts/proof-runner`, `scripts/validate-ledger`, `proofs/registry.yaml` and the proof's own files. Any change to one of those is a tooling change: regenerate the dependent artifacts in the SAME increment (`python3 scripts/proof-runner run --proof <id> --venue sandbox --root .` for each minted id), then gate on `python3 scripts/validate-ledger integrity --root .` (PRESENT, never INVALID) + `python3 scripts/ledger-gen --root .` + `git diff --exit-code proofs/ledger.json`. A lane brief whose boundary contains an attested path names this gate. Regenerate ONLY from a world-traversable tree (the repo, never a root-only scratch
copy: S0-11 drops to `nobody` and cannot read `0700` paths) — a real proof failure DELETES the minted artifact by design (VERIFY-N5g F8).
**The Laya dataset manifests are attested inputs too:** `docs/research/findings/laya-ft-labels/*/dataset-manifest.json` hash `scripts/transcript_export.py` and the `scripts/laya_ft/` code as code inputs, so a change to any of them regenerates the manifest's code hash and proves the dataset bytes unchanged (K265's step; SCRUB1 re-scrubs every stored record before it may, 2026-09-25). The lock check itself is the builder's pre-fit comparison (`collect_v2` at the manifest's recorded commit, run with the old
and the new scrub, its items counted), not a re-scrub of the stored states, which can miss a change the old opaque rule had
hidden (VERIFY-SCRUB1 F11, 2026-09-25: 0 of 6,220 items differed, and the proxy agreed that time).
**REAL-LEG CORPUS = a DECLARED input (VERIFY-CK10 F-R10-25):** the checker's real-producer tests read `S0_01_REAL_LEG_DIR`
(sandbox default `/root/s0-01-realleg/golden`, exported by `scripts/test_summary.sh`; the PC tree by `pc_suite.sh`) under
`S0_01_VENUE` sandbox/pc — corpus absent or incomplete = the suite FAILS by design, never skips; CI (venue unset) skips by
declaration. A fresh container restores it with `bash scripts/realleg_sync.sh pull` (20 s over the bridge, every sha verified
against the PC tree; `check` re-verifies).
**A PASTED COUNT CARRIES ITS SET (2026-09-15: the ledger's `1556 passed, 9 xfailed` floor was an 18-file run, read as the 13-file `tests/test_s0_01_*.py` glob — a 215-test "drop" that was no drop, AF-AP-73 at the floor):** `pc_suite.sh wait` prints `pytest-set: N files set=<sha12> — <files>` beside the summary, `lane_gate.sh`'s RESULT line carries `tests=<sha12>`, and `scripts/pc_suite.sh set-id -- <files>` prints the id a brief or a ledger line quotes a count against (sha256 of the sorted list of the path STRINGS as given — order-blind, spelling-sensitive: quote the paths repo-relative exactly as the brief lists them; the GOV2c-A lane read `892ef4ebb5b8` for the brief’s `f3baa8cf79c7` six files, 2026-09-22 — same files, another spelling). **Sandbox static-copy gate in ONE command:** `scripts/lane_gate.sh -r <rev> -f "<lane files>" -t "<tests>" [-n 2]` — a `git archive`
copy + exactly the lane's working-tree files, the identity table, N `test_summary.sh` runs whose counts must agree, one RESULT line the
checkpoint commit pastes; long sets run it DETACHED (`nohup … > gate.log 2>&1 &`) and read the log. **PC gate on EXACTLY the pushed commit while lanes hold the tree:** `pc_suite.sh` ships the working tree as a patch, so run it
from a clean detached worktree (`WT=$(mktemp -d) && git worktree add -q --detach $WT HEAD && cp .pc-bridge.env $WT/ && cd $WT &&
bash scripts/pc_suite.sh launch -n 8 -- <files>`; ff-sync the PC clone first; `wait <RUN_ID>` takes the id `launch` prints; remove
the worktree after). `launch` resolves the index via `git rev-parse --git-path index` (a worktree's `.git` is a file — bit 2026-09-06).
**`tests/test_vendored_manifest.py` copies the vendored inputs (`.claude/`, the `sandbox-kit/` roots, about 75 MB)
into pytest's `tmp_path` for EVERY test, from the WORKING TREE** (bit 2026-09-25 13:4xZ, CTX1: a whole-file run
filled the disk, 1.1 GB in one basetemp, and every writer on the box saw `No space left on device`; pytest keeps
the last three basetemps). Check `df -Pm /` first, pass `--basetemp` under a scratch dir you delete after, and run
only the `-k` tests you need. The copy also takes ignored files under `.claude/` (task #232), so prove a class-count
pin on a `git archive HEAD` mirror of `.claude/ .agents/ sandbox-kit/ vendor/` plus the changed files, not in the
shared tree.
**To run the whole `tests/test_vendored_manifest.py` on this disk, run one test at a time:** collect the ids (`--collect-only -q`) and run each alone with a fresh `--basetemp` deleted before the next (57 of 57 exit 0 that way at S1-L1's harvest, 2026-09-25; the whole file at once copies about 3.4 GB); task #273 gives the file one shared copy.

**A hook registered outside the repo can cost on every call (2026-09-25, AF-AP-220).** The codebase-memory installer wrote seven hooks into `~/.claude/settings.json`; the Read/Grep/Glob gate cost 2.0 s per call with 0 bytes out for a week, unseen, because a hook that prints nothing leaves no record in the transcript. Census every registered hook (the three settings files and the plugins) with a timed synthetic run and its bytes out (`docs/research/findings/system1-context/hook_probe.py`), and strip what gives nothing (`scripts/strip_cbm_hooks.py`).
