"""Local OpenAI-compatible embedding server for slopo (the semantic-duplicate detector; ADVISORY, never a gate).

Serves POST /v1/embeddings and GET /health on 127.0.0.1, backed by the official jinaai/jina-embeddings-v2-base-code
quantized ONNX (int8), mean-pooled over the attention mask (the model's 1_Pooling config). slopo reaches it through
LiteLLM's openai-compatible provider (slopo.conf.yaml: embedding_params.api_base). No API key; no code leaves the box;
CPU only.

PROVENANCE: ported from the owner's trading-system repository (github.com/Pxls21/trading-system, branch clean-build,
commit 3e332ce3a5a7affa49b52f3e83e4e0d42fcc464f, scripts/slopo_embed_server.py, sha256
ad91eed070a8c4d877af15967e476e74ff453de812b38d69a420aeee0e1a264d) by INSTALL1 (D-090, 2026-09-25). This is the
owner's code, not slopo's: slopo (AGPL-3.0-or-later) stays a pinned external tool in its own venv, and none of its
source is copied here. Changes from the source:
  - the model dir, the port and the tuning knobs are command-line flags (the source hard-coded them);
  - --workers N embeds N texts at once, each still alone in its own ONNX run (the source ran them one after another);
    --threads N sets onnxruntime's intra-op thread count per run (0 = onnxruntime's own default, the source's);
  - the tokenizer's padding is switched off explicitly, so a text's ids never depend on the other texts in a request;
  - usage.prompt_tokens is counted from the encodings already made (the source tokenized every text twice).
One text per ONNX run is kept on purpose: padding a text changes its int8 embedding (INSTALL1 report, section 3), so a
padded batch would make a vector depend on what it was batched with. The source behaviour is
--threads 0 --workers 1 --max-tokens 4096; the defaults below are the measured tuning (INSTALL1 report, section 3).

Run (the slopo venv; scripts/setup.sh builds it; scripts/slopo_review.sh starts and stops it around each embed):
  ~/venv-slopo/bin/python scripts/slopo_embed_server.py [--port 8811] [--model-dir DIR] [--threads N]
                                                          [--workers N] [--max-tokens N]
Model files: .slopo-runtime/model/{model_quantized.onnx,tokenizer.json}, pinned in upstream.lock.yaml
(advisory_models.jina-embeddings-v2-base-code) and downloaded and digest-checked by scripts/setup.sh.
Health probe: GET /health (NOT /v1/models, which this server does not serve; a 404 there is not a down server).

Truncation: inputs are clipped to --max-tokens. A function long enough to hit it is embedded by its head, which is
acceptable for duplicate detection (the head carries the signature and the setup); noted so nobody mistakes
tail-blindness for a model defect.
"""
from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import onnxruntime as ort
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from tokenizers import Tokenizer

DEFAULT_MODEL_DIR = Path(__file__).resolve().parent.parent / ".slopo-runtime" / "model"
DEFAULT_PORT = 8811
# jina v2 supports 8192 (ALiBi). 1024 was measured against 4096 on this repository's 1,334 units: 40 of them are longer
# and embed from their head, the cluster table stayed the same, and a 4-worker embed peaked at 1.8 GB, not 4.6 GB.
DEFAULT_MAX_TOKENS = 1024
DEFAULT_THREADS = 1         # one intra-op thread per run; the workers give the parallelism
DEFAULT_WORKERS = len(os.sched_getaffinity(0))   # the CPUs this process may run on (what nproc prints)
MODEL_ID = "jina-embeddings-v2-base-code-onnx-q8"


class EmbeddingRequest(BaseModel):
    input: list[str] | str
    model: str = "jina-code-onnx"


class Embedder:
    def __init__(self, model_dir: Path, max_tokens: int, threads: int, workers: int):
        self.tokenizer = Tokenizer.from_file(str(model_dir / "tokenizer.json"))
        self.tokenizer.enable_truncation(max_length=max_tokens)
        self.tokenizer.no_padding()
        options = ort.SessionOptions()
        options.intra_op_num_threads = threads
        self.session = ort.InferenceSession(
            str(model_dir / "model_quantized.onnx"), options, providers=["CPUExecutionProvider"]
        )
        # onnxruntime sessions take concurrent run() calls; each text still runs alone, in its own tensor.
        self.pool = ThreadPoolExecutor(max_workers=workers) if workers > 1 else None

    def _run(self, encoding) -> list[float]:
        ids = np.array([encoding.ids], dtype=np.int64)
        mask = np.array([encoding.attention_mask], dtype=np.int64)
        (hidden,) = self.session.run(["last_hidden_state"], {"input_ids": ids, "attention_mask": mask})
        # Mean pooling over the attention mask (the model's 1_Pooling config).
        m = mask[..., None].astype(np.float32)
        pooled = (hidden * m).sum(axis=1) / np.clip(m.sum(axis=1), 1e-9, None)
        return pooled[0].astype(float).tolist()

    def embed(self, texts: list[str]) -> tuple[list[list[float]], int]:
        encodings = self.tokenizer.encode_batch(texts)
        # Longest first, so the workers finish together; the output keeps the request's order.
        order = sorted(range(len(texts)), key=lambda i: -len(encodings[i].ids))
        runs = (self.pool.map if self.pool else map)(self._run, [encodings[i] for i in order])
        out: list[list[float]] = [[] for _ in texts]
        for i, vec in zip(order, runs):
            out[i] = vec
        return out, sum(len(e.ids) for e in encodings)


def build_app(embedder: Embedder, settings: dict) -> FastAPI:
    app = FastAPI()

    @app.post("/v1/embeddings")
    def embeddings(req: EmbeddingRequest):
        texts = [req.input] if isinstance(req.input, str) else req.input
        t0 = time.time()
        vecs, tokens = embedder.embed(texts)
        return {
            "object": "list",
            "model": req.model,
            "data": [{"object": "embedding", "index": i, "embedding": v} for i, v in enumerate(vecs)],
            "usage": {"prompt_tokens": tokens, "total_tokens": 0, "server_ms": int((time.time() - t0) * 1000)},
        }

    @app.get("/health")
    def health():
        return {"status": "ok", "model": MODEL_ID, **settings}

    return app


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    p.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    p.add_argument("--threads", type=int, default=DEFAULT_THREADS)
    p.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    p.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    a = p.parse_args(argv)
    if a.threads < 0 or a.workers < 1 or a.max_tokens < 1:
        p.error("--threads must be >= 0, --workers and --max-tokens >= 1")
    embedder = Embedder(a.model_dir, a.max_tokens, a.threads, a.workers)
    settings = {"max_tokens": a.max_tokens, "threads": a.threads, "workers": a.workers}
    uvicorn.run(build_app(embedder, settings), host="127.0.0.1", port=a.port, log_level="warning")


if __name__ == "__main__":
    main()
