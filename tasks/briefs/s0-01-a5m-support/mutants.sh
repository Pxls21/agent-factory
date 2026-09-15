#!/usr/bin/env bash
set -euo pipefail

# A5m mutation driver. Each row runs in a fresh archive tree. A mutant is
# countable only after its target changed, all mutated Python compiles, the
# named pytest selector collects at least one test, and pytest reports that node
# with assertion or exception detail.
ROOT=$(git rev-parse --show-toplevel)
PIN=${PIN:-1231624}
OUT=${A5M_MUTANT_DIR:-"$ROOT/../scratch/a5m/mutants"}
PYTEST=${PYTEST:-python}
export PATH=/home/rocco/venv-agent-factory/bin:$PATH
export S0_01_VENUE=${S0_01_VENUE:-pc}
export S0_01_REAL_LEG_DIR=${S0_01_REAL_LEG_DIR:-/home/rocco/s0-01-pinned/realleg/golden}
export S0_02_BUZZ_SRC=${S0_02_BUZZ_SRC:-/home/rocco/s0-01-pinned/buzz}
export PYTHONHASHSEED=0
mkdir -p "$OUT"

cases=(
  'M14|test_ck13_dead_branch_citation_mutants_die|T|for idx, fn in checks:|for idx, fn in checks[:1]:'
  'M16|test_ck13_dead_branch_citation_mutants_die|T|if not citations:|if False:'
  'M21|test_ck13_read_site_drift_validator_rejects_rebound_expected|T|return actual - expected, expected - actual|return set(), set()'
  'TABLE_ROWS|test_v24_table_rows_key_cannot_be_replaced_by_rows|C|table_rows=(\d+) |rows=(\d+) '
  'ARGV_OPTIONAL|test_ck12_pinned_required_file_cannot_be_dropped|P|"argv.txt": "required"|"argv.txt": "optional"'
  'TEARDOWN_REQUIRED|test_ck12_pinned_required_file_cannot_be_dropped|P|"teardown.txt": "optional"|"teardown.txt": "required"'
  'AP40_STAT|test_ck13_presence_gate_detector_covers_each_probe_family|T|and func.attr in {"stat", "is_file", "glob"}|and False and func.attr in {"stat", "is_file", "glob"}'
  'READ_FDOPEN|test_ck13_read_inventory_covers_each_declared_family|T|return "descriptor"|return "unguarded"'
  'READ_COPY|test_ck13_read_inventory_covers_each_declared_family|T|elif (isinstance(func, _ast.Attribute) and func.attr in {"run", "call", "check_call", "check_output", "Popen"}|elif False and (isinstance(func, _ast.Attribute) and func.attr in {"run", "call", "check_call", "check_output", "Popen"}'
  'READ_SUBPROCESS|test_ck13_read_inventory_covers_each_declared_family|T|func.attr in {"run", "call", "check_call", "check_output", "Popen"}|func.attr in set()'
  'WRITE_LINK|test_f43_no_direct_writes_outside_rewrite|T|, "link", "symlink"|'
  'WRITE_MOVE|test_f43_no_direct_writes_outside_rewrite|T|, "move"|'
  'WRITE_EXTRACT|test_f43_no_direct_writes_outside_rewrite|T|_ARCHIVE_WRITERS = {"extract", "extractall"}|_ARCHIVE_WRITERS = set()'
  'F1_ALT_USE|test_ck13_checker_has_no_private_pinned_process_predicate|C|def _pinned_process_count(commands):\n    return sum(1 for cmd in commands if pins.is_pinned_argv(cmd.split()))|def _is_pinned_process_alt(argv):\n    return argv[:1] == [PINNED_BUZZ_ACP_EXE_REALPATH]\n\n\ndef _pinned_process_count(commands):\n    return sum(1 for cmd in commands if _is_pinned_process_alt(cmd.split()) or pins.is_pinned_argv(cmd.split()))'
  'F1_AND|test_ck13_checker_has_no_private_pinned_process_predicate|C|if pins.is_pinned_argv(cmd.split()))|if pins.is_pinned_argv(cmd.split()) and cmd.startswith("/"))'
  'F1_LOCAL_HELPER_USE|test_ck13_checker_has_no_private_pinned_process_predicate|C|def _pinned_process_count(commands):\n    return sum(1 for cmd in commands if pins.is_pinned_argv(cmd.split()))|def _pinned_argv_local(argv):\n    return pins.is_pinned_argv(argv)\n\n\ndef _pinned_process_count(commands):\n    return sum(1 for cmd in commands if _pinned_argv_local(cmd.split()))'
  'F1_DEAD_PIN_COMPARE|test_ck13_checker_has_no_private_pinned_process_predicate|C|def _pinned_process_count(commands):|def _dead_pin_compare(argv):\n    return argv[0] == PINNED_TEE_PATH\n\n\ndef _pinned_process_count(commands):'
  'F1_SECOND_SHARED_USER|test_ck13_checker_has_no_private_pinned_process_predicate|C|def _pinned_process_count(commands):|def unrelated_shared_user(argv):\n    return pins.is_pinned_argv(argv)\n\n\ndef _pinned_process_count(commands):'
  'F1_SECOND_IF|test_ck13_checker_has_no_private_pinned_process_predicate|C|if pins.is_pinned_argv(cmd.split()))|if cmd and pins.is_pinned_argv(cmd.split()))'
  'CONTROL_COMMENT|test_ck13_read_site_drift_validator_rejects_rebound_expected|T|Every read site is named exactly|Every read operation is named exactly'
)

