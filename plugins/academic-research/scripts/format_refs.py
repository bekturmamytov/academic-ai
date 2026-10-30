# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Список литературы из sources.yaml: ГОСТ Р 7.0.100-2018, APA 7, IEEE.

    uv run format_refs.py sources.yaml --style gost [--order alpha|cite] [--md] [--all]

Печатает нумерованный список проверенных источников; непроверенные — отдельно,
с пометкой [НЕ ПРОВЕРЕНО]: в чистовик они не идут.
Модуль используют build_docx.py (format_entry, sort_entries, cite).
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import DataError, STYLES, fail, read_yaml, utf8_stdout  # noqa: E402

Run = tuple[str, bool]  # (текст, курсив)

CYR = re.compile(r"[А-Яа-яЁёӨөҮүҢң]")
INITIAL = re.compile(r"^[A-ZА-ЯЁӨҮҢ][a-zа-яёөүң]?\.$|^[A-ZА-ЯЁӨҮҢ]\.(-[A-ZА-ЯЁӨҮҢ]\.)?$")
MONTHS_EN = ["Jan.", "Feb.", "Mar.", "Apr.", "May", "Jun.", "Jul.", "Aug.", "Sep.", "Oct.", "Nov.", "Dec."]


def is_cyr(s: str) -> bool:
    return bool(CYR.search(s or ""))


def entry_lang(e: dict) -> str:
    if e.get("lang") in ("ru", "ky"):
        return "ru"
    if e.get("lang"):
        return "en"
    return "ru" if is_cyr(e.get("title", "")) else "en"


# ---------- имена ----------

def _initials(given: str) -> list[str]:
    out = []
    for part in re.split(r"[\s.]+", given.strip()):
        if not part:
            continue
        if "-" in part:
            out.append("-".join(p[0] + "." for p in part.split("-") if p))
        else:
            out.append(part[0] + ".")
    return out


def parse_name(a) -> tuple[str, list[str]]:
    """→ (фамилия, [инициалы]). Принимает «Фамилия, Имя Отчество», «Фамилия И. О.»,
    «И. О. Фамилия», «Given Family», {'family','given'}."""
    if isinstance(a, dict):
        if a.get("literal"):
            return a["literal"], []
        return a.get("family", "").strip(), _initials(a.get("given", ""))
    a = str(a).strip()
    if "," in a:
        fam, given = a.split(",", 1)
        return fam.strip(), _initials(given)
    toks = re.sub(r"\.(?=\S)", ". ", a).split()
    if len(toks) == 1:
        return toks[0], []
    if all(INITIAL.match(t) for t in toks[1:]):
        return toks[0], _initials(" ".join(toks[1:]))
    if all(INITIAL.match(t) for t in toks[:-1]):
        return toks[-1], _initials(" ".join(toks[:-1]))
    if is_cyr(a):  # русский порядок: Фамилия Имя Отчество
        return toks[0], _initials(" ".join(toks[1:]))
    return toks[-1], _initials(" ".join(toks[:-1]))


def name_inverted(a) -> str:
    fam, ini = parse_name(a)
    return f"{fam}, {' '.join(ini)}" if ini else fam


def name_direct(a) -> str:
    fam, ini = parse_name(a)
    return f"{' '.join(ini)} {fam}" if ini else fam


def family(a) -> str:
    return parse_name(a)[0]


# ---------- мелочи ----------

def dash(pages) -> str:
    return re.sub(r"\s*[-‐‑‒—]\s*", "–", str(pages)).strip()


def end_punct(s: str) -> str:
    s = s.strip()
    return s if s and s[-1] in ".?!" else s + "."


def accessed_gost(d) -> str:
    if not d:
        return date.today().strftime("%d.%m.%Y")
    try:
        y, m, dd = str(d)[:10].split("-")
        return f"{dd}.{m}.{y}"
    except ValueError:
        return str(d)


def accessed_ieee(d) -> str:
    try:
        y, m, dd = (int(x) for x in str(d)[:10].split("-"))
        return f"{MONTHS_EN[m - 1]} {dd}, {y}"
    except (ValueError, IndexError):
        today = date.today()
        return f"{MONTHS_EN[today.month - 1]} {today.day}, {today.year}"


class R:
    """Набор кусков описания: курсив отдельно, чтобы docx его сохранил."""

    def __init__(self):
        self.runs: list[Run] = []

    def add(self, text: str, italic: bool = False):
        if text:
            if self.runs and self.runs[-1][1] == italic:
                self.runs[-1] = (self.runs[-1][0] + text, italic)
            else:
                self.runs.append((text, italic))
        return self

    def text(self) -> str:
        return "".join(t for t, _ in self.runs)

    def sep(self, text: str):
        """Следующий элемент ГОСТ через «. – », без двойной точки."""
        cur = self.text().rstrip()
        return self.add((" – " if cur.endswith(".") else ". – ") + text)


