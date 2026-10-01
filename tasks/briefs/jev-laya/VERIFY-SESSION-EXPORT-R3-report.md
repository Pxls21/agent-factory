# VERIFY-SESSION-EXPORT-R3 report (task #439): the known-value pass and the R2 follow-ups

Role: adversarial-verifier (sandbox, Opus 5.5), the original verifier of the session exporter, resumed a second time.
Brief: `tasks/briefs/jev-laya/VERIFY-SESSION-EXPORT-R3-brief.md`. PIN: `5cf654e586943ab1ed6d3fec0865012f37f2ea9c`.
Venue: one scratch copy of the PIN (`git archive 5cf654e5 | tar -x`) at
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-session-export/r3pin` (deleted at the
end), called `<pin>` below; my harness is `<scratch>/h/`. No network, no bridge, no subagents, no edit to the shared
tree except this report. Never run: `--known-values default`, the check with its default sources or on a real secret
file, `kvr/escscan.py`, `kvr/fscan.py`. Every known value I use is a FAKE value in a scratch env file or a scratch key;
no canary, no FAKE known value and no 8-character window of either is printed here, except three FAKE values built from
the tool's own fixed words (the mark's word, a canary's name, the `stop_reason` key name), which the tool prints itself
(R3.2). `<scratch>` is `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-session-export`.

STATUS: DONE (2026-10-01 18:5xZ to 20:0xZ). **GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS** (R3.13). The seven
contract items hold through the real CLI at the PIN; no finding meets the blocking predicate, none is a CONTRACT-DEFECT.
Follow-ups R3-F-1 to R3-F-8: the pass can raise a gate count into a false refusal (0.06% of random keys, not the real
key); the escaped-form blind spot has no guard (no real value needs escaping); a known value in a source path survives
in the manifest; the gate's count differs from the check's for a value met twice; the standalone gate drops
`shapes_redacted`; four test gaps (38 of 43 mutants red; P9, P2r, V4 and G2 survive, P6 is equivalent); an `--offsets`
rerun does not keep the known-value set. Not run, by rule: `--known-values default` and the real sources (R3-U-18,
R3-U-19).

## R3.0 Premise, re-measured (18:5xZ; every line matches the brief)

Every command of the brief's premise block, run as written (the git lines on the shared repo; `keyscan.py` and
`numscan.py` read first: seeded FAKE keys, and counts over the coordinator's export). Saved:
`<scratch>/r3-premise.out` and `<scratch>/r3-premise2.out`. The output lines equal the brief's
(`diff <(sed -n 75,132p brief | grep -v '^$ ') <(grep -v '^$ ' r3-premise2.out)` prints nothing). Key lines:

```
5cf654e586943ab1ed6d3fec0865012f37f2ea9c
 4 files changed, 557 insertions(+), 56 deletions(-)
a6f97928afb5d529e8cc2cfa614681ec75946c5afc8fd3fc2574d29f3a4ba92e  scripts/session_export.py
5fedf0385ffedf1267f0ccaa4c88a4e214ac80002983a1d67827925afe83b48c  scripts/transcript_export.py
37bc7b174adcd603e19e76babb6d608c08884087caad6a303694c5a3efd73ca6  scripts/known_values_check.py
9d4fbdd58f460ad790c5c5dfab6b6d81b85c174e6a24c331e7f98884ab605521  tests/test_session_export.py
59b65d9fca9309b256307bc70c94ddc3bb1d88cfbbed05aac5a9730ba3720363  tests/test_transcript_export.py
e7ccfdf1b0dbb0893702b431845ac6b8e97660628bfe26c8dbe74c74a3581c51  tests/test_ship_to_pc.py
75c0884992d9774376ffef5a2a27262da305bf334a530882245eebdd7cdcf565  tests/test_known_values_check.py
the shared tree holds the PIN bytes of the seven files
303 tests collected
4 files set=176c0132a32b
36
seeded random 32-byte keys whose hex form holds an all-digit 8-window: 84575 of 200000 (42.3%)
files 390, event lines 202346, most digits in one number 6
numbers of 8+ digits by path: 0 in all
known_values {'env_files': [], 'forms': 12, 'mode': 'default', 'names': 12, 'windows': 352}
gate total 0 files 390 bad_lines 0 values {} shapes_redacted {}
known-values: 16 secret forms, 391 files, 466681485 bytes, NO HIT
```

The 18 grep anchors print at the brief's line numbers; `escscan.out`, `fscan.out`, `cmpscan.out` and `cmp6.out` read
as the brief quotes them.

## R3.1 The four lane test files at the PIN, twice (18:58:58 and 18:59:28 UTC)

```
$ cd <pin> && for i in 1 2; do date -u +%T; PYTHONDONTWRITEBYTECODE=1 bash scripts/test_summary.sh \
    tests/test_transcript_export.py tests/test_session_export.py tests/test_known_values_check.py tests/test_ship_to_pc.py \
    --basetemp /tmp/claude-0/vse-r3/gate$i 2>&1 | tail -3; done
18:58:58
303 passed in 29.00s
pytest-exit: 0
pytest-summary: 303 passed in 29.00s
18:59:28
303 passed in 28.55s
pytest-exit: 0
pytest-summary: 303 passed in 28.55s
```

303 passed equals the premise's 303 collected (set `176c0132a32b`). The private basetemps were deleted after the run.

## R3.2 The pass through the real CLI (contract item 1): no window survives; the escaped form does

Harness: `<scratch>/h/kv3.py` (groups `esc mb ov mark ident escv mbr per jobs`), every export `--known-values key-only`
with FAKE env files and scratch keys; the leak scan reads every output file (xz unpacked, the manifest) and the run's
stdout and stderr, and prints names only. Outputs: `<scratch>/r3/kv3-a.out` to `kv3-f.out`. One caveat on the
report's no-value promise: three FAKE values were built from the tool's own fixed words (the mark's word, the canary
name `bearer-lower`, the `stop_reason` key name), which the tool prints itself; no other piece of a FAKE value appears.

**Windows that start inside an escape** (`esc`, 13 FAKE tokens, each known only by the window that follows an escape):
the letter of `\n`, `\t`, `\r`, `\b`, `\f`; each of the five offsets inside `\u001b` (`u`, `0`, `0`, `1`, `b`); a run of
four escapes; an escape that is the string's start; two windows after two escapes in one string. Every line stays JSON,
every window and its escape go to one mark, and the check finds nothing (repeated lines folded; full in
`<scratch>/r3/kv3-a.out`):

```
esc    rc=0 leaks(out)=[] leaks(stdout+stderr)=[]
       esc-n 'a<redacted> b'   (esc-t, esc-r, esc-b, esc-f the same)
       esc-u1 .. esc-u5 'x<redacted> y'
       esc-run  '\t\r\n<redacted>\n\t'
       esc-end  '<redacted>'
       esc-two  'p<redacted>q'
       check rc=0 hits={}
