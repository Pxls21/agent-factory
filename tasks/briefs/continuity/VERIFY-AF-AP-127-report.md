# VERIFY-AF-AP-127 — report (task #155)

LANE: verify-af-ap-127 (sandbox, agent `adversarial-verifier`, shared tree, no worktree). PIN 1978e55. Brief:
`tasks/briefs/continuity/VERIFY-AF-AP-127-brief.md` (origin 649663a). Written incrementally; status: COMPLETE (2026-09-23 10:5xZ).

Legend: SOLID = reproduced in this session through the named real path; UNSURE = reviewed statically or inferred.
Scratch: `/tmp/vap127/` only (removed at the end).

## Item 1 — PREMISE re-measured (2026-09-23 10:14Z-10:22Z) — MATCHES, no CONTRACT-INVALID

Venue: sandbox, local HEAD 2f5b1c3 (origin 3846636; three local commits ahead, none on the boundary). SOLID. Re-checked at
10:3xZ after other lanes moved the heads (local a361204, origin de33838): `git diff --stat 1978e55 HEAD -- <boundary>` still empty.
```
$ git diff --stat 1978e55 HEAD -- <7 boundary files>; git diff --stat 1978e55 -- <same>   # HEAD and working tree vs PIN
(empty, rc=0) (empty, rc=0)
$ blob at 2d10a2c / 1978e55 / HEAD / working tree
b2887443b443 b2887443b443 SAME | HEAD=b2887443b443 WT=b2887443b443 scripts/transcript_export.py
04326ece5b7a 04326ece5b7a SAME | HEAD=04326ece5b7a WT=04326ece5b7a harness-ports/bin/hermes-session-export.py
a6691647faa5 a6691647faa5 SAME | HEAD=a6691647faa5 WT=a6691647faa5 .claude/hooks/edit-snapshot.py
cef778a1fd02 cef778a1fd02 SAME | HEAD=cef778a1fd02 WT=cef778a1fd02 tests/test_transcript_export.py
40da66cc04bd 40da66cc04bd SAME | HEAD=40da66cc04bd WT=40da66cc04bd harness-ports/tests/test_hermes_session_export.py
25eba0cc4912 25eba0cc4912 SAME | HEAD=25eba0cc4912 WT=25eba0cc4912 tests/test_edit_snapshot_ap_screen.py
29f572185384 767ab95d7585 CHANGED | HEAD=767ab95d7585 WT=767ab95d7585 tests/test_ap_screen.py
$ git log 2d10a2c..1978e55 -- <boundary>      -> ea18960 (AF-AP-132, line numbering) only; 1978e55..HEAD -> none
$ grep scrub(/[:cap] in the two exporters -> the same five lines as the brief (transcript_export.py:44,82; hermes-session-export.py:26,41,47)
$ git ls-files transcripts | wc -l -> 120; BEGIN..PRIVATE KEY files -> 0; <private-key-redacted> -> 0
$ git log -1 -- transcripts -> 1978e55 09-23 09:13 (true at 10:19Z; de33838 pushed new transcripts at 10:20Z — item 8 re-runs there)
$ call sites -> scripts/push_clean.sh:117-118, harness-ports/bin/pc-lane.sh:514 (the same three lines)
$ pytest tests/test_transcript_export.py tests/test_edit_snapshot_ap_screen.py tests/test_ap_screen.py -q -p no:cacheprovider --basetemp=/tmp/vap127/bt{1,2}
108 passed in 0.59s   (rc=0)
108 passed in 0.67s   (rc=0)
$ bash scripts/pc_suite.sh set-id -- <same three files>  -> 3 files set=7fa2348f21fe
$ TMPDIR=/tmp/vap127/tmp python3 harness-ports/tests/test_hermes_session_export.py -> test_hermes_session_export: 14 checks passed
$ python3 /tmp/vap127/screen_sweep.py <rev>   # the hook's REAL AP_SCREEN row, content via git show <rev>:<path>
@1978e55  : 2 hit(s) over 175 tracked files — .claude/hooks/edit-snapshot.py:185 (comment), :187 (message string)
@2d10a2c^ : 2 hit(s) over 172 files — harness-ports/bin/hermes-session-export.py:40, scripts/transcript_export.py:76  (red control)
@2d10a2c  : 2 hit(s) over 172 files — the hook's own two lines only
$ df -h /tmp -> 1.6G free
```
Test names in `tests/test_transcript_export.py`: :52, :69, :90, :106, :120 (as the brief). The premise block holds on every line.

## Item 2 — C1/C2, the order per write path

### 2a. Every value the two exporters write to disk (static read, then planted through the real `export()`; SOLID)

| # | writer file:line | value | scrubbed? | capped? | order | can it carry a secret? |
|---|---|---|---|---|---|---|
| S1 | `scripts/transcript_export.py:86` | day file header `# Conversation {day} (… {n} turns)` (`len(days[day])`) | no | no | — | `day` = `ts[:10]` (JSONL `timestamp`, written by Claude Code); `n` is an int |
| S2 | `scripts/transcript_export.py:82` | turn heading `## {role} @ {ts}` | **no** | no | — | `role` is fixed to user/assistant (:58); `ts` is the raw JSONL `timestamp` string: a planted FAKE value reached disk verbatim (2c) |
| S3 | `scripts/transcript_export.py:82` | turn body (`scrub(txt)[:cap]`) | yes | yes (`--cap`, default 4000) | **scrub whole, then cap** (C1 holds) | yes (user/assistant text; tool results and thinking blocks are never exported, :64) |
| S4 | `scripts/transcript_export.py:85` | file name `chat-{day}.md` | no | — | — | as S1 |
| P1 | `harness-ports/bin/hermes-session-export.py:55` | `# Hermes lane session {session}` | **no** | no | — | the `--session` argument (a Hermes session id) |
| P2 | `harness-ports/bin/hermes-session-export.py:56` | `- model:` | **no** | no | — | the `sessions.model` column |
| P3 | `harness-ports/bin/hermes-session-export.py:57` | `- started:` | n/a | no | — | formatted from a float; no |
| P4 | `harness-ports/bin/hermes-session-export.py:58` | `- cwd:` | **no** | no | — | the `sessions.cwd` column (a lane path) |
| P5 | `harness-ports/bin/hermes-session-export.py:59-60` | message/tool-call/token counts | n/a | no | — | integers; no |
| P6 | `harness-ports/bin/hermes-session-export.py:67` | `## tool result ({tool_name}) @ {ts} — {len} chars` | **no** | no | — | `tool_name` column (tool/model-supplied string); `ts` formatted; `len` an int |
| P7 | `harness-ports/bin/hermes-session-export.py:69` | tool-result body (only when `--tool-body-cap` > 0) | yes | yes (`tool_body_cap`) | **scrub whole, cap, indent** (`_body`, :41; C2 holds) | yes; off by default and off in the harvest (`harness-ports/bin/pc-lane.sh:514`, `hermes-session-export.py" --db`, passes no `--tool-body-cap`) |
| P8 | `harness-ports/bin/hermes-session-export.py:77,81` | `→ tools: {names}` (function names from `tool_calls`) | **no** | no | — | model-supplied names; the call ARGUMENTS are never written (good) |
| P9 | `harness-ports/bin/hermes-session-export.py:81` | `## {role} @ {ts}` | **no** | no | — | `messages.role` column (Hermes-written) |
| P10 | `harness-ports/bin/hermes-session-export.py:80-81` | message body (`_body(scrub, r["content"] or "", cap)`; every non-tool role, system included) | yes | yes (`--cap`, default 3000) | **scrub whole, cap, indent** (C2 holds) | yes |
| A1 | `harness-ports/bin/pc-lane.sh:516` (ADJACENT, not an exporter) | `profile:` + the whole `usage.json` appended to the committed PC transcript | **no** | no | — | today no: 102 of the 104 committed `transcripts/pc/*.md` carry a section; its keys are api_calls, cache_read/write_tokens, completed, cost_source, cost_status, estimated_cost_usd, failed, input/output/reasoning/total_tokens, model, provider, service_tier, session_id (measured @1978e55). Written by Hermes (`--usage-file`, `harness-ports/bin/pc-lane.sh:450`), so a future field is unscrubbed by construction. |

