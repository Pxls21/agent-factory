# VERIFY-J1-1-R1 report — independent adversarial verify of the decisions redactor (J1-1-R1) and the transcript scrubber (#187), task #189

- Lane: verify-j1-1-r1 (sandbox, shared tree, no worktree). Served model: `claude-opus-5-5` (Opus 5.5), per the session's own
  model line. No call in this lane ended in a refusal (AF-AP-154): every tool call returned output.
- PIN: `e37a052` (origin). The shared tree's HEAD moved three times during the lane (688b4bd, 1e4c40a, then 9b3bbdb and d556c9b:
  transcript digests, an S0-02 brief, a ledger plane); no boundary file changed, and at the end of the lane the nine boundary
  files in the worktree are still byte-identical to the PIN (`git hash-object` against `git rev-parse e37a052:<file>`).
- Brief: `tasks/briefs/laya/VERIFY-J1-1-R1-brief.md`. Contract sources read: `tasks/briefs/laya/J1-1-R1-brief.md` (AMENDMENT 1),
  `tasks/briefs/laya/J1-1-R1-report.md` section 12 (the D-1 ruling, N-1, N-2), the message of a318b8a (the #187 contract).
- Every secret planted in this lane is a FAKE string made up here (bodies over `QZJ8`, values prefixed `Fk2e`, `hunter2hunter2`, `Qz8…`). No `*.env`
  file and no real credential was read, printed or copied. Scratch: `/tmp/vj11r1/` only (removed at the end).
- Evidence levels used below: REPRODUCED (a driver or test ran in this lane, output pasted), STATIC (read from code, not run),
  INFERRED.

## 0. PREMISE re-measured (2026-09-23T13:07Z-13:18Z, sandbox)

The brief's two commit anchors were rewritten by push_clean (the documented PIN rule): local 5718ea0 is origin f0e431f and local
a318b8a is origin 32df68f. Tree identity across the rewrite is exact:
```
5718ea0 vs f0e431f tree:
c59bc86a453707a52c88ef13fe595835916fca45
c59bc86a453707a52c88ef13fe595835916fca45
a318b8a vs 32df68f tree:
da096e5ed802c8740c2e99aeb4180c27561a41ce
da096e5ed802c8740c2e99aeb4180c27561a41ce
--- diff 5718ea0 f0e431f (stat) ---
--- diff a318b8a 32df68f (stat) ---
```
So `git log -1 -- src/agent_factory/decisions` now prints `f0e431f J1-1-R1 landed (task #139; GATED-PENDING-VERIFY): …` and
`git log -1 -- scripts/transcript_export.py` prints `32df68f Transcript scrubber: quoted and compound credential names …` — the
same trees under the post-push SHAs. Explained; not a mismatch.

Blob ids, identical at HEAD, at the PIN `e37a052`, at 5718ea0 (decisions files) and at a318b8a (scrubber files):
```
20ebcd54f3ed7e180543c0d8036d545eb38764cd src/agent_factory/decisions/volatile.py
607b65b613e24063ca228a39f83026829735df83 src/agent_factory/decisions/canonical.py
71fc398a5340ab25076210313d87d8d4c103520f src/agent_factory/decisions/ledger.py
377ccd53da0cbb7b6ef981a08008126137cc1343 src/agent_factory/decisions/__init__.py
0afbf1b821ed9e59a7a08b7697e258b5eb4de5e5 tests/test_decisions_canonical.py
4a8bccead05fd147ecf1e8194f62694aabd55b13 tests/test_decisions_ledger.py
a47e0e5861c90912df2e3eee31a77b5bf66e1e7b scripts/transcript_export.py
8d1723beb46ecde73fdddf6a6048df32ff5635b5 tests/test_transcript_export.py
04326ece5b7a6ac59b76e2fc2a3d7ec6ff5b7c70 harness-ports/bin/hermes-session-export.py
worktree == HEAD for the boundary
```
The grep anchors match the brief's block exactly: `_BEARER` at `src/agent_factory/decisions/volatile.py:44`, then `:45`, `:53`,
`:73`, `:74`, `:82`, `:311`, `:322`, `:328-333`, `:337`, `:355`; `state_digest` at `src/agent_factory/decisions/canonical.py:7-8`,
then `:23`, `:72`, `:77`; `decision_state` at `src/agent_factory/decisions/ledger.py:42`, then `:270`, `:273`, `:404`;
`AGENT_TOKEN` at `scripts/transcript_export.py:33`. The golden commit (`01ca7d5 2026-09-23`) and both set ids match too:
```
2 files set=16a7b628685e
1 files set=73755bb9fbbf
72 passed in 2.34s            (tests/test_decisions_canonical.py tests/test_decisions_ledger.py) rc=0
23 passed in 1.00s            (tests/test_transcript_export.py) rc=0
test_hermes_session_export: 15 checks passed   rc=0
```
PREMISE: holds. No CONTRACT-INVALID stop on the premise.

## 1. Instruments and scratch

- Code intel: the brief's pack ran (`scripts/lane_context.sh … -o /tmp/vj11r1/pack.md`, rc=0, 162 lines). It names a THIRD
  consumer of the scrubber that the #187 commit message does not: `harness-ports/bin/qwen_matrix.py:126-137` (`_scrub_messages`,
  imports `scripts/transcript_export.py` by path). A literal sweep for `transcript_export` over `*.py`/`*.sh` finds the full set:
  `scripts/push_clean.sh:117-118` (`TRANSCRIPT_SYNC`: runs the exporter on every push),
  `SCRUB_SRC` at `harness-ports/bin/hermes-session-export.py:23`, `exporter` at `harness-ports/bin/qwen_matrix.py:127` (see V-11).
- Drivers use the REAL modules of the shared tree (`PYTHONPATH=/home/user/agent-factory/src`, read-only; each driver prints
  `volatile from: /home/user/agent-factory/src/agent_factory/decisions/volatile.py`). Mutants run on a `git archive e37a052` copy
  under `/tmp/vj11r1/pin` whose nine boundary blobs equal the PIN's (`git hash-object`, pasted in the lane log) and which runs
  `95 passed in 3.37s` + `15 checks passed` unmutated; pytest in that copy imports the copy's `src`
  (`VOLATILE_FROM /tmp/vj11r1/pin/src/agent_factory/decisions/volatile.py`), because the venv otherwise resolves
  `agent_factory` to the shared tree.
- Python 3.11.15. The regex engine checks signals: the PIN's exponential envval group on `'A_'*30` under a 1 s SIGALRM prints
  `interrupted by SIGALRM after 1.0 s -> the re engine checks signals` (`/tmp/vj11r1/d10_sre_signals.py`).

## 2. Item 2 — the D-1 order under conflict (REPRODUCED)

