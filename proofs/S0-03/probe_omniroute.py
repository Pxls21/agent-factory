#!/usr/bin/env python3
"""Probe whether OmniRoute accepts the explicitly supplied bearer credential.

The runner (`scripts/proof-runner:226-271`) maps this exit code through `probe.json`'s
`reason_map` into the blocked marker's `reason`, and the validator turns a `rejecting` marker for
S0-03 into proof-RED (`scripts/validate-ledger:336-338`). So the exit code decides whether a
result is read as "no credential yet" (an honest deferral) or "the credential was REFUSED" (a
RED). Conflating the two is a fail-open: before this fix EVERY failure returned 11
`credential_rejected`, so a stopped OmniRoute, a DNS failure and a 500 all reported that the
owner's credential had been rejected — a state the validator escalates to proof-RED.

Exit codes and why each is the one the marker needs:

  0   2xx                    the credential was ACCEPTED. The runner records
                             blocker_status `expired` — the deferral is over, the proof must run.
  10  key absent             `credential_absent` — nothing was presented; mapped in probe.json.
  11  HTTP 401 or 403        `credential_rejected` — OmniRoute's auth gate REFUSED the key that
                             was presented. This is the only refusal the gate can express:
                             `src/server/authz/policies/clientApi.ts:77` (no bearer) and `:96`
                             (invalid bearer) both reject 401/AUTH_002 when REQUIRE_API_KEY is
                             on. Mapped in probe.json; the validator turns it into proof-RED.
  12  any other HTTP status  UNMAPPED on purpose. A 404/500/503 says something about the service,
                             never about the credential. `reason_map` has no "12", so the runner
                             raises `probe-invalid` and the run fails LOUD instead of minting a
                             marker that misnames the blocker.
  13  URLError / timeout /   UNMAPPED on purpose, same argument: an unreachable or silent port is
      any transport error    not a credential verdict.
  64  usage                  no URL argument.

The credential is read from `OMNIROUTE_API_KEY` — the name `probe.json` threads through
`key_env`, the name the owner's Hermes profile env actually uses, and the name
`scripts/omniroute_invariants.sh:76` reads. The seed's `OMNIROUTE_UPSTREAM_KEY`
(`seeds/seed-stage0-v1.yaml:404`) and `docs/03_INTEGRATION_CONTRACTS.md:31-51` /
`.env.example:24`'s `OMNIROUTE_INTERNAL_API_KEY` are the SAME credential under two other names;
the three-way naming discrepancy is recorded, not resolved here (the registry's
`unblock_condition` string is the coordinator's edit).

The value is read from the environment and placed in a header. It is never printed, never
written to a file, and never passed in argv (AF-AP-35/AF-AP-39).
"""
import os
import sys
import urllib.error
import urllib.request

EXIT_OK = 0
EXIT_KEY_ABSENT = 10
EXIT_KEY_REJECTED = 11
EXIT_HTTP_OTHER = 12
EXIT_UNREACHABLE = 13
EXIT_USAGE = 64

REJECTING_STATUSES = (401, 403)


def main():
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        print("usage: probe_omniroute.py <url>", file=sys.stderr)
        return EXIT_USAGE
    key = os.environ.get("OMNIROUTE_API_KEY")
    if not key:
        return EXIT_KEY_ABSENT
    request = urllib.request.Request(
        sys.argv[1],
        headers={"Authorization": f"Bearer {key}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            if 200 <= response.status < 300:
                return EXIT_OK
            # urlopen only returns here for 2xx in practice; a non-2xx arrives as HTTPError.
            # Kept so the success test is an explicit range, not a fall-through.
            return EXIT_KEY_REJECTED if response.status in REJECTING_STATUSES else EXIT_HTTP_OTHER
    except urllib.error.HTTPError as exc:
        # HTTPError is a subclass of URLError — it MUST be caught first or every HTTP status
        # would fall into the transport branch below.
        return EXIT_KEY_REJECTED if exc.code in REJECTING_STATUSES else EXIT_HTTP_OTHER
    except urllib.error.URLError:
        return EXIT_UNREACHABLE
    except (TimeoutError, OSError):
        # A read timeout after the connection is established surfaces as TimeoutError/OSError
        # rather than URLError. Same verdict: not a credential result.
        return EXIT_UNREACHABLE


if __name__ == "__main__":
    raise SystemExit(main())
