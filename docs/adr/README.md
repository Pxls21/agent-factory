# Architecture decision records

The compact decision table is in `docs/08_DECISION_LOG.md`. Add a numbered ADR here when a decision changes a trust boundary, data model, selected component, or operational contract.

Status values: proposed, accepted, superseded, rejected.

Current accepted records:

- 0001: Hermes is the sole stock production runtime; ACP and the surrounding stack remain.
- 0002: OmniRoute is the sole model/embedding API egress.
- 0003: Four logical memory scopes are composed over ai-memory.
- 0004: Dream and JIT Foundry planes are isolated proposal/candidate producers.
