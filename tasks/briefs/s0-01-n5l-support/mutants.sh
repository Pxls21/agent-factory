#!/usr/bin/env bash
set -euo pipefail

# N5m mutation driver. Every row runs in a fresh archive copy with the lane's
# probe and test bytes overlaid. Mutants must compile and collect before a test
# result can grade them. The one comment-only control must remain green.
EXPECTED=13
ROOT=$(git rev-parse --show-toplevel)
PIN=${PIN:-97bb0c0}
OUT=${N5L_MUTANT_DIR:-"$ROOT/../scratch/n5l/mutants"}
PYTEST=${PYTEST:-python}
export PATH=/home/rocco/venv-agent-factory/bin:$PATH
export S0_01_VENUE=${S0_01_VENUE:-pc}
export S0_01_REAL_LEG_DIR=${S0_01_REAL_LEG_DIR:-/home/rocco/s0-01-pinned/realleg/golden}
export S0_02_BUZZ_SRC=${S0_02_BUZZ_SRC:-/home/rocco/s0-01-pinned/buzz}
mkdir -p "$OUT"

if [[ ${1:-} == --self-test ]]; then
  self_dir="$OUT/self-test"
  self_copy="$self_dir/mutants-row-deleted.sh"
  rm -rf "$self_dir"
  mkdir -p "$self_dir"
  cp "$0" "$self_copy"
  python3 - "$self_copy" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
lines = path.read_text().splitlines(keepends=True)
marker = "  'CLOSE_FDS_ALT_TARGET;"
hits = [index for index, line in enumerate(lines) if line.startswith(marker)]
assert len(hits) == 1, (marker, hits)
del lines[hits[0]]
path.write_text("".join(lines))
PY
  set +e
  N5L_MUTANT_DIR="$self_dir/run" bash "$self_copy" >"$self_dir/output.txt" 2>&1
  rc=$?
  set -e
  summary=$(python3 - "$self_dir/output.txt" <<'PY'
from pathlib import Path
import sys

lines = Path(sys.argv[1]).read_text(errors="replace").splitlines()
summary = [line for line in lines if line.startswith("EXPECTED=")]
print(summary[-1] if summary else "")
PY
  )
  printf 'SELF_TEST rc=%s %s\n' "$rc" "$summary"
  [[ $rc -ne 0 && "$summary" == \
      "EXPECTED=13 KILLED=12 SURVIVED=0 INVALID=0 CONTROL=1" ]]
  exit
fi

