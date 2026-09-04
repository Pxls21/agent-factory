# ADR 0005 — Foundry host: first-party minimal translator

- Status: accepted
- Date: 2026-09-04

## Context

The JIT Harness Foundry generates five source files per candidate:

- `memory.py`
- `planning.py`
- `action.py`
- `tool_policy.py`
- `prompt.yaml`

These files need a host to load, normalize, and execute them inside the evaluation sandbox.

## Alternatives considered

### Option A: First-party minimal host

A small translator written and owned by the project.

### Option B: OpenHarness interface extraction

Extract a limited subset of interface patterns from OpenHarness.

### Option C: Pinned, hardened OpenHarness derivative

Pin a full OpenHarness release and harden it.

## Decision

Use option A: a first-party minimal host that loads the five JIT output files (`memory.py`, `planning.py`, `action.py`, `tool_policy.py`, `prompt.yaml`).
