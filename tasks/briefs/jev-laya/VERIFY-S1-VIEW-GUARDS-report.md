> Coordinator note (2026-10-02 06:5xZ): the verifier's final message, saved whole. It cited two local commit ids (HEAD at its start and at its end); they are replaced here by their origin ids, be0d915a and 579ef6b0, because the push rewrites local ids. Nothing else is changed.

The D-9 survivors are now valid. On all 14 rebuilt shapes the PIN refuses with exit 2 and the intended reason, and each mutant fails with a traceback (exit 1). Every survivor except M34 is now shown to differ from the PIN.

# VERIFY-S1-VIEW-GUARDS (task #460): adversarial verify of the S1 view's guards

- **PIN:** `0555298e6c218a51374a52e7002a865ba18c3aba`. The premise matched at HEAD `be0d915a` (start). At HEAD `579ef6b0` (end) the PIN is still an ancestor and the premise files are unchanged.
- **Verifier:** sandbox Opus 5.5, no subagents, no network, no bridge.
- **Scratch directory:** `<W>` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vfy460-wKeKV0`.
- **Time:** the last `date -u` read `2026-10-02T06:39:04Z`. Two probe runs came after it.

## Gate recommendation

**NOT-READY, on one blocker: B1.** It rests on reproduced evidence only.

**B1:** D-10 says to refuse an `--out` that is a symbolic link, "to anything, an empty directory included". The code tests `os.path.islink(os.path.abspath(out))` (`view.py:381`). `abspath` resolves `..` by text, not by the filesystem. So when a symbolic link comes before `..` in the path, the check looks at the wrong entry. Example: `--out <dir>/hop/../link`, where `hop` is a link and `link` is a link to an empty directory.
- The kernel reports that `--out` is a link: `os.path.islink(out)` is `True`.
- The code's check reads `False`, so the view exits 0 and writes both outputs through the link into its target.
- No output can land inside a git work tree this way, because the git rule uses `realpath` and still refuses.
- A one-line correction inside the boundary refuses all three spellings and keeps `92 passed`.

Everything else is a follow-up or information. One question stays open (F1: the `toolUseID`s of prompt-time hooks). It needs a counts-only measure of the real export. Its answer can add a contract defect in D-8, but it does not change this verdict. If you rule B1's spelling outside D-10, the rest of the evidence supports MERGE-READY-WITH-FOLLOWUPS.

## Summary

- **D-8, the guards:** the code matches D-8 word for word on every shape I built through the real exporter. O5, O6, O7, O8 and q3b each drop under their guard and are counted once. Ids that meet two or three guards count once, under the first. No dropped id reaches `found`, label, split or any output.
- **Misses and false drops, all within D-8's literal wording:**
  - Duplicated call ids cause counted drops (F2).
  - A null call id causes an `own_result_in_state` drop (F3, the builder's open point).
  - A split prompt-time run whose hooks carry distinct or null `toolUseID`s is written with another hook's text in its state. That shape lies outside D-8's definition (F1, unverified on real data).
- **D-9:** four hand-made inputs still exit 1 (F4). The builder named one of them. One of the four leaves an empty `view.jsonl.part` in `--out`. The catch around `facts_of` makes a code defect read as an input refusal (I5).
- **D-10:** B1. The rest holds, including `.git` files, deep new paths and links in parent components. A residual race exists after the second check (F6). A bind mount is outside D-10's definition (I4).
- **D-11:** all three facts hold. A hard link is refused by the src check, not by the one-file check (I3).
- **Tests:** I ran 35 new mutants: 11 killed, 24 survived, 0 invalid.
  - All 24 survivors are test gaps; the code is right on each rule. 23 of them differ from the PIN on an input that holds their shape, and one (M34) is equivalent in effect.
  - The 14 D-9 survivors are catch classes that the builder's mutant set did not remove.
  - Two survivors (M42, M8) would each write a row that breaks the headline claim, and all 92 tests would stay green.
- **Normal behaviour:**
  - Round-1 fixture: `view.jsonl` is byte-equal to round 1's (`fe15dfc84d409d72`, 9 rows).
  - Two runs, another cwd, another code tree and Python 3.10 to 3.13 all give byte-identical outputs.

## 1. The premise (evidence demand 1): PASS

I re-ran every command of the brief's premise block at HEAD `be0d915a`. My scratch directory stood in for `/tmp/p460v`. Every output matched the brief line for line:

```
0555298e6c218a51374a52e7002a865ba18c3aba
the PIN is an ancestor of HEAD
Task #460 landed, gated pending verify: the S1 view's guards; the real run finds all 1,091 ids, drops none and repeats t
0
0
 scripts/s1_train/view.py    | 164 ++++++++---
 tests/test_s1_train_view.py | 664 +++++++++++++++++++++++++++++++++++++-------
 2 files changed, 686 insertions(+), 142 deletions(-)
e3b0c44298fc1c14 scripts/s1_train/__init__.py
901c086a6a90f90a scripts/s1_train/render.py
9ca2bece43af9a9f scripts/s1_train/view.py
668e4b46b7e241da tests/test_s1_train_view.py
   125 scripts/s1_train/render.py
   429 scripts/s1_train/view.py
  1360 tests/test_s1_train_view.py
  1914 total
