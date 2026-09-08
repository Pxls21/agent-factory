# What this bundle does NOT contain, and why

There is no `hermes/` half. A key-free Hermes leg cannot be captured through the pinned S0-01
launcher: `proofs/S0-01/tools/pc/pc_launch.py` builds the launch environment in `launch_env`,
which reads `OMNIROUTE_API_KEY` from the owner's profile env FILE (`HERMES_ENV`, a module
constant with no override) and refuses an empty value. `env -u OMNIROUTE_API_KEY` on the launcher
is therefore a no-op for the agent — the previous runner did exactly that, and the leg it would
have produced still carried the key.

The credential verdicts do not need it. They are decided on the DIRECT leg's own evidence:
`direct/direct.json` records `credential_presented` and the header names it sent, beside
OmniRoute's status. `check_credential_at_the_gate` reads that before the hermes half is required,
which is why a direct-leg-only bundle grades as the seed's kill switch rather than as a short
bundle. The second, independent signal (a Hermes environ with no `OMNIROUTE_API_KEY`) is still
implemented and still tested — `tests/test_s0_03_omniroute.py::test_an_environ_without_the_key_is_the_kill_switch`
drives it on a full bundle.

Making the Hermes half producible needs a seam in S0-01's launcher (a `--hermes-env` argument, or
an `S0_01_HERMES_ENV` override threaded into `launch_env` the way `hermes_home()` threads the
Hermes home). That is S0-01-side work, outside this proof's file boundary. It is NOT faked here.