Driver `/tmp/vj11r1/d2_order.py`: 43 shapes; each runs through the real `decision_state` (`src/agent_factory/decisions/volatile.py:355`)
with the shape inside `b1.finding_sev.msg`, then through `make_row` (`src/agent_factory/decisions/ledger.py:335`) and
`def append` (`src/agent_factory/decisions/ledger.py:432`) into a scratch ledger; the last JSONL line is read back from disk (`disk_leak`), the
output is fed to `decision_state` again (`idem`), and `replay` verifies the whole file at the end. FAKE body `QZJ8…`.
```
volatile from: /home/user/agent-factory/src/agent_factory/decisions/volatile.py
ok   password: sk-                            -> 'set password: <redacted:sk> now' disk_leak=False idem=True
ok   KEY=sk-                                  -> 'set KEY=<redacted:envval> now' disk_leak=False idem=True
ok   token = run-b64url tail                  -> 'set token = <redacted:envval> now' disk_leak=False idem=True
ok   password: Bearer                         -> 'set password: <redacted:bearer> now' disk_leak=False idem=True
ok   PASSWORD=Bearer                          -> 'set PASSWORD=<redacted:envval> now' disk_leak=False idem=True
ok   api_key="Bearer .."                      -> 'set api_key="<redacted:bearer>" now' disk_leak=False idem=True
ok   TOKEN: Bearer                            -> 'set TOKEN: <redacted:bearer> now' disk_leak=False idem=True
ok   literal placeholder in prose             -> 'set the <redacted:token> is here now' disk_leak=False idem=True
ok   password: literal placeholder            -> 'set password: <redacted:token> now' disk_leak=False idem=True
ok   KEY=literal placeholder                  -> 'set KEY=<redacted:envval> now' disk_leak=False idem=True
ok   two secrets: password + token            -> 'set password: <redacted:envval> token: <redacted:token> now' disk_leak=False idem=True
ok   two secrets: sk + Bearer                 -> 'set <redacted:sk> <redacted:bearer> now' disk_leak=False idem=True
ok   two secrets: API_KEY= + password:        -> 'set API_KEY=<redacted:envval> password: <redacted:envval> now' disk_leak=False idem=True
ok   two secrets glued by comma               -> 'set password=<redacted:envval>,token=<redacted:token> now' disk_leak=False idem=True
ok   tab separator                            -> 'set password: <redacted:envval> now' disk_leak=False idem=True
ok   NBSP separator                           -> 'set password: <redacted:envval> now' disk_leak=False idem=True
ok   NBSP before colon                        -> 'set password : <redacted:envval> now' disk_leak=False idem=True
ok   ideographic space                        -> 'set password: <redacted:envval> now' disk_leak=False idem=True
LEAK full-width colon                         -> 'set password：QZJ8QZJ8QZJ8QZJ8QZJ8 now' disk_leak=True idem=True
LEAK full-width equals                        -> 'set password＝QZJ8QZJ8QZJ8QZJ8QZJ8 now' disk_leak=True idem=True
LEAK full-width equals, token run             -> 'set token＝QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8 now' disk_leak=True idem=True
LEAK zero-width space before colon            -> 'set password\u200b: QZJ8QZJ8QZJ8QZJ8QZJ8 now' disk_leak=True idem=True
ok   two spaces (collapsed by normalize)      -> 'set password: <redacted:envval> now' disk_leak=False idem=True
LEAK SK- upper                                -> 'set SK-QZJ8QZJ8QZJ8QZJ8QZJ8 now' disk_leak=True idem=True
LEAK Sk- mixed                                -> 'set Sk-QZJ8QZJ8QZJ8QZJ8QZJ8 now' disk_leak=True idem=True
ok   BEARER upper                             -> 'set <redacted:bearer> now' disk_leak=False idem=True
ok   bEaReR mixed                             -> 'set <redacted:bearer> now' disk_leak=False idem=True
ok   ToKeN mixed run                          -> 'set ToKeN: <redacted:token> now' disk_leak=False idem=True
ok   Password= mixed                          -> 'set Password=<redacted:envval> now' disk_leak=False idem=True
ok   Api_Key: mixed                           -> 'set Api_Key: <redacted:envval> now' disk_leak=False idem=True
LEAK Password= 7 chars                        -> 'set Password=QZJ8QZJ now' disk_leak=True idem=True
LEAK lower-case PEM label                     -> 'set -----begin rsa private key----- QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8 -----end rsa private key----- no disk_leak=True idem=True
LEAK task-password: (sk eats name)            -> 'set ta<redacted:sk>: QZJ8QZJ8QZJ8QZJ8QZJ8 now' disk_leak=True idem=True
LEAK ask-password= (sk eats name)             -> 'set a<redacted:sk>=QZJ8QZJ8QZJ8QZJ8QZJ8 now' disk_leak=True idem=True
LEAK "task-password": ".."                    -> 'set "ta<redacted:sk>": "QZJ8QZJ8QZJ8QZJ8QZJ8" now' disk_leak=True idem=True
LEAK desk-secret_key: (sk eats name)          -> 'set de<redacted:sk>: QZJ8QZJ8QZJ8QZJ8QZJ8 now' disk_leak=True idem=True
LEAK flask-access_token= run (sk eats name)   -> 'set fla<redacted:sk>=QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8 now' disk_leak=True idem=True
LEAK disk-PASSWORD= short (PIN form)          -> 'set di<redacted:sk>=QZJ8QZ now' disk_leak=True idem=True
LEAK bearer eats name                         -> 'set <redacted:bearer>: QZJ8QZJ8QZJ8QZJ8QZJ8 now' disk_leak=True idem=True
LEAK sk- value then -password=                -> 'set <redacted:sk>=QZJ8QZJ8QZJ8QZJ8QZJ8 now' disk_leak=True idem=True
ok   control mask-token: run                  -> 'set mask-token: <redacted:token> now' disk_leak=False idem=True
ok   control task-api_key:                    -> 'set task-api_key: <redacted:envval> now' disk_leak=False idem=True
ok   control db_password=                     -> 'set db_password=<redacted:envval> now' disk_leak=False idem=True
replayed rows: 43 cases: 43 leaking cases: 16
```
What the JSONL holds: for every `LEAK` row the FAKE body is in the appended line on disk, and `replay` accepts all 43 rows (the
fixed-point check `restate` at `src/agent_factory/decisions/ledger.py:273` passes, because the leaked text is a fixed point of
`decision_state`). Reading of the 16 leaks:
- **The eaten name (V-1).** `sk-[A-Za-z0-9_-]{8,}` (`src/agent_factory/decisions/volatile.py:45`, no left boundary, and
  its class takes `-` and `_`) runs second (`:329`) and swallows a secret NAME that follows a word ending in `sk` and a hyphen:
  `task-password` becomes `ta<redacted:sk>`, so the widened env pass (`:333`) finds no name and the value survives. Same for
  `ask-password=`, the quoted `"task-password": "…"`, `desk-secret_key:`, and for C-F3a's `*_token` form (`flask-access_token=<run>`:
  `_TOKEN` at `:332` finds no `token` either). `_BEARER` (`:44`, class `[A-Za-z0-9._~+/-]{16,}`) does the same to a 16+ character
  hyphenated name after the word `bearer`. The controls show the mechanism: `mask-token` (the `sk-` class needs 8+ characters after
  `sk-`, `token` has 5) and `task-api_key` (7) keep their names and are redacted.
- Separators the ASCII classes do not name: normalize maps TAB, NBSP and U+3000 to one ASCII space first (redacted), but it keeps
  the full-width `：`/`＝` (NFC, not NFKC) and a zero-width space (not whitespace to `\s`): those leak (V-6).
- Case: `SK-`/`Sk-` are outside the case-sensitive `sk-` class; a mixed-case `Password=` with 7 characters is under the widened
  form's 8-character floor; a lower-case PEM label is outside the upper-case label family (V-7, all by the contract's own shapes).
- `KEY=sk-…`, `PASSWORD=Bearer …` and `KEY=<redacted:token>` are RELABELLED to envval by the unguarded class-2 pass (`:331`), the
  disclosed consequence in `tasks/briefs/laya/J1-1-R1-report.md` section 12.2; no byte leaks (V-10).

Pre-J1-1-R1 comparison (the parent of the landing commit, 32df68f, driver `/tmp/vj11r1/d2_prev.py`): every eaten-name shape
leaked there too, and so did the plain `password:` and `access_token=` forms (no widened class existed):
```
'task-password: QZJ8QZJ8QZJ8QZJ8QZJ'   -> 'set ta<redacted:sk>: QZJ8QZJ8QZJ8QZJ8QZJ8 now'
'flask-access_token=QZJ8QZJ8QZJ8QZJ'   -> 'set fla<redacted:sk>=QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8 now'
'password: QZJ8QZJ8QZJ8QZJ8QZJ8'       -> 'set password: QZJ8QZJ8QZJ8QZJ8QZJ8 now'
'access_token=QZJ8QZJ8QZJ8QZJ8QZJ8Q'   -> 'set access_token=QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8 now'
```
So V-1 is not a regression: J1-1-R1 closed C-F3a/C-F3b except where the frozen `sk`/`bearer` classes eat the name first.

## 3. Item 3 — the guard `_envval_wide` (REPRODUCED; no finding)

