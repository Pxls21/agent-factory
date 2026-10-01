# VERIFY-SESSION-EXPORT-R2 report (task #439): issue #78's pre-export items and the known-values fix

Role: adversarial-verifier (sandbox, Opus 5.5), the original verifier of the session exporter, resumed. Brief:
`tasks/briefs/jev-laya/VERIFY-SESSION-EXPORT-R2-brief.md`. PIN: `cc488cec8b8f8a09919a7266de482e6c03f0c346` (origin's
branch tip contains it). The landing commits are `1effb39c` (issue #78's items) and `f69f54cb` (AF-AP-255). Venue: one
scratch copy of the PIN (`git archive cc488cec | tar -x`) at
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-session-export/r2pin`, called
`<pin>` below; my harness is `<scratch>/h/`. No network, no bridge, no subagents, no edit to the shared tree except
this report. No canary and no 8-character window of one is printed anywhere: canaries are named, never shown.

STATUS: DONE (2026-10-01 17:2xZ). **GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS** (R2.12): all six contract items
hold through the PIN's CLI (item 5 statically); no finding meets the blocking predicate; nine follow-ups, first a
marked export that loses a key form glued to a canary (R2-F-1, a constructed input) and its missing test (R2-F-8).

## R2.0 Premise, re-measured (16:11Z; every line matches the brief)

```
$ git rev-parse cc488cec...^{commit}
cc488cec8b8f8a09919a7266de482e6c03f0c346
$ git log --format='%h %s' ee6ad873..cc488cec
cc488cec transcripts: scrubbed sandbox chat digests (2026-10-01)
f69f54cb known-values check: a compressed target is read unpacked, one it cannot read whole is refused (AF-AP-255, task #439)
1effb39c session export: issue #78's pre-export items (task #439): R1-F-1, the canary marker, R1-F-2's tests, R1-F-7
$ git diff --stat ee6ad873 cc488cec -- <the six files and the DSV2 manifest>
 .../2026-09-25-recorded/dataset-manifest.json      |  2 +-
 scripts/known_values_check.py                      | 73 +++++++++++++++--
 scripts/session_export.py                          | 55 +++++++++----
 scripts/transcript_export.py                       |  5 +-
 tests/test_known_values_check.py                   | 71 ++++++++++++++++
 tests/test_session_export.py                       | 95 ++++++++++++++++++++++
 tests/test_transcript_export.py                    | 16 ++++
 7 files changed, 294 insertions(+), 23 deletions(-)
$ (sha256 of each file at the PIN)
5fedf0385ffedf1267f0ccaa4c88a4e214ac80002983a1d67827925afe83b48c  scripts/transcript_export.py
2613b8889aabfac98101f4e46bd3f6aeacbeac5e990176ae984c4b1165580a3f  scripts/session_export.py
37bc7b174adcd603e19e76babb6d608c08884087caad6a303694c5a3efd73ca6  scripts/known_values_check.py
1075f75afe6fb633e2e398b60e9d54a12686a17ad3f78e4fc65a935ba5a8ac33  tests/test_transcript_export.py
5758cf5322abe8f6dc4052af910d04f53c3098f041f78d09d22f1764e6d30b9f  tests/test_session_export.py
75c0884992d9774376ffef5a2a27262da305bf334a530882245eebdd7cdcf565  tests/test_known_values_check.py
$ git show cc488cec:scripts/transcript_export.py | grep -n 'def _committed\|return s in keep or'
221:def _committed(s, keep):
226:    return s in keep or bool(m) and s[m.end():] in keep and not (m.end() > 12 and _keylike(s[:m.end() - 1]))
$ git show cc488cec:scripts/session_export.py | grep -n '<the brief's seven anchors>'
184:def mark_canaries(text, counts):
712:CHAT_DIGESTS = b"transcripts/"
715:def repo_runs(repo, commit):
798:def export_source(root, src, offset, out_dir, expect_sha, key, archives, mark=False):
822:    return {"src": src, "offset": offset, "input_sha256": sha, "output": src + ".xz", "output_sha256": sha256_file(dest),
967:    mark = a.mark_own_canaries or prior.get("own_canaries") == "marked"       # AF-AP-213; a rerun keeps its mode
1085:    e.add_argument("--mark-own-canaries", action="store_true")
$ git show cc488cec:scripts/known_values_check.py | grep -n '<the brief's eight anchors>'
47:UNPACK = ((b"\xfd7zXZ\x00", "xz", lzma.LZMADecompressor), (b"\x1f\x8b", "gzip", lambda: zlib.decompressobj(31)),
49:REFUSE = ((0, b"\x28\xb5\x2f\xfd", "zstd"), (0, b"PK\x03\x04", "zip"), (0, b"7z\xbc\xaf\x27\x1c", "7z"),
51:LAYERS = 8
58:class Unreadable(Exception):
139:def _unpack(make, data):
152:def _content(fp, data):
231:    except Unreadable as e:
$ git show cc488cec:docs/INCIDENT-LOG.md | grep -c '^| AF-AP-255 |'
1
$ git diff --quiet cc488cec -- <the six files> && echo ...
the shared tree holds the PIN bytes of the six files
$ python3 -m pytest --collect-only -q -p no:cacheprovider <the three test files> | tail -1
287 tests collected
$ bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py tests/test_session_export.py tests/test_known_values_check.py
3 files set=cb32e901cbed
$ ls <scratch>/h/ | wc -l
27
$ git merge-base --is-ancestor cc488cec origin/claude/soundbox-kit-migration-iz1jwf && echo yes
yes
```

The scratch copy holds the same six files (sha256 prefixes `5fedf038`, `2613b888`, `37bc7b17`, `1075f75a`, `5758cf53`,
`75c08849`). Its size is 249 MB; the disk had 4,380 MB free after it.

## R2.1 Gates at the PIN, scratch copy (reproduced)

```
$ cd <pin> && PYTHONDONTWRITEBYTECODE=1 bash scripts/test_summary.sh tests/test_transcript_export.py tests/test_session_export.py tests/test_known_values_check.py --basetemp <private>   (16:18:32Z)
pytest-exit: 0
pytest-summary: 287 passed in 17.42s
$ (the same, 16:18:50Z)
pytest-exit: 0
pytest-summary: 287 passed in 17.60s
```

Set `3 files set=cb32e901cbed`, the brief's set. Both runs agree, and the count equals the brief's collection count.

## R2.2 R1-F-1 through the real CLI (my R1.3 attack, re-pointed at the PIN; reproduced)

`VFX_WT=<pin> python3 h/attack_a3.py <dir>` (16:18:22Z): a scratch fixture repo, its committed set checked first with
the PIN's `repo_runs`, then 40 rows through the PIN's `export --repo <fixture> --commit <c2>`. The rows that changed
since R1 (pasted; a diff against R1's own output `<scratch>/r1-a3x.out` shows only these two: its other 35 rows read
the same, and the 3 rows R1.8 added for its mutants read `gone`):

```
  edge: <uncommitted identifier>=<committed> as a token line     strict result      gone
  edge: <uncommitted identifier>=<committed> inside a line       strict result      gone
rows 40, unexpected 0
standalone gate CLI (it rebuilds the set from the manifest's repo and commit): rc 0, total 0
```

R1-F-1 is closed at its reproduction: the uncommitted identifier glued by `=` to a committed run is redacted in both
positions, and every other row is unchanged: the named rules run first on 17 of 17 committed FAKE credentials, membership
stays exact, and only the tracked files at the export commit count. The code is my R1.8 candidate verbatim
(`scripts/transcript_export.py:226`).

## R2.3 AF-AP-213, the canary marker, through the CLI (16:3xZ)

Commands: `VFX_WT=<pin> python3 h/attack_mark.py <scratch>/am` (output `r2/am.out`, 178 lines) and
`VFX_WT=<pin> python3 h/mark_disc.py <scratch>/md` (`r2/md.out`). One tape is exported twice by the PIN's CLI, with no
flag (counted) and with `--mark-own-canaries` (marked); then each source line's events are read by the PIN's own
`gate_file` with the export's committed set and the key's printed forms, so each row's gate view is compared. FAKE
canaries come from the PIN's table and are never printed; the key is a scratch key the harness makes, chosen so its
standard base64 form survives the scrub (it starts with `w` and has a `+` or `/` in its first 19 characters).

**Contract checks (all hold):**

| Check | Result |
|---|---|
| Off by default | the counted export: rc 3, gate total 37, manifest `own_canaries: counted`, `canaries_marked` {} |
| Marked export | rc 3, gate total 4: exactly the rows the marking must leave (the key's b64 form in G7, G8, G9; a credential in a raw field, W3); manifest `own_canaries: marked`; totals `canaries_marked` 26 |
| Every field the exporter writes | P1-P8d: a whole canary in the result text, `outcome.hook_errors`, `outcome.denial_kind`, a Write input (canonical JSON), a hook attachment (canonical JSON), after a backslash, a control character, a tab, a quote and a newline, in `model`, `stop_reason`, the timestamp and the call id: each marked, 0 canaries left, 0 bad lines |
| Key forms never marked | G7 (form right after a canary), G8 (right before), G9 (alone): the gate counts the form in both modes |
| A strict result | P9: the strict pass redacts the canary first; nothing to mark; 0 in both modes |
| `--offsets` rerun of a marked manifest, no flag | marked, byte-identical outputs: True |
| Rerun of a counted manifest WITH the flag | marked (identical to the marked export, not the counted one) |
| Rerun of a manifest with no `own_canaries` key | no flag: counted, identical to the counted export; with the flag: marked, identical to the marked export |
| Standalone `gate` on the marked export | rc 3, total 4 with `--key`; total 1 without it (the key forms need `--key`) |
| R1-F-1's boundary (B rows, strict results, T committed) | NAME of 11 characters with a letter and a digit: kept; 12 and 13: redacted (NAME and value gone); 12 letters only: kept. Matches "12 or more characters with a letter and a digit" |

**The JSON-line argument, by construction** (`mark_disc.py`, 74 canaries): no canary character is escaped by
`json.dumps(ensure_ascii=False)`; none holds a JSON structural character; none starts with a character an escape
sequence can end with (`"\\/bfnrtu` or a hex digit); none is non-printable; no canary is inside another; no canary's
suffix is another's prefix. So for today's table a canary in an event's JSON line is exactly a canary in one of its
strings, and the P rows confirm it on every field. **No test pins this property**: the lane tests check only that no
two canaries share an 8-character window. A future canary that starts with `n`, `t` or a hex digit, or holds a quote,
would break the argument silently (FOLLOW-UP R2-F-3).

**Question 1 (can the marking hide a value that is not a whole canary, or take part of a real secret?).** It replaces
only exact canary text, so it never hides a value that is not a canary. But it can take part of a secret that SHARES
characters with a canary: the replacement removes the shared characters from the secret too. Shown with the pseudonym
key (the one secret the gate looks for by value):

- **D1** (one Bash result, `k <canary><key b64 form minus its first character>`, the form's first character being the
  canary's last): counted: **rc 3**, total 2 (`keyfile` 1, `pseudonym-key-b64` 1). Marked: **rc 0, total 0**, and the
  output holds 43 of the form's 44 characters (the whole form: False; its 43-character tail: True). The same in a raw
  field (W2).
- The shared characters must start the form with a canary's tail (the canaries end in `8`, `=`, `e`, `f`, `m`, `w` or
  `y`; a form can start with any of them but `=`), or end the form with a canary's head (only `E`, the signature
  canary's first character, against an upper-case hex form ending in `E`). In a scrubbed text
  only the standard b64 form with a `+` or `/` survives the scrub; in a raw field every form does.

**Question 2 (does the marking change what the gate sees for a secret glued to a canary?).** Yes, in two classes; 5
of the 37 rows lose a gate count, and in the run no row gains one:

- **Raw fields.** The exporter writes the timestamp, `tool`, `call_id`, `model`, `stop_reason` and
  `outcome.denial_kind` unscrubbed, so the gate is their only check. The marker's brackets end every rule's token
  class, so a rule whose match ran through a canary no longer matches the secret after it. **D2** (`toolDenialKind` =
  `Bearer <canary><24-char secret>`): counted **rc 3**, total 4 (`bearer` 1, `bearer-lower` 1, `opaque-run` 1, the
  canary 1); marked **rc 0, total 0**, the secret in the output. W3 (`api_key=<canary><secret>`) keeps its
  `credential` count (the value class takes `[`) and loses `opaque-run`; W4 (`model` = `m-<canary><secret>`, one
  46-character run) loses `opaque-run`.
- **The key's printed forms**, when one shares characters with a canary (D1, G6, W2 above).
- In scrubbed fields (the text, `hook_errors`), no pattern count can be lost: the export's text is a fixed point of the
  same rules, so the unmarked line has no pattern count to lose. G1, G2, G10, G11: the scrub took the canary and the
  secret as one run (0 in both modes); G4, G5: the named rule took both; G3 (`<canary>=<24-char secret>`): the secret
  stays in both modes and no rule counts it in either (a bare token is not a secret shape in a normal result).
- The other direction fails loud: **D3** (`<canary>sk-<secret>`, which the sk rule's left anchor misses after the
  canary's `w`): counted rc 3 on the canary alone; marked rc 3 with `sk-key` 1. The marker gives the rule its anchor.

**Severity.** Both loss classes need a canary glued to a secret in one token. The raw fields hold what the harness
writes (a timestamp, ids, a model name, a denial kind), and nothing writes a test canary glued to the real key with a
shared character. No real-data path to either shape is shown (R2.8: the real transcripts hold one canary, which loses nothing). So both
are FOLLOW-UP (R2-F-1, R2-F-2), not blockers: the material-effect clause fails (a hypothetical input). They do falsify
the literal sentence of contract item 2, "the gate still counts them [the key's printed forms]", for the D1 shape, and
the docstring of `mark_canaries` says the same. A one-place fix: in `write()`, run the key forms and the gate patterns
on the line before and after `mark_canaries` and keep the unmarked line (the gate then counts it) when a count drops.

**Other observations.** P10: a canary cut by the cap's head seam leaves a 10-character fragment in both modes; it is
neither marked nor counted (the gate counts whole canaries only). Pre-existing cap behaviour, harmless for a FAKE
value (INFO). The flag on a counted manifest's rerun overrides the manifest's mode with no notice; the new manifest
says `marked`, so the record stays honest (INFO). The B rows are R1-F-1's behaviour through the CLI at the boundary.

## R2.4 AF-AP-255, the known-values check (17:0xZ)

Command: `VFX_WT=<pin> python3 h/attack_kv.py <scratch>/kv r2/kv_ee6ad873.py` (output `r2/kv.out`). The only secret
source is a FAKE `--token-file` the harness writes; no real source is named. One target per run; the check's own
summary line is kept; values are never printed.

**Contract checks (hold).** xz, gzip and bzip2 are read by their first bytes (controls: rc 3, the token whole 1, "unpacked
1 of 1 files"); the zstd and lz4 frame magics at byte 0 are refused (rc 2); a stream cut short (a stale `.part`) is
refused. The lane test covers zip, 7z, tar, tar inside xz, the three cut streams, the three "stream then plain bytes"
cases and nine layers; all 13 of my unpacking mutants are red there (R2.6).

**AF-AP-255 red-green on our exporter's real output.** A real export (the PIN's CLI) of a Bash result that holds a FAKE
24-character token (a bare token survives the scrub): the PIN's check on the export dir: **rc 3**, token whole 1,
"unpacked 1 of 2 files (layers: xz 1)". The check at ee6ad873 on the same dir: **rc 0, NO HIT** (it searched the xz
bytes). The incident reproduces before the fix and is fixed at the PIN.

**Question: can a target hide text from the check and still pass?** Yes. Each target below holds the FAKE token and
reads as a pass (rc 0, NO HIT):

| Target | First bytes | Result |
|---|---|---|
| zlib stream | `78 9c` | rc 0, NO HIT |
| raw deflate | none | rc 0, NO HIT |
| lzma-alone (`.lzma`) | `5d 00 00` | rc 0, NO HIT |
| LZMA2 raw (no header) | none | rc 0, NO HIT |
| base64 of the text | text | rc 0, NO HIT |
| one byte, then a gzip stream | `0a 1f 8b` | rc 0, NO HIT |
| a text line, then an xz stream | text | rc 0, NO HIT |
| lz4 LEGACY frame, compressed | `02 21 4c 18` | rc 0, NO HIT |
| a skippable frame, then that lz4 legacy frame | `50 2a 4d 18` | rc 0, NO HIT |
| a skippable frame, then the zstd magic | `50 2a 4d 18` | rc 0, read raw (not refused) |
| a skippable frame, then the lz4 frame magic | `50 2a 4d 18` | rc 0, read raw (not refused) |

The lz4 legacy block was built by the harness from the published block format (literals plus 4-byte matches, so no
8-byte window of the token is literal) and decoded by the harness's own reader of the same format: **inferred**, not
checked with an lz4 tool (none in the sandbox). The last two rows show only the first-bytes misread; that a real zstd or
lz4 file behind a skippable frame hides text is **UNVERIFIED** here (no encoder in the sandbox). The zstd and lz4 frame
formats define skippable frames that decoders skip; to my knowledge pzstd writes one before each frame (not measured).

So contract item 6's "refuses zstd ... lz4" holds for a frame at byte 0 only: lz4's legacy frame, and either format
behind a skippable frame, is read raw. **R2-F-4 (FOLLOW-UP):** our tools write only xz and JSON, and the check runs on our
own export dir, so no real path produces these (the material-effect clause fails). A one-place fix closes the whole
class: after unpacking, refuse a target that is not UTF-8 text; add the skippable-frame range (`5X 2a 4d 18`) and the lz4
legacy magic to REFUSE.

**Question: does it refuse a file our own tools write?** A finished export's outputs and manifest: no (read as
above). Four refusals of readable or harmless files, each fail-closed (exit 2), none in a finished export (INFO): an xz
stream followed by 4 bytes of stream padding (valid; `xz -t` rc 0; Python's `lzma.open` writes no padding); plain text
with `ustar` at byte 257 (read as tar); plain text that starts with `BZh9` (read as a broken bzip2); and a stale
`.part`, which only an export cut mid-write leaves (refusing it is right).
An unpacked export whose byte 257 happened to read `ustar` would be refused the same way (fail-closed, very rare).

**Other observations (INFO, not changed by the landing).** A symlink inside a directory target is skipped: a directory
holding a link to a file with the token reads rc 0, NO HIT. The shipper reads each listed output through its path, so a
symlinked output would ship unchecked; our exporter writes no links. The check reads and unpacks each target whole in
memory (up to 8 layers), so a decompression bomb would exhaust memory (a crash, a non-zero exit; not measured).

## R2.5 Stray bytes after an output (17:0xZ)

The exporter cannot write them unseen: `export_source` writes one xz stream (`lzma.open(..., "wb")`), then takes
`output_sha256` from the file on disk, so the manifest's hash covers every byte it wrote. Stray bytes come only from a
later change to a file. Measured on a harness export (the PIN's tools; the stray text is a JSON line
`Authorization: Bearer <FAKE>`, which the gate counts when it reads it):

| After the export | `gate` CLI | `ship_to_pc.plan()` (in process) | the check |
|---|---|---|---|
| nothing (control) | rc 0, total 0 | ships 2 files | rc 0 |
| plain bytes appended | rc 0, total 0 (unseen: `lzma.open` read 2 of 3 lines) | BadInput: the sha256 is not the manifest's | rc 2, refused |
| a valid second xz stream appended | rc 3, total 4 (seen) | BadInput | rc 3, HIT |
| plain bytes appended and `output_sha256` rewritten to match | rc 0, total 0 (unseen) | ships 2 files | rc 2, refused |

**Answer.** Stray bytes cannot reach a shipped export through the shipper unless the manifest is rewritten to match:
`plan()` checks each listed output's sha256 (it does not re-run the gate; it trusts the manifest's gate line). If both
are changed, only the fixed check sees them (exit 2). The gate is blind to plain trailing bytes and never compares an
output with `output_sha256`. **R2-F-5 (FOLLOW-UP):** let the standalone gate check each output's `output_sha256` and
read with the check's strict multi-stream reader, so the gate refuses trailing bytes too. Not a blocker: no path writes
stray bytes, and the ship refuses a changed output.

## R2.6 Mutants (17:0xZ)

Driver: `python3 h/mutate_r2.py <scratch>/mr2 [ids]` (outputs `r2/mut-b1.out` to `r2/mut-b5.out`). Each mutant is one
exact-anchor edit on a scratch copy of the ten lane files (at most one mutant tree at a time, deleted after its run); the
three lane test files then run with a private basetemp. Baseline first (`--base`): the unmodified copy gives
**287 passed in 20.38s**, and each of the five probes on it matches its baseline line for line, so a red mutant below is
a real failure, never a setup error (AF-AP-223). A probe then reruns one of my attacks on the mutant and prints the
lines that differ from the real code.

| Group | Mutants | Killed by the lane tests | Survive |
|---|---|---|---|
| R1-F-2, contract item 3 | X1, X2a, X2b, X3, X4a, X4b, X4c, X6 | **8 of 8** | none |
| R1 context (not in this contract) | X5, X8, X9, X10, X11a, X11b, X12, X13, X18 | X5, X8, X9, X11b, X18 | X10, X11a, X12, X13 (R1's survivors, unchanged) |
| The marking | K5, K6, K7, K7b, K8, K9, K10, K11, K13, K14 | 7 | **K5, K6, K7** |
| The R1-F-7 filter | D4, D5, D6, D7 | **4 of 4** | none |
| R1-F-1's boundary | F2, F3, F4, F5, F7 | F4, F7 | **F2, F3, F5** |
| The check's unpacking | U1-U13 (13) | **13 of 13** | none |

Each of contract item 3's mutants is red by a named test: X1 by
`test_the_gate_exempts_a_committed_run_from_the_opaque_rule_only`; X2a, X2b, X3 and X6 by
`test_strict_pass_keeps_only_an_exact_committed_run`; X4a, X4b and X4c by `test_only_an_exact_committed_run_stays_raw`.
Each probe agrees: attack_a3's rows flip from gone or pseudo to kept on X2a to X6, and X1's gate probe reads total 0
instead of 1. **Contract item 3 holds.**

The survivors of this landing's own code, with what the probe shows:

- **K5** (mark only the `text` field): survives. The marked export's gate total goes from 4 to 21: a canary in
  `hook_errors`, `denial_kind`, `model`, `stop_reason`, the timestamp or the call id is no longer marked, so the gate
  counts it. It fails loud (exit 3), but it breaks contract item 2's "on each event's JSON line", and the only marking
  test plants its canary in a result text. **R2-F-7 (FOLLOW-UP):** plant one canary per field kind in the marking test.
- **K6** (the export's gate drops the key's forms when it marks): survives. The probe's marked export goes from total 4
  to 1: the key's printed forms (G7, G8, G9) are no longer counted, so a marked export with the printed key would pass.
  The PIN's code is right (R2.3 measured the forms counted through the CLI), but no test holds contract item 2's "the
  gate still counts them" for a marked export; the unit test checks only that `mark_canaries` leaves a key form alone.
  **R2-F-8 (FOLLOW-UP, the most useful test to add):** a marked export of a result holding a scrub-surviving b64 key form
  must exit 3 with `pseudonym-key-b64` 1.
- **K7** (a manifest with no `own_canaries` reruns marked): survives. Only an old manifest's rerun changes (no longer
  identical to the counted export). Contract item 2 names no mode for an old manifest; "off by default" reads as counted,
  which is what the PIN does (R2.3). INFO.
- **F2** (`m.end() > 13`: a 12-character token-like NAME stays committed), **F3** (`> 11`: an 11-character one is
  redacted) and **F5** (no length floor) all survive; the probe's B rows flip exactly at 11 and 12. The test's names
  are 22 characters (redacted) and 8 and 19 characters without a digit (kept), so nothing pins the boundary. The PIN's
  behaviour is right through the CLI (R2.3, the B rows). **R2-F-9 (FOLLOW-UP):** add 11- and 12-character token-like
  NAME controls.

X10, X11a, X12 and X13 are R1's survivors on rules this landing did not touch (`VERIFY-SESSION-EXPORT-report.md`,
section R1.8: each only over-redacts); they are unchanged and outside this contract (INFO).

## R2.7 R1-F-7, the chat-digest filter (17:1xZ)

**The filter's paths** (`h/filter_probe.py`, `r2/filter.out`; a scratch fixture repo with one FAKE 44-character run per
path, read by the PIN's `repo_runs`): `transcripts/sandbox/`, `transcripts/pc/`, a file directly under
`transcripts/` and one three folders down are out of the set; `docs/transcripts/`, a root `transcripts.md`,
`transcriptsX/`, `Transcripts/` (case), `a-transcripts/` and `docs/` stay in. 0 of 10 differ from contract item 4.
D4 to D7 (only `transcripts/sandbox/`; `transcripts/` anywhere; the prefix without its slash; no filter) are all red
by `test_repo_runs_leave_out_the_chat_digests` (R2.6). **Contract item 4 holds.**

**The real repo at the PIN** (`h/r2_measure.py`, read-only git on the shared repo, `r2/real.out`): the production set
holds 307,489 runs; the set before the filter held 321,423; **13,934 runs leave the set** and none is added; my own
reading of the filtered set equals the production one. By shape: **0 opaque runs (40+)**, 891 key runs (20+), 13,043
tokens (12+); 11,047 hold a letter and a digit, 396 of them in mixed case. The 0 is measured; the reason is inferred
from the code: the chat digests are written through `scrub`, whose last rule turns every 40+ run into
`<opaque-redacted>`.

**Question: does the filter remove anything the strict pass or the pseudonymizer still needed?** The pseudonymizer
loses nothing at this commit (no opaque run left the set; R2.8 counts 0 pseudonymizer keeps lost on the real
transcripts). The strict pass loses the keeps that only a digest decided (R2.8 counts them). Those runs are session
text that the chat digests copied from earlier sessions, so the keep was circular (a session's text exempting itself);
the change is more redaction in strict results, never less. Nothing the contract needs is lost.

**Question: does it change how the standalone `gate` reads an export made before the landing?** Yes, in the fail-loud
direction (`h/f7_oldexport.py`, `r2/f7.out`). A fixture repo tracks one FAKE run in `transcripts/sandbox/` and one in
`docs/`; a transcript echoes both:

| Export | Its own gate | The digest-only run in the output | The docs run in the output |
|---|---|---|---|
| ee6ad873's exporter | rc 0, total 0 | raw | raw |
| the PIN's exporter | rc 0, total 0 | pseudonymized | raw |

The ee6ad873 standalone gate on the OLD export: rc 0, total 0. **The PIN's standalone gate on the same OLD export: rc 3,
total 1 (`opaque-run` 1).** `cmd_gate` rebuilds the set from the manifest's repo and commit with today's code and
never compares it with the manifest's `repo.runs_sha256`, so it cannot say why an old export now fails. On the real
data this cannot happen at the PIN's commit (no opaque run left the set); an export made at an older commit could
change only through an opaque run in an older digest (not measured). **R2-F-6 (FOLLOW-UP):** let `gate` compare
`runs_sha256` and print "the committed set changed since this export" instead of counting silently.

## R2.8 The real transcripts, counts only (17:2xZ)

Command: `VFX_WT=<pin> nice -n 10 python3 h/r2_measure.py /root/.claude/projects /home/user/agent-factory cc488cec <scratch>/r2m 3`
(`r2/real.out`; a first run without the NAME= counters is `r2/real-run1.out` and agrees on every shared line). The
production glob and `fixed_offset` (offsets fixed at the start): 390 sources, 1,701,483,551 bytes; a scratch key made
in memory; the PIN's committed set; every event through the PIN's `settle` (198,704 payload texts, **3,191 strict
results**). Where a membership test changed its verdict, the event is scrubbed again the old way and compared. Wall
652 s with 3 workers at nice 10. **Positive control** for the instrument (the attack_mark tree and its fixture repo, where
the B rows hold 12- and 13-character token-like NAMEs): it counts 4 changed verdicts and **4 of 4** changed strict
results, as expected.

| Question | Count |
|---|---|
| R1-F-1: strict results that change | **0 of 3,191** |
| R1-F-1: `_committed` keep verdicts through the NAME= branch, on the PIN's path | 194 at the PIN; 194 with ee6ad873's `_committed` on the same calls (0 changed) |
| R1-F-7: runs that leave the committed set | **13,934** (0 opaque, 891 key runs, 13,043 tokens) |
| R1-F-7: strict keep verdicts that only a digest decided (now redacted) | 141 |
| R1-F-7: strict results that change | **82 of 3,191** |
| R1-F-7: payload texts that change; pseudonymizer keeps lost | 0; 0 |
| AF-AP-213: event lines with a whole canary | 1 (`orphan`, once, in `text`; R1's dispatch named one such canary in a lane's pytest traceback; I did not match the file) |
| AF-AP-213: lines where the marking loses or adds a gate count; lines unreadable after it | 0; 0; 0 |

**R1-F-1 changes nothing on today's data:** no NAME= keep has a NAME of 12 or more characters with a letter and a digit.
R1.6's 105 counted calls of the same branch on R1's code path and data (R1's set at 6ee93223, the builder's offsets);
today's 194 count calls on the PIN's path with more transcripts, so the two numbers are not the same measure. R1.6
found no mixed-case-with-digits NAME among its 105; today's run measures R1-F-1's own criterion directly and finds 0
changes. The fix guards a shape the data does not yet hold. **R1-F-7 redacts 82 more strict results** and changes
nothing else. **The marking's loss classes (R2-F-1, R2-F-2) do not occur on the real data:** its one canary sits in a
result text and loses no gate count.

## R2.9 DSV2 and the chat export (static, 17:1xZ)

**DSV2 (contract item 5).** `git diff ee6ad873 cc488cec -- .../2026-09-25-recorded/dataset-manifest.json` changes one
line: `scripts/transcript_export.py` from `6ad316dc…` (its sha256 at ee6ad873) to `5fedf038…` (its sha256 at the
PIN). `scripts/laya_ft/build_dataset.py` records that hash from the file on disk (`C.ROOT / p`), and the dataset text
passes `transcript_export.scrub`, which the landing did not change, so only the hash can move. **Holds (static).** NOT
run: `tests/test_laya_ft.py::test_version_2_record_rebuilds_byte_identically_at_the_pin` needs the sandbox Laya venue
(`S0_01_VENUE=sandbox`, the model snapshot) and a model forward pass; I skipped it on a shared CPU.

**The chat export.** The landing's `transcript_export.py` diff is the `_committed` hunk only (the premise's 5-line
stat). `git grep` at the PIN: `_committed` is called only inside `scrub_strict`, and `scrub_strict` only by
`session_export.py`; `scrub`, `scrub_payload` and every pattern table are unchanged. So the chat export and every
other importer of `scrub` give the same output (static proof). I did not run the chat export: its `main()` reads the
real secret files for its value gate.

## R2.10 Finding inventory (no severity filter, 17:2xZ)

Evidence levels: **reproduced** (through the PIN's CLI or production function, a command above), **static** (read at the
PIN), **inferred** (reasoned from reproduced facts), **UNVERIFIED**.

| # | Class | Finding | Evidence | Contract | Canonical path | Material effect | Reproduction | Suggested fix |
|---|---|---|---|---|---|---|---|---|
| R2-F-1 | FOLLOW-UP | The marking cuts a printed key form that shares a character with a canary; the gate then misses the form. A marked export passes (rc 0) holding 43 of the 44 characters of the key's b64 form; counted, the same input exits 3 | reproduced | item 2, "the gate still counts them": falsified for this shape | yes, the CLI | none shown: a hypothetical input (no path prints the real key glued to a test canary; the real data's one canary loses nothing) | `h/mark_disc.py` D1; `h/attack_mark.py` G6, W2 | in `write()`, count the key forms and the gate patterns on the line before and after `mark_canaries`; when a count drops, write the unmarked line |
| R2-F-2 | FOLLOW-UP | Raw fields (`ts`, `tool`, `call_id`, `model`, `stop_reason`, `outcome.denial_kind`) are not scrubbed, so the gate is their only check; marking a canary glued to a secret there loses the secret's pattern counts (D2: `Bearer <canary><secret>`, rc 3 to rc 0) | reproduced | none explicit (the brief's question 2) | yes, the CLI | none shown: those fields hold harness-written values | D2; W1, W3, W4 | the R2-F-1 fix covers it; or scrub the raw fields |
| R2-F-3 | FOLLOW-UP | The JSON-line argument holds for today's 74 canaries (verified by construction and on every field), but no test pins it | reproduced + static | item 2's mechanism | yes | none today; a future canary that starts with `n`, `t` or a hex digit, or holds a quote, would break it silently | `h/mark_disc.py` | a test: no canary character is escaped or structural, none starts with an escape-tail character |
| R2-F-4 | FOLLOW-UP | The check reads raw, and passes, 9 targets that hide the token (zlib, raw deflate, lzma-alone, LZMA2 raw, base64, a byte before gzip, a line before xz, an lz4 legacy frame, a skippable frame before it); the lz4 legacy frame and either format behind a skippable frame are not refused | reproduced (the lz4 legacy block: inferred; hiding behind a real zstd skippable frame: UNVERIFIED) | item 6, "refuses ... zstd ... lz4": falsified for those variants | yes, the check's CLI | none shown: our tools write only xz and JSON | `h/attack_kv.py` | refuse a target that is not UTF-8 text after unpacking; add `5X 2a 4d 18` and `02 21 4c 18` to REFUSE |
| R2-F-5 | FOLLOW-UP | The gate is blind to plain bytes after an output's stream and never checks `output_sha256`; the shipper refuses a changed output unless the manifest is rewritten to match; the fixed check refuses either way | reproduced | none (the brief's question) | yes | none: no path writes stray bytes | `h/attack_kv.py`, stray rows | the gate checks `output_sha256` and reads with the check's strict reader |
| R2-F-6 | FOLLOW-UP | The standalone `gate` rebuilds the committed set with today's code and never compares `runs_sha256`: after R1-F-7 an old export can fail it (fixture: rc 0 to rc 3, `opaque-run` 1) with no reason given | reproduced | none (item 4 is about the set) | yes, both CLIs | fail-loud; none on the real data at the PIN (0 opaque runs left the set) | `h/f7_oldexport.py` | compare `runs_sha256`; print "the committed set changed since this export" |
| R2-F-7 | FOLLOW-UP | Mutant K5 (mark only `text`) survives the lane tests; it breaks "on each event's JSON line" and fails loud (marked total 4 to 21) | reproduced | item 2 (no test holds it) | n/a (a test gap) | none at the PIN (the code marks every field) | `h/mutate_r2.py K5` | plant a canary in each field kind in the marking test |
| R2-F-8 | FOLLOW-UP | Mutant K6 (the export's gate drops the key forms when marking) survives: a marked export with the printed key would pass, and no test would see it | reproduced | item 2, "the gate still counts them" (no test holds it) | n/a (a test gap) | none at the PIN (G7, G8, G9 counted through the CLI) | `h/mutate_r2.py K6` | a marked export of a scrub-surviving b64 key form must exit 3 with `pseudonym-key-b64` 1 |
| R2-F-9 | FOLLOW-UP | Mutants F2 (`> 13`), F3 (`> 11`) and F5 (no length floor) survive: R1-F-1's boundary at 12 is not pinned | reproduced | item 1 (no test holds the boundary) | n/a (a test gap) | none at the PIN (the B rows: 11 kept, 12 redacted) | `h/mutate_r2.py F2 F3 F5` | add 11- and 12-character token-like NAME controls |
| R2-I-1 | INFO | Contract item 1 holds through the CLI: attack_a3 40 rows, 0 unexpected, both `<uncommitted identifier>=<committed>` rows gone; the boundary is right (11 kept, 12 and 13 redacted, 12 letters kept); on the real data 0 of 3,191 strict results change | reproduced | item 1 | yes | n/a | R2.2, R2.3 (B rows), R2.8 | none |
| R2-I-2 | INFO | Contract item 2 holds on every other point: off by default; every field marked; per source and totals (also two sources with `--jobs 2`: 26 + 26 = 52); the manifest's mode; the rerun's mode; the key forms counted when not cut | reproduced | item 2 | yes | n/a | R2.3 | none |
| R2-I-3 | INFO | The flag on a counted manifest's rerun overrides the manifest's mode with no notice; the new manifest says `marked` (honest). Mutant K7 (an old manifest reruns marked) survives; the PIN reruns it counted, which matches "off by default" | reproduced | item 2 (silent on both cases) | yes | none | R2.3; K7 | optional: print the override |
| R2-I-4 | INFO | A canary in a strict result is redacted by the strict pass, not marked; a canary cut by the cap's head seam leaves a 10-character fragment in both modes, neither marked nor counted (the gate counts whole canaries only) | reproduced | none | yes | none (FAKE values) | P9, P10 | none |
| R2-I-5 | INFO | Marking can also make the gate see more: a key glued after a canary's `w` (`<canary>sk-<secret>`) misses the sk rule's anchor in both the scrub and the counted gate; marked, the gate counts `sk-key` 1 | reproduced | none | yes | fail-loud | D3 | none |
| R2-I-6 | INFO | A token right after `<canary>=` is neither redacted nor counted in either mode (a bare token is not a secret shape in a normal result); pre-existing scrub behaviour | reproduced | none | yes | not changed by the landing | G3 | none |
| R2-I-7 | INFO | Four refusals, all fail-closed (exit 2), none in a finished export: xz with stream padding (`xz -t` accepts it), `ustar` at byte 257 of plain text, plain text that starts with `BZh9` (three false refusals), and a stale `.part` from an export cut mid-write (a right refusal) | reproduced | item 6 | yes | none | `h/attack_kv.py` | optional |
| R2-I-8 | INFO | The check skips a symlink inside a directory target (pre-existing); the shipper would read a symlinked output through its path. It holds no memory bound (a bomb would crash it, fail-closed; not measured) | reproduced / static | none | yes | none on our outputs (no links) | `h/attack_kv.py` | optional |
| R2-I-9 | INFO | AF-AP-255 red-green on our exporter's real output: the PIN's check finds a FAKE token in an export (rc 3); ee6ad873's check misses it (rc 0, NO HIT) | reproduced | item 6 | yes | the fix works | `h/attack_kv.py` | none |
| R2-I-10 | INFO | Contract item 3 holds: X1, X2a, X2b, X3, X4a, X4b, X4c, X6 are each red by a named test. R1's other survivors X10, X11a, X12, X13 are unchanged | reproduced | item 3 | n/a | n/a | R2.6 | none |
| R2-I-11 | INFO | Contract item 4 holds (10 paths, 0 differ; D4 to D7 red). R1-F-7 at the PIN: 13,934 runs leave (0 opaque); on the real data 82 strict results gain redactions, 0 payloads or pseudonyms change | reproduced | item 4 | yes | more redaction, as intended | R2.7, R2.8 | none |
| R2-I-12 | INFO | Contract item 5 holds statically: one line moved, the scrubber's hash, to its sha256 at the PIN; the rebuild test was not run | static | item 5 | n/a | n/a | R2.9 | run the rebuild test on the sandbox Laya venue when the CPU is free |
| R2-I-13 | INFO | The chat export cannot change: `_committed` is called only by `scrub_strict`, which only `session_export.py` calls | static | none | n/a | n/a | R2.9 | none |
| R2-I-14 | INFO | 13 of 13 unpacking mutants are red in `tests/test_known_values_check.py` | reproduced | item 6 | n/a | n/a | R2.6 | none |
| R2-I-15 | INFO (outside this boundary) | A lone surrogate in `toolDenialKind` crashes the export (rc 1, UnicodeEncodeError) in both modes: `denial_kind` is the one string field written without `_fix`. Pre-existing; fail-loud | reproduced | none | yes | the export stops; nothing wrong is written | an in-process tape (R2.13) | `outcome["denial_kind"] = _fix(r["toolDenialKind"])` |
| R2-I-16 | INFO | The real transcripts hold 1 whole canary (`orphan`, in a result text); the marking loses or adds no gate count there | reproduced | item 2 | yes | n/a | R2.8 | none |

## R2.11 The blocking predicate, item by item (17:2xZ)

Every candidate that maps to a contract item. A finding blocks only when all five hold.

| Finding | 1 Contract | 2 Canonical path | 3 Material effect | 4 Discriminator | 5 Ownership | Blocks? |
|---|---|---|---|---|---|---|
| R2-F-1 (a key form cut by the marking) | yes: item 2, "the gate still counts them" | yes: the CLI | **no**: a constructed input; nothing writes the real key glued to a test canary with a shared character; the real data's one canary loses nothing | yes: D1, rc 3 counted vs rc 0 marked | yes | no |
| R2-F-2 (raw-field patterns lost) | weak: no explicit item | yes | **no**: the raw fields hold harness-written values | yes: D2 | yes | no |
| R2-F-3 (the JSON-line argument unpinned) | item 2's mechanism | yes | **no**: holds for every canary today | no red today (a property test would be the discriminator) | yes | no |
| R2-F-4 (formats the check reads raw) | yes for the lz4 legacy frame and the skippable-frame variants: item 6 | yes: the check's CLI | **no**: our tools write only xz and JSON, and the shipper ships only sha-checked outputs | yes: `h/attack_kv.py` rows | yes | no |
| R2-F-5 (stray bytes unseen by the gate) | no | yes | **no**: no path writes them; the shipper and the check refuse them | yes | yes | no |
| R2-F-6 (the old export and today's gate) | no: item 4 holds | yes | fail-loud only; none on the real data at the PIN | yes: `h/f7_oldexport.py` | yes | no |
| R2-F-7, R2-F-8, R2-F-9 (surviving mutants) | items 2 and 1 name behaviour, not tests; item 3's mutants are all red | n/a: the PIN's behaviour is right through the CLI | **no**: test gaps, no wrong output today | yes: the mutants | yes | no |

No finding meets all five conditions. None is a CONTRACT-DEFECT: R2-I-15 (the surrogate crash) is on the production path
but outside this landing's boundary, pre-existing, and fail-loud (it writes nothing wrong).

## R2.12 GATE RECOMMENDATION (17:2xZ)

**MERGE-READY-WITH-FOLLOWUPS.** No qualifying blocker. All six contract items hold through the real CLI and code at
the PIN (item 5 statically: its rebuild test was NOT run). Follow-ups in order of value:

1. **R2-F-8 + R2-F-1:** a marked export must still count the key's printed forms. Add the test (K6 survives today), and
   make `write()` keep the unmarked line when the marking would drop a key-form or pattern count (one place; it also
   closes R2-F-2).
2. **R2-F-4:** the check should refuse a target that is not UTF-8 text after unpacking (closes every hiding format at
   once), and refuse the skippable-frame and lz4 legacy magics, which contract item 6 names in spirit.
3. **R2-F-9, R2-F-7, R2-F-3:** pin R1-F-1's boundary at 11 and 12, plant a canary per field kind, and assert the
   canaries' JSON-safety.
4. **R2-F-5, R2-F-6:** the gate checks `output_sha256` and `runs_sha256`, reads strictly, and says why a set changed.

The recommendation depends on two things I did not reproduce, and neither can move it: the DSV2 rebuild test (static
check only), and hiding behind a real zstd or lz4 skippable frame (UNVERIFIED, no encoder here; R2-F-4 is a follow-up
either way).

## R2.13 What I reproduced, reviewed statically, skipped, and NOT done (17:2xZ)

**Reproduced** (the PIN copy `<pin>`, its CLI or its production functions; FAKE canaries and secrets; scratch keys):
the premise (R2.0); the three test files twice, 287 passed each time (R2.1); R1-F-1 through attack_a3 and the B rows
(R2.2, R2.3); the marking on 37 rows and 3 one-row discriminators, counted vs marked (R2.3); the multi-source,
`--jobs 2` totals (26 + 26 = 52); the check on 22 targets, our exporter's real output, the ee6ad873 check as the red
control, and the stray-byte rows through the gate CLI, `ship_to_pc.plan()` in process (no bridge, no network) and the
check (R2.4, R2.5); 49 mutants with a clean baseline and five probes (R2.6); the filter probe and the old-export probe
(R2.7); the real-transcript counts, twice, with a positive control (R2.8); the lone-surrogate probe of R2-I-15 (a one-row
tape whose `toolDenialKind` holds the JSON escape `\ud800`, exported counted and marked: rc 1 both times).

**Static:** the landing's three diffs; the JSON-line argument's character classes (also checked by construction); the
DSV2 hash line and `build_dataset.py`'s hash source; the callers of `_committed` and `scrub_strict`; the shipper's
`plan()`.

**Skipped, with the reason:** the DSV2 rebuild test (needs the sandbox Laya venue and a model pass; a shared CPU); the
chat export's CLI (its `main()` reads the real secret files; static proof instead); a real zstd or lz4 encoder (none in
the sandbox); a decompression bomb (memory on a shared box). I read no secret file and no environment secret, ran no
shipper against a bridge, and printed no canary, no window of one, no transcript text, no run and no assignment NAME.

**NOT done:** nothing the brief asks is left open. The coordinator's background export and benchmark were left alone (I
started and waited on only my own two measurement runs, pids 20045 and 14365).

**Cleanup (17:3xZ):** the PIN copy, the fixture dirs, the mutant trees, the basetemp and every scratch key are
deleted (0 `*.key` files left under my scratch dir); the `h/` scripts and the `r2/*.out` count files stay (to rerun,
re-extract the PIN with `git archive cc488cec | tar -x` and point `VFX_WT` at it). `git status --short` in the shared
tree shows only this report (`?? tasks/briefs/jev-laya/VERIFY-SESSION-EXPORT-R2-report.md`).
