"""First-party passive decision ledger (J1, the Laya layer's capture spine).

J1-1 lands the closed state schemas (volatile), the
normalize -> redact -> canonical -> sha256 pipeline and the golden digests
(canonical). The append-only ledger and the harvest arrive in J1-2/J1-3.

NOTE on names: the `canonical` attribute here is the MODULE
(`agent_factory.decisions.canonical`), not the function -- the function
`canonical()` is imported from that module (re-exporting it would shadow the
module and make `import agent_factory.decisions.canonical as m` bind a
function, bpo-17636). The pipeline entry point is `state_digest`.
"""

from agent_factory.decisions.volatile import (  # noqa: F401 (re-exported)
    DecisionStateError,
    normalize,
    redact,
)
from agent_factory.decisions.canonical import state_digest  # noqa: F401

__all__ = ["DecisionStateError", "normalize", "redact", "state_digest"]