### 2b. The straddle attack — every class, EVERY cut point, the real `export()` of both exporters (SOLID)
Harness `/tmp/vap127/straddle.py`: text = `"note one two three " + SECRET + " and then the tail text of the turn"`, cap = len(lead) + k for every
k in 0..len(SECRET). Sandbox: a synthetic JSONL through `transcript_export.export()`. PC: a synthetic SQLite DB with the exact
`sessions`/`messages` columns `harness-ports/tests/test_hermes_session_export.py:21-28` builds, through `hermes-session-export.export()`,
the message body via `cap` and the tool body via `tool_body_cap`. Comparator = a scratch copy with ONLY the order reverted
(`/tmp/vap127/cmp/`, diff = the one line each). Leak = any 5-char window of the secret's sensitive part in the written file.
All values are random FAKE strings.
```
class                  len cuts | sandbox new/old-order leaks | PC msg new/old | PC tool body new/old
R0 private-key         451  452 |   0 /   0 |   0 /   0 |   0 /   0
R1 AGENT_TOKEN=         48   49 |   0 /   3 |   0 /   3 |   0 /   3
R1 PC_BRIDGE_TOKEN=     52   53 |   0 /   3 |   0 /   3 |   0 /   3
R1 X-Agent-Token:       51   52 |   0 /   3 |   0 /   3 |   0 /   3
R1 api_key:             45   46 |   0 /   3 |   0 /   3 |   0 /   3
R1 token=               42   43 |   0 /   3 |   0 /   3 |   0 /   3
R1 secret:              44   45 |   0 /   3 |   0 /   3 |   0 /   3
R1 password=            45   46 |   0 /   3 |   0 /   3 |   0 /   3
R1 passwd:              44   45 |   0 /   3 |   0 /   3 |   0 /   3
R1 Authorization:       51   52 |   0 /   3 |   0 /   3 |   0 /   3
R2 Bearer               43   44 |   0 /   3 |   0 /   3 |   0 /   3
R3 sk-                  39   40 |   0 /   7 |   0 /   7 |   0 /   7
R4 ghp_                 40   41 |   0 /  15 |   0 /  15 |   0 /  15
R5 AIza                 40   41 |   0 /  25 |   0 /  25 |   0 /  25
R6 xoxb-                41   42 |   0 /   5 |   0 /   5 |   0 /   5
R7 trycloudflare        58   59 |   0 /  40 |   0 /  40 |   0 /  40
R8 opaque40+            48   49 |   0 /  35 |   0 /  35 |   0 /  35
```
The old-order leak counts are exactly the cuts that leave a 5-char-or-longer stub under each pattern's minimum (8, 12, 20, 30, 10, 40;
the whole subdomain for R7). R0 does not leak even in the old order: the `\Z` alternative covers a block cut by the cap.

Written bytes around the cap (the real exporters; the secret cut in half; `‖` = the byte after the body; three paths identical per class):
```
R0 private-key       cap=244 len(body)= 76 | 'ed> and then the tail text of the turn' ‖ '\n'
R1 AGENT_TOKEN=      cap= 43 len(body)= 43 | 'one two three AGENT_TOKEN=<redacted> a' ‖ '\n'
R1 PC_BRIDGE_TOKEN=  cap= 45 len(body)= 45 | 'e two three PC_BRIDGE_TOKEN=<redacted>' ‖ '\n'
R1 X-Agent-Token:    cap= 44 len(body)= 44 | 'ne two three X-Agent-Token: <redacted>' ‖ '\n'
R1 api_key:          cap= 41 len(body)= 41 | 'e one two three api_key: <redacted> an' ‖ '\n'
R1 token=            cap= 40 len(body)= 40 | 'te one two three token=<redacted> and ' ‖ '\n'
R1 secret:           cap= 41 len(body)= 41 | 'e one two three secret: <redacted> and' ‖ '\n'
R1 password=         cap= 41 len(body)= 41 | 'e one two three password=<redacted> an' ‖ '\n'
R1 passwd:           cap= 41 len(body)= 41 | 'e one two three passwd: <redacted> and' ‖ '\n'
R1 Authorization:    cap= 44 len(body)= 44 | 'ne two three Authorization: <redacted>' ‖ '\n'
R2 Bearer            cap= 40 len(body)= 40 | 'te one two three Bearer <redacted> and' ‖ '\n'
R3 sk-               cap= 38 len(body)= 38 | 'note one two three sk-<redacted> and t' ‖ '\n'
R4 ghp_              cap= 39 len(body)= 39 | 'ote one two three gh<redacted> and the' ‖ '\n'
R5 AIza              cap= 39 len(body)= 39 | 'ote one two three AIza<redacted> and t' ‖ '\n'
R6 xoxb-             cap= 39 len(body)= 39 | 'ote one two three xox-<redacted> and t' ‖ '\n'
R7 trycloudflare     cap= 48 len(body)= 48 | 'wo three https://<bridge-link-redacted' ‖ '\n'
R8 opaque40+         cap= 43 len(body)= 43 | 'one two three <opaque-redacted> and th' ‖ '\n'
```
(PC message path: the byte after the body is `'\n\n## tool result'`; PC tool path: `'\n\n'`; the body bytes are the same.)
The discriminator, readable FAKE values, same cap, real vs order-reverted copy:
```
  sandbox real      cap=30: 'note one two three sk-<redacte'
  sandbox old-order cap=30: 'note one two three sk-FAKEfake'
  pc-msg  real      cap=37: 'note one two three AGENT_TOKEN=<redac'
  pc-msg  old-order cap=37: 'note one two three AGENT_TOKEN=FAKEfa'
  sandbox real      cap=39: 'note one two three gh<redacted> tail'
  sandbox old-order cap=39: 'note one two three ghp_FAKEfakeFAKEfake'
```
Two side effects of the new order, both visible above: a redaction that SHORTENS the text pulls later (scrubbed) bytes inside the cap
(R0: the 451-char block becomes a 22-char placeholder and the whole tail sentence now fits in a 244 cap; R1: `" a"` after the
placeholder), and the cap can cut a placeholder (`<redacte`). Neither writes a secret byte. Both bear on C6's wording (item 8, F9).

### 2c. The unscrubbed fields, FAKE planted values, through the real `export()` (SOLID)
```
  sandbox chat-2026-09-23.md: '## user @ 2026-09-23T05:00:00Z sk-FAKEheaderFAKEheader0000'
  pc '# Hermes lane session sk-FAKEheaderFAKEheader0000'
  pc '- model: m sk-FAKEheaderFAKEheader0000'
  pc '- cwd: /tree/sk-FAKEheaderFAKEheader0000'
  pc '## assistant @ 14:13:21 → tools: sk-FAKEheaderFAKEheader0000'
  pc '## tool result (sk-FAKEheaderFAKEheader0000) @ 14:13:22 — 11 chars (body not exported)'
  pc '## sk-FAKEheaderFAKEheader0000 @ 14:13:23'
```
Verdict for item 2: C1 and C2 hold as stated: every body path scrubs the whole text, then caps. 0 leaks over 1,199 cut points × 3 paths (sum of the `cuts` column).
The order-reverted copies leak on every class but R0. Seven heading and header values are not scrubbed at all (F4). No claim says
they are, and their sources are Hermes or Claude Code metadata. But `scripts/transcript_export.py:9-10` says "every class in
SECRET_PATTERNS is replaced before a byte reaches disk", and that is broader than the code.

## Item 3 — C3, the private-key class

