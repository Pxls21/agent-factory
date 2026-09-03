#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"

required_files=(
  README.md
  STATUS.md
  AGENTS.md
  SECURITY.md
  upstream.lock.yaml
  docs/01_ARCHITECTURE.md
  docs/02_COMPONENT_AUDIT.md
  docs/03_INTEGRATION_CONTRACTS.md
  docs/04_MEMORY_AND_GOVERNANCE.md
  docs/05_SECURITY.md
  docs/06_EVALUATION.md
  docs/07_BUILD_PLAN.md
  docs/08_DECISION_LOG.md
  docs/09_PREMORTEM.md
  docs/10_HARNESS_FOUNDRY.md
  docs/11_DREAM_PHASE.md
  config/hermes/config.yaml.example
  config/ai-memory/config.toml.example
  deploy/topology.blueprint.yaml
)

for relative_path in "${required_files[@]}"; do
  test -s "${repo_root}/${relative_path}" || {
    echo "missing or empty: ${relative_path}" >&2
    exit 1
  }
done

archive_dir="${repo_root}/docs/archive/v2-original"
archive_count="$(find "${archive_dir}" -maxdepth 1 -type f -name '[0-9][0-9]_*.md' | wc -l | tr -d ' ')"
test "${archive_count}" = "14" || {
  echo "expected 14 archived source documents, found ${archive_count}" >&2
  exit 1
}

(
  cd "${archive_dir}"
  sha256sum --check SHA256SUMS
)

if grep -rn -E '(codex-acp|claude-agent-acp|pi-acp)' "${repo_root}/config"; then
  echo "an excluded stock runtime adapter appears in active config/deployment files" >&2
  exit 1
fi

if ! grep -q 'BUZZ_ACP_AGENT_COMMAND=hermes-acp' "${repo_root}/.env.example"; then
  echo "buzz-acp is not configured to launch Hermes native ACP" >&2
  exit 1
fi

if ! grep -q 'role: sole_stock_production_workhorse' \
  "${repo_root}/deploy/topology.blueprint.yaml"; then
  echo "Hermes sole-workhorse invariant is missing from the deployment blueprint" >&2
  exit 1
fi

if git -C "${repo_root}" rev-parse --git-dir >/dev/null 2>&1; then
  git -C "${repo_root}" diff --check
fi

echo "planning repository verification passed"
