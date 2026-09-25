"""Laya's window fit, one function for training and serving (task #265, K265 contract rev 2; AF-AP-208).

`build_dataset.Fitter.fit` (every state of the fine-tune dataset) and `scripts/laya_systemone_server.py` (every per-chunk
state of its fan-out) both call `fit_state`, so the local server serves the shape the model was trained on, cut the way
training cut it. `fit_state(tok, q, max_len, head_max_len, state) -> (state, cuts)`:
- the state unchanged (the same object) when `laya.common.build_sequence`, called as `Agent.system_one` calls it, keeps
  all of it: the built length equals the empty-state length plus the state's own token count (the builder's verdict);
- otherwise a string state is cut to its longest fitting prefix. A dict's fields other than `chunk` are cut, the longest
  serialized value first (a tie in the dict's order): a string to its longest fitting prefix, a list to its longest
  fitting prefix of whole entries, by the dataset builder's own binary search; a field whose empty value still does not
  fit is emptied and the next field is cut, until the whole state fits. A field that is neither a string nor a list is
  kept whole; the key order is kept;
- `chunk` is never cut: `Unfit` (a ValueError) when the state does not fit with every other field empty.
`cuts` lists (field, length before, length after) for each field cut, in cut order (field None for a string state).
Importing this module needs only the standard library; laya is imported when a fit runs (the Laya venv).
"""
import json


class Unfit(ValueError):
    """The chunk does not fit Laya's window even with every other field empty. The message is the dataset builder's
    (`Fitter.fit` before this module); `kept` and `own` measure that emptied state (tokens kept, tokens it has)."""

    def __init__(self, chunk, kept, own):
        super().__init__("the chunk alone overflows Laya's window: %r" % (chunk[:80],))
        self.kept, self.own = kept, own


def _laya_builder():
    """laya.common's builder and serializer (the Laya venv); the model-free tests replace this function."""
    from laya.common import build_sequence, serialize_state
    return build_sequence, serialize_state


def _longest_prefix(value, state_with, fits):
    """The dataset builder's search: the n it finds with state_with(value[:n]) fitting, given that value[:0] fits and the
    whole value does not (a string by characters, a list by whole entries)."""
    lo, hi = 0, len(value)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if fits(state_with(value[:mid])):
            lo = mid
        else:
            hi = mid
    return lo


def fit_state(tok, q, max_len, head_max_len, state):
    """-> (state, cuts); see the module docstring. `q` is the internal question (`Agent._to_internal`)."""
    build_sequence, serialize_state = _laya_builder()
    empty = len(build_sequence(tok, "", q, max_len, head_max_len)[0])

    def measure(s):   # (kept, own): the state tokens build_sequence keeps, and the state's own token count
        own = len(tok(serialize_state(s).replace(tok.mask_token, " "), add_special_tokens=False)["input_ids"])
        return len(build_sequence(tok, s, q, max_len, head_max_len)[0]) - empty, own

    def fits(s):
        kept, own = measure(s)
        return kept == own

    if fits(state):
        return state, []
    if isinstance(state, str):
        n = _longest_prefix(state, lambda v: v, fits)
        return state[:n], [(None, len(state), n)]
    cur, cuts = dict(state), []
    fields = [k for k in state if k != "chunk" and isinstance(state[k], (str, list))]
    fields.sort(key=lambda k: len(json.dumps(state[k], ensure_ascii=False)), reverse=True)   # stable: ties keep order
    for k in fields:
        def state_with(v, k=k):
            s = dict(cur)
            s[k] = v
            return s
        whole = cur[k]
        if fits(state_with(whole[:0])):
            n = _longest_prefix(whole, state_with, fits)
            cur[k] = whole[:n]
            cuts.append((k, len(whole), n))
            return cur, cuts
        cur[k] = whole[:0]
        cuts.append((k, len(whole), 0))
    kept, own = measure(cur)
    raise Unfit(state.get("chunk", ""), kept, own)
