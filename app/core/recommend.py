from __future__ import annotations
import json, os
from typing import Dict, List

DATA_FILE = "app/data/processed/study_plans.json"

# Простые профили: mapping интересов/бэкграунда → теги курсов
PROFILE_TO_TAGS = {
    "software_engineer": ["mlops", "backend", "microservices", "kubernetes", "devops"],
    "data_analyst": ["statistics", "ab testing", "sql", "bi", "analytics"],
    "product_manager": ["product management", "ux", "metrics", "a/b", "communication"],
    "researcher": ["optimization", "probability", "deep learning", "generative", "cv", "nlp"],
    "data_engineer": ["big data", "spark", "dwh", "data engineering", "pipelines"]
}

def recommend(profile_key: str, k: int = 8) -> List[Dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        plans = json.load(f)
    # агрегируем все курсы, ищем по ключевым словам в названии
    all_courses = []
    for slug, sp in plans.items():
        for c in sp.get("courses", []):
            c["program"] = slug
            all_courses.append(c)
    tags = PROFILE_TO_TAGS.get(profile_key, [])
    # простая фильтрация по вхождению тегов в названии курса
    def score(course):
        title = (course.get("title") or "").lower()
        return sum(tag in title for tag in tags)
    ranked = sorted(all_courses, key=score, reverse=True)
    return ranked[:k]
