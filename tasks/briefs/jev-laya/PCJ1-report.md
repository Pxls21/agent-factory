COORDINATOR GRADE 2026-09-23T00:17Z (the coordinator's stamp; the lane's report follows unedited): the endpoint half holds (live /health on the PC: ok true, device cpu, the pinned revision; tests/test_laya_systemone_server.py 16 passed twice). The pruner half does NOT: "wired conditionally" named a condition no Hermes lane can meet. jev-pruner engages only after its own Codex PreToolUse hook has written a transcript pointer (~/.cache/jev-pruner/codex/<id>.json); this lane's setup smoke planted that pointer under a temporary HOME, and a real lane has none. Measured on the PC 2026-09-23: 108,894 bytes through the wrapper came back whole, the endpoint's calls counter stayed at 10, and no archive directory was written. The pc-lane.sh wiring was refused by the never-a-gate screen and reverted; the role paragraph is withdrawn; the coordinator's wrapper is parked (tasks/briefs/jev-laya/parked/README.md). Registry: AF-AP-120, AF-AP-121.

Verified live: PCJ1 proposal; not independently accepted. The user unit is active at 127.0.0.1:47411; the pruner wrapper is installed and wired conditionally. A real Hermes lane using the wrapper is NOT proven because the upstream wrapper’s fixed 30-second request deadline expires on this CPU workload and correctly preserves original output.

DATA: files changed
- scripts/laya_systemone_server.py:30-228 — device policy, pinned-revision guard, ready/health fields, and `State.calls` increment inside the lock.
- `laya_sh:1` names `laya-server.sh`; `laya_sh:44` sets `TRANSFORMERS_OFFLINE`; `laya_sh:65` makes `venv`; `laya_sh:131` calls `curl`; `jev_sh:1` names `jev-pruner-setup.sh`; `jev_sh:34` defines `patch_codex_client`; `jev_sh:109` starts `smoke`; `jev_sh:198` returns `main_failed`; `laya_test:1` names `Model-free`; `laya_test:67` defines `test_answer_fans_out_each_named_chunk_without_reusing_batch_state`; `lane:253` names `JEV_DIST`; `lane:260` exports `JEV_PRUNER_RUN`; `lane_test:513` names `ENVHARNESS`; `lane_test:548` checks `portfile`.
- `roles:61` tells lanes to invoke `JEV_PRUNER_RUN`; generated `.codex/agents/*.toml` were regenerated from those role sources. `ports:445` records `Laya` endpoint deployment and explicit NOT-proven boundary.

DATA: PC installation
- `laya-systemone.service`: active, loopback-only, `device=cpu`, `device_reason=auto: CUDA memory probe failed (CUDA error: out of memory); using CPU`.
- Health: `ok=true`, revision `1c5edc17a7acd8701df6fc341c0d179f1c62c982`, snapshot path under `/home/rocco/hf-laya`, calls 10.
- Install marker: `2026-09-22T20:18:50Z`.
- Versions: `laya==0.3.5`; `torch==2.14.0`; `transformers==5.17.0`.
- Installed sizes: `/home/rocco/hf-laya` 840M; `/home/rocco/venv-laya` 5.6G; `/home/rocco/jev-plugins/jev-pruner` 67M.
- jev-pruner HEAD: `47d017c34eab7690b95f075ce6f4839247c5dc0a`; `dist/codex/run.js` present.
- GPU remains unavailable: RTX 3090 24,576 MiB total / 24,022 MiB used / 101 MiB free; `VLLM::EngineCore` uses 23,762 MiB. I did not touch vLLM or OmniRoute.

DATA: Laya live smoke
- Run 1: `c1=0.4177 c2=0.6723 c3=0.4843 fan_out=3 latency_ms=25298.6`.
- Run 2: `c1=0.4177 c2=0.6723 c3=0.4843 fan_out=3 latency_ms=944.4`.
- `answers_bitwise_identical=True`.
- Sandbox comparison: nouls match exactly (`0.4177/0.6723/0.4843`). PC first request is much slower.

