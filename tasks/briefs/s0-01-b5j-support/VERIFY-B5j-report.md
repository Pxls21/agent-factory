# VERIFY-B5j — adversarial grade of lane B5j at PIN `01499e7`

## Verdict

**NOT-READY.** This PC lane is not an independent acceptance authority, and the candidate has three blocking, reproduced test-oracle gaps: a false three-line shutdown claim bypasses the two-line prose pin; unbounded tee-pipe reads bypass the walker through process/attribute indirection and trusted-helper naming; and a world-process enumeration using `ps aux` bypasses the census. The cheapest path is to harden those three static guards and commit their exact survivors as negative controls, then send the result to the sandbox adversarial-verifier lane.

This report is an adversarial handoff, not a promotion or gate verdict. Reproduced means I ran the stated command or scratch mutation on this PC. Static means I inspected the PIN bytes. I did not run a sandbox lane, alter the owner’s services, or execute a guard-disabling mutant against a real protected resource.

### PIN finding locations

- `kill_sig` and `kill_helper` are the derived direct-check names at `test:3767-3769`.
- `wait_subject` and `wait_method` are asserted at `test:3773-3775`.
- `src_lines` forms the false-prose windows at `test:3909-3912`; `secs_re` is the numeric pattern at `test:3902`.
- `def _is_pipe` is the direct-receiver predicate at `test:3133-3137`; `aliases` are built at `test:3141-3145`; `BOUNDED` is the named-helper exemption at `test:3157-3159`.
- `_kill_own_grandchild` is asserted to be `gone` at `test:2875-2879`; live branches are at `test:650-653` and `test:1284-1287`.
- `_reread_interpreter` catches `OSError` at `tee:96-109`; the impossible-PID test is at `test:3590-3602`.
- `SIGTERM` is the AST argument at `test:3001-3007`; `ast.Try` follows at `test:3008-3012`.
- `outcomes` supplies the winning aggregate at `test:3583-3588`; `os.access` proves FIFO execute mode at `test:892-896`.
- `AP_SCREEN` supplies the AF-AP-59 registry scan at `test:3040-3044`; `os.kill` is constrained at `test:3078-3089`.

## Item 0 — mechanical gates and file identity

Reproduced from a scratch copy of `git archive 01499e7` with `S0_01_VENUE=pc`, `S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`, and an explicit pytest basetemp:

- Full tee suite: **116 passed in 180.39s**, exit 0.
- Builder-report lint against `--rev 01499e7`: **28 refs — OK 28, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0**. I therefore disagree with the coordinator’s earlier `OK 24, NEAR 2, MISS 2` observation: on the archived PIN the cited lines exist and the named tokens are present.
- The anti-pattern screen found tee hits AP-24×4, AP-1×3, AF-AP-55×2, AP-51×2, AF-AP-58×1, AP-32×1; the test screen found AP-66×1. Pyflakes exited 0.
- The two scoped archive files match the reported final hashes: the tee is `990a2ad24475fde35291cd940e5f02d5e8dcf8f413cb16e4948f46407362cdb0` (567 lines) and the test file is `bbdd7cdbee35593e36244ace3942fbd4f310a3ca8ceccf49f5fb2cd6982f594a` (3950 lines).

The vendored primary source is `proofs/S0-01/vendor/buzz-acp/acp.rs`, sha256 `44e82861763694d2b82d02b15ee100ffd6c78874a2b2282865e6656c539c38f1`. Its shutdown range precedes the bounded child wait with group SIGKILL in the pinned source.

## Items 1–2 — source-derived clause and structural prose rule

The source-derived clause control is real for the direct mirror class. On scratch copies, swapping the sentence halves with the constant/docstring synchronized died because the kill half no longer named the derived signal/helper; changing the wait subject from child to socket died because it no longer matched the source wait call. Changing the vendored wait from 5 to 6 seconds died first at the pinned-oracle hash assertion.

The exact third independent buzz-acp docstring sentence died. Alternate buzz client spellings and “the client” prose placed in the module docstring with the literal `5 s` each died at the residue test; the docstring rule is stronger than its name-matching comment suggests for that spelling.

### VBJ-F1 [BLOCKING, SOLID] — three-line false shutdown prose survives

