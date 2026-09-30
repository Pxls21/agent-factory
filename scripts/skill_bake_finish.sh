#!/usr/bin/env bash
# skill_bake_finish.sh — the mechanical tail of a skill bake. Edit .claude/skills/<skill>/SKILL.md (and, for a hand-ported
# skill, its port .agents/skills/<skill>/SKILL.md) first; then this script mirrors a skill that is not hand-ported into
# .agents/skills, syncs the lane copies, records the hand-port base hashes, and regenerates sandbox-kit/VENDORED-MANIFEST.md
# in a CLEAN detached worktree that holds only the changed files: a
# live lane's untracked file under a vendored root would shift the manifest in the shared tree (AF-AP-188; done by hand twice
# on 2026-09-24). It prints the paths to commit and commits nothing; commit them with SKIP_MANIFEST_CHECK=1.
#   usage: scripts/skill_bake_finish.sh <skill> [<skill>...]
#   exit: 0 ready · 1 nothing changed · 64 usage/refused · 65 a hand-ported skill's port is missing (task #393), or a
#   pattern reader is red (a line CTX1 moved from CLAUDE.md is gone, a System-1 entry over its budget, a SKILL.md
#   frontmatter) · 66 disk
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
# Task #393: sync-skills never writes a hand-ported skill's .agents copy, and its --record below marks the .claude edit as
# ported: D-115's bake recorded contract-gate and orchestration while their .agents copies lacked the edit (2026-09-30).
# So a named hand-ported skill whose .claude SKILL.md changed while its .agents SKILL.md did not is refused BEFORE any
# sync. BAKE_UNPORTED_OK="<skill> ..." passes a change that needs no port, and says so.
in_before() { local f; for f in "${before[@]}"; do [ "$f" = "$1" ] && return 0; done; return 1; }
for s in "${SKILLS[@]}"; do
  grep -qx -- "$s" harness-ports/hand-ported.txt || continue
  in_before ".claude/skills/$s/SKILL.md" || continue
  in_before ".agents/skills/$s/SKILL.md" && continue
  case " ${BAKE_UNPORTED_OK:-} " in
    *" $s "*) echo "skill_bake_finish: BAKE_UNPORTED_OK names $s: its .agents copy stays as it is" >&2; continue;;
  esac
  echo "skill_bake_finish: $s is hand-ported, and .claude/skills/$s/SKILL.md changed while .agents/skills/$s/SKILL.md" \
    "did not: port the change by hand first (BAKE_UNPORTED_OK=\"$s\" when it needs no port)" >&2
  exit 65
done
# Order matters (task #369): the plain run mirrors a skill that is not hand-ported into .agents/skills (a hand-ported one is
# never overwritten), and the lane copies are filled FROM .agents/skills, so they come second; --record only hashes.
bash harness-ports/bin/sync-skills.sh >/dev/null
bash harness-ports/bin/sync-lane-skills.sh >/dev/null
bash harness-ports/bin/sync-skills.sh --record >/dev/null
mapfile -t changed < <(changed_now)
[ "${#changed[@]}" -gt 0 ] || { echo "skill_bake_finish: nothing changed" >&2; exit 1; }
only_named "${changed[@]}"
# CTX1 (D-089): every line CLAUDE.md held at its PIN stays in CLAUDE.md or a skill it names, verbatim. That test finds the
# skills by pattern, so a path-based gate never picks it up: a reworded moved line reached CI (run #1143, 2026-09-29).
if ! lossless_out="$(python3 tests/test_claude_md_lossless.py 2>&1)"; then
  printf '%s\n' "$lossless_out" | grep -E '^(lossless:|MISSING)' >&2 || printf '%s\n' "$lossless_out" | tail -5 >&2
  echo "skill_bake_finish: a line CTX1 moved from CLAUDE.md is gone: keep it verbatim, or name it in DROPPED with the owner's ruling" >&2
  exit 65
fi
# Two more readers find the skills by pattern: System-1 quotes whole entries under the hook's 2048-byte budget, so an
# entry that grows past it never arrives (a sentence added to the pc-suite entry, the same hour as run #1143), and every
# SKILL.md's frontmatter must parse. About two seconds together.
bt="$(mktemp -d "${TMPDIR:-/tmp}/skillbake-bt.XXXXXX")"
if ! readers_out="$(python3 -m pytest -q -rfE -p no:cacheprovider --basetemp="$bt/bt" tests/test_skill_frontmatter.py \
    tests/test_system1_context.py::test_every_row_resolves_and_each_entry_fits_a_call_alone 2>&1)"; then
  rm -rf "$bt"
  printf '%s\n' "$readers_out" | grep -E '^(FAILED|ERROR|E   )' | head -20 >&2 || true
  echo "skill_bake_finish: a skill reader is red (a System-1 entry over its budget, or a SKILL.md frontmatter): fix the skill" >&2
  exit 65
fi
rm -rf "$bt"
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
