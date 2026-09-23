#!/usr/bin/env bash
# jev-pruner-setup.sh — clone, patch, build, and smoke tamaratran/jev-pruner against local Laya.
set -uo pipefail

JEV_ROOT="${JEV_ROOT:-$HOME/jev-plugins/jev-pruner}"
JEV_PARENT="$(dirname "$JEV_ROOT")"
JEV_REPO="${JEV_REPO:-https://github.com/tamaratran/jev-pruner}"
JEV_REV="${JEV_REV:-47d017c}"
LAYA_BASE_URL="${LAYA_BASE_URL:-http://127.0.0.1:47411/v1/systemone}"
LAYA_HEALTH="${LAYA_HEALTH:-http://127.0.0.1:47411/health}"

fail() {
  local rc=1
  if [ "${!#}" -eq "${!#}" ] 2>/dev/null; then rc=${!#}; set -- "${@:1:$(($# - 1))}"; fi
  echo "jev-pruner-setup: $*" >&2
  exit "$rc"
}

clone_repo() {
  if [ -d "$JEV_ROOT/.git" ]; then
    echo "jev-pruner-setup: repo already present: $JEV_ROOT"
  else
    mkdir -p "$JEV_PARENT"
    git clone --depth 1 "$JEV_REPO" "$JEV_ROOT" || fail "clone failed" 4
  fi
  if ! git -C "$JEV_ROOT" rev-parse --verify --quiet "$JEV_REV^{commit}" >/dev/null; then
    git -C "$JEV_ROOT" fetch --depth 1 origin "$JEV_REV" || fail "fetch $JEV_REV failed and the object is not already in the shallow clone" 4
  fi
  git -C "$JEV_ROOT" checkout "$JEV_REV" || fail "checkout $JEV_REV failed" 4
  local head; head=$(git -C "$JEV_ROOT" rev-parse --short=7 HEAD)
  [ "$head" = "$JEV_REV" ] || fail "HEAD $head != $JEV_REV" 4
}

patch_codex_client() {
  local f="$JEV_ROOT/src/codex/prune.ts"
  local old='          const request = buildJevRequest({ apiKey }, state, questions);'
  local new='          const request = buildJevRequest({ apiKey, baseUrl: process.env.JEV_BASE_URL || undefined }, state, questions);'
  [ -f "$f" ] || fail "missing $f" 4
  local old_count new_count
  old_count=$(grep -Fxc "$old" "$f" || true)
  new_count=$(grep -Fxc "$new" "$f" || true)
  if [ "$new_count" -eq 1 ] && [ "$old_count" -eq 0 ]; then
    echo "jev-pruner-setup: codex baseUrl patch already applied"
    return 0
  fi
  [ "$old_count" -eq 1 ] || fail "anchor count for buildJevRequest line is $old_count, expected 1; nothing written" 4
  python3 - "$f" "$old" "$new" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
old = sys.argv[2]
new = sys.argv[3]
text = path.read_text()
if text.count(old) != 1 or text.count(new) != 0:
    raise SystemExit(2)
path.write_text(text.replace(old, new))
PY
  echo "jev-pruner-setup: codex baseUrl patch applied"
}

build() {
  clone_repo
  patch_codex_client
  (cd "$JEV_ROOT" && npm install --ignore-scripts --no-audit --no-fund && npm run build) || fail "npm install/build failed" 5
  [ -f "$JEV_ROOT/dist/codex/run.js" ] || fail "dist/codex/run.js missing after build" 5
  echo "jev-pruner-setup: build ok $JEV_ROOT/dist/codex/run.js"
}

make_gen() {
  local dir=$1
  mkdir -p "$dir"
  cat > "$dir/gen.py" <<'PY'
for i in range(1200):
    print(f"tests/test_synthetic_output_regression.py::test_case_{i:04d} PASSED")
print("E   AssertionError: expected 4 got 5")
print("FAILED tests/test_b.py::test_q")
print("KeyError: 'missing'")
PY
  cat > "$dir/small.py" <<'PY'
for i in range(100):
    print(f"small line {i}")
PY
  cat > "$dir/fail.py" <<'PY'
print("child fails after output")
raise SystemExit(1)
PY
  cat > "$dir/secret.py" <<'PY'
print("AWS_SECRET_ACCESS_KEY=not-a-real-secret-fixture")
print("routine output")
PY
}

make_context() {
  local dir=$1 session_id=$2 transcript
  transcript="$dir/$session_id.jsonl"
  mkdir -p "$dir/home/.cache/jev-pruner/codex"
  printf '%s\n' \
    "{\"type\":\"session_meta\",\"payload\":{\"id\":\"$session_id\"}}" \
    '{"type":"response_item","payload":{"type":"message","role":"user","content":[{"type":"input_text","text":"Run the synthetic pytest suite and retain its failures and final results."}]}}' \
    > "$transcript"
  printf '{"sessionId":"%s","transcript":"%s"}\n' "$session_id" "$transcript" \
    > "$dir/home/.cache/jev-pruner/codex/$session_id.json"
}

calls() {
  curl -fsS -m 5 "$LAYA_HEALTH" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("calls"))'
}

