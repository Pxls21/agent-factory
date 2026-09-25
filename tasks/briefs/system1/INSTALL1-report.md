# INSTALL1 report: slopo installed and tuned; the installation table closed (D-090)

Lane: INSTALL1 build (sandbox, Opus 5.5, `code-implementer`). Brief: `tasks/briefs/system1/INSTALL1-brief.md` (77ada56).
Started 2026-09-25 16:04Z (`date -u`: Fri Sep 25 16:04:24 UTC 2026). Written incrementally; a stop mid-run leaves this
record. Status: DONE in the sandbox; the PC lines written, NOT run (section 7).

**RESUMED after a container restart** (`date -u`: Fri Sep 25 16:50:59 UTC 2026; the restart killed the first run at about 16:4xZ). Sections 1 and its question were re-checked before being kept (section 1a); everything after them is written by the resumed run from 16:5xZ on.

## 1. Premise re-measured (evidence demand 1)

Run at 16:04Z (`date -u`: Fri Sep 25 16:04:37 UTC 2026), one run each, in the sandbox. The PC column is NOT run: no
bridge in this lane.

| premise line | measured now | match |
|---|---|---|
| `command -v slopo` (sandbox) | `NOT ON PATH rc=1` | yes |
| `command -v slopo` (PC) | NOT run here: no PC bridge in this lane | not measured |
| `git grep -n -i slopo -- scripts/setup.sh upstream.lock.yaml` | `upstream.lock.yaml:135:    adopted: "2026-09-05 (owner decision; same standing as slopo)"` only | yes |
| `sed -n '2,3p' .../SLOPO-INTEGRATION-MAP.md` | line 2 is empty, line 3 is `**What it is:** \`rafal-qa/slopo\` (v0.6.0, AGPL-3.0, Python 3.12+, PyPI) — an` | yes, one-line offset (the text is lines 3-4); does not matter |
| `ls` embed server and conf | both present (3242 B and 989 B, Sep 3); `slopo.ignore.txt` also present (1705 B) | yes |
| `ls -d /home/user/trading-system/.slopo-runtime` | `No such file or directory` rc=2 | yes |
| `git -C trading-system grep ... -- scripts/` | only `scripts/slopo_embed_server.py` (two lines: the "downloaded by setup" docstring and the `model_quantized.onnx` load) | yes |
| `df -h / \| tail -1` | `/dev/vda        252G   35G  2.6G  94% /` | yes |
| kit `post-commit` lines 50-60 | the IP-3 block: `if command -v slopo ... && [ -d "$REPO_ROOT/.slopo-runtime" ]; then ( flock -n 9 ... slopo index ... && slopo embed ... ) 9>/tmp/slopo-sync.lock ... &` | yes |
| audit section 7 counts | "Items: 34. installed: 29, not installed: 4, no installer in setup.sh: 16, no pin: 29." (`AUDIT-2026-09-25.md:1286`) | yes |
| sha256 (first 16) of the 5 boundary files, worktree vs `git show 3c495c9:<f>` | setup.sh `2abe9eefcb69f602` both · pc-setup.sh `1e08e9c0423cdbee` both · upstream.lock.yaml `54dd139b3bac09dc` both · post-commit `008767573a1690c2` both · .gitignore `6291afbc39e03492` both | yes, all 5 |

Verdict: the premise holds. No CONTRACT-INVALID.

### The brief's question: what the trading-system measured for slopo's speed

- It recorded NO wall time. The map's rollout step 3 asked for one ("measure wall time + token/unit counts — the only
  expensive step; record in the runbook", `SLOPO-INTEGRATION-MAP.md:119-120`); no runbook in `docs/` names slopo
  (`grep -n -i slopo docs/*RUNBOOK*` → no lines). The clone here has one commit, so git history cannot date it.
- An upper bound only (inferred, from two approximate stamps in `/home/user/trading-system/wiki/topics/live-state.md:1010-1020`): deployed
  "~19:25Z" with the "first full embed in flight", "MAIDEN ANALYZE DONE (~20:55Z)": at most about 90 minutes for index +
  first embed + analyze of 2,948 units / 426 files.
- The known slow step the map names: the first full embed ("only the first full embed is expensive",
  `SLOPO-INTEGRATION-MAP.md:14-15`). The embed server's own comment names the reason: "One text per ONNX run"
  (`/home/user/trading-system/scripts/slopo_embed_server.py:50-52`, and `MAX_TOKENS = 4096` at its line 31). Tuning starts there.
- Re-checked by the resumed run (one run each): the trading-system's `docs/*RUNBOOK*` files name no slopo (grep rc 1);
  the clone has 1 commit; its live-state lines 1010-1020 hold "DEPLOYED (~19:25Z)", "2948 units/426 files", "first
  full embed in flight" and "MAIDEN ANALYZE DONE (~20:55Z): 83 clusters, 160 exact-copy units". The answer holds.

## 1a. The survived state, re-checked before reuse (17:1xZ, one run each)

