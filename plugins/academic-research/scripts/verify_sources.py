# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx>=0.27", "pyyaml>=6", "python-docx>=1.1", "pypdf>=4"]
# ///
"""Проверка списка литературы: каждая запись должна найтись в реестре или у автора.

    uv run verify_sources.py sources.yaml [--only key1,key2] [--dry-run] [--no-fill]

Порядок: DOI (Crossref → doi.org) → поиск по заглавию (OpenAlex → Crossref) →
страница по url → файл автора. verified: true ставится только при совпадении
заглавия (≥ 0,85), года (±1) и фамилии первого автора (если её можно сравнить).
Пустые поля дополняются из найденной записи (--no-fill — не трогать).
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent))
from common import DataError, fail, read_yaml, utf8_stdout, write_yaml  # noqa: E402
from scholarly import (TITLE_MIN, authors_match, clean_doi, crossref_by_doi,  # noqa: E402
                       crossref_search, doiorg_by_doi, make_client, norm, openalex_search,
                       page_title, similarity)

FILL = ("authors", "container", "year", "volume", "issue", "pages", "publisher", "doi", "type")


def year_ok(entry: dict, cand: dict) -> bool:
    try:
        return abs(int(entry["year"]) - int(cand["year"])) <= 1
    except (KeyError, TypeError, ValueError):
        return True


def judge(entry: dict, cand: dict) -> tuple[bool, float, str]:
    """Совпадает ли кандидат с записью → (да/нет, похожесть заглавия, почему нет)."""
    score = similarity(entry.get("title", ""), cand.get("title", "")) if entry.get("title") else 1.0
    if score < TITLE_MIN:
        return False, score, f"заглавие не совпадает: «{cand.get('title', '')}»"
    if not year_ok(entry, cand):
        return False, score, f"год не совпадает: в реестре {cand.get('year')}, у вас {entry.get('year')}"
    if authors_match(entry, cand) is False:
        return False, score, f"первый автор не совпадает: в реестре {', '.join((cand.get('authors') or [])[:2])}"
    return True, score, ""


def check_doi(c, e) -> tuple[dict | None, str, str]:
    doi = clean_doi(e.get("doi"))
    rec, by = crossref_by_doi(c, doi), "crossref"
    if rec is None:
        rec, by = doiorg_by_doi(c, doi), "doi.org"
    if rec is None:
        return None, "", f"DOI {doi} не найден ни в Crossref, ни в doi.org"
    ok, score, why = judge(e, rec)
    if not ok:
        return None, "", f"DOI {doi} ведёт на другую работу — {why}"
    rec["_score"] = score
    return rec, by, ""


def check_search(c, e) -> tuple[dict | None, str, str]:
    title = e.get("title", "")
    if not title:
        return None, "", "нет заглавия — искать нечего"
    fam = (e.get("authors") or [""])[0]
    fam = str(fam).split(",")[0] if fam else ""
    best_why = "в OpenAlex и Crossref такой работы нет"
    try:
        y0, y1 = int(e["year"]) - 1, int(e["year"]) + 1
    except (KeyError, TypeError, ValueError):
        y0 = y1 = None
    for by, fn in (("openalex", lambda: openalex_search(c, title, 5, from_year=y0, to_year=y1)),
                   ("crossref", lambda: crossref_search(c, f"{title} {fam}".strip(), 5, y0, y1))):
        for cand in fn():
            ok, score, why = judge(e, cand)
            if ok:
                cand["_score"] = score
                return cand, by, ""
            if score >= TITLE_MIN:
                best_why = f"похожая запись есть, но {why}"
    return None, "", best_why


def check_url(c, e) -> tuple[dict | None, str, str]:
    code, title, text = page_title(c, e["url"])
    if code >= 400:
        return None, "", f"страница {e['url']} не открылась (код {code}) — нужна другая ссылка или файл"
    if e.get("title") and (similarity(e["title"], title) >= TITLE_MIN or norm(e["title"]) in norm(text)):
        return {"title": title or e["title"], "_score": similarity(e["title"], title)}, "url", ""
    return None, "", f"на странице {e['url']} нет такого заглавия"


def read_file_text(path: Path, pages: int = 5) -> str:
    suf = path.suffix.lower()
    if suf == ".pdf":
        from pypdf import PdfReader
        return " ".join((p.extract_text() or "") for p in PdfReader(str(path)).pages[:pages])
    if suf == ".docx":
        from docx import Document
        return " ".join(p.text for p in Document(str(path)).paragraphs[:400])
    return path.read_text(encoding="utf-8", errors="ignore")[:200_000]


def check_file(e, base: Path) -> tuple[dict | None, str, str]:
    p = (base / e["file"]).expanduser()
    if not p.exists():
        return None, "", f"файл {e['file']} не найден"
    try:
        text = read_file_text(p)
    except Exception as ex:  # повреждённый PDF и т. п.
        return None, "", f"файл {e['file']} не читается: {ex}"
    if e.get("title") and norm(e["title"]) in norm(text):
        return {"title": e["title"], "_score": 1.0}, "file", ""
    return None, "", f"в файле {e['file']} не нашлось заглавия"


def verify_entry(c: httpx.Client, e: dict, base: Path, fill: bool = True) -> dict:
    """Проверяет одну запись и возвращает её обновлённой. Сеть упала — запись не меняется, кроме verify_note."""
    notes = []
    rec = by = None
    try:
        if e.get("doi"):
            rec, by, why = check_doi(c, e)
            if not rec:
                # неверный DOI в чистовик не пускаем, даже если работа находится по заглавию
                notes.append(why)
                hint, _, _ = check_search(c, e) if "не найден" in why else (None, "", "")
                if hint:
                    notes.append(f"работа с таким заглавием есть: DOI {hint.get('doi', 'нет')}, "
                                 f"{hint.get('container', '')} {hint.get('year', '')} — исправьте DOI в записи")
        else:
            steps = [lambda: check_search(c, e)]
            if e.get("url"):
                steps.append(lambda: check_url(c, e))
            if e.get("file"):
                steps.append(lambda: check_file(e, base))
            for step in steps:
                rec, by, why = step()
                if rec:
                    break
                notes.append(why)
    except httpx.HTTPError as ex:
        e["verify_note"] = f"не удалось проверить сейчас (нет связи: {type(ex).__name__}) — запустите ещё раз"
        return e
    for k in ("verified_by", "match", "verify_note"):
        e.pop(k, None)
    e["verified_at"] = date.today().isoformat()
    if not rec:
        e["verified"] = False
        e["verify_note"] = "; ".join(n for n in notes if n)
        return e
    e["verified"] = True
    e["verified_by"] = by
    e["match"] = {k: rec[k] for k in ("title", "year", "doi") if rec.get(k)} | {"score": round(rec["_score"], 2)}
    if by in ("crossref", "doi.org", "openalex"):
        diffs = []
        for k in FILL:
            if not rec.get(k):
                continue
            if not e.get(k):
                if fill:
                    e[k] = rec[k]
            elif k in ("year", "pages", "volume", "issue") and str(e[k]).replace("–", "-") != str(rec[k]):
                diffs.append(f"{k}: в реестре {rec[k]}, у вас {e[k]}")
        if diffs:
            e["verify_note"] = "проверьте: " + "; ".join(diffs)
    return e


def main() -> None:
    utf8_stdout()
    ap = argparse.ArgumentParser(description="Проверка литературы по Crossref, doi.org, OpenAlex")
    ap.add_argument("sources", help="путь к sources.yaml")
    ap.add_argument("--only", help="ключи через запятую")
    ap.add_argument("--dry-run", action="store_true", help="не записывать файл")
    ap.add_argument("--no-fill", action="store_true", help="не дополнять пустые поля")
    args = ap.parse_args()
    path = Path(args.sources).expanduser().resolve()
    try:
        data = read_yaml(path)
    except DataError as e:
        fail(str(e))
    entries = data.get("sources") or []
    only = set(args.only.split(",")) if args.only else None
    with make_client() as c:
        for e in entries:
            if only and e.get("key") not in only:
                continue
            verify_entry(c, e, path.parent, fill=not args.no_fill)
            mark = "ПРОВЕРЕНО" if e.get("verified") else "НЕ ПРОВЕРЕНО"
            how = f" ({e['verified_by']})" if e.get("verified") else ""
            note = f" — {e['verify_note']}" if e.get("verify_note") else ""
            print(f"[{mark}]{how} {e.get('key')}: {e.get('title', '')}{note}")
    if not args.dry_run:
        write_yaml(path, data)
    ok = sum(1 for e in entries if e.get("verified") is True)
    print(f"\nИтого: проверено {ok} из {len(entries)}. Файл: {path}"
          + (" (не записан, --dry-run)" if args.dry_run else ""))
    if ok < len(entries):
        print("Непроверенные в чистовик не попадут: исправьте DOI/заглавие, дайте ссылку или файл источника.")


if __name__ == "__main__":
    main()