def plain(runs: list[Run]) -> str:
    return "".join(t for t, _ in runs)


def markdown(runs: list[Run]) -> str:
    out = []
    for t, i in runs:
        if i and t.strip():
            lead, trail = t[: len(t) - len(t.lstrip())], t[len(t.rstrip()):]
            out.append(f"{lead}*{t.strip()}*{trail}")
        else:
            out.append(t)
    return "".join(out)


# ---------- ГОСТ Р 7.0.100-2018 ----------

def _gost(e: dict) -> list[Run]:
    ru = entry_lang(e) == "ru"
    authors = e.get("authors") or []
    n = len(authors)
    typ = e.get("type", "article")
    r = R()
    if 1 <= n <= 3 and typ != "law":
        r.add(name_inverted(authors[0]) + " ")
    title = e.get("title", "").strip()
    r.add(title)
    if e.get("subtitle"):
        r.add(" : " + e["subtitle"])
    if typ == "thesis":
        if e.get("specialty"):
            r.add(" : специальность " + str(e["specialty"]) if ru else " : specialty " + str(e["specialty"]))
        if e.get("degree"):
            r.add(" : " + e["degree"])
    if typ == "law" and e.get("note"):
        r.add(" : " + e["note"])
    if n:
        shown = authors if n <= 4 else authors[:3]
        resp = ", ".join(name_direct(a) for a in shown)
        if n > 4:
            resp += " [и др.]" if ru else " [et al.]"
        r.add(" / " + resp)
    if typ == "thesis" and e.get("publisher"):
        r.add(" ; " + e["publisher"])
    if typ == "web":
        r.sep("Текст : электронный" if ru else "Text : electronic")
    if e.get("container") and typ in ("article", "chapter", "conference", "web"):
        r.add(" // " + e["container"])
        if e.get("editors"):
            r.add(" / " + ("под редакцией " if ru else "edited by ") +
                  ", ".join(name_direct(x) for x in e["editors"]))
    if e.get("edition"):
        r.sep(e["edition"])
    year = e.get("year")
    if typ in ("book", "chapter", "conference", "thesis") and (e.get("city") or e.get("publisher")):
        place = e.get("city", "")
        pub = e.get("publisher", "") if typ != "thesis" else ""
        s = place + (" : " + pub if pub and place else pub)
        r.sep(s + (", " + str(year) if year else ""))
    elif year:
        r.sep(str(year))
    if typ in ("article", "conference", "chapter"):
        vol = []
        if e.get("volume"):
            vol.append(("Т. " if ru else "Vol. ") + str(e["volume"]))
        if e.get("issue"):
            vol.append(("№ " if ru else "No. ") + str(e["issue"]))
        if vol:
            r.sep(", ".join(vol))
        if e.get("pages"):
            r.sep(("С. " if ru else "P. ") + dash(e["pages"]))
    if typ in ("book", "thesis") and e.get("total_pages"):
        r.sep(str(e["total_pages"]) + (" с." if ru else " p.").rstrip("."))
    if e.get("isbn"):
        r.sep("ISBN " + str(e["isbn"]))
    if e.get("doi"):
        r.sep("DOI " + e["doi"])
    if e.get("url") and (typ in ("web", "law") or not e.get("doi")):
        r.sep("URL: " + e["url"] + (" (дата обращения: " if ru else " (accessed: ")
              + accessed_gost(e.get("accessed")) + ")")
    r.runs[-1] = (end_punct(r.runs[-1][0]), r.runs[-1][1])
    return r.runs


# ---------- APA 7 ----------

def _apa_authors(authors: list, ru: bool) -> str:
    names = [name_inverted(a) for a in authors]
    if len(names) > 20:
        names = names[:19] + ["…", names[-1]]
        return ", ".join(names[:-1]) + " " + names[-1]
    if len(names) == 1:
        return names[0]
    amp = "&"
    return ", ".join(names[:-1]) + f", {amp} " + names[-1]


