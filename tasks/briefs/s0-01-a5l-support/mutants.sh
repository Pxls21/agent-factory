#!/usr/bin/env bash
set -euo pipefail

# A5l mutation driver. Each expected-kill row runs in a fresh archive copy so
# mutations cannot leak between cases. The comment-only row is the negative
# control and must stay green.
ROOT=$(git rev-parse --show-toplevel)
PIN=${PIN:-d23762a}
OUT=${A5L_MUTANT_DIR:-"$ROOT/../scratch/a5l/mutants"}
PYTEST=${PYTEST:-python}
export PATH=/home/rocco/venv-agent-factory/bin:$PATH
export S0_01_VENUE=${S0_01_VENUE:-pc}
export S0_01_REAL_LEG_DIR=${S0_01_REAL_LEG_DIR:-/home/rocco/s0-01-pinned/realleg/golden}
export S0_02_BUZZ_SRC=${S0_02_BUZZ_SRC:-/home/rocco/s0-01-pinned/buzz}
mkdir -p "$OUT"

cases=(
  "M14|test_ck13_dead_branch_citation_mutants_die|s/for idx, fn in checks:/for idx, fn in checks[:1]:/"
  "M16|test_ck13_dead_branch_citation_mutants_die|s/if not citations:/if False:/"
  "M21|test_ck13_read_site_drift_validator_rejects_rebound_expected|s/return actual - expected, expected - actual/return set(), set()/"
  "TABLE_ROWS|test_v24_table_rows_key_cannot_be_replaced_by_rows|s/table_rows=4/rows=4/"
  "ARGV_OPTIONAL|test_ck12_pinned_required_file_cannot_be_dropped|s/\"argv.txt\": \"required\"/\"argv.txt\": \"optional\"/"
  "TEARDOWN_REQUIRED|test_ck12_pinned_required_file_cannot_be_dropped|s/\"teardown.txt\": \"optional\"/\"teardown.txt\": \"required\"/"
  "AP40_STAT|test_ck12_presence_gate_detector_catches_extended_shapes|s/and func.attr in {\"stat\", \"is_file\", \"glob\"}/and False and func.attr in {\"stat\", \"is_file\", \"glob\"}/"
  "READ_FDOPEN|test_ck13_read_inventory_covers_each_declared_family|s/return \"descriptor\"/return \"unguarded\"/"
  "READ_COPY|test_ck13_read_inventory_covers_each_declared_family|s/and func.value.id == \"shutil\" and func.attr == \"copyfile\"/and func.value.id == \"shutil_DISABLED\" and func.attr == \"copyfile\"/g"
  "READ_SUBPROCESS|test_ck13_read_inventory_covers_each_declared_family|s/func.attr in {\"run\", \"call\", \"check_call\", \"check_output\", \"Popen\"}/func.attr in set()/"
  "WRITE_LINK|test_f43_no_direct_writes_outside_rewrite|s/, \"link\", \"symlink\"//"
  "WRITE_MOVE|test_f43_no_direct_writes_outside_rewrite|s/, \"move\"//"
  "WRITE_EXTRACT|test_f43_no_direct_writes_outside_rewrite|s/_ARCHIVE_WRITERS = {\"extract\", \"extractall\"}/_ARCHIVE_WRITERS = set()/"
  "CONTROL_COMMENT|test_ck13_read_site_drift_validator_rejects_rebound_expected|s/Every read site is named exactly/Every read operation is named exactly/"
)

killed=0
survived=0
control=0
for row in "${cases[@]}"; do
  IFS='|' read -r name test_name edit <<<"$row"
  dir="$OUT/$name"
  rm -rf "$dir"
  mkdir -p "$dir/tree" "$dir/base"
  git archive "$PIN" | tar -x -C "$dir/tree"
  cp "$ROOT/proofs/S0-01/check_acp_conformance.py" "$dir/tree/proofs/S0-01/check_acp_conformance.py"
  cp "$ROOT/tests/test_s0_01_check_acp_conformance.py" "$dir/tree/tests/test_s0_01_check_acp_conformance.py"
  cp "$ROOT/tests/test_s0_01_audit_cp5_controls.py" "$dir/tree/tests/test_s0_01_audit_cp5_controls.py"
  target="$dir/tree/tests/test_s0_01_check_acp_conformance.py"
  [[ "$name" == ARGV_OPTIONAL || "$name" == TEARDOWN_REQUIRED ]] && target="$dir/tree/proofs/S0-01/pins.py"
  python3 - "$target" "$edit" <<'PY'
from pathlib import Path
import re, sys
p = Path(sys.argv[1]); spec = sys.argv[2]
assert spec.startswith('s/')
body = spec[2:]
global_replace = body.endswith('/g')
body = body[:-2] if global_replace else body[:-1]
old, new = body.split('/', 1)
text = p.read_text()
updated, count = re.subn(old, new, text, count=0 if global_replace else 1)
assert (count >= 1) if global_replace else (count == 1), (p, old, count)
p.write_text(updated)
PY
  set +e
  (cd "$dir/tree" && "$PYTEST" -m pytest -q tests/test_s0_01_check_acp_conformance.py -k "$test_name" --basetemp="$dir/base") >"$dir/output.txt" 2>&1
  rc=$?
  set -e
  if [[ "$name" == CONTROL_COMMENT ]]; then
    [[ $rc -eq 0 ]] || { printf 'CONTROL_RED %s rc=%s\n' "$name" "$rc"; exit 1; }
    control=$((control + 1))
    printf 'CONTROL_GREEN %s\n' "$name"
  elif [[ $rc -ne 0 ]]; then
    killed=$((killed + 1))
    printf 'KILLED %s rc=%s\n' "$name" "$rc"
  else
    survived=$((survived + 1))
    printf 'SURVIVED %s\n' "$name"
  fi
done
printf 'EXPECTED=%s KILLED=%s SURVIVED=%s CONTROL=%s\n' "$((killed + survived))" "$killed" "$survived" "$control"
[[ $survived -eq 0 && $control -eq 1 ]]
