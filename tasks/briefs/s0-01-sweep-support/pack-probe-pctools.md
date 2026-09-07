# lane context pack — 2c83197 2026-09-07T22:42Z
files: proofs/S0-01/tools/acp_probe.py proofs/S0-01/tools/pc/pc_launch.py proofs/S0-01/tools/pc/pc_negative.py proofs/S0-01/tools/build_capture_record.py proofs/S0-01/pins.py
symbols: _drain_stderr pump_pipe pinned_present build_record main

## proofs/S0-01/tools/acp_probe.py
### graft skeleton

graft skeleton — proofs/S0-01/tools/acp_probe.py
- L41-L46  function _sha256_file  def _sha256_file(path)
- L49-L51  function _utc_now  def _utc_now()
- L54-L64  function _drain_stderr  def _drain_stderr(proc, stderr_path)
- L67-L79  function _redact_env  def _redact_env(env)
- L82-L87  function _write_env  def _write_env(framedir)
- L90-L131  function _write_evidence  def _write_evidence(framedir, timeline, agent, agent_realpath, child_pid, interp_realpath, interp_sha256, spawned_at_utc, agent_exit_code, probe_error)
- L134-L459  function main  def main(): # Validate required env vars early with a named message (L15/A10: exit 64). # Empty/unset cases exit 64 WITHOUT probe_error because the try block (which # writes runtime-identity.json) has not started yet — this is a documented # exception: probe_error requires the wrapped body to have opened.
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 9 hits over 1 files ---
AP-1: 4
    proofs/S0-01/tools/acp_probe.py:113: "python_dont_write_bytecode": os.environ.get("PYTHONDONTWRITEBYTECODE") == "1",
    proofs/S0-01/tools/acp_probe.py:140: v = os.environ.get(k)
    proofs/S0-01/tools/acp_probe.py:189: timeout_raw = os.environ.get("ACP_PROBE_TIMEOUT", "30")
    proofs/S0-01/tools/acp_probe.py:434: "python_dont_write_bytecode": os.environ.get("PYTHONDONTWRITEBYTECODE") == "1",
AF-AP-55: 3
    proofs/S0-01/tools/acp_probe.py:231: candidate = os.readlink("/proc/%d/exe" % proc.pid)
    proofs/S0-01/tools/acp_probe.py:303: interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)
    proofs/S0-01/tools/acp_probe.py:381: interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)
AP-32: 2
    proofs/S0-01/tools/acp_probe.py:42: h = hashlib.sha256()
    proofs/S0-01/tools/acp_probe.py:75: "sha256_12": hashlib.sha256(v.encode("utf-8")).hexdigest()[:12],

## proofs/S0-01/tools/pc/pc_launch.py
### graft skeleton

graft skeleton — proofs/S0-01/tools/pc/pc_launch.py
- L40-L41  function utc_now  def utc_now()
- L44-L49  function sha256_file  def sha256_file(path)
- L52-L59  function read_kv  def read_kv(path, key)
- L62-L71  function alive_pinned_buzz  def alive_pinned_buzz(pidfile)
- L74-L77  function masked_log_text  def masked_log_text(raw_path)
- L80-L269  function main  def main()
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 5 hits over 1 files ---
AF-AP-55: 2
    proofs/S0-01/tools/pc/pc_launch.py:68: exe = os.readlink(f"/proc/{pid}/exe")
    proofs/S0-01/tools/pc/pc_launch.py:221: exe_real = os.readlink(f"/proc/{pid}/exe")