67:VERSION = "s1-view-v2" … 411:def main(argv=None):   (all 14 grep lines equal the brief's)
57
1 files set=470c76f8303f
pytest-summary: 92 passed
75679ba5c0f7 tasks/briefs/jev-laya/S1-VIEW-GUARDS-report.md
ff5878312bf3 tasks/briefs/jev-laya/S1-VIEW-GUARDS-brief.md
85fdf2dbfb50 tasks/briefs/jev-laya/VERIFY-S3-5-VIEW-report.md
```

I read `pc_suite.sh` before running it: `set-id` is a local hash of the path list. It makes no bridge call and reads no env file.

At the end, HEAD was `579ef6b0`. The PIN is an ancestor, and the diff over the premise files (all but the test file) counts 0 lines. The test file had no committed change. Your announced test-only fix was still uncommitted in the main tree.

## 2. The builder's tests at the PIN (evidence demand 2)

From a `git archive 0555298e` copy (`<W>/pin`), with `TMPDIR=<W>/tmp`:

```
pytest-exit: 0
pytest-summary: 92 passed in 11.56s
run 1 rc=0
pytest-exit: 0
pytest-summary: 92 passed in 12.47s
run 2 rc=0
1 files set=470c76f8303f
```

## 3. The questions (my fixtures)

Every fixture follows the same path:
1. Raw records from the PIN test module's own builders (`Tape`, `success`, `cut_injection`).
2. The real exporter CLI (`init-key` FAKE key, a fixture repo, `--known-values key-only`).
3. A build written by `build_s1.write_split`.
4. The view CLI.

The harness is `<W>/h.py`. Each record order sits in its own transcript file.

### Q1. D-8, the guards, both ways

`( cd <W> && PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1 TMPDIR=<W>/tmp python3 q1.py )`

```
rc=0 stdout='s1-view: 22 build ids, 10 found, 0 not in the export, 0 ambiguous, 12 dropped by the guards; 18 files, 111 events, 87 blocks, 20712 characters rendered' stderr=''
not_found: {"ambiguous": 0, "carrier_truncated": 1, "not_in_export": 0, "own_result_in_state": 3, "same_call_hook_in_state": 8}
found: 10 split: {'heldout': 0, 'train': 10} label: {'false': 0, 'true': 10} carrier: {'hook_additional_context': 9, 'tool_result': 1}
OK  q3b              s1-1003b001 expect=carrier_truncated          got=carrier_truncated          state_event=3 unseen-in-state=[]
OK  o5               s1-10050a01 expect=written                    got=written                    state_event=3 unseen-in-state=[]
OK  o5               s1-10050a02 expect=same_call_hook_in_state    got=same_call_hook_in_state    state_event=6 unseen-in-state=[]
OK  o6               s1-10060a01 expect=own_result_in_state        got=own_result_in_state        state_event=3 unseen-in-state=[]
OK  o7               s1-10070a01 expect=written                    got=written                    state_event=4 unseen-in-state=[]
OK  o7               s1-10070a02 expect=same_call_hook_in_state    got=same_call_hook_in_state    state_event=7 unseen-in-state=[]
OK  o8               s1-10080a01 expect=same_call_hook_in_state    got=same_call_hook_in_state    state_event=3 unseen-in-state=[]
OK  otherevent       s1-100e0a01 expect=written                    got=written                    state_event=2 unseen-in-state=[]
OK  otherevent       s1-100e0a02 expect=written                    got=written                    state_event=6 unseen-in-state=[]
OK  empty            s1-100f0a01 expect=written                    got=written                    state_event=5 unseen-in-state=[]
OK  multi            s1-10100a01 expect=written                    got=written                    state_event=3 unseen-in-state=[]
OK  multi            s1-10100a02 expect=same_call_hook_in_state    got=same_call_hook_in_state    state_event=8 unseen-in-state=[]
OK  denysplit        s1-10110a01 expect=same_call_hook_in_state    got=same_call_hook_in_state    state_event=4 unseen-in-state=[]
OK  denyok           s1-10120a01 expect=written                    got=written                    state_event=2 unseen-in-state=[]
OK  g123             s1-10130a01 expect=same_call_hook_in_state    got=same_call_hook_in_state    state_event=4 unseen-in-state=[]
OK  g13              s1-10140a01 expect=same_call_hook_in_state    got=same_call_hook_in_state    state_event=5 unseen-in-state=[]
OK  dup_pre_result   s1-10150a01 expect=own_result_in_state        got=own_result_in_state        state_event=5 unseen-in-state=[]
OK  dup_post_hook    s1-10160a01 expect=same_call_hook_in_state    got=same_call_hook_in_state    state_event=7 unseen-in-state=[]
OK  ups_distinct     s1-10170a01 expect=written                    got=written                    state_event=3 unseen-in-state=['WIKI-HINT-DISTINCT-TOOLUSEID']
OK  ups_null         s1-10180a01 expect=written                    got=written                    state_event=3 unseen-in-state=['WIKI-HINT-NULL-TOOLUSEID']
OK  q2_null          s1-10190a01 expect=own_result_in_state        got=own_result_in_state        state_event=4 unseen-in-state=[]
OK  q2_null_ok       s1-101a0a01 expect=written                    got=written                    state_event=2 unseen-in-state=[]
partition: build_ids=22 found+not_found=22
label+split totals equal found: True
ALL AS EXPECTED
```

The record orders ("[Post X]" is a stamped hook_success plus hook_additional_context):

| File | Order | Result |
|---|---|---|
| o5 | call X; result X; [Post X] A; notification; [Post X] B | B dropped, same_call |
| o6 | call X; result X; [Pre X] | own_result |
| o7 | call A; call B; result A; [Post A] 1; result B; [Post A] 2 | 2 dropped, same_call |
| o8 | owner; UPS plain hook (id U, renders); notification; UPS stamp (id U) | same_call |
| q3b | call; result; a Post carrier the exporter cut | carrier_truncated |
| otherevent | call; [Pre X]; result; notification; [Post X] | both written (hookEvent differs) |
| empty | call; result; Post hook_success of X that renders `""`; notification; Post stamp | written |
| multi | [Post X] A; notification; call Y; result Y; [Post X] B | B dropped |
| denysplit | call Grep; Pre hook of X (renders); notification; stamped denial | same_call |
| denyok | call Grep; Pre nag; Pre hook; stamped denial | written |
| g123 | call; Pre hook (renders); result; cut Pre carrier (meets guards 1, 2, 3) | same_call, counted once |
| g13 | call; result; Post hook; notification; cut Post carrier (guards 1, 3) | same_call, counted once |
| dup_pre_result | call X; result X; text; call X again; [Pre X] | own_result (the first call's result) |
| dup_post_hook | call X; result X; Post hook X; text; call X again; result X; [Post X] | same_call (the first call's hook) |
| ups_distinct | owner; UPS plain hook (id U1); notification; UPS stamp (id U2) | written, other hook's text in state |
| ups_null | the same with `toolUseID` null on both | written, other hook's text in state |
| q2_null / q2_null_ok | see Q2 | own_result / written |

Answers:
- **The record orders O5 to O8 and q3b:** each drops under its guard, with the right count.
- **A hook of the carrier's call with another `hookEvent`:** kept (otherevent). D-8 matches `hookEvent`, so Pre hooks stay in a PostToolUse state; that is round 1's F4 question (I10).
- **A hook that renders `""`:** kept (empty).
- **A hook text that is not a JSON dict:** it cannot carry a `toolUseID`, so no guard can match it.
- **A run split by several non-hook events:** dropped (multi).
- **A tool_result carrier:** split, it is dropped; whole, it is written.
- **Duplicated call ids:** dropped under both guards, by D-8's literal wording (F2).
- **Two or three guards:** counted once, under the first (g123, g13).
- **Can a dropped id count as `found` or reach label or split?** No. `build_ids` equals `found` plus `not_found` (22 = 22), and the label and split totals equal `found`.
- **Outside D-8:** ups_distinct and ups_null are written with the other prompt-time hook's text in their state (F1).

### Q2. `own_result_in_state` with a null call id

The real exporter writes both shapes from raw records:
- a hook_additional_context with no `toolUseID`, giving a carrier whose call id is null;
- a tool_result block with no `tool_use_id`, giving `call_id: null`.

q2_null is a call, then a result with no id, then another call, then a stamped PreToolUse hook with no `toolUseID`. It is dropped as `own_result_in_state`, because `c == call_id` compares `None == None`. q2_null_ok is the same carrier with no such result before it, and it is written.

D-8's first guard says the call id is "not null"; its second guard does not say so. So the code is a sound literal reading of an open point. Its effect is a counted drop on a malformed transcript, never text in a state (F3). The harness always sets `tool_use_id`, and every one of the 3,468 real hook_additional_context records has the `toolUseID` key (key sets in S3-5-VIEW-brief). Their values are unmeasured.

### Q3. D-9: does every refusal exit 2?

`( cd <W> && … python3 q3.py )`; the reason is the last stderr line:

```
chunk is an int                    rc=1 left=None | AttributeError: 'int' object has no attribute 'replace'
chunk is null                      rc=1 left=None | AttributeError: 'NoneType' object has no attribute 'replace'
source is a string                 rc=1 left=None | AttributeError: 'str' object has no attribute 'get'
sources is a dict                  rc=1 left=None | AttributeError: 'str' object has no attribute 'get'
event text with a lone surrogate   rc=1 left=None | UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' in position 43: surrogates not allowed
item_id with a lone surrogate      rc=1 left=['view.jsonl.part'] | UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' in position 54: surrogates not allowed
export manifest not JSON           rc=2 … export manifest a list rc=2 … export sources a string rc=2 … export line not JSON rc=2 …
export bytes not UTF-8 rc=2 … export file missing rc=2 … export xz corrupt (LZMAError) rc=2 …
unknown pair, text in the role     rc=2 left=None | s1-view: refused: …: unknown (role, kind) ('owner ZQ-SESSION-TEXT-MARKER-q3', 'text') | MARK IN STDERR
labels line not JSON rc=2 … labels record a list rc=2 … build summary a list rc=2 … split manifest without labels rc=2 … --build is a file rc=2 … --export is a file rc=2
```

Also exit 2: an export manifest without `sources`, a build summary that is not JSON, a summary without `commit`, a labels record without `key`, a dataset line that is not JSON.

Where the four exit-1 inputs fail (tracebacks):
- non-str chunk: `view.py:343` → `render.py:60`;
- non-dict source: `common.py:191` (`row_identities`, called from `load_dataset`). `AttributeError` is not in the catch at `view.py:118`;
- event surrogate: `view.py:314` (`sha256_text` of the rendered stream), outside the catch at `:307-311`;
- item_id surrogate: `view.py:405` (`fh.write`). Only `OSError` is caught there. It leaves a 0-byte `view.jsonl.part` and the `--out` directory.

The surrogate inputs need forged files: the exporter turns lone surrogates into `?`, and `write_split` encodes strict UTF-8. The other two come through `write_split` over constructed rows. None of the tracebacks quotes session text (F4).

**Is any catch so broad that a code defect reads as an input refusal?** Yes. I planted a `TypeError` inside `facts_of` on a scratch copy (`"run_before": i - None`). The CLI then says `rc=2 refused: -home-user/3e3e…-000000000001.jsonl: unsupported operand type(s) for -: 'int' and 'NoneType'`. Round 1 caught only `UnknownPair` there. The tests still catch such a defect, because the world run must exit 0 (I5).

**Does a refusal's reason carry session text?** Two reasons quote input values. `UnknownPair` quotes the (role, kind) pair: a marker I planted in a hand-made role reached stderr. The src check quotes the event's `src`. The real exporter writes fixed roles and kinds and path-like srcs, so the risk is limited to hand-made inputs. JSON, recursion, type and lzma errors quote no text (I6).

### Q4. D-10, `--out`

`( cd <W> && … python3 q4.py )`. "landed" names each `view.jsonl` written, and `git rev-parse --is-inside-work-tree` gives git's verdict on its place:

```
link to an empty dir                 islink(out)=True  islink(abspath)=True  rc=2 landed=[] | … is a symbolic link
link to an empty dir, trailing /     islink(out)=False islink(abspath)=True  rc=2 landed=[] | … is a symbolic link
link to an empty dir, /.             islink(out)=False islink(abspath)=True  rc=2 landed=[] | … is a symbolic link
link to a non-empty dir              islink(out)=True  islink(abspath)=True  rc=2 landed=[] | … is a symbolic link
link to a file                       islink(out)=True  islink(abspath)=True  rc=2 landed=[] | … is a symbolic link
dangling link                        islink(out)=True  islink(abspath)=True  rc=2 landed=[] | … is a symbolic link
dangling link, /x below              islink(out)=False islink(abspath)=False rc=2 landed=[] | … [Errno 2] No such file or directory
in a work tree (.git dir)            … rc=2 landed=[] | … lies inside a git work tree (<Q>/repo/.git)
empty dir in a work tree             … rc=2 landed=[] | … lies inside a git work tree (<Q>/repo/.git)
new path deep in a work tree         … rc=2 landed=[] | … lies inside a git work tree (<Q>/repo/.git)
in a linked worktree (.git file)     … rc=2 landed=[] | … lies inside a git work tree (<Q>/wt/.git)
parent link into a work tree         … rc=2 landed=[] | … lies inside a git work tree (<Q>/repo/.git)
parent link out of a work tree       … rc=0 landed=[('outside/out/view.jsonl', 'no')] |
.. climbing into a work tree         … rc=2 landed=[] | … lies inside a git work tree (<Q>/repo/.git)
hop/../link -> empty dir outside     islink(out)=True  islink(abspath)=False rc=0 landed=[('T2_empty/view.jsonl', 'no')] |
hop/../link -> empty dir in repo     islink(out)=True  islink(abspath)=False rc=2 landed=[] | … lies inside a git work tree (<Q>/repo/.git)
hop/../link/ (trailing /)            islink(out)=False islink(abspath)=False rc=0 landed=[('T3_empty/view.jsonl', 'no')] |
```

The minimal B1 reproduction:

```
D=<W>/runs/b1; mkdir -p $D/B/sub $D/C $D/T; ln -s $D/B/sub $D/C/hop; ln -s $D/T $D/B/link
python3 <W>/pin/scripts/s1_train/view.py --build <W>/runs/q5/build --export <W>/runs/q5/export --out $D/C/hop/../link
s1-view: 2 build ids, 2 found, 0 not in the export, 0 ambigu…
rc=0  T now holds: summary.json view.jsonl
os.path.islink(out) = True | os.path.islink(os.path.abspath(out)) = False
corrected copy, hop/../link   rc=2 T holds [] | …/C/hop/../link is a symbolic link
corrected copy, hop/../link/  rc=2 T holds [] | …/C/hop/../link/ is a symbolic link
corrected copy, hop/../link/. rc=2 T holds [] | …/C/hop/../link/. is a symbolic link
corrected copy, the 92 tests: 92 passed
```

The correction on the scratch copy is one line: `or os.path.islink(out.rstrip("/").removesuffix("/.").rstrip("/") or out)` added to `view.py:381`.

**The gap between the two `check_out` calls** (`q4gap.py`, in-process; a monkeypatch plays the concurrent writer):

```
a: during the inputs         rc=2 in the work tree: [] | …/out-a is a symbolic link
b: after the second check    rc=0 in the work tree: ['summary.json', 'view.jsonl'] |
```

So a swap while the inputs are read is caught. A swap after the second check reaches the work tree (F6).

**A bind mount** (a private user and mount namespace): `repo/sub` mounted at `outside/mnt`, with `--out outside/mnt/out`. The view printed `view-rc=0`. Git, asked from the mount path, said `fatal: not a git repository`. After the namespace, `git status` in the repo shows `?? sub/out/summary.json` and `?? sub/out/view.jsonl` (I4).

**Can any of the brief's forms put an output inside a git work tree?** Only the race (F6) and the bind mount (I4). Every path form is refused when the physical place is inside a tree. Links in parent components are followed, and the git rule judges the physical place.

### Q5. D-11, the inputs

`( cd <W> && … python3 q5.py )`, on a two-file export:

```
output ../export2/a.xz (prefix sibling)      rc=2 | … resolves outside the export directory
output is the export directory (.)           rc=2 | … resolves outside the export directory
output is a directory inside                 rc=2 | …: [Errno 21] Is a directory: …
output through a link to a dir outside       rc=2 | … resolves outside the export directory
output a link inside to a file inside        rc=0 | found ['s1-50000a01', 's1-50000a02'] files_verified=2
one file: d/zz/../a against a                rc=2 | …: the outputs of …01.jsonl and …02.jsonl resolve to one file
one file: a hard link                        rc=2 | …02.jsonl: line 1 holds the src '…01.jsonl', not its manifest entry's
a byte copy under another name               rc=2 | …02.jsonl: line 1 holds the src '…01.jsonl', not its manifest entry's
an event's src differs (line 3)              rc=2 | …01.jsonl: line 3 holds the src '…02.jsonl', not its manifest entry's
output ../<own dir>/a (back inside)          rc=0 | found ['s1-50000a01', 's1-50000a02'] files_verified=2
```

- Outputs given as `../`, as an absolute path, or through a link to outside are refused. The builder's tests cover `../`, absolute and a link; I added the prefix sibling and a link to a directory outside.
- **Is a hard link "one file" under D-11?** Not to the code. Its one-file check compares `realpath`, which gives two different paths. The third check refuses the hard link anyway, and its reason names the entry (I3).

### Q6. The tests

- **Is the F16 run test independent?** Yes, by reading `test:296-305` and `test:878-890`. `run_blocks` reads the tape's raw records by `toolUseID` and `hookEvent`, and the hand-written expected blocks. The state is `"".join(s.exp)[:state_end]`. It never uses the adjacency loop, `R.block` or `R.render`. It shares D-8's definition by design, so it cannot see F1. It is only as strong as the fixture's shapes: M42 (below) survives because the fixture holds no split denial.
- **Mirrors:** no new test mirrors `view.py`. `capped()` and `cut_injection()` restate D-1's cap and the exporter's cut as oracles. The second is asserted against the export.
- **The deviation** (`_out`), reproduced on a scratch copy:

```
== basetemp inside a git work tree, the landed tests:            92 passed in 12.13s
== TMPDIR inside a git work tree (the _out_root precondition):   92 errors in 3.32s
== _out reverted to tmp_path/out, basetemp inside a git tree:    26 passed, 66 errors in 3.16s
== the same, basetemp outside git:                               92 passed in 11.37s
```

  It only moves `--out`. It hides no refusal, because every D-10 test still builds its link or tree under `tmp_path`. My review of the PIN diff of the old tests found three kinds of change: `--out` paths, counts updated for GUARD, and the run test's "holds the carrier" check moving from candidate to stamp (needed for ID_LONG2's capped block). The no-host-path check gained the `--out` root. No assertion was weakened.

### Q7. Normal behaviour, determinism, the boundary

`( cd <W> && … python3 q7.py )`. The round-1 fixture comes from 92d74958's own test builders, run through `<W>/r1`:

```
(2) again          rc=0 byte-identical=True
(2) cwd+relative   rc=0 byte-identical=True
(2) other tree     rc=0 byte-identical=True
(3) dropped ids: 12 leaks into any output: [('s1-10190a01', 'first line', 'view.jsonl')]
(1) round-1 fixture: view.jsonl r1 sha=fe15dfc84d409d72 pin sha=fe15dfc84d409d72 rows=9 byte-equal=True
    summary keys that differ: code.scripts/s1_train/view.py; counts.not_found.carrier_truncated (absent → 0); counts.not_found.own_result_in_state (absent → 0); counts.not_found.same_call_hook_in_state (absent → 0); version (s1-view-v1 → s1-view-v2)
    stdout r1 : s1-view: 10 build ids, 9 found, 1 not in the export, 0 ambiguous; 2 files, 48 events, 35 blocks, 10983 characters rendered
    stdout pin: s1-view: 10 build ids, 9 found, 1 not in the export, 0 ambiguous, 0 dropped by the guards; 2 files, 48 events, 35 blocks, 10983 characters rendered
```

The one "leak" is my own fixture: the dropped text `PRE-CONTEXT-WITH-NULL-CALL-ID` is a prefix of the written candidate `…-OK`. The dropped row's full JSON-quoted candidate, its digest and its id appear in no output. Under Python 3.10.20, 3.11.15, 3.12.3 and 3.13.12, `view.jsonl` and `summary.json` are identical on the Q1 fixture.

## 4. The mutant table (evidence demand 4)

I ran 35 new mutants on `<W>/mut`, a copy of the PIN, using `<W>/mut.py`:
- one exact edit each, checked unique in the file and compiled;
- `COLUMNS=1000`; the pristine file restored after each;
- the baseline first: `92 passed (total 92)` in both batches;
- AF-AP-223 scoring: a kill needs a FAILED test, and a changed total or an error-only run counts as INVALID.

Tally: batch D-8 `{'KILLED': 8, 'SURVIVED': 5, 'INVALID': 0}`; batch D-9 to D-11 `{'KILLED': 3, 'SURVIVED': 19, 'INVALID': 0}`. Both ended `restored: True`. Logs: `<W>/mut-d8.log`, `<W>/mut-rest.log`.

| # | Exact edit in view.py (old → new) | Result |
|---|---|---|
| M1 | `if call_id is not None and any(k < j and t == call_id and e == event …)` → drop `call_id is not None and ` | **SURVIVED** |
| M2 | same line → drop ` and e == event` | KILLED 5: absent_build_id, id_with_two_carriers, each_guard_item, every_present_id, summary |
| M3 | `elif ev["kind"] == "hook" and ends[k] > starts[k]:` → `elif ev["kind"] == "hook":` | **SURVIVED** |
| M5 | guard 1 `k < j` → `k <= j` | KILLED 5 (same) |
| M38 | guard 1 `k < j` → `k < i` | KILLED 5 (same) |
| M42 | `if call_id` → `if kind != "tool_result" and call_id` | **SURVIVED** |
| M43 | `e == event for` → `e == event and event in STEP_EVENTS for` | KILLED 7: + dropped_row_reaches_no_output, the F16 run test |
| M6 | guard 2: drop ` and kind != "tool_result"` | **SURVIVED** |
| M7 | guard 2: `k < j and c == call_id` → `c == call_id` | KILLED 6: + fake_key_planted |
| M8 | `elif events[i]["truncated"] is not None:` → `events[j]` | **SURVIVED** |
| M10 | `got = found.get(sid, [])` → `[g for g in found.get(sid, []) if g["guard"] is None] or found.get(sid, [])` | KILLED 1: id_with_two_carriers |
| M11 | `sum(counts["not_found"][g] for g in GUARDS),` → `counts["not_found"][GUARDS[0]],` | KILLED 1: absent_build_id |
| M12 | `counts["not_found"][f["guard"]] += 1` → `["not_in_export"]` | KILLED 3 |
| M14 | `:224 except (RecursionError, ValueError)` → `except RecursionError` | **SURVIVED** |
| M15–M18 | `:168 except (OSError, RecursionError, ValueError, KeyError, TypeError, AttributeError)` minus ValueError / TypeError / AttributeError / KeyError | **SURVIVED** (4) |
| M19–M21 | `:110` catch minus ValueError / KeyError / TypeError | **SURVIVED** (3) |
| M22–M24 | `:154` catch minus ValueError / KeyError / TypeError | **SURVIVED** (3) |
| M25 | `:118` catch minus ValueError | **SURVIVED** |
| M26 | `:198 except OSError` → `except ZeroDivisionError` | **SURVIVED** |
| M27 | `:205 except lzma.LZMAError` → `except ZeroDivisionError` | **SURVIVED** |
| M29 | `:381 islink(os.path.abspath(out))` → `islink(out)` | KILLED 2: symlink[link-dot], symlink[link-slash] |
| M30 | `:383 d = os.path.realpath(out)` → `abspath` | KILLED 2: git[through_a_link], out_with_a_nul |
| M31 | `:385 lexists(… ".git")` → `exists` | **SURVIVED** |
| M32 | `:418 check_out(args.out)` removed | **SURVIVED** |
| M34 | `:181` drop `path == root or ` | **SURVIVED** (equivalent in effect) |
| M35 | `:181 commonpath(…) != root` → `not path.startswith(root)` | **SURVIVED** |
| M36 | `:178 realpath` → `normpath` | KILLED 3: outside[symlink], output_with_a_nul, one_file[symlink] |
| M37 | `:218 if ev["src"] != src:` → `if n == 1 and ev["src"] != src:` | **SURVIVED** |

To show the survivors are not equivalent, I ran each mutated view against an input that holds its shape (`q6surv.py` and two re-runs):

| Mutant | Input | PIN's view | Mutant's view |
|---|---|---|---|
| M1 | ups_null | written=10 | 9 (drops it) |
| M3 | empty | written=10 | 9 (drops it) |
| M42 | denysplit | written=10 | 11: writes the split denial, state holds `GRAFT-HINT-OF-THE-SPLIT-DENIAL` |
| M6 | a denial after a reused id's result | written=1 | 0 (`own_result`) |
| M8 | a cut carrier preceded in its run by a short hook | `carrier_truncated` 1 | written=2: the cut candidate written |
| M35 | an output in a string-prefix sibling `eX-sibling` | rc=2 | rc=0, reads a file outside |
| M37 | src differs on line 3 | rc=2 | rc=0 |
| M32 | full `--out` plus a bad sha256 | refuses on `--out` | refuses on the input |
| M31 | a directory whose `.git` is a dangling link | rc=2 | rc=0 |
| M14–M27 | each shape rebuilt (below) | rc=2, intended reason | rc=1, traceback |
| M34 | output `.` | rc=2, entry named | rc=2, entry named (`Is a directory`) |

The M14 to M27 rows, each on its rebuilt shape:

```
M14 PIN rc=2 …jsonl: Expecting …   | mutant rc=1 json.decoder.JSONDecodeError
M15 PIN rc=2 the export's manifest.json: Expecting … | mutant rc=1 JSONDecodeError
M16 … list indices … | rc=1 TypeError      M17 … 'str' object has no attribute | rc=1 AttributeError
M18 … 'sources' | rc=1 KeyError            M19 the build: Expecting … | rc=1 JSONDecodeError
M20 the build: 'commit' | rc=1 KeyError     M21 the build: list indices … | rc=1 TypeError
M22 … labels: Expecting … | rc=1 JSONDecodeError   M23 … labels: 'key' | rc=1 KeyError
M24 … labels: list indices … | rc=1 TypeError      M25 … train split: Expecting … | rc=1 JSONDecodeError
M26 …: [Errno 2] … | rc=1 FileNotFoundError        M27 …: Corrupt input data | rc=1 _lzma.LZMAError
```

My first try at this table was invalid, and the fault was my harness: `q3.base_fixture()` wipes `runs/q3`, so q4 had deleted nine of the shapes. The table above comes from shapes rebuilt in the same script, with the PIN's reason printed for each.

I spot-checked two of the builder's mutants, re-made from its table's descriptions:
- G3-off (`elif False:`) gave `6 failed, 86 passed`.
- D11-src-off gave `1 failed, 91 passed` (`an_event_whose_src_is_not_its_entrys`).

Both match the builder's table.

## 5. The builder's deviation and observations, graded

- **Deviation (section 9, `_out`):** sound and necessary. It is reproduced exactly, hides no refusal, and weakens no assertion (Q6).
- **Observations (section 10):**
  - The PC basetemp lies inside the clone: sound, reproduced (26/66).
  - The real run's `--out` must lie outside every work tree: conformant to D-10.
  - `own_result_in_state` with a null call id: a sound literal reading of an open point (F3).
  - A non-str chunk exits 1: reproduced; it is F4(a). I found three more such inputs.
  - A link in a parent of `--out` is followed: sound for a plain parent link, but incomplete. A parent link followed by `..` defeats the link rule (B1).
  - A dangling link, a loop or a file as a parent: reproduced for `l_dangling/x` (exit 2 at write).
  - The gate union: confirmed. `git grep` at the PIN finds no code consumer of the stdout line or the version, only ledger and wiki history.
  - Its harness's AF-AP-223 fix: not verifiable. The harness is in the shared scratchpad, which I do not read.
- **N19 "equivalent":** equivalent in exit code only. Its premise ("D-10 refuses every symbolic link before `os.path.lexists` is reached") is false for B1's spelling. With `hop/../dang`, the PIN refuses at the first check ("exists and is not an empty directory"). N19 refuses later, at write (`[Errno 17] File exists`), after reading the inputs (I9).
- **Pyflakes and separators:** pyflakes rc 0 on both files. The separator check (`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`) prints 0 for both, with grep rc 1.

## 6. Your note: interpreter-worded reasons

Measured with `<W>/msgs.py`, which does the same operations the view does:

```
3.10.20 / 3.11.15 / 3.12.3: realpath NUL → ValueError: embedded null byte
3.13.12:                    realpath NUL → ValueError: lstat: embedded null character in path
all four: RecursionError: maximum recursion depth exceeded while decoding a JSON array fro… ; TypeError: unhashable type: 'list' ;
          FileNotFoundError: [Errno 2] No such file or directory: …
```

- `main()` in-process with a NUL `--out` exits 2 on both 3.11 and 3.13; only the wording differs. The reason echoes the NUL byte raw to stderr.
- The other pinned texts are stable on 3.10 to 3.13 here. Python 3.14 is not installed, so I cannot check it (UNVERIFIED). I recall that 3.14 rewords some unhashable-key messages; that would affect `test_an_event_whose_role_is_a_list_is_refused`.
- None of the other interpreters has pytest, so I could not run the suite under them (I7).

## 7. Finding inventory (no severity filter)

**B1. BLOCKER: D-10's link rule is defeated by a `<link>/..` spelling of `--out`.**
- **Evidence:** reproduced (Q4, the minimal reproduction).
- **Mechanism:** `view.py:381` tests the text-normalised path, `islink(abspath(out))`. When a symbolic link comes before `..`, the kernel resolves the path to another entry. `os.path.islink(out)` is `True`.
- **Contract:** D-10: "Refuse (exit 2, nothing written) an `--out` that is a symbolic link, to anything, an empty directory included (F14)."
- **Canonical path:** the CLI at the PIN.
- **Material effect:** the run exits 0 and writes both outputs through the link into its target. This is the effect F14 named and D-10 forbids. It is bounded: the git rule is physical, so the output never lands inside a work tree (git agrees).
- **Discriminator:** the command above. The one-line correction refuses all three spellings with `92 passed`.
- **Fix (inside the boundary):** also test `os.path.islink()` on `--out` with only trailing `/` and `/.` removed. Add a test with a `<link>/../<link>` `--out`.

**F1. FOLLOW-UP, UNVERIFIED on real data (a possible CONTRACT-DEFECT for D-8):** a prompt-time run split by a notification, whose hooks carry distinct or null `toolUseID`s.
- **Evidence:** ups_distinct and ups_null are written with the other hook's text in their state, through the real exporter.
- **Contract:** the code conforms to D-8, which matches equal non-null `toolUseID`s.
- **Unknown:** whether the harness writes such ids. Tracked files do not record it, and both fixtures (the builder's and round 1's) model one id per prompt. The real run's 0 drops over 40 UserPromptSubmit carriers rules out one constant id per file, not one id per hook.
- **Measure (counts only, for you):**
  1. Count the UserPromptSubmit and SessionStart hook events whose `toolUseID` is null or absent.
  2. For each owner text (a coordinator text in a lane), count the distinct `toolUseID`s among the UserPromptSubmit hook events after it and before the next model text. Count the cases with more than one.
- **If either count is above 0:** D-8 needs an amendment. That is not a repair for this builder.

**F2. FOLLOW-UP: duplicated call ids cause counted drops by D-8's literal wording.**
- **Evidence:** dup_pre_result is dropped as own_result because of the first call's result. dup_post_hook is dropped as same_call because of the first call's hook. The agent had read both texts.
- **Contract:** conformant to D-8 ("copy them").
- **Real data:** the real run dropped 0.
- **Fix (a D-8 amendment):** search for guard events only after the carrier's own last tool_call with its call id.

**F3. FOLLOW-UP (Q2): `None == None` in guard 2.** A sound literal reading. The effect is a counted false drop on a malformed transcript. Fix (a D-8 amendment): add "the call id is not null" to guard 2.

**F4. FOLLOW-UP: four hand-made inputs exit 1 (Q3).**
- **The four, and how each can be made:**
  - (a) a non-str chunk, through `write_split`;
  - (b) a non-dict source, through `write_split`;
  - (c) a lone surrogate in an event text, in a forged export;
  - (d) a lone surrogate in an `item_id`, in a forged build. Only (d) writes anything: a 0-byte `view.jsonl.part`.
- **Contract:** (a), (b) and (d) are outside D-9's enumerated classes and places. (c) is a `ValueError` at the edge of D-9's letter: it is raised at `:314`, after `:307-311` read the file.
- **Precedent:** round 1 graded the same class (F13) as a follow-up.
- **Your call:** flag (c) and (d) if you read D-9 more widely.
- **Fix:** catch `AttributeError` at the build reads, move `:314` inside the try, and catch `UnicodeError` in `write`.

**F5. FOLLOW-UP: 24 surviving mutants.** All 24 are test gaps; the code is right on each rule. 23 differ from the PIN on an input that holds their shape (section 4), and M34 is equivalent in effect.
- **The most important:** M42 and M8 each write a headline-breaking row with all 92 tests green.
- **Demand-7 coverage:** the builder's set removed only the D-9 catches the change added. Its "35 of 36 killed" therefore does not cover the D-9 classes on the read paths.
- **Fix:** add these fixture items:
  - a split denial;
  - a cut carrier that is not first in its run;
  - a null-id prompt run;
  - a non-rendering hook of the carrier's call before a split;
  - a denial after a reused id;
  - one refusal test per D-9 class per read site;
  - a dangling `.git`;
  - a bad `--out` with a bad input;
  - a prefix-sibling output;
  - a src mismatch after line 1.

**F6. FOLLOW-UP: the race after the second `check_out` (Q4).**
- **Evidence:** a writer that turns `--out` into a link into a work tree between `check_out` and `os.makedirs` gets both outputs written there. Reproduced in-process with a monkeypatch.
- **Contract:** D-10's "both calls" are kept.
- **Fix (hardening):** create `--out` with `os.mkdir`, and write with `O_NOFOLLOW` relative to a directory fd.

**Information items:**

| # | Observation |
|---|---|
| I1 | The non-miss shapes of Q1 behave as D-8 says. |
| I2 | Two or three guards are counted once. The partition holds (22 = 22). |
| I3 | A hard link or a byte copy is refused by the src check, not the one-file check. An output `.` is refused as "outside" (wording only). |
| I4 | A bind mount puts outputs inside a work tree. D-10's definition and git's own discovery both miss it, and it needs an operator-made mount. |
| I5 | The D-9 catch around `facts_of` turns a code defect into a "refused" with a src named. |
| I6 | `UnknownPair` and the src check quote input values on stderr (hand-made inputs only). |
| I7 | Interpreter-worded reasons (section 6). |
| I8 | The view.py docstring overclaims: "An input that cannot be read or checked is refused too", and "2 refused (… nothing written)". |
| I9 | The builder's N19 premise is false under B1's spelling. |
| I10 | The Pre hooks of the carrier's call stay in a PostToolUse state by D-8's `hookEvent` clause: the out-of-scope F4/F5 "which seen" question. |

## 8. The blocking predicate applied

| Finding | Contract | Real path | Material | Discriminator | Owned here | Blocks? |
|---|---|---|---|---|---|---|
| B1 | D-10 contradicted | yes, the CLI at the PIN | yes: outputs written through a link (bounded: never in git) | the command; the corrected copy | yes, `view.py:381` | **yes** |
| F1 | the headline; the code conforms to D-8 | built order; harness shape unmeasured | unknown | yes | no (a D-8 amendment) | no; a CONTRACT-DEFECT if measured above 0 |
| F2, F3 | conformant (D-8 literal) | built orders | counted drops | yes | no (amendment) | no |
| F4 | outside D-9's letter; (c) at its edge | hand-made or forged inputs | none written; (d) a 0-byte part file | yes | yes | no (your call on (c) and (d)) |
| F5 | test gaps; the code is right | — | none now | yes | yes | no |
| F6 | D-10 kept | needs a concurrent writer | yes, under the race | in-process | yes | no (hypothetical) |
| I1 to I10 | none, or conformant | — | — | — | — | no |

**Round table (D-115):**
- Round 1: 0 blockers.
- Round 2: 1 blocker, B1, in a class that did not exist in round 1 (D-10 is new).
- No class recurs. The repair is one line and one test, so another round converges.

## 9. Reproduced, static, skipped, NOT done

- **Reproduced:**
  - the premise (start and end) and the builder's tests twice, with the set id;
  - every Q1 to Q7 claim above, through the CLI or `facts_of` over real exports;
  - 35 mutants, each survivor discriminated;
  - the deviation numbers;
  - two of the builder's mutants;
  - pyflakes and the separator check;
  - the interpreter messages, and the view under 3.10 to 3.13.
- **Static (by reading only):** F16's independence; the test-diff review; the docstring check (I8).
- **NOT done:**
  - the real run, and the F1 measure: I may not read the real export or view;
  - pytest under 3.10, 3.12 or 3.13: no pytest there, and no install;
  - Python 3.14: not available;
  - a real concurrent writer: monkeypatch only;
  - `ap_screen`: the builder's gate;
  - the builder's other 34 mutants;
  - your test-only fix: my subject is the PIN archive;
  - any read of `.jev/`, env files, the coordinator's scratchpad, the builder's `g460-*` or round 1's `vfy444-*` directories, or real transcripts.

## 10. Hygiene and files

- **The main tree:** I wrote no tracked file in `/home/user/agent-factory`. Its status at the end shows `M docs/08_DECISION_LOG.md`, `M tests/test_s1_train_view.py` (your announced fix) and `M todo/BUILD-TASKLIST.md`. None is mine.
- **The premise run in the main tree:** it used `-p no:cacheprovider` and `PYTHONDONTWRITEBYTECODE=1`, with its basetemp in my scratch. Its temporary directories were removed by their own cleanup.
- **Large copies:** I deleted `mut`, `r1` and `pin2`. I kept `pin` (250 MB). Recreate the others with:
  - `cp -a <W>/pin <W>/mut`
  - `git -C /home/user/agent-factory archive 92d74958 | tar -x -C <W>/r1`
- **Re-run caveat:** `q4.py` and `q4gap.py` wipe `runs/q3`, so re-run `q3.py` before anything that needs its shapes.

Files are in `<W>`:
- `h.py`: the fixture harness;
- `q1.py`, `q3.py`, `q4.py`, `q4gap.py`, `q5.py`, `q7.py`, `msgs.py`: the question probes;
- `q6surv.py`, `rest.py`: survivor discrimination and the remaining probes;
- `mut.py`, `mut-d8.log`, `mut-rest.log`: the mutant harness and its logs;
- `runs/`: every fixture and output (FAKE data only).