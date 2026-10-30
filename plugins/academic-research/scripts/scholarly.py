"""Запросы к Crossref, doi.org и OpenAlex + сравнение записей. Общий для find_sources и verify_sources.

Зависимость: httpx (объявляет вызывающий скрипт). Клиент передаётся параметром —
тесты подставляют httpx.MockTransport.
"""
from __future__ import annotations

import html
import re
import unicodedata
from difflib import SequenceMatcher
from urllib.parse import quote

import httpx

MAILTO = "info@ailab.kg"
USER_AGENT = f"academic-research/0.1 (+https://ailab.kg; mailto:{MAILTO})"
CROSSREF = "https://api.crossref.org"
OPENALEX = "https://api.openalex.org"
TITLE_MIN = 0.85

CROSSREF_TYPES = {
    "journal-article": "article", "book": "book", "monograph": "book", "edited-book": "book",
    "book-chapter": "chapter", "proceedings-article": "conference", "dissertation": "thesis",
}
OPENALEX_TYPES = {
    "article": "article", "book": "book", "book-chapter": "chapter",
    "dissertation": "thesis", "proceedings-article": "conference",
}


def make_client(timeout: float = 20.0, transport: httpx.BaseTransport | None = None) -> httpx.Client:
    return httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=timeout,
                        follow_redirects=True, transport=transport)


# ---------- сравнение ----------

def norm(s: str) -> str:
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    s = unicodedata.normalize("NFKC", s).lower().replace("ё", "е")
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def similarity(a: str, b: str) -> float:
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


def clean_doi(doi: str | None) -> str:
    if not doi:
        return ""
    d = str(doi).strip()
    d = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", d, flags=re.I)
    return d.lower()


def year_of(parts) -> int | None:
    try:
        return int(parts["date-parts"][0][0])
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def first_family(entry: dict) -> str:
    a = (entry.get("authors") or [None])[0]
    if not a:
        return ""
    if isinstance(a, dict):
        return norm(a.get("family", ""))
    a = str(a)
    return norm(a.split(",")[0] if "," in a else a.split()[0])


def authors_match(entry: dict, cand: dict) -> bool | None:
    """True/False — совпала ли фамилия первого автора; None — сравнить нельзя (нет авторов, разные алфавиты)."""
    fam = first_family(entry)
    fams = [norm(str(x).split(",")[0]) for x in cand.get("authors") or []]
    if not fam or not fams:
        return None
    cyr = re.compile(r"[а-яөүң]")
    if bool(cyr.search(fam)) != bool(cyr.search(fams[0])):
        return None
    return any(fam == f or fam in f.split() for f in fams)


# ---------- преобразование записей в схему sources.yaml ----------

def _csl_like_to_entry(item: dict, origin: str) -> dict:
    def first(v):
        return (v[0] if isinstance(v, list) and v else v) or ""

    authors = []
    for a in item.get("author") or []:
        if a.get("family"):
            authors.append(f"{a['family']}, {a.get('given', '')}".strip().rstrip(","))
        elif a.get("name") or a.get("literal"):
            authors.append(a.get("name") or a.get("literal"))
    year = None
    for k in ("issued", "published-print", "published-online", "published", "created"):
        year = year_of(item.get(k) or {})
        if year:
            break
    e = {
        "type": CROSSREF_TYPES.get(item.get("type", ""), "other" if item.get("type") else "article"),
        "authors": authors,
        "title": html.unescape(re.sub(r"<[^>]+>", "", first(item.get("title")))).strip(),
        "container": first(item.get("container-title")),
        "year": year,
        "volume": item.get("volume", ""),
        "issue": item.get("issue", ""),
        "pages": item.get("page", ""),
        "publisher": item.get("publisher", ""),
        "doi": clean_doi(item.get("DOI")),
        "origin": origin,
    }
    if item.get("type") in ("article-journal",):
        e["type"] = "article"
    elif item.get("type") in ("paper-conference",):
        e["type"] = "conference"
    return {k: v for k, v in e.items() if v not in ("", None, [])}


def crossref_to_entry(item: dict) -> dict:
    return _csl_like_to_entry(item, "crossref")