expected=0
killed=0
survived=0
invalid=0
control=0
for row in "${cases[@]}"; do
  IFS='|' read -r name test_name target_key old new <<<"$row"
  dir="$OUT/$name"
  rm -rf "$dir"
  mkdir -p "$dir/tree" "$dir/base"
  git archive "$PIN" | tar -x -C "$dir/tree"
  cp "$ROOT/proofs/S0-01/check_acp_conformance.py" "$dir/tree/proofs/S0-01/check_acp_conformance.py"
  cp "$ROOT/tests/test_s0_01_check_acp_conformance.py" "$dir/tree/tests/test_s0_01_check_acp_conformance.py"
  cp "$ROOT/proofs/S0-01/pins.py" "$dir/tree/proofs/S0-01/pins.py"
  cp "$ROOT/tests/test_s0_01_audit_cp5_controls.py" "$dir/tree/tests/test_s0_01_audit_cp5_controls.py"
  case "$target_key" in
    C) target="$dir/tree/proofs/S0-01/check_acp_conformance.py" ;;
    T) target="$dir/tree/tests/test_s0_01_check_acp_conformance.py" ;;
    P) target="$dir/tree/proofs/S0-01/pins.py" ;;
    *) printf 'INVALID %s unknown-target=%s\n' "$name" "$target_key"; exit 1 ;;
  esac

  before=$(sha256sum "$target" | cut -d' ' -f1)
  set +e
  python3 - "$target" "$old" "$new" >"$dir/edit.txt" 2>&1 <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
old = sys.argv[2].replace(r"\n", "\n")
new = sys.argv[3].replace(r"\n", "\n")
text = path.read_text()
count = text.count(old)
if count != 1:
    raise SystemExit(f"edit-count={count} old={old!r}")
path.write_text(text.replace(old, new, 1))
PY
  edit_rc=$?
  set -e
  after=$(sha256sum "$target" | cut -d' ' -f1)
  if [[ $edit_rc -ne 0 || "$before" == "$after" ]]; then
    invalid=$((invalid + 1))
    printf 'INVALID %s edit rc=%s changed=%s\n' "$name" "$edit_rc" "$([[ "$before" != "$after" ]] && printf yes || printf no)"
    continue
  fi

  set +e
  (cd "$dir/tree" && "$PYTEST" -m py_compile \
      proofs/S0-01/check_acp_conformance.py proofs/S0-01/pins.py \
      tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_audit_cp5_controls.py) \
      >"$dir/compile.txt" 2>&1
  compile_rc=$?
  set -e
  if [[ $compile_rc -ne 0 ]]; then
    invalid=$((invalid + 1))
    printf 'INVALID %s compile rc=%s reason=%s\n' "$name" "$compile_rc" \
      "$(sed -n '/Error\|SyntaxError/{$p;q;}' "$dir/compile.txt")"
    continue
  fi

  set +e
  (cd "$dir/tree" && "$PYTEST" -m pytest --collect-only -q \
      tests/test_s0_01_check_acp_conformance.py -k "$test_name" \
      --basetemp="$dir/base/collect" -p no:cacheprovider) >"$dir/collect.txt" 2>&1
  collect_rc=$?
  set -e
  collected=$(sed -n 's/^\([0-9][0-9]*\)\/\([0-9][0-9]*\) tests collected.*/\1/p; s/^\([0-9][0-9]*\) tests\? collected.*/\1/p' "$dir/collect.txt" | tail -n 1)
  if [[ $collect_rc -ne 0 || -z "$collected" || "$collected" -lt 1 ]]; then
    invalid=$((invalid + 1))
    printf 'INVALID %s collect rc=%s collected=%s reason=%s\n' "$name" "$collect_rc" \
      "${collected:-0}" "$(sed -n '/ERROR\|no tests ran\|collected/{$p;q;}' "$dir/collect.txt")"
    continue
  fi

  set +e
  (cd "$dir/tree" && "$PYTEST" -m pytest -q \
      tests/test_s0_01_check_acp_conformance.py -k "$test_name" \
      --basetemp="$dir/base/run" -p no:cacheprovider) >"$dir/output.txt" 2>&1
  rc=$?
  set -e
  if [[ "$name" == CONTROL_COMMENT ]]; then
    if [[ $rc -ne 0 ]]; then
      invalid=$((invalid + 1))
      printf 'INVALID %s control-red rc=%s\n' "$name" "$rc"
    else
      control=$((control + 1))
      printf 'CONTROL_GREEN %s\n' "$name"
    fi
    continue
  fi

  expected=$((expected + 1))
  if [[ $rc -eq 0 ]]; then
    survived=$((survived + 1))
    printf 'SURVIVED %s\n' "$name"
    continue
  fi
  killer=$(sed -n '/^FAILED .*::/p' "$dir/output.txt" | head -n 1)
  detail=$(sed -n '/^E       /{p;q;}' "$dir/output.txt")
  killer_detail=$(printf '%s\n' "$killer" | sed -nE 's/^FAILED .+::[^ ]+ - ([^:]+): (.*)$/E       \1: \2/p')
  [[ -n "$killer_detail" ]] && detail="$killer_detail"
  if [[ -z "$killer" || -z "$detail" ]]; then
    invalid=$((invalid + 1))
    expected=$((expected - 1))
    printf 'INVALID %s pytest rc=%s no-assertion-line\n' "$name" "$rc"
    continue
  fi
  killed=$((killed + 1))
  printf 'KILLED %s | %s | %s\n' "$name" "$killer" "$detail"
done
printf 'EXPECTED=%s KILLED=%s SURVIVED=%s INVALID=%s CONTROL=%s\n' \
  "$expected" "$killed" "$survived" "$invalid" "$control"
[[ $invalid -eq 0 && $survived -eq 0 && $control -eq 1 && $killed -eq $expected ]]
