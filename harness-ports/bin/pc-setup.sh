#!/usr/bin/env bash
# pc-setup.sh — bring the PC up as the BUILD host for Hermes lanes (owner ruling 2026-09-03).
# The PC-side sibling of scripts/setup.sh: user-level, no sudo, idempotent, tolerant (an
# optional install that fails WARNs and the script continues). Mirrors what the sandbox
# session-start rebuilds, at PC paths:
#   AF_REPO   clone of this repo                default $HOME/agent-factory
#   AF_VENV   project venv (pyflakes/pytest/aleph) default $HOME/venv-agent-factory
#   CRG_VENV  code-review-graph venv           default $HOME/venv-crg
#   SLOPO_VENV slopo + its embed server's venv default $HOME/venv-slopo
# Also installs the advisory instruments (sentrux, ripwire digest-pinned into ~/.local/bin; slopo into its own venv with
# its pinned embedding model under $AF_REPO/.slopo-runtime/model), builds the code-review-graph
# and codebase-memory graphs, and refreshes a graft/gitnexus index that is older than HEAD (owner directive 2026-09-07:
# every instrument runs on the PC too — scripts/lane_context.sh must work here for the build lanes).
# Heavy index builds (gitnexus analyze, graft build) run DETACHED at the end — they outlive
# any bridge call; watch $AF_REPO/.lanes/pc-setup.log and the two index logs.
# Run it over the bridge detached:  nohup bash harness-ports/bin/pc-setup.sh > .lanes/pc-setup.log 2>&1 &
set -uo pipefail
: "${AF_REPO:=$HOME/agent-factory}"; : "${AF_VENV:=$HOME/venv-agent-factory}"; : "${CRG_VENV:=$HOME/venv-crg}"
: "${SLOPO_VENV:=$HOME/venv-slopo}"
export DO_NOT_TRACK=1
ok()   { echo "  ✓ $*"; }
warn() { echo "  ⚠ $*"; }
say()  { echo "== $* =="; }
PY311="$(command -v python3.11 || command -v python3)"
mkdir -p "$AF_REPO/.lanes" "$HOME/.local/bin"
cd "$AF_REPO" || { echo "no clone at $AF_REPO" >&2; exit 1; }
echo "pc-setup start $(date -u +%FT%TZ) on $(hostname) repo=$AF_REPO head=$(git log -1 --format=%h)"

say "git hooks"
git config core.hooksPath scripts/hooks && ok "core.hooksPath=scripts/hooks"

say "project venv ($AF_VENV)"
[ -x "$AF_VENV/bin/python" ] || "$PY311" -m venv "$AF_VENV" || warn "venv create failed"
if [ -x "$AF_VENV/bin/python" ]; then
  if [ -f "$AF_REPO/pyproject.toml" ]; then "$AF_VENV/bin/pip" install -q -e "$AF_REPO" >/dev/null 2>&1 && ok "agent-factory editable" || warn "agent-factory editable install failed"; fi
  # the pinned fubuki-os + its negative control (DECLARED inputs of the governance tests; scripts/pc_suite.sh exports them)
  bash "$AF_REPO/scripts/fubuki_pin_sync.sh" "$HOME/fubuki-pin" >/dev/null 2>&1 && ok "fubuki-os pinned checkout + negative control ($HOME/fubuki-pin)" || warn "fubuki_pin_sync failed — the governance tests fail by design until $HOME/fubuki-pin is provisioned"
  "$AF_VENV/bin/pip" install -q --upgrade pip >/dev/null 2>&1
  "$AF_VENV/bin/pip" install -q pyflakes pytest pytest-xdist "PyYAML>=6.0" "jsonschema==4.25.1" "rfc3339-validator==0.1.4" "mcp==1.29.1" >/dev/null 2>&1 && ok "pyflakes pytest pytest-xdist PyYAML jsonschema==4.25.1 rfc3339-validator==0.1.4 mcp==1.29.1" || warn "base pip install failed"
  "$AF_VENV/bin/pip" install -q -e "$AF_REPO/sandbox-kit/aleph[mcp]" >/dev/null 2>&1 && ok "aleph (editable, [mcp])" || warn "aleph install failed"
  "$AF_VENV/bin/python" -c "from mcp.server.fastmcp import FastMCP" 2>/dev/null && ok "mcp v1 API present" || warn "mcp v1 API missing — aleph MCP server will not start"
