# The pruner's floor, measured (2026-10-01 02:4xZ; task #415, D-123 item 1)

**TL;DR.** The pruner hook was alive but could not act. Claude Code shows a Bash output inline only up to about 30,000
characters, and in the week measured no inline output in the main thread reached the upstream floor of 10,000 estimated
tokens (0 of 9,982; in the lanes 4 of 19,270, 0.3% of their tokens). Above that size the harness saves the output to a
file, and the plugin's budget for a saved output is the 2 KB preview: a 183.4 KB test output drew 12 Jev calls and still
passed through untrimmed. Our copy now takes a floor of 1,000 tokens: that puts 41% of the main thread's inline Bash
tokens and 68% of the lanes' within the pruner's reach.

## The live test (02:31Z)

At 02:31Z a synthetic log (2,400 lines, `step NNNN worker ... processed batch ...`, no error words) went through the Bash
tool. The relay's `/health` counts went from 0 to 12 relayed (the upstream plugin's limit: one call plus 11), each 200,
0.9 to 2.8 s. The answers scored each 20-line chunk between 0.05 and 0.34. The plugin keeps a chunk above 0.1
(`src/retention.ts` `keepScore`), and the saved output's budget is the smaller of 8,000 characters and the preview the
model sees (about 2.3 KB), so the kept chunks could not fit: the original result passed through. The hook was loaded
(`CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` from the user settings' `env`); it had simply never met an output it could act on.

## The census (instrument: `scripts/tool_output_sizes.py`, the plugin's own token estimator, checked equal to it by node)

The distribution covers the inline results, the text the model received. A saved ("persisted") output is counted apart:
the model saw only its preview.

```
2026-10-01T02:47:58Z
$ python3 scripts/tool_output_sizes.py --since 2026-09-24 --tools Bash <main transcript>
Bash: results 9991 inline 9982 persisted 9 (source p50 252928 chars); inline: mean 345.2 p50 158 p75 405 p90 880 p95 1306 p99 2553 max 7765 (tokens; inline max 25153 chars)
  inline results above: >250 3685 >500 2006 >1000 813 >2000 193 >3000 63 >5000 10 >7500 1 >10000 0 >20000 0
  inline token share above: >250 0.828 >500 0.654 >1000 0.41 >2000 0.164 >3000 0.075 >5000 0.018 >7500 0.002 >10000 0.0 >20000 0.0
$ python3 scripts/tool_output_sizes.py --since 2026-09-24 --tools Bash <350 lane transcripts>
Bash: results 19305 inline 19270 persisted 35 (source p50 43417 chars); inline: mean 753.3 p50 368 p75 930 p90 1941 p95 2890 p99 5091 max 13186 (tokens; inline max 29308 chars)
  inline results above: >250 11561 >500 8042 >1000 4503 >2000 1834 >3000 899 >5000 211 >7500 30 >10000 4 >20000 0
  inline token share above: >250 0.945 >500 0.857 >1000 0.683 >2000 0.425 >3000 0.269 >5000 0.092 >7500 0.018 >10000 0.003 >20000 0.0
```

## The floor

| Floor (estimated tokens) | Main thread: inline outputs above, a week | share of its inline Bash tokens | Lanes: outputs above | share |
|---|---|---|---|---|
| 10,000 (upstream) | 0 | 0.0% | 4 | 0.3% |
| 2,000 | 193 | 16.4% | 1,834 | 42.5% |
| 1,000 (chosen) | 813 | 41.0% | 4,503 | 68.3% |
| 500 | 2,006 | 65.4% | 8,042 | 85.7% |

The mean inline output is 345 tokens in the main thread and 753 in the lanes; the median 158 and 368. A floor at the mean
would send most calls to Jev for a few lines each, and an output of 40 lines or fewer is at most two 20-line chunks, which
the plugin never trims (`few_chunks`, `src/output.ts:401`). 1,000 tokens is about 4,000 characters, some 50 lines of 80
characters, three chunks: about the smallest output with something to drop. It covers 813 outputs a week in the main thread (about 115 a day) and 4,503 in the lanes, each one to a few Jev
calls of about 1 to 3 s. The decision records (below) measure what the floor actually trims; the floor is a plugin option,
so a better value is one `claude plugin configure` away.

## What still passes untrimmed, by the plugin's own rules

- Output the plugin reads as a document: valid JSON, a diff, XML, `cat`/`jq`/`git diff`/`git show` commands, and any
  output with one line that looks like reference material (a markdown heading, a code fence, a `def`/`class`/`import`
  line; `src/retention.ts` `REFERENCE_PATTERN`, multi-line). Much of this repository's Bash output has such a line.
- A saved output whose kept chunks do not fit the preview budget (the live test's case).
- A chunk Jev scores above 0.1 stays, whatever the keep threshold.

## What changed (vendor/jev-pruner/PROVENANCE.md, local change 3)

- `baseUrl`: the hook sends Jev requests to the relay (127.0.0.1:47430). This ports the owner's uncommitted patch
  in the installed upstream plugin; it unblocks task #415.
- `archiveDir`: a trimmed output's full text goes to `.jev/pruner/archive`, outside `.claude/`, where the archive drifted
  the vendored-tree manifest (task #232).
- `decisionsDir`: every Bash call rewrites `.jev/pruner/decisions/last.json` (the heartbeat), and a call past the floor
  writes a record of its own under the UTC day; counts only.

Installed at 02:4xZ: `claude plugin marketplace add /home/user/agent-factory/vendor/jev-pruner`, `claude plugin install
fast-jev-output-floor@agent-factory-vendor`, `claude plugin configure ... --values-stdin` (base URL the relay, model
`openjev-latest`, `maxStateTokens` 8000, `minTokensFloor` and `minTokens` 1000, the two folders, and an `apiKey` that is
a placeholder: the relay drops the caller's Authorization header and adds the codiv key itself, so no pruner holds a real
key), then `claude plugin disable fast-jev-output@fast-jev-output`.

## Addendum 09:4xZ: the first live decisions, and the history window (local change 4, task #436)

- **The restart.** The container was recycled while the owner was away; the session's resume started a new Claude Code
  at 09:14:19Z, which loaded our copy (first heartbeat 09:23:22Z). `/reload-plugins` does not run over a remote
  connection (the owner, 09:22Z: "isn't available over a remote connection in this session").
- **Relative folders.** The hook resolves a relative `decisionsDir` or `archiveDir` against Claude Code's launch
  directory (`/home/user` in this cloud session), so the first records landed in `/home/user/.jev/`. Both are now
  absolute. That option change reloaded the hook at once: the next heartbeat landed in the repo's folder.
- **The first live decision past the floor (09:26:54Z):** a 220-line `git log`, 7,588 estimated tokens, 11 chunks, 12
  requests through the relay (0 errors) in 12.7 s, decision `incomplete_coverage`: all 11 chunks kept. The cause:
  upstream scores every chunk against every slice of the WHOLE session's history and keeps any chunk not scored against
  all of them, and the hook allows 12 requests per output, far fewer than this session's slices (P1 saw it once,
  2026-09-25). The relay spaces its sends 1.05 s apart, so the 12 requests cost about 13 s, for nothing.
- **Local change 4:** `historyTokens`, the newest whole messages that fit that many estimated tokens; set to 3,000, under
  half of `maxStateTokens` (8,000), so the window is one slice. On a test session of 400 messages: 1 request instead of
  12, and 13 of 15 chunks dropped instead of none. The task (the last three prompts) still comes from the whole session.
- **Not live yet.** Installed as version 0.1.1 at 09:41Z; it runs from the next Claude Code start, because an option
  change reloads the code already loaded (09:41:19Z: the record still lacked the new fields, 12 requests again, 13.8 s).
  The probe now warns while an installed update is newer than the running Claude Code.

## NOT done here

- The first live decision under the history window: it needs the next Claude Code start (the addendum above).
- The replay bridge (`scripts/jev_pipes/bridge.mjs`) does not replay the window yet (task #437).
- The drop rate per size band at the new floor: read it from the decision records after a day, then tune the floor.
- The saved-output path: whether a larger budget than the preview, or skipping such outputs, serves better.
