#!/usr/bin/env bash
# Install the vendored llm-wiki-compiler plugin into ~/.claude (council-style: commands + skill
# copied in; slash commands load next session). ${CLAUDE_PLUGIN_ROOT} references are rewritten to
# this vendored plugin directory's absolute path so templates/adapters/visualizer resolve.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="${SCRIPT_DIR}/plugin"
CLAUDE_DIR="${1:-${HOME}/.claude}"

[[ -d "${PLUGIN_ROOT}/commands" ]] || { echo "Error: ${PLUGIN_ROOT}/commands not found" >&2; exit 1; }

CMD_DEST="${CLAUDE_DIR}/commands"
SKILL_DEST="${CLAUDE_DIR}/skills/wiki-compiler"
mkdir -p "${CMD_DEST}" "${SKILL_DEST}"

n=0
for f in "${PLUGIN_ROOT}"/commands/*.md; do
  # Rewrite the plugin-root placeholder to the vendored absolute path.
  sed "s|\${CLAUDE_PLUGIN_ROOT}|${PLUGIN_ROOT}|g" "$f" > "${CMD_DEST}/$(basename "$f")"
  ((n+=1))
done

# Skill dir (SKILL.md + adapters), same rewrite.
mkdir -p "${SKILL_DEST}/adapters"
sed "s|\${CLAUDE_PLUGIN_ROOT}|${PLUGIN_ROOT}|g" \
  "${PLUGIN_ROOT}/skills/wiki-compiler/SKILL.md" > "${SKILL_DEST}/SKILL.md"
for f in "${PLUGIN_ROOT}"/skills/wiki-compiler/adapters/*.md; do
  sed "s|\${CLAUDE_PLUGIN_ROOT}|${PLUGIN_ROOT}|g" "$f" > "${SKILL_DEST}/adapters/$(basename "$f")"
done

echo "Installed ${n} wiki commands -> ${CMD_DEST}; skill -> ${SKILL_DEST}"
echo "Plugin root: ${PLUGIN_ROOT} (visualizer: node ${PLUGIN_ROOT}/visualize/server.js --wiki-dir wiki)"
echo "Restart the CLI for /wiki-* commands to load."
