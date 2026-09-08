# `fixtures/evidence-crun` — provenance

**This is a CONSTRUCTED negative fixture, not a captured PC run.** Its two halves have
different provenance and the split is the point:

| half | provenance |
|---|---|
| `canaries.jsonl` | **measured** — the shipped canaries, run uncontained on the sandbox host |
| `runtime-identity.json` | **deliberately typed** — the identity a correct containment run would record |

## How `canaries.jsonl` was captured (2026-09-08, from the repo root)

```sh
SENT=/tmp/s0-08-crun-fixture-sentinel.txt
printf 's0-08 crun fixture sentinel\n' > "$SENT"
for n in P1 P2 P3 P4 P5 P6 P7 P8; do
  case "$n" in
    P2) env -i PATH=/usr/bin:/bin S0_08_MAIN_CMDLINE='sleep 2147483647' \
          sh proofs/S0-08/canaries/$n.sh ;;
    P5) env -i PATH=/usr/bin:/bin S0_08_SENTINEL_PATH="$SENT" \
          sh proofs/S0-08/canaries/$n.sh ;;
    *)  env -i PATH=/usr/bin:/bin sh proofs/S0-08/canaries/$n.sh ;;
  esac
done > proofs/S0-08/fixtures/evidence-crun/canaries.jsonl
rm -f "$SENT"
```

`env -i` matters: the observation must be of the HOST, not of the sandbox session's own
environment. The first capture of this fixture was taken with the session env inherited and,
worse, by a P4 that has since been replaced — the committed line could no longer be produced by
the shipped `P4.sh` at all (VERIFY-G1 F5, the AF-AP-42 class: a fixture its own producer cannot
emit). `tests/test_s0_08_containment.py::test_crun_fixture_is_producible_by_the_shipped_canaries`
re-runs the same command and holds the binding.

The two canaries that need an input get it explicitly, because neither has a default:
`P2.sh` reads `S0_08_MAIN_CMDLINE` (the runner is the single source of that string) and `P5.sh`
reads `S0_08_SENTINEL_PATH`.

### Venue, and which values depend on it

Captured on the **sandbox** (`uname -r` = `6.18.44-fc-v24`), not the PC (`6.17.11-200.fc42`,
PC-BRIDGE.md:140). The PC's own `--runtime crun` negative control will produce the same failure
SHAPE with its own kernel string; this committed fixture is what `spec.json`'s negative leg pins,
so it stays stable regardless of venue.

| value | depends on |
|---|---|
| **P1's `rc`** | **the RUNNING USER** — see below |
| `uname_r`, `dmesg_first_line`, `proc_count`, `pid1_*` | the capture host |
| `dangerous_devices`, `dev_entries`, `mount_*`, `own_pid_*` | the capture host |
| P3's four `*_rc` / `*_out` | which of `python3`, `node`, `uv` sit in `/usr/bin:/bin` there |
| `docker_sock`, `mount_count`, `host_bind_roots` | the capture host |
| `secret_env_count` `"0"`, `secret_env_keys` `""` | **the `env -i` capture, not the host** |
| `sentinel_readable` `"yes"` | **the uncontained run, not the host** |

The `secret_env_*` and `sentinel_readable` rows are the producer-determined values; the regression
test compares those exactly and compares every canary's `observed` KEY SET exactly. The
host-dependent rows are compared only when the re-run happens on the same host (detected by
`uname_r`), which is stated in the test rather than left silent.

### P1's `rc` depends on the user, not on the host

`P1.sh` reads `dmesg`, and `kernel.dmesg_restrict=1` refuses that to an unprivileged caller. The
committed line was captured **as root in the sandbox**, so it carries `"rc":0` with a real boot line.
Re-run by an unprivileged user — the PC's pytest worker is uid 1000, and the PC gate on 2026-09-08
reddened on exactly this — the same canary correctly reports `"dmesg_first_line":""` with `"rc":1`.
That is `P1.sh` working as designed: a `dmesg` that could not run must be visible in `rc`, never
swallowed by a pipeline.

So `test_crun_fixture_is_producible_by_the_shipped_canaries` **derives** P1's expected `rc` from a
direct probe of the venue (`dmesg_works()`) and asserts it on BOTH arms — `rc 0` and a non-empty boot
line where dmesg is readable, `rc 1` and an empty one where it is not. Neither arm is a skip.

**The real containment run is unaffected.** Inside gVisor there is no `/proc/sys/kernel/dmesg_restrict`
and `syslog(2)` is not gated on `CAP_SYSLOG`: VERIFY-G1 measured `dmesg` working for uid 65534 and for
root with `-syslog` dropped inside a runsc sandbox. P1 therefore observes normally as the runtime user
in the venue this proof actually runs in; the venue split above bites only on the UNCONTAINED
stand-in, which is this fixture.

## Why `runtime-identity.json` is typed

It carries the **valid pinned identity on every field the checker pins about the runtime** —
`runsc_version`, `runsc_sha256`, `image_source_commit`, `run_argv` and `canary_exec_user` — even
though no container ran. That is the point of the fixture: a bundle whose identity metadata is
perfect must still FAIL, and must fail on P1, proving the checker reads the OBSERVATIONS rather
than trusting the identity file's claim about the runtime. `capture_argv` records how the
observations were really taken, so the artifact does not have to be read alongside this file to
know that.

Expected checker verdict (exit 1):

```
failure_reason: containment: P1 host kernel 6.18.44-fc-v24, not gVisor
```
