---
name: label-authoring
description: "How to make a new stack label (D-114): when a tool or a repeated multi-step check deserves a label, the scripts/stacks.toml schema, the rules every label keeps, its tests, and where it gets listed. Load before adding or changing a stack in scripts/stacks.toml."
---

# Making a new label

The owner (D-114, 2026-09-29): "if we get new tools or we find new things, we can create labels and scripts for them
... and then it'll just be another label." A label turns a check that would take four to six tool calls into ONE call.
It runs the same way every time, its output is capped, and each run is logged. This skill is the recipe. Skill
`box-and-labels` covers using the labels.

## When a label is worth making

- The same read-only sequence has run by hand more than twice. The stack's `replaces` field names what it replaces.
- A new instrument arrives (a code-intel tool, a checker). Give it a label in the SAME increment that installs it.
- One label answers one question ("who calls X", "what breaks if X changes"). A label is not one per tool.

## The recipe

1. **Measure each step's interface first** (build-loop, the seam rule). Run each command by hand on the real tree. Note
   its exit codes (a search that finds nothing often exits 1, so `ok_rc` lists 1), its output size, and what it prints
   when its tool is missing.
2. **A step that needs new logic gets a script.** Write it under `scripts/` with its own tests, and call it from the
   step. A step's `argv` is a list of words, never a shell string: no pipes, no `&&`, no redirection.
3. **Add the stack to `scripts/stacks.toml`:**

   ```toml
   [stacks.<label>]
   summary = "<one line: the question the label answers>"
   replaces = "<the calls it replaces>"
   outward = false
   rated = true            # content stacks only: each run takes a relevance and use score
   body = "<param>"        # optional: the parameter a box's body fills
   notes = ["<one-line caution>"]

   [stacks.<label>.params.<name>]
   type = "text"           # path, paths, symbol, symbols, text, word, words, agent, choice, int
   required = true

   [[stacks.<label>.steps]]
   id = "<step id>"
   argv = ["python3", "scripts/<tool>.py", "{<name>}"]
   group = 1               # steps of one group run side by side; a later group runs after
   timeout = 120
   cap_lines = 30
   ok_rc = [0, 1]
   ```

   - Stack keys: summary, replaces, outward, rated, params, steps, notes, body. Parameter keys: type, required,
     default, choices, split_from. Step keys: id, argv, group, timeout, cap_lines, ok_rc, required, when, repeat,
     foreach, unmapped_if, tool, save_cap_mb, empty_ok, needs, headline. `scripts/stack.py` refuses any other key.
   - Defaults: group 1, timeout 60, cap_lines 40, ok_rc [0], required true, save_cap_mb 20.
   - Placeholders: `{name}` for one value; `{name*}` for a list, one argument per item; `{name,}` joins a list with
     commas; `{name*:-e}` puts `-e` before each item. Built-ins: `{tree}`, `{run}`, `{main}`, `{head}`, `{branch}`,
     `{each}`, `{transcript}`, `{tmp}`. No other braces are allowed in an argument.
   - A step whose tool can be missing carries `unmapped_if` (the text the tool's wrapper prints when it is absent), so
     a missing tool reads `unmapped`, never ok.
   - Chaining: `foreach = "@<step>"` runs a step once per output line of an earlier step (as `{each}`); `needs` runs a
     step only when the named earlier steps ended ok.
4. **Check it:** `python3 scripts/stack.py explain <label> ...` prints the plan and runs nothing. Then do one real run
   and read its sections.
5. **Test it** in `tests/test_stack.py`: the committed registry loads with the new stack, `explain` shows its plan, and
   a negative control refuses a bad input with its exact message.
6. **List it (D-114):** a row in `box-and-labels`'s table, and a word in CLAUDE.md's labels line.
7. **Land it through the build loop:** gate every test that names a changed file.

## The rules every label keeps

- Read-only and inward: no step pushes, posts or publishes, and nothing is written outside the run directory.
  `outward = true` is refused when the registry loads.
- No model calls (KC-J1: no Laya or Jev in a gate). A tool with an optional model mode runs in its plain mode, as the
  `find` stack runs `chat_find.py --order lexical --no-jev-log`.
- No shell. Each `argv` element is one argument. A box never carries a command or a script (D-111).
- A label's output is evidence, never a verdict. The reader still judges.

## Ideas the owner ruled in (D-115, 2026-09-30), NOT built yet

- **Jev-powered steps (task #391).** The owner (D-114): "even jev powered scripts"; D-115: "yes, have jev powered
  labels". They form a separate ADVISORY class of stacks: marked as model-backed in the registry and the catalog, never
  used as a gate (KC-J1 still holds for `gate`, `review`, `ci` and every proof), and measured against the plain order
  before one replaces a plain label (D-077: in the A3 benchmark, Jev did not beat the plain order). Until task #391
  builds the class, `scripts/stack.py` still refuses a model call in any stack.
- **Per-agent label sets (task #392).** The owner (D-114): "each agent will have their own set of labels"; D-115: "yes".
  One possible shape: a per-stack list of the agent types that may use it, and a catalog printed per agent type. It
  needs a design pass and a change to `scripts/stack.py`, after task #391.
