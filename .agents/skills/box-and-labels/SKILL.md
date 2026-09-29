---
name: box-and-labels
description: "The chat box and the stack labels (D-113, D-114): the box grammar, what each label runs, its inputs and its body, and the rules. Load before writing a box or a REQ line, choosing a label, or adding a stack to scripts/stacks.toml."
---

# The box and the labels

The owner's design (D-113, 2026-09-29): a word, the LABEL, names a reviewed sequence of tool calls, a STACK in
`scripts/stacks.toml`. A box drawn in the chat names the label and fills its inputs like a form. A hook runs the stack
with those inputs and answers with one receipt. D-114 (the owner, 2026-09-29): CLAUDE.md lists every label, and this
skill holds the details.

## State (measured 2026-09-29)

- The labels run today as a tool call: `python3 scripts/stack.py <label> key=value ...`. `python3 scripts/stack.py
  explain <label> ...` prints the plan and runs nothing. The SessionStart hook prints the catalog.
- The box is BUILT (LS-B11, task #380, landed GATED-PENDING-VERIFY) and NOT ON. Its hooks (LS-B10's Stop and prompt
  hooks, `tasks/briefs/labeling/LS-B10-registration.patch`) are not registered. Until they are, a box in the chat does
  nothing, and no nonce line is injected.
- A box's body runs only when it is one line of at most 500 characters (LS-B11 D4: the runner's text type refuses a
  newline). A longer body gets a plain refusal, never a run.

## The labels (`scripts/stacks.toml`)

| Label | What it runs | Inputs | Box body | Rated |
|---|---|---|---|---|
| `find` | graft ask, the owner's rulings, the chat search (`chat_find.py`, plain order), the AF-AP registry rows | `q` | `q` | yes |
| `ctx` | graft skeletons and ask, GitNexus impact, code-review-graph, ripwire, the AP screen | `files`, `q`, `sym` | `q` | yes |
| `impact` | GitNexus impact, code-review-graph callers and tests, ripwire edit-check | `sym` | none | yes |
| `review` | sentrux architecture health (check, save, compare), ripwire's test gate, the pyflakes delta, the AP screen | `files`, `mode` | none | yes |
| `gate` | every test that names each path, plus the tests ripwire's call graph links to the change | `paths`, `mode`, `runs`, `graph`, `max_files` | none | no |
| `echo` | a pattern across the six code roots, the incident log's lines, the AP screen over the files hit | `pattern`, `roots` | `pattern` | yes |
| `premise` | per file: tracked or not, sha256, line count, the last commit | `files` | none | no |
| `harvest` | a finished lane: its served models and refusal stops, its hand-back, the report linted and hashed | `agent`, `report` | none | no |
| `ci` | the branch's stage0-ci verdict through `scripts/ci_gate.py` | `branch` | none | no |

Task #385 (backlog) adds five labels: codebase-memory, GitNexus detect-changes, `scripts/why.sh`,
`scripts/jev_locate.py` and `scripts/jev_echo.py`, the two Jev tools in their plain order (no stack calls a model,
KC-J1, D-077). Each new label gets a row here and a word in CLAUDE.md's labels line (D-114).

## The box (LS-B11; the full grammar is the THE BOX section of `scripts/ls_req.py`'s docstring)

```
┌─ find · r1 · <nonce>
│ q: where does the scrubber hide bearer tokens
└─
```

- Top edge: `┌─ <label> · <id> · <nonce>`. The label matches `[a-z][a-z0-9-]{1,23}`, the id is new in the session and
  matches `[a-z][a-z0-9]{0,15}`, and the nonce is the current turn's 12 lower-case hex digits. One space goes on each
  side of each `·`. A run of `─` after the nonce is decoration.
- Inside lines start with `│ `. First come the inputs, one `key: value` per line. The key is a parameter name of the
  stack. The value is the rest of the line after `: `, and it reaches the runner as ONE argument, never a shell word.
- An optional divider `│ ┄┄┄` (three or more `┄`). The lines below it, without their `│ `, are the BODY. The body fills
  the parameter that the stack names as its `body` (the Box body column). A body for a stack with no body, a second
  divider, or an input line that also sets the body parameter makes the box malformed.
- Bottom edge: `└─`, with more `─` allowed. There is no right edge.
- A box may sit inside a fence (three backquotes, a language word allowed). Boxes and REQ lines may follow each other.
  After the first request of a message, only requests, blank lines and fence lines may follow; any other text refuses
  every request of that message as malformed.
- Receipts: one per box, `RES <nonce> <id> <status>`, the run's result or a plain refusal (`refused: malformed
  (<why>)`, `refused: stale nonce`, ...), never silence. A well-formed box with an old nonce gets `refused: stale nonce`.
  A box broken on its own grammar and without the current nonce is an illustration (the example above): no receipt.
- The one-line fallback (LS-B10): `REQ <nonce> <id> <label> key=value ...`.
- The runs of one Stop round share a 240 s budget. Every request and its receipt is kept in `<main>/.jev/req/` as a
  labelled example (`form: "box"` or `form: "req"`). The off switch is the file `<main>/.jev/req-off`.

## Rules

- A box never carries a shell command or a script (D-111: the Stop hook runs outside the permission checks). The label
  comes from the registry, and the runner refuses an unknown input.
- No stack calls a model (KC-J1) or acts outward; `scripts/stack.py` refuses a registry that tries.
- After a rated stack's run, rate it: `--rate <run id>=<rel>/<use>` on the next stack call, or `python3
  scripts/stack.py rate <run id>=<rel>/<use>` (0 to 3 each). The ratings are System 1's data.
- When unsure what a label will run, run `explain` first.
- Adding or changing a label is a reviewed edit of `scripts/stacks.toml` with its tests in `tests/test_stack.py`, a row
  in this table, and a word in CLAUDE.md's labels line (D-114). The recipe is skill `label-authoring`.