def _apa(e: dict) -> list[Run]:
    ru = entry_lang(e) == "ru"
    typ = e.get("type", "article")
    authors = e.get("authors") or []
    year = str(e.get("year") or ("б. г." if ru else "n.d."))
    title = e.get("title", "").strip()
    r = R()
    italic_title = typ in ("book", "thesis", "web", "law")
    if authors:
        r.add(end_punct(_apa_authors(authors, ru)) + f" ({year}). ")
        r.add(end_punct(title) + " " if not italic_title else title, italic_title)
        if italic_title:
            if typ == "book" and e.get("edition"):
                r.add(f" ({e['edition']})")
            r.add(". " if not title.endswith(("?", "!")) else " ")
    else:
        r.add(title, italic_title)
        r.add(f". ({year}). ")
    if typ == "article":
        if e.get("container"):
            r.add(e["container"], True)
            if e.get("volume"):
                r.add(", ")
                r.add(str(e["volume"]), True)
            if e.get("issue"):
                r.add(f"({e['issue']})" if e.get("volume") else f", ({e['issue']})")
            if e.get("pages"):
                r.add(", " + dash(e["pages"]))
            r.add(".")
    elif typ in ("chapter", "conference"):
        if e.get("container"):
            r.add("In " if not ru else "В ")
            if e.get("editors"):
                eds = e["editors"]
                r.add(", ".join(name_direct(x) for x in eds) +
                      (" (Ed.), " if len(eds) == 1 else " (Eds.), "))
            r.add(e["container"], True)
            if e.get("pages"):
                r.add(f" (pp. {dash(e['pages'])})")
            r.add(".")
        if e.get("publisher"):
            r.add(" " + end_punct(e["publisher"]))
    elif typ == "thesis":
        r.runs[-1] = (r.runs[-1][0].rstrip(". ") + " ", r.runs[-1][1])
        r.add(f"[{e.get('degree', 'Doctoral dissertation')}, {e.get('publisher', '')}].".replace(", ]", "]"))
    elif typ == "book":
        if e.get("publisher"):
            r.add(end_punct(e["publisher"]))
    elif typ == "web":
        if e.get("container"):
            r.add(end_punct(e["container"]))
    elif typ == "law" and e.get("note"):
        r.add(end_punct(e["note"]))
    if e.get("doi"):
        r.add(" https://doi.org/" + e["doi"])
    elif e.get("url"):
        r.add(" " + e["url"])
    runs = [(re.sub(r"\s+", " ", t), i) for t, i in r.runs]
    runs[0] = (runs[0][0].lstrip(), runs[0][1])
    runs[-1] = (runs[-1][0].rstrip(), runs[-1][1])
    return runs


# ---------- IEEE ----------

def _ieee_authors(authors: list) -> str:
    names = [name_direct(a) for a in authors]
    if len(names) > 6:
        return names[0] + " et al."
    if len(names) <= 2:
        return " and ".join(names)
    return ", ".join(names[:-1]) + ", and " + names[-1]


def _ieee(e: dict) -> list[Run]:
    typ = e.get("type", "article")
    authors = e.get("authors") or []
    title = e.get("title", "").strip()
    year = str(e.get("year") or "")
    r = R()
    if authors:
        r.add(_ieee_authors(authors) + ", ")
    if typ in ("book",):
        r.add(title, True)
        if e.get("edition"):
            r.add(", " + e["edition"].rstrip("."))
        r.add(". ")
        place = ": ".join(x for x in (e.get("city"), e.get("publisher")) if x)
        r.add(", ".join(x for x in (place, year) if x) + ".")
    else:
        r.add(f"“{title},” ")
        if typ == "article":
            r.add(e.get("container", ""), True)
            parts = []
            if e.get("volume"):
                parts.append(f"vol. {e['volume']}")
            if e.get("issue"):
                parts.append(f"no. {e['issue']}")
            if e.get("pages"):
                parts.append(f"pp. {dash(e['pages'])}")
            if year:
                parts.append(year)
            r.add(", " + ", ".join(parts) if parts else "")
        elif typ in ("chapter", "conference"):
            r.add("in ")
            r.add(e.get("container", ""), True)
            parts = []
            if e.get("editors"):
                parts.append(", ".join(name_direct(x) for x in e["editors"]) + ", Eds.")
            if typ == "chapter":
                place = ": ".join(x for x in (e.get("city"), e.get("publisher")) if x)
                if place:
                    parts.append(place)
            if year:
                parts.append(year)
            if e.get("pages"):
                parts.append(f"pp. {dash(e['pages'])}")
            r.add(", " + ", ".join(parts) if parts else "")
        elif typ == "thesis":
            r.add(", ".join(x for x in (e.get("degree"), e.get("publisher"), e.get("city"), year) if x))
        elif typ == "web":
            r.add(e.get("container", "") + ("." if e.get("container") else ""))
            r.add(f" Accessed: {accessed_ieee(e.get('accessed'))}. [Online]. Available: {e.get('url', '')}")
            return _clean(r.runs)
        elif typ == "law":
            r.add(e.get("note", ""))
        else:
            r.add(year)
        if e.get("doi"):
            r.add(f", doi: {e['doi']}")
        r.add(".")
        if e.get("url") and not e.get("doi"):
            r.add(f" [Online]. Available: {e['url']}")
    return _clean(r.runs)


