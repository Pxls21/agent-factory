#!/usr/bin/env python3
"""heads.py — the heads of the first S1 training (task #441): the configurations, the folds, the fits and their
probabilities (docs/research/findings/s1-train/PREREG-441.md §3; brief tasks/briefs/jev-laya/S4-3-HEADS-brief.md E-2
to E-4). scripts/s1_train/evaluate.py, the one evaluator, chooses among the configurations and scores the choice.

The module imports no torch, so CI runs the configurations and the folds. A fit imports torch when it runs (the Laya
venv in the sandbox, the PC's venv-rwkv-b): one CPU thread, deterministic algorithms, torch.manual_seed(seed + fold)
before the fit and a torch.Generator with the same seed for the batch order, so one Python gives the same
probabilities on every run. A held-out row in a fit's training rows or in the fold it scores is refused (HeldOut).
Held-out rows are only scored, by score_heldout; their probability is the mean of the five fold models'.
"""
import datetime
import math


class Refused(Exception):
    """An input the heads do not accept; the reason is the message."""


class HeldOut(Exception):
    """A held-out row handed to a fit's training rows or to the fold it scores."""


# the inputs each family reads (§3) and what C2 and C3 read instead (§5); A's C2 zeroes s after standardization
INPUTS = {("A", "full"): ("s", "c_free"), ("A", "C2"): ("s", "c_free"), ("A", "C3"): ("s_w", "c_free"),
          ("B", "full"): ("c_ctx",), ("B", "C2"): ("c_free",), ("B", "C3"): ("c_ctx_w",),
          ("C", "full"): ("q_ctx",), ("C", "C2"): ("q_free",), ("C", "C3"): ("q_ctx_w",)}
FREE = ("c_free", "q_free")   # keyed by the row's candidate sha256, not by the row id


def is_int(v, low):
    return isinstance(v, int) and not isinstance(v, bool) and v >= low


def is_real(v):
    """A finite int or float, never a bool (a NaN compares false with everything, so it would pass a check)."""
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _pos(v):
    return is_real(v) and v > 0


def _nonneg(v):
    return is_real(v) and v >= 0


def _rate(v):
    return is_real(v) and 0 <= v < 1


def _int(low):
    return lambda v: is_int(v, low)


def _list(ok):
    return lambda v: isinstance(v, list) and v != [] and all(ok(x) for x in v)


def _field(d, key, ok, where):
    if not isinstance(d, dict) or key not in d or not ok(d[key]):
        raise Refused("grid: %s.%s is missing or not valid" % (where, key))
    return d[key]


def configurations(grid):
    """The configurations of §3 in the order it writes them (brief E-2): A by hidden layers, then learning rate, then
    epochs; then B (i) by λ and B (ii) by epochs; then C the same ("C": "same as B" takes B's grid). Each name is built
    from its values, so it is stable across runs."""
    if not isinstance(grid, dict) or set(grid) != {"A", "B", "C"}:
        raise Refused("grid: the keys must be exactly A, B and C")
    a = grid["A"]
    common = {k: _field(a, k, ok, "A") for k, ok in (
        ("hidden_width", _int(1)), ("out_dim", _int(1)), ("dropout", _rate), ("batch", _int(1)),
        ("weight_decay", _nonneg), ("logit_scale_init", is_real), ("logit_scale_max", _pos))}
    out = []
    for h in _field(a, "hidden_layers", _list(_int(1)), "A"):
        for lr in _field(a, "lr", _list(_pos), "A"):
            for e in _field(a, "epochs", _list(_int(1)), "A"):
                out.append(dict(common, name="A-h%d-lr%r-e%d" % (h, lr, e), family="A", head="pair",
                                hidden_layers=h, lr=lr, epochs=e))
    for fam in ("B", "C"):
        g = grid["B"] if fam == "C" and grid["C"] == "same as B" else grid[fam]
        steps = _field(g, "logreg_lbfgs_steps", _int(1), fam)
        for lam in _field(g, "logreg_l2", _list(_nonneg), fam):
            out.append({"name": "%s-logreg-l2_%r" % (fam, lam), "family": fam, "head": "logreg", "l2": lam,
                        "steps": steps})
        m = _field(g, "mlp", lambda v: isinstance(v, dict), fam)
        mlp = {k: _field(m, k, ok, fam + ".mlp") for k, ok in (
            ("hidden_width", _int(1)), ("dropout", _rate), ("lr", _pos), ("weight_decay", _nonneg),
            ("batch", _int(1)))}
        for e in _field(m, "epochs", _list(_int(1)), fam + ".mlp"):
            out.append(dict(mlp, name="%s-mlp-e%d" % (fam, e), family=fam, head="mlp", epochs=e))
    if len({c["name"] for c in out}) != len(out):
        raise Refused("grid: two configurations share a name")
    return out


