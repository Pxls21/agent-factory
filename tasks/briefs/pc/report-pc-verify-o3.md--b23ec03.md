NOT-READY — reproduced blocker: the recursive credential screen accepts opaque and Token-scheme `Authorization` values, allowing a credential-bearing provider profile to attest as key-free.

Report: `tasks/briefs/s0-03-support/VERIFY-O3-report.md`

→ Verified:
- Four-file gate: `242 passed in 42.44s`
- Direct S0-03 suite: `174 passed in 26.80s`
- File identities match O3’s table; report lint: `58 refs — OK 58, MISS 0`
- All six stated closures were attacked through the production checker/collector paths.

→ Blocker:
- `extra_headers.Authorization` with an opaque or Token-scheme value returns rc 0 PASS.
- Contract mapping, canonical production-path reproduction, material effect, deterministic discriminator, and in-boundary repair all hold.
- Repair: recognize `Authorization` case-insensitively by header identity regardless of value scheme; add opaque and Token-scheme negative controls.

→ Follow-ups:
- `row_counts` is emitted but not checked.
- Offset-bearing timestamps can be excluded by the collector’s lexical SQL prefilter.
- A second non-exact execute start is accepted; scope is ambiguous and the exact bound call remains proven.

No live service, owner database, key, credential, or Hermes profile was touched.
