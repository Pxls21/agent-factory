#!/usr/bin/env bash
# skill_bake_finish.sh — the mechanical tail of a skill bake. Edit .claude/skills/<skill>/SKILL.md (and, for a hand-ported
# skill, its port .agents/skills/<skill>/SKILL.md) first; then this script syncs the lane copies, records the hand-port base
# hashes, and regenerates sandbox-kit/VENDORED-MANIFEST.md in a CLEAN detached worktree that holds only the changed files: a
# live lane's untracked file under a vendored root would shift the manifest in the shared tree (AF-AP-188; done by hand twice
# on 2026-09-24). It prints the paths to commit and commits nothing; commit them with SKIP_MANIFEST_CHECK=1.
#   usage: scripts/skill_bake_finish.sh <skill> [<skill>...]      exit: 0 ready · 1 nothing changed · 64 usage/refused · 66 disk
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
[ $# -ge 1 ] || { echo "usage: skill_bake_finish.sh <skill> [<skill>...]" >&2; exit 64; }
for s in "$@"; do
  case "$s" in */*|.*|"") echo "skill_bake_finish: bad skill name: $s" >&2; exit 64;; esac
  [ -f ".claude/skills/$s/SKILL.md" ] || { echo "skill_bake_finish: no .claude/skills/$s/SKILL.md" >&2; exit 64; }
done
changed_now() {
  git status --porcelain --untracked-files=no -- .claude/skills .agents/skills .agents/lane-skills \
    harness-ports/hand-ported.sha256 | awk '{print $2}'
}
only_named() {                          # another lane's skill edit must never ride along; checked BEFORE any sync
  local f s ok
  for f in "$@"; do
    ok=0
    [ "$f" = harness-ports/hand-ported.sha256 ] && ok=1
    for s in "${SKILLS[@]}"; do
      case "$f" in ".claude/skills/$s/"*|".agents/skills/$s/"*|".agents/lane-skills/$s/"*) ok=1;; esac
    done
    [ "$ok" = 1 ] || { echo "skill_bake_finish: $f changed but is not one of the named skills: refusing" >&2; exit 64; }
  done
}
SKILLS=("$@")
mapfile -t before < <(changed_now)
only_named "${before[@]}"
bash harness-ports/bin/sync-lane-skills.sh >/dev/null
bash harness-ports/bin/sync-skills.sh --record >/dev/null
mapfile -t changed < <(changed_now)
[ "${#changed[@]}" -gt 0 ] || { echo "skill_bake_finish: nothing changed" >&2; exit 1; }
only_named "${changed[@]}"
free_mb="$(df -Pm . | awk 'NR==2 {print $4}')"
[ "${free_mb:-0}" -ge 1500 ] || { echo "skill_bake_finish: only ${free_mb:-?} MB free; a worktree needs about 1 GB" >&2; exit 66; }
WT="$(mktemp -d "${TMPDIR:-/tmp}/skillbake.XXXXXX")"
trap 'git worktree remove --force "$WT" >/dev/null 2>&1 || rm -rf "$WT"; git worktree prune' EXIT
git worktree add -q --detach "$WT" HEAD
for f in "${changed[@]}"; do cp "$f" "$WT/$f"; done
(cd "$WT" && python3 scripts/vendored_manifest.py --write >/dev/null && python3 scripts/vendored_manifest.py --check)
out=("${changed[@]}")
for m in sandbox-kit/VENDORED-MANIFEST.md sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv; do
  cmp -s "$WT/$m" "$m" || { cp "$WT/$m" "$m"; out+=("$m"); }
done
echo "skill_bake_finish: commit these with SKIP_MANIFEST_CHECK=1 (the manifest was regenerated in a clean worktree):"
printf '%s\n' "${out[@]}"