```

**Multi-byte neighbours** (`mb`, `mbr`): a window between 2-, 3- and 4-byte characters and after a combining mark
(`é<redacted>ü`, `中<redacted>文`, `😀<redacted>🎉`); a non-ASCII value whole (redacted); a value whose bytes start with a
UTF-8 continuation byte and one whose bytes end with a lead byte (both widened to the whole character:
`'a <redacted> b'`, `'c <redacted> d'`). A cut piece of a whole-only value stays (`'pre <F:mb-utf> post'`): values that
are not token-like are known whole only, by the check's own rule (the check: NO HIT on the same output).

**Overlapping and touching values** (`ov`): two values that overlap by 8 characters, two that touch, two one character
apart, a value inside another, and a window of one touching a window of the other:
`<<redacted>>`, `(<redacted>)`, `(<redacted>-<redacted>)`, `(<redacted>x<redacted>)`, `[<redacted>]`, `<redacted>`.

**A property fuzz of `redact_values` against an independent oracle** (`h/fuzz_rv.py`, in process, the real function):
random event-shaped lines with every escape class, multi-byte characters, DEL, U+2028, combining marks, and pieces of 4
FAKE tokens (one periodic), 3 whole-only values and a FAKE key's six forms, inside strings, numbers and keys. The oracle
finds the occurrences itself, widens with its own JSON string tokenizer, merges, and predicts the line or the refusal:

```
fuzz n=40000 seed=1 {'lines': 40000, 'with_hits': 37738, 'refused': 9469, 'agree': 40000, 'disagree': 0, 'survivors_outside_marks': 0, 'survivors_touching_marks': 0, 'bad_utf8': 0}
fuzz n=40000 seed=2 {'lines': 40000, 'with_hits': 37696, 'refused': 9572, 'agree': 40000, 'disagree': 0, 'survivors_outside_marks': 0, 'survivors_touching_marks': 0, 'bad_utf8': 0}
```

Negative controls (the same fuzz on mutant trees, 20,000 lines): P6 306 disagreements, P1 59 (each a refusal where a
line was due), P4 4,895; P2r 0 (the fuzz's needles never end inside a character; the CLI probe `mbr` covers that).

**Lines with no known value are written byte for byte** (`ident`: a line with escapes, `"`, `\`, ESC, DEL, CRLF, U+2028,
an 8-digit number and hex): `key-only == absent-env: True ; key-only == pass-off: True` (the pass off = `redact_values` a
no-op in process). On the real data the coordinator's compare scan, re-run by me (`kvr/cmpscan.py`, `kvr/cmp6.py`, counts
only), equals its saved output byte for byte: 200,706 identical lines, 30 different, 24 with a new mark; the other 6
differ in `text` only, each with fewer opaque pseudonyms (the committed set, as the brief says). `--jobs 3` writes the
same lines as `--jobs 1`.

