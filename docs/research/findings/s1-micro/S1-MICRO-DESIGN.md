# S1 micro-output: where a few tokens help, and how they stack (task #467)

STATUS: DESIGN, 2026-10-02 08:0xZ, the coordinator. Inputs: D-133 (the owner's three messages, 06:06Z to 06:33Z), the
evidence map beside this file (`S1-MICRO-MAP-evidence.md`, tables T1 to T6 and contradictions C1 to C9), and the slot
probe beside it (`copyable_probe.py`, its output in `copyable-2026-10-02.txt`, counts only). NOT built: everything
below. Nothing here touches a gate.

## 1. The short answer

**Point, do not write.** Most values a label call needs are already in the session stream that the RWKV state reads. So
the micro-output is mostly a few POINTERS into that stream, which deterministic code expands into exact values. Real
generated text is the rare case: one short free slot in a form.

**That splits the owner's hybrid cleanly.** The fast path (a choice plus pointers) fits the 40 ms budget. The slow path
(one short free text) runs only when a form needs it.

**It stacks under the standing rule "Jev finds, deterministic code blocks"** (JEV-LEVERAGE-AUDIT §3). The model
proposes a filled form. Code expands and checks it. The same runner and policy hooks run it. The model gains no new
authority.

## 2. The measurement: most slot values are already in the stream

The probe walked every transcript of this session (359 files, main thread and subagents) in order. For each tool call it
asked: does each variable value of the call already appear in the stream before it? "The stream" is what the S1 view
renders (prompts, texts, tool inputs, tool results; never a thinking block). "Appears" means a substring of the last 50
events (each capped at 20,000 characters) or an exact token anywhere earlier in the same transcript.

| Slot class (in Bash commands) | Values | In the last 50 events | Anywhere earlier (token) | Either |
|---|---|---|---|---|
| number | 292,471 | 95.1% | 97.9% | 99.0% |
| hex id (run ids, commit ids) | 12,248 | 85.8% | 95.5% | 98.4% |
| path | 276,575 | 71.8% | 76.7% | 81.0% |
| quoted string | 448,146 | 47.7% | 31.6% | 51.2% |

For the file path of the file tools: Edit 97.8% (4,540 calls), Read 67.1% (3,763), Write 9.2% (1,747; a new file).

**The form view.** A label covers a command SHAPE (the command with its values replaced). In a repeated shape, a value
that recurs in the same slot is a constant of the form, not free text. Counting a value seen 3 or more times in its
slot as a form constant:

| Shapes seen | Commands | No free slot | Exactly one free slot | The free values |
|---|---|---|---|---|
| 50 or more times | 4,093 | 26.5% | 71.5% | 3,090; median 17 characters (p75 59, p90 185); 2,811 are quoted strings |
| 10 or more times | 7,205 | 32.9% | 62.1% | 5,271; median 33 (p75 93, p90 393) |
| 2 or more times | 13,979 | 34.6% | 47.7% | 16,958; median 30 (p75 82, p90 229) |

**What this means.** In the commands that repeat most, 98.0% need at most one value that a pointer cannot supply, and
that value is almost always a short quoted string (a search pattern, a question, a message). The long tail (p90 of 185
to 393 characters) is code: inline scripts and heredocs. That stays with the main model.

Limits of the probe: it counts this session only; "free" means "not in the stream as typed", so a value the model could
infer but not copy counts as free; the form-constant rule (3 times in a slot) is a heuristic; the shapes are of typed
Bash commands, not of label calls, which do not exist yet for most kinds.

## 3. The rule per slot: point first, generate last

| Slot class (T3's classes) | Output form | Generated tokens | Expansion |
|---|---|---|---|
| (a) a closed set (a choice, a mode, a flag) | a choice head over the set | 0 | none |
| (b) a reference to the stream (a path just edited, an agent id just returned, a run id just printed) | a HANDLE: a short tag that the render gives each entity as it enters the stream | 1 | deterministic lookup |
| (c) text the stream holds (an error line, a symbol, a test name) | a span: the handle of an event plus start and end positions | 2 or 3 | deterministic slice |
| (c) text the stream does not hold (a new pattern, a question) | generated under a closed grammar, ended by a stop token, capped in length | a few | the parameter's own check; a failed check means no suggestion |

**Copy beats generate.** A copied value cannot hold a character the stream did not hold, cannot invent a path, and
inherits the scrub the stream already passed (D-118). Today's registry fits this rule well: of its 27 parameters, 5 are
closed sets, 15 are references and 5 are free text bodies, plus one bounded int and one derived value (T3b).

## 4. The stack, layer by layer

| Layer | Exists today (T5) | Missing |
|---|---|---|
| 1. State stream | `scripts/session_export.py`, `scripts/s1_train/render.py`, `scripts/s1_train/view.py` (offline) | a live reader that streams events into the state (task #448); per-role states (task #453); entity handles in the render |
| 2. Choice heads | the `s1.inject` question, its dataset and baselines | the heads and their pre-registration (task #441) |
| 3. Micro-output head | nothing | everything (task #467) |
| 4. Deterministic expansion and checks | `scripts/stack.py`'s parameter checks (`check_path`, `check_scalar`, VALUE_RE, the deny lists), `scripts/ls_req.py`'s box and REQ grammar | a resolver from a handle to a value (`pre_resolve` reads only the request, the registry and the environment) |
| 5. Runner and policy | `scripts/stack.py` (argv only, no shell, no outward step), the Stop-hook runner in `ls_req.py`, the KC-J1 screen | nothing new: a suggestion enters as a request, so every existing check applies |
| 6. Feedback | S1-RATE, the stack ratings, the box receipts | an accepted, edited or rejected signal per suggestion |

**The micro-output adds one layer (3) and one function (the handle resolver in 4).** Layers 5 and 6 stay as they are.
That is the "properly stacked" part: the model sits upstream of the same checks a typed call meets.

## 5. Where it helps beyond labels

The owner's first example is a label call with its slots filled. The map's decision points (T1, T2) show more places
where a pointer or a short text closes a gap:

1. **Label calls.** Paths, symbols, agent ids and branches by handle; most calls need zero generated characters.
2. **Forms for the kinds no label covers (T4).** Reads (a path and a line range), tests (paths and a revision), waits
   (a pid or a run id) and PC jobs (a run id) are already form-shaped. They become labels first (task #465 names five),
   then the head fills them.
3. **The search intercept (H3).** Today the graft question is the raw grep pattern. A span from the agent's own words
   before the call (the `intent` field of the S1 state) can ask a better question. The block decision stays the fixed
   rule's.
4. **The pruner's marker (H14).** When chunks are dropped, a one-line marker copied from the dropped text (a test
   summary line, an error line) tells the agent what went. This also lowers the risk KC-J5 names (C6).
5. **The injection hooks (H1, H2, H6).** A pointer to WHICH line of a section governs the step, so a hook shows one line
   instead of a whole excerpt.
6. **Bookkeeping (H10, F44).** A ledger headline's event word (a closed set) and task id (a reference); the body stays
   with the coordinator.
7. **Report digests and the done check (P7, P8).** Pointers to the findings and files a claim rests on.

## 6. Where it must never go

1. **A gate or a predicate** (KC-J1): the `gate`, `review` and `ci` labels, the proofs, and every policy decision.
2. **Its own feedback.** An S1-RATE score or a stack rating comes from the consumer, never from the model it grades.
3. **An outward action.** Labels are inward by design (D-113 item 2): no commit, push or PC write from a suggestion.
4. **Free-form code.** The long tail of free values is code, and it stays with the main model.

## 7. Latency: two paths

| Path | What runs | Sandbox, 3 threads (RWKV-CPU-2026-10-01) | PC |
|---|---|---|---|
| fast | the choice and up to one handle | about 21 ms a token generated (46.0 to 47.7 tokens a second) | not measured |
| slow | one free slot, median 17 characters (about 5 tokens) | about 100 ms | not measured |
| ingestion | each new event read into the state | about 333 tokens a second (about 425 on 4 threads) | not measured |

**Reading is the real cost, not writing.** A 10,000-token tool result takes about 30 s to stream into the state on 3
sandbox threads. So the live reader ingests as events arrive (never at decision time), and the render's caps (4,000
characters a block today: the first 3,000 and the last 1,000) bound it. One decision's latency through llama.cpp is not
measured (C7).

## 8. Order of work

1. **Close task #460 and run task #441** (the choice heads). The micro-output head reads the same state and is scored
   by the same evaluator.
2. **Measure on the PC:** generation and reading speed of RWKV-7 0.4B (and the 0.1B model) at 3, 6 and 12 threads, and
   one decision end to end.
3. **Grow the labels around repeated shapes** (task #465's five, then T4's form-shaped kinds). Each form declares its
   slots and their classes.
4. **Handles in the render:** `render.py` tags each entity as it enters the stream; a resolver in `stack.py` maps a
   handle back to its value and refuses an unknown one.
5. **A pilot head on one label** (`why file=` or `premise files=`), trained on this session's own calls and scored by
   one evaluator against plain baselines (the last path mentioned; the most frequent value), with the acceptance lines
   written before the run.
6. **Suggest only, live**, with the accept rate measured; then run read-only labels automatically; effectful labels
   never.

Vision and audio adapters come much later (the owner, D-133).

## 9. Gaps and contradictions this design depends on

- **C1, a claim with no check behind it.** Two skills say `scripts/stack.py` refuses a stack that calls a model
  (`box-and-labels` L88, `label-authoring` L83). stack.py has no such check (the map's grep; confirmed by the coordinator
  2026-10-02 08:0xZ). Today only a convention and two test pins hold it. A micro-output that produces label calls must
  not depend on it: task #469 builds the check or corrects the claim.
- **C6, drop mode.** KC-J5 says one harmful drop turns drop mode off everywhere; the pruner runs in drop mode (task
  #406). The marker in §5 item 4 is a mitigation, not a ruling.
- **C7, latency.** The 40 ms budget rests on sandbox generation speed; no decision has been timed end to end.
- **Constrained decoding.** No llama.cpp binary or `rwkv` package is on this machine, and build 0c1e570's grammar flags
  were not read (T6). llama.cpp's GBNF grammars are a claim from vendored skills until measured.
- **Pointers in a frozen model.** Task #441's contrastive heads choose among options; whether a frozen RWKV state can
  also pick handles without tuning its weights is open, and the pilot (step 5) is the test.