smoke() {
  [ -f "$JEV_ROOT/dist/codex/run.js" ] || fail "missing run.js (run build first)" 3
  local tmp before after rc bytes_in bytes_out archive endpoint_result main_failed small_in small_out bad_err bad_rc fail_rc secret_out
  tmp=$(mktemp -d)
  make_gen "$tmp"
  make_context "$tmp" pcj1-smoke
  before=$(calls) || fail "health before failed" 3
  set +e
  (
    cd "$tmp" || exit 1
    HOME="$tmp/home" JEV_BASE_URL="$LAYA_BASE_URL" TYPESAFE_API_KEY=local CODEX_THREAD_ID=pcj1-smoke \
      node "$JEV_ROOT/dist/codex/run.js" -- python3 "$tmp/gen.py"
  ) > "$tmp/pruned.out" 2> "$tmp/pruned.err"
  rc=$?
  set -e
  after=$(calls) || fail "health after failed" 3
  bytes_in=$(python3 "$tmp/gen.py" | wc -c)
  bytes_out=$(wc -c < "$tmp/pruned.out")
  archive=$(find "$tmp/.jev-pruner" -maxdepth 1 -type f -name 'codex-*.txt' -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2- || true)
  [ "$rc" -eq 0 ] || fail "main smoke exited $rc" 6
  [ "$bytes_in" -ge 60000 ] || fail "main fixture is only $bytes_in bytes; expected at least 60000" 6
  [ -n "$archive" ] && [ -f "$archive" ] || fail "main smoke did not write the full-output archive" 6
  cmp -s "$archive" <(python3 "$tmp/gen.py") || fail "main smoke archive differs from original output" 6
  main_failed=0
  if [ "$after" -gt "$before" ] && [ "$bytes_out" -lt "$bytes_in" ]; then
    endpoint_result="answered and pruned"
    grep -Eo '([^[:space:]]+\.jev-pruner/[^[:space:]]+)' "$tmp/pruned.out" | head -1 >/dev/null || fail "pruned output did not print its archive path" 6
  elif [ "$after" -le "$before" ]; then
    endpoint_result="timed out at the upstream 30-second deadline"
    main_failed=1
  else
    endpoint_result="answered but preserved original output"
    main_failed=1
  fi
  echo "jev-pruner-setup: smoke rc=$rc bytes_in=$bytes_in bytes_out=$bytes_out calls_before=$before calls_after=$after endpoint=$endpoint_result archive=$archive"
  for planted in 'E   AssertionError: expected 4 got 5' 'FAILED tests/test_b.py::test_q' "KeyError: 'missing'"; do
    grep -Fq "$planted" "$tmp/pruned.out" || fail "planted line missing after prune: $planted" 6
    echo "jev-pruner-setup: planted survived: $planted"
  done

  python3 "$tmp/small.py" > "$tmp/small.raw"
  set +e
  JEV_BASE_URL="$LAYA_BASE_URL" TYPESAFE_API_KEY=local CODEX_THREAD_ID=pcj1-small \
    node "$JEV_ROOT/dist/codex/run.js" -- python3 "$tmp/small.py" > "$tmp/small.out" 2> "$tmp/small.err"
  small_rc=$?
  set -e
  small_in=$(wc -c < "$tmp/small.raw")
  small_out=$(wc -c < "$tmp/small.out")
  [ "$small_rc" -eq 0 ] || fail "small-output child exit changed to $small_rc" 6
  cmp -s "$tmp/small.raw" "$tmp/small.out" || fail "small output changed" 6
  echo "jev-pruner-setup: negative small rc=$small_rc bytes_in=$small_in bytes_out=$small_out identical=yes"

  make_context "$tmp" pcj1-closed
  set +e
  (
    cd "$tmp" || exit 1
    HOME="$tmp/home" JEV_BASE_URL=http://127.0.0.1:1/v1/systemone TYPESAFE_API_KEY=local CODEX_THREAD_ID=pcj1-closed \
      node "$JEV_ROOT/dist/codex/run.js" -- python3 "$tmp/gen.py"
  ) > "$tmp/bad.out" 2> "$tmp/bad.err"
  bad_rc=$?
  set -e
  python3 "$tmp/gen.py" > "$tmp/gen.raw"
  [ "$bad_rc" -eq 0 ] || fail "closed-port fallback changed child exit to $bad_rc" 6
  cmp -s "$tmp/gen.raw" "$tmp/bad.out" || fail "closed-port fallback output changed" 6
  bad_err=$(grep -Ei 'fail|error|ECONN|refused|fetch' "$tmp/bad.err" | head -1 || true)
  echo "jev-pruner-setup: negative closed-port rc=$bad_rc identical=yes stderr=${bad_err:-<upstream swallowed fetch failure>}"

  python3 "$tmp/fail.py" > "$tmp/fail.raw" || true
  set +e
  JEV_BASE_URL="$LAYA_BASE_URL" TYPESAFE_API_KEY=local CODEX_THREAD_ID=pcj1-exit1 \
    node "$JEV_ROOT/dist/codex/run.js" -- python3 "$tmp/fail.py" > "$tmp/fail.out" 2> "$tmp/fail.err"
  fail_rc=$?
  set -e
  [ "$fail_rc" -eq 1 ] || fail "child-exit control returned $fail_rc, expected 1" 6
  cmp -s "$tmp/fail.raw" "$tmp/fail.out" || fail "child-exit output changed" 6
  echo "jev-pruner-setup: negative child-exit rc=$fail_rc output_bytes=$(wc -c < "$tmp/fail.out") identical=yes"

  python3 "$tmp/secret.py" > "$tmp/secret.raw"
  set +e
  JEV_BASE_URL="$LAYA_BASE_URL" TYPESAFE_API_KEY=local CODEX_THREAD_ID=pcj1-secret \
    node "$JEV_ROOT/dist/codex/run.js" -- python3 "$tmp/secret.py" > "$tmp/secret.out" 2> "$tmp/secret.err"
  secret_rc=$?
  set -e
  [ "$secret_rc" -eq 0 ] || fail "secret-screen child exit changed to $secret_rc" 6
  cmp -s "$tmp/secret.raw" "$tmp/secret.out" || fail "secret-screen output changed" 6
  secret_out=$(tr '\n' '|' < "$tmp/secret.out")
  echo "jev-pruner-setup: negative secret rc=$secret_rc identical=yes output=$secret_out"
  if [ "$main_failed" -ne 0 ]; then
    echo "jev-pruner-setup: smoke FAILED: $endpoint_result; original output was preserved" >&2
    return 6
  fi
}

case "${1:-}" in
  install|build) build;;
  smoke) smoke;;
  *) echo "usage: jev-pruner-setup.sh install|build|smoke"; exit 64;;
esac