| survived item | check | result |
|---|---|---|
| section 1 premise | the 4 unchanged boundary files re-hashed (first 16 of sha256) | `2abe9eefcb69f602` setup.sh, `1e08e9c0423cdbee` pc-setup.sh, `54dd139b3bac09dc` lock, `008767573a1690c2` post-commit: all still equal the PIN; `.gitignore` differs only by the first run's slopo block. Section 1 holds |
| `/root/venv-slopo` (447 MB) | `slopo --version`; `pip check`; installed files vs the wheel's RECORD | `Slopo 0.6.0`, Python 3.12.3 (`/usr/bin/python3.12 -m venv`); `No broken requirements found.`; 65 of 65 files match the wheel's RECORD |
| the wheel (scratch) | `sha256sum` vs PyPI's JSON API (`pypi.org/pypi/slopo/0.6.0/json`) | `ec9d2dd8c5e152c5f1e7cb1d88e25f44b215e3bef308a282a8a9259f5ec6105b`, 65,252 bytes: equal to PyPI's published digest and size. License-Expression AGPL-3.0-or-later, Requires-Python >=3.12 |
| `.slopo-runtime/model/model_quantized.onnx` | `sha256sum` vs the Hugging Face LFS oid at revision `516f4baf13dec4ddddda8631e019b5737c8bc250` (the repo's main, Apache-2.0, not gated) | `ed45870251c9f0cf656e78aab0d37a23489066df8a222bb1c8caf8a45f2cb16d`, 161,895,621 bytes: equal |
| `.slopo-runtime/model/tokenizer.json` | `git hash-object` vs the published git blob id (the file is not in LFS) | `64a31466e9fdd5ef043ff0f07b97ee2e256a205e`: equal. Its sha256 (pinned from here on): `b01c78a902aa4facb2f47f95449f48e2f7bbfea5d2472ee2f6ce92323c6f86e5` |
| `scripts/slopo_embed_server.py` provenance header | source sha256 + commit + branch in `/home/user/trading-system` | `ad91eed0...1a264d`, commit `3e332ce3a5a7affa49b52f3e83e4e0d42fcc464f`, branch `clean-build`, origin `github.com/Pxls21/trading-system`: all equal the header. Its forward claims (a setup.sh download, a lock pin) were not yet true; now they are (sections 2, 4) |
| the first run's tuning numbers | its scratch logs `runs/bench.jsonl`, `runs/index.jsonl` | kept only as a second sample beside this run's re-measurement (section 3); its probe outputs (parity, padding, threads, memory) were never saved, so every probe was re-run |

Nothing was downloaded again: the venv, the wheel and both model files verified.

Status at 17:1xZ: server rewritten and bit-parity-checked; `slopo.conf.yaml`, `slopo.ignore.txt`, `scripts/slopo_review.sh`,
the post-commit slopo block, the setup.sh slopo block + pins + smoke table, the pc-setup.sh slopo block and the lock
pins are written; tuning cells R-V0..R-V3 measured; the with-tests cell is running; tests not yet written.

## 3. slopo tuned, measured (evidence demand 2)

Venue: the sandbox, 4 CPUs, 16 GB RAM, no swap, shared with two live lanes (load1 before/after is in each scratch JSON line;
a cell run while another lane's suite ran reads slower). Instruments: `scratchpad/install1/bench.py` (embed of a fresh
copy of one template index through a server started with the given flags, then `slopo analyze`; wall, server CPU from
/proc, server peak RSS = VmHWM, cluster count from the report dir, drift = vectors compared with the reference DB) and
`measure.py` (one command: wall, user+sys CPU, peak RSS of the whole process tree via RUSAGE_CHILDREN). "pre" = the
first run's sample (same bench.py, same template, its log `runs/bench.jsonl`); "R" = this run's sample on the final
server code (`runs/bench2.jsonl`). Inputs, every embed cell: the four-root scope template (1,339 units, 1,334 distinct
bodies, 305,998 tokens; p50 123, p90 522, p99 1,531, max 2,453 tokens: NO unit reaches 4,096).

### 3.1 The full embed, before and after each kept change (same inputs; cluster count and table checked every step)

| server flags | runs | embed wall s | server CPU s | server peak RSS MB | vectors equal to the source's | clusters | cluster table |
|---|---|---|---|---|---|---|---|
| `--threads 0 --workers 1 --max-tokens 4096` (the SOURCE behaviour) | 2 | 357.41 pre, 260.11 R | 944.74, 827.43 | 2,217.0, 3,465.3 | 1,334/1,334 (R vs pre: bit-identical across the restart) | 18, 18 | reference; R identical |
| `--threads 1 --workers 4 --max-tokens 4096` | 2 | 149.14 pre, 153.59 R | 472.04, 481.36 | 4,577.6, 4,588.9 | 1,334/1,334 bit-identical, both | 18, 18 | identical (vectors bit-identical, so the table is) |
| `--threads 1 --workers 4 --max-tokens 2048` | 2 | 134.24 pre, 184.82 R | 454.57, 478.06 | 4,478.0, 4,571.0 | 1,327/1,334 (min cos 0.962) | 18, 18 | identical (pre and R diffed) |
| `--threads 1 --workers 4 --max-tokens 1024` (KEPT: the defaults) | 2 | 96.97 pre, 103.33 R | 332.73, 350.18 | 1,857.7, 1,842.8 | 1,294/1,334 (the 40 units over 1,024 tokens; min cos 0.861) | 18, 18 | identical (pre and R diffed) |

Kept, with the reason each: (1) `--workers 4 --threads 1`: 4 texts at once, each still alone in its own ONNX run: about
2x faster than the source and 1.9x less CPU, vectors bit-identical (the source's intra-op threads spin). (2)
`--max-tokens 1024`: another 1.5x, and the peak falls from 4.6 GB to 1.8 GB (attention memory grows with the square of
the length and the 4 workers start on the longest texts together); 40 of 1,334 units are embedded from their first
1,024 tokens, and the 18-cluster table is unchanged. Together: about 3x faster, 2.6x less CPU, a lower peak than the
source. (2048 keeps more units exact but not the memory: 4.5 GB.) The R-2048 wall (184.82 s against 134.24 s pre) is the
spread this shared box gives; read single cells within about 40 percent.

Rejected, with the measurement: padded batching (the first run's `--batch-tokens`): padding a text by 64 tokens changes
its int8 vector (cos 0.996314), and a 2-text padded batch changes both (cos 0.994664 and 0.988947; `probes/pad_probe.out`);
a vector would then depend on what it was batched with, so an incremental sync and a full embed would disagree. The
option is removed; a committed test holds the property (a text's vector is bit-identical alone and in a 4-text request)
and a negative control shows padding still moves it. The ORT arena off: the longest unit alone peaks at 1,430 MB
against 1,965 MB, but runs 50 percent slower (5.34 s against 8.06 s; `probes/mem_probe.out`); at the 1,024 cap the arena
costs 12 MB (497 against 485 MB). Not changed. The fp32 model: NOT measured (a 640 MB download on a disk with 2.0 GB
free and three lanes; the int8 model is the source's choice and the smaller one).

Parity (`probes/parity2.out`, one run, deterministic): the final server, in both the source configuration and the tuned
one, gives vectors bit-identical to the SOURCE server's own loop (executed from the trading-system file) on 40 real
units, 40,342 tokens, the 12 longest included.

### 3.2 The cells the brief names (commands and run counts)

| cell | command (run from) | runs | result |
|---|---|---|---|
| first full index | `slopo index` (bench template, first run) / `slopo index` (K265 clone) | 1 + 1 | 1.54 s, 1,339 units from 114 files (pre) / 0.95 s, 1,330 units from 112 files |
| index, nothing changed | `slopo index` (first run, twice) | 2 | 0.63 s, 0.59 s |
| first full index + embed, the DEPLOYED path | `bash scripts/slopo_review.sh --sync` (the real repo, no slopo.db yet) | 1 | rc 0, 130.33 s wall, 356.28 s CPU, peak RSS 1,861.7 MB (the whole tree: wrapper, slopo, server), 1,361 bodies embedded (the scope plus L5's live `scripts/chat_find.py`); no server left running |
| first full embed, K265 tree | `slopo embed` (K265 clone, tuned server started by hand) | 1 | 125.88 s, 1,325 bodies |
| incremental sync after a one-file commit, AFTER (deployed) | `bash scripts/slopo_review.sh --sync` (clone, after a commit that changed one function) | 2 | 6.22 s and 5.53 s; peak 379.2 and 359.0 MB; 1 unit embedded; the server started and stopped inside |
| incremental sync, BEFORE (the kit's snippet shape) | resident source-config server, then `slopo index && slopo embed`, LiteLLM's network price list on (same commit, same starting DB) | 2 | 4.96 s and 4.59 s; peak 232.7 and 232.4 MB (client side only: the resident server holds 290 MB idle and GBs of arena after a full embed, always) |
| incremental sync, no unit changed | `bash scripts/slopo_review.sh --sync` after a comment-only commit (slopo strips comments from a unit's body) | 1 | 0.45 s: the count check starts no server |
| `slopo review` on a real lane diff | `slopo review --base 6abed36^` (the K265 clone at `6abed36`, K265 rev 2 landed) | 2 | 0.39 s, 0.32 s; "1 of 17 changed units look similar to other code." (below) |
| `slopo analyze` | `slopo analyze` (the real repo, deployed index) | 2 | 0.28 s, 0.27 s; 63.1 MB; 18 clusters; "Similarity ratio (excluding exact copies): 3.02% (41/1356 units flagged as similar)" |
| peak memory | the rows above | - | full embed 1.84-1.86 GB (the server); incremental 360-380 MB; review 56 MB; analyze 63 MB; client 257 MB during a full embed |

The known slow steps: the first full embed (as the trading-system map said; it recorded no wall time, section 1) and,
per sync, LiteLLM's import: `import litellm` 2.90 s and 3.05 s with the local price list, 3.33 s and 3.52 s without
(the default fetches it from raw.githubusercontent.com: source "remote"). The wrapper sets the local list: no network,
about 0.45 s saved per embed call. `litellm.telemetry = True` is set in the package, but nothing reads it on this path
(grep: the only other use is a local variable in the proxy CLI): no telemetry leaves the box.

What the K265 review found (advisory, reported not fixed): `_chunk_map` at `scripts/qwen_jev.py:385-395`, a unit K265
changed, is the same function as `_chunk_map` at `scripts/laya_systemone_server.py:124-133` (score 1.00). Both copies are still
at HEAD (`git grep -n "def _chunk_map" HEAD -- scripts/`).

### 3.3 Does tests/ belong? No, for the standing scope (measured)

The same kept flags on the scope with `tests/` (one run, `R-WT`): 5,756 distinct bodies (4.3x), embed 342.98 s,
server CPU 1,000.21 s, peak 1,991.1 MB, **112 clusters** against 18. By where the members live: 85 test-only (76
percent: fixtures and setups repeated by design), 14 test plus production, 13 production only. So `tests/` stays out of
`slopo.conf.yaml` (as in the trading-system's config): it multiplies the first embed by 3.3 and the triage by 6.
The 14 mixed clusters carry a lead worth one on-demand run: a test that holds a copy of the production function it
tests (cluster 1: `utf8_redecode_lenient` in `proofs/S0-01/tools/scripted_backend.py` and in
`tests/red/test_s0_01_backend_credential_screen.py`), the mirror-test shape the build loop warns about. Such a run needs
its own config and DB (the scope is frozen per DB); NOT built here. `harness-ports/tests/` (9 files, 56 units) stays in,
under the brief's `harness-ports/` root: noted as the one inconsistency.

## 2. What was built (contract items 1, 2 and 5; files and lines, from `git diff -U0` and `wc -l`)

| file | change | what it does |
|---|---|---|
| `scripts/slopo_embed_server.py` (NEW, 134 lines) | ported, provenance header | the trading-system server (sha256 `ad91eed0...`, commit `3e332ce`), with flags for the port, the model dir and three knobs; one text per ONNX run kept (bit-identical to the source, section 3); `--workers N` (default: the CPUs) runs N texts at once; `--threads` (default 1); `--max-tokens` (default 1024, measured); the tokenizer's padding switched off explicitly; `/health` reports the settings. The first run's padded batching was removed (section 3.1) |
| `scripts/slopo_review.sh` (NEW, 87 lines) | the review wrapper | `scripts/slopo_review.sh <base-ref>`: `slopo index`, then `slopo embed` when a unit waits (the server started on the config's port and stopped on every exit, AF-AP-145's shape), then `slopo review --base <base-ref>`; `--sync` stops after the embed (the hook's call). One slopo run at a time (flock: the sync skips, a review waits). A running server is reused only when its `/health` names the model and the 1,024 cap (AF-AP-33); another server on the port is refused, exit 4. No network: `LITELLM_LOCAL_MODEL_COST_MAP=True` |
| `slopo.conf.yaml` (NEW, 42 lines) | ported, rescoped | `source_dir: .`, then `/*` and `/*/` excluded and `scripts/ src/ proofs/ harness-ports/` brought back; `**/vendor/` and `/proofs/S0-01/tools/archive/` excluded (vendored `acp.rs`; byte-exact archived instruments); `tests/` out (section 3.3); the model on `127.0.0.1:8811` |
| `slopo.ignore.txt` (NEW, 10 lines) | ported header, empty ledger | the trading-system's dismissed hashes cover its own paths, so none carry over |
| `scripts/hooks/post-commit` +30 at 145-174 | the slopo sync | after a commit that changed a file slopo reads (slopo's 10 extensions, case-insensitive, under a root the config brings back; the config is read, so the scope has one source), `scripts/slopo_review.sh --sync` in the background, `nice -n 19 ionice -c 3`, output to `$T/slopo-sync.log` after one decision line per commit ("launched (first: ...)" or "none: ..."). The quartet's code and log are unchanged |
| `scripts/setup.sh` +150 -10: 8-10, 139-143, 212-280, 306-307, 334-338, 453-509 | install, pins, smoke table | header list; codebase-memory pinned to v0.10.8 (`CBM_DOWNLOAD_URL`); the slopo block (the wheel by sha256, its own venv with the server's pinned runtime, `--no-cache-dir`, the kept wheel, `~/.local/bin/slopo`, the model by revision and sha256, the 1 GB floor before each download); code-review-graph 2.3.8; pyflakes 3.4.0, pytest 9.1.1, pytest-xdist 3.8.0; the smoke table |
| `harness-ports/bin/pc-setup.sh` +55 -1: 9-11, 19, 96-145 | the PC lines | the same slopo block at PC paths (`$HOME/venv-slopo`, `$AF_REPO/.slopo-runtime/model`), with the first Python 3.12 or later it finds (Fedora 42's python3 is 3.13; on PyPI, onnxruntime 1.30.0, tokenizers 0.23.2, numpy 2.5.3, tree-sitter 0.26.0 and tree-sitter-python 0.25.0 have cp313 Linux x86_64 wheels, checked; the other dependencies NOT checked). NOT run here (no bridge) |
| `upstream.lock.yaml` +130: 155-170, 199-209, 250-352 | pins | `advisory_tooling.slopo` (version, `package_wheel_digest`, AGPL-3.0-or-later, role `advisory_semantic_duplicate_detector_never_a_gate`); `advisory_models.jina-embeddings-v2-base-code` (revision, both file digests, Apache-2.0); new sections `session_toolchain` (9), `vendored_tooling` (7), `container_provided` (9). No new key is `repository`, `commit` or `*_sha256`, so `parse_lock` still reads 25 entries and `validate_pin_agreement` passes (run) |
| `.gitignore` +8 at 69-76 | the first run's block, kept | `/slopo.db`, `/slopo.db-journal` (slopo keeps SQLite's rollback journal: no WAL pragma in its source), `/slopo-report/`, `/.slopo-runtime/` |
| `tests/test_slopo.py` (NEW, 655 lines) | the tests | section 6 |

**Can slopo and the embed server share one venv? Yes, measured.** `/root/venv-slopo` (447 MB) holds slopo 0.6.0 and the
server's runtime (onnxruntime 1.30.0, tokenizers 0.23.2, fastapi 0.141.1, uvicorn 0.54.0); `pip check`: "No broken
requirements found." The server needs nothing slopo does not already pull in except onnxruntime, tokenizers, fastapi
and uvicorn, and slopo's own pins (numpy ~=2.5.2, litellm ~=1.98.0) do not conflict with them. One venv, one 447 MB,
not two.

## 4. The installation table closed (contract item 4; the audit's 34 rows, section 7)

"Before" is the audit's cell; "after" is this lane's change. setup.sh line numbers are at the final file.

| # | item | installed (sandbox) | setup.sh line | pin in upstream.lock.yaml |
|---|---|---|---|---|
| 1 | graft | yes | yes (0.16.0) | NEW `session_toolchain.graft` 0.16.0 |
| 2 | GitNexus | yes | yes (1.6.10) | NEW `session_toolchain.gitnexus` 1.6.10 |
| 3 | codebase-memory | yes (0.10.8) | NOW PINNED: `CBM_DOWNLOAD_URL=.../releases/download/v0.10.8` (the asset answered HTTP 200 to a HEAD) | NEW `session_toolchain.codebase-memory-mcp` 0.10.8 |
| 4 | code-review-graph | yes (2.3.8) | NOW PINNED `code-review-graph==2.3.8` | NEW `session_toolchain.code-review-graph` |
| 5 | ripwire | yes | yes | yes (unchanged) |
| 6 | sentrux | yes | yes | yes (unchanged) |
| 7 | **slopo** | **was NO; now yes** (0.6.0, verified against PyPI) | **NEW** (the wheel by sha256) | **NEW** `advisory_tooling.slopo` + the model's `advisory_models` entry |
| 8 | prism skills (5) | yes | none needed: committed under `.claude/skills` | NEW pointer `vendored_tooling.prism-skills` (PROVENANCE-PRISM.md) |
| 9 | honey plugin | yes | yes (vendored marketplace) | NEW pointer `vendored_tooling.honey-for-devs` |
| 10 | jev plugin | yes | **NO (NOT done, section 7)** | yes (`advisory_tooling.jev-pruner`, unchanged) |
| 11 | aegis plugin | yes | **NO (NOT done, section 7)** | NEW pointer `vendored_tooling.aegis-skills` (the skills; the plugin is not vendored) |
| 12 | wiki compiler | yes | yes (vendored) | NEW pointer `vendored_tooling.llm-wiki-compiler` |
| 13 | council | yes | yes (vendored) | NEW pointer `vendored_tooling.council-of-high-intelligence` |
| 14 | Ouroboros | yes | yes (0.53.0) | NEW `session_toolchain.ouroboros-ai` 0.53.0 |
| 15 | aleph | yes | yes (vendored, editable) | NEW pointer `vendored_tooling.aleph` |
| 16 | phoenix-docs | n/a (an http MCP) | yes (registration) | nothing to pin: a hosted endpoint; the smoke table says so |
| 17 | Laya venv (sandbox) | yes | **NO (NOT done, section 7)** | yes (unchanged) |
| 18 | RWKV / fla venv | absent BY DESIGN: PC only, `~/venv-rwkv` and `~/venv-rwkv-b` on the PC (PC-BRIDGE.md:216, `scripts/gpu_side_by_side.sh:65`); no script in the repo creates them | no (PC work) | the model entry exists (`rwkv7-goose-world2.9-0.4b`, `runtime_required` names fla 0.3.0) |
| 19-21 | node, npm, uv | yes | none needed: the container brings them | NEW `container_provided` (v22.22.2, 10.9.7, 0.8.17) |
| 22 | pytest | yes | NOW PINNED 9.1.1 | NEW `session_toolchain.pytest` |
| 23 | **pytest-xdist** | **was NO; now yes** (3.8.0, `import` and the smoke line) | **NEW** (3.8.0) | **NEW** `session_toolchain.pytest-xdist` |
| 24 | pyflakes | yes | NOW PINNED 3.4.0 | NEW `session_toolchain.pyflakes` |
| 25 | mcp 1.29.1 | yes | yes | NEW `session_toolchain.mcp` |
| 26-30 | ripgrep, jq, git, claude CLI, gpg | yes | none needed: the container brings them | NEW `container_provided` (14.1.0, 1.7, 2.43.0, 2.1.280, 2.4.4); plus python3.12 3.12.3 (slopo's interpreter) |
| 31 | gh | absent BY DESIGN: this sandbox reaches GitHub through the GitHub MCP tools | no | nothing to pin (absent) |
| 32 | output styles | yes | yes (vendored copy) | NEW pointer `vendored_tooling.output-styles` |
| 33 | session hooks | yes | yes | the repository's own script: nothing upstream to pin |
| 34 | git hooks | yes | yes | the repository's own hooks: nothing upstream to pin |

After: installed 31 of 34 (was 29), 2 absent by design (gh, the RWKV venv), 1 n/a (phoenix-docs). A setup.sh line is
missing for 3 rows that need one (jev plugin, aegis plugin, Laya venv: NOT done); the other 11 rows without a line need
none (8 container-provided, prism committed in git, gh by design, RWKV on the PC). A lock entry or pointer now covers
30 rows; the 4 without one carry nothing to pin (phoenix-docs, gh, the two repo-owned hook sets).

## 5. setup.sh run twice (evidence demand 3)

- Run 1 (17:39Z, the code at that time): rc 0 in 62 s, and it exposed a DEFECT of mine: the slopo present-check
  (`slopo --version | grep -qx "Slopo 0.6.0"`) fails under `set -o pipefail` (grep exits at the match, slopo's next
  flushed line breaks the pipe: PIPESTATUS `1 0`), so the run deleted `/root/venv-slopo` and rebuilt it from PyPI
  (about 450 MB; the same versions came back: litellm 1.98.1, numpy 2.5.3, onnxruntime 1.30.0, `pip check` clean). It
  also left 114.2 MB in pip's http cache (removed: the files written after 17:38). The session-start log
  (`/tmp/agent-factory-setup.log`, last written 16:44:23, before this setup.sh went live at 17:12) names no slopo line,
  so no compaction ran the defect. Fixed in the three places with that shape (setup.sh and pc-setup.sh `slopo_ok()`:
  the version captured with no pipe; the wrapper's `up()`: a here-string), and guarded by two tests (section 6).
  Run 1 was also the one live pass through the install branch: "slopo 0.6.0 installed into /root/venv-slopo (wheel
  digest verified)".
- Runs 2 and 3 (the fixed code): rc 0 in 20 s each; lines saying "installed into", "downloaded (", "installed
  (prebuilt" or "installed (/root/venv-crg": 0 and 0; `warn` lines: 0 and 0; the venv's timestamp unchanged
  (17:40:00.212 before and after); free disk 1,753 MB before, 1,752 MB after. Nothing was downloaded.
- The model-download branch, exercised live on the small file: setup.sh's own loop (extracted verbatim) into a scratch
  model dir holding a hard link of the ONNX file fetched `tokenizer.json` at revision `516f4ba` and verified it
  (`b01c78a902aa4fac...`, no `.part` left); with the digest's last hex digit changed, the file was refused, its `.part`
  removed, the "model present" line not printed. The 162 MB ONNX download itself was NOT exercised (disk).

Run 3's smoke table, pasted (colour codes stripped):

```
◆ Tool smoke table (one line per tool; a MISSING line is a warning, never a stop)
  ✓ graft                      found    0.16.0
  ✓ GitNexus                   found    1.6.10
  ✓ codebase-memory            found    codebase-memory-mcp 0.10.8
  ✓ code-review-graph          found    code-review-graph 2.3.8
  ✓ ripwire                    found    ripwire 0.4.0 (Release, GNU 14.2.1, built_from=unknown)
  ✓ sentrux                    found    sentrux 0.5.7
  ✓ slopo                      found    Slopo 0.6.0
  ✓ slopo model                found    jina-embeddings-v2-base-code int8 ONNX + tokenizer, digests verified
  ✓ prism skills (count)       found    5
  ✓ honey plugin               found    /root/.claude/plugins/cache/greenpt/honey
  ✓ jev plugin                 found    /root/.claude/plugins/cache/fast-jev-output
  ✓ aegis plugin               found    /root/.claude/plugins/cache/aegis-dev/aegis
  ✓ wiki commands (count)      found    11
  ✓ council agents (count)     found    18
  ✓ Ouroboros                  found    Ouroboros version 0.53.0
  ✓ aleph                      found    usage: aleph [-h] [--timeout TIMEOUT] [--max-output MAX_OUTPUT]
  ✓ Laya venv                  found    laya 0.3.5
  ✓ node                       found    v22.22.2
  ✓ npm                        found    10.9.7
  ✓ uv                         found    uv 0.8.17
  ✓ pytest                     found    pytest 9.1.1
  ✓ pytest-xdist               found    pytest-xdist 3.8.0
  ✓ pyflakes                   found    3.4.0 Python 3.11.15 on Linux
  ✓ mcp (aleph's SDK)          found    mcp 1.29.1
  ✓ ripgrep                    found    ripgrep 14.1.0
  ✓ jq                         found    jq-1.7
  ✓ git                        found    git version 2.43.0
  ✓ claude CLI                 found    2.1.280 (Claude Code)
  ✓ gpg                        found    gpg (GnuPG) 2.4.4
  ✓ output styles (count)      found    4
  ✓ session hooks              found    session hooks: present in /home/user/.claude/settings.json
  ✓ git hooks                  found    scripts/hooks
  - gh (GitHub CLI)            absent by design: this sandbox reaches GitHub through the GitHub MCP tools
  - RWKV / fla venv            PC only: ~/venv-rwkv and ~/venv-rwkv-b on the PC (PC-BRIDGE.md); no sandbox tool uses it
  - phoenix-docs               an http MCP registration (the user-scope block above registers it); no binary to run

◆ Tool smoke: 32 found, 0 missing, 3 absent by design
```

A MISSING line is a `warn()` line, the kind the session-start hook surfaces (`grep '^  ! '`), and `smoke()` never
exits: a committed test runs the function's own text on a missing tool and on a tool that prints nothing, and the
shell carries on (section 6).

## 6. Tests (evidence demand 4)

`tests/test_slopo.py` (NEW, 43 tests, 6 groups): the post-commit slopo block (17: a code commit launches the sync
from the repo root; a docs-only commit, a path outside the roots, a language slopo does not parse, no install or no
config launches nothing and the log says why; the sync never blocks the commit; the hook's roots are the config's; its
extension set is slopo's own `supported_extensions()`), the wrapper (usage exits 2, not installed 3, a sync skips
while the lock is held and runs when it is free, the wrapper and server agree on the 1,024 cap, a squatting server
with another cap is refused with exit 4 and left running, and the REAL pipeline on a throwaway repo: a sync embeds
every unit and leaves no server; an unrelated new function gives "No similar code involving the changes."; a near-copy
under a new name gives "1 of 1 changed units look similar to other code."), the server (a vector is bit-identical
alone and inside a 4-text request, 4 workers bit-identical to 1; negative control: 64 pad tokens move the vector; bad
flags exit 2), the scope through slopo's own scanner (the four roots only, no vendored or archived file; negative
control: without `"/*/"` the scope leaks into `tests/` and `sandbox-kit/`), the pins (the lock's slopo and model
entries parse; setup.sh and pc-setup.sh name the lock's wheel, runtime and model exactly; setup.sh's install lines carry
the session-toolchain versions; the kept wheel matches the lock and its RECORD matches every installed file; the model
files match; negative controls: a flipped digest fails each), and setup.sh (`smoke()`'s own text reports a missing tool
and carries on; `slopo_ok()` of both setup scripts passes under pipefail on the real venv; negative control: the old
`| grep -qx` shape fails on a matching version). The venv- and model-dependent tests skip BY DECLARATION where those
are absent (CI); here none skipped.

The gate set (`scripts/pc_suite.sh set-id`: `8 files set=be6e027a2a97`): `tests/test_slopo.py`,
`tests/test_post_commit_reindex.py`, `tests/test_shell_syntax.py`, `tests/test_vendored_manifest_parse.py`,
`tests/test_upstream_lock_lane_runtime.py`, `tests/test_laya_pin.py`, `tests/test_stage0_ci_workflow.py`,
`tests/test_sentrux_review.py` (the new file plus every existing test that reads a file this lane changed). On the final
files, `bash scripts/test_summary.sh <the 8 files>`, twice (pasted):

```
pytest-exit: 0
pytest-summary: 131 passed in 166.50s (0:02:46)
pytest-exit: 0
pytest-summary: 131 passed in 174.79s (0:02:54)
```

(`pytest --co`: 43 in `tests/test_slopo.py`, 88 in the other seven.) Two earlier runs on the pre-fix files also gave
`131 passed` (188.59 s, 183.54 s). pyflakes on `tests/test_slopo.py scripts/slopo_embed_server.py`: rc 0.
`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`: 0 for each of the 11 files written or changed (the report included).
`bash -n`: rc 0 on every shell file at every save; `python3 scripts/ap_screen.py`: 0 hits on the wrapper, both setup
scripts and the hook.
`python3 scripts/report_lint.py tasks/briefs/system1/INSTALL1-report.md` (worktree): "report_lint: 7 refs — OK 7, NEAR 0,
MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)" (the trading-system references are written as absolute paths).

Red-green: the new tests were first run green only; their teeth were then proven by eight mutants of the real files
(scratch copies, the test file redirected to each): 7 KILLED (no extension check: 3 failed; the sync blocks: 1; no root
check: 3; no lock in the wrapper: 1; a model-only `/health` probe: 1; the server left running: 1; padding switched on: 1).
The 8th, "no docs-plane skip in the slopo block", SURVIVED: that check was dead code (no root holds a docs-plane path,
and slopo parses no Markdown) and would have silently blocked a root the config might add under `tasks/`; it was
removed, the config staying the scope's one source. The pipefail defect: red shown on the old check against the real
venv ("NOT present", the rebuild path), green on the fixed one, and both halves held by committed tests.

## 7. NOT done (first-class)

1. **The PC lines are written, NOT run** (no bridge in this lane): the `slopo_ok` block, `harness-ports/bin/pc-setup.sh:96-145`. The
   coordinator runs them over the bridge; the PC's Python, disk and pip versions are NOT measured here.
2. **No setup.sh install line for the jev and aegis plugins** (table rows 10, 11): neither is vendored in an installable
   form (`vendor/jev-pruner` has no plugin manifest; the aegis skills are vendored, the plugin was installed by hand
   from `/root/jev-plugins/Aegis`), and a plugin install adds hooks to every session (AF-AP-220's class): an owner
   decision, not a lane's.
3. **No setup.sh line for the sandbox Laya venv** (`/root/venv-laya-probe`, row 17): torch (CPU) plus transformers
   would not fit the 1 GB floor on this disk; the venv exists here and its pin is in the lock.
4. **The RWKV/fla venvs** (row 18) stay PC-only with no creating script (PC work).
5. **The skills were not edited.** Proposed for the coordinator, with the mirror rule and the bake tail:
   `code-intel-trio/SKILL.md:224-225` names `slopo review --base <push-base>`; the command still works, but it refuses a
   stale index or an unembedded unit, so the line could name `scripts/slopo_review.sh <push-base>` (it syncs first).
   `bug-echo/SKILL.md:583-592` needs no change: its condition (`slopo.conf.yaml` and `.slopo-runtime/` present) now
   holds, and `slopo analyze` runs from the repository root.
6. **The found defect is not registered** in the ANTI-PATTERN REGISTRY (`docs/INCIDENT-LOG.md` is outside this
   boundary). Class, for the coordinator: a `producer | grep -q` (or `| head`) used as a condition under `set -o
   pipefail`, where the producer writes after the matched line: grep exits, the next write breaks the pipe, pipefail
   fails the condition although the text matched. Echo sweep (every tracked shell file with `pipefail`, `sandbox-kit/`,
   `vendor/` and `.claude/skills` left out): BUG, the three sites of this lane (fixed); WATCH
   `harness-ports/tests/test_qwen_server.sh:194` (a multi-write script into `grep -qF`; green today); OK the rest (an
   `echo`/`printf` of a variable is one write, done before grep reads; `head -1 file | grep -q` writes one line).
7. **The fp32 model was not measured** (a 640 MB download on this disk); nor the 162 MB ONNX download branch (the
   tokenizer's was, section 5).
8. **The PC-side versions of pytest, pyflakes, code-review-graph and codebase-memory stay unpinned** in pc-setup.sh
   (their PC versions are not measured; the lock says so per entry).
9. **An on-demand with-tests slopo run** (a second config and DB; the mirror-test lead of section 3.3) is not built.
10. **An orphaned server after a SIGKILL of the wrapper** is not handled: the trap cannot run, the server outlives the
    run, and a later sync reuses it (its cap matches) and never stops it. A parent-death signal in the server would
    close it; not built.
11. The first triage of the 18 clusters and the ignore ledger's first entries (the trading-system map's IP-4) are not
    done: out of this brief.

## 8. DISCREPANCIES and deviations from the brief (flagged)

1. **The wrapper is 87 lines, not one.** `slopo review` refuses a stale index ("Index is out of date. Run `index` and
   `embed` first.") and an unembedded unit, and an embed needs the server, so a one-line `slopo review --base` wrapper
   fails on every lane's uncommitted work. The call is one line: `scripts/slopo_review.sh <base-ref>`.
2. **The flock moved from the hook into the wrapper** (the kit's snippet locks in the hook): one lock owner, shared by
   the post-commit sync (which skips when busy) and a review (which waits). A lock in both would deadlock (the child
   would lock again a file its parent holds).
3. **setup.sh now pins pytest, pyflakes, code-review-graph and codebase-memory** (item 4 and standing rule 13): a fresh
   container gets these versions, not the newest. The CI workflow (`.github/workflows/stage0-ci.yml:40,84,103`) still
   installs `pyflakes pytest` unpinned: the venues can drift (outside this boundary).
4. **The server's defaults changed** from the source's behaviour to the measured tuning (threads 1, workers = the CPUs,
   max tokens 1024); `--threads 0 --workers 1 --max-tokens 4096` reproduces the source bit for bit (section 3.1).
5. **The first run's padded batching was reversed**, with the measurement (section 3.1).
6. **This lane's own defect** (section 5): run 1 rebuilt the slopo venv from PyPI, against "nothing re-downloaded".
   Fixed and guarded; runs 2-5 downloaded nothing.
7. `python3 scripts/vendored_manifest.py --check` fails in this shared tree on `.claude/ (first-party)` (18 committed,
   20 generated: `.claude/fast-jev-output/`, ignored plugin output, task #232), not on anything this lane changed; the
   lock half (`validate_pin_agreement`) passes, and `parse_lock` reads the same 25 entries.
8. `review` and `analyze` share `slopo-report/`, and a review that finds nothing leaves the directory as it was: the
   wrapper's header says the verdict is the last line.
9. `harness-ports/tests/` (56 units) is inside the scope while `tests/` is out (section 3.3).
10. The brief's disk figure (2.6 GB at authoring) was 2.0 GB at dispatch and is 2.0 GB at the end of this run.
11. Four smoke rows are presence checks, not versions (prism 5, wiki 11, council 18, output styles 4; the plugins by
    path).

## 9. Self-attack: the three likeliest ways this change is wrong, and how each was checked

1. **The post-commit sync could hurt the box.** On a fresh container (no `slopo.db`), the first code commit runs a full
   embed in the background: about 130 s and a 1.86 GB peak (measured, the deployed path). Checked: it runs at
   `nice -n 19 ionice -c 3`, one at a time (flock), the peak is bounded by the 1,024 cap (4.6 GB without it), and
   nothing stays resident after it. NOT ruled out: with other heavy jobs on a 16 GB box with no swap, a transient
   1.9 GB can still matter.
2. **One DB could mix vectors from two server settings** (a hand-started server reused by a sync). Checked: the
   wrapper reuses a server only when `/health` names the model and the 1,024 cap; a squatter with 4,096 is refused and
   embeds nothing (test, and mutant M6 killed). Residual: a server started with the same cap but another `--model-dir`
   would be reused (the model id is a constant string).
3. **The live setup.sh and post-commit could break a session or a commit.** Checked: `bash -n` at every save and a
   scratch-then-move for each; setup.sh runs 2-5 rc 0 with no warn line; the hook's tests run the real hook in
   throwaway repos (17 pass) and the existing quartet tests stay green. It did break once, in the way that costs
   (run 1's venv rebuild): found by running it, fixed, and now held by a test.

## 10. Disk footprint (final, `du -sh` and `df -h /`)

`/root/venv-slopo` 447 MB (slopo and the server's runtime, one venv, plus the kept 65 KB wheel);
`.slopo-runtime/model` 157 MB; `slopo.db` 6.9 MB and `slopo-report/` 80 KB (the deployed index and its analyze);
pytest-xdist and execnet 0.9 MB in the project venv; `/root/.local/bin/slopo` a symlink; pip's cache back to 5.7 MB
(the rebuild's 114.2 MB removed); scratch 252 KB (the run logs and probe outputs cited above; the clone, the bench DBs,
the report dirs and the extracted slopo source were deleted). Total about 612 MB, of which 604 MB (the venv and the
model) predates this resumed run. Free on `/`: 2.0 GB at dispatch, 2.0 GB now; the 1 GB floor held at every step
(lowest reading 1.74 GB).

Status: DONE in the sandbox (`DONE:` = tests green; the deployed sync, the review and the analyze ran live here);
the PC half is written and NOT run. Report closed at 18:0xZ (`date -u`: Fri Sep 25 18:01:42 UTC 2026).

## 11. This lane's files (for the harvest)

The shared tree also holds other lanes' changes that are NOT this lane's (seen at the end: `.claude/hooks/edit-snapshot.py`,
`docs/INCIDENT-LOG.md`, `sandbox-kit/VENDORED-MANIFEST.md`, `tests/test_edit_snapshot_ap_screen.py`,
`todo/BUILD-TASKLIST.md`, `tasks/briefs/system1/S1-L1-R1-report.md`, and L5's `scripts/chat_find.py`,
`tests/test_chat_find.py`, `tasks/briefs/system1/L5-report.md`). This lane's, all in the brief's boundary:
MODIFIED `scripts/setup.sh`, `harness-ports/bin/pc-setup.sh`, `scripts/hooks/post-commit`, `upstream.lock.yaml`,
`.gitignore`; CREATED `scripts/slopo_embed_server.py`, `scripts/slopo_review.sh`, `slopo.conf.yaml`, `slopo.ignore.txt`,
`tests/test_slopo.py`, this report. Local, ignored or outside the repository: `/root/venv-slopo`, `.slopo-runtime/model/`,
`slopo.db`, `slopo-report/`, `/root/.local/bin/slopo`, pytest-xdist 3.8.0 in `/root/venv-agent-factory`. No git write
was made to this repository; the only commits were in the scratch clone.
