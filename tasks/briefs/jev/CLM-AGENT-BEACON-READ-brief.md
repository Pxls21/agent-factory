# STATIC READ: Contrastive-LM/CLM and Asymptote-Labs/agent-beacon (task #222, D-069 item 6)

**Role:** evidence-gatherer (Opus 5.5, sandbox). EVIDENCE ONLY: what each repository is and does, measured from its files.
No verdict on adoption; the coordinator decides. The owner's framing: CLM is "8B but could be leveraged later";
agent-beacon "might be worth looking at". Context: our System-1 models are Laya (a ~421M BERT-class scorer on the PC's CPU)
and MoJev (a 16k-token typed-decision scorer); our observability plane is Phoenix + OpenObserve on the PC
(`docs/OBSERVABILITY-RUNBOOK.md`); our supervision layer ideas are canny (`docs/research/findings/`, grep canny) and the
Claude Code hooks under `.claude/hooks/`.

## Steps and limits
1. `df -h /home/user` first. Clone ONE repo at a time, shallow, LFS skipped, with a long timeout:
   `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/Contrastive-LM/clm /home/user/contrastive-lm/clm`
   `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/Asymptote-Labs/agent-beacon /home/user/asymptote-labs/agent-beacon`
   If free disk would fall under 800 MB, stop and report instead. Record each HEAD sha.
2. STATIC READING ONLY. Never execute, import, install, build or `pip install` anything from these repositories. No
   network calls other than the two clones.
3. At the end, delete both clones (`rm -rf` those two paths only) and confirm with `df`.

## Evidence to collect (tables, file:line)
Per repository: purpose (README claims) against what the code actually does; license; languages and size; last commit
date; tests and CI present or not; dependencies; the public API or entry points; configuration; what data it collects
and where it sends data (network egress: hosts, ports, env vars); security-relevant behavior (credentials it reads, files
it writes, shell it runs).
- CLM: architecture, parameter count, context length, training objective, where the weights live (LFS, Hugging Face id),
  inference requirements (GPU memory, CPU feasibility), published evaluations with their datasets and whether numbers are
  reproducible from the repo; any scoring / embedding / classification head (the capability Jev-class use would need).
- agent-beacon: what it instruments (which agent harnesses: Claude Code hooks? Codex? OpenTelemetry?), its data model,
  its storage and UI, how it would attach to a Claude Code session, and overlaps with our hooks, canny, Phoenix/OpenObserve.
Mark every capability claim as MEASURED-IN-REPO (a test, a benchmark script with outputs) or CLAIMED-ONLY.

## Deliverable
ONE file: `docs/research/findings/CLM-AGENT-BEACON-READ-2026-09-24.md` (under ~40 KB; header: date, your model, the two
HEAD shas). Do not commit. Write nothing else in our repository.

## Constraints (standing)
No commits, pushes, GitHub writes, PRs or comments; no PC bridge use; do NOT spawn subagents; never print a secret.
Every claim carries a file:line in the cloned repo or a pasted command with its output.
