#!/bin/bash
# resume-heal.sh — the whole mechanical fresh-container resume in ONE command
# (ported from trading-system; retro lesson 2026-08-25: the sequence was re-derived
# by hand twice in a day). Idempotent; safe on a healthy tree. Judgment steps
# (three-clock compare, task-DB re-seed from todo/BUILD-TASKLIST.md, PC probe via
# the bridge) stay with the coordinator — this handles only mechanics.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
BR="${RESUME_BRANCH:-$(git rev-parse --abbrev-ref HEAD)}"
git fetch origin "$BR" -q && git merge --ff-only "origin/$BR" 2>/dev/null \
  && echo "tree: $(git log -1 --format=%h) (ff-synced)" \
  || echo "tree: $(git log -1 --format=%h) (NO ff — diverged or already current; compare clocks manually)"
git config core.hooksPath scripts/hooks && echo "hooks: active"
VP=/root/venv-agent-factory/bin/python
[ -x "$VP" ] && "$VP" -c "import pyflakes" 2>/dev/null && echo "venv: ok" || echo "venv: MISSING — run scripts/setup.sh"
[ -x /root/venv-agent-factory/bin/aleph ] && echo "aleph: ok" || echo "aleph: MISSING — run scripts/setup.sh"
export DO_NOT_TRACK=1
command -v graft >/dev/null 2>&1 || npm install -g @nanonets/graft@0.16.0 --silent
[ -f graft/INDEX.md ] || { nohup graft build >/tmp/graft-build.log 2>&1 & echo "graft: building (bg)"; }
command -v gitnexus >/dev/null 2>&1 && [ ! -f .gitnexus/run.cjs ] && { nohup gitnexus analyze >/tmp/gitnexus-analyze.log 2>&1 & echo "gitnexus: indexing (bg)"; }
[ -f .pc-bridge.env ] && echo "bridge: .pc-bridge.env present (probe: scripts/pc.sh hostname)" || echo "bridge: no .pc-bridge.env — ask the owner for the BRIDGE READY banner"
echo "resume-heal done — now: three-clock compare, task-DB re-seed from todo/BUILD-TASKLIST.md, PC probe"