def when(text):
    """A view row's ISO `time` as a datetime; refused when it does not parse. A trailing Z is read as +00:00, which
    Python reads before 3.11 too (the PC's venv may be older than the sandbox's 3.11)."""
    if isinstance(text, str):
        try:
            return datetime.datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
        except ValueError:
            pass
    raise Refused("time %r is not an ISO time" % (text,))


def folds(rows, k):
    """{id: part} for `rows` ({id: {"split", "kind", "time"}}, training rows only: a held-out row is refused): each
    kind's rows sorted by (time, id) and cut into k contiguous parts as equal as possible, the first parts one row
    longer (a kind with three rows fills parts 0 to 2); fold j is every kind's part j (§3)."""
    by_kind = {}
    for i in sorted(rows):
        if rows[i]["split"] != "train":
            raise HeldOut("folds: %s is a held-out row" % i)
        by_kind.setdefault(rows[i]["kind"], []).append((when(rows[i]["time"]), i))
    out = {}
    for kind in sorted(by_kind):
        try:
            seq = sorted(by_kind[kind])
        except TypeError:
            raise Refused("folds: the times of kind %s mix naive and aware values" % kind)
        q, extra = divmod(len(seq), k)
        start = 0
        for part in range(k):
            end = start + q + (1 if part < extra else 0)
            for _, i in seq[start:end]:
                out[i] = part
            start = end
    return out


class Data:
    """The rows and the feature matrices a fit reads; scripts/s1_train/evaluate.py builds it from checked inputs.
    `rows` maps a view row id to {"split", "label", "kind", "time", "cand" (its candidate's sha256), "state" (its src
    and state_end)}; `mats` maps an array name to a features.Matrix. The folds are cut here, once."""

    def __init__(self, rows, mats, k, seed, std_floor):
        self.rows, self.mats, self.k, self.seed, self.floor = rows, mats, k, seed, std_floor
        self.ids = sorted(rows)
        self.train_ids = [i for i in self.ids if rows[i]["split"] == "train"]
        self.heldout_ids = [i for i in self.ids if rows[i]["split"] == "heldout"]
        self.fold_of = folds({i: rows[i] for i in self.train_ids}, k)
        self.pos = {i: n for n, i in enumerate(self.ids)}
        cand, state = {}, {}
        self.cand_code = {i: cand.setdefault(rows[i]["cand"], len(cand)) for i in self.ids}
        self.state_code = {i: state.setdefault(rows[i]["state"], len(state)) for i in self.ids}
        self._tensors = {}

    def tensor(self, torch, name):
        """The array `name` as one float64 row per view row, in id order (a free array by the row's candidate)."""
        if name not in self._tensors:
            keys = [self.rows[i]["cand"] for i in self.ids] if name in FREE else self.ids
            m = self.mats[name]
            self._tensors[name] = torch.tensor([m.get(key) for key in keys], dtype=torch.float64)
        return self._tensors[name]


def _torch():
    import torch
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    return torch


def _no_heldout(data, ids, what):
    for i in ids:
        if data.rows[i]["split"] != "train":
            raise HeldOut("%s: %s is a held-out row" % (what, i))


def _batches(torch, n, batch, epochs, seed):
    """E-4's batch order: a torch.Generator seeded with the fit's seed, a fresh permutation of the n rows per epoch,
    cut into batches of `batch`, the last partial batch kept."""
    g = torch.Generator()
    g.manual_seed(seed)
    for _ in range(epochs):
        order = torch.randperm(n, generator=g)
        for start in range(0, n, batch):
            yield order[start:start + batch]


