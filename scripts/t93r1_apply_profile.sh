#!/usr/bin/env bash
# T93-R1 — OWNER-RUN STEP on the PC (D-042 option 4, mechanism D-048 option 1; 2026-09-22).
#
# What it does (idempotent, reversible, never a YAML rewrite):
#   1. refuses unless the dated backup exists and the live config is still byte-identical to it;
#   2. APPENDS a `custom_providers:` block to ~/.hermes/profiles/agentfactory/config.yaml carrying the
#      per-request OmniRoute universal-handoff skip flag (`_omnirouteSkipUniversalHandoff: true`) as a
#      per-provider `extra_body`, scoped by `model` to EXACTLY `agentfactory-build-local` and
#      `agentfactory-verify-local` — the raw local id and every other model are untouched
#      (the throwaway-home dry run of 2026-09-22 14:5xZ proved this shape: flag present on the
#      local-combo turn, absent on the raw-id control); the original bytes stay a byte-identical prefix;
#   3. validates the result loads as YAML with exactly two entries;
#   4. launches controls A (combo: flag expected PRESENT) and B (raw id: flag expected ABSENT) in the
#      background, writing ~/.cache/af-probes/t93r1-apply.out — read it after ~2 minutes.
#
# Why the owner runs it: the sandbox's auto-mode classifier refuses any command that names the Hermes
# profile config (16:5xZ, "Modify Shared Resources"), so the coordinator cannot apply it over the bridge.
# Revert: cp -p "$B" "$P"  (the backup path is printed below).
#
# Usage (on the PC):  bash scripts/t93r1_apply_profile.sh
set -u
P="$HOME/.hermes/profiles/agentfactory/config.yaml"
B="$P.bak-20260922T165224Z-t93r1"
[ -f "$B" ] || { echo "ABORT: backup missing: $B (make one: cp -p \"$P\" \"$B\")"; exit 64; }
cmp -s "$P" "$B" || { echo "ABORT: $P already differs from the backup — inspect: diff \"$B\" \"$P\""; exit 65; }
grep -q '^custom_providers:' "$P" && { echo "ABORT: custom_providers already present in $P"; exit 66; }
python3 - "$P" <<'PY'
import sys, yaml, os, tempfile
p = sys.argv[1]
cfg = yaml.safe_load(open(p)) or {}
prov = (cfg.get("providers") or {}).get("omniroute-fedora") or {}
base = prov.get("api") or prov.get("base_url"); ke = prov.get("key_env"); tr = prov.get("transport")
assert base and ke, "providers.omniroute-fedora block incomplete (api/key_env)"
entries = []
for m in ("agentfactory-build-local", "agentfactory-verify-local"):
    e = {"name": "omniroute-fedora", "base_url": base, "model": m, "key_env": ke,
         "extra_body": {"_omnirouteSkipUniversalHandoff": True}}
    if tr: e["transport"] = tr
    entries.append(e)
block = ("\n# T93-R1 (D-042 option 4 via D-048 option 1, 2026-09-22): per-request OmniRoute universal-handoff skip,\n"
         "# scoped by model to the two local combos only; the raw local id and every other model are untouched.\n"
         "# Backup: config.yaml.bak-20260922T165224Z-t93r1 (byte-identical prefix; this block is appended).\n"
         + yaml.safe_dump({"custom_providers": entries}, sort_keys=False, allow_unicode=True))
orig = open(p, "rb").read()
if not orig.endswith(b"\n"): block = "\n" + block
new = orig + block.encode("utf-8")
d = os.path.dirname(p)
fd, tmp = tempfile.mkstemp(dir=d, prefix=".config.yaml.", suffix=".tmp")
with os.fdopen(fd, "wb") as f: f.write(new)
os.chmod(tmp, 0o600); os.replace(tmp, p)
chk = yaml.safe_load(open(p))
cps = chk.get("custom_providers")
assert isinstance(cps, list) and len(cps) == 2 and all(c["extra_body"]["_omnirouteSkipUniversalHandoff"] is True for c in cps)
assert open(p, "rb").read()[:len(orig)] == orig
print("APPLIED: prefix byte-identical, 2 custom_providers entries, models:", [c["model"] for c in cps])
PY
echo "--- appended block (key_env redacted) ---"
diff "$B" "$P" | grep '^>' | sed -E 's/(key_env|api_key|token|secret)(.*)$/\1: <redacted>/I'
cat > /tmp/t93r1_controls.sh <<'CS'
N=$(od -An -N3 -tx1 /dev/urandom | tr -d ' \n')
cd "$HOME/agent-factory"
echo "N=$N start=$(date -u +%H:%M:%SZ)"
echo "--- A: combo (expect flag PRESENT)"; timeout 200 hermes -p agentfactory --no-restore-cwd -m agentfactory-build-local -z "Reply with the single word pong. (t93r1-apply-A-$N)" 2>&1 | tail -2 | cut -c1-160
echo "--- B: raw id (expect flag ABSENT)"; timeout 200 hermes -p agentfactory --no-restore-cwd -m qwen-local/qwen3.8-27b-local -z "Reply with the single word pong. (t93r1-apply-B-$N)" 2>&1 | tail -2 | cut -c1-160
sleep 3
python3 - "$N" <<'PY'
import sys,sqlite3,json,os,datetime
N=sys.argv[1]
c=sqlite3.connect("file:"+os.path.expanduser("~/.omniroute-migrated/storage.sqlite")+"?mode=ro",uri=True)
rows=c.execute("select id,timestamp,requested_model,provider,status,combo_name,artifact_relpath from call_logs order by timestamp desc limit 60").fetchall()
found=0
for r in rows:
    if not r[6]: continue
    try: a=json.load(open(os.path.join(os.path.expanduser("~/.omniroute-migrated/call_logs"),r[6])))
    except Exception: continue
    s=json.dumps(a)
    for tag in ("t93r1-apply-A-"+N,"t93r1-apply-B-"+N):
        if tag in s:
            found+=1
            pl=a.get("pipeline") or {}
            cr=json.dumps(pl.get("clientRawRequest",{}).get("body",{})); pr=json.dumps(pl.get("providerRequest",{}))
            print(f"{tag}: status={r[4]} requested={r[2]} combo={r[5]} provider={str(r[3])[:28]} flag_in_client_body={'_omnirouteSkipUniversalHandoff' in cr} flag_in_provider_request={'_omnirouteSkipUniversalHandoff' in pr} roles={[m.get('role') for m in (pl.get('clientRawRequest',{}).get('body',{}).get('messages') or []) if isinstance(m,dict)][:6]}")
print("artifacts found:",found,"end=",datetime.datetime.utcnow().strftime('%H:%M:%SZ'))
PY
CS
mkdir -p "$HOME/.cache/af-probes"
(setsid nohup bash /tmp/t93r1_controls.sh > "$HOME/.cache/af-probes/t93r1-apply.out" 2>&1 </dev/null &)
echo "controls A/B launched — read: cat ~/.cache/af-probes/t93r1-apply.out (after ~2 min); revert: cp -p \"$B\" \"$P\""
