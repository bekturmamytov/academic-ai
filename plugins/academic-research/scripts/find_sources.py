# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx>=0.27", "pyyaml>=6"]
# ///
"""Поиск литературы в OpenAlex и Crossref.

    uv run find_sources.py "вибродиагностика насосов" [--lang ru] [--limit 10]
        [--from-year 2015] [--source both|openalex|crossref] [--yaml candidates.yaml]

Печатает кандидатов с DOI, годом, авторами, изданием. --yaml — записать их в
схеме sources.yaml (verified: false): проверку ставит только verify_sources.py.
КиберЛенинка и eLibrary API не имеют — там автор ищет сам и даёт ссылку.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent))
from common import fail, utf8_stdout, write_yaml  # noqa: E402
from scholarly import crossref_search, make_client, norm, openalex_search  # noqa: E402


def make_key(e: dict, used: set[str]) -> str:
    a = (e.get("authors") or ["src"])[0]
    fam = re.sub(r"\W", "", str(a).split(",")[0]).lower() or "src"
    base = f"{fam}{e.get('year', '')}"
    key, n = base, 1
    while key in used:
        n += 1
        key = f"{base}{chr(ord('a') + n - 1)}"
    used.add(key)
    return key


def search(c: httpx.Client, query: str, *, lang: str | None, limit: int, from_year: int | None,
           source: str) -> tuple[list[dict], list[str]]:
    found, errors = [], []
    if source in ("both", "openalex"):
        try:
            found += openalex_search(c, query, limit, lang, from_year)
        except httpx.HTTPError as e:
            errors.append(f"OpenAlex не ответил: {e}")
    if source in ("both", "crossref"):
        try:
            found += crossref_search(c, query, limit, from_year)
        except httpx.HTTPError as e:
            errors.append(f"Crossref не ответил: {e}")
    seen, out = set(), []
    for e in found:
        sig = e.get("doi") or norm(e.get("title", ""))
        if sig and sig not in seen and e.get("title"):
            seen.add(sig)
            out.append(e)
    return out, errors


def line(i: int, e: dict) -> str:
    a = e.get("authors") or []
    who = "; ".join(a[:3]) + (" и др." if len(a) > 3 else "")
    bits = [f"{i}. {who or '—'} ({e.get('year', 'б. г.')}). {e['title']}."]
    if e.get("container"):
        bits.append(f"{e['container']}.")
    bits.append(f"DOI {e['doi']}" if e.get("doi") else "без DOI")
    meta = e.get("origin", "")
    if e.get("cited_by") is not None:
        meta += f", цитирований {e['cited_by']}"
    return " ".join(bits) + f"  [{meta}]"


def main() -> None:
    utf8_stdout()
    ap = argparse.ArgumentParser(description="Поиск литературы в OpenAlex и Crossref")
    ap.add_argument("query")
    ap.add_argument("--lang", help="язык публикаций: ru, en, ky … (только OpenAlex)")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--from-year", type=int)
    ap.add_argument("--source", choices=("both", "openalex", "crossref"), default="both")
    ap.add_argument("--yaml", help="записать кандидатов в файл в схеме sources.yaml")
    args = ap.parse_args()
    with make_client() as c:
        found, errors = search(c, args.query, lang=args.lang, limit=args.limit,
                               from_year=args.from_year, source=args.source)
    for msg in errors:
        print(f"Предупреждение: {msg}", file=sys.stderr)
    if not found:
        if errors:
            fail("поиск не удался — нет связи с OpenAlex и Crossref")
        print("Ничего не нашлось. Попробуйте другие слова, английский запрос или --lang en.")
        return
    for i, e in enumerate(found, 1):
        print(line(i, e))
    if args.yaml:
        used: set[str] = set()
        rows = []
        for e in found:
            e = {"key": make_key(e, used), **{k: v for k, v in e.items() if k not in ("cited_by", "openalex")},
                 "verified": False}
            rows.append(e)
        write_yaml(Path(args.yaml), {"sources": rows})
        print(f"\nКандидаты: {Path(args.yaml).resolve()} — выберите нужные и перенесите в sources.yaml,"
              " затем verify_sources.py.")


if __name__ == "__main__":
    main()
