#!/bin/bash
# TURN-RETRO GATE (owner directive 2026-08-25, supersedes wiki-stop-gate.sh):
# once per batch of landed work (keyed on HEAD), block turn-end with the full
# self-tuning checklist — wiki, bugs/lessons, skills, next-time-easier. The
# sentinel makes it bounded: one retro per new HEAD, answered by DOING what is
# needed or explicitly stating nothing is. This mechanizes the deep-work
# retrospective rule so it no longer depends on the coordinator remembering.
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SENT="$REPO_ROOT/.git/turn-retro-acked"
HEAD_SHA="$(cd "$REPO_ROOT" && git rev-parse --short HEAD 2>/dev/null)" || exit 0
if [ -f "$SENT" ] && [ "$(cat "$SENT")" = "$HEAD_SHA" ]; then
  exit 0
fi
# Exemptions: ack silently when EVERY commit since the last acked SHA is
# (a) index-stamp machine churn, or (b) wiki-only (a wiki delta IS a retro
# product — demanding a retro for the retro is a loop; bit live 2026-08-25
# twice: churn ping-pong, then wiki-delta ping-pong).
if [ -f "$SENT" ]; then
  LAST="$(cat "$SENT")"
  NONEXEMPT=0
  for C in $(cd "$REPO_ROOT" && git rev-list "$LAST..HEAD" 2>/dev/null); do
    SUBJ="$(cd "$REPO_ROOT" && git log -1 --format=%s "$C")"
    case "$SUBJ" in "gitnexus index-stamp churn"*) continue;; esac
    FILES="$(cd "$REPO_ROOT" && git diff-tree --no-commit-id --name-only -r "$C")"
    if [ -n "$FILES" ] && [ -z "$(echo "$FILES" | grep -v '^wiki/')" ]; then
      continue
    fi
    NONEXEMPT=1; break
  done
  if [ "$NONEXEMPT" = 0 ] && [ -n "$(cd "$REPO_ROOT" && git rev-list "$LAST..HEAD" 2>/dev/null)" ]; then
    echo "$HEAD_SHA" > "$SENT"
    exit 0
  fi
fi
echo "$HEAD_SHA" > "$SENT"

WIKI_LINE="wiki: FRESH"
if [ -f "$REPO_ROOT/.git/wiki-stale" ]; then
  WIKI_LINE="wiki: STALE since $(cat "$REPO_ROOT/.git/wiki-stale") — land the delta (live-state.md at minimum)"
fi

cat >&2 <<EOF
TURN-END RETRO (once per landed batch; answer by doing, or state "retro: nothing to bake" explicitly):
1. $WIKI_LINE — is live-state.md still accurate after this turn's work?
2. Bugs/wrinkles found this turn: did each get /bug-echo, a registry row, and (if greppable) an AP_SCREEN entry?
3. Nuance worth keeping that ISN'T a bug: does any skill (build-loop / orchestration / deep-work / session-continuity / vendor-first / code-intel-trio) deserve the lesson baked in NOW, same increment?
4. Next-time-easier: is there a script/hook/doc that would have made this turn's task trivial? If cheap, build it; if not, register it as a task.
5. Luck lens (skill \`luck\`, workflow only): did this batch make the SETUP more solvent/circulating/integrated (lessons baked where the next task finds them, telemetry feeding back, parts newly connected) — or did something land as a one-off that will pool and decay?
EOF
exit 2