Labels, primary source where the tool is present (no key generated): `strings /lib/x86_64-linux-gnu/libcrypto.so.3` (OpenSSL 3.0.13)
lists `ANY|DSA|EC|ED25519|ED448|ENCRYPTED|RSA|SM2|X25519|X448 PRIVATE KEY` and the `-----BEGIN %s-----` format; `strings /usr/bin/gpg`
(GnuPG 2.4.4) lists `BEGIN PGP PRIVATE KEY BLOCK` and `BEGIN PGP SECRET KEY BLOCK` (the PGP 2.x label gpg still reads). `ssh-keygen` is
ABSENT in this sandbox: the OpenSSH label (`OPENSSH PRIVATE KEY`) and its 70-column body come from the OpenSSH key format, not a probe
here (UNSURE on the source, SOLID on the scrub result for that label). Every block below is FAKE: a random base64 body (seeded) at the
family's real line width and a realistic size; no body is printed. Harness `/tmp/vap127/keys.py`: `scrub` = the REAL
`scripts/transcript_export.py:44`; `def scrub(text: str)`; the two "split across two turns" rows go through the REAL `export()` of each exporter. A body line
"left" = at least one 8-char fragment of it is in the output. Deterministic: two runs, md5 `646d4abf5e5dd70bf5a601e7bd4f1a32` both times.
```
family                                       | shape                                      | redacted | body lines left | body chars left
OpenSSH (ssh-keygen, ed25519)                | LF                                         |        1 |    0 / 6         |     0 / 400
                                             | CRLF                                       |        1 |    0 / 6         |     0 / 400
                                             | indented (YAML |)                          |        1 |    0 / 6         |     0 / 400
                                             | quoted reply (> )                          |        1 |    0 / 6         |     0 / 400
                                             | JSON string, literal \n                    |        1 |    0 / 6         |     0 / 400
                                             | BEGIN lost upstream (tail+END)             |        0 |    3 / 4         |   168 / 260
                                             | two blocks in one text                     |        2 |    0 / 12        |     0 / 800
                                             | END lost at source (BEGIN+head)            |        1 |    0 / 3         |     0 / 210
                                             | split across two turns [sandbox export()]  |        1 |    2 / 6         |   140 / 400
                                             | split across two turns [PC export()]       |        1 |    2 / 6         |   140 / 400
OpenSSH (ssh-keygen, rsa-3072)               | LF                                         |        1 |    0 / 38        |     0 / 2600
                                             | CRLF                                       |        1 |    0 / 38        |     0 / 2600
                                             | indented (YAML |)                          |        1 |    0 / 38        |     0 / 2600
                                             | quoted reply (> )                          |        1 |    0 / 38        |     0 / 2600
                                             | JSON string, literal \n                    |        1 |    0 / 38        |     0 / 2600
                                             | BEGIN lost upstream (tail+END)             |        0 |   21 / 23        |   951 / 1550
                                             | two blocks in one text                     |        2 |    0 / 76        |     0 / 5200
                                             | END lost at source (BEGIN+head)            |        1 |    0 / 19        |     0 / 1330
                                             | split across two turns [sandbox export()]  |        1 |   17 / 38        |   766 / 2600
                                             | split across two turns [PC export()]       |        1 |   17 / 38        |   766 / 2600
PKCS#1 RSA (openssl genrsa -traditional)     | LF                                         |        1 |    0 / 25        |     0 / 1588
                                             | CRLF                                       |        1 |    0 / 25        |     0 / 1588
                                             | indented (YAML |)                          |        1 |    0 / 25        |     0 / 1588
                                             | quoted reply (> )                          |        1 |    0 / 25        |     0 / 1588
                                             | JSON string, literal \n                    |        1 |    0 / 25        |     0 / 1588
                                             | BEGIN lost upstream (tail+END)             |        0 |   13 / 15        |   580 / 948
                                             | two blocks in one text                     |        2 |    0 / 50        |     0 / 3176
                                             | END lost at source (BEGIN+head)            |        1 |    0 / 12        |     0 / 768
                                             | split across two turns [sandbox export()]  |        1 |   11 / 25        |   452 / 1588
                                             | split across two turns [PC export()]       |        1 |   11 / 25        |   452 / 1588
PKCS#1 RSA legacy-encrypted                  | LF                                         |        1 |    0 / 26        |     0 / 1624
                                             | CRLF                                       |        1 |    0 / 26        |     0 / 1624
                                             | indented (YAML |)                          |        1 |    0 / 26        |     0 / 1624
                                             | quoted reply (> )                          |        1 |    0 / 26        |     0 / 1624
                                             | JSON string, literal \n                    |        1 |    0 / 26        |     0 / 1624
                                             | BEGIN lost upstream (tail+END)             |        0 |   15 / 16        |   823 / 984
                                             | two blocks in one text                     |        2 |    0 / 52        |     0 / 3248
                                             | END lost at source (BEGIN+head)            |        1 |    0 / 13        |     0 / 832
                                             | split across two turns [sandbox export()]  |        1 |   12 / 26        |   631 / 1624
                                             | split across two turns [PC export()]       |        1 |   12 / 26        |   631 / 1624
PKCS#1 DSA                                   | LF                                         |        1 |    0 / 19        |     0 / 1180
                                             | CRLF                                       |        1 |    0 / 19        |     0 / 1180
                                             | indented (YAML |)                          |        1 |    0 / 19        |     0 / 1180
                                             | quoted reply (> )                          |        1 |    0 / 19        |     0 / 1180
                                             | JSON string, literal \n                    |        1 |    0 / 19        |     0 / 1180
                                             | BEGIN lost upstream (tail+END)             |        0 |   10 / 12        |   350 / 732
                                             | two blocks in one text                     |        2 |    0 / 38        |     0 / 2360
                                             | END lost at source (BEGIN+head)            |        1 |    0 / 9         |     0 / 576
                                             | split across two turns [sandbox export()]  |        1 |    8 / 19        |   276 / 1180
                                             | split across two turns [PC export()]       |        1 |    8 / 19        |   276 / 1180
PKCS#8 (openssl genpkey)                     | LF                                         |        1 |    0 / 26        |     0 / 1624
                                             | CRLF                                       |        1 |    0 / 26        |     0 / 1624
                                             | indented (YAML |)                          |        1 |    0 / 26        |     0 / 1624
                                             | quoted reply (> )                          |        1 |    0 / 26        |     0 / 1624
                                             | JSON string, literal \n                    |        1 |    0 / 26        |     0 / 1624
                                             | BEGIN lost upstream (tail+END)             |        0 |   13 / 16        |   659 / 984
                                             | two blocks in one text                     |        2 |    0 / 52        |     0 / 3248
                                             | END lost at source (BEGIN+head)            |        1 |    0 / 13        |     0 / 832
                                             | split across two turns [sandbox export()]  |        1 |   10 / 26        |   551 / 1624
                                             | split across two turns [PC export()]       |        1 |   10 / 26        |   551 / 1624
PKCS#8 encrypted (openssl pkcs8 -topk8)      | LF                                         |        1 |    0 / 28        |     0 / 1750
                                             | CRLF                                       |        1 |    0 / 28        |     0 / 1750
                                             | indented (YAML |)                          |        1 |    0 / 28        |     0 / 1750
                                             | quoted reply (> )                          |        1 |    0 / 28        |     0 / 1750
                                             | JSON string, literal \n                    |        1 |    0 / 28        |     0 / 1750
                                             | BEGIN lost upstream (tail+END)             |        0 |   16 / 17        |   931 / 1046
                                             | two blocks in one text                     |        2 |    0 / 56        |     0 / 3500
                                             | END lost at source (BEGIN+head)            |        1 |    0 / 14        |     0 / 896
                                             | split across two turns [sandbox export()]  |        1 |   13 / 28        |   739 / 1750
                                             | split across two turns [PC export()]       |        1 |   13 / 28        |   739 / 1750
SEC1 EC (openssl ecparam -genkey)            | LF                                         |        1 |    0 / 3         |     0 / 164
                                             | CRLF                                       |        1 |    0 / 3         |     0 / 164
                                             | indented (YAML |)                          |        1 |    0 / 3         |     0 / 164
                                             | quoted reply (> )                          |        1 |    0 / 3         |     0 / 164
                                             | JSON string, literal \n                    |        1 |    0 / 3         |     0 / 164
                                             | BEGIN lost upstream (tail+END)             |        0 |    2 / 2         |    48 / 100
                                             | two blocks in one text                     |        2 |    0 / 6         |     0 / 328
                                             | END lost at source (BEGIN+head)            |        1 |    0 / 1         |     0 / 64
                                             | split across two turns [sandbox export()]  |        1 |    2 / 3         |    48 / 164
                                             | split across two turns [PC export()]       |        1 |    2 / 3         |    48 / 164
GnuPG --export-secret-keys --armor           | LF                                         |        0 |   13 / 15        |   639 / 900
                                             | CRLF                                       |        0 |   11 / 15        |   567 / 900
                                             | indented (YAML |)                          |        0 |   13 / 15        |   639 / 900
                                             | quoted reply (> )                          |        0 |   13 / 15        |   639 / 900
                                             | JSON string, literal \n                    |        0 |   13 / 15        |   639 / 900
                                             | BEGIN lost upstream (tail+END)             |        0 |    8 / 9         |   373 / 516
                                             | two blocks in one text                     |        0 |   21 / 30        |  1062 / 1800
                                             | END lost at source (BEGIN+head)            |        0 |    6 / 7         |   330 / 448
                                             | split across two turns [sandbox export()]  |        0 |   13 / 15        |   639 / 900
                                             | split across two turns [PC export()]       |        0 |   13 / 15        |   639 / 900
GnuPG legacy label (PGP 2.x, gpg reads it)   | LF                                         |        0 |   14 / 15        |   594 / 900
                                             | CRLF                                       |        0 |   13 / 15        |   592 / 900
                                             | indented (YAML |)                          |        0 |   14 / 15        |   594 / 900
                                             | quoted reply (> )                          |        0 |   14 / 15        |   594 / 900
                                             | JSON string, literal \n                    |        0 |   14 / 15        |   594 / 900
                                             | BEGIN lost upstream (tail+END)             |        0 |    8 / 9         |   367 / 516
                                             | two blocks in one text                     |        0 |   24 / 30        |  1026 / 1800
                                             | END lost at source (BEGIN+head)            |        0 |    7 / 7         |   245 / 448
                                             | split across two turns [sandbox export()]  |        0 |   14 / 15        |   594 / 900
                                             | split across two turns [PC export()]       |        0 |   14 / 15        |   594 / 900
```
End to end, one turn, a FAKE GnuPG block, through the real exporters (`/tmp/vap127/w3b`):
```
sandbox export(): <private-key-redacted> x0, <opaque-redacted> x10, body lines with an 8-char fragment on disk: 11/15; armor lines on disk: ['-----BEGIN PGP PRIVATE KEY BLOCK-----', '-----END PGP PRIVATE KEY BLOCK-----']
PC export(): <private-key-redacted> x0, <opaque-redacted> x10, body lines with an 8-char fragment on disk: 11/15; armor lines on disk: ['-----BEGIN PGP PRIVATE KEY BLOCK-----', '-----END PGP PRIVATE KEY BLOCK-----']
current rule matches the PGP block: False | candidate rule: True | candidate still matches the PEM header: True
scrub with the candidate first rule: body lines left 0/15; result = 'here is the owner key backup:\n<private-key-redacted>\nstore it offline'
```
(candidate, scratch only: `-----BEGIN [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----.*?(?:-----END [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----|\Z)`, `re.S`.)