Driver `/tmp/vj11r1/d3_guard.py`: (a) enumerates the guard's whole keep-set, (b) runs 40,000 random differential cases (the real
`_redact_str` vs the same passes with the guard removed) and counts secret bytes kept ONLY because of the guard, (c) runs hostile
shapes through `decision_state`.
```
(a) values the guard keeps: 34 - all are prefixes of the five placeholders; alphabet: :<>abcdeiklnoprstvy
(b) fuzz cases=40000 guarded!=unguarded=18654 secret bytes kept ONLY because of the guard=0
(c) 'password: <redacted:sk>QZJ8QZJ8QZJ8'            -> 'password: <redacted:envval>'                        secret_left=False
(c) 'password: QZJ8QZJ8QZJ8<redacted:sk>'            -> 'password: <redacted:envval>'                        secret_left=False
(c) 'password: <redacteQZJ8QZJ8QZJ8'                 -> 'password: <redacted:envval>'                        secret_left=False
(c) 'password: <redacted:tokQZJ8QZJ8QZJ8'            -> 'password: <redacted:envval>'                        secret_left=False
(c) 'password: <redacted:token>;QZJ8QZJ8QZJ8'        -> 'password: <redacted:token>;QZJ8QZJ8QZJ8'            secret_left=True
(c) 'password: abcdefgh;QZJ8QZJ8QZJ8'                -> 'password: <redacted:envval>;QZJ8QZJ8QZJ8'           secret_left=True
(c) 'password: <redacted:token>&QZJ8QZJ8QZJ8'        -> 'password: <redacted:token>&QZJ8QZJ8QZJ8'            secret_left=True
(c) 'password: <redacted:tok QZJ8QZJ8QZJ8'           -> 'password: <redacted:tok QZJ8QZJ8QZJ8'               secret_left=True
(c) 'token: <redacted:token>QZJ8QZJ8QZJ8'            -> 'token: <redacted:envval>'                           secret_left=False
(c) 'token: QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8;QZJ8QZJ8QZJ8' -> 'token: <redacted:token>;QZJ8QZJ8QZJ8'               secret_left=True
(c) 'api_key=<redacted:envval>QZJ8QZJ8QZJ8'          -> 'api_key=<redacted:envval>'                          secret_left=False
(c) 'password: <REDACTED:SK>QZJ8QZJ8QZJ8'            -> 'password: <redacted:envval>'                        secret_left=False
```
Answer: no. The guard keeps a value only when the WHOLE greedy value is one of 34 fixed strings (placeholder prefixes of 8+
characters), and it changes nothing outside the match, so it cannot keep a byte the unguarded form would remove (0 of 40,000). A
placeholder followed by more value (no delimiter) becomes envval whole. Every `secret_left=True` row keeps text after a `;`, `&` or
space, and the same text survives with an ordinary value (`password: abcdefgh;…`), so it is the contract's value shape (the
scrubber's `[^\s"'&,;]{8,}`), not the guard (V-8).

## 4. Item 4 — bound after redact (REPRODUCED)

Driver `/tmp/vj11r1/d4_straddle.py`: 19 NEW shapes (the widened, quoted and compound names, `Token=`, `X-Agent-Token`, a run with
`==` padding, the relabels, OPENSSH and a mismatched END label, and the V-1 shape), each straddling every one of the 16 bounded
keys at every cut position k, with the builder's harness shape (`"a"*(limit-k-1) + " " + secret + " tail"`), then an NFC
truncation fuzz for A3:
```
single-quoted api_key                    cases=  528 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
PASSWORD spaced                          cases=  544 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
secret colon                             cases=  496 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
passwd equals                            cases=  480 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
apikey colon                             cases=  496 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
client_secret json                       cases=  668 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
X-API-KEY header                         cases=  544 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
private-key spaced                       cases=  592 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
url query                                cases=  576 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
export PASSWORD=                         cases=  623 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
Token= run                               cases=  713 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
X-Agent-Token run                        cases=  848 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
run then ==                              cases=  758 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
KEY=sk- relabel                          cases=  480 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
password: sk-                            cases=  576 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
password: Bearer                         cases=  638 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
OPENSSH, END                             cases= 1518 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
EC label with digits-free END mismatch   cases= 1428 body_leak=   0 A5_ident_fail=   0 A3_idem_fail=  0 over_limit=0
task-password (V-1 shape)                cases=  608 body_leak= 336 A5_ident_fail= 336 A3_idem_fail=  0 over_limit=0  e.g. ('b2.hit_role', 'sym', 18, 'aaaaaaaaaaa ta<redacted:sk>: Q')
A3 NFC-truncation fuzz: 20000 states, non-idempotent: 0
```
A broader A3 fuzz (`/tmp/vj11r1/d4b_idem_fuzz.py`: random mixtures of names, separators, whole and cut placeholders, FAKE
secrets, delimiters, PEM markers, `sk-`/`Bearer` prefixes, at every bounded key, 80% padded to straddle the limit), two seeds:
```
states=150000 refused=0 non-idempotent (new)=0 D-2 (known lane PIN suffix)=0
states=150000 refused=0 non-idempotent (new)=0 D-2 (known lane PIN suffix)=0
```
Answers: bound runs after redact on every path, and every bounded field is within its limit. A3 holds on every new shape (D-2 stays
the one known exception). A secret PREFIX is left on disk after the cut only when redact missed the secret in the first place: the
V-1 row above keeps `Q`, the first body byte, right at the cut (`'… ta<redacted:sk>: Q'`). Bound adds no leak of its own.

## 5. Item 5 — cost (REPRODUCED; no finding)

Driver `/tmp/vj11r1/d5_cost.py`: each pattern the brief names, pathological inputs, sizes doubling 4k to 128k characters, the
best of 3 full `sub` scans under a 5 s SIGALRM; `max-ratio` = the largest t(n)/t(n/2) from 16k up (linear about 2, quadratic about
4). All 169 rows (24 for the six `src/agent_factory/decisions/volatile.py` patterns, 18 generators x 9 `SECRET_PATTERNS` in
`SECRET_PATTERNS` at `scripts/transcript_export.py:24-45`) are in `/tmp/vj11r1/d5_cost.out`; the rows the brief singles out and the worst ones:
```
pattern / input                                                      4k       8k      16k      32k      64k     128k   (ms)
volatile._TOKEN: 'token:' repeated                                  0.29      0.58      1.19      2.38      4.62      9.14  max-ratio(>=16k)=2.01
volatile._ENVVAL: 'A_' run (the removed nested group)               0.05      0.11      0.21      0.43      0.82      1.73  max-ratio(>=16k)=2.11
volatile._ENVVAL_WIDE: 'a_' run                                     0.25      0.50      1.03      2.05      4.39      8.42  max-ratio(>=16k)=2.14
volatile._ENVVAL_WIDE: 'key"="' repeated                            0.36      0.73      1.48      2.97      5.91     12.40  max-ratio(>=16k)=2.10
volatile._PRIVKEY: BEGIN line repeated, no END                      0.08      0.16      0.34      0.69      1.38      2.79  max-ratio(>=16k)=2.06
volatile._PRIVKEY: one BEGIN then '-----END ' repeated              0.10      0.21      0.43      0.85      1.71      3.44  max-ratio(>=16k)=2.01
SECRET_PATTERNS[0]: BEGIN line repeated, no END                     0.08      0.16      0.33      0.66      1.36      2.71  max-ratio(>=16k)=2.06
SECRET_PATTERNS[1]: 'a' run (one alnum run)                         0.55      1.18      2.29      4.68      9.37     18.73  max-ratio(>=16k)=2.04
SECRET_PATTERNS[1]: '_key' run                                      0.65      1.28      2.57      5.11     10.24     20.58  max-ratio(>=16k)=2.01
SECRET_PATTERNS[1]: 'Ab1' run (the builder's)                       0.54      1.10      2.13      4.41      8.72     17.42  max-ratio(>=16k)=2.07
SECRET_PATTERNS[1]: 'key =' + space run + 'short'                   0.55      1.10      2.20      4.44      8.92     17.67  max-ratio(>=16k)=2.02
SECRET_PATTERNS[5]: 'a'+dash run+' '                                0.03      0.05      0.11      0.37      0.48      0.89  max-ratio(>=16k)=3.51
SECRET_PATTERNS[5]: '-----BEGIN ' repeated                          0.04      0.05      0.11      0.28      0.46      1.56  max-ratio(>=16k)=3.36
```
No row grows faster than linear. The three ratios above 3 are sub-millisecond timer noise on `SECRET_PATTERNS[5]` (the `xox` rule)
and `[7]`: each is followed by a ratio of 1.3-1.7, and none passes 2 ms at 128k. End to end at 64 KB (65,536 characters) through the
real entry points (`/tmp/vj11r1/d5b_endtoend.py`; 43 generators, the worst lines and the CLIs):
```
'token ' repeated                                      0.0124     0.0128      (decision_state s, scrub s)
'KEY= ' repeated                                       0.0120     0.0123
'xoxb-' + dash run                                     0.0073     0.0138
ALL generators concatenated                            0.0046     0.0061
worst decision_state: 0.0124 s   worst scrub: 0.0138 s
transcript_export CLI, one 64 KB turn: rc=0 0.057 s (includes interpreter start)
hermes-session-export, one 64 KB turn: rc=0 0.055 s (includes interpreter start)
```
Answer: every pattern is linear (AF-AP-152 not present); the worst 64 KB input costs 0.0138 s, about 70 times under the predicate's
1 s.

## 6. Item 6 — #187 by new shapes (REPRODUCED)

Driver `/tmp/vj11r1/d6_scrubber.py`: one assistant turn per shape in a fake JSONL, run through the real CLI
(`scripts/transcript_export.py --transcript <fake> --out <scratch>`, never the live transcript), and the same texts as assistant
messages in a fake `state.db` run through `harness-ports/bin/hermes-session-export.py`; each shape's FAKE value is looked up in both
outputs. `take` = a shape the #187 contract says the rule now takes (a quoted name, a compound `*_key`/`*-key` name, and every PIN
form). Then a PIN-form differential: every name of the pre-#187 rule (`git show a318b8a^:scripts/transcript_export.py`) x 4 cases x
7 separators x 3 quotes x 2 value lengths, old `scrub()` vs new.
```
CLI rc 0 -> <tmp>/out/chat-2026-09-23.md
hermes-session-export rc 0
ok  /ok   [take                ] json client_secret           cli='"client_secret": "<redacted>"' | hermes-same=True
ok  /ok   [take                ] access-key colon             cli='access-key: <redacted>' | hermes-same=True
ok  /ok   [take                ] X-API-KEY header             cli='X-API-KEY: <redacted>' | hermes-same=True
ok  /ok   [take                ] private-key spaced =         cli='private-key = <redacted>' | hermes-same=True
ok  /ok   [take                ] db_password=                 cli='db_password=<redacted>' | hermes-same=True
LEAK/LEAK [other spelling      ] backtick name                cli='`api_key`: Fk2eBacktick06' | hermes-same=True
ok  /ok   [take                ] backtick whole assignment    cli='`password=<redacted>' | hermes-same=True
ok  /ok   [take                ] backtick value               cli='api_key: <redacted>' | hermes-same=True
LEAK/LEAK [other spelling      ] backtick name+value          cli='`secret_key`: `Fk2eBacktick09`' | hermes-same=True
LEAK/LEAK [other spelling      ] YAML block scalar |          cli='password: |\n  Fk2eYamlBlock10' | hermes-same=True
LEAK/LEAK [other spelling      ] YAML folded >-               cli='api_key: >-\n  Fk2eYamlFold011' | hermes-same=True
LEAK/LEAK [other spelling      ] YAML block, compound name    cli='secret_key: |\n    Fk2eYamlBlock12' | hermes-same=True
ok  /ok   [take                ] export API_KEY=              cli='export API_KEY=<redacted>' | hermes-same=True
ok  /ok   [take                ] export db_password=""        cli='export db_password="<redacted>"' | hermes-same=True
ok  /ok   [take                ] export SECRET_KEY=''         cli="export SECRET_KEY='<redacted>'" | hermes-same=True
ok  /ok   [take                ] URL ?api_key=&               cli='https://x.example/cb?api_key=<redacted>&next=1' | hermes-same=True
ok  /ok   [take                ] URL ?access_token=&          cli='https://x.example/cb?access_token=<redacted>&x=1' | hermes-same=True
ok  /ok   [take                ] URL ?client_secret=          cli='https://x.example/cb?client_secret=<redacted>' | hermes-same=True
LEAK/LEAK [other spelling      ] Authorization: Basic         cli='Authorization: Basic RmsyZUJhc2ljQXV0aDE5' | hermes-same=True
LEAK/LEAK [other spelling      ] lower-case bearer            cli='authorization: bearer Fk2eLowerBearer20' | hermes-same=True
LEAK/LEAK [other spelling      ] hash rocket                  cli='password => "Fk2eHashRocket21"' | hermes-same=True
LEAK/LEAK [other spelling      ] Go :=                        cli='password := Fk2eGoAssign022' | hermes-same=True
LEAK/LEAK [other spelling      ] XML element                  cli='<password>Fk2eXmlTag00023</password>' | hermes-same=True
LEAK/LEAK [other spelling      ] CLI flag, space              cli='--password Fk2eCliFlag0024' | hermes-same=True
LEAK/LEAK [other spelling      ] URL userinfo                 cli='postgres://user:Fk2eUrlUserinfo25@host/db' | hermes-same=True
LEAK/LEAK [other spelling      ] secretkey (no separator)     cli='secretkey: Fk2eNoSepKey026' | hermes-same=True
LEAK/LEAK [other spelling      ] privatekey (no separator)    cli='privatekey=Fk2eNoSepKey027' | hermes-same=True
LEAK/LEAK [other spelling      ] bare key:                    cli='key: Fk2eBareKey0028' | hermes-same=True
LEAK/LEAK [other spelling      ] Stripe-shaped sk_live_       cli='sk_live_Fk2eStripe029abcdefgh' | hermes-same=True
LEAK/LEAK [other spelling      ] Python raw string            cli='password = r"Fk2eRawString30"' | hermes-same=True
LEAK/LEAK [contract value shape] comma inside value           cli='api_key: "Fk2e,Comma0031xyz"' | hermes-same=True
LEAK/LEAK [other spelling      ] full-width colon             cli='password：Fk2eFullWidth32' | hermes-same=True
ok  /ok   [take                ] camelCase apiKey             cli='apiKey: <redacted>' | hermes-same=True
ok  /ok   [take                ] lower x-api-key=             cli='x-api-key=<redacted>' | hermes-same=True
ok  /ok   [take                ] AWS quoted                   cli='AWS_SECRET_ACCESS_KEY: "<redacted>"' | hermes-same=True
ok  /ok   [take                ] tight JSON token             cli='"token":"<redacted>"' | hermes-same=True
ok  /ok   [take                ] spaced single-quoted passwd  cli="'passwd' : '<redacted>'" | hermes-same=True
ok  /ok   [take                ] tabs around =                cli='password\t=\t<redacted>' | hermes-same=True
ok  /ok   [take                ] value on next line           cli='password=\n  <redacted>' | hermes-same=True
ok  /ok   [take                ] task-password (V-1 shape)    cli='task-password: <redacted>' | hermes-same=True
contract-'take' shapes leaking through the CLI: 0
kept prose 'the sort_key: name ordering'                              -> 'the sort_key: name ordering' | old-rule-same=True hermes-same=True
FP   prose 'use primary_key=customer_identifier here'                 -> 'use primary_key=<redacted> here' | old-rule-same=False hermes-same=True
FP   prose 'see foreign_key: reference_table_name'                    -> 'see foreign_key: <redacted>' | old-rule-same=False hermes-same=True
kept prose 'hotkey: ctrl+shift+p'                                     -> 'hotkey: ctrl+shift+p' | old-rule-same=True hermes-same=True
FP   prose 'dict_key=some_dictionary_value'                           -> 'dict_key=<redacted>' | old-rule-same=False hermes-same=True
FP   prose 'the monkey_key: bananas_and_more'                         -> 'the monkey_key: <redacted>' | old-rule-same=False hermes-same=True
kept prose 'api_key: None'                                            -> 'api_key: None' | old-rule-same=True hermes-same=True
FP   prose 'api_key = os.environ["X"]'                                -> 'api_key = <redacted>"X"]' | old-rule-same=True hermes-same=True
FP   prose 'token: refreshed'                                         -> 'token: <redacted>' | old-rule-same=True hermes-same=True
FP   prose 'password: required'                                       -> 'password: <redacted>' | old-rule-same=True hermes-same=True
kept prose 'keyboard_key_map: qwertyuiop'                             -> 'keyboard_key_map: qwertyuiop' | old-rule-same=True hermes-same=True
FP   prose 'partition_key = "user_id_bucket"'                         -> 'partition_key = "<redacted>"' | old-rule-same=False hermes-same=True
FP   prose 'cache-key: v2-build-artifacts'                            -> 'cache-key: <redacted>' | old-rule-same=False hermes-same=True
FP   prose 'sort-key: descending_order'                               -> 'sort-key: <redacted>' | old-rule-same=False hermes-same=True
FP   prose '"idempotency_key": "order-20260923-0001"'                 -> '"idempotency_key": "<redacted>"' | old-rule-same=False hermes-same=True
FP   prose '"public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFk2e" -> '"public_key": "<redacted> AAAAC3NzaC1lZDI1NTE5AAAAIFk2e"' | old-rule-same=False hermes-same=True
kept prose 'the secret: flag is documented'                           -> 'the secret: flag is documented' | old-rule-same=True hermes-same=True
kept prose 'tokenizer: whitespace'                                    -> 'tokenizer: whitespace' | old-rule-same=True hermes-same=True
prose lines redacted by the new rule: 12 of 18
PIN-form differential: 1848 inputs; old redacts but new does not: 0; outputs differ: 0
```
Answers:
- Every shape the #187 contract names is taken (21 of 21, 0 leaks), through both exporters, byte-identical between them. The V-1 shape
  that leaks in the decisions redactor (`task-password: …`) is scrubbed here, because the credential rule runs before the scrubber's
  own sk rule, and that rule starts `\bsk-` (`scripts/transcript_export.py:37`).
- "Every existing name form is kept": 1,848 PIN-form inputs, 0 regressions and 0 changed outputs. The replacement and the private-key
  rule's first place are unchanged (the a318b8a diff touches line 33 and two comment lines only).
- False positives on prose: 9 of the 18 prose lines are newly redacted by the compound class (`old-rule-same=False`); 3 more were
  already redacted before #187. A masked census of committed text (`/tmp/vj11r1/d6b_corpus.py`; it never prints a value, only the
  matched name and the value's shape):
```
part 1: 1489 committed files, 254560 lines; lines #187 newly redacts: 161
  top newly matched names (lower-cased): [('owner_key', 40), ('private_key', 25), ('ac_key', 21), ('api_key', 15), ('token', 13), ('unknown-key', 12), ('missing-key', 7), ('secret_key', 6), ('access_key', 3), ('cache_key', 3), ('password', 3), ('probe_key', 3), ('server_key', 2), ('pair_key', 2), ('lock_key', 2)]
  newly redacted values ending like code ( ) , [ ] vs other: {'-': 161, 'code': 12}
part 2: 120 committed transcript digests; lines not a fixed point of today's scrubber: 0
```
  `unknown-key` and `missing-key` are this repo's own refusal texts (`decision-state-unknown-key: b1.finding_sev.timestamp`), so a
  transcript that quotes a decisions refusal loses its detail (V-12). Part 2: no committed digest holds a value today's scrubber would
  still change (INFO V-25).
- Other spellings leak through both exporters (17 rows marked `other spelling`/`contract value shape`): V-13. The realistic ones are
  `Authorization: Basic …`, a lower-case `bearer` (the scrubber's Bearer rule at `scripts/transcript_export.py:35` has no `re.I`),
  YAML block scalars (`password: |`), `--password <value>`, a URL's userinfo, `secretkey:`/`privatekey=`/bare `key:` (the compound
  class needs a `_`/`-`), and a Stripe-shaped `sk_live_…` under 40 characters.
- Cost: linear (section 5).

## 7. Item 7 — the goldens (REPRODUCED)

Mutants on the scratch copy (runner `/tmp/vj11r1/mut.py`, full output `/tmp/vj11r1/mut_G.out`): `gold` = the two golden tests
(`test_golden_digests_exact`, `test_relanding_stable`) alone; `dec` = the whole 72-test pair.
```
G1 [one golden state byte] edits=1 compile=n/a :: KILLED          gold: collected=2/2 -> 2 failed in 0.11s   (unmutated: rc=0 2 passed)
G2 [one golden variant byte] edits=1 compile=n/a :: KILLED        gold: collected=2/2 -> 1 failed, 1 passed   (test_relanding_stable; unmutated: rc=0 1 passed)
G3 [the fixture's own expected_digest] edits=1 :: SURVIVED        dec: collected=72/72 -> 72 passed in 2.51s
G4 [drop the privkey pass]            gold: 2 passed  dec: 5 failed, 67 passed   :: KILLED (not by the goldens)
G5 [drop the sk pass]                 gold: 2 passed  dec: 6 failed, 66 passed   :: KILLED (not by the goldens)
G6 [drop the bearer pass]             gold: 2 passed  dec: 4 failed, 68 passed   :: KILLED (not by the goldens)
G7 [drop the upper-case env pass]     gold: 2 passed  dec: 2 failed, 70 passed   :: KILLED (not by the goldens)
G8 [drop the token pass]              gold: 2 passed  dec: 6 failed, 66 passed   :: KILLED (not by the goldens)
G9 [drop the widened env pass]        gold: 2 passed  dec: 11 failed, 61 passed  :: KILLED (not by the goldens)
G10 [bound is the identity]           gold: 2 passed  dec: 5 failed, 67 passed   :: KILLED (not by the goldens)
G11 [decision_state redacts BEFORE normalize] dec: 1 failed, 71 passed :: KILLED by test_order_is_normalize_then_redact (unmutated: rc=0 1 passed)
```
Answers:
- The 7 digests are bound to the fixture STATES: one byte of a golden state reds both golden tests, one byte of a variant reds
  `test_relanding_stable`. They are NOT bound to any redaction pass or to bound: every golden state is short and secret-free (the
  longest field is 63 characters), so dropping any of the six passes or the cut leaves both golden tests green; other tests kill
  each one. This confirms VERIFY-J1-1's Oracle A on `test_golden_digests_exact` (`tasks/briefs/laya/VERIFY-J1-1-report.md:264`) (V-4).
- The fixtures carry an `expected_digest` key that equals the test constants today but that no test reads (G3 survives; a literal
  sweep finds no reader) (V-19).
- The order test's discriminator survives D-1: `token:  <run>` (two spaces) is bridged by no class before normalize (the widened
  form takes at most one space each side), and a `decision_state` that redacts before normalizing is red (G11). The builder's x10
  (`\s*`) re-run here is red for the same reason (section 8).

## 8. Item 8 — mutants (REPRODUCED; NEW mutants only, none of the builder's 23 or the coordinator's five)

Runner `/tmp/vj11r1/mut.py` (outputs `/tmp/vj11r1/mut_N.out`, `/tmp/vj11r1/mut_S.out`, `/tmp/vj11r1/mut_S123.out`). Per mutant: a
fresh copy of `/tmp/vj11r1/pin`, an exact-count edit, `py_compile`, the collection count equal to the baseline (AF-AP-78:
`BASELINE collected (unmutated): {'dec': 72, 'gold': 2, 'scr': 23}`; every row collected 72/72 or 23/23), the run, and every
killing test re-run on the UNMUTATED copy (AF-AP-138; a parametrized id is re-run as its whole function). Scrubber rows also run
`harness-ports/tests/test_hermes_session_export.py` (`15 checks passed` on every row). One harness defect of mine, disclosed: the
first S1-S3 run printed `KILL NOT CREDITED` because my parser cut parametrized node ids at their first space; after the fix the
same three mutants re-ran and are credited (`/tmp/vj11r1/mut_S123.out`: `the killing test(s) on the UNMUTATED copy: rc=0 8 passed`).

For each SURVIVOR, `/tmp/vj11r1/d8_discriminate.py` runs a discriminating input through the real function of the unmutated copy
and of the mutated copy (one subprocess per side). The four suspected-equivalent survivors get a 60,000-call `decision_state`
differential instead (`sha256 of all outputs: unmutated af9d99e75bcc8b60`, and `equal=True` for N6, N7, N15, N19).

| id | mutant (file) | run (mutated) | verdict | killing test, unmutated re-run / survivor discriminator |
|---|---|---|---|---|
| N1 | `_SK.sub` and `_BEARER.sub` swapped (`src/agent_factory/decisions/volatile.py:329-330`) | 72 passed | SURVIVED | `Bearer sk-QZJ8…`: unmutated `Bearer <redacted:sk>`, mutant `<redacted:bearer>` (relabel, no leak) |
| N2 | token class before the upper-case env form (`:331-332`) | 72 passed | SURVIVED | `token <32-run>KEY=hunter2hunter2`: unmutated `token <redacted:token>=<redacted:envval>`, mutant `token <redacted:token>=hunter2hunter2` (LEAK) |
| N6 | bound `rstrip()` -> `strip()` (`:350`) | 72 passed | SURVIVED (equivalent) | 60k differential equal: normalize already stripped the left edge |
| N7 | bound `rstrip()` -> `rstrip(" ")` | 72 passed | SURVIVED (equivalent) | 60k differential equal: after normalize every whitespace is an ASCII space |
| N8 | bound cuts UTF-8 bytes | 1 failed, 71 passed | KILLED | `test_bound_cuts_code_points_strips_trailing_whitespace_every_field_within_limit`; unmutated `1 passed` |
| N9 | bound cuts at limit-1 | 2 failed, 70 passed | KILLED | the bound test + `test_decision_state_idempotent_including_a_cut_inside_each_placeholder`; unmutated `2 passed` |
| N10 | `_SK` floor 8 -> 9 (`:45`) | 72 passed | SURVIVED | `sk-QZJ8QZJ8`: unmutated `<redacted:sk>`, mutant unchanged (LEAK) |
| N11 | `_BEARER` floor 16 -> 17 (`:44`) | 72 passed | SURVIVED | `Bearer QZJ8QZJ8QZJ8QZJ8`: unmutated `<redacted:bearer>`, mutant unchanged (LEAK) |
| N12 | `_BEARER` capital `Bearer` only (no `(?i)`) | 72 passed | SURVIVED | `bearer QZJ8…`: unmutated `<redacted:bearer>`, mutant unchanged (LEAK) |
| N13 | `_TOKEN` run floor 32 -> 33 (`:53`) | 2 failed, 70 passed | KILLED | `test_order_is_normalize_then_redact`, `test_secret_redacted_every_class`; unmutated `2 passed` |
| N14 | `_ENVVAL_WIDE` without SECRET (`:75`) | 72 passed | SURVIVED | `client_secret: QZJ8…`: unmutated `client_secret: <redacted:envval>`, mutant unchanged (LEAK) |
| N15 | `_ENVVAL_WIDE` without `API_?KEY` | 72 passed | SURVIVED (equivalent) | 60k differential equal: `KEY` has no left boundary and matches inside `API_KEY` |
| N16 | widened value takes `& , ;` (`:76`) | 72 passed | SURVIVED | `password: QZJ8QZJ8;QZJ8…`: unmutated keeps `;QZJ8…`, mutant redacts it (over-redaction) |
| N17 | widened form, no quote before the value | 3 failed, 69 passed | KILLED | env forms, over-limit identity, straddle; unmutated `3 passed` |
| N18 | privkey label without digits (`:83-84`, 2 edits) | 72 passed | SURVIVED | `-----BEGIN SM2 PRIVATE KEY----- …`: unmutated `<redacted:privkey>`, mutant keeps the block (LEAK) |
| N19 | `_PRIVKEY` without `re.S` (`:85`) | 72 passed | SURVIVED (equivalent) | 60k differential equal: normalize turns every newline into a space before redact |
| N20 | privkey pass LAST (`:328`) | 72 passed | SURVIVED | `secret: -----BEGIN RSA PRIVATE KEY----- <body> -----END …`: unmutated `secret: <redacted:privkey>`, mutant `secret: <redacted:envval> RSA PRIVATE KEY----- <body> …` (LEAK of the body) |
| N21 | guard knows the token placeholder only (`:317`) | 1 failed, 71 passed | KILLED | `test_token_run_keeps_the_token_placeholder_and_no_placeholder_is_relabelled`; unmutated `1 passed` |
| N22 | `_TOKEN` without the quote after the name | 2 failed, 70 passed | KILLED | token forms, no-relabel test; unmutated `2 passed` |
| N23 | the fixed-point `restate` removed (`src/agent_factory/decisions/ledger.py:273`) | 1 failed, 71 passed | KILLED | `tests/test_decisions_ledger.py::test_state_not_canonical`; unmutated `1 passed` |
| S1 | credential rule without `re.I` (`scripts/transcript_export.py:33`) | 4 failed, 19 passed | KILLED | 4 quoted/compound items; the whole function unmutated `8 passed` |
| S2 | no quote before the value | 4 failed, 19 passed | KILLED | 4 quoted items; unmutated `8 passed` |
| S3 | lookbehind -> `\b` | 2 failed, 21 passed | KILLED | the AWS and DJANGO items; unmutated `8 passed` |
| S4 | separator `\s*` -> `\s?` | 23 passed | SURVIVED | `password  =  Fk2eValue01`: unmutated redacted, mutant unchanged (LEAK) |
| S5 | private-key rule after the credential rule | 1 failed, 22 passed | KILLED | `test_key_block_after_a_credential_keyword_is_scrubbed_whole`; unmutated `1 passed` |
| S6 | private-key rule without the END-less `\Z` | 1 failed, 22 passed | KILLED | `test_private_key_block_is_scrubbed_whole_or_to_the_end`; unmutated `1 passed` |
| S7 | Bearer floor 8 -> 9 (`:35`) | 23 passed | SURVIVED | `Bearer Fk2eVal8`: unmutated redacted, mutant unchanged (LEAK) |
| S8 | credential value floor 8 -> 9 | 23 passed | SURVIVED | `password: Fk2eVal8` (8 characters): unmutated redacted, mutant unchanged (LEAK) |
| S9 | `api[_-]?key` -> `api[_-]key` | 23 passed | SURVIVED | `apikey: Fk2eValue01`: unmutated redacted, mutant unchanged (LEAK) |
| S10 | `Authorization` dropped | 23 passed | SURVIVED | `Authorization: Fk2eRawToken01`: unmutated redacted, mutant unchanged (LEAK) |
| S11 | compound class needs 1+ character before `_key` | 23 passed | SURVIVED | `_key: Fk2eValue01`: unmutated redacted, mutant unchanged (LEAK) |
| S12 | `scrub(txt)[:cap]` -> cap BEFORE scrub (`scripts/transcript_export.py:86`) | 1 failed, 22 passed | KILLED | `test_secret_straddling_the_cap_never_reaches_disk`; unmutated `1 passed` |
| S13 | `secret` dropped | 23 passed | SURVIVED | `secret: Fk2eValue01`: unmutated redacted, mutant unchanged (LEAK) |
| S14 | `passwd` dropped | 23 passed | SURVIVED | `passwd=Fk2eValue01`: unmutated redacted, mutant unchanged (LEAK) |

The item-7 golden mutants G1-G11 are in section 7. Totals over the 45 NEW mutants (N 20, S 14, G 11): 23 KILLED, 22 SURVIVED; of
the survivors, 4 are equivalent on the production path (N6, N7, N15, N19), 1 is dead fixture data (G3), and 17 are test gaps with
a pasted discriminator (N1, N2, N10, N11, N12, N14, N16, N18, N20, S4, S7, S8, S9, S10, S11, S13, S14): V-2, V-5, V-14.

The brief's own example list mapped: "swap sk and bearer" = N1 (survives); "token class before the upper-case env form" = N2
(survives); "widen `\s?` to `\s*`", "drop the guard's prefix half" and "drop `(?<=_)`" are the builder's x10, x12 and x6, so I
re-ran them as an independent check and did not count them as new: `x10r … 1 failed, 71 passed :: KILLED`,
`x12r … 3 failed, 69 passed :: KILLED`, `x6r … 4 failed, 68 passed :: KILLED` (each killing test green unmutated), which confirms
those three rows of `tasks/briefs/laya/J1-1-R1-report.md` section 12.6; "change bound's rstrip" = N6/N7 (equivalent) and N8/N9
(killed); the scrubber's "drop `re.I`", "drop the second `[\"']?`" and "lookbehind -> `\b`" = S1, S2, S3 (killed).

## 9. Item 9 — every write path (REPRODUCED + two instruments)

Sinks in `src/agent_factory/decisions/` (literal sweep for `sha256|os.write|open(|canonical(|normalize(|redact(|bound(|
decision_state(|state_digest(`), cross-checked with graft (`graft ask … --in src/agent_factory/decisions`) and code-review-graph
`callers_of` (production callers of `redact`: `decision_state` only; of `bound`: `decision_state` only; of `normalize`:
`decision_state` only, plus two name collisions with `unicodedata.normalize`; of `_sha256_hex`: `_compute_row_id`,
`_compute_row_digest`, `_validate_row`; of `make_row`: tests only — no production caller exists yet, J1-3's harvest is not built):
- The only file write is `os.write` in `append` (`src/agent_factory/decisions/ledger.py:484`). Before it, `append` runs
  `_validate_row` (`:449`) and `_check_line` on the exact bytes (`:465`), both of which end in the fixed-point check
  `decision_state(qid, row["state"], None) == row["state"]` (`:273`).
- `make_row` builds `state` and `state_digest` with `decision_state` and `state_digest` (`:404-405`) and validates its own row.
- `state_digest` is `hashlib.sha256` over `canonical(decision_state(` (`src/agent_factory/decisions/canonical.py:77-78`).
- ONE digest of a state without `decision_state`: step (c), `_sha256_hex(canonical(row["state"]))` (`src/agent_factory/decisions/
  ledger.py:254`). It is only a comparison, and step (d) at `:273` runs right after it on every append and replay, so a state that
  is not a `decision_state` fixed point never passes.
- `replay` validates every line with the same `_validate_row`.
Negative control through the real `append` (`/tmp/vj11r1/d9_bypass.py`: hand-built rows whose three digests are computed correctly):
```
caught class, raw            -> REFUSED decision-row-state-not-canonical
caught class, raw sk         -> REFUSED decision-row-state-not-canonical
over the limit (201 chars)   -> REFUSED decision-row-state-not-canonical
missed shape (V-1), raw      -> REFUSED decision-row-state-not-canonical
already a fixed point        -> APPENDED
rows on disk: 1 | hunter2hunter2 on disk: False
```
Answer: no path writes or digests a state around `decision_state`; the ledger stores exactly the fixed points of `decision_state`.
So the ledger is as safe as `decision_state`'s coverage and no safer: V-1's value reaches disk only because it is inside
`decision_state`'s own output (section 2). Adjacent (known, VERIFY-J1-1 A-6): `incumbent_answer`, `producer` and `source_ref`
(`path`, `locator`) are written verbatim, never redacted (V-17).

A new A3 counterexample surfaced while tracing the two roots (the fixed-point check passes `root=None`, `make_row` passes the
caller's root). `/tmp/vj11r1/d2b_list.py` and a follow-up probe:
```
b1.finding_sev    file          once='~x.py'                again(root='/r' ) -> RAISES decision-state-abs-path: file
b1.finding_sev    file          once='~x.py'                again(root=None ) -> RAISES decision-state-abs-path: file
b1.finding_sev    file          once='~$report.docx'        again(root='/r' ) -> RAISES decision-state-abs-path: file
ap.violates_row   action_target once='~tool'                again(root='/r' ) -> RAISES decision-state-abs-path: action_target
v1.finding_class  paths         once=['~a.py']              again(root='/r' ) -> RAISES decision-state-abs-path: paths
b1.finding_sev    file          once='src/~x.py'            again(root='/r' ) -> fixed point
root-relative '~x.py': make_row REFUSED decision-row-state-not-canonical | decision_state with root: ~x.py
```
`_path` (`src/agent_factory/decisions/volatile.py:125-142`) relativizes `/r/~x.py` to `~x.py`, then refuses that same value on the
next pass because it starts with `~`. `decision_state` is therefore not idempotent for any path field whose repo-relative form
starts with `~` (an Office lock file `~$report.docx` at the root, say), and `make_row` refuses the row (fail-closed, no bytes
written). The `decision_state` docstring (`:355-362`) names one exception, D-2; this is a second, with a different mechanism (V-3).

## 10. Item 10 — the alarm-guarded backtracking test (REPRODUCED)

The test (`_Runaway`, `tests/test_decisions_canonical.py:636-664`) installs a raising handler (`:652`), then inside the loop arms
`ITIMER_REAL` for 5 s (`:655`) one statement BEFORE the `try:` that catches `_Runaway` (`:656-658`), and disarms in that `try`'s
`finally` (`:661`). That is AF-AP-58's shape, and the edit-snapshot hook's signature matches it (`.claude/hooks/edit-snapshot.py:148`;
`scripts/ap_screen.py --tests` has no such rule: `0 hits`). Driver `/tmp/vj11r1/d10_alarm.py` extracts the REAL function by AST from
the shared tree's test file and runs it with each window made long on purpose (AF-AP-58's method), then reads the timer and the
handler:
```
extracted test_env_assignment_redaction_does_not_backtrack_exponentially lines 636 - 664
A. as written (the real redact)                             0.00s -> PASSED                                    | timer after=(0.0, 0.0) handler restored=True
B. runaway inside redact (the alarm fires in the try)       5.00s -> Failed: redact backtracked for over 5 s on 'A_A_A_A_A_A_A_A_A_A_A_A_'... | timer after=(0.0, 0.0) handler restored=True
C. alarm lands in the inner finally (window c)              5.00s -> _Runaway:                                 | timer after=(0.0, 0.0) handler restored=True
D. alarm lands between arming and the inner try (b)         0.01s -> _Runaway:                                 | timer after=(0.0, 0.0) handler restored=True
```
Answers: it cannot leave SIGALRM armed or the handler replaced (every path ends `(0.0, 0.0)` and restored). It CAN fire outside its
`try` in two one-statement windows (C and D); the test then ends in a bare `_Runaway` instead of its `pytest.fail` message. That is
still red and still correct (the box stalled for 5 s), never a hang and never a false green. It cannot hang the suite on this
interpreter: the regex engine checks signals (section 1), and the four inputs take microseconds, so a slow box does not false-red
it either (V-15). NOT verified: under xdist the test would need to run on the worker's main thread (`signal.signal` raises
`ValueError` elsewhere); xdist is not installed in the sandbox and the PC was out of bounds (V-16, UNVERIFIED). Adjacent: the ledger
file's own watchdog (`tests/test_decisions_ledger.py:836-850`) arms `signal.alarm(10)` with `SIG_DFL`, which on a hang terminates
the whole pytest process rather than failing one test; both tests disarm in `finally`, so they do not interact in sequence (INFO,
in V-15).

## 11. V-1 — two measured repair options (scratch copies only; for the coordinator's decision, not applied)

Both options run the unchanged 72-test pair and the item-2 driver on a scratch copy of the PIN.
- Option A, the pass order (no class form changes; the ruling's classes 1-4 keep their order; bearer keeps its place): move the sk pass
  after the widened env pass (`_SK.sub` from `src/agent_factory/decisions/volatile.py:329` to after `:333`), `/tmp/vj11r1/amendC`:
```
72 passed in 2.48s
ok   password: sk-                            -> 'set password: <redacted:envval> now' disk_leak=False idem=True
ok   PASSWORD=Bearer                          -> 'set PASSWORD=<redacted:envval> now' disk_leak=False idem=True
ok   task-password: (sk eats name)            -> 'set ta<redacted:sk>: <redacted:envval> now' disk_leak=False idem=True
ok   ask-password= (sk eats name)             -> 'set a<redacted:sk>=<redacted:envval> now' disk_leak=False idem=True
ok   "task-password": ".."                    -> 'set "ta<redacted:sk>": "<redacted:envval>" now' disk_leak=False idem=True
ok   desk-secret_key: (sk eats name)          -> 'set de<redacted:sk>: <redacted:envval> now' disk_leak=False idem=True
ok   flask-access_token= run (sk eats name)   -> 'set fla<redacted:sk>=<redacted:token> now' disk_leak=False idem=True
ok   disk-PASSWORD= short (PIN form)          -> 'set di<redacted:sk>=<redacted:envval> now' disk_leak=False idem=True
LEAK bearer eats name                         -> 'set <redacted:bearer>: QZJ8QZJ8QZJ8QZJ8QZJ8 now' disk_leak=True idem=True
ok   sk- value then -password=                -> 'set <redacted:sk>=<redacted:envval> now' disk_leak=False idem=True
replayed rows: 43 cases: 43 leaking cases: 9
```
  The name stays over-redacted (C-F2, filed), but no value survives; the 9 leaks left are the 8 other spellings of section 2 and
  the bearer variant. A variant that moved BOTH sk and bearer after class 4 (`/tmp/vj11r1/amendB`, also `72 passed`) opened a new
  leak, `PASSWORD=Bearer <token>` -> `PASSWORD=<redacted:envval> QZJ8…` (class 2's `\S+` stops at the space), so bearer must stay
  ahead of class 2.
- Option B, the class forms (keeps the landed order): C-F2's own proposal, `_SK = re.compile(r"\bsk-[A-Za-z0-9_-]{8,}")`, then a
  bearer guard `(?i)bearer\s+[A-Za-z0-9._~+/-]{16,}+=*+(?![\"']?\s?[:=])` (possessive, Python 3.11), `/tmp/vj11r1/amend`:
```
_SK only:           72 passed in 2.53s    replayed rows: 43 cases: 43 leaking cases: 10   (the six sk-eaten shapes closed)
_SK + _BEARER:      72 passed in 2.82s    replayed rows: 43 cases: 43 leaking cases: 9    (bearer variant closed; the contrived sk-…-password= stays)
task-password (V-1 shape)  straddle cases=608 body_leak=0 A5_ident_fail=0; A3 fuzz states=60000 non-idempotent (new)=0
amended _SK 'a-sk-' ms: 0.03 0.07 0.12 0.26 (16k..128k)    amended _BEARER 'bearer ' ms: 0.39 0.77 1.72 3.46 (linear)
```
  Option B also removes C-F2's over-redaction of words such as `task-implementer`, but it changes the sk form that the J1-1-R1 brief
  left out of the repair ("NOT in this repair: the sk- word boundary (C-F2)").
Either option needs a committed red-first test with the section-2 shapes. The golden digests are unchanged under both (the
golden test is in the 72).

## 12. FINDING INVENTORY (no severity filter; the predicate applied per finding)

Legend: class · evidence · contract mapping · canonical path · material effect · reproduction · suggested fix.

**V-1 — BLOCKER (J1-1-R1). A secret NAME eaten by an earlier class lets its value into the ledger.** REPRODUCED. `_SK`
(`sk-[A-Za-z0-9_-]{8,}`, `src/agent_factory/decisions/volatile.py:45`, no left boundary, class takes `-` and `_`) and `_BEARER` (`:44`) run before the
assignment classes (`:329-330` vs `:331-333`) and swallow a hyphen-prefixed secret name: `task-password: v` -> `ta<redacted:sk>: v`.
Eight rows of section 2 leak this way (six names eaten by `sk-`, one by `bearer`, and a contrived `sk-…-password=` where the sk
value runs into the name); in the straddle sweep 336 of 608 cases leave a body byte, including a cut prefix (section 4).
Contract: A4 C-F3b (the names "with a prefix … matched … the value becomes the envval placeholder"), A4 C-F3a (the `*_token`
assignment forms), and A4's class order rule "an assignment wins its own class". Canonical path: `decision_state` -> `make_row` ->
`append` -> the JSONL line on disk; `replay` accepts every row. Material: a secret byte of a named class survives into the ledger.
Discriminator: `task-password: <FAKE>` and its siblings (`/tmp/vj11r1/d2_order.py`), red at the PIN; the six sk-eaten shapes are
green under both options of section 11, the bearer one under option B's bearer guard. Boundary: `src/agent_factory/decisions/volatile.py` (`_redact_str`). Not a regression: the pre-J1-1-R1 parent leaked
every one of these shapes and the plain ones too. It EXTENDS C-F2, filed as over-redaction only:
`secret_bytes_in_ledger=False` at `tasks/briefs/laya/VERIFY-J1-1-report.md:330`, `task-implementer failed` at `tasks/briefs/laya/VERIFY-J1-1-report.md:392`.
Once C-F3a/C-F3b exist, the same missing boundary also makes a value leak.
Incidence: 0 of 1,016 committed non-vendored `.md/.py/.yaml/.yml/.sh` files hold the shape (a word ending in `sk-`, a secret
name and a separator); 39 words ending in `sk-` exist there, all C-F2 over-redaction. Fix: option A or B of section 11, plus a red-first test.

**V-2 — FOLLOW-UP (J1-1-R1). The D-1 class order is not pinned by any test.** REPRODUCED (N1, N2, N20 survive, section 8). N2
(token class before class 2) leaks `hunter2hunter2` on `token <32-run>KEY=hunter2hunter2`; N20 (privkey last) leaks a whole PEM body
on `secret: -----BEGIN RSA PRIVATE KEY----- …`, the scrubber's F8a case that `tests/test_transcript_export.py` pins and the decisions
tests do not. `tasks/briefs/laya/J1-1-R1-report.md` section 12.1 says class 2's place is pinned by
`test_token_assignment_forms_redacted` (`PC_BRIDGE_TOKEN=<run>` keeps envval); that input cannot tell the order apart, because class
2 has no guard and relabels the token placeholder to envval either way (evidence overstated; the code order is right). Not a
blocker: no leak in the unmutated code. Fix: add the three discriminators as tests.

**V-3 — FOLLOW-UP (J1-1-R1; extends issue #47's D-2 with a second mechanism).** REPRODUCED (section 9). A path field whose
root-relative form starts with `~` (`/r/~x.py`, an Office lock file `~$report.docx`, a `paths` item, an `action_target`) is accepted
once and refused on the second pass (`decision-state-abs-path`), so A3 ("idempotent on its own output") is false for it and
`make_row` refuses the row. The `decision_state` docstring (`src/agent_factory/decisions/volatile.py:355-362`) and the J1-1-R1
report's self-attack both name one exception (D-2). Mapped to A3, and technically "a stated claim false as stated"; but it fails
CLOSED (no byte written) and its fix sits in normalize's relativize step, which A1 keeps as is, which is D-2's disposition. Fix in
`_path` (`src/agent_factory/decisions/volatile.py:125-142`): refuse a `~`-leading relative result on the first pass too, and name
both exceptions in the docstring.

**V-4 — FOLLOW-UP (known: VERIFY-J1-1 Oracle A).** REPRODUCED (G4-G10: both golden tests stay green with any one redact pass or the
cut removed). The goldens bind the fixture states only. Fix: one golden per class carrying a FAKE secret and one over-limit field.

**V-5 — FOLLOW-UP (J1-1-R1). Contract forms no test pins.** REPRODUCED (N10, N11, N12, N14, N16, N18 survive; the discriminator
leaks in five of them, section 8): the sk floor 8, the bearer floor 16, bearer's case-insensitivity, SECRET in the widened names
(C-F3b lists it; no test has a bare `secret:`/`client_secret:` name), the widened value's `& , ;` stop set, digits in a PEM label.
The code is right today. Fix: one boundary test each.

**V-6 — FOLLOW-UP (both). Separators normalize keeps.** REPRODUCED (section 2 and section 6). Full-width `：`/`＝` survive NFC, and a
zero-width space is not `\s`; the value leaks in the decisions redactor, and the full-width colon leaks in the scrubber. Not
contract-mapped (the contract names ASCII `=`/`:`); AF-AP-149's family. Fix: an NFKC view for matching, or explicit mapping of
U+FF1A/U+FF1D and removal of U+200B-U+200D/U+FEFF before redact — a contract decision, since normalize is the stability mechanism.

**V-7 — INFO. Limits the contract's own shapes set.** REPRODUCED. `SK-`/`Sk-` (the sk class is case-sensitive), a widened value under
8 characters (`Password=QZJ8QZJ`), lower-case PEM labels, a secret split across two `paths` items (each item is redacted alone and
the list is re-sorted: `['QZJ8…', 'src/token:']`), and the lane's PIN-suffix strip shortening a widened value below the floor before
redact (`password: Qz8--deadbeef0` -> `password: Qz8`; the upper-case form is still redacted).

**V-8 — INFO. The widened value stops at `& , ; ' "` or a space.** REPRODUCED (section 3). A tail after such a character survives
(`password: abcdefgh;QZJ8…`), with or without the guard; the scrubber's value shape, adopted by C-F3b.

**V-9 — INFO. A3/A5 hold on every new shape.** REPRODUCED (section 4): 18 shapes x 16 keys x every cut, 0 leaks, 0 identity failures,
0 idempotence failures; 300,000 random states, 0 new non-idempotent; NFC truncation fuzz 0 of 20,000. D-2 stays known (issue #47).

**V-10 — INFO (disclosed in `tasks/briefs/laya/J1-1-R1-report.md` section 12.2).** REPRODUCED. The unguarded class 2 relabels:
`KEY=sk-…`, `PASSWORD=Bearer …` and a literal `KEY=<redacted:token>` end as envval. No byte leaks.

**V-11 — INFO (#187). The commit names one importer; there are three consumers.** REPRODUCED (pack + literal sweep).
`_scrub_messages` at `harness-ports/bin/qwen_matrix.py:126-137` also imports the scrubber by path, and `TRANSCRIPT_SYNC` at `scripts/push_clean.sh:117-118` runs the CLI on
every push. The fix reaches all of them; only the commit message's bug-echo line is incomplete.

**V-12 — FOLLOW-UP (#187). The compound class over-redacts real text.** REPRODUCED (section 6): 9 of 18 prose probes newly
redacted; a masked census finds 161 of 254,560 committed lines newly redacted, led by code identifiers (`owner_key` 40,
`private_key` 25, `ac_key` 21) and this module's own refusal texts (`unknown-key` 12, `missing-key` 7). Safe for secrets; it costs
transcript readability (the scrubber twin of O-1). Not contract-mapped (#187 bounds no false-positive rate). Fix: a design decision.

**V-13 — FOLLOW-UP (#187). Other spellings leak through both exporters.** REPRODUCED (section 6, 17 rows): backtick-quoted names,
YAML block scalars, `Authorization: Basic`, lower-case `bearer` (no `re.I` on `scripts/transcript_export.py:35`), `=>`, `:=`, XML
elements, `--password <v>`, URL userinfo, `secretkey`/`privatekey`/bare `key`, a Stripe-shaped `sk_live_…` under 40 characters,
`r"…"`, a full-width colon, a comma inside the value. Outside #187's contract; AF-AP-149's family. Fix: case-insensitive Bearer
and Basic first (the realistic headers), then YAML block values and CLI flags.

**V-14 — FOLLOW-UP (#187). Name forms and floors no test pins.** REPRODUCED (S4, S7, S8, S9, S10, S11, S13, S14 survive; each
discriminator leaks, section 8): the multi-space separator, the Bearer floor, the value floor from above (8 not 9), `apikey`,
`Authorization`, an empty compound prefix (`_key:`), `secret`, `passwd`. My 1,848-input differential shows the behavior holds
today; the committed tests would not notice it going. Fix: one planted line per PIN name form.

**V-15 — FOLLOW-UP (J1-1-R1). The alarm test has AF-AP-58's two windows.** REPRODUCED (section 10). An alarm in window (b) or (c)
ends the test in a bare `_Runaway`, not its `pytest.fail` text; always red, never a hang, nothing left armed. Fix: one `try` from the
arming statement through the disarm. INFO beside it: `setitimer(ITIMER_REAL, 0)` cancels any outer timer without restoring it, and
the ledger file's watchdog (`tests/test_decisions_ledger.py:836-850`, `signal.alarm(10)` with `SIG_DFL`) kills the whole pytest
process on a hang.

**V-16 — UNVERIFIED (J1-1-R1).** Under xdist (`scripts/pc_suite.sh` runs `-n 8` on the PC) `signal.signal` needs the worker's main
thread, or the alarm test errors with `ValueError`. Not run: xdist is absent from the sandbox venv and the PC is out of bounds.

**V-17 — INFO (known: VERIFY-J1-1 A-6).** STATIC + REPRODUCED by d9's rows: `incumbent_answer`, `producer` and `source_ref` are
written verbatim; only `state` passes through `decision_state`.

**V-18 — INFO (pre-existing).** REPRODUCED. A refusal text carries the raw value
(`decision-state-bad-enum: v1.finding_class.disposition=password=hunter2…`) and `make_row` passes it through unchanged; exception
text only, never the ledger. A harvest that logs refusals would copy raw text into its log.

**V-19 — INFO.** REPRODUCED (G3). The golden fixtures' `expected_digest` key equals the test constants but no test reads it; it can
drift silently.

**V-20 — INFO.** REPRODUCED (N6, N7, N15, N19 equivalent over a 60,000-call differential): `re.S` on `_PRIVKEY` is dead on the
`decision_state` path, `API_?KEY` is redundant with `KEY` in both env classes, and bound's `rstrip()` equals `strip()` there.

**V-21 — INFO (no finding).** REPRODUCED (section 5): every pattern linear; worst 64 KB input 0.0138 s.

**V-22 — INFO (no finding).** REPRODUCED (section 3): the guard cannot keep a secret byte (34-value keep-set; 0 of 40,000).

**V-23 — INFO (no finding).** REPRODUCED (section 9): no write or digest path goes around `decision_state`; the fixed-point gate
refuses every hand-built non-fixed-point state.

**V-24 — INFO (no finding).** REPRODUCED (G11, x10r): the order test's discriminator still discriminates after D-1.

**V-25 — INFO.** REPRODUCED (masked): the 120 committed transcript digests are fixed points of today's scrubber (0 lines).

**V-26 — INFO (confirms AF-AP-149's WATCH sites; extends the second).**
`scripts/t93r1_apply_profile.sh:58` knows `key_env|api_key|token|secret` only (no `password`), as filed.
`_STDERR_LEAK_RE` at `proofs/S0-01/check_acp_conformance.py:153`, measured with its own
compiled pattern: it detects `token=v`, `token:v`, `Bearer v` and a 64-hex run, and MISSES `token: v` (a space after the colon),
`"token": "v"`, `AGENT_TOKEN = v`, `password=v`, `api_key: v` and `sk-…`. It is an attested input of an accepted proof, so a change
means a re-mint.

## 13. GATE RECOMMENDATIONS (the coordinator owns the gate)

**J1-1-R1 (f0e431f, local 5718ea0): `NOT-READY` — blocker V-1.** It meets all five predicate conditions, reproduced through
`decision_state` -> `make_row` -> `append` -> the JSONL on disk. This rests on one contract reading I cannot settle from primary
text: the D-1 ruling names classes 1-4 only (the J1-1-R1 report, section 12: "sk and bearer, which the ruling does not name, keep
their PIN place"), so sk's place ahead of them is the builder's choice, and option A (section 11: move the sk pass after the widened
pass) is an in-boundary fix that changes no class form. If the coordinator holds the order recorded at landing
(`in the D-1 order` at `todo/BUILD-TASKLIST.md:241`: privkey → sk → bearer → …) as frozen, read this line as `CONTRACT-INVALID` on A4's "with a prefix"
promise for secret names that the `sk-` or `bearer` class eats first, and take option B (C-F2's `\bsk-` plus a bearer guard) as the smallest measured
amendment. Everything else in J1-1-R1 held under attack: A1-A5 on every new shape, the guard, linear cost, every write path through
`decision_state`, the order test's discriminator. Follow-ups: V-2, V-3, V-4, V-5, V-6, V-15; V-16 unverified.

**#187 (32df68f, local a318b8a): `MERGE-READY-WITH-FOLLOWUPS`.** No blocker. Every shape the #187 contract names is taken (21 of 21)
through the real CLI and the Hermes exporter, byte-identical; 0 regressions and 0 changed outputs over 1,848 PIN-form inputs; linear
(worst 0.0138 s at 64 KB); the private-key rule's first place, the lookbehind, the case-insensitivity, the quote before the value and
the scrub-then-cap order are each pinned by a killed mutant (S5, S3, S1, S2, S12). Follow-ups: V-12, V-13, V-14; INFO V-11, V-25, V-26.

## 14. DISCREPANCIES

- The premise's anchors are the pre-push local SHAs: 5718ea0 is origin f0e431f and a318b8a is origin 32df68f, with identical trees
  (section 0). Explained by push_clean's rewrite; not a premise mismatch.
- HEAD moved during the lane (688b4bd, 1e4c40a, 9b3bbdb, d556c9b: transcripts, an S0-02 brief, a ledger plane); the nine boundary
  files stayed byte-identical to the PIN.
- `tasks/briefs/laya/J1-1-R1-report.md` section 12.1 cites `test_token_assignment_forms_redacted` as the pin for class 2's place in
  the order; mutant N2 (token class first) survives that test (V-2).
- The docstring's `J1-1-R1 report D-2` exception (`src/agent_factory/decisions/volatile.py:360-362`) and the J1-1-R1 report's self-attack name ONE
  A3 exception (D-2); V-3 is a second.
- The message of a318b8a says the fix reaches `harness-ports/bin/hermes-session-export.py`; it also reaches
  `harness-ports/bin/qwen_matrix.py`, and `scripts/push_clean.sh` runs the CLI (V-11).
- Mutant counts: the ledger line (`todo/BUILD-TASKLIST.md:241`) quotes d1a "4 failed, 68 passed" and d1b "10 failed, 62 passed"
  (72 tests), the builder's report "4 failed, 69 passed" and "10 failed, 63 passed" (73: the builder's copy adds an import check).
  Same kills; different denominators.
- The brief's mutant examples include three of the builder's own (x6 = drop `(?<=_)`, x10 = `\s*`, x12 = the guard's prefix half):
  re-run as a check (all KILLED), not counted as new.
- My own harness defect, disclosed in section 8: the first S1-S3 run could not credit its kills (node ids with spaces); fixed and
  re-run.

## 15. NOT-done (first-class)

- No PC or bridge use (the brief forbids it): V-16 (the alarm test under xdist's `-n 8`) is UNVERIFIED.
- No full-tree suite. Run here: the boundary's three suites (`72 passed`, `23 passed`, `15 checks passed`, section 0), the 45 new
  mutants and 3 re-runs, and the drivers named per section.
- The builder's 23 mutants and the coordinator's five (M1-M5) were not re-run, except x6, x10 and x12 as a spot check.
- Options A and B (section 11) were measured on scratch copies with the unchanged tests and my drivers only; no test was written
  (the boundary is read-only for this lane).
- The masked corpus scans print counts and names, never values; I did not inspect any matched value in committed text.
- Python 3.11.15 only: the regex engine's signal checks (section 1) were not measured on another interpreter.
- No `/bug-echo` beyond the two in-scope redactors and the two AF-AP-149 WATCH sites (V-26).
- Scratch `/tmp/vj11r1/` is removed at the end of the lane; each driver is described above in enough detail to rebuild it.

## 16. Report lint (two fix rounds of the three allowed)

```
$ python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/VERIFY-J1-1-R1-report.md --root .
round 1: report_lint: 40 refs — OK 13, NEAR 1, MISS 17, UNCHECKABLE 9, UNRESOLVED 0 (worktree)   (FLOOR: OK 13 < 15)
round 2: report_lint: 41 refs — OK 38, NEAR 0, MISS 3, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
round 3: report_lint: 41 refs — OK 41, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
```