def _clean(runs: list[Run]) -> list[Run]:
    out = [(re.sub(r"\s+", " ", t).replace(",,", ",").replace(" ,", ","), i) for t, i in runs]
    out = [(t.replace(",.", "."), i) for t, i in out]
    return out


FORMATTERS = {"gost": _gost, "apa": _apa, "ieee": _ieee}


def format_entry(e: dict, style: str = "gost") -> list[Run]:
    if style not in FORMATTERS:
        raise DataError(f"стиль «{style}» не знаю — gost, apa или ieee")
    return FORMATTERS[style](e)


# ---------- порядок и ссылки в тексте ----------

def sort_key(e: dict):
    a = e.get("authors") or []
    head = family(a[0]) if a and len(a) <= 3 else e.get("title", "")
    head = head.strip("«»\"' ").lower()
    return (0 if is_cyr(head) else 1, head, str(e.get("year", "")))


def sort_entries(entries: list[dict], order: str = "alpha", cite_order: list[str] | None = None) -> list[dict]:
    if order == "cite" and cite_order is not None:
        pos = {k: i for i, k in enumerate(cite_order)}
        return sorted(entries, key=lambda e: (pos.get(e.get("key"), len(pos)), sort_key(e)))
    return sorted(entries, key=sort_key)


def apa_author_year(e: dict, lang: str = "ru") -> str:
    a = e.get("authors") or []
    ru = is_cyr(family(a[0])) if a else lang == "ru"
    if not a:
        who = e.get("title", "")[:40]
    elif len(a) == 1:
        who = family(a[0])
    elif len(a) == 2:
        who = f"{family(a[0])} {'и' if ru else '&'} {family(a[1])}"
    else:
        who = f"{family(a[0])} {'и др.' if ru else 'et al.'}"
    return f"{who}, {e.get('year') or ('б. г.' if ru else 'n.d.')}"


def cite(refs: list[tuple[dict, int, str]], style: str, lang: str = "ru") -> str:
    """refs — [(запись, номер в списке, локатор)] → «[1, с. 5; 3]» / «(LeCun et al., 2015)» / «[1], [3]»."""
    if style == "apa":
        parts = [apa_author_year(e, lang) + (f", {loc}" if loc else "") for e, _, loc in refs]
        return "(" + "; ".join(parts) + ")"
    refs = sorted(refs, key=lambda r: r[1])
    if style == "ieee":
        return ", ".join(f"[{n}" + (f", {loc}" if loc else "") + "]" for _, n, loc in refs)
    return "[" + "; ".join(f"{n}" + (f", {loc}" if loc else "") for _, n, loc in refs) + "]"


def main() -> None:
    utf8_stdout()
    ap = argparse.ArgumentParser(description="Список литературы по ГОСТ / APA / IEEE")
    ap.add_argument("sources", help="путь к sources.yaml")
    ap.add_argument("--style", choices=STYLES, default="gost")
    ap.add_argument("--order", choices=("alpha", "cite"), default=None)
    ap.add_argument("--md", action="store_true", help="курсив звёздочками (markdown)")
    ap.add_argument("--all", action="store_true", help="показать и непроверенные (с пометкой)")
    args = ap.parse_args()
    try:
        entries = list(read_yaml(Path(args.sources)).get("sources") or [])
    except DataError as e:
        fail(str(e))
    order = args.order or ("cite" if args.style == "ieee" else "alpha")
    ok = sort_entries([e for e in entries if e.get("verified") is True], order,
                      [e.get("key") for e in entries])
    bad = [e for e in entries if e.get("verified") is not True]
    render = markdown if args.md else plain
    for i, e in enumerate(ok, 1):
        prefix = f"[{i}] " if args.style == "ieee" else ("" if args.style == "apa" else f"{i}. ")
        print(prefix + render(format_entry(e, args.style)))
    if bad:
        print(f"\nНе проверено ({len(bad)}) — в чистовик не попадут:", file=sys.stderr)
        for e in bad:
            line = plain(format_entry(e, args.style)) if args.all else e.get("title", e.get("key"))
            note = f" — {e['verify_note']}" if e.get("verify_note") else ""
            print(f"  [НЕ ПРОВЕРЕНО] {e.get('key')}: {line}{note}", file=sys.stderr)


if __name__ == "__main__":
    main()
