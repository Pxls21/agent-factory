# S4-2-READ (task #471): the reading program of the first S1 training

Role: code-implementer (sandbox, Opus 5.5). PIN: b1df2d35 (the code commit under the origin head at authoring, which adds only transcripts; full id in the premise). Report:
`tasks/briefs/jev-laya/S4-2-READ-report.md` (write it incrementally from the start). Do NOT spawn subagents. Touch ONLY
the files in the boundary; report adjacent defects, never fix them. Planting FAKE keys and markers in fixtures is
defensive testing of the owner's own data path (D-118: the scrub stays), authorized by the owner.

## WHY

Task #441 is the first S1 training (`tasks/s1-heads-breakdown.md`, its pre-registration
`docs/research/findings/s1-train/PREREG-441.md`): a frozen RWKV-7 0.4B reads each transcript's rendered stream once, in
a GPU window on the owner's PC, and small heads learn on the CPU whether an injected context helps the step it was
injected at. This task builds the program that turns the view of the S1 dataset (task #444, `scripts/s1_train/view.py`)
into features. Task #472 (the heads and the evaluator) runs beside you on disjoint files and reads your output through
`scripts/s1_train/features.py`, which the coordinator wrote; it is the interface, so you read it and never change it.

You cannot run the real model here (no GPU, no torch in the sandbox's main Python, no transformers). So the program is
built around one backend interface: a deterministic FAKE backend and a fake tokenizer prove every rule in the tests,
and the `fla` backend and the Hugging Face tokenizer are thin adapters that first run on the PC (the coordinator's
smoke job, task #441). Keep those adapters small and obvious.

## GOAL

`scripts/s1_train/read.py`, a CLI with five subcommands: `tokens`, `read`, `tails`, `compare`, `smoke`; and its tests.

## BOUNDARY

- CREATE `scripts/s1_train/read.py`, `tests/test_s1_train_read.py`.
- READ, never modify: `scripts/s1_train/features.py` and `tests/test_s1_train_features.py` (the features format: use
  `features.write` and `features.read`, never another writer); `scripts/s1_train/view.py` (`read_manifest`,
  `stream_events`: reuse them for the export checks, and its D-10 git-work-tree test for your text outputs);
  `scripts/s1_train/render.py` (`render`, `body`); `docs/research/findings/s1-train/PREREG-441.md` (§2 and §8: the
  feature definitions and the machine-read block); `tests/test_s1_train_view.py` (how a fixture session is exported,
  built and viewed through the REAL producers); `docs/research/findings/j2b-variants/rwkv7_g0.py` (lines 137-149 and
  87-96: how the PC loads the checkpoint and its tokenizer, forwards with a cache and copies it with
  `copy.deepcopy`).
- Every other file is out of bounds. Task #472 creates `scripts/s1_train/heads.py`, `scripts/s1_train/evaluate.py` and
  their tests at the same time: never touch them.

## PINNED DECISIONS (a conflict with the tree is a STOP-and-report)

**R-1 The pre-registration block.** `--prereg <file>`: the file's only fenced ```json block is parsed (none, two, or
invalid JSON: refused). From it: `inputs.view_jsonl_sha256`, `inputs.view_summary_sha256`,
`inputs.export_manifest_sha256`, `features.candidate_block` (holds `{body}` exactly once), `features.question_block`,
`features.short_window_tokens` (a positive int), `word_overlap.state_tail_chars` (a positive int). Every output's
manifest records the prereg file's sha256 and a copy of the whole block (task #472 compares it with the block it reads).

**R-2 The inputs are verified before use.** `--view <dir>`: `view.jsonl` and `summary.json`, each sha256 equal to the
block's. `--export <dir>`: `manifest.json`'s sha256 equal to the block's; each export file read through
`view.read_manifest` and `view.stream_events` (their sha256, xz and schema checks). Only the files that hold rows are
read. Each such file is rendered with `render.render(events)`; the sha256 of the rendered text must equal
`summary.json`'s `streams[src].sha256`, else refused. Each row's `state_end` must be the start of a non-empty block
and greater than 0, else refused.

**R-3 Tokens per block.** A file's blocks are the non-empty slices `text[starts[i]:starts[i+1]]` (the last one to the
end) in order. Each block is tokenized ON ITS OWN (a live reader reads each event when it arrives); a file's token
stream is the concatenation, kept up to its last row's `state_end` (nothing after it is read). A row's token position is
the number of tokens of the blocks before its `state_end`. The candidate block of a distinct candidate is
`candidate_block` with `{body}` replaced (a plain string replace, never `str.format`) by `render.body(candidate)`; the
question block is `question_block` verbatim; each is tokenized on its own.

**R-4 `tokens`.** `read.py tokens --view <dir> --export <dir> --prereg <file> --tokenizer fake|hf [--model <dir>] --out
<dir>`. Writes `manifest.json` (version `s1-tokens-v1`; the prereg sha256 and block; the view and export sha256s; the
tokenizer's identity; per file: its key, the sha256 of its token file, its token and block counts, and its rows as
`[row id, token position]`; per distinct candidate sha256: its candidate token ids' offset and length in
`candidates.tok`; the question's ids; the sha256 of every file it writes), one `<k>.tok` per file that holds rows (k: its
index in the sorted list of those files' `src`), and `candidates.tok`. A `.tok` file is uint32 little-endian ids. The
`hf` tokenizer: `AutoTokenizer.from_pretrained(<model dir>, trust_remote_code=True, local_files_only=True)`, `encode(text,
add_special_tokens=False)`; its identity is its class name, its vocabulary size and the sha256 of each file named
`*vocab*` in the model dir (never a host path). The `fake` tokenizer: greedy longest match over a fixed vocabulary of
the 256 single bytes of the UTF-8 text plus multi-byte pieces that cross a block boundary when a whole text is
tokenized at once (at least `"\n\nH"`, `"\n\nC"`, `"\n\nR"`, `"\n\nO"` and `"Hook:"`), so that tokenizing a whole text
differs from tokenizing its blocks.

**R-5 `read`.** `read.py read --tokens <dir> --backend fake|fla [--model <dir>] [--only <src> ...] [--segment N]
[--work <dir>] --out <features dir>`. Every token file's sha256 is checked against the tokens manifest first. For each
file in order (all of them, or the `--only` ones): from the zero state, read the stream in forwards of at most
`--segment` tokens (default 32768) that end at each distinct row position. At a row position: `s` is the readout; copy
the state, read the candidate block on the copy (`c_ctx`), then the question block on the same copy (`q_ctx`), drop the
copy, and go on with the original. Rows at the same position share `s`. Then, per row, from the zero state: the last
`short_window_tokens` tokens before its position (all of them when fewer), readout `s_w`; then the candidate block
(`c_ctx_w`) and the question block (`q_ctx_w`) on that state. Then, per distinct candidate of the rows read, from the
zero state: the candidate block (`c_free`), then the question block (`q_free`). The features go out through
`features.write` (rows sorted by id; free keys sorted), with `meta` holding exactly the keys `backend` (its identity),
`tokens_manifest_sha256`, `prereg_sha256`, `prereg_block` and `counts` (tokens read per file, forwards, rows); task
#472 reads them by these names. Timings go to
`<work>/timings.json` and stderr, never into the features (they would break byte identity). With `--work`, each
finished file's readouts are saved there and a later run with the same `--work` and the same tokens skips that file
(counted `resumed`); the result equals an uninterrupted run byte for byte.

**R-6 The backend interface.** `name`; `identity()` (a dict: versions, the model weights' sha256, the device; never a
host path); `dim()`; `zero()`; `read(state, ids) -> (state, readout)` (ids non-empty; the readout is the final hidden
state after the last norm at the last id, as a list of floats; the state passed in may be consumed); `copy(state)`. The
`fake` backend is pure Python, dimension 8, deterministic, and every readout depends on every id read before it (for
example a per-dimension decay-and-add over a fixed embedding of each id), so reading the candidate on the original state
instead of the copy changes every later row's `s`. The `fla` backend imports torch, transformers and fla only inside
itself; it loads the model as `rwkv7_g0.py` does (bf16, `.to("cuda").eval()`), reads with `model.model(input_ids=...,
past_key_values=state, use_cache=True)` under `torch.no_grad()`, takes `last_hidden_state[0, -1]` as a float list, and
copies with `copy.deepcopy`. It is never imported or run by a test.

**R-7 `tails`.** `read.py tails --view <dir> --export <dir> --prereg <file> --out <dir>`: verifies as R-2, and writes
`tails.jsonl` (one `{"id", "tail"}` line per row, sorted by id; `tail` = the last `state_tail_chars` characters of the
rendered text before `state_end`) and `manifest.json` with exactly the keys `prereg_sha256`, `view_jsonl_sha256`,
`view_summary_sha256`, `export_manifest_sha256`, `count` and `tails_sha256` (task #472 reads them by these names). Task #472's word-overlap baseline reads it. No tokenizer is needed.

**R-8 `compare` and `smoke`.** `read.py compare <features A> <features B>`: for each row array, the cosine per row over
the rows both hold, and for each free array per key both hold; prints one JSON object, `{"arrays": {<name>: {"n", "min", "median",
"max"}}, "min": <the overall minimum>}` (task #472 reads its `min`). `read.py smoke --backend fake|fla [--model <dir>] --out <file>`: on fixed built-in texts A, B
and C, (1) the copy check: A, then C on a copy, then B on the original, gives B's readout EQUAL to A then B; (2) the
split check: A and B in one read against A then B, cosine reported, at least 0.999 required; (3) for `fla` only, the
head check: `model.lm_head` applied to the readout (in the model's dtype) against the model's own last-position
logits from `model(...)` on the same ids, from the zero state: the same argmax and a cosine of at least 0.9999, which
proves the readout is the hidden state the head reads (bf16 makes a max-abs bound meaningless: the 2026-09-24 window
saw logit differences up to 0.1875 between two splits of one text). Exit 0 only when every check passes; the JSON result says
which ran.

**R-9 Outputs that hold session text.** Token ids decode to session text and tails are session text, so `tokens`,
`tails` and `--work` refuse an output inside a git work tree (view.py's D-10 rule, reused), an output named with a
`..` part (AF-AP-261: a missing part before the `..` changes what it names once it is created), and an output that is
not empty. Nothing session-derived is printed: stdout carries one line of counts.

**R-10 Determinism.** No clock, no host path, no randomness in any output; the same inputs give byte-identical outputs
with the fake backend, a resumed run included.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below at your HEAD; stop and report on a mismatch.
2. Fixtures through the REAL producers, as `tests/test_s1_train_view.py` makes them: a session tree with a main
   transcript and one lane transcript, exported by the real exporter (`init-key` FAKE key, a fixture repo,
   `--known-values key-only`), a frozen build written by `build_s1.write_split`, and `view.py` run over them; a fixture
   pre-registration file whose block carries the fixture's sha256s (computed in the test). The session holds at least
   four scored injections in two files, two of them on one call (one position, two rows), a thinking block holding a
   marker, and one row whose state is longer than the fixture's short window.
3. Normal tests: every row's `s`, `c_ctx`, `q_ctx`, `s_w`, `c_ctx_w`, `q_ctx_w` and every candidate's `c_free`,
   `q_free` equal an independent oracle in the test, a fold of the fake backend's update over the ids the test computes
   itself from the rendered text (never by calling read.py's own helpers); the token positions equal the oracle's;
   `compare` of a run with itself reads 1.0; `smoke --backend fake` passes; `tails` holds each row's last characters.
4. Failure tests, each asserting the exact exit code and the named reason: a view, summary or export manifest whose
   sha256 is not the block's; a summary stream sha256 that does not match the render; a `state_end` that is not a block
   start (the fixture's view and its sha256 in the fixture block both changed, so only that check can refuse it); a
   `state_end` of 0; a token file whose bytes changed; a prereg with no block or two blocks; a `candidate_block` without
   `{body}`; an output inside a git work tree, with a `..` part, or not empty.
5. Security-boundary tests: the thinking marker is in no token stream (decoded with the fake tokenizer) and no tail; a
   FAKE key planted in an export event after the export (the test updates the manifest's sha256 and the fixture
   block's) is in no token stream and no tail; the copy rule (a candidate read on a copy never reaches a later `s`) is
   tested by the oracle, not by the code's own state.
6. Determinism: two runs byte-identical; a run with `--only` the first file into a `--work` dir, then a full run with the
   same `--work`, equals a full run without it, byte for byte, and counts that file as resumed.
7. Mutants on a scratch copy of your file (one exact edit each, the baseline green first), each red on a named test: the
   candidate read on the original state; `s` taken after the candidate; the whole text tokenized at once; a row position
   one block late; the short window not from the zero state; the window length ignored; the render sha256 check off; the
   token-file sha256 check off; the free arrays keyed by row; the git-work-tree refusal off; the `..` refusal off; the
   question block read from the zero state instead of after the candidate. Paste the table.
8. Tests run twice: `bash scripts/test_summary.sh --basetemp <scratch dir> tests/test_s1_train_read.py` (the counts
   pasted from its `pytest-summary:` line) and `bash scripts/pc_suite.sh set-id -- tests/test_s1_train_read.py`; the
   file runs in under two minutes. Also run `tests/test_s1_train_features.py` and `tests/test_s1_train_view.py` once and
   paste their lines (you change neither).
9. Gates: pyflakes on every file you write; `python3 scripts/ap_screen.py <your files>` (paste its tells and answer
   each); the separator check (`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0).
10. NOT run here: the `hf` tokenizer and the `fla` backend (the coordinator runs `tokens --tokenizer hf` and `smoke
    --backend fla` on the PC first). Say so in the report; never claim them tested.

## STANDING RULES

No outward-facing action (no push, PR or comment); no network; no PC bridge. Never commit, stash, checkout or reset in
`/home/user/agent-factory` (the coordinator commits). Never read `.jev/`, the coordinator's scratchpad, `/root/.codiv/`,
`.pc-bridge.env`, any `*.env`, the pseudonym key under `/root/.config/session-export/`, or a real transcript under
`/root/.claude/projects/`; never run the exporter with `--known-values default`, nor `scripts/known_values_check.py`
with its default sources. In the session scratchpad, read nothing outside a directory you create there. FAKE strings
for anything secret-shaped, built at run time. Long commands in ONE foreground call; no background job. A pytest
`--basetemp` parent must exist first. Every test run with `PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox
HF_HUB_OFFLINE=1`, no `-n`. Your final message is the report: files and lines, the pasted counts, the mutant table,
discrepancies, and what is NOT done.

## PREMISE — MEASURED at authoring (2026-10-02 09:3xZ, /home/user/agent-factory@b1df2d35)

Re-run each command at your HEAD; its output must match.

```
$ git rev-parse --verify b1df2d3508155b8b664750e715f680505e113eb7^{commit}
b1df2d3508155b8b664750e715f680505e113eb7
$ git merge-base --is-ancestor b1df2d3508155b8b664750e715f680505e113eb7 HEAD && echo the PIN is an ancestor of HEAD
the PIN is an ancestor of HEAD
$ git diff --stat b1df2d3508155b8b664750e715f680505e113eb7 HEAD -- scripts/s1_train/ tests/test_s1_train_view.py tests/test_s1_train_features.py docs/research/findings/s1-train/PREREG-441.md docs/research/findings/j2b-variants/rwkv7_g0.py | wc -l
0
$ ls scripts/s1_train/ | grep -v __pycache__
__init__.py
features.py
render.py
view.py
$ test -e scripts/s1_train/read.py || echo read.py absent; test -e tests/test_s1_train_read.py || echo test_s1_train_read.py absent
read.py absent
test_s1_train_read.py absent
$ sha256sum scripts/s1_train/features.py scripts/s1_train/render.py scripts/s1_train/view.py | cut -c1-16
6a32c42d16299365
901c086a6a90f90a
4629e0c720edaa82
$ grep -n -E '^def (read_manifest|stream_events|check_out)' scripts/s1_train/view.py
161:def read_manifest(edir):
191:def stream_events(path, entry):
376:def check_out(out):
$ grep -n -E '^def (render|body|block)|^VERSION|^CAP' scripts/s1_train/render.py
34:VERSION = "s1-render-v1"
35:CAP, HEAD, TAIL = 4000, 3000, 1000          # characters of a body, after the scrub and the newline rule
71:def body(text, counts=None):
100:def block(event, counts=None):
117:def render(events, counts=None):
$ grep -n -E '^def (write|read)|^VERSION|^ROW_ARRAYS|^FREE_ARRAYS' scripts/s1_train/features.py
21:VERSION = "s1-features-v1"
22:ROW_ARRAYS = ("s", "c_ctx", "q_ctx", "s_w", "c_ctx_w", "q_ctx_w")
23:FREE_ARRAYS = ("c_free", "q_free")
47:def write(out_dir, rows, free, dim, arrays, meta):
104:def read(in_dir):
$ sed -n '137,149p' docs/research/findings/j2b-variants/rwkv7_g0.py | grep -c from_pretrained
2
$ python3 -c "import importlib.util as u; print([m for m in ('numpy', 'torch', 'transformers', 'fla') if u.find_spec(m)])"
[]
$ B=$(mktemp -d) && PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1 python3 -m pytest -q -p no:cacheprovider tests/test_s1_train_features.py tests/test_s1_train_view.py --basetemp $B/bt 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//'
112 passed
```
