from __future__ import annotations
import re, time, json, os
from typing import Dict, List
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

PROGRAM_PAGES = {
    "ai": ["https://abit.itmo.ru/program/master/ai", "https://ai.itmo.ru/"],
    "ai_product": ["https://abit.itmo.ru/program/master/ai_product"]
}

def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def extract_visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # remove nav, script, style
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(soup.stripped_strings)
    return re.sub(r"\s+", " ", text)

def discover_study_plan_links(html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        label = (a.get_text() or "").lower()
        href = a["href"]
        if any(key in label for key in ["учебный план", "план обучения"]) or "drive.google.com" in href:
            links.append(href)
    return list(dict.fromkeys(links))

def normalize_url(base_url: str, href: str) -> str:
    if href.startswith("http"): return href
    if href.startswith("//"): return "https:" + href
    if href.startswith("/"):
        from urllib.parse import urlparse
        p = urlparse(base_url)
        return f"{p.scheme}://{p.netloc}{href}"
    return href

def collect_program_corpus() -> Dict[str, Dict]:
    out: Dict[str, Dict] = {}
    for slug, pages in PROGRAM_PAGES.items():
        texts = []
        plan_links = []
        for url in pages:
            html = fetch(url)
            txt = extract_visible_text(html)
            texts.append({"url": url, "text": txt})
            for href in discover_study_plan_links(html):
                plan_links.append(normalize_url(url, href))
        out[slug] = {"pages": texts, "plan_links": list(dict.fromkeys(plan_links))}
    return out
