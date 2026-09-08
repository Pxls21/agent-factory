# `fixtures/evidence-crun` — provenance

**This is a CONSTRUCTED negative fixture, not a captured PC run.**

`canaries.jsonl` was captured by running all eight canaries under plain `sh` on the
sandbox host (the uncontained stand-in the brief names), 2026-09-08:

```sh
cd proofs/S0-08/canaries
{ sh P1.sh; sh P2.sh; sh P3.sh; sh P4.sh; \
  S0_08_SENTINEL_PATH=<tmp sentinel> sh P5.sh; sh P6.sh; sh P7.sh; sh P8.sh; } \
  > ../fixtures/evidence-crun/canaries.jsonl
```

Every observation in it is a real measurement of the uncontained host — nothing was typed.
The host kernel it records is therefore the sandbox's `6.18.44-fc-v24`, **not** the PC's
`6.17.11-200.fc42` (PC-BRIDGE.md:140). The PC's own `--runtime crun` negative control will
produce the same failure SHAPE with its own kernel string; this committed fixture is what
`spec.json`'s negative leg pins, so it stays stable regardless of venue.

`runtime-identity.json` deliberately carries the **valid pinned runsc identity**
(`release-20260817.0`, sha256 `048b89aa…074c`) even though no container ran. That is the
point of the fixture: a bundle whose identity metadata looks correct but whose canaries were
taken outside gVisor must still FAIL, and must fail on P1 — proving the checker reads the
observations rather than trusting the identity file's claim about the runtime.

Expected checker verdict (exit 1):

```
failure_reason: containment: P1 host kernel 6.18.44-fc-v24, not gVisor
```
