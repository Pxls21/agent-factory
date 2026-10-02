# S3-5-VIEW (task #444): the RWKV view of the S1 dataset

Role: code-implementer (sandbox, Opus 5.5). PIN: f7f78165 (the origin head at authoring; full id in the premise). Report:
`tasks/briefs/jev-laya/S3-5-VIEW-report.md` (write it incrementally from the start). Do NOT spawn subagents. Touch ONLY
the files in the boundary; report adjacent defects, never fix them. Planting FAKE keys and markers in fixtures is
defensive testing of the owner's own data path (D-118: the scrub stays), authorized by the owner.

## WHY

D-125 and D-126 (the owner, 2026-10-01; rows in `docs/08_DECISION_LOG.md`): RWKV-7 is the only System-1 model. A frozen
RWKV-7 reads each transcript's exported stream once, and small contrastive heads (Contrastive-LM's method) learn on the
CPU whether an injected context helps the step it was injected at. The first training is task #441; the live home is
task #448. Both need this task first (S3-5 in `tasks/laya-s3-breakdown.md`): for every scored injection of the frozen
S1 build, WHERE in its transcript's stream it sits, WHAT the agent had seen before it (the state), and WHAT was injected
(the candidate), with the build's label and split.

The S1 build (task #438, `scripts/laya_ft/build_s1.py`) made Laya rows: five short fields cut to fit a 1,024-token
window. RWKV reads the whole stream, so the state is no longer a set of fields: it is the stream itself, rendered as
text, up to the injection. The render is shared: task #441's reading pass renders each stream the same way to find each
state's end, and task #448 renders the live transcript the same way. One render, three users.

## GOAL

1. `scripts/s1_train/render.py`: the ONE render of an exported event stream into text, block by block, with the offset
   where each event's block starts. A block depends on its event alone (task #448 renders one event at a time).
2. `scripts/s1_train/view.py`: a CLI that reads a frozen S1 build and a session export, finds every source id of the
   build in the export's stream, and writes one view row per id (its stream file, its state's end, its candidate, its
   label and split) and a summary of counts and digests (no session text). The same inputs give byte-identical outputs.

## BOUNDARY

- CREATE `scripts/s1_train/__init__.py` (empty), `scripts/s1_train/render.py`, `scripts/s1_train/view.py`.
- CREATE `tests/test_s1_train_view.py` (both modules; fixtures only).
- READ, never modify: `scripts/session_export.py` (the event schema; its CLI makes the fixture exports),
  `scripts/s1_scores.py` (`PLAIN_EVENTS`, `HOOK_ERROR_RX`, `injections_of`, `stamp_of`: the ONE reading of what a hook
  handed the model and of a stamp), `scripts/hook_context.py` (`STAMP_RX`, `request`, `stamp`: the ONE stamp format),
  `scripts/laya_ft/build_s1.py` (`chunk_of`, `write_split`), `scripts/laya_ft/common.py` (`load_dataset`,
  `join_labels`, `label_key`, `jsonl_lines`, `sha256_hex`), `scripts/transcript_export.py` (`scrub_payload`),
  `tests/test_session_export.py` (how a test builds a fixture transcript tree, a FAKE pseudonym key with `init-key`, a
  fixture repo, and an export with `--known-values key-only`; its canaries show how a FAKE secret is built at run time).
- Every other file is out of bounds. `scripts/transcript_export.py` is hashed by the DSV2 record, and
  `scripts/session_export.py` is under verification now (VERIFY-SESSION-EXPORT-R3 runs on it): a defect you find there
  goes in the report.

## THE INPUTS (shapes at the PIN; copy, do not redesign)