fi

say "node tools (npm prefix $(npm config get prefix 2>/dev/null))"
# Pin gitnexus to the sandbox version (1.6.10): the PC carried a pre-existing 1.3.9 whose index
# layout (.gitnexus/run.cjs, flat gitnexus-* skills) differs from what the skills describe.
GN_WANT=1.6.10; GN_HAVE="$(gitnexus --version 2>/dev/null | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)"
if [ "$GN_HAVE" != "$GN_WANT" ]; then
  npm i -g --ignore-scripts "gitnexus@$GN_WANT" >/dev/null 2>&1 && npm rebuild -g @ladybugdb/core >/dev/null 2>&1 \
    && ok "gitnexus $GN_WANT installed (was ${GN_HAVE:-absent})" || warn "gitnexus $GN_WANT install failed (have ${GN_HAVE:-none})"
else ok "gitnexus $GN_HAVE"; fi
command -v graft >/dev/null 2>&1 || npm install -g @nanonets/graft@0.16.0 >/dev/null 2>&1
command -v graft >/dev/null 2>&1 && { graft telemetry disable >/dev/null 2>&1; ok "graft $(graft --version 2>/dev/null | head -1)"; } || warn "graft not installed"

say "codebase-memory-mcp (prebuilt)"
if [ -x "$HOME/.local/bin/codebase-memory-mcp" ]; then ok "binary present"
elif [ -f "$AF_REPO/sandbox-kit/codebase-memory-mcp/install.sh" ]; then
  bash "$AF_REPO/sandbox-kit/codebase-memory-mcp/install.sh" --dir="$HOME/.local/bin" >/dev/null 2>&1 && ok "installed" || warn "prebuilt install failed"
else warn "no install.sh"; fi

say "code-review-graph ($CRG_VENV)"
[ -x "$CRG_VENV/bin/code-review-graph" ] || { "$PY311" -m venv "$CRG_VENV" && "$CRG_VENV/bin/pip" install -q code-review-graph >/dev/null 2>&1; }
[ -x "$CRG_VENV/bin/code-review-graph" ] && ok "present" || warn "install failed"

say "sentrux + ripwire (advisory instruments, digest-pinned — the same pins as scripts/setup.sh; binary only)"
# Owner directive 2026-09-07: EVERY instrument runs on the PC too (the build lanes live here). User-level, no sudo.
SENTRUX_VER="v0.5.7"
SENTRUX_BIN_SHA="3237f80fe20d54aad4deefa8a143f0d60543bb5d2d6ad891eb42432f155725a6"
SENTRUX_GRAM_SHA="8849f1eb07df3f6d4ea1ed422d8dee4b9b79a250682fa5646675dae466554454"
RIPWIRE_VER="v0.4.0"
RIPWIRE_ASSET_SHA="fd0bd0fa849c0e08db59a6a7e5c2d3e9bc062d3089b54196daf9332cd21bbfc8"
RIPWIRE_BIN_SHA="6a1957b829f74e29b16caf550e90ea5504afa3ebd200c0b253f2f3afaae76aa3"
TMPD="$(mktemp -d)"
if [ -x "$HOME/.local/bin/sentrux" ] && [ "$(sha256sum "$HOME/.local/bin/sentrux" | cut -d" " -f1)" = "$SENTRUX_BIN_SHA" ]; then
  ok "sentrux $SENTRUX_VER present (digest verified)"
elif curl -fsSL -m 300 -o "$TMPD/sentrux" "https://github.com/sentrux/sentrux/releases/download/$SENTRUX_VER/sentrux-linux-x86_64" \
     && [ "$(sha256sum "$TMPD/sentrux" | cut -d" " -f1)" = "$SENTRUX_BIN_SHA" ]; then
  install -m 0755 "$TMPD/sentrux" "$HOME/.local/bin/sentrux" && ok "sentrux $SENTRUX_VER installed (digest verified)"