AP-32: 2
    proofs/S0-01/tools/pc/pc_launch.py:45: h = hashlib.sha256()
    proofs/S0-01/tools/pc/pc_launch.py:209: live_env[k] = {"redacted": True, "len": len(v), "sha256_12": hashlib.sha256(v.encode("utf-8")).hexdi
AF-AP-45: 1
    proofs/S0-01/tools/pc/pc_launch.py:247: for line in subprocess.run(["ps", "-eo", "pid,ppid", "--no-headers"], capture_output=True, text=True

## proofs/S0-01/tools/pc/pc_negative.py
### graft skeleton
graft skeleton — proofs/S0-01/tools/pc/pc_negative.py

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## proofs/S0-01/tools/build_capture_record.py
### graft skeleton

graft skeleton — proofs/S0-01/tools/build_capture_record.py
- L20-L21  function _sha256  def _sha256(data: bytes) -> str
- L24-L29  function _sha256_file  def _sha256_file(p: Path) -> str
- L32-L42  function _parse_manifest_gz  def _parse_manifest_gz(gz_path: Path) -> dict
- L45-L159  function main  def main() -> int
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 15 hits over 1 files ---
AF-AP-40: 10
    proofs/S0-01/tools/build_capture_record.py:58: if tl_path.exists():
    proofs/S0-01/tools/build_capture_record.py:82: if rid_path.exists():
    proofs/S0-01/tools/build_capture_record.py:87: if env_path.exists():
    proofs/S0-01/tools/build_capture_record.py:93: if startup_path.exists():
    proofs/S0-01/tools/build_capture_record.py:100: if model_path.exists():
    proofs/S0-01/tools/build_capture_record.py:105: if mentions_dir.is_dir():
    ... +4
AP-32: 4
    proofs/S0-01/tools/build_capture_record.py:20: def _sha256(data: bytes) -> str:
    proofs/S0-01/tools/build_capture_record.py:21: return hashlib.sha256(data).hexdigest()
    proofs/S0-01/tools/build_capture_record.py:25: h = hashlib.sha256()
    proofs/S0-01/tools/build_capture_record.py:42: return {k: _sha256(v.encode("utf-8")) for k, v in sections.items()}
AF-AP-41: 1
    proofs/S0-01/tools/build_capture_record.py:95: kvs = dict(re.findall(r"(idle_timeout|max_turn|session_policy)=(\S+)", startup))

## proofs/S0-01/pins.py
### graft skeleton
graft skeleton — proofs/S0-01/pins.py

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## graft ask — which producer writes each file into a leg framedir on the PC, and which allowlist in the checker or pins admits those names
graft ask — "which producer writes each file into a leg framedir on the PC, and which allowlist in the checker or pins admits those names"  (lexical)

1. main · function  [symbol]
   proofs/S0-01/tools/pc/pc_launch.py:L80-L269
   def main()

2. pc_negative.py · file  [symbol]
   proofs/S0-01/tools/pc/pc_negative.py

3. main · function  [symbol]
   proofs/S0-01/tools/acp_probe.py:L134-L459
   def main(): # Validate required env vars early with a named message (L15/A10: exit 64). # Empty/unset cases exit 64 WITHOUT probe_error because the try block (which # writes runtime-identity.json) has not started yet — this is a documented # exception: probe_error requires the wrapped body to have opened.

4. main · function  [symbol]
   proofs/S0-01/tools/archive/build_capture_record_v1.py:L43-L101
   def main() -> int

5. frame_tee.py · file  [symbol]
   proofs/S0-01/tools/frame_tee.py

6. main · function  [symbol]
   proofs/S0-01/tools/build_capture_record.py:L45-L159
   def main() -> int

7. _has_invalid_utf8_bytes · function  [symbol]
   proofs/S0-01/tools/scripted_backend.py:L249-L271
   def _has_invalid_utf8_bytes(s: str) -> bool

8. frame_tee_v1.py · file  [symbol]
   proofs/S0-01/tools/archive/frame_tee_v1.py

## symbol _drain_stderr
### GitNexus impact (upstream)
  "impactedCount": null,
  "risk": "UNKNOWN",
      "impactedCount": 0,
      "risk": "UNKNOWN",
      "direct": 0,
      "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe."
      "impactedCount": 0,
      "risk": "UNKNOWN",
### code-review-graph callers_of / tests_for
  "summary": "'_drain_stderr' matches 2 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "_drain_stderr",
      "name": "_drain_stderr",
      "name": "_drain_stderr",
      "name": "_drain_stderr",
  "summary": "'_drain_stderr' matches 2 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "_drain_stderr",
      "name": "_drain_stderr",
      "name": "_drain_stderr",
      "name": "_drain_stderr",
### ripwire callers
<callers of="_drain_stderr" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=_drain_stderr">

## symbol pump_pipe
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/tools/frame_tee.py::pump_pipe')",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/tools/frame_tee.py::pump_pipe')",
### ripwire callers
<callers of="pump_pipe" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=pump_pipe">

## symbol pinned_present
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "'pinned_present' matches 2 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "test_pinned_present_is_exact_over_a_synthetic_table",
      "name": "_scan_header",
      "name": "test_pinned_present_is_exact_over_a_synthetic_table",
      "name": "_scan_header",
  "summary": "'pinned_present' matches 2 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "test_pinned_present_is_exact_over_a_synthetic_table",
      "name": "_scan_header",
      "name": "test_pinned_present_is_exact_over_a_synthetic_table",
      "name": "_scan_header",
### ripwire callers

## symbol build_record
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching 'build_record'.",
  "summary": "No node found matching 'build_record'.",
### ripwire callers

## symbol main
### GitNexus impact (upstream)
  "impactedCount": null,
  "risk": "UNKNOWN",
      "impactedCount": 2,
      "risk": "LOW",
      "direct": 1
      "impactedCount": 1,
      "risk": "LOW",
      "direct": 1
### code-review-graph callers_of / tests_for
  "summary": "'main' matches 681 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
  "summary": "'main' matches 681 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
      "name": "main",
### ripwire callers
<callers of="main" defs="32" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=main">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
<test-gate changed="1" impacted="0" tests="0" untested="0" shown_tests="0" tests_capped="0" shown_untested="0" untested_capped="0" script_gates_unmodelled="4" script_gates_registered="0" script_gates_mapped="0" script_gates_unresolved_dynamic="0" ccx_bar="15" counts_floor="1" total="0" has_more="0" next_offset="0" offset="0" limit="20" at="2c8319759+dirty" next="--situ">