**PIN mechanism:** the prose oracle scans physical source lines only in adjacent pairs and recognizes only a literal numeric duration format.

**Failing input:** insert the following module comment outside the masked clause:

```text
# buzz_acp gives a wedged leg SIGKILL
# only after a grace period has lasted
# 5 s, so late output remains valid.
```

**Expected:** reject. It makes the inverse reader-facing claim about the primary source: kill follows a five-second grace, rather than precedes the bounded child wait.

**Observed:** the focused source-oracle test passed (`1 passed in 0.37s`). No two physical lines carry both `SIGKILL` and `5 s`; g1 also does not inspect comments and its client spelling is `buzz-acp`. Equivalent comments using `five seconds` or `5s` also passed. A single-line misleading string literal was caught by the proximity assertion, so this is a bounded-window/token-domain escape, not a wholly absent rule.

**Minimal fix:** tokenize prose-bearing comments/docstrings/strings into bounded sentences or clauses rather than physical two-line windows, normalize client-name and duration spelling, and require the derived-order clause rather than a token co-occurrence ban. Add the exact three-line comment, a `five seconds` spelling, and a `5s` spelling as committed negative controls.

## Items 3–5 — pipe, zombie, and identity controls

Direct pipe forms are caught: unbounded iterator, comprehension, nested direct pipe alias, `readlines`, and raw `os.read` mutations failed under the walker. The standalone hang probe stayed outside pytest as required: after 3 seconds with client stdin held open, it recorded `reader_alive=True`, `tee_poll=None`, tee `wchan=hrtimer_nanosleep`, reader `wchan=anon_pipe_read`; closing only the probe’s stdin released both processes with rc 0.

### VBJ-F2 [BLOCKING, SOLID] — “every pipe mention” has live unbounded-read escapes

**PIN mechanism:** the walker recognizes direct `tee_proc.stdout`/stderr receivers, tracks aliases assigned directly from that pipe, and skips all mentions in a function named `_drain` or `_read_with_deadline`.

**Failing inputs and observed focused runs:**

1. `p = tee_proc; line = p.stdout.readline()` passed (`1 passed in 0.65s`). The process alias is intentionally outside the matcher’s receiver identity.
2. `getattr(tee_proc, "stdout").readline()`, `tee_proc.__dict__["stdout"].readline()`, and `lambda q=tee_proc: q.stdout.readline()` each passed (`1 passed` each). These are the same unbounded-read class under attribute indirection.
3. A local `_drain(pipe)` whose body is `return pipe.readline()`, called as `_drain(tee_proc.stdout)`, passed (`1 passed in 0.84s`). The helper name is trusted without inspecting its body, deadline, thread ownership, or join.
4. Padding the file with 55 harmless direct mentions plus the process-alias read also passed. The mention-count floor prevents an empty walk, but does not prove classification coverage.

**Expected:** reject every unbounded tee-pipe consumer, including aliases and a helper that merely adopts a trusted name.

**Minimal fix:** resolve local aliases of `tee_proc` as well as pipe aliases; inspect helper bodies/arguments structurally for a deadline and cleanup contract, or remove the helper-name exemption; treat dynamic `getattr`/`__dict__` pipe access as forbidden in this test file. Commit the four survivors above as negative controls.

**Zombie branch:** the meaningful live branch is covered when the fixture itself remains live. Replacing the zombie fixture’s 0.3-second sleeper with a 30-second sleeper died (`assert 'live' == 'gone'`, 2.36s). The two live sites likewise reject the opposite expected branch. The high-volume status fixture remains a by-construction gone case: no live-branch reachability claim should be made from it.

**Identity/OSError:** the module helper catches `(OSError, IOError)` around both readlink and hashing. I invoked both arms directly: simulated readlink EACCES and post-readlink hash ENOENT returned `None` and emitted the specified re-sample marker. A copied interpreter unlinked after launch produced a deleted executable link and also returned `None` with the marker. Read-only `/proc/1/exe` as the lane user returned EACCES. The deterministic impossible-pid control also passes. No OSError path reproduced here escaped.

## Item 6 — SIGTERM identity

The AST pin rejects imported, literal, and local-alias SIGTERM forms because it requires an attribute named `SIGTERM`; each scratch mutation died. Adding an extra SIGINT registration immediately before the required `try` also died. An additional SIGINT installation after the `try` begins is outside this focused structural contract; it is a documented scope limit, not a claim that no other signals can ever be installed.

