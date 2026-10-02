# VERIFY-S4-2-READ (task #471): the adversarial verify of the S1 reading program

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: b9f835de (the landing on origin; full id in the premise).
Report: your FINAL MESSAGE is the report, whole. The harness may refuse a report-file Write from a subagent ("Subagents
should return findings as text"); never route around a refusal. The coordinator saves it as
`tasks/briefs/jev-laya/VERIFY-S4-2-READ-report.md`. Keep working notes in your own scratch directory. Do NOT spawn
subagents. Touch NO tracked file. Planting FAKE keys and markers in fixtures is defensive testing of the owner's own
data path (D-118: the scrub stays), authorized by the owner.

## THE SUBJECT

The landing b9f835de added `scripts/s1_train/read.py` (789 lines), `tests/test_s1_train_read.py` (870 lines, 52 tests)
and the build lane's report `tasks/briefs/jev-laya/S4-2-READ-report.md` (the lane's own report; the coordinator replaced
three citations of a local commit id before the push, nothing else).

**The frozen contract is `tasks/briefs/jev-laya/S4-2-READ-brief.md` at the PIN (its rules R-1 to R-10 and its evidence
demands), with `docs/research/findings/s1-train/PREREG-441.md` §2 and §8 and `tasks/s1-heads-breakdown.md`'s pinned
decisions.** Attack the code against THOSE, never against the builder's own tests or report. The builder's report names
its discrepancies and deviations (its section 7: D-1 to D-12, A-1) and its residual assumptions (section 9). Grade each
as contract-conformant, a sound reading of an open point, or a defect.

Why it matters: task #441 trains small heads on these features, and its 220 held-out rows give ONE claim. A readout
taken at the wrong position, a candidate read on the state the stream goes on with, a window that is not the last
tokens before the row, or a free read that is not from the zero state would train the heads on the wrong question, and
nothing downstream could tell. The `fla` backend and the `hf` tokenizer have never run (no torch in the sandbox); the
PC's smoke job and tokens step run them first, so their code is graded by reading, against the measured loader.

**Round table (D-115).** Round 1: this landing. No earlier round.

## QUESTIONS (answer each with evidence; a question is not a claim)

**Q1. R-3 and R-4, the tokens.** Is each non-empty block tokenized on its own, and is a row's position the number of
tokens of the blocks before its `state_end`, for every shape: two rows at one `state_end`, rows of two files, a
`state_end` at the first non-empty block (refused?), a block of one character, multibyte text across a block's end, a
candidate over render's cap, the stream cut at the last row's `state_end` (nothing after it read)? Is the candidate
block exactly `features.candidate_block` with `{body}` replaced by `render.body` of the candidate, and the question
block exactly `features.question_block`?

**Q2. R-5, the read.** Does every forward end at a row position, so that `s` is the readout at the row's last token?
Is the candidate (then the question) read on a COPY that is then dropped, so no later readout depends on it? Is the
window the last `short_window_tokens` tokens before the position, read from the zero state, with the candidate and the
question after it? Are `c_free` and `q_free` read from the zero state, one per distinct candidate? Does `--segment`
change any readout of the fake backend (it must not)? With `--only` and `--work`: does a resumed run equal an
uninterrupted one in every byte, and can a stale `.part`, a work record of another run, another file or another row
set, or a `work.json` of another backend or segment, ever be taken as this run's?

**Q3. R-2, the inputs.** For each check (the three sha256s of the block's `inputs`, the export's manifest re-read, each
file's render against `summary.json`'s stream sha256, each row's `state_end`, each row's `candidate_sha256`): build the
corrupted input through the real producers and show the refusal, or show the corrupted input that passes and writes
features or tokens.

**Q4. R-9, the outputs.** `..`, a symbolic link (to a directory, a file, dangling), an output inside a git work tree
(through a `.git` directory and a `.git` file), a missing output whose nearest existing parent is in a tree, a
non-empty output; for `tokens`, `tails`, `--work` (a fresh one and a resumed one) and `read --out`. Can any of these put
token ids, tails or readouts inside a git work tree, or over another output?

