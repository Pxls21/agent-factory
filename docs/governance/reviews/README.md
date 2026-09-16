# Governance review records (GOV2b)

A Fubuki governance packet is **reviewed** only if this directory holds an owner‑signed record for its
governance hash. `agent_factory.governance.load_packet` computes the hash over the canonical compiled
packet, then `review.verify_review` requires:

- `docs/governance/reviews/<hash>.json` — the record, and
- `docs/governance/reviews/<hash>.json.asc` — a detached OpenPGP signature over that record file,
- which verifies against the committed owner key `docs/governance/owner-signing-key.asc` (in an isolated
  keyring), and whose `governance_hash` field equals the packet's hash and whose `reviewed` field is `true`.

The reviewed bit does **not** come from the packet's own body (VERIFY‑GOV1 F2): a packet cannot assert its
own review, and a review binds to **exact content** — a one‑byte change to the reviewed sources changes the
hash, so no prior record applies and `load_packet` fails closed (`fubuki-packet-unreviewed`). A record signed
by any key other than the committed owner key is refused (`fubuki-review-signature-invalid`), so a first‑party
store is not on its own enough to forge a review. This is the runtime‑hash analogue of the accepted‑proof
anchor (a signed git tag; see `../README.md`); the vehicle differs because the object is a hash, not a commit.

## Owner step — sign a review record

Run from the repo root, with the owner signing key available to `gpg` (same key whose public half is at
`docs/governance/owner-signing-key.asc`).

1. Compute the packet's governance hash (the pin must verify first):

   ```
   HASH=$(FUBUKI_OS_ROOT=<pinned fubuki-os checkout> python3 - <<'PY'
   import os
   from pathlib import Path
   from agent_factory.governance.pin import verify_pinned_fubuki
   from agent_factory.governance.packet import compile_canonical, governance_hash
   verify_pinned_fubuki(Path(os.environ["FUBUKI_OS_ROOT"]), Path("upstream.lock.yaml"))
   print(governance_hash(compile_canonical("<sources root>")))
   PY
   )
   ```

2. Write the record and sign it:

   ```
   printf '{\n  "governance_hash": "%s",\n  "reviewed": true,\n  "reviewer": "<name>",\n  "date": "%s"\n}\n' \
     "$HASH" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "docs/governance/reviews/$HASH.json"
   gpg --armor --detach-sign --output "docs/governance/reviews/$HASH.json.asc" "docs/governance/reviews/$HASH.json"
   ```

3. Commit both files and push. `load_packet` will then return a reviewed packet for that exact hash.

A record whose sources later change no longer matches (the hash moves) — sign a new record for the new hash.
Do not hand‑edit a record after signing: the detached signature will stop verifying.
