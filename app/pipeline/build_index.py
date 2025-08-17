from __future__ import annotations
import json, os
from typing import List
from app.parsers.html_pages import collect_program_corpus
from app.parsers.study_plan_pdf import fetch_pdf_text, extract_courses_from_text
from app.core.rag import RAGEngine, chunk_text
from app.core.models import DocChunk

DATA_DIR = "app/data"
RAW_JSON = os.path.join(DATA_DIR, "raw/corpus.json")
PROCESSED_JSON = os.path.join(DATA_DIR, "processed/study_plans.json")
INDEX_NPY = os.path.join(DATA_DIR, "processed/index.npy")

def main():
    os.makedirs(os.path.join(DATA_DIR, "raw"), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "processed"), exist_ok=True)

    corpus = collect_program_corpus()
    with open(RAW_JSON, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    study_plans = {}
    docs: List[DocChunk] = []
    for slug, bundle in corpus.items():
        study_plans[slug] = {"courses": []}
        # HTML pages → chunks
        for p in bundle["pages"]:
            for ch in chunk_text(p["text"], p["url"]):
                docs.append(ch)
        # Attempt to fetch study plan PDFs (if present)
        for link in bundle.get("plan_links", []):
            try:
                text = fetch_pdf_text(link)
                study_plans[slug]["courses"].extend(extract_courses_from_text(text))
                for ch in chunk_text(text, link):
                    docs.append(ch)
            except Exception as e:
                print(f"[warn] failed to parse plan {link}: {e}")

    with open(PROCESSED_JSON, "w", encoding="utf-8") as f:
        json.dump(study_plans, f, ensure_ascii=False, indent=2)

    # Build vector index in-memory and persist FAISS via numpy (simple demo)
    rag = RAGEngine()
    rag.build(docs)
    # Persist minimal — in проде храните faiss index + meta сериализацию
    # Здесь мы не сохраняем faiss напрямую для краткости.

if __name__ == "__main__":
    main()