Answers to item 3:
- Redacted whole: every PEM/OpenSSH family (OpenSSH, PKCS#1 RSA/DSA, PKCS#1 legacy-encrypted with `Proc-Type`/`DEK-Info`, PKCS#8,
  encrypted PKCS#8, SEC1 EC) in every shape that keeps its BEGIN line: LF, CRLF, indented (YAML block, `> ` quote), inside a JSON
  string with literal `\n`, two blocks in one text (2 placeholders, text between them kept), and END lost at the source (`\Z`).
- Never redacted: the GnuPG armored secret key, under both labels, in every shape. The rule needs `PRIVATE KEY-----` right after
  the label; GnuPG writes `PRIVATE KEY BLOCK-----`. The opaque rule removes only 40+ runs between `+` and `/`, so 11-14 of 15 body
  lines, 567-639 of 900 body characters, reach the written file through both real exporters. -> F1.
- Body left on disk for ALL families: a block whose BEGIN line was lost upstream (the rule is anchored on BEGIN; nothing mirrors the
  `\Z` alternative for a missing BEGIN), and a block split across two turns (turn 2 has no BEGIN). -> F2.
- Adjacent, not armored: `openssl pkey -text` prints the private exponent as colon-separated hex; a FAKE dump keeps 18 of 18
  `privateExponent` lines verbatim (no rule matches colon hex). -> F3.

## Item 4 — cost of the new order (the real `scrub`, whole text) — linear; no finding

Box: 4 cores, load 1.8 → 1.4 during the run (other agents live), so the ratios carry the verdict, not the absolute times. Harness
`/tmp/vap127/timing.py`: best of 3 per size, the REAL `scripts/transcript_export.py:44` `scrub`; ratio = t(2n)/t(n) (2 = linear, 4 = quadratic).
```
case                                                                 1.25MB   2.50MB   5.00MB  10.00MB   ratios
A  mixed (committed chat text + FAKE secrets + key blocks)           0.254s   0.501s   1.024s   2.041s   1.97 2.04 1.99
B1 BEGIN <non-key label> lines, no END                               0.182s   0.352s   0.743s   1.506s   1.93 2.11 2.03
B2 BEGIN RSA PRIVATE KEY header at start, no END, base64 after       0.021s   0.041s   0.085s   0.171s   2.00 2.04 2.02
B3 BEGIN + 'PRIVATE KEY ' repeated, never '-----'                    0.189s   0.379s   0.771s   1.567s   2.00 2.04 2.03
C1 one alnum run (a single 40+ token)                                0.171s   0.347s   0.683s   1.390s   2.03 1.97 2.04
C2 base64 with + and / (runs < 40), no newlines                      0.184s   0.356s   0.718s   1.467s   1.93 2.02 2.04
D1 BEGIN + one uppercase run                                         0.186s   0.371s   0.740s   1.483s   1.99 2.00 2.00
D2 BEGIN + 1000 uppercase + newline, repeated                        0.187s   0.367s   0.733s   1.506s   1.96 2.00 2.06
D3 BEGIN + 'A ' run (uppercase and spaces)                           0.202s   0.400s   0.806s   1.621s   1.98 2.01 2.01
E  adversarial opaque: 'a-'*20 + dashes (no word boundary at >=40)   0.655s   1.251s   2.535s   5.003s   1.91 2.03 1.97
F1 adversarial credential: 'token' + 4000 spaces + 'x'               0.186s   0.383s   0.768s   1.591s   2.06 2.01 2.07
F2 'password=' + 7-char value, repeated                              0.212s   0.405s   0.816s   1.645s   1.91 2.01 2.02
G  BEGIN key header then '-----END '+1000 uppercase, repeated        0.025s   0.049s   0.099s   0.198s   1.98 2.03 2.00
```
Every case is linear (ratios 1.91-2.11). The worst constant is E, derived from the opaque rule's `\b…{40,}\b` backtracking (at most
~40 failing start positions per dash tail): 0.5 s/MB, about 3.4x the typical 0.15 s/MB, still linear. The private-key rule's
`[A-Z0-9 ]*` and lazy `.*?(…|\Z)` never re-scan: the first BEGIN without an END consumes the rest of the text in one match (B2, G).
Production shape: the push-time exporter on the coordinator's REAL 468 MB session transcript (`--out /tmp/vap127/real-*`, never
the default path): new order 3.4 s wall, order-reverted copy 2.9 s, pre-fix exporter (`git show 2d10a2c^:scripts/transcript_export.py`)
2.9 s; 16 day files each; ~20 MB max RSS. The new order costs about +0.5 s per push. The lane harvest scrubs capped DB rows of the same kind.

## Item 7 — C5, the exposure count — REPRODUCED EXACTLY, with its method named

