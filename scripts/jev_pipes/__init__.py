"""Jev pipelines (JEV-FIT plan, docs/research/findings/jev-fit/PLAN-2026-09-25.md): rank, collect, present.

P1 (task #231, seed seeds/seed-jev-pipes-p1-v1.yaml) is the replay of the vendored jev-pruner over this session's recorded
tool results: `replay_pruner.py` (the command), `transcript.py` (the records), `accounting.py` (saved, misses, net, verdict)
and `bridge.mjs` (the Node side that calls the pruner's own `trimOutput`). Advisory: nothing here is a gate.
"""
