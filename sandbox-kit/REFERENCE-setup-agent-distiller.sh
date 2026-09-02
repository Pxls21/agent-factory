# REFERENCE ONLY — not run as-is. Copied verbatim from pxls21/agent-distiller
# (branch claude/project-setup-access-rjmun7) scripts/setup.sh, 2026-07-07. Installs that repo's
# specific toolchain (GitNexus, Ouroboros, DataFlow/SkillOpt, tree-sitter, etc.) — trading-system's
# own scripts/setup.sh is the minimal bootstrap actually used here.
#!/usr/bin/env bash
# agent-distiller environment setup.
#
# The dev container is ephemeral — global installs vanish on reclaim — so this
# script is the source of truth for the toolchain and is safe to re-run.
# It is verified-accurate as of 2026-06-15 (see docs/STACK.md).
#
# Usage:  bash scripts/setup.sh [--full]
#   (no args) installs Ouroboros + the Python tools (the build essentials).
#   --full    also installs scala-cli and astonish.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$REPO_ROOT/.venv"
FULL=false

# Git identity — container restarts wipe local config, which made post-restart commits show as
# Unverified on GitHub (committer email != noreply@anthropic.com). Re-assert it every session.
git -C "$REPO_ROOT" config user.email noreply@anthropic.com 2>/dev/null || true
git -C "$REPO_ROOT" config user.name  Claude 2>/dev/null || true
[ "${1:-}" = "--full" ] && FULL=true

say()  { printf '\n\033[1;34m◆ %s\033[0m\n' "$*"; }
ok()   { printf '  \033[1;32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[1;33m!\033[0m %s\n' "$*"; }

# --- System packages -------------------------------------------------------
# bubblewrap backs skill2workflow.isolation; without it confinement_available()
# is False and real-trace gate validation/lift FAILS CLOSED. Gone on reclaim.
say "System packages"
if command -v bwrap >/dev/null 2>&1; then
  ok "bubblewrap present"
else
  apt-get install -y bubblewrap >/dev/null 2>&1 \
    && ok "bubblewrap installed (isolation confinement)" \
    || warn "bubblewrap install failed — real-trace validation will fail closed"
fi

# --- Ouroboros (build orchestrator) ----------------------------------------
say "Ouroboros"
if command -v ouroboros >/dev/null 2>&1 || command -v ooo >/dev/null 2>&1; then
  ok "already installed ($(ouroboros --version 2>/dev/null || echo present))"
else
  OUROBOROS_INSTALL_RUNTIME=claude \
    curl -fsSL https://raw.githubusercontent.com/Q00/ouroboros/main/scripts/install.sh | bash \
    && ok "installed" || warn "Ouroboros install failed"
fi

# Patch a known ooo bounded-auto bug (see sandbox-kit/OUROBOROS-SETUP.md):
# same-key conservative-default self-conflicts block interview closure. The
# patcher is idempotent and runs in the interpreter that owns the ooo install.
if [ -f "$REPO_ROOT/scripts/patch_ouroboros.py" ]; then
  OOO_PY="$(command -v ooo-python 2>/dev/null || echo /root/.local/share/uv/tools/ouroboros-ai/bin/python)"
  [ -x "$OOO_PY" ] || OOO_PY="$(command -v python3)"
  "$OOO_PY" "$REPO_ROOT/scripts/patch_ouroboros.py" \
    && ok "ooo ledger patch applied" || warn "ooo patch skipped/failed"
fi

# Register the Ouroboros MCP server against the LOCAL binary. The plugin ships an
# .mcp.json that launches it via `uvx --from ouroboros-ai[mcp,claude]`, which
# RE-RESOLVES the package from PyPI at startup — blocked by this sandbox's network
# policy (the resolver only sees stale 0.1–0.7 versions), so the plugin server
# fails to connect and the MCP interview/seed tools never load. The already-installed
# `ouroboros` binary serves fine, so point a user-scope server at it. Idempotent.
# NOTE: MCP servers connect at Claude Code session START, so this takes effect on the
# NEXT session, not the one running setup.sh. (see sandbox-kit/OUROBOROS-SETUP.md §8)
if command -v claude >/dev/null 2>&1 && command -v ouroboros >/dev/null 2>&1; then
  claude mcp remove ouroboros --scope user >/dev/null 2>&1 || true
  if claude mcp add ouroboros --scope user -- ouroboros mcp serve >/dev/null 2>&1; then
    ok "ouroboros MCP server registered (local binary; loads next session)"
  else
    warn "ouroboros MCP registration failed (use 'ooo auto' headless instead)"
  fi
