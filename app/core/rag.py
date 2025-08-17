from __future__ import annotations
import os, re, textwrap
from typing import List, Dict, Tuple
from .models import Embedder, VectorIndex, DocChunk
import numpy as np

RELEVANCE_THRESHOLD = 0.3  # для cosine/ip; подобрать эмпирически

def chunk_text(text: str, url: str, chunk_size: int = 800, overlap: int = 120):
    chunks: List[DocChunk] = []
    i = 0
    idx = 0
    while i < len(text):
        chunk = text[i:i+chunk_size]
        chunks.append(DocChunk(id=f"{url}#chunk{idx}", url=url, text=chunk))
        i += chunk_size - overlap
        idx += 1
    return chunks

class RAGEngine:
    def __init__(self, embed_model: str | None = None):
        self.embedder = Embedder(embed_model)
        self.index: VectorIndex | None = None

    def build(self, docs: List[DocChunk]):
        X = self.embedder.encode([f"passage: {d.text}" for d in docs])
        self.index = VectorIndex(dim=X.shape[1], metric="ip")
        self.index.add(X, docs)

    def query(self, q: str, k: int = 5) -> Tuple[List[Tuple[float, DocChunk]], float]:
        assert self.index is not None
        q_emb = self.embedder.encode([f"query: {q}"])
        results = self.index.search(q_emb, k=k)
        max_score = results[0][0] if results else 0.0
        return results, max_score

def format_answer(question: str, results: List[Tuple[float, DocChunk]], max_score: float) -> str:
    # Гейт релевантности
    if max_score < RELEVANCE_THRESHOLD:
        return ("Извините, я отвечаю только по программам «Искусственный интеллект» "
                "и «Управление ИИ‑продуктами (AI Product)». Не могу помочь с этим вопросом.")
    # Собираем сжатый контекст с источниками
    ctx = []
    seen = set()
    for score, ch in results[:3]:
        src = ch.url
        if src not in seen:
            ctx.append(f"- {src}")
            seen.add(src)
    answer = "Ниже — выдержки из официальных страниц программ:\n" + "\n".join(ctx)
    return answer