def _inputs(torch, data, fit, idx):
    """The fit's inputs for the rows at `idx`, standardized with its training rows' mean and standard deviation."""
    xs = [((data.tensor(torch, n)[idx] - mu) / sd).to(torch.float32) for n, (mu, sd) in zip(fit["names"], fit["stats"])]
    if fit["config"]["family"] == "A" and fit["variant"] == "C2":
        xs[0] = torch.zeros_like(xs[0])   # §5 C2 for A: zeros for s after standardization
    return xs


def _tower(nn, d, cfg):
    """E-4: Linear(d, width) -> LayerNorm -> GELU -> Dropout per hidden layer (Linear(width, width) after the first),
    then Linear(width, out_dim)."""
    w, layers = cfg["hidden_width"], []
    for n in range(cfg["hidden_layers"]):
        layers += [nn.Linear(d if n == 0 else w, w), nn.LayerNorm(w), nn.GELU(), nn.Dropout(cfg["dropout"])]
    return nn.Sequential(*layers, nn.Linear(w, cfg["out_dim"]))


def _pair(torch, model, s, c, cfg):
    """The L2-normalized state and action embeddings and exp(t), clamped at logit_scale_max (E-4)."""
    F = torch.nn.functional
    scale = model.t.exp().clamp(max=cfg["logit_scale_max"])
    return F.normalize(model.state(s), dim=-1), F.normalize(model.action(c), dim=-1), scale


def pair_loss(torch, L, y, a, b, cand, state):
    """Family A's loss on one batch (E-4). L[i, j] = exp(t) <state_i, action_j>. Over the batch's yes rows Y (|Y| < 2
    gives 0): state to action -log(exp(L[i,i]) / sum_j exp(L[i,j])) and action to state -log(exp(L[i,i]) /
    sum_j exp(L[j,i])), j over Y where j = i or row j shares neither the candidate nor the state with row i; their
    mean, plus the BCE of sigmoid(a L[i,i] + b) against the label over every batch row."""
    diag = L.diagonal()
    bce = torch.nn.functional.binary_cross_entropy_with_logits(a * diag + b, y)
    yes = torch.nonzero(y > 0.5).flatten()
    if yes.numel() < 2:
        return bce
    ly = L[yes][:, yes]
    cy, sy = cand[yes], state[yes]
    keep = ((cy[:, None] != cy[None, :]) & (sy[:, None] != sy[None, :])) | torch.eye(len(yes), dtype=torch.bool)
    masked = ly.masked_fill(~keep, float("-inf"))
    d = ly.diagonal()
    return ((torch.logsumexp(masked, dim=1) - d).mean() + (torch.logsumexp(masked, dim=0) - d).mean()) / 2 + bce


