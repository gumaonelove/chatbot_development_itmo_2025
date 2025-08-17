from __future__ import annotations
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

@dataclass
class DocChunk:
    id: str
    url: str
    text: str

class Embedder:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or os.getenv("EMBED_MODEL", "intfloat/multilingual-e5-base")
        self.model = SentenceTransformer(self.model_name)
    def encode(self, texts: List[str]) -> np.ndarray:
        # e5 requires "query: ..."/"passage: ..." prefixes for best quality
        return self.model.encode(texts, normalize_embeddings=True)

class VectorIndex:
    def __init__(self, dim: int, metric: str = "ip"):
        if metric not in {"ip","l2"}: raise ValueError("metric must be ip or l2")
        self.metric = faiss.METRIC_INNER_PRODUCT if metric=="ip" else faiss.METRIC_L2
        self.index = faiss.IndexFlatIP(dim) if metric=="ip" else faiss.IndexFlatL2(dim)
        self.meta: List[DocChunk] = []
    def add(self, embeddings: np.ndarray, meta: List[DocChunk]):
        assert embeddings.shape[0] == len(meta)
        self.index.add(embeddings.astype(np.float32))
        self.meta.extend(meta)
    def search(self, query_emb: np.ndarray, k: int = 5) -> List[Tuple[float, DocChunk]]:
        D, I = self.index.search(query_emb.astype(np.float32), k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx == -1: continue
            results.append((float(dist), self.meta[idx]))
        return results
