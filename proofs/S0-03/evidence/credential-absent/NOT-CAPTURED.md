# credential-absent: what this bundle does NOT contain, and why

There is no `hermes/` half. A key-free Hermes leg cannot be captured through the pinned S0-01
launcher: `proofs/S0-01/tools/pc/pc_launch.py` builds the launch environment in `launch_env`,
which reads `OMNIROUTE_API_KEY` from the owner's profile env FILE (`HERMES_ENV`, a module
constant with no override) and refuses an empty value. `env -u OMNIROUTE_API_KEY` on the launcher
is therefore a no-op for the agent — the old runner did exactly that and would have produced a
negative bundle whose Hermes environ still carried the key.

The kill switch does not need it: the credential is absent from THIS REQUEST, and
`direct/direct.json` records that fact structurally (`credential_presented: false`, and no
`Authorization` key in `request_headers_sent`) beside OmniRoute's 401. The checker grades the
bundle on that evidence.

Making the Hermes half producible needs a seam in S0-01's launcher (a `--hermes-env` argument, or
an `S0_01_HERMES_ENV` override threaded into `launch_env` the way `hermes_home()` threads the
Hermes home). That is S0-01-side work; this proof does not fake it.
