# INSTALL1: slopo installed and tuned; every tool the workflow names installed and smoke-checked on a fresh container (D-090)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/INSTALL1-report.md` (write it
incrementally from the start). PIN: 3c495c9 (origin; every boundary file below is unchanged from the PIN to the local head,
measured). Evidence: `docs/research/findings/system1-context/AUDIT-2026-09-25.md` section 7 (the installation table, 34 items).

## WHY

The owner: "some of the tools aren't properly installed, like slopo ... it's very useful, one that we're supposed to be using
very often", and "our slopo isn't very well optimised, and we need it to be". The audit measured 34 items: slopo, pytest-xdist,
gh and the RWKV venv missing in the sandbox; 16 items with no install line in `scripts/setup.sh`; 29 with no pin in
`upstream.lock.yaml` (standing rule 13 requires one for every upstream dependency). The coordinator measured slopo missing on
the PC too. An instrument that is not installed never runs, and the System-1 layer (the design in the same folder) will run
these tools automatically: they must install on every fresh container.

## CONTRACT

1. **slopo, installed and pinned.** Package `slopo` from PyPI, version 0.6.0 (the source the trading-system integration named:
   `rafal-qa/slopo`, AGPL-3.0, Python 3.12+; `/home/user/trading-system/docs/SLOPO-INTEGRATION-MAP.md`).
   - Install it into its own venv, never into the project venv.
   - Pin it in `upstream.lock.yaml`: version, the wheel's sha256, license, role "advisory, never a gate".
   - `setup.sh` installs it on a fresh container. `pc-setup.sh` does the same on the PC; you write the PC lines, the
     coordinator runs them over the bridge.
   - Never vendor its source into this repository: AGPL code stays a pinned external tool.
2. **slopo, wired.**
   - Port the trading-system's local embedding server (`/home/user/trading-system/scripts/slopo_embed_server.py`, a local ONNX
     model, no API key, code never leaves the box), with a provenance header.
   - Port its config and ignore files, rescoped to this repository's code (`scripts/`, `src/`, `proofs/`, `harness-ports/`, and
     say whether `tests/` belongs).
   - Port the incremental sync after each commit (the kit's `post-commit` snippet: `slopo index` then `slopo embed`, niced,
     flocked, never blocking), gated by the hook's rule that re-indexes only on a code change.
   - Add a one-line wrapper for `slopo review --base <ref>` (CLAUDE.md and the `code-intel-trio` skill name that command).
   - Ignore the local artifacts in `.gitignore`.