fi

# --- Python pipeline tools (DataFlow, SkillOpt, hive) -----------------------
# A project venv keeps these isolated and reproducible.
say "Python tools (.venv)"
if command -v uv >/dev/null 2>&1; then
  [ -d "$VENV" ] || uv venv "$VENV" >/dev/null
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
  uv pip install -q open-dataflow skillopt \
    && ok "open-dataflow + skillopt" || warn "DataFlow/SkillOpt install failed"
  # hive is not published; install from source. rust-brain may need a Rust
  # toolchain — the pure-python rule_fast path works without it.
  uv pip install -q "git+https://github.com/DJLougen/hive.git" \
    && ok "hive-agent-memory (source)" \
    || warn "hive build failed (rust-brain may need cargo; rule_fast still usable)"
  # Phase 2 skill->workflow deps: pm4py = WF-net soundness gate, simpleeval =
  # sandboxed branch predicates, jsonschema = constrained convert/fill output.
  uv pip install -q pm4py simpleeval jsonschema \
    && ok "pm4py + simpleeval + jsonschema" || warn "Phase 2 deps install failed"
  # Data-strategy D2 normalization: RepoMap-style span selection (tree-sitter parse +
  # networkx PageRank) feeding the proposer, and MinHash/LSH near-dup dedup. tree-sitter
  # is OPTIONAL at runtime — distill_core.normalize_spans falls back to line-window
  # selection when it is absent, so the gate still works without a grammar.
  uv pip install -q "tree-sitter>=0.21" "tree-sitter-language-pack==1.9.1" networkx datasketch \
    && ok "tree-sitter + language-pack + networkx + datasketch" || warn "D2 normalization deps install failed"
else
  warn "uv not found — install uv first (https://docs.astral.sh/uv/)"
fi

# --- Phase 3 retrieval: real CPU embeddings + type gate ---------------------
# spaCy en_core_web_md is github-hosted (reachable in the sandbox) and gives real
# 300-dim word vectors on CPU — no GPU/HF needed. mypy is the type-driven gate.
say "Phase 3 deps (spaCy + en_core_web_md, numpy, mypy)"
# Primary embedder = WordLlama (real CPU sentence model; weights ship in the pip
# wheel, so it loads fully offline — no HuggingFace needed). spaCy = fallback.
# Use `uv pip` (not `python -m pip`): the uv-created .venv ships no pip, so a bare
# `python -m pip install` fails ("No module named pip") and silently skips mypy —
# the lint gate. `uv pip` installs into the active venv without needing pip there.
PYDEPS_INSTALL="python -m pip install"
command -v uv >/dev/null 2>&1 && PYDEPS_INSTALL="uv pip install"
$PYDEPS_INSTALL -q "wordllama>=0.3" "spacy>=3.7" "numpy>=1.26" "mypy>=1.8" "datasketch>=1.6" \
  && ok "wordllama + spacy + numpy + mypy" || warn "pip install failed"
# OpenTelemetry = the observability instrumentation substrate (obs/ package). The PyPI wheel fetch can be
# slow through the egress proxy, so bump uv's HTTP timeout to avoid a spurious "operation timed out".
UV_HTTP_TIMEOUT=180 $PYDEPS_INSTALL -q "opentelemetry-api>=1.42" "opentelemetry-sdk>=1.42" \
  "opentelemetry-exporter-otlp-proto-http>=1.42" \
  && ok "opentelemetry-api + opentelemetry-sdk + otlp-http (human plane)" \
  || warn "opentelemetry install failed (obs/ tests will skip)"
# Phoenix coding-agent integration: the `px` CLI (terminal access to traces/experiments/datasets/prompts).
# MCP servers (phoenix-docs + phoenix instance ops) live in .mcp.json; skills in .claude/skills/phoenix-* —
# both committed, so only the global npm CLI needs reinstalling each container. Default endpoint = the human
# plane (override with PHOENIX_HOST). Verify: `PHOENIX_HOST=https://project-mine-ultimately-examinations.trycloudflare.com px project list`.
if command -v npm >/dev/null 2>&1; then
  command -v px >/dev/null 2>&1 && ok "phoenix-cli (px) present" \
    || { npm install -g @arizeai/phoenix-cli >/dev/null 2>&1 && ok "phoenix-cli (px)" || warn "phoenix-cli install failed"; }
fi
# arize-phoenix-client: headless experiments/datasets API (scripts/phoenix_experiment.py, Stream A of
# seed-phoenix-leverage-v1). Lightweight pure-python client; not the full server.
.venv/bin/python -c "import phoenix.client" >/dev/null 2>&1 && ok "phoenix.client present" \
  || { uv pip install -q --python .venv/bin/python arize-phoenix-client >/dev/null 2>&1 && ok "phoenix.client" || warn "phoenix-client install failed"; }
