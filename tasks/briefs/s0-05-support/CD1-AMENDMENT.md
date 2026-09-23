# CD1: the S0-05 live-leg launch recipe, a contract amendment (coordinator, 2026-09-23)

STATUS: DECIDED from measurements, except OD-1 (the relay bind), which is the owner's. This amendment feeds the E3 brief.
E3 is written after E2-R1 lands, because both touch `proofs/S0-05/tools/pc/run_s0_05_units.sh`. Task #142.

## The defect (mine, returned by VERIFY-E2 as CD1)

The E2 contract named S0-01's capture launcher in both `LAUNCH` rows (`run_s0_05_units.sh:52` and `:54` at PIN 9223162):
`/usr/bin/python3 $S0_01_TOOLS/pc_launch.py --leg run-1 --model s0-01-pong`. That launcher is S0-01's tool, not a unit launcher.
Read at HEAD (`proofs/S0-01/tools/pc/pc_launch.py`, `main`): it deletes and recreates `<base>/.markers/v2-run-1`, writes S0-01's
`.markers/buzz-acp.pid` and `.markers/current-framedir`, rewrites the model line of the pinned Hermes `config.yaml`, and probes
the scripted backend at `127.0.0.1:20201`, which no namespace can reach. Run by the root runner inside a unit namespace, it would
re-own S0-01's framedir as root and then die at the probe, so it could never record a `run` unit. The lane built what the contract
said; the contract was wrong.

## PREMISE: MEASURED at authoring (2026-09-23, the PC as uid 1000, read-only; scratch under `/home/rocco/s0-05-scratch/`)

The three probe scripts are committed beside this file (`tasks/briefs/s0-05-support/CD1-probes/`); each was shipped to the PC
base64-encoded and run once through `scripts/pc.sh`. Lines starting `#` inside the fenced blocks are my notes, not output.
Some `==` headers are shortened, some log lines lose their timestamp, and ANSI colour codes are stripped; nothing else is
changed in the lines shown.

Probe 1, listeners, identities, `--help` (03:09:17Z):

```
== listeners (20128 OmniRoute, 3999 relay, 20201 scripted backend)
0.0.0.0:20128
127.0.0.1:20201
127.0.0.1:3999
== identity
rocco 755 16859136 /home/rocco/s0-01-pinned/buzz/target/release/buzz-acp
a5a17ffc0c7ef878648a506b9d5066120b91984d1158a60e6ce9664a39f88064
rocco 755 249 /home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp
f90a0cc333fa86d99495c7c984e4e11a1b83a7e3dc92883b7fd295ae70358ef1
#!/home/rocco/s0-01-pinned/.venv-hermes/bin/python3
== S0-01 framedir owner (CD1's inferred damage; the runner never ran on the PC)
rocco 755 2026-09-22 16:12:08.474657002 +0100 /home/rocco/s0-01-pinned/.markers
rocco 755 2026-09-22 16:07:28.746447903 +0100 /home/rocco/s0-01-pinned/.markers/v2-run-1
== hermes-acp --help
usage: hermes-acp [-h] [--version] [--check] [--setup] [--setup-browser]
                  [--yes]
== files written into the scratch tree by the two --help calls
<scratch>/home
<scratch>/hermes-home
```

The two sha256 values equal `PINNED_BUZZ_ACP_SHA256` and `PINNED_AGENT_ENTRYPOINT_SHA256` (`proofs/S0-01/pins.py:32` and `:34`).
S0-01's tree is undamaged: CD1's harm was reproduced by VERIFY-E2 in the sandbox, never on the PC.

Probe 2, lifetime and startup writes, inside `unshare -c -n` (no network; 03:10:36Z). Only the relevant lines:

