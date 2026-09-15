# lane context pack — f707f56 2026-09-15T12:02Z
files: harness-ports/bin/qwen-server.sh harness-ports/bin/omniroute_local_builder.py
symbols: render_exec install restart

## harness-ports/bin/qwen-server.sh
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).
graft skeleton — harness-ports/bin/qwen-server.sh

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## harness-ports/bin/omniroute_local_builder.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

graft skeleton — harness-ports/bin/omniroute_local_builder.py
- L56-L58  function node_payload  def node_payload(name: str = NODE_NAME, base_url: str = LOCAL_URL) -> dict
- L61-L62  function connection_payload  def connection_payload(node_id: str, api_key: str, name: str = NODE_NAME) -> dict
- L65-L79  function combo_payload  def combo_payload(node_id: str, base_combo: dict | None, name: str = COMBO_NAME, model_id: str = MODEL_ID) -> dict
- L82-L101  function env_value  def env_value(path: Path, key: str) -> str | None
- L104-L108  function find_by_name  def find_by_name(items: list, name: str) -> dict | None
- L112-L138  class CliTransport  class CliTransport
- L115-L116  method __init__  def __init__(self, node_bin: str = "node", helper: Path = HERE / "omni_api.mjs")
- L118-L138  method call  def call(self, method: str, path: str, body: dict | None = None)
- L141-L158  function http_json  def http_json(url: str, bearer: str | None = None, body: dict | None = None, timeout: float = 30.0)
- L161-L162  function say  def say(msg: str)
- L165-L173  function unwrap  def unwrap(data, *keys)
- L176-L180  function require  def require(status: int, data, what: str, ok=(200, 201))
- L184-L187  function local_server_serves_alias  def local_server_serves_alias(server_key: str) -> bool
- L190-L194  function exposed_model_ids  def exposed_model_ids(inference_key: str | None) -> list[str]
- L197-L252  function ensure  def ensure(t, server_key: str, inference_key: str | None, wait_s: int = 90) -> int
- L255-L272  function status  def status(t, server_key: str | None, inference_key: str | None) -> int
- L275-L298  function probe  def probe(inference_key: str | None, model: str = COMBO_NAME) -> int: # A nonce per probe: OmniRoute answered an identical repeat in 0.0 s from its response cache (2026-09-14) — # a cached pong proves nothing about the server behind the route.
- L301-L314  function remove  def remove(t) -> int
- L317-L336  function main  def main(argv=None) -> int
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 10 hits over 1 files ---
AP-1: 9
    harness-ports/bin/omniroute_local_builder.py:43: OMNI_URL = os.environ.get("OMNIROUTE_BASE_URL", "http://127.0.0.1:20128").rstrip("/")
    harness-ports/bin/omniroute_local_builder.py:44: LOCAL_URL = os.environ.get("QWEN_OMNI_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
    harness-ports/bin/omniroute_local_builder.py:45: NODE_NAME = os.environ.get("QWEN_OMNI_NODE", "qwen-local")           # the node name AND the model-i
    harness-ports/bin/omniroute_local_builder.py:46: ALIAS = os.environ.get("QWEN_ALIAS", "qwen3.8-27b-local")             # what llama-server --alias se
    harness-ports/bin/omniroute_local_builder.py:47: COMBO_NAME = os.environ.get("QWEN_OMNI_COMBO", "agentfactory-build-local")
    harness-ports/bin/omniroute_local_builder.py:48: BASE_COMBO = os.environ.get("QWEN_OMNI_BASE_COMBO", "agentfactory-build")   # its members follow the
    ... +3
AF-AP-40: 1
    harness-ports/bin/omniroute_local_builder.py:324: server_key = KEY_FILE.read_text().strip() if KEY_FILE.is_file() else None

## graft ask — how does qwen-server.sh build the ExecStart from the QWEN_* knobs, how does it refuse to restart under a live lane, and what does install/restart do
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).
graft ask — "how does qwen-server.sh build the ExecStart from the QWEN_* knobs, how does it refuse to restart under a live lane, and what does install/restart do"  (lexical)

1. build-roles.py · file  [symbol]
   harness-ports/bin/build-roles.py

2. main · function  [symbol]
   harness-ports/bin/omniroute_local_builder.py:L317-L336
   def main(argv=None) -> int

3. _scrub · function  [symbol]
   harness-ports/bin/hermes-session-export.py:L25-L29
   def _scrub()

4. hermes-hook-adapter.py · file  [symbol]
   harness-ports/bin/hermes-hook-adapter.py

5. omni_api.mjs · file  [symbol]
   harness-ports/bin/omni_api.mjs

6. hermes-config-merge.py · file  [symbol]
   harness-ports/bin/hermes-config-merge.py

7. parse_search · function  [symbol]
   harness-ports/bin/codex-hook-adapter.py:L96-L132
   def parse_search(cmd: str) -> dict | None

8. build · function  [symbol]
   harness-ports/bin/build-roles.py:L71-L87
   def build(root: Path) -> dict[Path, str]

## symbol render_exec
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching 'render_exec'.",
  "summary": "No node found matching 'render_exec'.",
### ripwire callers

## symbol install
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "'install' matches 127 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "check_diffdock_installation",
      "name": "print_installation_instructions",
      "name": "test_has_installation_instructions",
      "name": "get_installed_components",
      "name": "list_installed",
      "name": "test_add_components_already_installed",
      "name": "test_get_installed_components_empty",
      "name": "test_get_installed_components_no_config",
      "name": "test_get_installed_components_with_files",
      "name": "test_list_installed_empty",
      "name": "test_list_installed_no_config",
  "summary": "'install' matches 127 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "check_diffdock_installation",
      "name": "print_installation_instructions",
      "name": "test_has_installation_instructions",
      "name": "get_installed_components",
      "name": "list_installed",
      "name": "test_add_components_already_installed",
      "name": "test_get_installed_components_empty",
      "name": "test_get_installed_components_no_config",
      "name": "test_get_installed_components_with_files",
      "name": "test_list_installed_empty",
      "name": "test_list_installed_no_config",
### ripwire callers
<callers of="install" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=install">

## symbol restart
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "'restart' matches 2 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "/home/user/agent-factory/proofs/S0-01/tools/pc/pc_backend_restart.sh",
      "name": "test_worker_restart_rehydrates_context_and_callbacks",
      "name": "/home/user/agent-factory/proofs/S0-01/tools/pc/pc_backend_restart.sh",
      "name": "test_worker_restart_rehydrates_context_and_callbacks",
  "summary": "'restart' matches 2 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "/home/user/agent-factory/proofs/S0-01/tools/pc/pc_backend_restart.sh",
      "name": "test_worker_restart_rehydrates_context_and_callbacks",
      "name": "/home/user/agent-factory/proofs/S0-01/tools/pc/pc_backend_restart.sh",
      "name": "test_worker_restart_rehydrates_context_and_callbacks",
### ripwire callers

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
