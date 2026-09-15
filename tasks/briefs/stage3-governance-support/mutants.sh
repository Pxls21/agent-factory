#!/usr/bin/env bash
# GOV1 mutation driver. Each mutant must make the focused deterministic test red.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PY="${PYTHON:-python3}"
WORK="${GOV1_MUTANT_TMP:-$(mktemp -d)}"
CONTROL=0
EXPECTED=12
KILLED=0
SURVIVED=0
INVALID=0
trap 'rm -rf "$WORK"' EXIT

FILES=(
  src/agent_factory/governance/packet.py
  src/agent_factory/governance/projection.py
  src/agent_factory/governance/bounds.py
  src/agent_factory/governance/pin.py
  src/agent_factory/audit/events.py
  tests/test_governance_packet.py
  tests/test_governance_projection.py
  tests/test_governance_bounds.py
  tests/test_governance_pin.py
  tests/test_audit_events.py
)

export FUBUKI_OS_ROOT="${FUBUKI_OS_ROOT:?FUBUKI_OS_ROOT is required}"
export FUBUKI_OTHER_ROOT="${FUBUKI_OTHER_ROOT:?FUBUKI_OTHER_ROOT is required}"
# The upstream is NOT on PYTHONPATH: the tests reach it through verify_pinned_fubuki (the
# production path insertion). An ambient upstream path masked the root-insertion mutant.
export PYTHONPATH="$ROOT/src"

if ! "$PY" -m py_compile "${FILES[@]/#/$ROOT/}"; then
  echo "INVALID: baseline py_compile failed"
  exit 1
fi
if ! "$PY" -m pytest --collect-only -q -p no:cacheprovider \
  "$ROOT"/tests/test_governance_*.py "$ROOT/tests/test_audit_events.py" >/dev/null; then
  echo "INVALID: baseline collection failed"
  exit 1
fi
if "$PY" -m pytest -q -p no:cacheprovider \
  "$ROOT"/tests/test_governance_*.py "$ROOT/tests/test_audit_events.py" >/dev/null; then
  CONTROL=1
else
  echo "INVALID: baseline tests failed"
  exit 1
fi

run_mutant() {
  name="$1" file="$2" old="$3" new="$4" test="$5"
  mutant="$WORK/$name"
  mutant_test="$mutant/$test"
  test_file="${test%%::*}"
  test_node="${test#*::}"
  mkdir -p "$mutant/src/agent_factory/governance" "$mutant/src/agent_factory/audit" "$(dirname "$mutant_test")"
  cp -a "$ROOT/src/agent_factory/." "$mutant/src/agent_factory/"
  cp "$ROOT/$test_file" "$mutant/$test_file"
  target="$mutant/$file"
  "$PY" - "$target" "$old" "$new" <<'PY'
import sys
from pathlib import Path
path = Path(sys.argv[1]); old = sys.argv[2]; new = sys.argv[3]
text = path.read_text()
if text.count(old) != 1:
    raise SystemExit(3)
path.write_text(text.replace(old, new))
PY
  patch_rc=$?
  if [ "$patch_rc" -ne 0 ] || ! "$PY" -m py_compile "$target"; then
    INVALID=$((INVALID+1)); echo "INVALID $name"; return
  fi
  if (cd "$mutant" && PYTHONPATH="$mutant/src" \
      "$PY" -m pytest --import-mode=importlib -q -p no:cacheprovider "$test_file::$test_node" >/dev/null 2>&1); then
    SURVIVED=$((SURVIVED+1)); echo "SURVIVED $name"
  else
    KILLED=$((KILLED+1)); echo "KILLED $name"
  fi
}

run_mutant lint-violation-becomes-review src/agent_factory/governance/packet.py \
  'if "VIOLATION" in tiers:' 'if "NEVER" in tiers:' \
  tests/test_governance_packet.py::test_lint_exit_semantics
run_mutant hash-subset src/agent_factory/governance/packet.py \
  'return hashlib.sha256(canonical_bytes).hexdigest()' 'return hashlib.sha256(canonical_bytes[:1]).hexdigest()' \
  tests/test_governance_packet.py::test_compile_is_canonical_and_hash_is_exact_sha256
run_mutant hash-not-canonical-bytes src/agent_factory/governance/packet.py \
  'return hashlib.sha256(canonical_bytes).hexdigest()' 'return hashlib.sha256(repr(json.loads(canonical_bytes)).encode()).hexdigest()' \
  tests/test_governance_packet.py::test_compile_is_canonical_and_hash_is_exact_sha256
run_mutant join-reads-payload src/agent_factory/governance/bounds.py \
  'kept.append(by_id[record_id])' 'kept.append(getattr(decision, "payload", by_id[record_id]))' \
  tests/test_governance_bounds.py::test_bound_join_never_reads_planted_decision_payload
run_mutant projection-plain-dict src/agent_factory/governance/projection.py \
  'return MappingProxyType({key: _freeze(item) for key, item in value.items()})' 'return {key: _freeze(item) for key, item in value.items()}' \
  tests/test_governance_projection.py::test_projection_is_deeply_immutable_and_selective
run_mutant projection-no-excl src/agent_factory/governance/projection.py \
  '| os.O_EXCL' '| os.O_TRUNC' \
  tests/test_governance_projection.py::test_projection_refuses_hash_mismatch_and_existing_path
run_mutant projection-skip-envelope-hash src/agent_factory/governance/projection.py \
  'if not isinstance(projection_hash, str) or not hashlib.sha256(body_bytes).hexdigest() == projection_hash:' 'if not isinstance(projection_hash, str):' \
  tests/test_governance_projection.py::test_projection_document_hash_covers_every_byte
run_mutant event-allows-empty-reason src/agent_factory/audit/events.py \
  'if not isinstance(self.reason, str) or not self.reason.strip():' 'if not isinstance(self.reason, str):' \
  tests/test_audit_events.py::test_event_requires_reason
run_mutant pin-skips-commit src/agent_factory/governance/pin.py \
  'if actual != expected:' 'if False and actual != expected:' \
  tests/test_governance_pin.py::test_other_commit_refuses_by_name
run_mutant projection-follow-symlink src/agent_factory/governance/projection.py \
  '        | getattr(os, "O_NOFOLLOW", 0)' '        | 0' \
  tests/test_governance_projection.py::test_projection_refuses_symlink_before_write
run_mutant audit-follow-symlink src/agent_factory/audit/events.py \
  '| getattr(os, "O_NOFOLLOW", 0)' '| 0' \
  tests/test_audit_events.py::test_jsonl_sink_refuses_symlink
run_mutant pin-skips-root-insert src/agent_factory/governance/pin.py \
  'for entry in (str(root), str(root / "src")):' 'for entry in (str(root / "src"),):' \
  tests/test_governance_pin.py::test_pinned_upstream_modules_resolve_from_the_pinned_checkout

echo "EXPECTED=$EXPECTED KILLED=$KILLED SURVIVED=$SURVIVED INVALID=$INVALID CONTROL=$CONTROL"
[ "$KILLED" -eq "$EXPECTED" ] && [ "$SURVIVED" -eq 0 ] && [ "$INVALID" -eq 0 ] && [ "$CONTROL" -eq 1 ]
