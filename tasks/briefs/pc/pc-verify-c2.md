# VERIFY-C2 — the targeted independent adversarial verify of the lane done-gate (task #148)

PIN: e8db82c
ROLE: adversarial-verifier (read-only against production; every mutation on a scratch copy under `../scratch/`)
REPORT: write `tasks/briefs/canny/VERIFY-C2-report.md` (untracked is fine) and paste its summary as your final answer.

## What landed, and the contract

C2 (commit "C2: the lane done-gate …", GATED-PENDING-VERIFY, shipped switched OFF): `harness-ports/bin/lane-done-gate.py`
(`record`, a Hermes `post_tool_call` observer of edit facts and check facts; `gate`, a `pre_verify` directive that nudges when
a code file changed after the last passing check) + `harness-ports/tests/test_lane_done_gate.py`; the create-time switch
`LANE_DONE_GATE` in `harness-ports/bin/lane-profile.sh` (+ `harness-ports/tests/test_lane_profile.sh`); `run-all.sh` lists
the new suite. The frozen contract is the build brief `tasks/briefs/pc/pc-c2.md` (its items 2-5 and its measured premise:
the Hermes b3399c1 hook payload shapes and the 109-command corpus); the lane's report is `tasks/briefs/canny/C2-report.md`.
Attack the contract, never only the builder's cases.

## Items (report EVERY observation; no severity filter; SOLID/UNSURE per observation)

1. PREMISE. Re-measure the block below (blob ids, line counts, the two test counts, the seam lines). A mismatch is
   CONTRACT-INVALID: stop and report it.
2. THE CLOSED CHECK SET, GRADED BY EXECUTION (the brief's item 2, AF-AP-133). For every command shape `counts_as_check`
   accepts, and for at least ten you write that it must refuse (a check piped into `true`, `|| true`, `; true`, a check in a
   subshell whose rc is discarded, `echo pytest`, a commented-out check, a check under `timeout` that times out, a check
   followed by `exit 0`), execute the shape through bash against a FAILING stub and a PASSING stub and show the recorded
   fact matches the real exit code. A shape recorded as a passing check while its test failed is a blocker.
3. THE RECORDER (`record`). Feed the hook the payload shapes from the brief's premise (terminal result envelopes with and
   without `exit_code`, a timeout's 124, `write_file`, `patch` in the V4A multi-file form, a malformed payload, an unknown
   tool). Show which facts are written, where, and that a malformed payload never crashes the Hermes turn (the hook's exit
   code and stdout). Name the line that decides each case.
4. THE GATE (`gate`). Sequences: edit then passing check (no nudge); passing check then edit (one nudge); edit, failing check
   (nudge); repeated `pre_verify` calls (bounded, never an endless loop; the brief names the bound); an empty ledger; a
   ledger file that is corrupt or not a regular file. Paste the directive output for each.
5. THE SWITCH. `LANE_DONE_GATE` unset, `0`, `1`, and a junk value: the generated `config.yaml` bytes (OFF must equal today's
   output byte for byte; ON must add exactly the two entries). `verify` on each form.
6. MUTANTS (scratch copies only). The lane's mutation table (its report) on the PIN's bytes, plus at least five of your
   own: the gate ignores order; a failing check recorded as passing; the switch always ON; the recorder swallowing an edit
   path in a V4A patch; the nudge bound removed. Paste each diff line, the count and the killing test. A survivor is a
   finding: name the missing test.
7. GATES (each call under the 420 s cap): `python3 harness-ports/tests/test_lane_done_gate.py` twice, `bash
   harness-ports/tests/test_lane_profile.sh` twice, `python -m pytest -q tests/test_verify_command.py` once (C1 untouched),
   `bash harness-ports/tests/run-all.sh` once (one known red suite predates C2: `test_qwen_matrix_sh.sh`, the SECOND_SIGINT
   cell; show it on a clean `git archive e8db82c` copy before calling it pre-existing).