```
== hermes-acp --version
0.21.0
== hermes-acp --check
Hermes ACP check OK
== hermes-acp, stdin /dev/null, 30 s cap
rc=1 secs=.384660991
# the traceback runs through asyncio's _UnixReadPipeTransport._add_reader (stdin) and ends in:
PermissionError: [Errno 1] Operation not permitted
2026-09-23 04:10:37 [ERROR] acp_adapter.entry: ACP agent crashed
== hermes-acp, stdin held open 10 s then EOF, 30 s cap
rc=1 secs=10.002158049
2026-09-23 04:10:37 [INFO] acp_adapter.entry: Starting hermes-agent ACP adapter
2026-09-23 04:10:37 [ERROR] acp_adapter.entry: ACP agent crashed
# stdout was a regular file here; the crash is logged in the start second, and the 10 s is the
# pipeline waiting for `sleep 10`. The adapter's log clock is local time (UTC+1).
== buzz-acp, an INVENTED key, relay unreachable (isolated), agent /bin/false, 20 s cap
rc=1 secs=.009693578
# the startup line, shortened here to the fields the amendment uses:
buzz-acp starting: relay=ws://127.0.0.1:3999 ... idle_timeout=1500s max_turn=7200s agents=1 ... session_policy=channel ...
ERROR buzz_acp: agent initialize failed: Agent process exited unexpectedly agent=0
Error: all 1 agents failed to start — cannot continue
== files written into the scratch tree
# eleven entries under hermes-home, listed here on one line; <scratch>/home stayed empty:
<scratch>/hermes-home/{audio_cache,cron,hooks,image_cache,logs,logs/curator,memories,pairing,sessions,skills,SOUL.md}
```

Probe 3, the isolation instrument and both ends piped (03:11:19Z). Probe 2 first listed `/sys/class/net`, which shows the
host's interfaces from any netns (sysfs keeps the view of the netns that mounted it): the wrong instrument. Re-checked:

```
== host view: interfaces in /proc/net/dev
lo enp7s0 wlp6s0 tailscale0
== isolated view: /proc/net/dev + ip -o link (inside unshare -c -n)
lo
lo:
== hermes-acp, stdin a pipe held open 10 s, stdout+stderr a pipe into cat (inside unshare -c -n), 30 s cap
rcs(sleep,hermes,cat)=0 0 0 secs=10.044975363
tracebacks=0
[INFO] acp_adapter.entry: Starting hermes-agent ACP adapter
[INFO] acp_adapter.server: ACP client connected
```

## The amendment (decided)

**A1. No S0-01 tool in any S0-05 row.** Each unit is executed from its pinned realpath (`PINNED_AGENT_REALPATH`,
`PINNED_BUZZ_ACP_EXE_REALPATH`). Before launch, the runner checks the file's sha256 against the pin
(`PINNED_AGENT_ENTRYPOINT_SHA256`, `PINNED_BUZZ_ACP_SHA256`). A mismatch is `not-run|unit identity mismatch: <path>`. A test
refuses any row that names `proofs/S0-01/tools`, `.markers` or `.secrets`.

**A2. S0-05 owns every byte it writes.** Each unit gets a scratch tree under the evidence root, owned by the unit's user, with
its own `HOME` and `HERMES_HOME`. The Hermes unit writes eleven entries into `HERMES_HOME` at startup (probe 2), so it can never
share S0-01's home. The live leg takes a `stat` census of `/home/rocco/s0-01-pinned/.markers` and every `v2-*` directory before
and after the leg and fails if anything changed.

**A3. The Hermes unit's stdio is two pipes.** Stdin is a pipe the runner holds open for the canary window. Stdout and stderr go
through a pipe into the unit log. Neither end is ever `/dev/null` or a regular file: either one makes the ACP adapter crash at
startup with `PermissionError` from asyncio's epoll registration (probe 2). Closing stdin is the clean stop: the adapter exits 0
at EOF (probe 3). Namespace destroy stays the backstop for a unit that does not stop.

**A4. The unit runs as a non-root user.** The runner needs root to build namespaces, but the unit does not. It drops the unit to
the service user (`setpriv --reuid=<uid> --regid=<gid> --init-groups`, uid 1000 on the PC unless the owner names a dedicated
service user) inside `ip netns exec`, before exec. The live record asserts `Uid:` in `/proc/<pid>/status` is not 0. This is
standing rule 11, and it is the class behind the root-owned framedir VERIFY-E2 reproduced.

