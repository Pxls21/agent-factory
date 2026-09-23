# REPIN-a-R1 lane record — the PC lanes that ran on the lane runtime b3399c1

Measured by the coordinator on the PC, read-only, 2026-09-23 09:14Z, over the bridge (the script is below the table). It answers
VERIFY-REPIN-a F3: the `verified:` field of `hermes-agent-lane-runtime` in `upstream.lock.yaml` counted ledger stamps with a grep
that included non-PC notes and missed PC ones. This record counts the primary source instead: the lane directories that
`scripts/pc_lane.sh` creates under `~/agent-factory/.lanes/` on the PC.

**Rule.** A lane counts when its directory's LATEST launch (the mtime of `prompt.md`, which `harness-ports/bin/pc-lane.sh:218`
truncates at every start; else `brief.md`) is at or after
2026-09-08T14:22:00Z, the owner's `hermes update` that installed b3399c1 (D-043, D-048). `report` = a non-empty `report.md`;
`FAILED` = a `FAILED` marker present at the measurement time.

**Result.** 110 lanes: 98 with a report, 4 with a FAILED marker, the rest live or stopped without a report.

**Limits, stated.** No lane records the Hermes sha it ran on (REPIN-b adds it to `lane.meta`), so a lane launched with a
`HERMES_BIN` override would be counted here although it did not run b3399c1; the dispatcher's default is `hermes` on the PATH,
which resolved to b3399c1 at 08:58Z. Lane directories removed before 09:14Z are not counted.