## Item 7 — race aggregate and FIFO domain

The always-failing re-sample mutation died: all 20 trials lost. The real aggregate passed idle in 2.53 seconds and under six PID-scoped busy loops in 8.40 seconds. Both runs had at least one winning sample, as required. This demonstrates discrimination on this host, not a universal flake bound.

The committed FIFO and directory tests passed (`2 passed in 0.27s`). An executable FIFO fixture is actually executable; changing it to mode 0644 killed the fixture assertion, proving the test reaches the `isfile` half of the production guard. A symlink to an executable FIFO, an executable FIFO itself, and a directory were also run directly: each returned rc 64 and the exact non-executable-agent diagnostic.

## Items 8–9 — discrepancy reconstructions and D4

I agree with the corrected controls that do discriminate: third independent exact docstring sentence, live-fixture zombie branch, removal of all timeline collectors, and the `pkill -f`/`pgrep -a -f`/list-form `ps -ef` AF-AP-59 constructions all failed their focused pins. The earlier draft’s claim that the live assertion flip at site 1 survived was not reproducible: live to gone at the first live assertion failed. The corrected live-fixture mutation above is the appropriate branch-reachability proof.

D4 is mechanically consistent. Production has four raw `PINNED_SHUTDOWN_CLAUSE` token occurrences: one module-docstring reference, the definition, and two reference-only drain-loop comments. The only full sentence occurs exactly in the module docstring and split constant. The five named reference-only sites used by the oracle are those two comments plus the three test docstrings.

### VBJ-F3 [BLOCKING, SOLID] — world-process census misses `ps aux`

**PIN mechanism:** AF-AP-59 screening delegates to a registry regex; the complementary AST pin only sees attribute-form `os.kill`/`os.killpg`.

**Failing input:** a dormant `CENSUS_MUTANT = "ps aux"` source string inserted in the test file.

**Expected:** reject any world-scoped process census, as the test name and its docstring promise.

**Observed:** the focused census test passed (`1 passed in 0.65s`). In contrast, list-form `["ps", "-ef"]`, `pkill -f`, and `pgrep -a -f` were caught. `ps aux` is a real, common whole-host enumeration spelling outside the registry’s regex domain.

**Minimal fix:** make the negative control parse subprocess invocations and shell command literals into an allowlist of own-PID operations, or expand the registry with tested normalized `ps` argument coverage. Add `ps aux` as a committed negative control.

Two additional static limits are documented but remain live: `from os import kill as k` and `subprocess.run(["kill", ...])` bypass the kill-call AST pin. I did not invoke either action; dormant lambda/source mutations passed the static test. These are non-blocking only because the current pin explicitly scopes itself to `os.kill`/`os.killpg`, but they must be closed if the claim is widened to “no process killing.”

## Item 10 — scratch mutation ledger

I executed 43 scratch mutation attempts after resumption, all from independent copies with explicit basetemps. Three are excluded as invalid evidence: one stale class-qualified pytest target collected zero tests (rc 4), one mutation changed a different fixture than its focused target, and one mutator made no source change. The remaining **40 real mutations produced 23 killed and 17 survived**. This meets the brief’s 40-mutant floor.

| group | killed | survived | result |
|---|---:|---:|---|
| Direct pipe / alias / signal AST | 7 | 4 | Direct iterator/comprehension/nested alias and signal syntax controls die; receiver indirection remains VBJ-F2. |
| Zombie, census, collector | 5 | 1 | Live fixture, branch, two census spells, and collection removal die; a dormant `ps -ef` string survives. |
| Source/prose attacks | 8 | 3 | Pinned source hash, literal string, and six docstring forms die; multiline/alternate-duration prose is VBJ-F1. |
| Census and kill spelling attacks | 1 | 4 | `ps aux` is VBJ-F3; import/subprocess kill spellings are documented scope limits. |
| Pipe receiver/helper attacks | 1 | 4 | The helper-argument shape is rejected; dynamic/process aliases and trusted helper name are VBJ-F2. |
| FIFO mutation controls | 1 | 1 | The executable FIFO fixture is real; removing its fixture assertion is a by-construction test weakening. |