cases=(
  'READ_NOFOLLOW_DROP;probe;test_probe_read_regular_refuses_final_symlink_with_eloop;    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC;    flags = os.O_RDONLY | os.O_NONBLOCK | os.O_CLOEXEC'
  'READ_NONBLOCK_DROP;probe;test_probe_read_primitive_refuses_named_non_regular_shapes;    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC;    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC'
  'READ_SISREG_DROP;probe;test_probe_read_primitive_refuses_named_non_regular_shapes;        st = os.fstat(fd)\n        if not stat.S_ISREG(st.st_mode):\n            raise OSError("not a regular file: %s" % (path,));        st = os.fstat(fd)\n        if False:\n            raise OSError("not a regular file: %s" % (path,))'
  'READ_NO_CLOSE_ON_REFUSAL;probe;test_probe_read_primitive_leaves_no_fd_on_refusal;    except Exception:\n        os.close(fd)\n        raise\n    try:\n        handle = os.fdopen(fd, mode);    except Exception:\n        raise\n    try:\n        handle = os.fdopen(fd, mode)'
  'CLOSE_BEFORE_FSTAT;probe;test_probe_read_primitive_reads_a_regular_file;        st = os.fstat(fd)\n        if not stat.S_ISREG(st.st_mode):\n            raise OSError("not a regular file: %s" % (path,));        os.close(fd)\n        st = os.fstat(fd)\n        if not stat.S_ISREG(st.st_mode):\n            raise OSError("not a regular file: %s" % (path,))'
  'FD_LEAK_TRIPLE;probe;test_probe_census_agent_sees_only_stdio_and_its_output_fd;        framedir_fd = os.open(\n            framedir, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)\n\n        # A16:;        framedir_fd = os.open(\n            framedir, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)\n        os.set_inheritable(framedir_fd, True)\n\n        # A16:'
  'FD_LEAK_PIPE;probe;test_probe_census_agent_sees_only_stdio_and_its_output_fd;        proc = subprocess.Popen(\n            [agent], stdin=subprocess.PIPE, stdout=subprocess.PIPE,\n            stderr=subprocess.PIPE, close_fds=True\n        );        n5m_leak_read_fd, n5m_leak_write_fd = os.pipe()\n        os.set_inheritable(n5m_leak_read_fd, True)\n        proc = subprocess.Popen(\n            [agent], stdin=subprocess.PIPE, stdout=subprocess.PIPE,\n            stderr=subprocess.PIPE, close_fds=False\n        )'
  'CLOSE_FDS_FALSE;probe;test_probe_agent_launch_pins_the_close_fds_default_second_defence;            stderr=subprocess.PIPE, close_fds=True;            stderr=subprocess.PIPE, close_fds=False'
  'CLOSE_FDS_COMMENT_ONLY;probe;test_probe_agent_launch_pins_the_close_fds_default_second_defence;            stderr=subprocess.PIPE, close_fds=True;            stderr=subprocess.PIPE, close_fds=False  # close_fds=True'
  'CLOSE_FDS_ALT_TARGET;probe;test_probe_agent_launch_pins_the_close_fds_default_second_defence;        proc = subprocess.Popen(\n            [agent], stdin=subprocess.PIPE, stdout=subprocess.PIPE,;        sidecar = subprocess.Popen([agent], close_fds=False)\n        proc = subprocess.Popen(\n            [agent], stdin=subprocess.PIPE, stdout=subprocess.PIPE,'
  'CLOSE_FDS_LOOP;probe;test_probe_agent_launch_pins_the_close_fds_default_second_defence;        proc = subprocess.Popen(\n            [agent], stdin=subprocess.PIPE, stdout=subprocess.PIPE,\n            stderr=subprocess.PIPE, close_fds=True\n        )\n        child_pid = proc.pid;        for _n5n_index in range(2):\n            proc = subprocess.Popen(\n                [agent], stdin=subprocess.PIPE, stdout=subprocess.PIPE,\n                stderr=subprocess.PIPE, close_fds=True\n            )\n        child_pid = proc.pid'
  'NONREG_ERROR_TEXT;probe;test_probe_read_primitive_refuses_named_non_regular_shapes;            raise OSError("not a regular file: %s" % (path,));            raise OSError("not regular: %s" % (path,))'
  'FD_CLOSE_REDIRECT;probe;test_probe_read_primitive_leaves_no_fd_on_refusal;        os.close(fd)\n        raise\n    try:\n        handle = os.fdopen(fd, mode);        os.close(os.open(os.devnull, os.O_RDONLY))\n        raise\n    try:\n        handle = os.fdopen(fd, mode)'
  'CONTROL_COMMENT;probe;test_probe_read_primitive_reads_a_regular_file;    N5k round 14 (AF-AP-70 closed for reads):;    N5k round 14 (AF-AP-70 closed for file reads):'
)

prepare_tree() {
  local dir=$1
  rm -rf "$dir"
  mkdir -p "$dir/tree" "$dir/base"
  git archive "$PIN" | tar -x -C "$dir/tree"
  cp "$ROOT/proofs/S0-01/tools/acp_probe.py" "$dir/tree/proofs/S0-01/tools/acp_probe.py"
  cp "$ROOT/tests/test_s0_01_acp_probe.py" "$dir/tree/tests/test_s0_01_acp_probe.py"
}

