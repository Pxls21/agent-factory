#!/usr/bin/env bash
# pc_manifest.sh — v2.2 entry-typed manifest of the FOUR pinned trees (contract §14, audit P1 "symlinks").
# Env: PHASE=pre|post|baseline FD=<dir> [BASE=/home/rocco/s0-01-pinned]. Detached by the caller.
# Body: `## <tree>` header per tree in the pinned order hermes-agent, buzz, acp, venv-hermes, then one
# line per entry: `<sha256> <f|l> <mode4>  ./path[ -> target]` — f = sha256 of the file bytes,
# l = sha256 of "symlink -> <target>"; any other entry type is listed with type `?` (the checker rejects
# it). Entries are sorted by relative path bytes; .git directories are pruned; symlinked directories are
# listed as `l` entries and never descended. Summary: `<tree> <sha256-of-section-text>` x4 + UTC time.
set -u
BASE=${BASE:-/home/rocco/s0-01-pinned}
: "${FD:?}" "${PHASE:?}"
mkdir -p "$FD"
OUT=$FD/manifest-$PHASE.txt
python3 - "$BASE" "$OUT" <<'PY'
import hashlib, os, stat, sys
base, out = sys.argv[1], sys.argv[2]
TREES = [("hermes-agent", "hermes-agent"), ("buzz", "buzz"), ("acp", "acp"), ("venv-hermes", ".venv-hermes")]

def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 16), b""):
            h.update(c)
    return h.hexdigest()

with open(out, "w", encoding="utf-8") as o:
    for name, sub in TREES:
        root = os.path.join(base, sub)
        if not os.path.isdir(root):
            raise SystemExit(f"pc_manifest: tree {name} missing at {root}")
        entries = []
        for dp, dns, fns in os.walk(root):
            dns.sort()
            for d in list(dns):
                if d == ".git":
                    dns.remove(d)
                    continue
                full = os.path.join(dp, d)
                if os.path.islink(full):
                    entries.append(full)
                    dns.remove(d)
            for fn in fns:
                entries.append(os.path.join(dp, fn))
        entries.sort(key=lambda p: os.path.relpath(p, root).encode("utf-8", "surrogateescape"))
        o.write(f"## {name}\n")
        for full in entries:
            rel = "./" + os.path.relpath(full, root)
            st = os.lstat(full)
            mode = f"{stat.S_IMODE(st.st_mode):04o}"
            if stat.S_ISLNK(st.st_mode):
                tgt = os.readlink(full)
                o.write(f"{hashlib.sha256(('symlink -> ' + tgt).encode('utf-8', 'surrogateescape')).hexdigest()} l {mode}  {rel} -> {tgt}\n")
            elif stat.S_ISREG(st.st_mode):
                o.write(f"{sha_file(full)} f {mode}  {rel}\n")
            else:
                o.write(f"{'0' * 64} ? {mode}  {rel}\n")
PY
python3 - "$OUT" "$FD/manifest-$PHASE.summary" <<'PY'
import sys, hashlib, datetime
body = open(sys.argv[1], "rb").read()
assert body.startswith(b"## hermes-agent\n"), "manifest body must open with the hermes-agent header"
out = []
for part in body.split(b"## ")[1:]:
    name, _, text = part.partition(b"\n")
    out.append(f"{name.decode()} {hashlib.sha256(text).hexdigest()}")
out.append(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
open(sys.argv[2], "w").write("\n".join(out) + "\n")
PY
gzip -9 -n -f "$OUT"
sha256sum "$OUT.gz" | cut -d" " -f1 > "$OUT.gz.sha256"
touch "$FD/manifest-$PHASE.done"