**Exact mutation ledger.** Killed: `PIPE_NESTED_ALIAS`, `PIPE_COMPREHENSION`, `PIPE_ITERATION` at the walker’s `bad` assertion; `SIG_FROM_IMPORT`, `SIG_LITERAL`, `SIG_ALIAS` at the required SIGTERM attribute assertion; `SIGINT_ADDITIONAL` at the immediate-try assertion; `ZOMBIE_S1_FLIP` and `LIVE_FIXTURE_SLEEP` on the returned branch; `CENSUS_PKILL`, `CENSUS_PGREP`, and `CENSUS_PS_EF_LIST` at AF-AP-59; `R19_COLLECTOR` at the first artifact-presence assertion; `ORACLE_WAIT_6` at the pinned source hash; `PROX_STRING` at the proximity assertion; all six module-docstring spellings at the residue assertion; `HELPER_ARGUMENT` at the pipe walker; and `FIFO_MODE` at the executable-FIFO fixture assertion.

Survived: `PIPE_GETATTR`, `PIPE_DICT`, `PIPE_PROCESS_ALIAS`, `PIPE_BOUNDED_NAME`; `CENSUS_PS`; `PROX_3LINE`, `PROX_SPELLED`, `PROX_5S`; `CENSUS_PS_AUX`, `KILL_FROM_IMPORT`, `KILL_SUBPROCESS`, `FLOOR_PAD_PROCESS_ALIAS`; `GETATTR_READ`, `DICT_READ`, `LAMBDA_ALIAS`, `TRUSTED_DRAIN`; and `FIFO_NO_ASSERT`. The substantive survivors are classified in VBJ-F1 through VBJ-F3; the import/subprocess kill and fixture-assertion survivors are explicitly scoped or by construction. No survivor was relabelled as a success.

## Item 11 — 18-class re-scan

Static AST/literal re-scan of the two PIN files found no new relevant name/literal conditional accepting branch without a fail-loud other arm. The simple comparisons are solely local count/state/module-dispatch values and the test registry selector. None accepts an external domain value; the `ps aux` coverage gap is a registry-domain issue rather than a fail-open production conditional.

The remaining 18-class surfaces were exercised by the full 116-test suite and focused hostile controls: NaN/Infinity handling, read receivers, raw pipe reads, waits, environment domains, broad OSErrors, /proc identity, signal install, shutdown mirrors, collector artifacts, process census, and FIFO/file domain. Reproduced defects from this scan are VBJ-F1 through VBJ-F3; no additional production fail-open was found.

## Item 12 — discipline and evidence audit

All product changes were inspected on the PIN and all mutations used scratch copies; the working tree’s pre-existing staged brief/transcript were not modified. PID-scoped cleanup was used for the hang probe and six load loops. No `pkill`, broad `pgrep`, service action, credential read, commit, or push occurred.

The builder report’s source claim was re-derived from the committed vendored source, rather than accepted from its prose. The file-identities, builder-report lint, AP screen, pyflakes, full suite, focused suite counts, standalone wchan evidence, and OSError cases above are reproduced. The only deliberately skipped execution was an actual imported/subprocess kill mutant, because triggering a guard-disabling process-kill form is unsafe; it was assessed as a dormant static mutation only.

## Item 13 — design and cheapest repair

The two-line whole-file ban is not the right final shape. It both permits a plainly misleading three-line statement and constrains harmless explanatory prose based on line wrapping rather than semantic content. A prose-span/sentence parser with normalized spelling and a single source-derived allowed clause would be narrower where it matters and less hostile to maintainers.

The mention-count floor is only a presence floor. It proves the AST walk saw enough syntactic mentions for today’s file, but cannot prove aliases, dynamic attributes, or helper bodies received the right classification. It should remain as a regression sentinel only after identity/alias tracking and helper-body validation are added.

The next round should: (1) close VBJ-F1 with committed multiline/duration-spelling negative controls; (2) close VBJ-F2 with process-alias/dynamic receiver/helper-body controls; (3) close VBJ-F3 with normalized whole-process enumeration detection; (4) rerun the full tee suite and the independent sandbox adversarial lane. Coordinator-owned items remain VB-F12 corpus re-capture, VB-F13 PC stat, and VB-F14.
