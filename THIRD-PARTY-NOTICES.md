# Third-Party Notices — Agent Factory

This file lists every upstream dependency pinned in `upstream.lock.yaml` and its license.
Agent Factory's own first-party license is pending (see `LICENSE-DECISION.md`).

## Selected core

| Component | License | Repository |
|---|---|---|
| agent-client-protocol | Apache-2.0 | https://github.com/agentclientprotocol/agent-client-protocol.git |
| hermes-agent | MIT | https://github.com/NousResearch/hermes-agent.git |
| buzz | Apache-2.0 | https://github.com/block/buzz.git |
| omniroute | MIT | https://github.com/diegosouzapw/OmniRoute.git |
| fubuki-os | Apache-2.0 | https://github.com/NerdHerderDani/fubuki-os.git |
| ai-memory | MIT | https://github.com/akitaonrails/ai-memory.git |
| gvisor | Apache-2.0 | https://github.com/google/gvisor.git |

## Selected later planes

| Component | License | Repository |
|---|---|---|
| jit | MIT | https://github.com/bingreeky/JIT.git |
| gbrain | MIT | https://github.com/garrytan/gbrain.git |
| harnessrouter | Apache-2.0 | https://github.com/HarnessRouter/harnessrouter.git |
| openharness | MIT | https://github.com/HKUDS/OpenHarness.git |
| alphaeval | MIT | https://github.com/GAIR-NLP/AlphaEval.git |
| pandaprobe | Apache-2.0 | https://github.com/chirpz-ai/pandaprobe.git |

## Development and reference

| Component | License | Repository |
|---|---|---|
| ast-grep | MIT | https://github.com/ast-grep/ast-grep.git |
| comby | Apache-2.0 | https://github.com/comby-tools/comby.git |
| openbot | MIT | https://github.com/CopilotKit/OpenBot.git |

## Not selected as stock runtimes (audited, pinned for reference)

| Component | License | Repository |
|---|---|---|
| codex-acp | Apache-2.0 | https://github.com/agentclientprotocol/codex-acp.git |
| claude-agent-acp | Apache-2.0 | https://github.com/agentclientprotocol/claude-agent-acp.git |
| pi-acp | MIT | https://github.com/svkozak/pi-acp.git |
| codex-cli | Apache-2.0 | https://github.com/openai/codex.git |
| claude-code | (see repo) | https://github.com/anthropics/claude-code.git |
| pi | (see repo) | https://github.com/earendil-works/pi.git |

## Attribution obligations

All selected dependencies use permissive licenses (MIT or Apache-2.0). When Agent Factory
distributes code that includes or links against these dependencies:

- **MIT**: retain the copyright notice and license text in distributions.
- **Apache-2.0**: retain NOTICE files (if any), the license text, and state changes made.

No copyleft obligations apply to any currently selected dependency.
