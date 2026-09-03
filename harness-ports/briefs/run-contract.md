# BRIEF — run every contract item and report DATA (role: contract-runner, route agentfactory-sweep)
PIN: {PIN}

Mechanical lane. You execute; you do not judge. Contract: `{CONTRACT_FILE}` items {CONTRACT_ITEMS}. First action: `pwd && git rev-parse HEAD` equals the PIN. Interpreter: `$HOME/venv-agent-factory/bin/python`. No edits, no commits, no pushes, no subagents.

For EACH item: run its literal command(s) exactly as written (or the obvious literal reading — if an item has no runnable command, write `NOT-RUNNABLE: <why>`), paste the invocation and the decisive output lines, and mark PASS/FAIL by the item's own stated criterion. Append each finished item to `$LANE_REPORT_DRAFT` as you go.

Report: a table `item | PASS/FAIL/NOT-RUNNABLE | command | decisive output`, then `NOT-done`. No prose.