**The export** (`scripts/session_export.py export --out <dir>`): `<dir>/manifest.json`, whose `sources` list has one
entry per transcript file with (among others) `src`, `output` (the `.jsonl.xz` file, relative to the export directory)
and `output_sha256` (the sha256 of that file's bytes); one `.jsonl.xz` per transcript file, one JSON event per line, in
record order, each with exactly the keys `seq, src, line, ts, role, kind, tool, call_id, text, truncated, outcome,
model, stop_reason`. A hook event's `text` is the canonical JSON of the transcript's attachment (`attachment()`:
`canon(a)`), so its `type`, `hookEvent`, `toolUseID` and `content` are readable; a `system` record of subtype
`stop_hook_summary` is a hook event whose JSON `type` is `system`; a `Stop hook feedback:` user text is a hook event
with plain text. In the main transcript the person is `owner` and the model `coordinator`; in a lane's transcript the
coordinator's messages are `coordinator` and the lane's model is `agent` (`speaker`, `assistant`).

**The S1 build** (written by `build_s1.write_split`): `<build>/train/` and `<build>/heldout/`, each with
`dataset.jsonl`, `labels.jsonl` and `manifest.json`, and `<build>/summary.json` (its `commit` is the build's commit). A
dataset row has `item_id, options, question, question_id, question_sha, sources, state, state_sha` (and `cut` when the
fit cut a field); `sources` is a list of `{id, kind: "injection", source, time}`, and one row can hold several sources
(identical states merged). A labels record has `key, sent_state_sha, question_sha, options, target, answer, model,
endpoint, ...`; `target` is `[0.0, 1.0]` (true) or `[1.0, 0.0]` (false) over the options `["false", "true"]`.
`common.load_dataset(<split dir>)` reads and verifies a split; it loads both real splits at the PIN.

## PINNED DECISIONS (a conflict with the tree is a STOP-and-report)

**D-1 The render.** `render(events, counts=None) -> (text, starts)` takes the events of ONE export file in file order;
`starts[i]` is the offset in `text` where event i's block begins (the length of every block before it, so it is
defined for an event that renders nothing). `block(event, counts=None) -> str` gives one event's block,
`"<label>: <body>\n\n"`, or `""`:

| (role, kind) | label | body |
|---|---|---|
| (owner, text), (coordinator, text), (agent, text) | `Owner`, `Coordinator`, `Agent` | the text |
| (coordinator, tool_call), (agent, tool_call) | `Coordinator calls <tool>`, `Agent calls <tool>` | the text (the input) |
| (tool, tool_result) | `Result of <tool>` (`?` when tool is null) | the text |
| (hook, hook) | `Hook` | what the hook handed the model, below |
| (system, summary) | `Summary` | the text |
| (coordinator, thinking), (agent, thinking), (system, notification), (system, harness_notice), (system, api_error), (tool, file_change), (tool, pruner_archive) | none: `""` | |
| any other pair | refused: `UnknownPair`, the pair named | |

A hook event's body: its text parsed as JSON; a dict whose `type` starts with `hook_` gives the texts
`s1_scores.injections_of({"type": "attachment", "attachment": a})` returns, joined by `"\n"` (a
hook_additional_context's content; a hook_success's content only for `PLAIN_EVENTS`; a blocking error's message;
nothing else); a dict of any other type gives nothing; a text that is not JSON gives itself when it starts with
`Stop hook feedback:`, and nothing otherwise (counted `hook_unparsed`).

The body, in this order: `transcript_export.scrub_payload(body)` (no opaque callable; counted `scrub_changed` when it
changed anything); `"\r\n"` and `"\r"` to `"\n"`; every run of two or more `"\n"` to one `"\n"` (the blank line is the
block separator); strip; empty gives `""`; over 4,000 characters, the first 3,000, then `"\n[... N characters cut
...]\n"` (N = length minus 4,000), then the last 1,000 (counted `cut`). A thinking block's text never reaches any
output. `VERSION = "s1-render-v1"`; the constants are module-level names.

Rejected: the labels `User` and `Assistant` (in a lane the coordinator is the user, in the main session it is the
assistant; the export's own roles need no perspective rule and are the same at serving time); notifications and harness
notices (harness text the export keeps for the record, 9,730 and 776 events, 1,847 of them already cut; a later version
may add them, under a new VERSION); no cap (a few events run past 100,000 characters, and D-126's live reader reads
about 333 tokens a second on 3 threads); removing S1-RATE lines (the live stream holds them; they are the history's own
record of what helped); hook_success stdout for tool events (the harness parses a JSON stdout and hands the model the
additional context alone: `s1_scores.PLAIN_EVENTS`).

**D-2 The carrier and the candidate.** A build source id is found where the ONE reader finds a stamp: in a hook event,
`s1_scores.stamp_of(kind, text)` over each `(kind, text)` that `injections_of` returns for its attachment; in a
tool_result event whose text `s1_scores.HOOK_ERROR_RX` matches (a hook that denied the tool: the search-intercept case;
`injections_of` keeps such a result for the same reason), `stamp_of("tool_result", text)`. That event is the carrier. The candidate is `build_s1.chunk_of(stamped, whole)`, where `whole` is true when the stamped text's last
line (after `rstrip("\n")`) equals `hook_context.request(id)`, then the body rules of D-1 without the cap (scrub,
newlines, strip). An id with two carriers, in one file or two, is not found (`ambiguous`), never guessed. The stamp's
source must equal the build source's `source`, else refuse.

**D-3 The state.** An id's state ends where the run of hook events that holds its carrier begins: from the carrier, walk
back over events whose kind is `hook` (for a tool_result carrier, walk back from the tool_result). The run's first event
(or the carrier, when no hook precedes it) is `state_event`; `state_end = starts[<its index>]`. The hooks of one call
run in parallel and never see each other's output, so no hook text of that run is in the state. Checks per id: the
rendered text holds the id nowhere before `state_end` (`text.find(id) >= state_end`; else refuse, the id named); for a
PreToolUse or PostToolUse carrier, a tool_call whose `call_id` equals the carrier's `toolUseID` lies before
`state_event` (`step_found`, counted; its seq is `step_event`); for a tool_result carrier, the tool_call with its
`call_id`.

**D-4 The label and the split are the build's, never recomputed.** Each source id of a row in `<build>/train` or
`<build>/heldout` takes that split and the row's label (the joined target `[0.0, 1.0]` is `true`, `[1.0, 0.0]` is
`false`; anything else, a row with no label record, or a source id in two rows is refused).

**D-5 Inputs are verified before use.** Each export file's sha256 equals its manifest entry's `output_sha256`; its xz
data is read whole by one `lzma.LZMADecompressor` and refused when the stream is cut (`eof` false) or bytes follow it
(`unused_data`; AF-AP-255: `lzma.open` drops such bytes silently); `seq` strictly increases within a file. The splits
load through `common.load_dataset`, and each `labels.jsonl` matches its manifest's `labels.sha256`. Any failure: exit
2, nothing written.

**D-6 The outputs.** The CLI: `python3 scripts/s1_train/view.py --build <S1 build dir> --export <export dir> --out
<dir>`. `--out` must not exist, or be an empty directory (else exit 2); it lives outside git. AMENDED 2026-10-02
11:5xZ (D-134): an `--out` with a `..` part is refused (exit 2), since a missing part before it let `missing/../E` replace
a full directory's outputs (task #460's B2).
`view.jsonl`: one row per found id, sorted by (`src`, `state_event`, `id`), exactly the keys `id, item_id, split, label
(a JSON boolean), source, time (the build source's), src (the manifest entry's src: the transcript file the stream
came from; its stream file is that entry's output), carrier (the kind
injections_of gave, or "tool_result"), hook_event (the attachment's hookEvent, or for a tool_result carrier the event
HOOK_ERROR_RX names), call_id, step_event (or null), state_event, state_end, candidate, candidate_sha256`.
`summary.json` (no session text): `version` ("s1-view-v1"), `render` (`VERSION`, cap 4,000, head 3,000, tail 1,000),
`code` (path: sha256 for render.py, view.py and each module they import from `scripts/`), `inputs` (the build's
`commit` and each of its files' sha256; the export's `export_id`, `code_sha256` and the number of files verified),
`counts` (build_ids, found, not_found by reason, by carrier, by hook_event, by split, by label, step_found,
time_equal (the build source's `time` equals the carrier event's `ts`), candidate_vs_chunk (`equal`, `equal_prefix`,
`differs`: the candidate against the build row's `state.chunk` under the same newline rule), hook_run_before (`0`,
`1+`), and the render's counts), `streams` (keyed by the manifest entry's src: events, rendered events, characters,
the sha256 of the rendered text; task #441 checks its own render against it). Stdout: one line of counts. Exit 0 done, 2 refused (the
reason on stderr).