8. REPORT AND GATE RECOMMENDATION. Every finding with file:line, the reproduction command and SOLID/UNSURE. End with
   `GATE RECOMMENDATION: MERGE-READY | MERGE-READY-WITH-FOLLOWUPS | NOT-READY | CONTRACT-INVALID` and the blocking
   predicate applied to each blocker.

Out of scope: the live check with the switch ON in a real lane (the coordinator's, after the dispatcher forwards the switch).

## Standing do-nots

- Never edit the C2 files, `scripts/verify_command.py` or `harness-ports/bin/pc-lane.sh` in your tree; every mutation
  lives under `../scratch/`. Never run `hermes`, and never read `~/.hermes/`: the payload shapes are in the build brief's
  premise, take them as given.
- Never touch any `.lanes/` directory other than your own; never kill a process you did not start.
- No outward-facing actions (no PRs, issues, comments, pushes). Do not spawn subagents.
- Bound the report lint: apply its `fix:` hints for at most three rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 21:1xZ, /home/user/agent-factory@e8db82c; the blobs equal the working-tree hashes below)

```
$ for f in (the C2 files): git hash-object <f> | cut -c1-12; wc -l
4186102615f0 314 harness-ports/bin/lane-done-gate.py
58b72468fade 404 harness-ports/tests/test_lane_done_gate.py
f32198144d05 298 harness-ports/bin/lane-profile.sh
dd60fbd707fd 241 harness-ports/tests/test_lane_profile.sh
5af4f54f2e07 78 harness-ports/tests/run-all.sh
$ python3 harness-ports/tests/test_lane_done_gate.py | tail -1
lane done gate: 19 passed, 0 failed
$ bash harness-ports/tests/test_lane_profile.sh | tail -1
lane profile: 13 passed, 0 failed
$ grep -n -E '^def |^CHECKS|^[A-Z_]+ = |is_verify|max_verify_nudges|sys.exit|except' harness-ports/bin/lane-done-gate.py | head -40
20:ROOT = Path(__file__).resolve().parents[2]
21:VERIFY_COMMAND = ROOT / "scripts" / "verify_command.py"
22:CODE_SUFFIXES = {
26:PROJECT_PATTERNS = [
32:PATCH_PATH = re.compile(
36:RC_WRAPPER = re.compile(
46:def _warn(message: str) -> None:
50:def _repo_root(_cwd: Any) -> Path:
54:def ledger_file(root: Path, session_id: Any) -> Path:
61:def _classifier():
70:def _is_direct_check(command: str, module: Any, patterns: list[str]) -> bool:
79:            return module.is_verify(stripped, patterns)
81:        return module.is_verify(stripped, patterns)
85:def counts_as_check(command: str) -> tuple[bool, str]:
96:    except Exception as exc:
100:def _append(path: Path, fact: dict[str, Any]) -> None:
110:def _result_exit_code(extra: Any) -> tuple[int | None, str]:
118:    except Exception as exc:
128:def _edit_paths(tool: str, tool_input: Any) -> list[str]:
145:def record(payload: dict[str, Any]) -> None:
182:def _facts(path: Path) -> list[dict[str, Any]]:
189:        except Exception:
197:def _relative(path: str, root: Path) -> str:
202:        except ValueError:
207:def _is_code(path: str, root: Path) -> bool:
225:    except OSError:
229:def gate(payload: dict[str, Any]) -> None:
295:def main() -> int:
308:    except Exception as exc:
$ grep -n 'LANE_DONE_GATE' harness-ports/bin/lane-profile.sh scripts/pc_lane.sh harness-ports/bin/pc-lane.sh
harness-ports/bin/lane-profile.sh:116:  python3 - "$target/config.yaml" "$lane" "${LANE_DONE_GATE:-0}" "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
$ git rev-parse --short=12 e8db82c:harness-ports/bin/lane-done-gate.py e8db82c:harness-ports/bin/lane-profile.sh (one per call)
4186102615f0
f32198144d05
```