else warn "sentrux: download or digest check failed"; fi
if [ -x "$HOME/.local/bin/sentrux" ] && [ ! -d "$HOME/.sentrux/plugins/python" ]; then
  if curl -fsSL -m 300 -o "$TMPD/grammars.tgz" "https://github.com/sentrux/sentrux/releases/download/$SENTRUX_VER/grammars-linux-x86_64.tar.gz" \
     && [ "$(sha256sum "$TMPD/grammars.tgz" | cut -d" " -f1)" = "$SENTRUX_GRAM_SHA" ]; then
    mkdir -p "$HOME/.sentrux/plugins" && tar xzf "$TMPD/grammars.tgz" -C "$HOME/.sentrux/plugins" && ok "sentrux grammars unpacked (digest verified)"
  else warn "sentrux grammars: download or digest check failed"; fi
fi
[ -x "$HOME/.local/bin/sentrux" ] && SENTRUX_DEV=1 SENTRUX_SKIP_GRAMMAR_DOWNLOAD=1 "$HOME/.local/bin/sentrux" analytics off >/dev/null 2>&1 || true
if [ -x "$HOME/.local/bin/ripwire" ] && [ "$(sha256sum "$HOME/.local/bin/ripwire" | cut -d" " -f1)" = "$RIPWIRE_BIN_SHA" ]; then
  ok "ripwire $RIPWIRE_VER present (digest verified)"
elif curl -fsSL -m 300 -o "$TMPD/ripwire.tar.gz" "https://github.com/redhat-et/ripwire/releases/download/$RIPWIRE_VER/ripwire-${RIPWIRE_VER#v}-linux-x64.tar.gz" \
     && [ "$(sha256sum "$TMPD/ripwire.tar.gz" | cut -d" " -f1)" = "$RIPWIRE_ASSET_SHA" ] \
     && tar xzf "$TMPD/ripwire.tar.gz" -C "$TMPD" --strip-components=1 "ripwire-${RIPWIRE_VER#v}-linux-x64/ripwire" \
     && [ "$(sha256sum "$TMPD/ripwire" | cut -d" " -f1)" = "$RIPWIRE_BIN_SHA" ]; then
  install -m 0755 "$TMPD/ripwire" "$HOME/.local/bin/ripwire" && ok "ripwire $RIPWIRE_VER installed (digest verified; binary only — the bundled skills/hooks are never installed)"
else warn "ripwire: download, asset or binary digest check failed"; fi
rm -rf "$TMPD"

say "slopo (advisory semantic-duplicate detector; the same pins as scripts/setup.sh)"
# INSTALL1 (D-090): slopo 0.6.0 (AGPL-3.0-or-later: its own venv, never vendored) plus the embed server's runtime, and
# the embedding model. The wheel and the two model files are digest-checked; each installs only when absent or wrong,
# and only while 1 GB of disk stays free after it. Python 3.12 or later (Fedora 42's python3 is 3.13).
SLOPO_WHEEL="slopo-0.6.0-py3-none-any.whl"
SLOPO_WHEEL_URL="https://files.pythonhosted.org/packages/97/6e/be36bed69c636ffddabc9c41f8738303f28e47ad50529a8f412604414e1c/$SLOPO_WHEEL"
SLOPO_WHEEL_SHA="ec9d2dd8c5e152c5f1e7cb1d88e25f44b215e3bef308a282a8a9259f5ec6105b"
SLOPO_SERVER_PINS="onnxruntime==1.30.0 tokenizers==0.23.2 fastapi==0.141.1 uvicorn==0.54.0"
JINA_URL="https://huggingface.co/jinaai/jina-embeddings-v2-base-code/resolve/516f4baf13dec4ddddda8631e019b5737c8bc250"
JINA_FILES="onnx/model_quantized.onnx=ed45870251c9f0cf656e78aab0d37a23489066df8a222bb1c8caf8a45f2cb16d"
JINA_FILES+=" tokenizer.json=b01c78a902aa4facb2f47f95449f48e2f7bbfea5d2472ee2f6ce92323c6f86e5"
room_for() { [ "$(df -Pm "$1" | awk 'NR==2 {print $4}')" -ge $((1024 + $2)) ]; }   # room_for DIR MB: 1 GB stays free
sha_is() { [ -f "$1" ] && [ "$(sha256sum "$1" | cut -d" " -f1)" = "$2" ]; }
PY312=""
for c in python3.12 python3.13 python3; do
  command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(sys.version_info < (3, 12))' && { PY312="$(command -v "$c")"; break; }