# llm-keypool: OpenAI-compatible proxy pooling free-tier hosted APIs (Groq/Gemini/Cerebras/...). The
# deterministic spine needs the model ONLY at codify/GEPA generate time, so generation can run against
# this pool instead of the local GPU — no PC, no heat (distill_core.live_backend.build_keypool_backend).
# The CLI install doesn't survive container reclaim; the registered keys (SQLite at ~/.llm-keypool) don't
# either and are secrets, so they're re-added per session by hand (`llm-keypool add --provider groq -k ...`),
# never committed. Start the pool: `llm-keypool proxy` (serves http://127.0.0.1:8000/v1).
command -v llm-keypool >/dev/null 2>&1 && ok "llm-keypool (px-free model pool) present" \
  || { uv tool install "llm-keypool[all]" >/dev/null 2>&1 && ok "llm-keypool installed" \
       || warn "llm-keypool install failed (free-tier pool backend unavailable)"; }
# Patch the proxy to FORWARD reasoning_effort (it strips all params but messages/max_tokens/temperature).
# Without it the thinking qwen3.6-27b can't turn reasoning off → slow codify. Idempotent.
# MEASURED 2026-06-29 on the PC (Qwable-3.6-27b q5_k_m, MTP nextn spec-decode, RTX 3090, reasoning-budget
# 256): serving ~46.5 tok/s; one call ~4.3s/200tok; a real codify of a small practice doc (3 checks) ~27s
# wall. Latency is ~entirely LLM token generation — the gate's bash subprocess fan-out is ~1.7ms/spawn
# (negligible). (The old "~141s/codify" note was stale/pre-patch — do not use it as a benchmark.)
python3 scripts/patch_keypool.py >/dev/null 2>&1 && ok "llm-keypool reasoning_effort passthrough patched" \
  || warn "llm-keypool proxy patch skipped (reasoning_effort passthrough — codify will be slow)"
export PHOENIX_HOST="${PHOENIX_HOST:-https://project-mine-ultimately-examinations.trycloudflare.com}"
python -c "import sys; sys.path.insert(0,'.'); from distill_core.embed import load_model; m=load_model(); print(m.name)" \
  >/dev/null 2>&1 && ok "embedder loads offline ($(python -c "import sys;sys.path.insert(0,'.');from distill_core.embed import load_model;print(load_model().name)" 2>/dev/null))" \
  || warn "embedder load failed"
if ! python -c "import spacy, en_core_web_md" >/dev/null 2>&1; then
  python -m spacy download en_core_web_md >/dev/null 2>&1 \
    && ok "en_core_web_md (fallback) downloaded" || warn "en_core_web_md download skipped"
fi

# --- Council of High Intelligence (pre-research debate stage) ----------------
# Multi-persona structured-disagreement deliberation (/council). Vendored under
# sandbox-kit/; install.sh is file-copy only (no net/sudo/exec) into ~/.claude, so it
# re-installs each session (the ~/.claude install does not survive container reclaim).
# Claude-only here (one backbone); run on the PC for true multi-provider routing.
say "Council of High Intelligence"
if bash "$REPO_ROOT/sandbox-kit/council-of-high-intelligence/install.sh" >/dev/null 2>&1; then
  ok "/council installed (18 persona agents + skill -> ~/.claude; restart CLI to load)"
else
  warn "council install skipped (sandbox-kit/council-of-high-intelligence/install.sh failed)"
fi

# --- llm-wiki-compiler (codebase wiki: subsystem-level map + knowledge graph) --
# Vendored under sandbox-kit/ (MIT, ussumant/llm-wiki-compiler v2.1). File-copy only into
# ~/.claude (re-installs each session, like the council). The compiled wiki for this repo is
# committed at wiki/; /wiki-compile refreshes it, /wiki-visualize serves the knowledge graph.
say "llm-wiki-compiler"
if bash "$REPO_ROOT/sandbox-kit/llm-wiki-compiler/install.sh" >/dev/null 2>&1; then
  ok "/wiki-* installed (12 commands + skill -> ~/.claude; restart CLI to load)"
else
  warn "wiki-compiler install skipped (sandbox-kit/llm-wiki-compiler/install.sh failed)"
fi

if ! $FULL; then
  say "Done (essentials). Re-run with --full for orca/astonish toolchains."
  exit 0
fi