```
cutoff=2026-09-08T14:22:00Z now=2026-09-23T09:14:40Z
2026-09-08T14:22:32Z report - pc-verify-d5m.md--246bec7
2026-09-08T14:25:47Z report - pc-verify-b5j.md--01499e7
2026-09-08T14:27:09Z report - pc-verify-n5i.md--628da83
2026-09-08T14:28:43Z report - pc-b2.md--246bec7
2026-09-08T14:29:54Z report - pc-verify-m2.md--cb91edf
2026-09-08T14:31:16Z report - pc-verify-g2.md--887f021
2026-09-08T15:20:53Z report - pc-verify-ck13.md--77f46a2
2026-09-08T16:16:34Z report - pc-verify-p5b.md--77f46a2
2026-09-08T16:17:48Z report - pc-verify-o2.md--d12fc13
2026-09-08T16:40:47Z report - pc-m3.md--038bc9b
2026-09-08T17:23:53Z - FAILED pc-b5k.md--5e4f816
2026-09-08T17:31:30Z report - pc-n5j.md--99b7b37
2026-09-08T18:30:02Z report - pc-verify-b2.md--f737de5
2026-09-08T19:14:10Z report - pc-g3.md--488b238
2026-09-08T19:15:21Z report - pc-p5c.md--3614dc9
2026-09-08T19:24:45Z report - pc-k1.md--be5cf35
2026-09-08T20:11:31Z - FAILED pc-d5n.md--887f341
2026-09-08T20:16:09Z report - pc-p5c-b.md--3614dc9
2026-09-08T20:23:49Z - FAILED pc-o3.md--887f341
2026-09-08T21:33:43Z report - pc-b3.md--887f341
2026-09-08T21:47:45Z report - pc-p5c-c.md--3614dc9
2026-09-08T22:12:57Z report - pc-verify-n5j.md--fe2dc3b
2026-09-14T15:51:38Z - - pc-n5k.md--c6c384a
2026-09-14T21:35:12Z - - pc-n5k-xhigh.md--c6c384a
2026-09-14T21:56:34Z - - pc-n5k-xhigh-v2.md--c6c384a
2026-09-15T00:05:24Z - - pc-n5k-xhigh-v3.md--c6c384a
2026-09-15T07:36:28Z report - pc-verify-n5k.md--3277373
2026-09-15T07:59:02Z report - pc-a5l.md--d23762a
2026-09-15T10:40:19Z report - pc-verify-ck14.md--b6483df
2026-09-15T11:57:06Z report - pc-a5m.md--1231624
2026-09-15T12:04:23Z report - pc-qm1.md--47549c7
2026-09-15T12:27:13Z report - pc-qm0.md--7537910
2026-09-15T13:12:45Z report - pc-n5l.md--97bb0c0
2026-09-15T13:42:09Z report - pc-gov1.md--9376760
2026-09-15T15:01:22Z report - pc-verify-gov1.md--78f400d
2026-09-15T15:15:19Z report - pc-qm0b.md--efde78d
2026-09-15T15:16:15Z report - pc-qm1.md--efde78d
2026-09-15T15:16:30Z report - pc-verify-n5l.md--efde78d
2026-09-15T15:18:43Z report - pc-verify-qm0.md--efde78d
2026-09-15T16:02:06Z report - pc-verify-ck15.md--bf8a5dc
2026-09-15T16:07:55Z report - pc-n5m.md--2c7ed47
2026-09-15T16:50:35Z report - pc-a5n.md--c41aab6
2026-09-15T16:50:45Z report - pc-verify-qm1.md--c41aab6
2026-09-15T17:09:44Z - - brief.md--0000000
2026-09-15T18:14:34Z report - pc-verify-n5m.md--f911bd0
2026-09-15T18:16:05Z report - pc-qm1c.md--f911bd0
2026-09-15T19:32:10Z report - pc-n5n.md--c728be5
2026-09-15T19:32:10Z report - pc-verify-a5n.md--c728be5
2026-09-15T19:32:10Z report - pc-verify-qm1c.md--c728be5
2026-09-15T19:56:13Z report - pc-qm1d.md--c728be5
2026-09-15T21:12:33Z report - pc-verify-qm1d.md--8c1dbe6
2026-09-15T21:29:26Z report - pc-a5o.md--99ecb36
2026-09-16T00:19:10Z report - pc-verify-a5o.md--45e7bf6
2026-09-17T09:42:10Z report - pc-verify-b3.md--c6c384a
2026-09-17T09:46:14Z report - pc-verify-m3.md--e776dd0
2026-09-17T09:46:17Z report - pc-verify-g3.md--7f60d83
2026-09-17T10:01:20Z report - pc-o3.md--a827346
2026-09-17T11:22:36Z report - pc-b4.md--6760808
2026-09-17T11:56:28Z report - pc-m4.md--c367d76
2026-09-17T12:37:15Z report - pc-verify-o3.md--b23ec03
2026-09-17T13:29:59Z report - pc-o4.md--d84a90a
2026-09-17T13:30:47Z report - pc-verify-m4.md--d84a90a
2026-09-17T13:53:55Z report - pc-verify-b4.md--95c0bb1
2026-09-17T14:28:15Z report - pc-b5.md--0c67ae9
2026-09-17T15:24:38Z report - pc-verify-o4.md--a154431
2026-09-19T18:05:22Z report - pc-b4.md--798ce74
2026-09-19T18:09:12Z report - pc-a5p.md--798ce74
2026-09-21T14:34:19Z report - pc-vb-f12-t2.md--38ad46b
2026-09-21T16:38:10Z report - pc-vb-f12-g1.md--772ce3b
2026-09-21T21:08:34Z report - pc-verify-vb-f12.md--955ab74
2026-09-21T22:30:09Z report - pc-vb-f12-g2.md--85836a5
2026-09-22T00:16:18Z report - pc-verify-g2.md--f84265f
2026-09-22T01:22:45Z report - pc-a5q.md--236bec7
2026-09-22T01:24:18Z report - pc-b6.md--236bec7
2026-09-22T01:25:44Z report - pc-k1-c.md--236bec7
2026-09-22T02:34:25Z report - pc-s4h.md--d92bfcf
2026-09-22T02:50:28Z report - pc-b7.md--c439580
2026-09-22T04:29:34Z report - pc-verify-a5q.md--2e02afd
2026-09-22T04:38:38Z report - pc-verify-s4h.md--a815883
2026-09-22T04:58:00Z report - pc-k1-d.md--4d45f19
2026-09-22T05:56:56Z report - pc-verify-b67.md--22bd6f5
2026-09-22T06:22:57Z report - pc-verify-gov2c.md--4cc3fe2
2026-09-22T07:13:27Z report - pc-e1-r1.md--953ccfe
2026-09-22T07:19:32Z report - pc-t90-premise-gate.md--c2a0df2
2026-09-22T08:15:31Z report - pc-b8.md--889f1cc
2026-09-22T08:54:33Z report - pc-verify-gov2c-a.md--dab9803
2026-09-22T09:15:03Z report - pc-verify-gov2c-b.md--dab9803
2026-09-22T09:26:11Z report - pc-t91-provider-mix-safety-family.md--93faca0
2026-09-22T09:38:00Z report - pc-verify-gov2c-c.md--dab9803
2026-09-22T10:39:50Z report - pc-verify-k1.md--cd976f5
2026-09-22T10:58:32Z report - pc-gov2d.md--2da04bf
2026-09-22T12:38:13Z report - pc-k1-g.md--46186d6
2026-09-22T12:53:54Z report - pc-t90-r1.md--9ca3279
2026-09-22T13:19:57Z report - pc-t93-local-400-evidence.md--a58a1b9
2026-09-22T13:56:53Z report - pc-verify-b8.md--b3eba6a
2026-09-22T14:12:06Z report - pc-verify-gov2d.md--d116cbc
2026-09-22T14:19:49Z report - pc-verify-t90.md--c49880c
2026-09-22T15:35:13Z report - pc-t90-r2.md--435b057
2026-09-22T15:46:08Z report - pc-gov2e.md--c4d12d1
2026-09-22T16:03:28Z report - pc-verify-k1-g.md--fe2284d
2026-09-22T16:09:39Z report - pc-b9.md--71463f3
2026-09-22T17:36:22Z report - pc-verify-gov2e.md--949aa85
2026-09-22T19:22:17Z report - pc-verify-t90-r2.md--76ca87c
2026-09-22T19:32:43Z report - pc-jev-laya-pc.md--dd4c579
2026-09-22T21:52:34Z report - pc-j1-1.md--330803c
2026-09-22T23:11:58Z report - pc-t92.md--879c6f9
2026-09-23T02:45:18Z - - pc-verify-j1-1.md--52c02ee
2026-09-23T02:51:29Z - FAILED pc-verify-j1-0-r23-stamp.md--5a00d13
2026-09-23T03:56:48Z - - pc-k1-h.md--74aa8c5
2026-09-23T07:14:08Z - - pc-verify-t92-t90r3-pcj1.md--433d15e
```

The measuring script (run on the PC with `bash`):

```bash
cd $HOME/agent-factory/.lanes 2>/dev/null || { echo "no .lanes dir"; exit 3; }
CUT=$(date -u -d '2026-09-08 14:22:00' +%s)
echo "cutoff=2026-09-08T14:22:00Z now=$(date -u +%FT%TZ)"
n=0; r=0; f=0
for d in */; do
  d=${d%/}
  first=$(stat -c %Y "$d/prompt.md" 2>/dev/null || stat -c %Y "$d/brief.md" 2>/dev/null || echo 0)
  [ "$first" -ge "$CUT" ] || continue
  n=$((n+1))
  rep=$( [ -s "$d/report.md" ] && echo report || echo - ); [ "$rep" = report ] && r=$((r+1))
  fl=$( [ -f "$d/FAILED" ] && echo FAILED || echo - ); [ "$fl" = FAILED ] && f=$((f+1))
  printf '%s %s %s %s\n' "$(date -u -d @$first +%FT%TZ)" "$rep" "$fl" "$d"
done | sort
```
