# RW1 Report — ripwire v0.4.0 advisory adoption

PIN verified: dd0cbc2bcc22fb3345f068b520c2f254247b1ed5

## DONE

| # | Deliverable | File:line | Proof |
|---|---|---|---|
| 1 | upstream.lock.yaml | upstream.lock.yaml:137-148 | `advisory_tooling.ripwire` block: repo, tag, commit, asset_sha256, binary_sha256, license, role, adopted, telemetry |
| 2 | scripts/setup.sh | scripts/setup.sh:167-189 | Block mirrors sentrux pattern: skip on digest match, else download+verify asset+verify binary+install; warn on failure; idempotent |
| 3 | scripts/ripwire_review.sh | scripts/ripwire_review.sh:1-72 | 8 modes, exclude set baked in, --limit on flat verbs, --top-k on map, exit 64 before binary probe, exit 0 on missing binary |
| 4 | tests/test_ripwire_review.py | tests/test_ripwire_review.py:1-152 | 21 tests: (a) bogus mode exit 64, (b) 8 modes missing binary exit 0, (c) argv per mode with fake binary, (d) exit code passthrough, (e) negative control mutant |
| 5 | Docs: THIRD-PARTY-AGENT-TOOLS.md | sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md:119-163 | ripwire section: provenance, unsigned caveat, skills/hooks not-installed rule, blind spot, flag quirks, PC install step |
| 5 | Docs: code-intel-trio (claude) | .claude/skills/code-intel-trio/SKILL.md:112-147 | ripwire section: when to use each mode, wrapper invocations, DORMANT rule, pins |
| 5 | Docs: code-intel-trio (agents) | .agents/skills/code-intel-trio/SKILL.md:120-155 | same hunk as claude copy |
| 5 | sync-lane-skills | .agents/lane-skills/code-intel-trio/ | `bash harness-ports/bin/sync-lane-skills.sh` → synced 25 skills (2 changed: build-loop, code-intel-trio) |
| 6 | Gate lines | below | all pasted verbatim |

## Digests

- **asset_sha256:** `fd0bd0fa849c0e08db59a6a7e5c2d3e9bc062d3089b54196daf9332cd21bbfc8`
- **binary_sha256:** `6a1957b829f74e29b16caf550e90ea5504afa3ebd200c0b253f2f3afaae76aa3`

## Gate lines (verbatim)

### map --top-k=5 (first line, the header)

```
<!-- ripwire v1 t=fn|method|cls|struct|iface|var|sec|macro(...) ... -->
<!-- files=365 symbols=11528 edges=2127 shown=5 est_tokens=972 ... order=important-first -->
<r root="/home/user/agent-factory" est_tokens="972" pr_iters="11">
```

### callers _write_status

```xml
<callers of="_write_status" defs="1" count="3" ... shown="3" capped="0" total="3" ...>
  <s t="fn" n="main" p="proofs/S0-01/tools/frame_tee.py:102"/>
  <s t="fn" n="pump_fd" p="proofs/S0-01/tools/frame_tee.py:242"/>
  <s t="fn" n="pump_pipe" p="proofs/S0-01/tools/frame_tee.py:326"/>
</callers>
```

### test_summary (run 1)

```
pytest-summary: 21 passed in 0.19s
```

### test_summary (run 2)

```
pytest-summary: 21 passed in 0.18s
```

### lint_delta

```
lint_delta (worktree vs origin/claude/soundbox-kit-migration-iz1jwf): 4 .py changed, 0 NEW pyflakes hit(s), 0 removed
```

### setup.sh idempotent

```
✓ ripwire v0.4.0 present (digest verified)
```

### sync-lane-skills

```
DRIFT: build-loop
DRIFT: code-intel-trio
sync-lane-skills: synced 25 skills into .agents/lane-skills (2 changed)
```

### Telemetry check performed

`strings` on the binary for telemetry/analytics/phone-home/sentry/mixpanel/amplitude/segment/posthog/track keywords: zero relevant matches (all hits were from embedded documentation text about git tracking, caching, and variable naming). Outbound URL scan (`strings | grep https?://`): no phone-home URLs found — only `http://127.0.0.1`, `http://localhost` (MCP loopback listener), GitHub docs URLs, language-spec references, and the SARIF schema URL. `--help` text has no telemetry/analytics subcommands. The binary is documented as offline; writes a per-root cache under TMPDIR only.

## NOT_DONE

- **CLAUDE.md update** — out of scope per boundary override; the coordinator adds the one-clause bullet on the "Advisory instruments" line.
- **harness-ports/hand-ported.sha256** — out of scope per boundary override; the coordinator runs `sync-skills.sh --record` at commit time.
- **PC-side install** — owner-run step, documented in THIRD-PARTY-AGENT-TOOLS.md §ripwire.

## DISCREPANCIES

None. All brief-stated facts verified:
- Tarball sha256 matches the published `.tar.gz.sha256` file and the brief's stated value.
- Binary sha256 matches the brief's stated value.
- `--version` output matches: `ripwire 0.4.0 (Release, GNU 14.2.1, built_from=unknown)`.
- `--callers` with `--top-k` exits 1 as documented.
- `--callers=_write_status` returns main/pump_fd/pump_pipe as the brief predicted.
- `--for` ignores `--top-k` as documented (no rejection, BM25 route).

## SELF-ATTACK

1. **The setup.sh block might fail to extract the binary if tarball structure changes.** Mitigated: `--strip-components=1` with explicit path `ripwire-0.4.0-linux-x64/ripwire` pins the extraction to the exact inner path; the binary digest check after extraction catches any content mismatch; the `warn` path prevents setup.sh from failing. Risk: LOW — the version is pinned, the structure was verified.

2. **The wrapper passes `$ROOT` as the scan directory, which means it scans the full repo root including files other lanes hold dirty.** This is correct behavior (ripwire reads the tree, never writes into it, and the exclude flags skip vendored trees). The alternative (a composed copy like sentrux) is unnecessary because ripwire has native `--exclude`. Risk: NONE.

3. **The test suite uses a fake binary (shell script) and never exercises the real ripwire binary.** This is by design (deterministic, no network, no real binary needed — per the brief's spec). The gate lines (deliverable 6) exercise the REAL binary through the wrapper and are pasted verbatim above. Risk: LOW — the fake proves the wrapper builds the correct argv; the gate proves the real binary accepts it.