3. **slopo, tuned ("optimised"), measured, not assumed.** Measure and report, before and after each change you keep:
   - the first full index and embed;
   - an incremental sync after a one-file commit;
   - `slopo review` on a real lane diff (the K265 commit is a good one);
   - `slopo analyze`;
   - peak memory.
   Tune what the measurements point at (the embed server's threads and batching, the quantized model, the scope) and show
   the result on the same inputs. Report the cluster count before and after a tuning step, so speed never costs results
   silently.
4. **The rest of the installation table.** For every row of the audit's section 7:
   - one that is NOT installed is installed (pytest-xdist into the project venv; `gh` stays absent by design: this sandbox uses
     the GitHub MCP tools, so say so; the RWKV/fla venv belongs to the PC: say where it lives);
   - one with no `setup.sh` line gets one where the container does not bring it;
   - one with no pin gets a pin where it is an upstream dependency (a container-provided system tool is marked as such).
5. **A smoke table at session start.** `setup.sh` prints one line per tool: name, found or not, and its `--version` (or a
   presence check). A missing tool warns loudly and never stops the session.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. The timing table of contract item 3, each cell with its command and run count.
3. `bash scripts/setup.sh` run twice. The second run shows every tool found; paste the smoke table. The run is idempotent:
   nothing is re-downloaded when present.
4. Tests for the wrapper, the post-commit gating (a docs-only commit syncs nothing; a code commit syncs), and the lock-file
   pins (every new pin parses and its sha256 matches the downloaded artifact). Run `bash scripts/test_summary.sh` twice with
   the set id; pyflakes rc 0; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write.
5. NOT-done and DISCREPANCIES.

## BOUNDARY

MODIFY: `scripts/setup.sh`, `harness-ports/bin/pc-setup.sh`, `upstream.lock.yaml`, `scripts/hooks/post-commit` (the slopo sync
only), `.gitignore`, and the tests of those. CREATE: the slopo config and ignore files at the repository root, the ported embed
server under `scripts/`, the review wrapper under `scripts/`, new tests, your report. The `code-intel-trio` and `bug-echo` skills
may be edited only where a slopo command or path they name changes; follow the mirror rule, then run the bake tail.
READ everything else. Another lane (S1-L1) is live in this tree on `.claude/settings.json`,
`scripts/install_session_hooks.py`, `.claude/hooks/session-start.sh` and their tests: touch none of them. Scratch:
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/install1/`.

## STANDING RULES

No git writes (the coordinator commits); no PC bridge; no outward-facing action. Downloads come only from PyPI, the model's
official host and the pinned release URLs. Never read a secret file. The disk is tight (2.6 GB free; a model and a venv can
take hundreds of MB): measure sizes, delete scratch as you go, and say the final footprint. Keep at least 1 GB free at every
step: another lane shares this disk and a full disk kills both (AF-AP-219). Run `df` before each download or install, and stop
and report if one would cross the floor. Say whether slopo and the embed server can share one venv.

## PREMISE — MEASURED at authoring (2026-09-25 15:5xZ)

```
$ command -v slopo  (sandbox; and on the PC over the bridge)
NOT ON PATH  (both)
$ git grep -n -i slopo -- scripts/setup.sh upstream.lock.yaml
upstream.lock.yaml:135:    adopted: "2026-09-05 (owner decision; same standing as slopo)"   <- the only mention; no install, no pin
$ sed -n '2,3p' /home/user/trading-system/docs/SLOPO-INTEGRATION-MAP.md
**What it is:** `rafal-qa/slopo` (v0.6.0, AGPL-3.0, Python 3.12+, PyPI) — an
embedding-based semantic code-duplicate detector. tree-sitter extracts
$ ls /home/user/trading-system/scripts/slopo_embed_server.py /home/user/trading-system/slopo.conf.yaml
both present (the embed server: jina-embeddings-v2-base-code, model_quantized.onnx, CPU, port 8811, one text per ONNX run)
$ ls -d /home/user/trading-system/.slopo-runtime   (16:0xZ)
No such file or directory   <- no venv and no model in this container: build them fresh
$ git -C /home/user/trading-system grep -i -E 'slopo.*(install|pip|download)|model_quantized' -- scripts/   (16:0xZ)
only the embed server itself (its docstring says the model is "downloaded by setup"; no setup line exists): write the installer
$ df -h / | tail -1   (16:0xZ)
/dev/vda        252G   35G  2.6G  94% /
$ sed -n '50,60p' /home/user/sandbox-kit/scripts/git-hooks/post-commit   (the kit's sync snippet, IP-3)
if command -v slopo >/dev/null 2>&1 && [ -d "$REPO_ROOT/.slopo-runtime" ]; then ... slopo index ... && slopo embed ...
$ (the audit, section 7) 34 items; installed 29; NOT installed 4 (slopo, pytest-xdist, gh, the RWKV/fla venv);
  no install line in setup.sh 16; no pin in upstream.lock.yaml 29
$ sha256sum (at the PIN) | cut -c1-16
2abe9eefcb69f602  scripts/setup.sh
1e08e9c0423cdbee  harness-ports/bin/pc-setup.sh
54dd139b3bac09dc  upstream.lock.yaml
008767573a1690c2  scripts/hooks/post-commit
6291afbc39e03492  .gitignore
```

A question for you, not a fact: what did the trading-system integration measure for slopo's speed, and does its map name a
known slow step? Read `docs/SLOPO-INTEGRATION-MAP.md` and its research notes there, and start the tuning from that.