**Q5. R-7 and R-8.** Is each tail the last `state_tail_chars` CHARACTERS of the rendered text before `state_end`? Does
the tails manifest carry exactly the keys R-7 lists (the builder's D-1)? Does `compare` take the cosine over the keys
both runs hold, and refuse two runs with none in common? Can `smoke`'s copy check pass when `copy()` returns the same
object, or when the candidate read changes the original state? Can the split or head check pass on a broken readout?

**Q6. The `fla` backend and the `hf` tokenizer, by reading.** Compare `FlaBackend` and `HFTokenizer` line by line with
the loader and forward that ran on the PC (`docs/research/findings/j2b-variants/rwkv7_g0.py`: the load at 135-149, the
cached forward at 87-114) and with `docs/research/findings/j2b-variants/rwkv7-g0/2026-09-24-window2/README.md`. Is
`last_hidden_state[0, -1]` the hidden state after the model's last norm? Is `copy.deepcopy` of the cache a full copy
(the forward changes the cache in place)? Name every point where the first PC run can fail or, worse, run and read the
wrong thing, and say which of the smoke's three checks would catch it.

**Q7. The tests.** Is the oracle (`encode`, `fold`) independent of the code (no import, no shared helper that decides a
rule)? Is any test a mirror of the code it tests? Run NEW mutants (not the builder's 23; one exact edit each, on a
scratch copy, the baseline green first) on R-2 to R-9, and name each survivor.

**Q8. The boundary and determinism.** Does any stdout or stderr line, any refusal reason, `timings.json`, a manifest or
the features `meta` carry session text (the rendered text, a candidate, a tail)? Does a planted FAKE key or a thinking
marker in the export reach any token file, tail or output? Are two runs byte-identical, from two working directories?

## EVIDENCE DEMANDS

1. Premise: re-run the block below at your HEAD; on any difference, stop and report CONTRACT-INVALID with the
   differing lines.
2. The builder's tests at the PIN, twice: `bash scripts/test_summary.sh tests/test_s1_train_read.py --basetemp <scratch dir>/bt`
   (paste each `pytest-summary:` line) and `bash scripts/pc_suite.sh set-id -- tests/test_s1_train_read.py`.
3. Every claim reproduced through the real code path (the CLI, or the module functions over exports the real exporter
   made from fixture transcripts and views `view.py` made), with the command and its output pasted.
4. The mutant table: each mutant's exact edit, the tests that failed, the survivors named.
5. Every observation reported, with no severity filter. Then the blocking predicate: a finding BLOCKS only when it
   shows a feature wrong (a readout at a position other than the row's `state_end`, or one that holds a token after
   it; a candidate or question read on the state the stream goes on with; a window or a free read not from the zero
   state; a wrong candidate or question block; an array whose keys are not its rows or candidates), an input check
   that passes a corrupted input and writes tokens or features, session text in an output other than a token or tail
   file, an output written inside a git work tree, or a contradiction of a frozen R-rule. Everything else is a
   follow-up.
6. A gate recommendation: MERGE-READY, MERGE-READY-WITH-FOLLOWUPS, NOT-READY or CONTRACT-INVALID. The coordinator owns
   the gate.

## STANDING RULES

No outward-facing action (no push, PR or comment); no network; no PC bridge. Never commit, stash, checkout or reset in
`/home/user/agent-factory`, and never write a tracked file there: make scratch copies (`git archive b9f835de` into
your scratch directory) for mutants and fixtures. Never read `.jev/`, the coordinator's scratchpad, `/root/.codiv/`,
`.pc-bridge.env`, any `*.env`, the pseudonym key under `/root/.config/session-export/`, any real export, or a real
transcript under `/root/.claude/projects/`; never run the exporter with `--known-values default`, nor
`scripts/known_values_check.py` with its default sources. FAKE strings for anything secret-shaped, built at run time,
never a literal; a test failure message names a canary, never its value. Long commands in ONE foreground call; no
background job. Never `cd` at a command's top level (wrap it: `( cd <dir> && ... )`). A pytest `--basetemp` parent
must exist first. Every test run with `PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1`, no `-n`; set
`COLUMNS=1000` when a driver reads pytest's short summary. The test file's output root comes from `tempfile.mkdtemp`:
set `TMPDIR` to a directory in your scratch directory. Another lane (task #472: `scripts/s1_train/heads.py`,
`scripts/s1_train/evaluate.py`, `tests/test_s1_train_heads.py`) may land while you work: never open its files; the
premise names the files that matter, and a change to any of them is a stop-and-report.

## PREMISE — MEASURED at authoring (2026-10-02 10:5xZ, /home/user/agent-factory@b9f835de)

Re-run each command at your HEAD; its output must match.

```
$ git rev-parse --verify b9f835de^{commit}
b9f835de6fa11524fc27915b20377379e8d8297f
$ git merge-base --is-ancestor b9f835de HEAD && echo the PIN is an ancestor of HEAD
the PIN is an ancestor of HEAD
$ git log -1 --format=%s b9f835de | cut -c1-120
Task 471 landed, gated pending verify: the reading program of the first S1 training (scripts/s1_train/read.py)
$ git diff --stat b9f835de HEAD -- scripts/s1_train tests/test_s1_train_read.py tests/test_s1_train_features.py tests/test_s1_train_view.py tasks/briefs/jev-laya/S4-2-READ-brief.md tasks/briefs/jev-laya/S4-2-READ-report.md docs/research/findings/s1-train/PREREG-441.md tasks/s1-heads-breakdown.md scripts/laya_ft/common.py scripts/laya_ft/build_s1.py scripts/session_export.py docs/research/findings/j2b-variants/rwkv7_g0.py | wc -l
0
$ git show --stat --format= b9f835de | tail -5
 scripts/s1_train/read.py                  | 789 +++++++++++++++++++++++++++
 tasks/briefs/jev-laya/S4-2-READ-report.md | 307 +++++++++++
 tests/test_s1_train_read.py               | 870 ++++++++++++++++++++++++++++++
 todo/BUILD-TASKLIST.md                    |   2 +
 4 files changed, 1968 insertions(+)
$ sha256sum scripts/s1_train/__init__.py scripts/s1_train/features.py scripts/s1_train/render.py scripts/s1_train/view.py scripts/s1_train/read.py tests/test_s1_train_read.py tasks/briefs/jev-laya/S4-2-READ-brief.md tasks/briefs/jev-laya/S4-2-READ-report.md docs/research/findings/s1-train/PREREG-441.md | awk '{print substr($1,1,16), $2}'
e3b0c44298fc1c14 scripts/s1_train/__init__.py
6a32c42d16299365 scripts/s1_train/features.py
901c086a6a90f90a scripts/s1_train/render.py
4629e0c720edaa82 scripts/s1_train/view.py
8af6a2bced1fef74 scripts/s1_train/read.py
ea91d683d53c384f tests/test_s1_train_read.py
20376c4823a3bb3f tasks/briefs/jev-laya/S4-2-READ-brief.md
4d8f0019cf7222ed tasks/briefs/jev-laya/S4-2-READ-report.md
07be205f4125eab8 docs/research/findings/s1-train/PREREG-441.md
$ wc -l scripts/s1_train/read.py tests/test_s1_train_read.py
  789 scripts/s1_train/read.py
  870 tests/test_s1_train_read.py
 1659 total
$ grep -n '^def \|^class ' scripts/s1_train/read.py
77:class Refused(Exception):
81:def sha256(data):
85:def _bytes(path, what):
93:def json_bytes(obj):
97:def u32(ids):
107:def ids_of(data, name):
117:def cosine(a, b):
126:def json_blocks(text):
143:def read_prereg(path):
176:def blocks(text, starts):
181:def read_inputs(view_dir, export_dir, p):
248:def _named(flag, out):
255:def check_out(flag, out):
265:def _put(out, name, data):
272:def write_out(flag, out, files):
286:class FakeTokenizer:
312:class HFTokenizer:
334:def tokenizer(name, model):
344:class FakeBackend:
378:class FlaBackend:
431:def make_backend(name, model):
441:def stream(tok, text, starts, last):
454:def cmd_tokens(args):
488:def load_tokens(tdir):
526:def forward(backend, state, ids, segment):
535:def read_file(backend, ids, rows, cand, q_ids, window, segment):
557:def open_work(work, binding):
574:def load_record(work, k, entry, rids):
590:def save_record(work, k, entry, vecs, forwards, dim):
606:def cmd_read(args):
680:def cmd_tails(args):
695:def cmd_compare(args):
715:def cmd_smoke(args):
752:def main(argv=None):
$ grep -c '^def test_' tests/test_s1_train_read.py
26
$ bash scripts/pc_suite.sh set-id -- tests/test_s1_train_read.py
1 files set=9b7b5a45ec51
$ mkdir -p /tmp/p471v && PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1 bash scripts/test_summary.sh tests/test_s1_train_read.py --basetemp /tmp/p471v/bt 2>&1 | grep pytest-summary | sed -E 's/ in [0-9.]+s.*//'; rm -rf /tmp/p471v
pytest-summary: 52 passed
```