mutate_exact() {
  local target=$1 old=$2 new=$3
  python3 - "$target" "$old" "$new" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
old = sys.argv[2].replace("\\n", "\n")
new = sys.argv[3].replace("\\n", "\n")
text = path.read_text()
count = text.count(old)
assert count == 1, (path, old, count)
path.write_text(text.replace(old, new, 1))
PY
}

killed=0
survived=0
invalid=0
control=0
index=0
for row in "${cases[@]}"; do
  index=$((index + 1))
  IFS=';' read -r name target_kind test_name old new <<<"$row"
  slug="$name"
  dir="$OUT/$(printf '%02d' "$index")-$slug"
  prepare_tree "$dir"
  if [[ "$target_kind" == probe ]]; then
    target="$dir/tree/proofs/S0-01/tools/acp_probe.py"
  else
    target="$dir/tree/tests/test_s0_01_acp_probe.py"
  fi
  mutate_exact "$target" "$old" "$new"

  if [[ "$name" == FD_LEAK_TRIPLE ]]; then
    target="$dir/tree/proofs/S0-01/tools/acp_probe.py"
    mutate_exact "$target" \
      '            stderr=subprocess.PIPE, close_fds=True' \
      '            stderr=subprocess.PIPE, close_fds=False'
  fi

  set +e
  (cd "$dir/tree" && python3 -m py_compile \
      proofs/S0-01/tools/acp_probe.py tests/test_s0_01_acp_probe.py) \
      >"$dir/compile.txt" 2>&1
  compile_rc=$?
  if [[ $compile_rc -eq 0 ]]; then
    (cd "$dir/tree" && "$PYTEST" -m pytest --collect-only -q \
      tests/test_s0_01_acp_probe.py -k "$test_name" \
      --basetemp="$dir/base-collect") >"$dir/collect.txt" 2>&1
    collect_rc=$?
  else
    collect_rc=125
  fi
  set -e

  if [[ $compile_rc -ne 0 || $collect_rc -ne 0 ]]; then
    invalid=$((invalid + 1))
    printf 'INVALID %s compile_rc=%s collect_rc=%s\n' "$name" "$compile_rc" "$collect_rc"
    continue
  fi

  set +e
  if [[ "$name" == READ_NONBLOCK_DROP ]]; then
    timeout 15s bash -c 'cd "$1" && exec "$2" -m pytest -q tests/test_s0_01_acp_probe.py -k "$3" --basetemp="$4"' \
      _ "$dir/tree" "$PYTEST" "$test_name" "$dir/base-run" >"$dir/output.txt" 2>&1
  else
    (cd "$dir/tree" && "$PYTEST" -m pytest -q \
      tests/test_s0_01_acp_probe.py -k "$test_name" \
      --basetemp="$dir/base-run") >"$dir/output.txt" 2>&1
  fi
  rc=$?
  set -e

  if [[ "$name" == CONTROL_COMMENT ]]; then
    if [[ $rc -ne 0 ]]; then
      printf 'CONTROL_RED %s rc=%s\n' "$name" "$rc"
      exit 1
    fi
    control=$((control + 1))
    printf 'CONTROL_GREEN %s\n' "$name"
  elif [[ $rc -ne 0 ]]; then
    killed=$((killed + 1))
    printf 'KILLED %s rc=%s ' "$name" "$rc"
    python3 - "$dir/output.txt" <<'PY'
from pathlib import Path
import sys

lines = Path(sys.argv[1]).read_text(errors="replace").splitlines()
failed = [line for line in lines if line.startswith("FAILED ")]
print(failed[-1] if failed else "FAILED <timeout> - bounded timeout")
PY
  else
    survived=$((survived + 1))
    printf 'SURVIVED %s\n' "$name"
  fi
done

printf 'EXPECTED=%s KILLED=%s SURVIVED=%s INVALID=%s CONTROL=%s\n' \
  "$EXPECTED" "$killed" "$survived" "$invalid" "$control"
[[ $killed -eq $EXPECTED && $survived -eq 0 && $invalid -eq 0 && $control -eq 1 ]]