**Meaning outside the spans:** bytes outside a span are copied, never re-encoded; the widening removes only the escape
or the character a window overlaps (`esc-run` loses the one `\n` its window began on), and a merge joins only spans
that overlap or touch. The fuzz holds this exactly (80,000 of 80,000 lines equal the oracle's).

**Windows the mark and its neighbours form** (`mark`): the pass does not rescan, so a line can hold a known window that
the pass itself made. Three FAKE constructions, each caught by the export's gate (exit 3) and by the check:

| Case | What the written line holds | Export | Gate values | Check |
|---|---|---|---|---|
| a token-like value built around the mark's word; another known value in the line | the mark's word, a window of the first value | rc 3 | `ZQ_R value: 1` | rc 3, `ZQ_R value: 1` |
| a whole-only value: the mark's last 6 characters and 2 letters; those 2 letters follow a known value | the value whole, across the mark's end | rc 3 | `ZQ_W value: 1` | rc 3, `ZQ_W value: 1` |
| a token-like value holding a canary's name; that canary marked (`--mark-own-canaries`) | 5 windows inside `[canary:<name>]` | rc 3 | `ZQ_P value: 5` | rc 3, `ZQ_P value: 5` |

So no mark-formed window ships; each such run refuses (fail-loud). A real random secret holding the mark's word or a
canary name is not a practical case (INFO R3-I-11).

**The escaped-form blind spot is real and nothing flags it** (`escv`, the brief's question): whole-only FAKE values
holding a character `json.dumps` escapes. The line holds the escaped form; the pass, the gate and the check all search
the raw bytes (the first line shortened; full in `<scratch>/r3/kv3-f.out`):

```
escv   rc=0  gate total=0 values={}   redacted: ZQ_BACKSLASH_END, ZQ_DEL_MID, ZQ_U2028_MID
       quote-mid      value in the event's text (decoded) True  | redacted False
       backslash-mid  value in the event's text (decoded) True  | redacted False
       backslash-end  value in the event's text (decoded) False | redacted True
       tab-mid        value in the event's text (decoded) True  | redacted False
       del-mid        value in the event's text (decoded) False | redacted True
       u2028-mid      value in the event's text (decoded) False | redacted True
       check rc=0 {} (NO HIT)
```

A value with a quote, a backslash before its last character, or a control character ships whole, and the export exits
0 with the check's NO HIT. A trailing backslash is caught by luck (the needle matches the first byte of `\\`); DEL and
U+2028 are not escaped by `json.dumps(ensure_ascii=False)`. No test and no guard names this: `grep -i escap` over the
pass and its tests finds only the widening's comments, and `value_table` takes such a value silently. A non-UTF-8 env
file is the same class: its latin-1 value is a row in the manifest (`latin.env:ZQ_LAT value`) but can never match the
UTF-8 export (`env` group: the value ships whole, rc 0). Today no real value needs escaping or holds a non-ASCII byte
(the coordinator's `escscan.out`), so this is FOLLOW-UP R3-F-2, not a blocker.

## R3.3 ValueOutsideString on the real path, and how loud the refusal is

`vos` group, two FAKE constructions:

```
vos-key rc=2 leaks(out)=[] leaks(stdout+stderr)=[] outdir=['-vos']
       no manifest
       stderr: session_export: -vos/a.jsonl: a known value (pseudonym-key base64url, pseudonym-key base64url-nopad) outside a string value || session_export: -vos/b.jsonl: a known value (pseudonym-key base64url, pseudonym-key base64url-nopad) outside a string value
vos-num rc=2 leaks(out)=[] leaks(stdout+stderr)=[] outdir=['-vos', 'd.jsonl.xz']
       no manifest
       stderr: session_export: -vos/c.jsonl: a known value (d.env:ZQ_DIGITS value) outside a string value
       ship.plan: BadInput: no readable manifest.json with sources and a gate in <W>/vos/o3
```

`vos-key`: a crafted scratch key whose base64url form begins with the first 8 characters of the `stop_reason` key name;
every event line holds that key, so every source refuses. `vos-num`: an all-digit FAKE token (16 digits, token-like)
whose window is the 8-digit `timedOutAfterMs`; that source refuses, the other source's output stays in the out dir with
no manifest, and the shipper's own `plan()` refuses the dir. The refusal is loud: exit 2, one stderr line per source
naming the source path and the value NAMES and why, no value printed, no manifest. It does not name the field. The out
dir is left non-empty, so a rerun into it stops at "out dir not empty".

**Can it fire on real-shaped data?** The event keys are fixed names (`seq`, `src`, `line`, `ts`, `role`, `kind`, `tool`,
`call_id`, `text`, `truncated`, `outcome`, `model`, `stop_reason` and the outcome's and truncated's own keys); a tool's
input is a string (`canon`), so no transcript-made key reaches a line. Numbers are `seq`, `line`, `exit_code`,
`timed_out_after_ms` and the cap's counts. A refusal needs a key window inside a key name (a base64url window equal to 8
characters of a fixed name: about 1 in 3 x 10^14 per window pair) or an 8+ digit number holding one of the key's all-digit
windows (the export's longest number is 6 digits; `truncated.dropped` reaches 8 digits only past a 10 MB text, and then
the chance is about 1 in 10^8 per window). Not a practical case at the PIN.

**A test gap:** no test runs a ValueOutsideString refusal through the export. Mutant P9 (the exception not caught in
`export_source`) survives the four files; the probe shows the run then exits 1 with a traceback and leaves
`a.jsonl.xz.part` in the out dir (R3-F-6). The behaviour at the PIN is right (above).

## R3.4 The values (contract item 2) and `--known-env-file` / `--known-values`

`--known-values` is required (argparse; mutant R4, a default of `key-only`, is red). `key-only` reads no source: the
key's 6 forms and 260 windows for a 32-byte key, or 4 forms and 187 windows when the key's base64 holds no `+` or `/`
(its url forms are then the same values, kept once; several of my scratch keys). `default` was **never run** (standing
rule); statically it is `key_values(key)` plus `known_values(default_sources())`, `default_sources()` =
KNOWN_VALUE_SOURCES plus the four EXTRA_ENV names, and the test with the reader replaced pins that tuple (mutants R5 and
V9 red). The real manifest names 12 rows: the key's 6 forms, `.pc-bridge.env` PC_BRIDGE_TOKEN value and PC_BRIDGE_URL
value and host, `api.env:TYPESAFE_API_KEY value`, `env:CLAUDE_CODE_MESSAGING_TOKEN value`, `env:GH_TOKEN value` (names
only, read from the manifest).

`--known-env-file` edge cases through the CLI (`env` group; `<base>` is my scratch dir):

| Env file | Exit | What happens |
|---|---|---|
| only values shorter than 8 | 2 | `--known-env-file <base>/short.env is missing or holds no value of 8 or more characters`; no out dir |
| comments only; an empty file | 2 | the same refusal |
| a value of exactly 8 characters | 0 | taken (whole only: not token-like) |
| a directory | 2 | `value gate: cannot read the source adir.env (IsADirectoryError)` |
| a FIFO | 2 | `cannot read the source fifo.env (NotRegularFile)`, at once, no hang |
| a symlink to a good file | 0 | followed; the manifest records the LINK's base name (`link.env`) |
| a dangling symlink; a missing file | 2 | the "missing or holds no value" refusal |
| latin-1 bytes | 0 | the ASCII token is redacted; the latin-1 value is a row that can never match the UTF-8 export, and ships whole (R3-F-2's class) |
| the same file twice | 0 | one row per value (forms 7), `env_files: ['good.env', 'good.env']` |
| CRLF, `export `, quotes | 0 | parsed as the check parses it |

Every refusal prints the path and no value. A refused file prints a misleading first line too:
`transcript_export: value gate: source <path> missing or empty, skipped`, then the refusal (R3-I-14).

**The mirror with the check (the brief's question on the three rows with no windows):** exact by construction for every
env, env-file and raw-file source: `transcript_export.known_values` loads `known_values_check.py` by path at run time and
calls its own `_env_values`, `_forms`, `_windows`, `_read_regular` and `MIN_VALUE`, so the window rule (16+ token
characters with a digit), the host form, the minimum length and the quote stripping are the check's own code, not a
copy. The key's six forms are a reimplementation (`key_values`), pinned equal to the check's `_raw_forms` and window by
`test_the_key_forms_are_the_checks_raw_forms` (mutants V6, V7, V8 red). The rule's application is pinned by
`test_without_the_pass_the_gate_and_the_check_find_them` for one windowed value and two whole-only forms (a URL and its
host). So a piece of the bridge URL, its host, or GH_TOKEN is caught by neither tool, exactly as the brief says, and the
two tools cannot drift apart on it. No test or guard covers the escaped-form blind spot (R3.2).

**A value met twice keeps its first row** (two files, one file twice, two names in one file): verified (`cnt` and the
`twice` row above). No test holds it: mutant V4 (no dedup) survives; its effect is on counts and the manifest's `forms`,
never a leak (R3.5).

**An `--offsets` rerun does not keep the known-value set** (`rerun` group): an export made with a FAKE env file, rerun
from its manifest WITHOUT the file, exits 0 with the value whole in the output (`rr-2nd rc=0 leaks(out)=['rerun-T(whole)']`,
`env_files=[]`); the same rerun with the file is byte-identical. The rerun takes `own_canaries` from the manifest and the
committed set from its commit, but neither the known-value mode nor the env files (R3-F-8).

## R3.5 The gate's value count against the check's (contract item 3)

The gate's window "index" is the index into `sorted(set(windows))` (both `_windows` functions dedup and sort), so a
value with repeated windows counts each distinct content once, as the check does; the union across files is the check's
union too (`cnt2`: one value in two files, gate 10, check 10, equal). A value cannot span a line break: an env value is
cut at `\n` and at `\r` (`_env_values`), a token-like window holds no line break, and the key's forms hold none; inside a
line, `json.dumps` writes every newline as `\n`.

Where the counts differ (`cnt`, `cnt-path`, `mark`; the check's per-name dicts are cut from these lines for width, the
full lines are in `<scratch>/r3/kv3-c.out`):

```
cnt    a                          gate={'a.env:ZQ_T value': 18, 'a.env:ZQ_U value': 14} (sum 32) | check rc=3 (rows 2, total 32 HIT(S)) | per-name equal=True
cnt    a+b                        gate={'a.env:ZQ_T value': 18, 'a.env:ZQ_U value': 14} (sum 32) | check rc=3 (rows 3, total 50 HIT(S)) | per-name equal=False
cnt    a twice                    gate={'a.env:ZQ_T value': 18, 'a.env:ZQ_U value': 14} (sum 32) | check rc=3 (rows 4, total 64 HIT(S))
cnt    c (two names, one value)   gate={'c.env:ZQ_ONE value': 18} (sum 18) | check rc=3 (rows 2, total 36 HIT(S)) | per-name equal=False
```

1. **A value met twice:** the gate counts it under its first row only (the dedup of item 2); the check counts it under
   every row it reads. Item 2's dedup and item 3's "is the check's count" cannot both hold for such a value. Zero and
   non-zero still agree on event lines (R3-F-4).
2. **The manifest:** the check reads every file under the out dir, `manifest.json` too; the gate reads the `.xz` files
   only. The manifest holds paths, canary names and fixed words. `mark` P-ctl: check 5 hits, gate 0 (the canary's
   NAME in the manifest's gate block). `cnt-path` (a FAKE window in a source's directory name): every event's `src` is
   redacted (`-p-<redacted>/p.jsonl`), but the manifest, the summary's `folders` stdout line and the output file's own
   name keep the path (the last checked separately: the out dir's path holds the window). The export exits 0 (gate 0); the check over the out dir exits 3. Item 7's "no output prints a
   value" is falsified for this constructed input (R3-F-3).

**`shapes_redacted`, LOWER:** a count the pass takes off a line reaches the total in every case I built: `std` shape
(`Bearer <FAKE>` in the raw `denial_kind`): `shapes={'bearer': 1, 'bearer-lower': 1}`, gate total 2, rc 3; D2 with the
secret known (R3.6): total 4 with `opaque-run` held. `lost()` counts drops per pattern name, so a line that loses one
match and gains another of the same name nets to no hold, but then the gate still counts the gained one.

**`shapes_redacted`, RAISE: yes, the pass can add a count** (`raise` group). A committed hex run (AMENDMENT 3 keeps it
as text) that holds a window of the key's hex form is cut by the pass; a remainder of 40+ identifier characters is a new,
uncommitted `opaque-run` match (lines shortened; full in `<scratch>/r3/kv3-d.out`, where my display regex also prints
the mark's `edac` as `<hex4>`):

```
rs-key-in rc=3  redacted={'pseudonym-key hex': 5} shapes={} | gate total=2 patterns={'opaque-run': 2}
       cut@0 (56 left)          <redacted><hex56>  f
       cut@56 (56 left)         <hex56><redacted>  f
       cut@28 (28+28)           <hex27><redacted><hex28>  f
       40-hex cut@0 (32 left)   <redacted><hex32>  f
rs-contro rc=0  redacted={} | gate total=0          (the same four committed runs, a key that holds none of their windows)
```

(`cut@28` loses one character more: the key's previous hex window matches there too, by chance; 5 matches for 4 runs.)

The pass turns a ship into a refusal (fail-loud, never a leak), and nothing in the output names the pass as the cause:
the operator sees `pattern:opaque-run 2` and `shapes_redacted {}`. On the real data this needs a key hex window inside a
committed 48+ character run: 0.06% of seeded random keys on today's corpus (R3.9); not the real key (its export's gate
reads 0). R3-F-1.

**The standalone gate** (`session_export.py gate DIR --key K`) reads 0 where the export's own gate refused: `std` shape
(export rc 3, total 2: shapes held) and `std` value (export rc 3, total 1: a mark-formed window) both give
`standalone gate rc=0 ['total 0']`. The docstring says the standalone gate counts no known value; it does not say it
drops `shapes_redacted`. The shipper reads the manifest's total, so no refused export ships (R3-F-5, which extends R2-F-6).

## R3.6 R2-F-1, R2-F-2 and R2-F-8 re-attacked with the pass on (contract item 4)

My R2 discriminators (`h/mark_disc.py` D1 to D3), unchanged, through `h/re_r3.py`, which adds `--known-values
key-only` to each export call, and in a second run also a FAKE env file holding D2's and D3's FAKE secrets
(`<scratch>/r3/re.out`):

```
### key-only
D1 the key's b64 form overlapping a canary, in a Bash result
  counted rc 0 total 0; nonzero patterns []; nonzero canaries/key forms []; key b64 whole in output False; its 43-char tail in output False
  marked  rc 0 total 0; nonzero patterns []; nonzero canaries/key forms []; key b64 whole in output False; its 43-char tail in output False
D2 raw toolDenialKind: Bearer canary+secret
  counted rc 3 total 4; nonzero patterns [('bearer', '1'), ('opaque-run', '1'), ('bearer-lower', '1')]; nonzero canaries/key forms [('archive-env', '1')]; the secret in output True
  marked  rc 3 total 4; nonzero patterns [('bearer', '1'), ('opaque-run', '1'), ('bearer-lower', '1')]; nonzero canaries/key forms [('archive-env', '1')]; the secret in output True
D3 a canary glued before sk-<secret> in a Bash result (the scrub's left anchor fails on the canary's w)
  counted rc 3 total 1; nonzero patterns []; nonzero canaries/key forms [('env-grep', '1')]; the secret in output True
  marked  rc 3 total 1; nonzero patterns [('sk-key', '1')]; nonzero canaries/key forms []; the secret in output True
### with-env
D1 (the same two lines as above: rc 0 total 0 in both modes)
D2 raw toolDenialKind: Bearer canary+secret
  counted rc 3 total 4; nonzero patterns [('bearer', '1'), ('bearer-lower', '1')]; nonzero canaries/key forms [('archive-env', '1')]; the secret in output False
  marked  rc 3 total 4; nonzero patterns [('bearer', '1'), ('bearer-lower', '1')]; nonzero canaries/key forms [('archive-env', '1')]; the secret in output False
D3 a canary glued before sk-<secret> in a Bash result (the scrub's left anchor fails on the canary's w)
  counted rc 3 total 1; nonzero patterns []; nonzero canaries/key forms [('env-grep', '1')]; the secret in output False
  marked  rc 0 total 0; nonzero patterns []; nonzero canaries/key forms []; the secret in output False
```

- **R2-F-1 is closed:** at R2 the marked D1 export passed holding 43 of the key form's 44 characters; now no window of
  any of the key's six forms is in any of the four D1 outputs (a separate scan of every output file, every 8-byte
  window: `key-form windows in the output: 0` in counted and marked, key-only and with-env). The pass takes the form
  before the marking. The marking never sees a key form, so the guard's key-form branch is defence in depth in
  production (`found` always holds the key's forms).
- **R2-F-2 is closed:** with the secret unknown, D2's marked line stays unmarked (the guard) and the gate counts the
  bearer shapes, the 44-character run and the canary (rc 3). With the secret known, the pass takes it, the `opaque-run`
  count it took is held (total 4 = 3 counted + 1 held), and the marked run still exits 3.
- **D3 marked with the secret known exits 0, rightly:** the secret is gone, and the marker no longer makes an `sk-` shape.
- **A canary count is not held (INFO R3-I-10):** in counted mode D1's canary loses its last character (shared with the
  form) to the pass, so the gate's whole-canary count goes from 1 to 0 and the run exits 0 (R2: rc 3). Only a FAKE
  canary's 19-character piece ships (the same scan: the canary is not whole, 12 of its 13 windows are in the output, in
  all four runs; the marking cannot mark a piece). The landing's test comment says this. The claim "the pass never turns
  a refusal into a ship" holds for pattern counts, not for canary counts; the real export runs marked, where the canary
  is never counted.
- **R2-F-8 is closed:** mutant K6 (the export's gate drops the key forms when marking) is red
  (`test_a_key_form_glued_to_a_canary_never_ships`).

## R3.7 R2-I-15 and R2-F-9 (contract items 5 and 6)

- **R2-I-15:** a lone surrogate in `toolDenialKind` (written into the transcript with `ensure_ascii`, so as `\ud800`):
  `sur-key rc=0`, `denial_kind ['zq?kind <F:sur-T>']`, and with the FAKE value known `sur-env rc=0`, the value redacted
  in the same field. Mutant R3 (`_fix` removed) is red.
- **R2-F-9:** `test_a_token_like_name_before_a_committed_run_is_kept_up_to_11_characters` holds names of 11 characters
  (kept), 12 with a letter and a digit (redacted) and 12 letters (kept). Mutants F2 (`> 13`), F3 (`> 11`) and F5 (no
  length floor), all R2 survivors, are red now.
- **R2-F-7 closed too, by the way:** mutant K5 (mark only the `text` field) is red now
  (`test_marking_never_hides_a_shape_in_a_raw_field` plants its canary in `denial_kind`).

## R3.8 The records (contract item 7)

- The manifest's block, every run: `known_values {mode, env_files (base names), names (sorted label + form), forms,
  windows}`; `totals.values_redacted`, `totals.shapes_redacted`, `canaries_unmarked`; `gate.values`,
  `gate.shapes_redacted`. Mutant R1 (env files by full path) and R2 (`values_redacted` out of the totals) are red.
- `values_redacted` counts NEEDLE matches, not value occurrences: one whole 24-character token counts 1 + 17 (`ov`: a
  value met whole three times counts 36). The real export's 56 are window matches, as `fscan.out` says (INFO R3-I-13).
- **No output prints a value:** every run's stdout, stderr and output files were scanned for every FAKE value whole and
  by every 8-byte window: nothing, except (a) the self-made cases above (the mark's word, a canary name, the latin-1 and
  escaped values, which no tool can see), and (b) a FAKE window in a source PATH, which the manifest, the `folders`
  stdout line and the output file name keep (R3-F-3).
- **Every existing test export call has `--known-values key-only`:** an AST scan of `tests/test_session_export.py` and
  `tests/test_ship_to_pc.py` finds 16 + 1 export calls; the one without the flag in its text is the mode test's loop,
  whose first case omits it on purpose and asserts that stderr names the flag, so its exit 2 is for the right reason (no
  call is green only because argparse failed). No other script or test calls the export.

## R3.9 Chance redactions by the key's hex windows, on real-shaped text (the brief's question)

`h/hexscan.py` reads the coordinator's export at the PIN (`exports/session-export-2026-10-01-kv`, counts only, never a
line's text) and 20,000 seeded random FAKE keys (never the real key). For each 8-character hex window in an event's
strings (lower or upper case, not mixed) it records the context and whether a key's hex (lower) or HEX (upper) form
holds it; it also counts the positions where a cut would leave a 40+ remainder of a 48+ identifier run (the RAISE of
R3.5). Positive control first (`<scratch>/r3/hexctl`, 5 planted lines): each planted window of key 0 found in its
context, a 40-hex run with no key window not, 34 RAISE positions for a 64-hex run (offsets 0 to 16 and 40 to 56). Then:

```
event lines 202346; lines holding an 8-hex window 202346; hex window positions 4195714
expected chance matches per random key = positions x 57/16^8 = 0.0557
  pseudonym positions    112505  expected/key 0.00149  simulated: keys with >=1 match 5 of 20000 (0.025%), mean 0.00050
  uuid      positions   1581126  expected/key 0.02098  simulated: keys with >=1 match 2 of 20000 (0.010%), mean 0.00020
  hex40     positions    201432  expected/key 0.00267  simulated: keys with >=1 match 5 of 20000 (0.025%), mean 0.00455
  hex64     positions    604086  expected/key 0.00802  simulated: keys with >=1 match 27 of 20000 (0.135%), mean 0.01360
  other     positions   1696565  expected/key 0.02252  simulated: keys with >=1 match 19 of 20000 (0.095%), mean 0.00510
  any       keys with >=1 chance redaction: 54 of 20000 (0.270%)
RAISE: positions where a cut leaves a 40+ remainder of a 48+ identifier run 376168; expected/key 0.00499; simulated keys with >=1: 12 of 20000 (0.060%)
```

(112,505 pseudonym positions = 5 windows x the manifest's 22,501 pseudonyms, a cross-check.) Every line holds a hex
window because every `src` holds a session id; most positions repeat, so the chance that a key hits at all is set by the
distinct windows: **about 1 key in 370 would redact at least one hex window somewhere in today's corpus, and about 1 in
1,700 would turn the export into a false refusal (R3-F-1).** The real key does neither: the real export's
`values_redacted` has no `pseudonym-key` row and its gate reads 0. The chance grows with the corpus (each export reads
every transcript), roughly in proportion to its distinct hex windows.

What a chance redaction would hide: a piece of a sha256 or a commit id (a reader loses the digest; a later compare by
digest fails), of a pseudonym (`[opaque:ab<redacted>cd]` no longer joins with its other occurrences, and the manifest's
`pseudonyms` total, counted before the pass, no longer matches the output), or of a session id in `src` (every event of
that source changes `src`, while the manifest and the file name keep the path). None is a secret, and the gate still
counts nothing it should not, except the RAISE. Base64 windows: 8-character runs of the base64 alphabet are common
(words), but a match needs 1 in 64^8 per window pair; negligible.

## R3.10 Mutants of the pass, the value table, the gate count, the guard and the records

`h/mutate_r3.py`: each mutant one exact-anchor edit (asserted to match once) on a scratch copy of the lane's ten files,
the four lane test files with a private basetemp, one mutant tree at a time, deleted after its run. Clean baseline
first: `BASE the unmodified copy | 303 passed in 28.17s | red: none`, and every probe group's baseline saved
(`<scratch>/r3/mut-base.out`). 43 mutants; outputs `<scratch>/r3/mut-1.out` to `mut-3.out`.

| Area | Mutants | Red (killed) | Survive |
|---|---|---|---|
| The R2 survivors, re-anchored | K5, K6, F2, F3, F5 | all 5 | none |
| The pass | P1 no escape widening, P2 no UTF-8 widening, P2r no RIGHT UTF-8 widening, P3 `\uXXXX` as 2 bytes, P4 touching spans not merged, P5 first occurrence only, P6 non-overlapping finds, P7 no shape check, P8 the shape ignores keys, P9 ValueOutsideString not caught, P10 the pass off when marking, P11 the pass after the marking | P1, P2, P3, P4, P5, P7, P8, P10, P11 | **P2r, P6, P9** |
| The values | V1 windows dropped, V2 whole values dropped, V3 env values never windowed, V4 no dedup, V5 an empty env file taken, V6 base64url-nopad dropped, V7 key forms not windowed, V8 `KV_WINDOW = 9`, V9 default mode without the key forms | V1, V2, V3, V5, V6, V7, V8, V9 | **V4** |
| The gate's count | G1 whole once per line, G2 windows summed per file, G3 values out of the total, G4 no `found` to the gate, G5 `shapes_redacted` out of the total, G6 no cut shape recorded, G7 the pass's loss read on key forms, G8 every window index 0 | G1, G3, G4, G5, G6, G7, G8 | **G2** |
| The guard | M1 patterns only, M2 key forms only, M3 removed, M4 unmarked lines not counted | all 4 | none |
| The records | R1 env files by full path, R2 `values_redacted` out of the totals, R3 R2-I-15 undone, R4 the mode defaults, R5 EXTRA_ENV out | all 5 | none |

38 of 43 red. The five survivors, each probed through the CLI on its mutant tree (`h/survivor_r3.py`,
`<scratch>/r3/survivors.out`):

- **P2r** (no right UTF-8 widening): a value whose bytes end inside a character makes its source refuse
  (`mbr rc=2 ... a known value (mbr.env:ZQ_END value) outside a string value`) instead of being redacted (PIN: rc 0,
  `'a <redacted> b'`). Fail-closed; no test holds the right side (the landing's M3 covers the left).
- **P6** (non-overlapping finds): a periodic value's overlapping occurrence keeps its tail: `'x <redacted>AB y'` (PIN:
  `'x <redacted> y'`). Equivalent for the leak property (an uncovered stretch can never hold a whole window, since its
  first window would itself be found); the fuzz: 306 lines differ, 0 survivors. INFO.
- **P9** (ValueOutsideString not caught): rc 1 with a traceback and a `.part` file left, instead of rc 2 (R3.3).
- **V4** (no dedup): counts change (`a twice`: the gate's whole count doubles, 19 and 15 instead of 18 and 14), never a
  leak; no test holds item 2's "a value met twice keeps its first row".
- **G2** (windows summed per file): `cnt2` gate 14 against the check's 10; no test holds item 3's "a union across files".

The builder's own 26 mutants (M1 to M23, F2, F3, F5) were killed on the 12 new tests; mine add P2r, P6, P9, V4 and G2 as
gaps.

## R3.11 Finding inventory (no severity filter)

Columns: class · evidence · contract mapping · canonical path · material effect · reproduction · suggested fix.

| # | Class | Finding | Evidence | Contract | Canonical path | Material effect | Reproduction | Fix |
|---|---|---|---|---|---|---|---|---|
| R3-F-1 | FOLLOW-UP | **The pass can RAISE a gate count:** a key hex window inside a committed 48+ run leaves an uncommitted 40+ remainder, a new `opaque-run` match, so the export refuses (rc 3) with `shapes_redacted {}` and nothing naming the pass | reproduced | none explicit (the brief's question; item 3 speaks of the other direction) | yes, the CLI | a false refusal, never a leak; 0.06% of random keys on today's corpus; not the real key | `h/kv3.py raise` (rc 3, `opaque-run` 2; control rc 0) | record and print the counts the pass ADDED (e.g. `shapes_added`), or treat a run cut by the pass from a committed run as committed |
| R3-F-2 | FOLLOW-UP | **The escaped-form blind spot has no guard:** a known value holding a quote, a backslash before its end or a control character is written escaped; the pass, the gate and the check search the raw bytes, so it ships whole (rc 0, check NO HIT). A non-UTF-8 env value is the same class | reproduced | item 1's intent (its wording, "the bytes that are written", holds literally) | yes | none today: no real value needs escaping or holds a non-ASCII byte (`escscan.out`) | `h/kv3.py escv`, `env` (latin-1) | add each value's JSON-escaped form as a needle (and in the check), or refuse at `value_table` a value that `json.dumps` would escape or that is not UTF-8, so the gap is loud |
| R3-F-3 | FOLLOW-UP | **A known value in a source path** is redacted in every event's `src`, but the manifest (`sources[].src`, `folders`), the summary's `folders` stdout line and the output file's name keep it; the export's gate reads only the `.xz` lines (rc 0) while the check, which reads the manifest, exits 3 | reproduced | item 7 "no output prints a value": falsified for this input | yes | none: no real transcript path holds a secret, and the check reads the manifest before a ship | `h/kv3.py cnt` (`cnt-path`) | refuse a source whose path holds a known value (as the pass refuses a value outside a string), or let the export's gate read the manifest bytes too |
| R3-F-4 | FOLLOW-UP | **The gate's value count is not the check's count** when a value is met twice (two files, one file twice, two names in one file: gate 32/32/18 against the check's 50/64/36), and when the manifest holds a window (the check counts the manifest; `mark` P-ctl: 5 against 0) | reproduced | item 3 "which is the check's own whole + windows seen count": exact only per kept row and over event lines | yes (the real `gate()` in process with the real table; the check's CLI) | none: zero and non-zero agree on event lines; the check is the stricter one | `h/kv3.py cnt`, `mark` | say "per kept row, over event lines" in the docstring and the manifest, or count every row as the check does |
| R3-F-5 | FOLLOW-UP | **The standalone gate reads 0 on exports the export refused:** it counts no known value (documented) and ignores the manifest's `shapes_redacted` (not documented) | reproduced | none (extends R2-F-6, task #450) | yes, both CLIs | none: the shipper reads the manifest's total | `h/kv3.py std` (export rc 3, total 2 and 1; standalone rc 0) | add the manifest's `gate.shapes_redacted`; print that values are not counted |
| R3-F-6 | FOLLOW-UP | **No test runs a ValueOutsideString refusal through the export:** mutant P9 survives (rc 1, a traceback, a `.part` file left) | reproduced | item 1 "the run exits 2" (true at the PIN, untested) | n/a (a test gap) | none at the PIN (rc 2, a clean stderr line, no manifest) | `h/mutate_r3.py P9`; `h/kv3.py vos` | a CLI test with an all-digit FAKE token in `timedOutAfterMs`: rc 2, the line, no manifest |
| R3-F-7 | FOLLOW-UP | **Surviving mutants P2r, V4, G2:** the right UTF-8 widening, the dedup, and the window union across files are untested | reproduced | items 1, 2, 3 name them | n/a (test gaps) | none at the PIN (each probe right on the PIN) | `h/mutate_r3.py P2r V4 G2`; `h/survivor_r3.py` | three small tests: a value ending inside a character; a value in two env files; one value in two sources |
| R3-F-8 | FOLLOW-UP | **An `--offsets` rerun does not keep the known-value set:** rerun without the first run's env file, the value ships (rc 0) | reproduced | none (the rerun keeps `own_canaries` and the committed set, not this) | yes | none unless an operator reruns with another set; the check would still find the value | `h/kv3.py rerun` | refuse a rerun whose mode or env-file names differ from the manifest's |
| R3-I-9 | INFO | Chance redactions by the key's hex windows: 0.27% of random keys hit at least one window in today's corpus (digests, commit ids, pseudonyms, session ids); none for the real key | reproduced (counts only) | the brief's question | yes (the real export's lines) | non-secret text lost in a few lines; a pseudonym or `src` join could break | `h/hexscan.py` | none needed now; the same scan can be re-run as the corpus grows |
| R3-I-10 | INFO | Canary counts are not held: counted-mode D1 goes rc 3 to rc 0 when the pass cuts the canary's shared character; a FAKE 19-character canary piece ships (12 of 13 windows), unmarked | reproduced | item 3's "never turns a refusal into a ship" is about pattern counts | yes | none: the real run marks canaries, and the piece is FAKE | `h/re_r3.py`, D1 | hold canary counts the pass takes off too, or accept as the test comment does |
| R3-I-11 | INFO | Windows formed by the mark or the canary marker and their neighbours are not removed (no rescan), but the gate and the check count them (rc 3) | reproduced | item 1 | yes | fail-loud; needs a known value holding the mark's word or a canary name | `h/kv3.py mark` | none needed |
| R3-I-12 | INFO | Mutant P6 (non-overlapping finds) is equivalent for the leak property; it leaves fewer than 8 bytes of a periodic value | reproduced | item 1 "every occurrence" (literal) | n/a | none | `h/survivor_r3.py P6 per` | optional test with a periodic value |
| R3-I-13 | INFO | `values_redacted` counts needle matches (a whole token: 1 + its windows), not value occurrences | reproduced | item 7 (counts) | yes | none | `h/kv3.py ov` | name it "matches" in the docstring |
| R3-I-14 | INFO | A refused `--known-env-file` first prints "... missing or empty, skipped", then the refusal | reproduced | none | yes | cosmetic | `h/kv3.py env` | suppress the chat export's skip line for an explicit env file |
| R3-I-15 | INFO | A symlinked env file is followed; the manifest names the link, not the target | reproduced | item 7 (env file base names) | yes | none | `h/kv3.py env` | optional |
| R3-I-16 | INFO | ValueOutsideString is loud (rc 2, source and value names, no value, no manifest; the shipper refuses) and not practical on real-shaped data (fixed key names, numbers of at most 6 digits) | reproduced + static | item 1 | yes | none | `h/kv3.py vos` | none |
| R3-I-17 | INFO | Closed by this landing: R2-F-1, R2-F-2, R2-F-8, R2-F-9, R2-I-15, and R2-F-7 too (K5 now red) | reproduced | items 4, 5, 6 | yes | n/a | R3.6, R3.7, R3.10 | none |
| R3-U-18 | UNVERIFIED | `--known-values default` not run (standing rule); its wiring is pinned by a test with the reader replaced; a missing default source is skipped with one stderr line, so with every source missing it would run on the key's forms alone (the manifest's names would show it) | static | item 2 | not run | unknown | none (by rule) | optional: refuse `default` when no default source is present |
| R3-U-19 | UNVERIFIED | Pieces of the three no-window real rows (the bridge URL, its host, GH_TOKEN) are caught by neither tool, by design; whether the corpus holds such a piece cannot be measured without reading the secrets | static | the brief's question | n/a | unknown | none (by rule) | the coordinator's own scan, if wanted |

## R3.12 The blocking predicate, per finding

| Finding | 1 contract | 2 canonical repro | 3 material effect | 4 discriminator | 5 ownership | Blocks? |
|---|---|---|---|---|---|---|
| R3-F-1 RAISE | no explicit criterion | yes | **no**: a false refusal (fail-loud), none for the real key | yes | yes | no |
| R3-F-2 escaped form | item 1's intent, not its wording | yes | **no**: no real value needs escaping | yes | yes | no |
| R3-F-3 value in a path | item 7 | yes | **no**: a constructed path; the check catches it | yes | yes | no |
| R3-F-4 counts | item 3 (the "is the check's count" wording) | yes | **no**: zero and non-zero agree on event lines | yes | yes | no |
| R3-F-5 standalone gate | none | yes | **no**: the shipper reads the manifest | yes | yes (with task #450) | no |
| R3-F-6, R3-F-7 test gaps | items 1 to 3 name the behaviour | n/a | **no**: right at the PIN | yes (mutants) | yes | no |
| R3-F-8 rerun | none | yes | **no**: operator choice; the check would see it | yes | yes | no |
| INFO and UNVERIFIED rows | — | — | no | — | — | no |

No finding meets all five conditions. None is a CONTRACT-DEFECT: no real input loses data, falsifies evidence or ships a
value (the real export's gate 0 and the check's NO HIT stand; the blind spots need inputs the real sources do not hold).

## R3.13 GATE RECOMMENDATION

**MERGE-READY-WITH-FOLLOWUPS.** The seven contract items hold through the real CLI at the PIN; no blocker. The
follow-ups, most useful first: R3-F-2 (make the escaped-form blind spot loud), R3-F-1 (name the pass when it raises a
count), R3-F-3 (paths), R3-F-6 and R3-F-7 (four small tests), R3-F-5 (with task #450), R3-F-8, R3-F-4 (wording).
This recommendation does not depend on anything I did not reproduce, except that `default` mode (R3-U-18) and the real
sources' pieces (R3-U-19) were not run, by rule.

## R3.14 What I reproduced, reviewed statically, and skipped

- **Reproduced (the real CLI at the PIN copy, FAKE values, scratch keys):** the premise; the four test files twice; the
  pass on escapes, multi-byte characters, overlaps, mark-formed windows, byte identity and worker processes; the
  escaped-form and non-UTF-8 blind spots; ValueOutsideString and its loudness, with the shipper's own `plan()`; the env
  file cases; the gate's count against the check's (dedup, the manifest, a path, two files); `shapes_redacted` lower and
  raise; the standalone gate; the R2 discriminators D1 to D3 with the pass on; R2-I-15; the rerun; the AST scan of the
  test calls; 43 mutants with a clean baseline and CLI probes of the survivors; an 80,000-line fuzz of `redact_values`
  against an independent oracle, with 4 mutant controls; the hex-window measurement over the coordinator's export (counts
  only, a positive control first); the coordinator's `cmpscan.py` and `cmp6.py` re-run (equal to the saved outputs).
- **In process, with the real functions:** the fuzz; the `cnt` gate counts (`gate()` with `value_table()` needles on a
  key-only export); the pass-off identity control.
- **Static only:** `default` mode's wiring; why a value cannot span a line break; why ValueOutsideString is not
  practical on real data (the event schema); the mirror (the same check functions loaded by path).
- **Skipped, by rule:** `--known-values default`; the check with default sources or on a real secret; `kvr/escscan.py`
  and `kvr/fscan.py`; any read of a real secret or of a real line's text. **Skipped, out of scope:** R2-F-3 to R2-F-6
  (task #450), except where this landing changed them (R2-F-6: R3-F-5; R2-F-7: closed).