**A5. The Hermes unit carries no credential.** No `OMNIROUTE_API_KEY` and no `config.yaml` beyond what the adapter writes itself.
It starts, serves ACP on its pipes and is contained (probe 3 shows it starts without either). The positive control stays C0 from
the namespace to the allowed OmniRoute address. A model round trip from inside the namespace is S0-03's claim, not S0-05's; it is
NOT in scope, and the runner's header already says the canaries prove the namespace, not the unit's own sockets.

**A6. The buzz-acp unit is the pair, and it is BLOCKED today.** Its row runs the pinned buzz-acp with
`--agent-command <PINNED_AGENT_REALPATH> --agent-args ""`, the S0-01 idle and max-turn values, and an S0-05 fixture identity,
never S0-01's `.secrets/agent.env`. buzz-acp spawns the agent as its own child process (probe 2 shows it initializing the agent
and failing on it, with no relay error logged), and a child inherits its parent's namespace. So the pair's allow-set is
{relay, OmniRoute}, per docs/05 §6 ("Buzz relay and
local/private `hermes-acp` endpoint/process"). Rejected: one namespace per process. buzz-acp spawns the agent through
`--agent-command` in its own namespace, and splitting them would need root inside buzz-acp. BLOCKED: the relay listens on
`127.0.0.1:3999` only (probe 1), so C0 fails from every namespace. The runner records `not-run|positive control unreachable:
relay bound to 127.0.0.1:3999` until OD-1 is decided.

**A7. The runner proves the unit ran.** At canary time it records the unit's pid from `ip netns pids <ns>`, the realpath of
`/proc/<pid>/exe`, the sha256 of the entrypoint (argv[1] for the Python unit), and the Uid. The canaries run only if the record
matches the pins. This replaces `pc_launch.py`'s readiness files and closes F14's question for the live leg: the real unit, not a
stand-in, was alive in the namespace.

**A8. The runner forms the Hermes allow entry itself.** The veth host address comes from the namespace name
(`egress_ns_host_ip`, `netns_lib.sh:49`: `10.201.<octet>.1`). The operator supplies only the port (`20128`), and the runner forms
`$(egress_ns_host_ip "$ns"):20128`. An operator who types an address that does not match the hash would only fail C0, but a
derived value removes the chance.

## What this does NOT settle

- Whether the host firewall accepts traffic from a veth host end to `:20128`. OmniRoute listens on `0.0.0.0:20128` (probe 1),
  so no rebind is needed, but only the root runner's C0 preflight can measure the firewall. If the owner later binds OmniRoute to
  Tailscale only (task #34's option), the Hermes unit's C0 fails with the named reason, as designed.
- The S0-05 fixture identity for the buzz-acp pair (a key the relay accepts). It is needed only after OD-1.
- The seed's wording question for the second assertion (containment property versus a routed variant). It stays the owner's, as
  E2 said.

## OD-1, the owner's decision: how a namespace reaches the relay

The relay the pinned buzz-acp uses listens on `127.0.0.1:3999`, and a namespace has its own loopback. Options:

1. **A runner-scoped DNAT (recommended).** For the leg only, the root runner adds a host `nat PREROUTING` rule on the pair's veth
   host end (`<veth-host>:3999` to `127.0.0.1:3999`) and sets `route_localnet=1` on that one interface. Both are removed in
   cleanup and checked by the census. No service is touched or restarted. The cost: for the leg's duration, that one interface
   may route to loopback, and only the allow-listed port is DNAT-ed.
2. **Rebind the relay.** The owner configures the relay to also listen on the veth host address and restarts it for the leg. It is
   cleaner on the host network, but it is a restart of the owner's service, and the veth address exists only while the leg runs.
3. **Leave buzz-acp not-run.** S0-05 then covers the Hermes unit only, and the seed's "every non-OmniRoute unit" stays unmet, so
   S0-05 cannot mint.
