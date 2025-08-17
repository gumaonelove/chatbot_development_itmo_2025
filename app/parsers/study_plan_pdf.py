from __future__ import annotations
import io, re, requests, pdfplumber
from typing import List, Dict

def google_drive_direct(url: str) -> str:
    # поддержка ссылок вида https://drive.google.com/file/d/<ID>/view?usp=sharing
    m = re.search(r"/d/([a-zA-Z0-9_-]+)/", url)
    if not m: return url
    file_id = m.group(1)
    return f"https://drive.google.com/uc?export=download&id={file_id}"

def fetch_pdf_text(url: str) -> str:
    u = google_drive_direct(url)
    r = requests.get(u, timeout=60)
    r.raise_for_status()
    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)

def extract_courses_from_text(text: str) -> List[Dict]:
    # Heuristics по ключевым словам: «семестр», «з.е.», «дисциплина» и т.п.
    items: List[Dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        # Простая эвристика: "N семестр — Название — X з.е."
        m = re.search(r"(?P<sem>\d+)\s*семестр.*?(?P<title>[^–—]+)[–—-].*?(?P<credits>\d+(?:[.,]\d+)?)\s*(?:з\.е\.|ECTS)", line, flags=re.I)
        if m:
            items.append({"semester": int(m.group("sem")), "title": m.group("title").strip(), "credits": float(m.group("credits").replace(",", "."))})
    return items