done
slopo_ok() {   # the pinned slopo answers and the server's runtime imports. No `| grep -q` here: under pipefail it
  local v      # breaks slopo's pipe after the first line, fails, and every run rebuilt the venv (INSTALL1, found live)
  v="$("$SLOPO_VENV/bin/slopo" --version 2>/dev/null)" || return 1
  [ "${v%%$'\n'*}" = "Slopo 0.6.0" ] && "$SLOPO_VENV/bin/python" -c "import onnxruntime, tokenizers, fastapi, uvicorn" 2>/dev/null
}
if slopo_ok; then
  ok "slopo 0.6.0 present ($SLOPO_VENV)"
elif [ -z "$PY312" ]; then warn "slopo: no Python 3.12 or later"
elif ! room_for "$HOME" 600; then warn "slopo: under 1.6 GB free — install skipped"
else
  TMPD="$(mktemp -d)"
  # shellcheck disable=SC2086  # SLOPO_SERVER_PINS is a list of requirement words
  if curl -fsSL -m 300 -o "$TMPD/$SLOPO_WHEEL" "$SLOPO_WHEEL_URL" && sha_is "$TMPD/$SLOPO_WHEEL" "$SLOPO_WHEEL_SHA" \
     && rm -rf "$SLOPO_VENV" && "$PY312" -m venv "$SLOPO_VENV" \
     && "$SLOPO_VENV/bin/pip" install -q --no-cache-dir "$TMPD/$SLOPO_WHEEL" $SLOPO_SERVER_PINS >/dev/null 2>&1 \
     && cp "$TMPD/$SLOPO_WHEEL" "$SLOPO_VENV/$SLOPO_WHEEL"; then
    ok "slopo 0.6.0 installed into $SLOPO_VENV with $PY312 (wheel digest verified)"
  else warn "slopo: download, digest check, venv or pip install failed"; fi
  rm -rf "$TMPD"
fi
[ -x "$SLOPO_VENV/bin/slopo" ] && ln -sfn "$SLOPO_VENV/bin/slopo" "$HOME/.local/bin/slopo"
mkdir -p "$AF_REPO/.slopo-runtime/model"; jina_ok=0
for spec in $JINA_FILES; do
  f="${spec%%=*}"; sha="${spec#*=}"; dest="$AF_REPO/.slopo-runtime/model/${f##*/}"
  if ! sha_is "$dest" "$sha"; then
    room_for "$AF_REPO" 200 || { warn "slopo model: under 1.2 GB free — ${f##*/} not downloaded"; continue; }
    if curl -fsSL -m 900 -o "$dest.part" "$JINA_URL/$f" && sha_is "$dest.part" "$sha"; then mv -f "$dest.part" "$dest"
    else rm -f "$dest.part"; warn "slopo model: ${f##*/} download or digest check failed"; continue; fi
  fi
  jina_ok=$((jina_ok+1))
done
[ "$jina_ok" -eq 2 ] && ok "slopo model present ($AF_REPO/.slopo-runtime/model, digests verified)"
say "ouroboros (uv tool)"
command -v ouroboros >/dev/null 2>&1 || uv tool install ouroboros-ai==0.53.0 >/dev/null 2>&1
if command -v ouroboros >/dev/null 2>&1; then
  ok "ouroboros $(ouroboros --version 2>/dev/null | head -1)"
  OOO_PY="$HOME/.local/share/uv/tools/ouroboros-ai/bin/python"
  [ -x "$OOO_PY" ] && "$OOO_PY" "$AF_REPO/scripts/patch_ouroboros.py" >/dev/null 2>&1 && ok "patches applied" || warn "patch_ouroboros skipped"