def train(config, data, labels, ids, fold, variant="full"):
    """Fit `config` on the training rows `ids` with `labels` ({id: bool}) and return the fit (§3, E-3, E-4). The seed is
    the block's cv seed plus `fold`. A held-out row in `ids` is refused before torch is imported."""
    _no_heldout(data, ids, "train")
    if not ids:
        raise Refused("train: no training rows")
    torch = _torch()
    nn, F = torch.nn, torch.nn.functional
    seed = data.seed + fold
    torch.manual_seed(seed)
    names = INPUTS[(config["family"], variant)]
    idx = torch.tensor([data.pos[i] for i in ids], dtype=torch.long)
    stats = []
    for name in names:
        x = data.tensor(torch, name)[idx]
        mu = x.mean(0)
        stats.append((mu, ((x - mu) ** 2).mean(0).sqrt().clamp(min=data.floor)))
    fit = {"config": config, "variant": variant, "fold": fold, "names": names, "stats": stats}
    xs = _inputs(torch, data, fit, idx)
    y = torch.tensor([1.0 if labels[i] else 0.0 for i in ids], dtype=torch.float32)
    d, head = xs[0].shape[1], config["head"]
    if head == "pair":
        model = nn.Module()
        model.state = _tower(nn, d, config)
        model.action = _tower(nn, xs[1].shape[1], config)
        model.t = nn.Parameter(torch.tensor(float(config["logit_scale_init"])))
        model.a = nn.Parameter(torch.tensor(1.0))
        model.b = nn.Parameter(torch.tensor(0.0))
        cand = torch.tensor([data.cand_code[i] for i in ids], dtype=torch.long)
        state = torch.tensor([data.state_code[i] for i in ids], dtype=torch.long)
        opt = torch.optim.AdamW(model.parameters(), lr=config["lr"], weight_decay=config["weight_decay"])
        model.train()
        for bi in _batches(torch, len(ids), config["batch"], config["epochs"], seed):
            s, c, scale = _pair(torch, model, xs[0][bi], xs[1][bi], config)
            loss = pair_loss(torch, scale * s @ c.T, y[bi], model.a, model.b, cand[bi], state[bi])
            opt.zero_grad()
            loss.backward()
            opt.step()
    elif head == "logreg":
        model = nn.Linear(d, 1)
        opt = torch.optim.LBFGS(model.parameters(), max_iter=config["steps"], line_search_fn="strong_wolfe")

        def closure():
            opt.zero_grad()
            loss = (F.binary_cross_entropy_with_logits(model(xs[0]).squeeze(1), y)
                    + config["l2"] * model.weight.pow(2).sum())   # λ ||w||², not the bias (E-4)
            loss.backward()
            return loss
        opt.step(closure)
    else:
        model = nn.Sequential(nn.Linear(d, config["hidden_width"]), nn.GELU(), nn.Dropout(config["dropout"]),
                              nn.Linear(config["hidden_width"], 1))
        opt = torch.optim.AdamW(model.parameters(), lr=config["lr"], weight_decay=config["weight_decay"])
        model.train()
        for bi in _batches(torch, len(ids), config["batch"], config["epochs"], seed):
            loss = F.binary_cross_entropy_with_logits(model(xs[0][bi]).squeeze(1), y[bi])
            opt.zero_grad()
            loss.backward()
            opt.step()
    fit["model"] = model
    return fit


def _probs(fit, data, ids):
    torch = _torch()
    idx = torch.tensor([data.pos[i] for i in ids], dtype=torch.long)
    xs = _inputs(torch, data, fit, idx)
    model, cfg = fit["model"], fit["config"]
    model.eval()
    with torch.no_grad():
        if cfg["head"] == "pair":
            s, c, scale = _pair(torch, model, xs[0], xs[1], cfg)
            z = model.a * (scale * (s * c).sum(-1)) + model.b   # P(yes) = sigmoid(a L[i,i] + b)
        else:
            z = model(xs[0]).squeeze(1)
        probs = torch.sigmoid(z).tolist()
    for p in probs:
        if not (math.isfinite(p) and 0.0 <= p <= 1.0):
            raise Refused("%s fold %d: a probability is not finite" % (cfg["name"], fit["fold"]))
    return dict(zip(ids, probs))


def score(fit, data, ids):
    """The fit's probabilities for the training rows of its own fold; a held-out row is refused."""
    _no_heldout(data, ids, "score")
    return _probs(fit, data, ids)


def score_heldout(fit, data, ids):
    """The fit's probabilities for held-out rows (and only those)."""
    for i in ids:
        if data.rows[i]["split"] != "heldout":
            raise Refused("score_heldout: %s is a training row" % i)
    return _probs(fit, data, ids)


def fit_fold(config, data, labels, fold, variant="full"):
    """Fold `fold`'s model: trained on the other folds' rows; its probabilities for its own fold's rows ("fold") and
    for every held-out row ("heldout")."""
    train_ids = [i for i in data.train_ids if data.fold_of[i] != fold]
    own = [i for i in data.train_ids if data.fold_of[i] == fold]
    fit = train(config, data, labels, train_ids, fold, variant)
    return {"fold": score(fit, data, own), "heldout": score_heldout(fit, data, data.heldout_ids)}


def cross_validate(config, data, labels, variant="full"):
    """§3 for one configuration: every training row's out-of-fold probability from the fold model that did not train
    on it ("oof"), and each held-out row's mean over the k fold models ("heldout"); nothing is retrained on all rows."""
    oof, per = {}, []
    for k in range(data.k):
        r = fit_fold(config, data, labels, k, variant)
        oof.update(r["fold"])
        per.append(r["heldout"])
    return {"oof": oof, "heldout": {i: math.fsum(p[i] for p in per) / len(per) for i in data.heldout_ids}}