**D-7 Determinism.** No clock, no host path, no randomness in either output; two runs over the same inputs are
byte-identical.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below at your HEAD; stop and report on a mismatch.
2. Fixtures through the REAL producers: a session tree (a main transcript and one lane transcript, raw records modeled
   on `tests/test_session_export.py`'s builders), exported by the real exporter (`init-key` FAKE key, a fixture repo,
   `--known-values key-only`); a frozen build written by `build_s1.write_split` over constructed rows. The session holds:
   an owner prompt; coordinator text; a Bash call with a PreToolUse S1 injection written as the harness writes one (a
   hook_success whose stdout is the JSON and whose content is empty, then the hook_additional_context); its result; a
   PostToolUse S1 injection; a UserPromptSubmit injection after a prompt; a denied Grep whose is_error result's first
   line ends `]: [S1 <id> search-intercept]`; a SessionStart hook_success with plain stdout; a thinking block; a
   notification; a compaction summary; two parallel calls whose hook runs follow each other; two S1 injections on one
   call; a build id absent from the stream. Normal tests: every present id found once, with the expected carrier,
   state_event, state_end, candidate (equal to the text that was stamped), label and split; the render of the fixture
   equals an expected string written out in the test.
3. Failure tests, each asserting the exact exit code and the named reason: an id missing (counted `not_in_export`, exit
   0); an export file whose bytes differ from the manifest's sha256; bytes after the xz stream; a cut xz stream; an
   unknown (role, kind); seq not increasing; a build row with no label; a source id in two rows; an id with two carriers
   (counted `ambiguous`); a stamp source that differs from the build's; `--out` not empty.