def csl_to_entry(item: dict) -> dict:
    return _csl_like_to_entry(item, "doi.org")


def openalex_to_entry(w: dict) -> dict:
    authors = []
    for au in w.get("authorships") or []:
        name = ((au.get("author") or {}).get("display_name") or "").strip()
        if not name:
            continue
        toks = name.split()
        authors.append(f"{toks[-1]}, {' '.join(toks[:-1])}".strip().rstrip(",") if len(toks) > 1 else name)
    src = ((w.get("primary_location") or {}).get("source") or {})
    b = w.get("biblio") or {}
    pages = "-".join(x for x in (b.get("first_page"), b.get("last_page")) if x)
    e = {
        "type": OPENALEX_TYPES.get(w.get("type", ""), "article"),
        "authors": authors,
        "title": (w.get("title") or w.get("display_name") or "").strip(),
        "container": src.get("display_name", ""),
        "year": w.get("publication_year"),
        "volume": b.get("volume") or "",
        "issue": b.get("issue") or "",
        "pages": pages,
        "doi": clean_doi(w.get("doi")),
        "lang": w.get("language") or "",
        "origin": "openalex",
        "cited_by": w.get("cited_by_count"),
        "openalex": w.get("id", ""),
    }
    return {k: v for k, v in e.items() if v not in ("", None, [])}


# ---------- запросы ----------

def crossref_by_doi(c: httpx.Client, doi: str) -> dict | None:
    r = c.get(f"{CROSSREF}/works/{quote(doi, safe='/')}", params={"mailto": MAILTO})
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return crossref_to_entry(r.json()["message"])


def doiorg_by_doi(c: httpx.Client, doi: str) -> dict | None:
    """DOI вне Crossref (DataCite, mEDRA …): content negotiation на doi.org."""
    r = c.get(f"https://doi.org/{quote(doi, safe='/')}",
              headers={"Accept": "application/vnd.citationstyles.csl+json"})
    if r.status_code in (404, 406) or "json" not in r.headers.get("content-type", ""):
        return None
    r.raise_for_status()
    e = csl_to_entry(r.json())
    e.setdefault("doi", doi)
    return e


def openalex_search(c: httpx.Client, query: str, limit: int = 10, lang: str | None = None,
                    from_year: int | None = None, to_year: int | None = None) -> list[dict]:
    filters = []
    if lang:
        filters.append(f"language:{lang}")
    if from_year:
        filters.append(f"from_publication_date:{from_year}-01-01")
    if to_year:
        filters.append(f"to_publication_date:{to_year}-12-31")
    params = {"search": query, "per-page": limit, "mailto": MAILTO}
    if filters:
        params["filter"] = ",".join(filters)
    r = c.get(f"{OPENALEX}/works", params=params)
    r.raise_for_status()
    return [openalex_to_entry(w) for w in r.json().get("results", [])]


def crossref_search(c: httpx.Client, query: str, limit: int = 10, from_year: int | None = None,
                    to_year: int | None = None) -> list[dict]:
    params = {"query.bibliographic": query, "rows": limit, "mailto": MAILTO}
    filters = []
    if from_year:
        filters.append(f"from-pub-date:{from_year}")
    if to_year:
        filters.append(f"until-pub-date:{to_year}")
    if filters:
        params["filter"] = ",".join(filters)
    r = c.get(f"{CROSSREF}/works", params=params)
    r.raise_for_status()
    return [crossref_to_entry(it) for it in r.json()["message"].get("items", [])]


def page_title(c: httpx.Client, url: str) -> tuple[int, str, str]:
    """→ (код ответа, заглавие из citation_title/og:title/<title>, текст страницы)."""
    r = c.get(url)
    body = r.text if r.status_code < 400 else ""
    title = ""
    for pat in (r'<meta[^>]+name=["\']citation_title["\'][^>]+content=["\']([^"\']+)',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']citation_title',
                r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)',
                r"<title[^>]*>(.*?)</title>"):
        m = re.search(pat, body, re.I | re.S)
        if m:
            title = html.unescape(m.group(1)).strip()
            break
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S | re.I)
    return r.status_code, title, re.sub(r"<[^>]+>", " ", text)