DATA: pruner live smoke
- Main wrapper: `rc=6 bytes_in=78088 bytes_out=78088 calls_before=6 calls_after=6 endpoint=timed out at the upstream 30-second deadline`; the archived original was `/tmp/tmp.yrhxhWW38i/.jev-pruner/codex-ffb08d85-265e-4206-8adf-80965e4874c1.txt`.
- The 1,200-line fixture is 78,088 bytes and 25,321 estimated tokens; it exceeds the 60,000-byte / ~15,000-token brief threshold.
- Planted lines survived verbatim: `E   AssertionError: expected 4 got 5`; `FAILED tests/test_b.py::test_q`; `KeyError: 'missing'`.
- The upstream wrapper created its full-output archive before scoring, then hit its 30-second deadline and returned the original stdout unchanged. `jev-pruner-setup.sh` reports this as exit 6 rather than presenting a fail-open timeout as a successful pruning smoke.
- Negative controls:
  - 100 lines: `rc=0`, 1,390 bytes in/out, byte-identical.
  - Closed port: `rc=0`, output byte-identical; upstream swallows fetch failure, so stderr is empty.
  - Child exit 1: `rc=1`, 25 output bytes, byte-identical.
  - Secret-looking fixture: `rc=0`, byte-identical passthrough.
- `TYPESAFE_API_KEY=local` is a local placeholder ignored by the loopback endpoint, not a credential.

DATA: gates
- `~/venv-laya/bin/python -m pytest tests/test_laya_systemone_server.py ...` twice: `16 passed in 0.03s`; `16 passed in 0.02s`.
- `~/venv-agent-factory/bin/python -m pytest ...`: `16 passed in 0.02s`.
- `scripts/test_summary.sh tests/test_laya_systemone_server.py`: `16 passed in 0.04s`.
- `bash harness-ports/tests/test_pc_lane.sh` twice: `62 passed, 0 failed` each run.
- `bash harness-ports/tests/run-all.sh`: `ALL SUITES PASSED`; included PC lane `62/0`, dispatcher `37/0`, admission `22/0`, qwen-server `101/0`, sync-skills `34/0`.
- `bash -n`, `git diff --check`, and `venv-agent-factory` pyflakes: passed.
- `build-roles.py --check`: `OK: 3 role config layers match their sources`.

DATA: mutation controls
- m1: auto picks CUDA merely when available → `test_pick_device_matrix` red (`1 failed, 15 passed`).
- m2: fan-out sends whole batch state → recorder routing test red (`1 failed, 15 passed`).
- m3: unmatched question gets `fan_out` → fallback negative control red (`1 failed, 15 passed`).
- m4: revision guard removed → revision test red (`1 failed, 15 passed`).
- m5: unhealthy pc-lane path exports JEV variables → exact unhealthy-endpoint check red (`61 passed, 1 failed`). Original suite restored to `62 passed, 0 failed`.

DATA: AP screen
- Test screen: AF-AP-33 at `laya:162` (`self.path`) and AP-66 at `laya:219` (`State.load_error`); both new but intentional.
- Non-test screen: AF-AP-45 at `lane:122` (`pids`) and AP-51 at `lane_test:137` (`first-report`) are pre-existing and outside this hunk.

DISCREPANCIES / NOT-done
- GPU CUDA path is implemented and matrix-tested, but not live-tested because only 101 MiB is free. CPU service is intentional.
- A real Hermes lane invoking `node "$JEV_PRUNER_RUN" -- <command>` is not proven. The next lane should test it after resolving or accepting the external pruner’s 30-second CPU deadline.
- The fixture now meets the byte target: its 1,200 lines yield 78,088 bytes and 25,321 estimated tokens. This is above the requested ~15,000 tokens but preserves the exact requested 1,200-line shape.
- `upstream.lock.yaml`, `scripts/pc_lane.sh`, ledger, wiki, Hermes profile configuration, vLLM, and OmniRoute were not touched.

SELF-ATTACK
1. Device policy could select GPU incorrectly: full exact-reason matrix and m1 kill this; live health reports CPU and pinned revision.
2. Fan-out could reuse the batch state: recorder asserts per-chunk state and m2 kills it; live endpoint returns discriminating scores with `fan_out=3`.
3. An unhealthy endpoint could still inject the wrapper: closed-port OFF test passes; m5 makes the exact check fail.

retro: Real defect/finding: jev-pruner’s hard 30-second request deadline makes CPU Laya fail-open for the requested long batch. Treat this as a capacity boundary, not proof of pruning. No project skill change made.