else warn "ouroboros not installed"; fi

say "harness-port checks"
bash harness-ports/bin/sync-skills.sh --check >/dev/null 2>&1 && ok "skills in sync" || warn "skills drift — run harness-ports/bin/sync-skills.sh"
"$PY311" harness-ports/bin/build-roles.py --check >/dev/null 2>&1 && ok "roles match" || warn "roles drift — run build-roles.py"

say "indexes (detached)"
if command -v gitnexus >/dev/null 2>&1 && [ ! -f .gitnexus/run.cjs ]; then
  ( flock -n 9 || exit 0; nohup gitnexus analyze --skip-agents-md > .lanes/gitnexus-analyze.log 2>&1 ) 9>.lanes/gitnexus-analyze.lock & ok "gitnexus analyze launched (.lanes/gitnexus-analyze.log)"
else ok "gitnexus index present or tool absent"; fi
if command -v graft >/dev/null 2>&1 && [ ! -f graft/INDEX.md ]; then
  ( flock -n 9 || exit 0; nohup graft build > .lanes/graft-build.log 2>&1 ) 9>.lanes/graft-build.lock & ok "graft build launched (.lanes/graft-build.log)"
else ok "graft index present or tool absent"; fi
# The other two quartet graphs (owner directive 2026-09-07: the instruments run on the PC too). code-review-graph builds
# its graph when absent (~80 s here); codebase-memory indexes the clone in fast mode when its project DB is absent
# (the DB is per-machine under ~/.cache/codebase-memory-mcp/). A STALE graft/gitnexus index (older than HEAD's commit)
# is refreshed the same detached way — the post-commit hook keeps them fresh only for commits made ON this machine,
# and lanes here build on commits fetched from origin.
if [ -x "$CRG_VENV/bin/code-review-graph" ] && [ ! -f .code-review-graph/graph.db ]; then
  ( flock -n 9 || exit 0; nohup "$CRG_VENV/bin/code-review-graph" build > .lanes/crg-build.log 2>&1 ) 9>.lanes/crg-build.lock & ok "code-review-graph build launched (.lanes/crg-build.log)"
else ok "code-review-graph graph present or tool absent"; fi
if [ -x "$HOME/.local/bin/codebase-memory-mcp" ] && ! ls "$HOME/.cache/codebase-memory-mcp/"*agent-factory*.db >/dev/null 2>&1; then
  ( flock -n 9 || exit 0; nohup "$HOME/.local/bin/codebase-memory-mcp" cli index_repository --repo-path "$AF_REPO" --mode fast > .lanes/cbm-index.log 2>&1 ) 9>.lanes/cbm-index.lock & ok "codebase-memory index launched (.lanes/cbm-index.log)"
else ok "codebase-memory index present or tool absent"; fi
HEAD_T="$(git log -1 --format=%ct)"
if command -v gitnexus >/dev/null 2>&1 && [ -f .gitnexus/run.cjs ] && [ "$(stat -c %Y .gitnexus/run.cjs)" -lt "$HEAD_T" ]; then
  ( flock -n 9 || exit 0; nohup gitnexus analyze --skip-agents-md > .lanes/gitnexus-analyze.log 2>&1 ) 9>.lanes/gitnexus-analyze.lock & ok "gitnexus index older than HEAD — analyze relaunched"
fi
if command -v graft >/dev/null 2>&1 && [ -f graft/INDEX.md ] && [ "$(stat -c %Y graft/INDEX.md)" -lt "$HEAD_T" ]; then
  ( flock -n 9 || exit 0; nohup graft build > .lanes/graft-build.log 2>&1 ) 9>.lanes/graft-build.lock & ok "graft index older than HEAD — build relaunched"
fi
echo "pc-setup done $(date -u +%FT%TZ)"