# NOTE: tracebase (Node ≥24 clone-and-build) used to live here. Removed: the built capture stage
# (distill_core/capture.py) hand-parses native session JSONL directly — no tracebase import anywhere
# in the codebase (see docs/STACK.md) — so cloning/building it was dead weight.

# --- Scala 3 toolchain for orca / Phase 2 (real compiler via coursier) -------
# The native scala-cli binary is UNUSABLE in this sandbox: its baked truststore
# rejects the egress-proxy MITM CA (scala-cli#2963). curl and the JVM trust it
# (via /etc/ssl/certs), so we drive a real scalac/scala through the JVM coursier
# launcher instead. On the Fedora real tier, plain scala-cli works — keep it.
say "Scala 3 toolchain (coursier + scalac/scala wrappers)"
SCALA_VER="3.3.4"
BIN="$REPO_ROOT/.tools/bin"; mkdir -p "$BIN"
CJ="$REPO_ROOT/.tools/coursier.jar"

# (1) Trust the egress-proxy CA in the JVM truststore so coursier can fetch from
#     Maven Central over the inspected TLS connection (idempotent).
JH="$(java -XshowSettings:properties 2>&1 | awk -F= '/java.home/{gsub(/ /,"",$2);print $2}')"
CACERTS="$JH/lib/security/cacerts"
if [ -w "$CACERTS" ] || [ -w "$(readlink -f "$CACERTS")" ]; then
  python3 - "$CACERTS" <<'PY' 2>/dev/null && ok "egress CA trusted in JVM truststore" || warn "could not import egress CA (Maven fetch may fail)"
import re, subprocess, sys, tempfile, os
cacerts = sys.argv[1]
bundle = open("/etc/ssl/certs/ca-certificates.crt").read()
blocks = re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", bundle, re.S)
n = 0
for i, b in enumerate(blocks):
    subj = subprocess.run(["openssl","x509","-noout","-subject"], input=b,
                          capture_output=True, text=True).stdout
    if "Anthropic" in subj or "Egress" in subj:
        with tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False) as f:
            f.write(b + "\n"); pem = f.name
        subprocess.run(["keytool","-importcert","-noprompt","-trustcacerts",
                        "-alias", f"egress-ca-{i}", "-file", pem,
                        "-keystore", cacerts, "-storepass", "changeit"],
                       capture_output=True)
        os.unlink(pem); n += 1
sys.exit(0 if n else 1)
PY
else
  warn "JVM truststore not writable; skipping egress-CA import"
fi

# (2) coursier JVM launcher (uses the JVM truststore fixed above).
if [ ! -f "$CJ" ]; then
  curl -fsSL -o "$CJ" https://github.com/coursier/coursier/releases/latest/download/coursier.jar \
    && ok "coursier.jar" || warn "coursier.jar download failed"
fi

# (3) scalac / scala wrappers on PATH (coursier caches the compiler after run 1).
cat > "$BIN/scalac" <<EOF
#!/usr/bin/env bash
exec java -jar "$CJ" launch scalac:$SCALA_VER -- "\$@"
EOF
cat > "$BIN/scala" <<EOF
#!/usr/bin/env bash
exec java -jar "$CJ" launch scala:$SCALA_VER -- "\$@"
EOF
chmod +x "$BIN/scalac" "$BIN/scala"
if "$BIN/scalac" -version >/dev/null 2>&1; then
  ok "scalac/scala $SCALA_VER ready (add .tools/bin to PATH)"
else
  warn "scalac smoke test failed (check Maven Central egress + JVM CA)"
fi
# Real-tier convenience: native scala-cli (will NOT work in this sandbox's TLS).
command -v scala-cli >/dev/null 2>&1 || \
  curl -fsSL -o "$REPO_ROOT/.tools/scala-cli.gz" \
    https://github.com/VirtusLab/scala-cli/releases/latest/download/scala-cli-x86_64-pc-linux.gz 2>/dev/null \
  && gunzip -f "$REPO_ROOT/.tools/scala-cli.gz" 2>/dev/null \
  && chmod +x "$REPO_ROOT/.tools/scala-cli" 2>/dev/null \
  && warn "scala-cli binary saved for the real tier (unused in sandbox)" || true

# --- astonish (Go YAML workflows) -------------------------------------------
say "astonish"
if command -v astonish >/dev/null 2>&1; then
  ok "already installed"
else
  curl -fsSL https://raw.githubusercontent.com/schardosin/astonish/refs/heads/main/install.sh | sh \
    && ok "installed" || warn "astonish install failed"
fi

say "Done (full). See docs/STACK.md for what each component does."