4. Security-boundary tests: a marker planted in a thinking block is in no output and no rendered stream; a FAKE key
   (built at run time as the exporter's tests build their canaries, never a literal) planted in an export event after
   the export (the test updates the manifest's sha256) is in no output; no state holds its own id; no hook text of the
   carrier's run is in that id's state.
5. Determinism: two runs, byte-identical outputs.
6. Mutants on a scratch copy of your files (one exact edit each, the baseline green first), each red on a named test:
   thinking rendered; the state cut at the carrier instead of the run; hook_success content rendered for PreToolUse; the
   cap off; the tail dropped from the cap; the scrub off; the request line kept in the candidate; the stamp line kept;
   the label taken from the other split; the sha256 check off; the trailing-bytes check off; an unknown pair rendered;
   each file read twice (AF-AP-254); seq order unchecked. Paste the table.
7. Tests run twice: `bash scripts/test_summary.sh --basetemp <scratch dir> tests/test_s1_train_view.py` (the counts
   pasted from its `pytest-summary:` line) and `bash scripts/pc_suite.sh set-id -- tests/test_s1_train_view.py`. Keep
   the fixtures small: the file should run in under two minutes.
8. Gates: pyflakes on every file you write; `python3 scripts/ap_screen.py <your files>` (paste its tells and answer
   each); the separator check on every file you write (`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0).
9. NOT run here: the real build. The coordinator runs `view.py` over the real export and the frozen build after
   landing and compares its counts with the prototype's (below); you never read those files.

## STANDING RULES

No outward-facing action (no push, PR or comment); no network; no PC bridge. Never commit, stash, checkout or reset in
`/home/user/agent-factory` (the coordinator commits). Never read `.jev/`, the coordinator's scratchpad, `/root/.codiv/`,
`.pc-bridge.env`, any `*.env`, the pseudonym key under `/root/.config/session-export/`, or a real transcript under
`/root/.claude/projects/`; never run the exporter with `--known-values default`, nor `scripts/known_values_check.py`
with its default sources. FAKE strings for anything secret-shaped, built at run time. Long commands in ONE foreground
call; no background job. A pytest `--basetemp` parent must exist first. Every test run with
`PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1`, no `-n`. Your final message is the report: files and
lines, the pasted counts, the mutant table, discrepancies, and what is NOT done.

## PREMISE — MEASURED at authoring (2026-10-01 19:5xZ, /home/user/agent-factory@f7f78165)

Re-run each command at your HEAD; its output must match.

```
$ git rev-parse --verify f7f781658ccd010883f79f759847b5bbd333b2d1^{commit}
f7f781658ccd010883f79f759847b5bbd333b2d1
$ git merge-base --is-ancestor f7f781658ccd010883f79f759847b5bbd333b2d1 HEAD && echo the PIN is an ancestor of HEAD
the PIN is an ancestor of HEAD
$ git diff --stat f7f781658ccd010883f79f759847b5bbd333b2d1 HEAD -- scripts/session_export.py scripts/s1_scores.py scripts/hook_context.py scripts/laya_ft/build_s1.py scripts/laya_ft/common.py scripts/transcript_export.py tests/test_session_export.py | wc -l
0
$ ls scripts/s1_train tests/test_s1_train_view.py 2>&1 | sed 's/^ls: //'
cannot access 'scripts/s1_train': No such file or directory
cannot access 'tests/test_s1_train_view.py': No such file or directory
$ git grep -l s1_train f7f781658ccd010883f79f759847b5bbd333b2d1 -- scripts tests harness-ports | wc -l
0
$ grep -n '^ID_RX\|^SOURCE_RX\|^STAMP_RX = \|^REQUEST = \|^def request\|^def stamp(' scripts/hook_context.py
51:ID_RX = r"s1-[0-9a-f]{8}"
52:SOURCE_RX = r"[A-Za-z0-9_.-]+"
53:STAMP_RX = re.compile(r"\[S1 (" + ID_RX + r") (" + SOURCE_RX + r")\]")                   # the first line, whole
56:REQUEST = ('Begin your next text with "S1-RATE {id} rel=R use=U" (+ a note <=120 chars: why, if a 0), one line per '
66:def request(sid):
71:def stamp(text, source, sid):
$ grep -n '^PLAIN_EVENTS\|^HOOK_ERROR_RX\|^TAIL_STAMP_RX\|^def injections_of\|^def stamp_of' scripts/s1_scores.py
67:PLAIN_EVENTS = ("UserPromptSubmit", "SessionStart")        # the events whose plain stdout reaches the model
70:HOOK_ERROR_RX = re.compile(r"([A-Za-z]+):(\S+) hook error: \[")
71:TAIL_STAMP_RX = re.compile(r"\]: (" + hc.STAMP_RX.pattern + r")\Z")   # a stamped stderr, after the harness's prefix
117:def injections_of(r):
160:def stamp_of(kind, text):
$ grep -n '^def chunk_of\|^def write_split\|^QID\|^VERSION\|^PROVENANCE' scripts/laya_ft/build_s1.py
40:QID = "s1.inject"
41:VERSION = "s1-v1"
46:PROVENANCE = "s1-rate live score"
159:def chunk_of(stamped, whole):
308:def write_split(out, name, pairs, base, ts):
$ grep -n '^def load_dataset\|^def join_labels\|^def label_key\|^def jsonl_lines\|^def sha256_hex\|^DATASET_FILE\|^MANIFEST_FILE' scripts/laya_ft/common.py
22:DATASET_FILE = "dataset.jsonl"
23:MANIFEST_FILE = "manifest.json"
97:def sha256_hex(data):
127:def label_key(item_id, question_id):
143:def jsonl_lines(text):
221:def load_dataset(ddir, heldout=None):
302:def join_labels(rows, labels):
$ grep -n '^def scrub_payload' scripts/transcript_export.py
182:def scrub_payload(text: str, opaque=None) -> str:
$ grep -n 'ORIGIN_ROLE = \|self\.emit(n, ts, \|return "system", "summary"\|return "hook", "hook"\|return ("owner" if self.main\|role = "coordinator" if self.main' scripts/session_export.py
145:ORIGIN_ROLE = {"human": "owner", "coordinator": "coordinator", "peer": "agent"}
601:            return "system", "summary"
603:            return "hook", "hook"
610:        return ("owner" if self.main else "coordinator"), "text"
635:            self.emit(n, ts, "system", "notification", canon(r))
643:            self.emit(n, ts, "system", "api_error", _text_of(content), model=model, stop_reason=stop)
645:        role = "coordinator" if self.main else "agent"
647:            self.emit(n, ts, role, "text", content, model=model, stop_reason=stop)
652:                self.emit(n, ts, role, "text", b.get("text") if isinstance(b.get("text"), str) else "", model=model,
656:                    self.emit(n, ts, role, "thinking", b["thinking"], model=model, stop_reason=stop)
665:                self.emit(n, ts, role, "tool_call", text, tool=name, call_id=cid, mode=mode, model=model,
668:                self.emit(n, ts, role, "text", canon(b), model=model, stop_reason=stop)
677:                self.emit(n, ts, role, kind, text)
688:                self.emit(n, ts, role, kind, _text_of([b]))
706:        self.emit(n, ts, "tool", "tool_result", text, tool=name, call_id=cid, outcome=outcome, mode=mode)
709:            self.emit(n, ts, "tool", "pruner_archive", read_archive(entry), tool=name, call_id=cid, mode=mode)
719:                self.emit(n, ts, "tool", "file_change", body, tool=name, call_id=cid,
735:                self.emit(n, ts, role, kind, text, mode=mode)
737:            self.emit(n, ts, "hook", "hook", canon(a), mode=mode)
739:            self.emit(n, ts, "system", "harness_notice", canon(a), mode=mode)
741:            self.emit(n, ts, "system", "notification", canon(a), mode=mode)
747:            self.emit(n, ts, "system", "api_error", body)
753:            self.emit(n, ts, "hook", "hook", body, outcome=outcome)
755:            self.emit(n, ts, "system", "notification", body)
$ grep -n '"output_sha256"' scripts/session_export.py
990:    return {"src": src, "offset": offset, "input_sha256": sha, "output": src + ".xz", "output_sha256": sha256_file(dest),
$ grep -n '^def _run\|^def _key\|^def _export\|"init-key"' tests/test_session_export.py
465:def _run(*args):
469:def _key(where):
472:    r = _run("init-key", "--key", path)
477:def _export(tree, out, key, *extra, jobs=2):
833:    r1 = _run("init-key", "--key", path)
838:    r2 = _run("init-key", "--key", path)
860:    assert "init-key" in _export(tree, tmp_path / "o9", tmp_path / "missing.key", jobs=1).stderr
1536:def _key_file(where, key):
$ PYTHONDONTWRITEBYTECODE=1 python3 -c "import sys; sys.path.insert(0, 'scripts'); import laya_ft.build_s1 as b, s1_scores as s, hook_context as h; t = h.stamp('A' + chr(10) + 'B', 'filepacks', 's1-00000000'); print(b.chunk_of(t, True) == 'A' + chr(10) + 'B', s.stamp_of('hook_additional_context', t)[:2], s.PLAIN_EVENTS)"
True ('s1-00000000', 'filepacks') ('UserPromptSubmit', 'SessionStart')
```

## What the real data showed (the coordinator, at the PIN; counts only; you never read these files)

The frozen build is `s1-2026-10-01-pushed` (its summary's commit 5be8cc0c); the export is the coordinator's 2026-10-01
export made at 5cf654e5 (390 sources, 202,346 events, gate total 0). Each block is a scratch script's output.

```
# kinds.py: the export's (role, kind) counts; thinking; hook_success content against stdout; the non-JSON hook events
files 390
== (role, kind)
  72343  ('tool', 'tool_result')
  43941  ('agent', 'tool_call')
  28416  ('coordinator', 'tool_call')
  12763  ('agent', 'text')
   9840  ('coordinator', 'text')
   9730  ('system', 'notification')
   9038  ('hook', 'hook')
   7854  ('agent', 'thinking')
   4361  ('tool', 'file_change')
   2543  ('coordinator', 'thinking')
    776  ('system', 'harness_notice')
    421  ('owner', 'text')
    227  ('system', 'summary')
     82  ('system', 'api_error')
     11  ('tool', 'pruner_archive')
== truncated by kind {'notification': 1847, 'tool_call': 59, 'tool_result': 23, 'text': 58, 'summary': 17, 'hook': 3}
== thinking {'text present': 10397}
== hook_success (hookEvent, content vs stdout, stdout shape)
   1672  ('PostToolUse', 'content empty', 'stdout {')
   1454  ('PreToolUse', 'content empty', 'stdout {')
    278  ('SessionStart', 'content==stdout', 'stdout text')
    198  ('SessionStart', 'content empty', 'stdout {')
     55  ('UserPromptSubmit', 'content==stdout', 'stdout text')
      8  ('PostToolUse', 'content==stdout', 'stdout text')
      6  ('UserPromptSubmit', 'content differs', 'stdout text')
      4  ('SessionStart', 'content differs', 'stdout text')
      2  ('SubagentStart', 'content empty', 'stdout {')
== non-JSON hook events (class, truncated)
    571  ('starts Stop hook feedback', False)

# hookshape.py: the hook events' attachment types, the stamped ones, and their key sets
== (type, hookEvent): count
   1680  ('hook_success', 'PostToolUse')
   1672  ('hook_additional_context', 'PostToolUse')
   1454  ('hook_success', 'PreToolUse')
   1446  ('hook_additional_context', 'PreToolUse')
   1317  ('system', '<none>')
    480  ('hook_success', 'SessionStart')
    183  ('hook_additional_context', 'UserPromptSubmit')
    165  ('hook_additional_context', 'SessionStart')
     61  ('hook_success', 'UserPromptSubmit')
      2  ('hook_system_message', 'SessionStart')
      2  ('hook_cancelled', 'UserPromptSubmit')
      2  ('hook_success', 'SubagentStart')
      2  ('hook_additional_context', 'SubagentStart')
      1  ('hook_system_message', 'PostToolUse')
== stamped (type, hookEvent)
   1266  ('hook_success', 'PreToolUse')
   1258  ('hook_additional_context', 'PreToolUse')
    833  ('hook_success', 'PostToolUse')
    833  ('hook_additional_context', 'PostToolUse')
     82  ('hook_additional_context', 'UserPromptSubmit')
== key sets
   3677  ('hook_success', ('command', 'content', 'durationMs', 'exitCode', 'hookEvent', 'hookName', 'stderr', 'stdout', 'toolUseID', 'type'))
   3468  ('hook_additional_context', ('content', 'hookEvent', 'hookName', 'toolUseID', 'type'))
   1317  ('system', ('hasOutput', 'hookAdditionalContext', 'hookCount', 'hookErrors', 'hookInfos', 'level', 'preventedContinuation', 'stopReason', 'subtype', 'toolUseID', 'type'))
      3  ('hook_system_message', ('content', 'hookEvent', 'hookName', 'toolUseID', 'type'))
      2  ('hook_cancelled', ('command', 'durationMs', 'hookEvent', 'hookName', 'timedOut', 'timeoutMs', 'toolUseID', 'type'))

# edges.py: the prompt-time injections' neighbours; the denied searches' shape (the stamp's offset in the first line, the request line's index from the end)
   16  UserPromptSubmit: before the run owner/text; after the run coordinator/text; run length 1
   11  UserPromptSubmit: before the run owner/text; after the run coordinator/text; run length 2
    3  UserPromptSubmit: before the run owner/text; after the run system/notification; run length 1
    3  UserPromptSubmit: before the run owner/text; after the run system/notification; run length 2
    2  UserPromptSubmit: before the run owner/text; after the run system/notification; run length 3
    3  UserPromptSubmit: before the run system/notification; after the run coordinator/text; run length 1
    1  UserPromptSubmit: before the run system/notification; after the run coordinator/text; run length 2
    1  UserPromptSubmit: before the run system/notification; after the run system/notification; run length 2
    1  tool_result: prefix chars 344; lines 15; request line index from end [1]; tail after request 0 chars; markers ['hook']
    3  tool_result: prefix chars 344; lines 8; request line index from end [1]; tail after request 0 chars; markers ['hook']

# sizes.py: the characters of the kinds D-1 renders (before the scrub and the newline rule), under per-event caps
rendered characters (uncapped): 261432200 in 176989 events
  tool_result     154914325 chars    72343 events
  tool_call        83874327 chars    72357 events
  text             11979157 chars    23024 events
  hook              5628989 chars     9038 events
  summary           5035402 chars      227 events
  cap   1000 chars per event:     88401794 chars (33.8%)
  cap   2000 chars per event:    126863994 chars (48.5%)
  cap   4000 chars per event:    168322023 chars (64.4%)
  cap   8000 chars per event:    207727827 chars (79.5%)
  cap  16000 chars per event:    239080510 chars (91.5%)
  event length p50: 378
  event length p90: 3380
  event length p99: 18343
  event length p99.9: 40543
  largest event: 113958
files: 386; the largest three: [(81137163, 31.0), (5202243, 2.0), (4264263, 1.6)]

# scrubtime.py: transcript_export.scrub_payload over 20 million characters of export text
texts 13515, chars 20011220, seconds 18.5, chars per second 1084124, changed 1347

# proto.py: D-1 to D-4 as written above, over the real export and the frozen build (ran 4 minutes; the landing's real run is compared with these counts)
      1091  build_ids
       432  candidate chars over 1000 False
       659  candidate chars over 1000 True
       432  candidate_vs_chunk equal
       659  candidate_vs_chunk equal_prefix
       323  carrier hook hook_additional_context PostToolUse
       724  carrier hook hook_additional_context PreToolUse
        40  carrier hook hook_additional_context UserPromptSubmit
         4  carrier tool_result PreToolUse
      1091  found
       220  found split heldout
       871  found split train
        30  hook run before 0
      1061  hook run before 1+
     14561  render cut
     15175  render scrub_changed
      1051  step_found True
 170573221  stream chars
      1091  time_equal
      1091  whole True
rc=0
```