The method is in `docs/INCIDENT-LOG.md:32` ("a named secret under 8 characters, `sk-` under 12, `Bearer` under 8 at a turn's end …
across 48,701 committed turn bodies in 118 transcript files, and 0 in the new J1-1 transcript (423 bodies)"). The measurement point is
the J1-1 landing: `01ca7d5^` has 118 files (102 pc, 16 sandbox); `01ca7d5` adds `transcripts/pc/pc-j1-1.md--330803c.md`.
```
$ python3 - <<count sections>>      # the count that reproduces C5 (verbatim output)
@01ca7d5^: files=118  lines matching ^#{1,2} = 49016  sections from splitting each file on ^'## ' = 48701
@1978e55: files=120  lines matching ^#{1,2} = 50905  sections from splitting each file on ^'## ' = 50582
J1-1 transcript: sections split on ^'## ' = 423 | '## ' lines = 422
# -> 48,701 and 423 are C5's numbers exactly: sections, one per file header plus one per '## ' line
$ python3 /tmp/vap127/item7stubs.py 01ca7d5^    # the incident's three stub classes at every section end, plus every
$ python3 /tmp/vap127/item7stubs.py 1978e55     # SECRET_PATTERNS class at the end of every body the cap actually cut
@01ca7d5^: files=118
   capped bodies (pc, len == 3000): 2
   capped bodies (sandbox, len == 4000): 78
   key headers anywhere (any family, PGP included): 0
   sections: 48701
   stub hits: 0
@1978e55: files=120
   capped bodies (pc, len == 3000): 2
   capped bodies (sandbox, len == 4000): 121
   key headers anywhere (any family, PGP included): 0
   sections: 50582
   stub hits: {'capped-end opaque run 20-39 at the cut': 1}
     transcripts/sandbox/chat-2026-09-04.md:2509  capped-end opaque run 20-39 at the cut
# the one hit, classified without printing it: "stub length: 25 | char classes: {'lower': 0, 'upper': 0, 'digit': 0, '_': 0, '-': 25}"
# = a run of 25 '-' characters (a separator line cut at the cap), not a secret: a false positive of the widened class
```
What the 48,701 counts (INFO, F10): sections, not bodies. At `01ca7d5^` it is 118 file-header sections + 44,109 PC `## ` lines
(18,014 message turns + 25,512 `## tool result (` headings whose body is NOT exported, so they hold no text) + 4,474 sandbox `## `
lines (4,404 turn headings + 70 `## ` lines inside bodies). Turn bodies that can carry text: 4,404 + 18,014 = 22,418. The zero holds on
either count: 0 key blocks and 0 cut-short stubs.

## Item 8 — C6: the CURRENT scrub over every committed transcript — 0 of 120 files change

```
$ python3 /tmp/vap127/item8.py <rev>     # content via git show <rev>:<path>; prints positions and classes only
@1978e55: 120 committed files under transcripts/; scrub(text) != text in 0      (the PIN)
@de33838: 120 committed files under transcripts/; scrub(text) != text in 0      (origin at 10:3xZ: a transcript push after the PIN)
@a361204: 120 committed files under transcripts/; scrub(text) != text in 0      (local HEAD)
@5dfd550: 119 committed files under transcripts/; scrub(text) != text in 0      (the last OLD-order transcript commit, 02:51)
negative control (a FAKE AGENT_TOKEN= line through the same scrub): planted text changes under scrub: True
```
No unredacted secret-shaped string is committed, the scrubber is a fixed point on its own output over the whole corpus, and no stale
export differs. There is nothing to classify. One caution: a cut-short stub is below its pattern's minimum by definition, so this check
cannot see one. Item 7 covers stubs.

C6 through the real history. The fix's first re-export is the pair `5dfd550` (02:51, old order) → `280d3df` (02:59, new order):
```
$ python3 /tmp/vap127/c6diff.py 5dfd550 280d3df <the 11 changed transcripts/sandbox files>   # spans classified by difflib; counts only
5dfd550 -> 280d3df: paired turns 3242, changed 27, turns only in new 16, only in old 0
     27  window extension at the cap (more scrubbed text)
# categories not printed are 0: redaction (new placeholder), LESS-REDACTION, window shrink, tail replaced, placeholder changed, OTHER
$ python3 - <<mechanism check over the same 27 turns>>
{'changed': 27, 'old is a prefix of new': 27, 'new body == 4000 chars (the cap)': 27, 'old body < 4000 chars': 27, 'new body carries a placeholder before the old end': 27}
chars admitted per turn: min 23 max 143 total 1700
```
So the re-export added 0 redactions, removed 0, and admitted 1,700 scrubbed characters at the caps of 27 turns: the placeholders are
shorter than the text they replace, so the cap now falls later. "never less" holds. The first half does not: the ledger's
"only more redaction" (`todo/BUILD-TASKLIST.md:186`) and the brief's "changes no byte except by redacting" are false as stated,
and the commit's "more redaction" names changes that did not happen: every change was admitted text, none a redaction (F9). No admitted byte is a secret: all of it is `scrub(whole text)` output, and item 8's scan finds 0.

## Item 5 — C4, the screen row, on new shapes (the REAL `AP_SCREEN` entry, loaded exactly as `tests/test_edit_snapshot_ap_screen.py:459`: `_AP_BY_ID["AF-AP-127"]`)

The row (`.claude/hooks/edit-snapshot.py:186`): `\b(?:scrub|redact|sanitize|mask_secrets?|_redact_str)\w*\(\s*[\w.]+\[\s*:[^\]\n]*\]\s*\)`,
i.e. ONE spelling: a verb, then a dotted NAME, then a slice that STARTS with `:`, then the closing paren. Harness `/tmp/vap127/item5.py`
(the landing's four shapes are excluded; "should" = would a secret straddling the bound escape its pattern).
```
shape                                              fires  should  verdict
brief: explicit zero lower bound                   False  True    MISS
brief: extra argument                              False  True    MISS
brief: a call result sliced                        False  True    MISS
brief: two-step, one hunk                          False  True    MISS
brief: a truncating helper                         False  True    MISS
brief: textwrap.shorten                            False  True    MISS
brief: full-copy slice (no cap)                    True   False   FALSE-POSITIVE
brief: shell, cap before scrub (.sh)               False  True    MISS
extra: dict subscript then slice                   False  True    MISS
extra: parenthesised expr sliced                   False  True    MISS
extra: underscore verb                             False  True    MISS
extra: module-private verb                         False  True    MISS
extra: tail cap (a suffix slice that IS a cap)     False  True    MISS
extra: windowed scrub (every window edge cuts)     False  True    MISS
extra: keyword argument                            False  True    MISS
extra: concatenation                               False  True    MISS
extra: str() then slice                            False  True    MISS
extra: space before [                              False  True    MISS
extra: direct re.sub on a capped slice             False  True    MISS
extra: other verbs                                 False  True    MISS
extra: multi-line call                             True   True    ok
extra: trailing-newline drop                       True   False   FALSE-POSITIVE
extra: in a comment only                           True   False   FALSE-POSITIVE
control: the fixed shape                           False  False   ok
```
End to end through the real hook `main()` (Edit payload on stdin; `/tmp/vap127/hookprobe/`):
```
== hit.py   (scrub(txt[:cap]))            -> "AF-AP-127a redaction/scrub applied to an already-capped slice …"  rc=0
== miss.py  (scrub(r["content"][:cap]))   -> registry screen printed, no AF-AP-127 line                         rc=0
== hit.sh   (the same text in a .sh file) -> no output at all: `.claude/hooks/edit-snapshot.py:407` returns unless the path ends in .py
```
Reading: the row pins the landing's spelling and little else. Counted from the harness output: 24 shapes, 20 that should fire,
19 of those missed, 3 false positives. Missed: explicit `0:` lower bound,
an extra or keyword argument, `r["k"][:n]`, `(expr)[:n]`, `str(x)[:n]`, `x [:n]`, concatenation, the verbs `_scrub`/`self._redact`/
`mask`/`censor`/`anonymize`, a direct `PAT.sub(…, x[:n])`, a windowed scrub `scrub(x[i:i+n])`, a TAIL cap `scrub(x[-n:])`, a two-step
cap, a truncating helper, and any shell pipeline (the hook never screens `.sh`). Only the multi-line call fires. It fires falsely on
`redact(x[:])` (a full copy), `scrub(buf[:-1])`, and a comment: the hook's own lines 185/187 are its only two hits over the tree (item 1).
The repo defines ten redaction-named functions in production code. Four of the nine that redact something (a string, a mapping, or a file's text) fall outside the row's verb list
(the tenth, `_scrub`, only returns the scrubber): `_redact` (`proofs/S0-04/check_compression.py:105`),
`_redact_env` (`proofs/S0-01/tools/acp_probe.py:171`), `_scrub_messages` (`harness-ports/bin/qwen_matrix.py:126`) and
`masked_log_text` (`proofs/S0-01/tools/pc/pc_launch.py:79`); list from `/tmp/vap127/verbs.py`, an AST walk of every def @1978e55.
C4's "never on … a suffix slice" is literally true, but a tail cap IS a suffix slice, and it cuts a straddling secret at its start:
the key name is lost and the value's tail is kept. So the no-fire is a design gap in the row (F6). Measured with the real `scrub`:
```
text = "the bridge env: AGENT_TOKEN=FAKEfakeFAKEfake00000000 and more"
tail cap n=40:  scrub(text[-n:]) = '_TOKEN=<redacted> and more'   |  scrub(text)[-n:] = 'dge env: AGENT_TOKEN=<redacted> and more'
tail cap n=30:  scrub(text[-n:]) = 'EfakeFAKEfake00000000 and more'   |  scrub(text)[-n:] = 'GENT_TOKEN=<redacted> and more'
```
The id also prints fused to its message (`AF-AP-127a redaction…`): `{ap_id:6s}` at `.claude/hooks/edit-snapshot.py:461-463` is narrower
than every 9-char `AF-AP-*` id (INFO, hook-wide).

## Item 6 — C4's sweep by an INDEPENDENT instrument (Python `ast`, not the hook's regex)

`/tmp/vap127/item6_ast.py` @1978e55: every first-party `.py` (and python-shebang extensionless file) under scripts, harness-ports,
src, proofs, .claude/hooks; tests separately. Flags a call to a redaction verb (`scrub|redact|sanitiz|mask|censor|anonymi|obfuscat`,
Name or Attribute) or any `.sub(` whose argument is (a) a bounded slice directly, (b) contains one, (c) a name assigned from one in the
same scope (two-step), (d) a call to a truncating-looking helper.
```
[production] python files walked @1978e55: 83; hits: 3
   harness-ports/bin/hermes-session-export.py:41  .sub sub(): DIRECT upper-bounded slice  | return _HEADING_SHAPED.sub(r" \1", scrub(text)[:cap])
   src/agent_factory/decisions/ledger.py:274  verb redact(): HELPER normalize()  | restate = redact(normalize(qid, row["state"], None))
   src/agent_factory/decisions/ledger.py:405  verb redact(): HELPER normalize()  | s = redact(normalize(question_id, raw_state, root))
[tests] python files walked @1978e55: 76; hits: 3
   tests/test_decisions_canonical.py:338  verb redact(): HELPER normalize()  | right_input = canonical(redact(normalize("b1.finding_sev", raw)))
   tests/test_decisions_canonical.py:172  verb redact(): HELPER normalize()  | clean_text = canonical(redact(normalize(qid, clean_state)))
   tests/test_decisions_canonical.py:183  verb redact(): HELPER normalize()  | pipeline_input = canonical(redact(normalize(qid, secret_state)))
```
Classification: `harness-ports/bin/hermes-session-export.py:41` is the heading-indent `.sub` on already scrubbed-then-capped text,
the correct order (a false positive of the instrument). `src/agent_factory/decisions/ledger.py:274,405` (`restate = redact(normalize(qid, row["state"], None))`) IS the class: `_normalize_field`
slices `s = s[: f.limit]` (`src/agent_factory/decisions/volatile.py:142-143`, EXCERPT_LIMIT 400) and `redact` runs on the result.
Probed live through the real functions: a FAKE `sk-` key straddling the 400-char `action_excerpt` comes out as `…aaaaaa sk-FA` (len 400);
redacting the whole text first gives `…aa <redacted:sk>`. This is the J1-1 instance of the class.
The registry row `docs/INCIDENT-LOG.md:475` (`AF-AP-127`) already marks it `OPEN for J1-1 until J1-1-R1`; J1-1-R1 has not landed (the log has only commits that mention it). It is outside this fix's boundary.
But the screen cannot see it (the truncation is inside a helper), so C4's "finds no other instance in … src/" is a statement about the
regex's output, not about the tree (F7).
Shell (`*.sh`, `*.bash` and sh-shebang files under scripts, harness-ports, src, proofs, .claude/hooks, .github; 84 files): 23 cap sites
(`head -c`, `cut -c`, `tail -c`, `${v:a:b}`). None feeds a scrub on its line or pipeline. The one with a scrub word within 3 lines,
`proofs/S0-02/tools/pc/run_s0_02_legs.sh:135`, is a byte-exact timeline split at a line boundary; its neighbour word is a comment
about a masked log (read at the PIN via `git show` only; that tree is another lane's).
ADJACENT (outside the fix), writes of capped text into a COMMITTED file with no scrub: `/tmp/vap127/item6_adj.py` found 28 bounded
slices of output-like values in production python; the 10 whose function also writes something go to exceptions, stderr or
console lines (`harness-ports/bin/omniroute_local_builder.py:132,137,291`, `scripts/gn_mcp.py:95`, `scripts/ooo_mcp.py:103`), or are
line-terminator strips (`proofs/S0-01/tools/frame_tee.py:347,349,438,440`) — none reaches a committed file. The unscrubbed writes
into committed files are UNCAPPED: the exporters' header and heading fields (item 2c, F4) and the `usage.json` append at `harness-ports/bin/pc-lane.sh:516`
(F5).

## Item 9 — test strength: the mutation audit (scratch copies under `/tmp/vap127/mut/` only)

Tree per mutant: a copy of `scripts/transcript_export.py`, `harness-ports/bin/hermes-session-export.py`, `tests/test_transcript_export.py`,
`harness-ports/tests/test_hermes_session_export.py`, `tests/conftest.py`, `pyproject.toml` (repo layout kept, so each test finds its
tool and the PC exporter imports the mutant's scrubber by path). The other two suite files never load an exporter (`grep -c` = 0 in
`tests/test_edit_snapshot_ap_screen.py` and `tests/test_ap_screen.py`), so they cannot kill an exporter mutant. Builder
`/tmp/vap127/mutate.py` (each replacement must match exactly once), runner `/tmp/vap127/runmut.sh` (py_compile, collect, pytest, the
14 checks). Unmutated copy: `5 tests collected`, `5 passed in 0.29s`, `test_hermes_session_export: 14 checks passed`.

| mutant | compiles / collects | `tests/test_transcript_export.py` | PC checks | verdict |
|---|---|---|---|---|
| M1 sandbox order reverted (`scrub(txt[:cap])`) | ok / 5 | `1 failed, 4 passed` — `test_secret_straddling_the_cap_never_reaches_disk` | 14 passed | KILLED |
| M2 PC `_body` order reverted (`scrub(text[:cap])`) | ok / 5 | `5 passed` | rc=1 `AssertionError: status ok AGENT_TOKEN=cVMjX` at check line 86 | KILLED |
| M3 private-key rule dropped | ok / 5 | `1 failed, 4 passed` — `test_private_key_block_is_scrubbed_whole_or_to_the_end` | 14 passed | KILLED |
| M4 private-key rule moved after the opaque rule | ok / 5 | `5 passed` | 14 passed | **SURVIVED** (F8a) |
| M5 `\Z` alternative dropped | ok / 5 | `1 failed, 4 passed` — `test_private_key_block_is_scrubbed_whole_or_to_the_end` | 14 passed | KILLED |
| M6 `re.S` dropped | ok / 5 | `1 failed, 4 passed` — `test_private_key_block_is_scrubbed_whole_or_to_the_end` | 14 passed | KILLED |
| M7 `_body`: cap after indent (`sub(…, scrub(text))[:cap]`) | ok / 5 | `5 passed` | 14 passed | **SURVIVED** (F8b; near-equivalent) |
| X1 (extra) PC message path inlines the old order in `export()` | ok / 5 | `5 passed` | 14 passed | **SURVIVED** (F8c) |
| X2 (extra) key label needs a type (`[A-Z0-9 ]+`) | ok / 5 | `5 passed` | 14 passed | **SURVIVED** (F8d) |
| X3 (extra, control) key rule greedy `.*` | ok / 5 | `1 failed, 4 passed` — `test_private_key_block_is_scrubbed_whole_or_to_the_end` | 14 passed | KILLED |

AF-AP-138, each killing test on the REAL unmutated tree before the kill is counted:
```
$ pytest "tests/test_transcript_export.py::test_secret_straddling_the_cap_never_reaches_disk" "tests/test_transcript_export.py::test_private_key_block_is_scrubbed_whole_or_to_the_end" -q -p no:cacheprovider --basetemp=/tmp/vap127/btk
2 passed in 0.21s   (rc=0)
$ TMPDIR=/tmp/vap127/tmp python3 harness-ports/tests/test_hermes_session_export.py
test_hermes_session_export: 14 checks passed   (rc=0)
```
The survivors are real behaviour changes, not equivalent mutants (each probe through the mutant copy's real functions):
```
M4 probe  'secret: -----BEGIN RSA PRIVATE KEY-----…' : real -> body lines left 0/20 | M4 -> body lines left 16/20
X2 probe  plain PKCS#8 '-----BEGIN PRIVATE KEY-----'  : real -> body lines left 0/20 | X2 -> body lines left 16/20
X1 probe  PC export() message body at cap 27: real -> 'status ok AGENT_TOKEN=<reda'
X1 probe  PC export() message body at cap 27: X1   -> 'status ok AGENT_TOKEN=FAKEf'
```
M4: a credential keyword on the BEGIN line (`secret: -----BEGIN …`) lets rule 1 eat `-----BEGIN` as a value when the key rule runs
late; the comment "First, so no later rule leaves pieces of it behind" (`scripts/transcript_export.py:25-26`) states the property,
but no test pins it. X1: the only PC straddle check calls `_body` directly (`harness-ports/tests/test_hermes_session_export.py:84-86`),
so `export()`'s message path could stop using `_body` and every check stays green. X2: the tests use only the RSA and OPENSSH labels,
so the plain PKCS#8 label is unpinned. M7 is near-equivalent: the consumer's `HEADING` (`harness-ports/bin/qwen_matrix.py:30`)
needs `## user|assistant|tool result (… @ …\n\n`, which is longer than the indenter's prefix (`harness-ports/bin/hermes-session-export.py:33`, `_HEADING_SHAPED`).
So either order keeps the grammar safe; M7 changes only the body length at the cap (the real order lets a body exceed the cap by one
byte per indented heading). C2 states the cap-then-indent order, and nothing pins it.

## Adjacent probes (outside C1-C6; FAKE values; the real `scripts/transcript_export.py:44` `scrub`)
```
lowercase bearer (RFC 7235: scheme is case-insensitive)    -> 'Authorization: bearer 0123456789abcdef0123456789abcdef'
JSON-quoted key                                            -> '{"password": "FAKEhunter2FAKE", "api_key": "FAKE0123abcd4567"}'
AWS-shaped pair (FAKE)                                     -> 'AWS_ACCESS_KEY_ID=AKIAFAKEFAKEFAKE0000 aws_secret_access_key: FAKE/fake+FAKEfakeFAKE/fake+FAKEfake0000'
prose naming a BEGIN line (no END)                         -> 'The rule matches <private-key-redacted>'
openssl pkey -text shape (FAKE hex): privateExponent lines left verbatim: 18 / 18 | any placeholder: False
$ git grep -c "<private-key-redacted>" de33838 -- transcripts   -> (no output: 0 files)
```
The first three pass unredacted (F12). The fourth drops the rest of its sentence (F13). The fifth is F3.

## Finding inventory (no severity filter)

Predicate columns: C = contract-mapped (C1-C6, the brief's frozen claims) · P = reproduced through the real exporter or hook entry ·
M = materially effective (a secret byte reaches a written file, or a claim is false as stated) · D = concrete discriminator ·
B = in-boundary (the two exporters, the scrubber, the screen row). A finding blocks only with all five.

| # | class | comp. | finding (file:line) | evidence | C | P | M | D | B | reproduction | suggested fix |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 | **BLOCKER** | (c) | The private-key rule never matches GnuPG's armored secret key (`-----BEGIN PGP PRIVATE KEY BLOCK-----`, and gpg's PGP 2.x input label `PGP SECRET KEY BLOCK`): the rule needs `PRIVATE KEY-----` right after the label (`scripts/transcript_export.py:27`). 11-14 of 15 body lines (567-639 of 900 body chars) reach the written file through BOTH real exporters, in every shape. | SOLID | C3 (and the brief's item 3 family list) | yes | yes | yes | yes | `python3 /tmp/vap127/keys.py` (GnuPG rows); `/tmp/vap127/w3b` probe: current rule False, candidate True, 0/15 lines left | Accept `(?:PRIVATE|SECRET) KEY(?: BLOCK)?` in BEGIN and END; add a per-family test with PGP included |
| F2 | FOLLOW-UP | (c) | A block whose BEGIN was lost upstream, or one split across two turns, leaves body lines for EVERY family (e.g. PKCS#1 RSA: 13/15 tail lines; split: 11/25 lines through both exporters). Nothing mirrors the `\Z` alternative for a missing BEGIN. | SOLID | none (C3 is anchored on BEGIN; it claims nothing for a BEGIN-less fragment) | yes | secret bytes, outside the claim | yes | yes | `/tmp/vap127/keys.py` rows "BEGIN lost upstream" and "split across two turns" | A mirror rule: from the start of a text to an END line when no BEGIN precedes it (watch for over-redaction before a stray END) |
| F3 | FOLLOW-UP (adjacent) | scrubber | `openssl pkey -text` prints the private exponent as colon hex; a FAKE dump keeps 18/18 `privateExponent` lines. | SOLID | none (not armored) | yes | outside any claim | yes | scrubber | item 3 probe | A `Private-Key:`/`priv:` hex-block rule, or state the gap in the docstring |
| F4 | FOLLOW-UP | (a)(b) | Seven heading or header values are written unscrubbed: `scripts/transcript_export.py:82` (`{ts}` in `days.setdefault`); `harness-ports/bin/hermes-session-export.py:55` (`# Hermes lane session {session}`), `:56` (model), `:58` (cwd), `:67` (tool_name), `:77,81` (tool-call names), `:81` (role). The docstring at `scripts/transcript_export.py:9-10` says every class is replaced "before a byte reaches disk". | SOLID (FAKE planted values reached disk, item 2c) | none (C1/C2 are about bodies) | yes | no secret today (harness metadata); a model-chosen tool name is the one model-reachable field | yes | yes | item 2c | Scrub each assembled line (or the file text) before the write, or narrow the docstring |
| F5 | FOLLOW-UP (adjacent) | PC harvest | `harness-ports/bin/pc-lane.sh:516` appends `profile:` and the whole `usage.json` to the committed PC transcript with no scrub. | SOLID (static; 102 committed sections: 16 keys, no credential field) | none | static + corpus | none today | — | no (pc-lane.sh) | item 2a row A1 | Pass the appended block through the same `scrub` |
| F6 | FOLLOW-UP | (d) | The row fires on one spelling, `verb(name[:bound])` (`.claude/hooks/edit-snapshot.py:186`): 19 of 20 cap-before-scrub shapes are missed (`r["k"][:n]`, `(expr)[:n]`, `x[0:n]`, a tail cap `x[-n:]`, `_scrub`/`self._redact`, 4 of the repo's 9 redactors, extra or keyword args, `.sh`); 3 false positives. The no-fire on a tail cap is a design gap (item 5 probe). | SOLID | C4 as the LANDING states it (the four named shapes; "finds no other instance") holds. The brief's paraphrase ("fires on a scrub/redact of an already-capped slice") is broader and false | yes | advisory screen (`.claude/hooks/edit-snapshot.py:9-11`: it never blocks); no byte on disk | yes | yes | `python3 /tmp/vap127/item5.py`; `/tmp/vap127/hookprobe` | Widen the subscript target and the lower bound, add `_`-prefixed verbs and the repo's redactor names, run the row on `.sh` via `scripts/ap_screen.py`; or narrow the claim |
| F7 | INFO (adjacent, known) | J1-1 | `src/agent_factory/decisions/volatile.py:142-143` (`if f.limit is not None:` then `s = s[: f.limit]`) truncates before `redact` (`src/agent_factory/decisions/ledger.py:274,405`): a FAKE `sk-` key straddling the 400 limit comes out `…sk-FA` through the real functions at the PIN. The registry marks it OPEN for J1-1-R1 (`docs/INCIDENT-LOG.md:475`); the screen cannot see it (helper). | SOLID | none (the ledger scopes it out) | yes | not this fix | yes | no | item 6 probe | J1-1-R1 |
| F8a | FOLLOW-UP | (c) | Mutant M4 (key rule after the opaque rule) survives both suites; with a keyword on the BEGIN line (`secret: -----BEGIN …`) 16/20 body lines leak. The "First, so no later rule…" property (`scripts/transcript_export.py:25-26`) is unpinned. | SOLID | C3 (true in code, untested) | yes | no (current code correct) | yes | yes | item 9 | Add a keyword-prefixed BEGIN case to the key test |
| F8b | FOLLOW-UP | (b) | Mutant M7 (cap after indent) survives; near-equivalent: the consumer's `HEADING` (`harness-ports/bin/qwen_matrix.py:30`) keeps the grammar safe either way; only the body length at the cap changes. | SOLID | C2's stated order (untested) | yes | no | yes | yes | item 9 | Pin the order, or drop it from the claim |
| F8c | FOLLOW-UP | (b) | Mutant X1 (the old order inlined in `export()`'s message path) survives: the only straddle check calls `_body` directly (`harness-ports/tests/test_hermes_session_export.py:84-86`); probe writes `…AGENT_TOKEN=FAKEf`. | SOLID | C2 (true in code, untested through `export()`) | yes | no (current code correct) | yes | yes | item 9 | A straddle case through `export()` for a message body |
| F8d | FOLLOW-UP | (c) | Mutant X2 (`[A-Z0-9 ]+`) survives: the tests pin only the RSA and OPENSSH labels; a plain PKCS#8 block then leaks 16/20 lines. | SOLID | C3 (true in code, untested) | yes | no (current code correct) | yes | yes | item 9 | Parametrize the key test over the families (PKCS#8, ENCRYPTED, EC, OPENSSH, RSA, PGP after F1) |
| F9 | FOLLOW-UP (claim correction) | (a) | C6: the fix's real re-export (`5dfd550`→`280d3df`) changed 27 committed turns, ALL by admitting 23-143 more scrubbed characters at the cap (1,700 total), and 0 by redaction. "only more redaction" (`todo/BUILD-TASKLIST.md:186`) and "changes no byte except by redacting" (the brief) are false as stated. "never less" holds: 0 less-redaction spans, 0 of 120 files change under the current scrub. | SOLID | C6 | yes (the real committed history) | the claim is false as stated; no secret byte | yes | **no**: the wrong text is the ledger note and commit message, not the component code, which is correct | `python3 /tmp/vap127/c6diff.py 5dfd550 280d3df …` | Reword: "never less redaction; placeholders shorter than their match let the cap admit more scrubbed text" |
| F10 | INFO | C5 | "48,701 committed turn bodies" counts SECTIONS: 118 file headers + 25,512 PC tool-result headings with no body + 70 in-body `## ` splits + the turns; text-bearing bodies = 4,404 + 18,014 = 22,418. The zero holds on either count. | SOLID | C5 (the number reproduces exactly) | yes | no | — | — | item 7 | Say "sections" or count bodies |
| F11 | INFO | hook | The tell prints `AF-AP-127a redaction…`: `{ap_id:6s}` (`.claude/hooks/edit-snapshot.py:463`) is narrower than every 9-char `AF-AP-*` id. | SOLID | none | yes | no | — | hook-wide | item 5 | `{ap_id:10s}` |
| F12 | FOLLOW-UP (adjacent) | scrubber | Pre-existing coverage gaps outside C1-C6: `Authorization: bearer <token>` (lowercase scheme), JSON-quoted keys (`"password": "…"`, `"api_key": "…"`), AWS-shaped key pairs pass unredacted. | SOLID (FAKE values, the real scrub) | none | yes | outside any claim | yes | scrubber | "Adjacent probes" above | `(?i)bearer`; allow a closing quote before the separator; an AKIA/aws_secret rule |
| F13 | INFO | scrubber | Prose that names a BEGIN line with no END loses the rest of its turn (the `\Z` alternative; over-redaction by design). 0 placeholders in committed transcripts @de33838. | SOLID | C3 (as designed) | yes | no | — | — | same probe | Accept, or require a base64 line after BEGIN |
| F14 | INFO (discrepancy) | evidence | The commit message and the registry row say the row found "1 hit on HEAD's exporter"; the real row at `2d10a2c^` finds 2 (both exporters). | SOLID | none | yes | no | — | — | item 1 (`screen_sweep.py 2d10a2c^`) | Correct the count |
| F15 | UNVERIFIED | (c) | `ssh-keygen` is absent in this sandbox: the OpenSSH label and its 70-column body come from the format, not a binary. The scrub result on that label is SOLID. | UNSURE (source) | — | — | — | — | — | — | Read the label from `ssh-keygen` on the PC when a bridge is up |

Reproduced vs static: every row above was run in this session through the named real function, except F5 (static read of
`harness-ports/bin/pc-lane.sh:516` plus a measurement of the committed sections) and F15. Deliberately skipped: the full repo suite
and a thermo-nuclear pass (outside this bounded verify); the other lanes' trees (`proofs/S0-02/` was read once at the PIN through
`git show`, never in the worktree).

## GATE RECOMMENDATION (one per component; the coordinator owns the gate)

- **(a) the sandbox exporter's order — MERGE-READY-WITH-FOLLOWUPS.** C1 holds: 0 leaks over 1,199 cut points, a red comparator,
  and M1 killed by `test_secret_straddling_the_cap_never_reaches_disk`. Follow-ups: F4 and F9 (a claim correction; it meets "false as
  stated" but fails the boundary condition: the fix is ledger text, and the code is correct).
- **(b) the PC exporter's order — MERGE-READY-WITH-FOLLOWUPS.** C2 holds on both capped paths (0 leaks), and M2 is killed by check 14.
  Follow-ups: F8c (the message path is not straddle-tested through `export()`), F8b, F4; adjacent F5.
- **(c) the private-key class — NOT-READY on F1.** GnuPG armored secret keys are never matched, and their body bytes reach the written
  file through both real exporters. F1 meets all five conditions. The one focused repair: the label alternation plus a per-family test.
  If that test also covers a keyword-prefixed BEGIN line and plain PKCS#8, it closes F8a and F8d too. F2 and F3 are follow-ups.
  (The verdict does not depend on the export label I did not produce: no key was generated. Both labels in the gpg 2.4.4 binary,
  `PRIVATE KEY BLOCK` and `SECRET KEY BLOCK`, go unmatched.)
- **(d) the screen row — MERGE-READY-WITH-FOLLOWUPS.** The landing's C4 holds as stated: the four named shapes, and no other regex hit
  over 175 files. The coverage is narrow (F6), and the one live in-tree instance of the class (F7, J1-1) is invisible to it.

Overall: **NOT-READY**, on F1 in component (c) only. The order fix itself, (a) and (b), is ready with follow-ups.

## Report lint (three rounds of its `fix:` hints, then pasted)
```
$ python3 scripts/report_lint.py --min-refs 15 tasks/briefs/continuity/VERIFY-AF-AP-127-report.md --root .
report_lint: 69 refs — OK 51, NEAR 1, MISS 3, UNCHECKABLE 14, UNRESOLVED 0 (worktree)
```
Round 1 was 66 refs, OK 36, MISS 16. The residual MISS lines are INSIDE pasted tool output: item 6's AST paste (the J1-1 ledger's
line 405 and the two J1-1 canonical-test lines 172 and 183). The lint's own "cited line reads" shows each cited line is exactly the line
the paste quotes. The pastes stay verbatim.

## DISCREPANCIES

1. The commit message and `docs/INCIDENT-LOG.md:475` say the row found "1 hit on HEAD's exporter"; the real row at `2d10a2c^` finds 2 (F14).
2. C5's "48,701 committed turn bodies" reproduces exactly as a number but counts sections, not bodies (F10).
3. C6: "only more redaction" vs the real re-export: 27 window extensions and 0 redactions (F9).
4. The brief's C4 paraphrase ("fires on a scrub/redact of an already-capped slice") is broader than the landing's claim (the four named
   shapes); the landing's claim holds, the paraphrase does not (F6).
5. `scripts/transcript_export.py:9-10` says every class is replaced before a byte reaches disk; heading `ts` bypasses the scrub (F4).
6. The heads moved during the lane: local 2f5b1c3 → a361204, origin 3846636 → de33838 (a transcript push at 10:20Z). The boundary
   is unchanged at a361204. Item 8 was re-run at de33838 and a361204: 0 files change.
7. The brief's other-lane list (`upstream.lock.yaml`, `docs/HARNESS-PORTS.md`, `tests/test_upstream_lock_lane_runtime.py`) differs from
   the dispatch message's list (`scripts/ci_gate.py`, `scripts/push_clean.sh`, `tests/test_ci_gate.py`, `scripts/no_laya_in_gates.py`, …).
   I touched none of either: my only repository write is this report.

## NOT-done

- No PC or bridge use (brief rule). The live Hermes `state.db` was not probed. The PC exporter was attacked on the test's own schema,
  so which `messages.role` values Hermes writes, and whether any role other than `tool` carries tool output, is UNVERIFIED.
- `ssh-keygen` is absent: the OpenSSH label and width were not read from a binary (F15). No key was generated with any tool.
- Not tested: Unicode-obfuscated secrets (zero-width characters, homoglyphs), URL- or HTML-encoded key blocks, and binary (non-UTF-8)
  DB content.
- Whether `AP_SCREEN` runs in the Hermes and Codex ports on PC lanes was not examined.
- The full repo suite was not run. Only the brief's three pytest files, the 14 checks, and the two suites per mutant were run.
- Item 4 ran on a contended box (load 1.4-1.8 on 4 cores): the ratios carry the verdict; the absolute times are indicative.
- Scratch `/tmp/vap127/` is removed at the end of the lane (the removal is recorded in the final message, not here).
