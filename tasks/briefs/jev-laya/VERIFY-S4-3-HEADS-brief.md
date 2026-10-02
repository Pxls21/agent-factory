# VERIFY-S4-3-HEADS (task #472): the adversarial verify of the heads and the one evaluator

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: daa20757 (the landing on origin; full id in the premise).
Report: your FINAL MESSAGE is the report, whole. The harness may refuse a report-file Write from a subagent ("Subagents
should return findings as text"); never route around a refusal. The coordinator saves it as
`tasks/briefs/jev-laya/VERIFY-S4-3-HEADS-report.md`. Keep working notes in your own scratch directory. Do NOT spawn
subagents. Touch NO tracked file.

## THE SUBJECT

The landing daa20757 added `scripts/s1_train/heads.py` (340 lines), `scripts/s1_train/evaluate.py` (640 lines),
`tests/test_s1_train_heads.py` (931 lines, 51 tests: 38 pure, 13 with torch in the Laya venv) and the build lane's report
`tasks/briefs/jev-laya/S4-3-HEADS-report.md`, and amended `docs/research/findings/s1-train/PREREG-441.md` (its 11:0xZ
AMENDED paragraph and §3's family A row; the §8 block is unchanged). The coordinator changed one thing in the lane's
code before the landing: `evaluate.py`'s `DEVIATIONS` became `[]` (with a comment), because the amendment made §3 name
the same-state mask the code applies; the report's last section, "Coordinator's harvest notes", says so.

**The frozen contract is the AMENDED `docs/research/findings/s1-train/PREREG-441.md` at the PIN (§3, §4, §5, §8; the
amendment freezes the report's §2 readings G-1 to G-11), with `tasks/briefs/jev-laya/S4-3-HEADS-brief.md` (E-1 to E-9)
where the pre-registration is silent.** Attack the code against THOSE, never against the builder's own tests or report.
Grade each of the report's discrepancies, gap readings and findings (its §2 and §8: D-1, G-1 to G-11, N-1 to N-3, F-1,
F-2) as contract-conformant, a sound reading of an open point, or a defect.

Why it matters: task #441's 220 held-out rows give ONE claim, and this code alone turns the features into the verdict.
A held-out row that reaches a fit, the choice or a threshold; a McNemar or bar that is off by one; a control that can
never fire or fires on a sound run; a claim made without its test: any of these mints a false verdict that nothing
downstream can catch. The real features do not exist yet; the evaluator first runs on them once, on the PC.

**Round table (D-115).** Round 1: this landing. No earlier round.

## QUESTIONS (answer each with evidence; a question is not a claim)

**Q1. The held-out wall.** Trace every path a held-out row's label, features or probability can take: the folds, the
standardization statistics, every fit, the out-of-fold probabilities, the threshold, the choice, C1, C1b, C2, C3, the
word-overlap threshold. Can a held-out row's label or vector influence anything chosen before the held-out score is
read? Build the shapes that would show it (a held-out row whose kind has the only label of its value, a planted label
leak) and run them.

**Q2. §3, the configurations, the folds and the fits.** Are the 20 configurations exactly the block's grid, in its
order, with the block's values (and nothing else) reaching each fit? Are the folds each kind's training rows sorted by
(time, id) and cut into 5 contiguous parts, fold k every kind's part k? Is family A the amended loss (the same
candidate OR the same state masked out of a yes row's denominators, in both directions; the BCE over every batch row;
`exp(t)` at most the block's max)? Are B and C the stated logistic regression (λ‖w‖², L-BFGS 200 steps) and MLP? Is
each held-out probability the mean of the five fold models'?

**Q3. §3's threshold and choice.** The candidates (0, 1 and the midpoints), the accuracy at a threshold (a row is yes
when its probability is at least τ), each tie rule, the choice (out-of-fold rows right, then the lower log loss, then
the earlier configuration). Find any input where the code's choice differs from the rule's.

**Q4. §4, the bar.** The kind rule from the training rows' majority per kind; the 178 check; McNemar's b and c and its
exact one-sided tail; PASS, NOT SHOWN and FAILED at every boundary (178 and 179 right; p just below and at 0.05). Check
McNemar against an independent computation (your own exact binomial, not the code's).

**Q5. §5, the controls and the verdict.** C1 (the labels permuted inside each kind, the whole procedure, seeds 1 to 3;
VOID at two seeds meeting the PASS rule), C1b, C2 (A: `s` zeroed after standardization; B: `c_free`; C: `q_free`), C3
(the short-window arrays); the two claims; VOID on a read repeat below 0.999 and on two records that differ; INCOMPLETE
without `--read-repeat`. Can a control be silently skipped, run on the real labels, or scored on permuted held-out
labels? Is F-1 a defect of the code or a property of the pre-registered control?

**Q6. E-1, the inputs.** Every check before any fit: the block's values and types, the view's rows and counts, the
features (every byte, the block on BLOCK_KEYS, a vector for every row and candidate), the tails, the read repeat. Build
each corrupted input and show its refusal (exit 3, before a fit), or show one that passes and is scored.

**Q7. The record and the boundary.** Sorted keys, no clock, no host path, no session text (a candidate, a tail); the
stdout line; `--twice` comparing two whole evaluations; `--out` never written over. Does any refusal reason carry
session text?

**Q8. The tests.** Is any test a mirror of the code it tests? Is the planted-signal fixture strong enough to tell a
working procedure from a broken one, and is the no-signal fixture able to fail? Run NEW mutants (not the builder's 31;
one exact edit each, on a scratch copy, the baseline green first) on Q1 to Q7, and name each survivor.

## EVIDENCE DEMANDS

1. Premise: re-run the block below at your HEAD; on any difference, stop and report CONTRACT-INVALID with the
   differing lines.
2. The builder's tests at the PIN, twice: `bash scripts/test_summary.sh tests/test_s1_train_heads.py --basetemp <scratch dir>/bt`
   (paste each `pytest-summary:` line) and `bash scripts/pc_suite.sh set-id -- tests/test_s1_train_heads.py`.
3. Every claim reproduced through the real code path (the CLI, or the module functions on synthetic features written
   by `scripts/s1_train/features.py`), with the command and its output pasted. Torch runs in the Laya venv
   (`/root/venv-laya-probe/bin/python`), as the test file does.
4. The mutant table: each mutant's exact edit, the tests that failed, the survivors named.
5. Every observation reported, with no severity filter. Then the blocking predicate: a finding BLOCKS only when it
   shows the verdict or a claim can be wrong (a held-out row that reaches a fit, a choice or a threshold; a wrong count,
   McNemar tail, bar or tie rule; a control that cannot fire, fires on a sound run by the code's fault, or runs on the
   wrong labels or inputs; a claim without its test; a corrupted input that is scored), session text in the record, or
   a contradiction of the amended pre-registration. Everything else is a follow-up.
6. A gate recommendation: MERGE-READY, MERGE-READY-WITH-FOLLOWUPS, NOT-READY or CONTRACT-INVALID. The coordinator owns
   the gate.

## STANDING RULES

No outward-facing action (no push, PR or comment); no network; no PC bridge. Never commit, stash, checkout or reset in
`/home/user/agent-factory`, and never write a tracked file there: make scratch copies (`git archive daa20757` into
your scratch directory) for mutants and fixtures. Never read `.jev/`, the coordinator's scratchpad, `/root/.codiv/`,
`.pc-bridge.env`, any `*.env`, the pseudonym key under `/root/.config/session-export/`, any real export, or a real
transcript under `/root/.claude/projects/`. Long commands in ONE foreground call; no background job. Never `cd` at a
command's top level (wrap it: `( cd <dir> && ... )`). A pytest `--basetemp` parent must exist first. Every test run with
`PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1`, no `-n`; set `COLUMNS=1000` when a driver reads
pytest's short summary. Another lane (VERIFY-S4-2-READ, on `scripts/s1_train/read.py`) works in the same tree; it
touches no tracked file. The premise names the files that matter, and a change to any of them is a stop-and-report.

## PREMISE — MEASURED at authoring (2026-10-02 11:1xZ, /home/user/agent-factory@daa20757)

Re-run each command at your HEAD; its output must match.

```
$ git rev-parse --verify daa20757^{commit}
daa2075724b44eef530d4e3c468ec2077a34d5c6
$ git merge-base --is-ancestor daa20757 HEAD && echo the PIN is an ancestor of HEAD
the PIN is an ancestor of HEAD
$ git log -1 --format=%s daa20757 | cut -c1-120
Task 472 landed, gated pending verify: the heads and the one evaluator of the first S1 training; the pre-registration am
$ git diff --stat daa20757 HEAD -- scripts/s1_train tests/test_s1_train_heads.py tests/test_s1_train_features.py tasks/briefs/jev-laya/S4-3-HEADS-brief.md tasks/briefs/jev-laya/S4-3-HEADS-report.md docs/research/findings/s1-train/PREREG-441.md tasks/s1-heads-breakdown.md | wc -l
0
$ git show --stat --format= daa20757 | tail -7
 docs/research/findings/s1-train/PREREG-441.md |  13 +-
 scripts/s1_train/evaluate.py                  | 640 ++++++++++++++++++
 scripts/s1_train/heads.py                     | 340 ++++++++++
 tasks/briefs/jev-laya/S4-3-HEADS-report.md    | 281 ++++++++
 tests/test_s1_train_heads.py                  | 931 ++++++++++++++++++++++++++
 todo/BUILD-TASKLIST.md                        |   2 +
 6 files changed, 2206 insertions(+), 1 deletion(-)
$ sha256sum scripts/s1_train/features.py scripts/s1_train/heads.py scripts/s1_train/evaluate.py tests/test_s1_train_heads.py tasks/briefs/jev-laya/S4-3-HEADS-brief.md tasks/briefs/jev-laya/S4-3-HEADS-report.md docs/research/findings/s1-train/PREREG-441.md | awk '{print substr($1,1,16), $2}'
6a32c42d16299365 scripts/s1_train/features.py
f3187e1b30a9dbe9 scripts/s1_train/heads.py
aa76246b0237f43d scripts/s1_train/evaluate.py
8d19d90ed7e92dc6 tests/test_s1_train_heads.py
26724322d9011c76 tasks/briefs/jev-laya/S4-3-HEADS-brief.md
b220eb2ed61983d0 tasks/briefs/jev-laya/S4-3-HEADS-report.md
f596ffee74ee9155 docs/research/findings/s1-train/PREREG-441.md
$ git diff daa20757~1 daa20757 -- docs/research/findings/s1-train/PREREG-441.md | grep -c '^[-+][^-+]'
12
$ python3 -c "import re,hashlib; t=open('docs/research/findings/s1-train/PREREG-441.md',encoding='utf-8').read(); b=re.findall(r'\`\`\`json\n(.*?)\n\`\`\`', t, re.S); print(len(b), hashlib.sha256(b[0].encode()).hexdigest()[:16])"
1 43580dab3a486cd3
$ wc -l scripts/s1_train/heads.py scripts/s1_train/evaluate.py tests/test_s1_train_heads.py
  340 scripts/s1_train/heads.py
  640 scripts/s1_train/evaluate.py
  931 tests/test_s1_train_heads.py
 1911 total
$ grep -n '^def \|^class \|^DEVIATIONS\|^BLOCK_KEYS' scripts/s1_train/heads.py scripts/s1_train/evaluate.py
scripts/s1_train/heads.py:16:class Refused(Exception):
scripts/s1_train/heads.py:20:class HeldOut(Exception):
scripts/s1_train/heads.py:31:def is_int(v, low):
scripts/s1_train/heads.py:35:def is_real(v):
scripts/s1_train/heads.py:40:def _pos(v):
scripts/s1_train/heads.py:44:def _nonneg(v):
scripts/s1_train/heads.py:48:def _rate(v):
scripts/s1_train/heads.py:52:def _int(low):
scripts/s1_train/heads.py:56:def _list(ok):
scripts/s1_train/heads.py:60:def _field(d, key, ok, where):
scripts/s1_train/heads.py:66:def configurations(grid):
scripts/s1_train/heads.py:99:def when(text):
scripts/s1_train/heads.py:110:def folds(rows, k):
scripts/s1_train/heads.py:135:class Data:
scripts/s1_train/heads.py:161:def _torch():
scripts/s1_train/heads.py:168:def _no_heldout(data, ids, what):
scripts/s1_train/heads.py:174:def _batches(torch, n, batch, epochs, seed):
scripts/s1_train/heads.py:185:def _inputs(torch, data, fit, idx):
scripts/s1_train/heads.py:193:def _tower(nn, d, cfg):
scripts/s1_train/heads.py:202:def _pair(torch, model, s, c, cfg):
scripts/s1_train/heads.py:209:def pair_loss(torch, L, y, a, b, cand, state):
scripts/s1_train/heads.py:227:def train(config, data, labels, ids, fold, variant="full"):
scripts/s1_train/heads.py:290:def _probs(fit, data, ids):
scripts/s1_train/heads.py:309:def score(fit, data, ids):
scripts/s1_train/heads.py:315:def score_heldout(fit, data, ids):
scripts/s1_train/heads.py:323:def fit_fold(config, data, labels, fold, variant="full"):
scripts/s1_train/heads.py:332:def cross_validate(config, data, labels, variant="full"):
scripts/s1_train/evaluate.py:38:BLOCK_KEYS = ("inputs", "rows", "features", "cv", "grid", "bar", "controls", "word_overlap")
scripts/s1_train/evaluate.py:45:DEVIATIONS = []
scripts/s1_train/evaluate.py:48:def _sha(b):
scripts/s1_train/evaluate.py:52:def _read(path, what):
scripts/s1_train/evaluate.py:60:def _no_constant(name):
scripts/s1_train/evaluate.py:64:def _json(raw, what):
scripts/s1_train/evaluate.py:71:def _lines(raw, what):
scripts/s1_train/evaluate.py:85:def prereg_block(text):
scripts/s1_train/evaluate.py:96:def _at(block, path):
scripts/s1_train/evaluate.py:105:def _need(block, path, ok, what):
scripts/s1_train/evaluate.py:112:def _hex64(v):
scripts/s1_train/evaluate.py:116:def _alpha(v):
scripts/s1_train/evaluate.py:120:def check_block(block):
scripts/s1_train/evaluate.py:148:def load_view(view_dir, block):
scripts/s1_train/evaluate.py:178:def load_features(features_dir, block, rows):
scripts/s1_train/evaluate.py:208:def load_tails(tails_dir, block, rows):
scripts/s1_train/evaluate.py:236:def load_read_repeat(path):
scripts/s1_train/evaluate.py:245:def kind_rule(rows):
scripts/s1_train/evaluate.py:261:def words(text, n):
scripts/s1_train/evaluate.py:266:def jaccard(a, b):
scripts/s1_train/evaluate.py:272:def load(prereg, view, feats, tails, read_repeat=None):
scripts/s1_train/evaluate.py:306:def threshold(probs, labels):
scripts/s1_train/evaluate.py:319:def log_loss(probs, labels):
scripts/s1_train/evaluate.py:326:def auc(scores, labels):
scripts/s1_train/evaluate.py:337:def metrics(ids, labels, kinds, scores, called, hard):
scripts/s1_train/evaluate.py:364:def mcnemar(a_right, b_right):
scripts/s1_train/evaluate.py:377:def _mc(m, b_is):
scripts/s1_train/evaluate.py:382:def _frac(x):
scripts/s1_train/evaluate.py:386:def meets_pass_rule(block, right, mc):
scripts/s1_train/evaluate.py:392:def verdict(block, right, mc, c1_passing, read_repeat_min, twice):
scripts/s1_train/evaluate.py:417:def choose(configs, results, labels):
scripts/s1_train/evaluate.py:436:def judge(rows, ids, probs, tau):
scripts/s1_train/evaluate.py:446:def permute_within_kind(rows, seed):
scripts/s1_train/evaluate.py:461:def permute_all(rows, seed):
scripts/s1_train/evaluate.py:469:def _labels_note(rows, labels):
scripts/s1_train/evaluate.py:476:def _procedure(inp, configs, labels):
scripts/s1_train/evaluate.py:483:def _control(inp, labels, configs, rule_right, model_right, variant="full"):
scripts/s1_train/evaluate.py:499:def evaluate(inp, only=None):
scripts/s1_train/evaluate.py:555:def claims(block, vs_full):
scripts/s1_train/evaluate.py:566:def _dumps(record):
scripts/s1_train/evaluate.py:570:def _check_out(out):
scripts/s1_train/evaluate.py:579:def run(args):
scripts/s1_train/evaluate.py:602:def explore(args):
scripts/s1_train/evaluate.py:611:def main(argv=None):
$ grep -c '^def test_' tests/test_s1_train_heads.py
41
$ bash scripts/pc_suite.sh set-id -- tests/test_s1_train_heads.py
1 files set=e8d6713191fd
$ mkdir -p /tmp/p472v && PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1 bash scripts/test_summary.sh tests/test_s1_train_heads.py --basetemp /tmp/p472v/bt 2>&1 | grep pytest-summary | sed -E 's/ in [0-9.]+s.*//'; rm -rf /tmp/p472v
pytest-summary: 51 passed
```
