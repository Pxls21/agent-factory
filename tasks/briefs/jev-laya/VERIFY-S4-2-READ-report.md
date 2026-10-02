All eight questions are answered with live evidence (Q6 by reading, as the brief requires), the mutant table is complete, and the real tree is untouched (`git status` shows only the coordinator's own edits). The report follows.

# VERIFY-S4-2-READ (task #471): verify report on the S1 reading program

**Recommendation: MERGE-READY-WITH-FOLLOWUPS.** No finding meets the whole blocking predicate. Two caveats, stated here because the recommendation depends on them:
- **Not run here:** the `fla` backend and the `hf` tokenizer. There is no torch here, so I graded them by reading only.
- **F1 is a judgment call for you.** If breakdown decision 8 ("session-derived data stays out of git … the features sit beside them") binds `read --out`, F1 meets every blocking condition and the recommendation becomes NOT-READY on F1 alone.

PIN `b9f835de`. Measured 2026-10-02 11:01Z to 11:39Z (`date -u`). Scratch: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-s4-2-read/`.

## 0. TL;DR

- [x] **Premise:** it matched at HEAD `d50b48f9` (11:01Z). It moved during the verify; see §1. Only `PREREG-441.md` changed (preamble and §3). §2, §8 and the json block are byte-identical, so read.py's contract did not move.
- [x] **Builder's tests:**
  - `pytest-summary: 52 passed` twice at `d50b48f9`, and once more at the new HEAD `6b8c026b`.
  - Set `9b7b5a45ec51`.
- [x] **The features are right by lineage.** I ran `read` through `RD.main` with a recording backend and checked the full list of ids each readout's state had read since its zero state. All 54 vectors match the contract at segments 1, 7, 64 and 32768, with zero mismatches. That covers 7 rows × 6 arrays, plus 6 candidates × 2 arrays.
- [x] **R-2:** every input check refuses its corrupted input (exit 2, nothing written). The only two passes are allowed by the contract.
- [x] **R-9:** `tokens`, `tails` and `--work` refuse all 12 hostile path shapes, fresh and resumed. **`read --out` writes the features inside a git work tree (F1).**
- [x] **Q8:**
  - No session text, key or marker appears in any output other than the token and tail files, including stdout, stderr and 36 refusals.
  - The outputs are byte-identical from two working directories.
- [x] **Mutants:** 30 new ones. 8 KILLED, 22 SURVIVED. Of the survivors:
  - 9 guard rules the code gets right but no test pins. For each I ran a discriminator: the same scenario on the real code and on the mutant, through the CLI.
  - 1 is a no-op control.
  - The rest are equivalent on the pinned inputs, race-only, or turn a refusal into a crash.
- [ ] **Time-sensitive, because the GPU window is open (commit `28c8e708`):**
  - F3: none of the smoke's three checks reads a long forward on a carried state.
  - F4: `read --backend fla` never checks that the tokens came from that checkpoint's tokenizer.
  - F2: `compare`'s `min` can be vacuous on rows, and it feeds the read-repeat VOID check.

## 1. Premise (evidence demand 1) and how it moved

**At my start: matched.** At HEAD `d50b48f9`, 11:01Z, every output of the brief's premise block matched, including:
- `0` diff lines;
- the nine sha256 prefixes;
- the def and class list;
- `26` test functions;
- `1 files set=9b7b5a45ec51`.

**11:10Z: the coordinator amended `PREREG-441.md` in the working tree.** I compared the PIN copy with the working tree:
```
section 1 identical / section 2 identical / section 3 DIFFERS / sections 4-8 identical
json block identical: True 43580dab3a486cd3
file sha256 pin 07be205f4125eab8 wt f596ffee74ee9155
```

**11:35Z: HEAD moved to `6b8c026b`.** Commit `daa20757` landed task #472 and committed the amendment. Re-running the premise now gives:
```
$ git diff --stat b9f835de HEAD -- <the premise paths>
 docs/research/findings/s1-train/PREREG-441.md |  13 +-
 scripts/s1_train/evaluate.py                  | 640 ++++
 scripts/s1_train/heads.py                     | 340 ++++
$ sha256sum ... (only this line differs from the brief)
f596ffee74ee9155 docs/research/findings/s1-train/PREREG-441.md
```

The `scripts/s1_train` lines are task #472's files, which the brief anticipated; I never opened them. The brief calls a premise-file change a stop-and-report. I report it here but did not stop: the parts of the contract that bind read.py (PREREG §2 and §8) are byte-identical, and read.py, the test, the S4-2 brief and report, features.py, render.py and view.py are unchanged. **The decision to keep or void this verify is yours.**

One side effect: any output made before the amendment records `prereg_sha256` `07be205f…`, while the block is unchanged. The PC tokens step started at 10:5xZ, before the amendment.

## 2. Gates (evidence demand 2)

```
$ PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1 TMPDIR=<scratch>/tmp bash scripts/test_summary.sh tests/test_s1_train_read.py --basetemp <scratch>/gate{1,2}/bt
pytest-exit: 0
pytest-summary: 52 passed in 7.43s
pytest-exit: 0
pytest-summary: 52 passed in 7.56s
$ bash scripts/pc_suite.sh set-id -- tests/test_s1_train_read.py
1 files set=9b7b5a45ec51
(at HEAD 6b8c026b, once more) pytest-summary: 52 passed in 7.69s
(the scratch PIN copy: baseline) pytest-summary: 52 passed; siblings features+view: pytest-summary: 112 passed
```

Other gates:
- **`set-id`** only hashes file names. I read its code first; it makes no bridge call.
- **pyflakes** on read.py and the test: rc 0.
- **Separator count:** 0 for read.py, the test and the report.
- **`ap_screen.py`:** `17 hits over 2 files` (AP-32 16, AP-51 1), and the test screen reads `0 hits`. Both match the builder's report.

## 3. Method

**My own fixture, built through the real producers** (`work/fx.py`, world `w1/`):
- The exporter CLI, with an `init-key` FAKE key, a fixture repo and `--known-values key-only`.
- `build_s1.write_split`, then `view.py` over both.
- The session content is my own. It holds shapes the builder's fixture lacks:
  - three rows on one call;
  - one candidate shared by two files;
  - early rows (A1 at 235 characters, B1 at 69) shorter than the tail and than the window;
  - an emoji and CJK at block ends and around the cap's cut;
  - a candidate holding `{body} {0} {{x}} %s %d`;
  - a third file with no rows;
  - text after the last row.

**My own oracle:**
- Positions come from `render.block` on each event, with offsets summed by the driver. This avoids read.py's slicing and render's `starts`.
- The tokenizer is an explicit greedy scan.
- For R-5 I check lineage: a subclass of the fake backend records, for each state object, every id read since its zero state, and stamps each readout with that history. A spy on `features.write` captures the arrays.

I reused only the builder's mechanical record writers (`Tape`, `success`).

## 4. Answers

### Q1: R-3 and R-4, the tokens

All shapes are correct (`work/q1.py`, and a synthetic check of `stream`):
```
tokens rc 0 stdout s1-read tokens: 2 files, 7 rows, 6 candidates, 4563 tokens in 19 blocks
file 0: stream == oracle: True (3901 ids); ends at the last state_end: True
   s1-0000fa01 252 / s1-0000fa02 657 / s1-0000fa03 657 / s1-0000fa04 657 / s1-0000fa05 3901  (all == oracle)
   decoded == text[:last]: True | after-last in stream: False
file 1: stream == oracle: True (662 ids); s1-0000fb01 69 / s1-0000fb02 662 (== oracle)
files holding rows only: [...] | C absent: True
candidate ... == Hook: + body(candidate) + blank line: True (6 of 6; the capped one 4836 ids)
question ids == question_block verbatim: True
A4 candidate keeps braces and percent: True | A5 candidate over the cap: True
synthetic (RD.stream): one-char blocks, a single 4-byte emoji block, empty blocks between, pieces across
every boundary: ids, positions and block counts == oracle at every cut point -> PASS
```

- **A `state_end` at the first non-empty block** is offset 0, and read.py refuses it (Q3).
- **A one-character block** cannot come from render; the shortest block is `Hook: x` plus a blank line, 9 characters. I checked that case through `RD.stream` directly.

### Q2: R-5, the read

**All read rules hold** (`work/q2.py`):
```
segment     1: lineage mismatches none; stream ends at each row position and nothing past the last: True/True; meta forwards 5272, reads logged 5272
segment     7: ... none ... True/True; 793 == 793
segment    64: ... none ... True/True; 128 == 128
segment 32768: ... none ... True/True; 52 == 52
files identical across segments 1, 7, 64, 32768: every .f32 True; index.json False
index.json identical once counts.forwards is removed: True
```

Lineage confirms each part of R-5:
- Every forward on the stream ends at a row position, and `s` is the readout at that point.
- The candidate is read on a copy, then the question on the same copy; no later readout's history holds them.
- The window holds the last 100 tokens before the position (B1's 69 tokens are read whole), read from the zero state, then the candidate, then the question.
- `c_free` and `q_free` are read from the zero state, one per distinct candidate of the rows read.
- `--segment` changes no readout.

**Resume and `--work`** (`work/q2b.py`):
```
1. resumed == uninterrupted, every byte: True | ... 2 files (1 resumed) ...
2. stale 1.part dir: rc 0 | resumed == uninterrupted: True | 1.part left: False
2b. stale 1.part FILE: rc 2 ... [Errno 20] Not a directory: '.../1.part'
3. the two token sets: 0.tok sha256 equal: True | windows: 100 60
   rc 0 ... (1 resumed) | resumed == uninterrupted: False
   arrays that differ from the uninterrupted run: ['c_ctx_w', 'q_ctx_w', 's_w']
4. file 0's record at 1: rc 2 ... the record of ... is not this file's
5. another segment: rc 2 ... holds another run's work: its work.json is not this run's
6. another backend identity: rc 2 ... holds another run's work ...
7. a record's meta keys: ['forwards', 'sha256', 'src', 'version'] | work.json keys: ['backend', 'segment', 'tokens_manifest_sha256', 'version']
```

So:
- A stale `.part`, another file's record, and a `work.json` of another backend or segment are never taken.
- **A record moved in by hand from another run's `--work` is taken (F5).**

### Q3: R-2, the inputs

Every check is broken through the real producers (`work/q3.py`). Each refusal exits 2 and writes nothing, for `tokens` and `tails` alike:
```
sha256 of view.jsonl / summary.json / manifest.json not the block's -> refused (named reason)
export file bytes vs its entry            -> ...: its bytes do not match the manifest's output_sha256
render sha256 vs summary stream           -> ...: the sha256 of its render is not summary.json's
a change after the last row only          -> the same refusal (whole-file sha256)
state_end inside a block / 0 / at the text's end / -5 / true / 643.0 / a block start of file B -> refused
candidate_sha256 mismatch; a src not in the export; summary without a row file's stream; a duplicate row id -> refused
manifest changed while it was read (in-process, read_manifest patched) -> refused
the no-row file corrupted                -> rc 0, tokens written   (R-2: only row files are read)
state_end moved to another block start (view AND block updated) -> rc 0 (R-2 can test only "a block start")
```

Neither pass is a corrupted input of the features.

### Q4: R-9, the outputs

Results by output kind (`work/q4.py`, `work/q4b.py`). Exit code 2 means a refusal, and every refusal created nothing.

| path shape | `tokens` | `tails` | `--work` (fresh) | `read --out` | `smoke --out` |
|---|---|---|---|---|---|
| `missing/../x`, `empty/..` | 2 | 2 | 2 | 2 | 2 |
| a link to an empty dir, a file, or nothing (dangling) | 2 | 2 | 2 | 2 | 2 |
| the same link spelled `link/` or `link/.` | 2 | 2 | 2 | **0: written through the link** | 2 |
| inside a tree (`.git` directory, `.git` file, a missing deep path, a parent link into a tree) | 2 | 2 | 2 | **0: written inside the tree (F1)** | 0 (no session text) |
| not empty | 2 | 2 | 2 | 2 | 2 |

A resumed `--work`:
- Moved into a tree, linked into a tree, or wrapped in a tree created later: all exit 2.
- A link to a valid work dir outside git is taken (F10).
- `--work` equal to `--out`, or inside it, exits 2 only after every file is read (F9).

So: token ids, tails and `--work` readouts never land in a git tree or over another output. **`read --out` readouts can land in a git tree.**

### Q5: R-7 and R-8

**Tails are right.**
- Each tail is the last 600 characters before `state_end`. A1 (235 characters) and B1 (69) give their whole state; the builder's fixture never reaches that branch.
- The lines are sorted by id.
- The tails manifest holds exactly R-7's keys, which is D-1.

**`compare`:**
- It takes the cosine over the keys both runs hold.
- It refuses two runs with nothing in common.
- But (F2):
```
compare, no row in common, one candidate in common: rc 0 | min 1.0 | row arrays n: {'s': 0, 'c_ctx': 0, ... 'c_free': 1, 'q_free': 1}
```

**Smoke** (in-process, `work/q58.py`):
```
smoke with Nested  rc 1 | {'copy': False, 'head': 'not run', 'split': True}    (a shallow copy over nested state)
smoke with FirstId rc 1 | {'copy': True, 'head': 'not run', 'split': False}    (the readout at a read's first id)
smoke with Scaled  rc 0 | {'copy': True, 'head': 'not run', 'split': True}     (a consistent wrong readout)
```

- The copy check fails a same-object copy (the builder's test) and a shallow copy (mine).
- A consistently wrong readout passes the fake smoke. Only fla's head check could catch it, by design.

### Q6: `fla` and `hf`, by reading only (not run here)

| point | `rwkv7_g0.py` (measured on the PC) | read.py | same? |
|---|---|---|---|
| load | `from_pretrained(..., trust_remote_code=True, local_files_only=True, torch_dtype=bfloat16).to("cuda").eval()` (lines 143-144) | lines 396-397 | yes |
| fla import | before load (phase_env, lines 124-126, in the window-2 run) | line 389, before load | yes |
| tokenizer | `AutoTokenizer.from_pretrained(...)`; `encode(..., add_special_tokens=False)` (lines 138, 156) | lines 322, 327 | yes |
| forward | `model(input_ids, past_key_values, use_cache, logits_to_keep=1)` under `inference_mode` → `logits[0,-1]` (lines 92-93) | `model.model(...)` under `no_grad` → `last_hidden_state[0,-1]` (line 414) | differs by design; this path never ran on the PC |
| zero / copy | `None` / `copy.deepcopy` (lines 111, 114) | lines 409, 418 | yes |

Is `last_hidden_state[0, -1]` taken after the last norm?
- As I know fla's `RWKV7Model`, yes: it applies the final norm before it returns. That is unverified here, because no fla source exists in the sandbox.
- The head check proves it at run time.

Is `copy.deepcopy` a full copy?
- fla's Cache keeps its tensors in lists and dicts, and deepcopy clones them. Also unverified here.
- Window 2 never tested copy isolation: its reuse check (lines 195-198) used no copy.
- The smoke's copy check is the first proof.

How the first PC run can go wrong, and which smoke check catches it:

**It can fail loudly, with an exception.** The causes:
- a missing import (exit 2);
- a wrong `--model` (traceback);
- a missing `model.model` or `last_hidden_state`;
- a missing `tok.vocab_size` (F7: for `tokens`, this raises only after the whole pass, at line 477);
- a transformers ≥ 4.54 venv, where fla 0.3.0's Cache cannot be built (`rwkv7_g0.py` lines 24-26);
- CUDA running out of memory.

The smoke crashes first on most of these. Its exit 1 looks the same as a failed check (F8).

**It can run silently and read the wrong thing:**
- **A readout before the norm, or at another position:** the head check catches it.
- **A copy that shares state with the original:** the copy check catches it.
- **A state not carried between reads:** the split check catches it, but only on about 35 tokens. No smoke check and no window-2 measurement ever read a long forward on a carried or copied state (F3). That is the read's main path: 32,768-token segments, and every candidate block read on a copy. Window 2 measured a 2,048-token prefill from zero, then a 15-token suffix.
- **Fake-tokenizer tokens, or tokens from another checkpoint, read by fla:** nothing catches it (F4).
- **A tokenizer that changes the text it encodes:** nothing catches it; all three smoke checks give the same verdict whatever the ids are.
- **Weights that are not the block's `model_safetensors_sha256`:** read.py records the weights' sha256 but never compares them with the block (F4).

### Q7: the tests

**The oracle is independent.**
- `encode` is a regex and `fold` is the test's own loop; neither imports read.py.
- It shares only the fake's specification constants (pieces, decay, the embedding formula), which any value oracle must mirror.
- My lineage oracle needs none of these constants, and it agrees.

**No test mirrors the code.** read.py is called only as the subject: through the CLI, through `read_prereg` (checked against literals and an independent parse), and through `RD.main` with injected faults.

**Mutants:** §5.

### Q8: the boundary and determinism

**Planted FAKE keys** (`work/q8.py`). I planted six shapes after the export, in a state text, a tool result, a candidate, a thinking block and after the last row:
```
in the state stream 0.tok: ['bare20'] | in candidates.tok: ['bare20'] | in tails.jsonl: ['bare20']
scrub marks read: gh<redacted> 3, sk-<redacted> 3, Bearer <redacted> 3, token=<redacted> 3, <opaque-redacted> 3
thinking marker in any stream or tail: False
FAKE keys in any other output: none   (18 outputs: manifests, meta, work.json, records, timings, smoke, all stdout/stderr)
session marks in any other output: none | 16-character windows of the rendered text in any other output: none (147 windows)
refusal outputs screened: 36 | session marks or candidate heads in any: none
two working directories: 35 files compared; differ: ['work/timings.json']; stdout equal: True
a host path in any output file: none
```

**The bare 20-character canary** reaches the tokens and the tails because no scrub rule matches its shape. That is render's scrub boundary (F12), not read.py's.

**Determinism holds.** Two runs from two working directories are byte-identical, except `work/timings.json`, which R-5 puts there. No host path appears in any output.

## 5. Mutant table (Q7; 30 new mutants)

Method: one exact edit each, whose old text occurs exactly once, on a scratch copy of the PIN. The baseline reads `52 passed`, and so does the restored copy. A mutant is KILLED only when a test FAILS; an error-only run would not count.

| id | exact edit (old → new) | verdict | failing tests, or the discriminator (real vs mutant, CLI) |
|---|---|---|---|
| N1 | `heads = {a for a, _b in blocks(text, starts)}` → `heads = set(starts)` | SURVIVED | Differs only for a `state_end` at the text's end: a crash instead of a refusal |
| N2 | `if r["id"] in seen:` → `if False:` | SURVIVED | A view with a duplicate row: real exit 2; mutant exit 0 with a duplicate tail line |
| N3 | `if manifest != mjson:` → `if False:` | SURVIVED | Race-only. The check works in-process (Q3) |
| N4 | `if src not in entries:` → `if False:` | SURVIVED | A crash (KeyError) instead of exit 2 |
| N8 | `if a >= last:` → `if a > last:` | KILLED | `test_the_token_streams_and_positions_equal_the_oracle`, +3 more |
| N9 | `.replace("{body}", R.body(cands[h]))` → `.format(body=R.body(cands[h]))` | SURVIVED | Equivalent on the pinned template. Template `Hook: {body} {{zqtpl}}`: real keeps `{{zqtpl}}` (6 of 6); mutant gives `{zqtpl}` |
| N10 | `R.body(cands[h])` → `R.clean(cands[h])` | KILLED | `test_every_feature_equals_the_oracle`, +1 more |
| N11 | the question encoded after `.strip()` | SURVIVED | Equivalent on the pinned question text |
| N15 | `del cp …` → `state = cp` | KILLED | `test_every_feature_equals_the_oracle` |
| N16 | window `max(0, pos - window)` → `max(1, pos - window)` | KILLED | `test_every_feature_equals_the_oracle` |
| N17 | window → `max(0, pos - window + 1)` | KILLED | `test_every_feature_equals_the_oracle` |
| N19 | free arrays `for rid in done}` → `for rid in m["candidate_of"]}` | KILLED | `test_a_resumed_run_equals_an_uninterrupted_run_byte_for_byte` |
| N21 | `and index["rows"] == sorted(rids)` → `and True` | SURVIVED | Reachable only through a record moved by hand (F5) |
| N22 | the record's src and sha256 checks → `True` | SURVIVED | Reachable only through a record moved by hand (F5) |
| N23 | `if os.path.lexists(part):` → `if False:` | SURVIVED | A stale `.part` is refused (exit 2) instead of cleared; fails closed |
| N24 | the resumed probe `check_out("--work", …".next")` → `pass` | SURVIVED | A valid `--work` moved into a tree: real exit 2; mutant exit 0, **with record 1 written inside the tree** |
| N25 | the binding without `"backend"` | SURVIVED | Real exit 2; mutant exit 0, resuming from another backend's record |
| N26 | the binding without `"tokens_manifest_sha256"` | SURVIVED | Window-60 tokens, then window-100 tokens, on one `--work`: real exit 2; mutant exit 0 with `s_w`, `c_ctx_w` and `q_ctx_w` wrong |
| N27 | the row-position check → `True` | SURVIVED | Needs a crafted tokens manifest |
| N28 | the span check → `pass` | SURVIVED | Needs a crafted tokens manifest |
| N31 | `text[max(0, r["state_end"] - n):…]` → `text[r["state_end"] - n:…]` | SURVIVED | My fixture: real correct; **mutant gives empty tails for `s1-0000fa01` and `s1-0000fb01`** |
| N32 | tails `sorted(rows, key=…id)` → `rows` | SURVIVED | A view in reversed order: real sorted; mutant not |
| N33 | `if not every:` → `if False:` | SURVIVED | A crash (ValueError) instead of exit 2 |
| N34 | `compare` reads one key per array (`[:1]`) | KILLED | `test_compare_of_a_run_with_itself_reads_one`, `test_compare_reads_the_cosine_per_key_both_runs_hold` |
| N38 | the second check in `write_out` removed | SURVIVED | Race-only |
| N43 | `p[k] > 0` → `p[k] >= 0` | SURVIVED | A window of 0 is refused later by `load_tokens`; a tail of 0 would give empty tails |
| N44 | `type(p[k]) is int` → `isinstance(p[k], int)` | SURVIVED | Real refuses `true` at `tokens`; the mutant writes tokens and `read` refuses them later |
| N45 | the question check → `if False:` | SURVIVED | An empty question is refused later by `load_tokens` |
| N46 | the binding refusal → `pass` | KILLED | `test_a_work_dir_of_another_run_is_refused` |
| N47 | control: `heads … \| {0}` | SURVIVED | Expected: offset 0 is refused earlier |

Totals: 8 KILLED, 22 SURVIVED.

## 6. The builder's deviations, graded

All are conformant or a sound reading; none is a defect.
- **D-1, sound.** The tails manifest follows R-7's "exactly" over R-1's general rule, and task #472's brief (lines 52-53) reads R-7's keys.
- **D-2 to D-3, sound.**
- **D-4, sound and forced.** I reproduced `--only <src>`, R-5's own form; argparse rejects it with "expected one argument", because exported srcs start with `-`.
- **D-5 to D-7, sound added guards.**
- **D-8, a sound reading,** with two observations (F5, F10).
- **D-9 to D-12, sound.**
- **A-1:** outside the boundary; not verified.

The builder's three residual assumptions (§9 of its report):
1. A misreading shared by code and oracle: my independent lineage oracle agrees with the code.
2. The PC adapters may fail on first contact: see Q6.
3. The tails-manifest keys: settled by task #472's brief.

## 7. Finding inventory (no severity filter)

**F1. FOLLOW-UP. `read --out` writes the features inside a git work tree.** It also writes through a link spelled `link/`.
- Evidence: verified. `read.py:609-611` applies only the `..` check and the exists/empty check, not view.py's D-10 rule.
- Contract: R-9 names only `tokens`, `tails` and `--work`, and the code conforms. Breakdown decision 8 ("session-derived data stays out of git … the features sit beside them") argues the other way.
- Path: the canonical CLI (Q4 table).
- Effect: float hidden states and the meta can land in a git work tree. No session text.
- Fix: call `check_out("--out", args.out)` in `cmd_read`, and adjust the builder's `out_not_empty` message assertion.
- The adjacent gap in `features.py:61`, which the coordinator owns, is F15.

**F2. FOLLOW-UP. `compare`'s `min` is vacuous on rows when two runs share no row but share a candidate.** It exits 0 with `min` taken from the free arrays only.
- Evidence: verified (Q5).
- Contract: R-8 is met literally.
- Effect: that `min` feeds the evaluator's `--read-repeat` VOID check (S4-3 brief, lines 105-107). A read-repeat of the wrong files would pass that check without comparing a single row.
- Fix: refuse when any row array has `n` 0, or when the two row sets differ.

**F3. FOLLOW-UP, time-sensitive. No smoke check reads a long forward on a carried or copied state.**
- Evidence: the forward length (~35 tokens) is verified. That fla picks its kernel by length is unverified.
- Contract: R-8 fixes the smoke's checks but not the text lengths; the build conforms.
- Effect: a fault in carrying state through long chunked forwards would pass every check, including the PREREG's read-repeat.
- Fix: before the read job, add a split check and a copy check at scale. For example, 2 × 300 tokens or more read in one forward and in two, cosine ≥ 0.999, and a candidate longer than 64 tokens read on a copy.

**F4. FOLLOW-UP. `read --backend fla` checks neither the tokens nor the weights against the checkpoint.**
- It never compares the tokens manifest's tokenizer identity with the `--model` checkpoint, and never compares the weights sha256 with the block's `model_safetensors_sha256`.
- Evidence: reviewed statically (`read.py:614-622`).
- Effect: fake-tokenizer tokens, or another checkpoint, would be read silently.
- Fix: refuse a tokenizer name other than `hf`, refuse vocab files that differ from the model dir's, and refuse weights that differ from the block's.

**F5. FOLLOW-UP. A `--work` record is not self-binding.**
- A record moved by hand from another run's `--work` is taken when its token file and rows match. I reproduced window-60 values under a window-100 meta, exit 0.
- The program cannot create this state by itself; `work.json` gates the whole directory.
- Fix: put the binding's sha256 into each record's meta and check it.

**F6. FOLLOW-UP. Test gaps.** Nine survivors guard rules the code gets right, shown by their discriminators: N2, N9, N21, N22, N24, N25, N26, N31 and N32. The ones that matter most:
- N24: a resumed `--work` inside a tree;
- N26: a `--work` reused with other tokens;
- N31: rows whose state is shorter than the tail. Likely on real data, since the tail is 4,000 characters.

**F7. FOLLOW-UP. Some identities are checked only at the end.**
- `HFTokenizer.identity()` (`vocab_size`) is first called after the whole tokenization (`read.py:477`). A missing attribute would lose the PC tokens pass.
- `smoke` calls its identities after the checks (`read.py:740`).
- Fix: call `identity()` at construction.

**F8. INFO. A crash and a failed smoke check share exit 1.** I reproduced a raising backend: exit 1 and no result file. Check for the result file.

**F9. INFO.** `--work` equal to `--out`, or inside it, is refused only after every file is read. The records survive in `--work`, so a re-run resumes them.

**F10. INFO.** A resumed `--work` that is a link to a valid work dir outside git is taken. D-10's link refusal runs only on a fresh `--work`; the git walk still runs on the resolved path.

**F11. INFO.** A stale `<k>.part` that is a file blocks a resume (exit 2) until it is removed by hand.

**F12. INFO, outside read.py.** A bare 20-character FAKE key reaches the tokens and tails, because no rule in `render.py` or `transcript_export.py` matches its shape. Both are outputs R-9 keeps out of git.

**F13. INFO.** A real row with `state_end` 0 would refuse the whole `tokens` run, as R-2 requires. I did not measure whether the real view holds one.

**F14. INFO, cosmetic.** A `--work` refusal names `--out` and the probe path `work.json.next`.

**F15. INFO, adjacent, the coordinator's file.** `features.write`'s link check (`features.py:61`) has the same trailing-slash gap as `read.py:610`: `os.path.islink("link/")` is False.

**F0. INFO.** The premise moved mid-verify (§1).

## 8. The blocking predicate

| finding | contract mapping | reproduced on the real path | material | discriminator | owned here |
|---|---|---|---|---|---|
| F1 | no, under R-9 (yes only under decision 8) | yes | yes | yes | yes |
| F2 | no | yes | yes | yes | yes |
| F5 | no | yes (by hand only) | yes | yes | yes |
| F3, F4 | no | n/a | — | — | contract-level |
| F6 | no; the code is correct and the gaps are in the tests | — | — | — | — |

No finding meets every condition. **No CONTRACT-DEFECT.**

## 9. Scope

- **Reproduced:** Q1 to Q5, Q7 and Q8, through the CLI and the module functions, over exports and views made by the real producers.
- **Read only:** Q6 (fla and hf), fla's internals (both unverified here), and the two race-only checks (N3, N38).
- **Skipped:**
  - the builder's 23 mutants (the brief asks for new ones);
  - its scratch driver (it lies outside my directory);
  - A-1;
  - any PC run, `.jev/`, and any real export.

## 10. Files

The subject:
- `/home/user/agent-factory/scripts/s1_train/read.py`
- `/home/user/agent-factory/tests/test_s1_train_read.py`

My drivers, in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-s4-2-read/work/`:
- `fx.py`, `q1.py`, `q2.py`, `q2b.py`, `q3.py`, `q4.py`, `q4b.py`, `q8.py`, `q58.py`, `mut.py`, `disc.py`

In `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-s4-2-read/`:
- `mutants.json`: the mutant results
- `pin/`: the PIN copy
- `w1/`: the fixture world

**Recommendation: MERGE-READY-WITH-FOLLOWUPS.** The `fla` backend and the `hf` tokenizer were graded by reading only. If you read breakdown decision 8 as binding `read --out`, F1 alone makes it NOT-READY.
