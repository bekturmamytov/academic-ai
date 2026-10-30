# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1", "pyyaml>=6"]
# ///
"""Учебно-методическое пособие: manual.yaml + главы .md → out/manual.pdf (Typst) и out/manual.docx.

    uv run build_manual.py <manual.yaml> [--course course.yaml] [--no-pdf]
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import DataError, fail, new_document, out_dir, para, read_yaml, university_name  # noqa: E402
from content_kit import (  # noqa: E402
    add_runs, add_toc, literature_status, load_context, mark_runs, parse_inline, parse_md, render_docx,
    split_frontmatter,
)
from i18n import LABELS, t  # noqa: E402

LABELS.update({
    "manual_kind": {"ru": "Учебно-методическое пособие", "ky": "Окуу-методикалык колдонмо", "en": "Study guide"},
    "reviewers": {"ru": "Рецензенты", "ky": "Рецензенттер", "en": "Reviewers"},
    "pages": {"ru": "с.", "ky": "б.", "en": "p."},
    "figure": {"ru": "Рисунок", "ky": "Сүрөт", "en": "Figure"},
    "recommended": {
        "ru": "Рекомендовано к изданию Учёным советом ______________ (протокол № ___ от «___» ________ 20__ г.)",
        "ky": "______________ Илимий кеңеши тарабынан басмага сунушталган (№ ___ протокол, «___» ________ 20__ ж.)",
        "en": "Recommended for publication by the Academic Council of ______________ (minutes No. ___ of ________)",
    },
})
TEMPLATE = Path(__file__).resolve().parent.parent / "skills" / "manual" / "templates" / "manual.typ"
TYPST_LANG = {"ru": "ru", "ky": "ky", "en": "en"}


def prep_blocks(blocks: list[dict], src_dir: Path, build: Path) -> list[dict]:
    """Готовит блоки к JSON для Typst: пометки — отдельными runs, картинки — копией в папку сборки."""
    out = []
    for b in blocks:
        b = dict(b)
        if "runs" in b:
            b["runs"] = mark_runs(b["runs"])
        if b["t"] in ("ul", "ol"):
            b["items"] = [dict(it, runs=mark_runs(it["runs"])) for it in b["items"]]
        if b["t"] == "table":
            n = len(b["header"])
            b["header"] = [mark_runs(c) for c in b["header"]]
            b["rows"] = [[mark_runs(c) for c in (r + [[]] * n)[:n]] for r in b["rows"]]
        if b["t"] == "img":
            src = src_dir / b["path"]
            if src.is_file():
                dst = build / "img" / src.name
                dst.parent.mkdir(exist_ok=True)
                shutil.copyfile(src, dst)
                b["file"] = f"img/{src.name}"
        out.append(b)
    return out


def literature(spec: dict, data: dict, lang: str, warns: list[str]) -> list[list[dict]]:
    items = [str(x) for x in spec.get("literature", []) or []]
    if not items and data.get("literature"):
        from content_kit import passport_literature

        items = [it["text"] for it in passport_literature(data)]
    has_course = bool(data.get("literature"))
    out = []
    for text in items:
        status = literature_status(text, data) if has_course else "unknown"
        if status in ("absent", "unverified"):
            text = f"{text} {t('unverified', lang)}"
            warns.append(f"литература: «{text[:50]}…» — нет проверенной записи в паспорте курса")
        out.append(mark_runs(parse_inline(text)))
    if items and not has_course:
        warns.append("литература не сверена с паспортом курса (course.yaml не найден) — проверьте каждый источник")
    return out


def build_docx(meta: dict, chapters: list[tuple[list[dict], Path]], lit: list[list[dict]], lang: str, path: Path):
    doc = new_document()
    para(doc, meta["ministry"], align="center", size=12)
    para(doc, meta["university"], bold=True, align="center")
    if meta["department"]:
        para(doc, meta["department"], align="center")
    for _ in range(5):
        para(doc)
    para(doc, ", ".join(meta["authors"]), align="center")
    para(doc, meta["title"].upper(), bold=True, align="center")
    if meta["subtitle"]:
        para(doc, meta["subtitle"], align="center")
    para(doc, meta["kind"], align="center")
    for _ in range(6):
        para(doc)
    para(doc, f'{meta["city"]} {meta["year"]}', align="center")
    back = para(doc, f'УДК {meta["udk"]}', indent=False)
    back.paragraph_format.page_break_before = True
    para(doc, f'ББК {meta["bbk"]}', indent=False)
    if meta["author_sign"]:
        para(doc, meta["author_sign"], indent=False)
    para(doc, meta["recommended"], italic=True, align="center", size=12)
    if meta["reviewers"]:
        para(doc, f'{t("reviewers", lang)}:', bold=True, indent=False, size=12)
        for r in meta["reviewers"]:
            para(doc, r, indent=False, size=12)
    para(doc, f'{", ".join(meta["authors"])}. {meta["title"]}: {meta["kind"]} / {", ".join(meta["authors"])}. — '
              f'{meta["city"]}, {meta["year"]}. — ___ {t("pages", lang)}', size=12)
    if meta["annotation"]:
        para(doc, meta["annotation"], size=12)
    para(doc, f'ISBN {meta["isbn_line"]}', indent=False, size=12)
    para(doc, f'© {", ".join(meta["authors"])}, {meta["year"]}', align="right", size=12)
    add_toc(doc, lang, new_page=True)
    for blocks, src in chapters:
        render_docx(doc, blocks, src, new_page=True)
    if lit:
        h = doc.add_heading(t("literature", lang), level=1)
        h.paragraph_format.page_break_before = True
        for i, runs in enumerate(lit, 1):
            add_runs(para(doc), [{"text": f"{i}. "}] + runs)
    doc.save(path)


def main() -> None:
    ap = argparse.ArgumentParser(description="Сборка учебно-методического пособия (PDF через Typst и docx)")
    ap.add_argument("manual", help="путь к manual.yaml")
    ap.add_argument("--course", help="путь к course.yaml (для литературы и титула; необязательно)")
    ap.add_argument("--no-pdf", action="store_true", help="только docx, без Typst")
    a = ap.parse_args()
    src = Path(a.manual).expanduser().resolve()
    warns: list[str] = []
    try:
        spec = read_yaml(src)
        data = load_context(src, a.course)
        lang = spec.get("language") or data.get("language", "ru")
        prof = data.get("_profile", {})
        teacher = (data.get("teacher") or {}).get("name") or prof.get("name", "")
        authors = spec.get("authors") or ([teacher] if teacher else [])
        if not spec.get("title"):
            raise DataError("в manual.yaml нет title — названия пособия")
        if not authors:
            raise DataError("не указаны авторы: заполните authors в manual.yaml или name в profile.yaml")
        files = spec.get("chapters") or []
        if not files:
            raise DataError("в manual.yaml нет списка chapters (файлы глав .md)")
        build = (out_dir(data) if data.get("course") else src.parent / "out") / "manual-build"
        build.mkdir(parents=True, exist_ok=True)
        chapters_json, chapters_docx = [], []
        for f in files:
            p = (src.parent / f).resolve()
            if not p.exists():
                raise DataError(f"не найдена глава {p}")
            _, body = split_frontmatter(p.read_text(encoding="utf-8"))
            blocks = parse_md(body)
            chapters_docx.append((blocks, p.parent))
            chapters_json.append(prep_blocks(blocks, p.parent, build))
        placeholders = {k: spec.get(k) or "____________" for k in ("udk", "bbk", "isbn")}
        for k in ("udk", "bbk", "isbn"):
            if not spec.get(k):
                warns.append(f"{k.upper()} не указан — на обороте титула прочерк; получите в библиотеке/издательстве")
        dept = prof.get("department", "")
        meta = {
            "title": str(spec["title"]), "subtitle": str(spec.get("subtitle") or ""),
            "kind": str(spec.get("kind") or t("manual_kind", lang)),
            "authors": [str(x) for x in authors], "udk": placeholders["udk"], "bbk": placeholders["bbk"],
            "isbn_line": placeholders["isbn"], "author_sign": str(spec.get("author_sign") or ""),
            "reviewers": [str(r) for r in spec.get("reviewers") or []],
            "recommended": str(spec.get("recommended") or t("recommended", lang)),
            "annotation": " ".join(str(spec.get("annotation") or "").split()),
            "city": str(spec.get("city") or prof.get("city", "")),
            "year": str(spec.get("year") or ""), "paper": "a4" if str(spec.get("paper", "a5")).lower() == "a4" else "a5",
            "lang": TYPST_LANG.get(lang, "ru"),
            "ministry": t("ministry", lang), "university": university_name(data, lang),
            "department": f'{t("department", lang)} «{dept}»' if dept else "",
        }
        if not meta["reviewers"]:
            warns.append("не указаны рецензенты (reviewers) — для издания пособия они обязательны")
        if not meta["year"]:
            raise DataError("в manual.yaml нет year — года издания")
        lit = literature(spec, data, lang, warns)
        labels = {k: t(k, lang) for k in ("reviewers", "pages", "figure", "toc", "literature")}
        (build / "data.json").write_text(json.dumps({"meta": meta, "labels": labels, "chapters": chapters_json,
                                                     "literature": lit}, ensure_ascii=False), encoding="utf-8")
        shutil.copyfile(TEMPLATE, build / "manual.typ")
        docx_path = build.parent / "manual.docx"
        build_docx(meta, chapters_docx, lit, lang, docx_path)
        print(docx_path)
        if not a.no_pdf:
            typst = shutil.which("typst")
            if not typst:
                raise DataError("Typst не установлен — PDF не собран (docx готов). Запустите /academic:setup")
            pdf = build.parent / "manual.pdf"
            r = subprocess.run([typst, "compile", "--root", str(build), str(build / "manual.typ"), str(pdf)],
                               capture_output=True, text=True, encoding="utf-8")
            if r.returncode != 0:
                raise DataError(f"Typst не собрал PDF:\n{r.stderr.strip()}")
            for line in r.stderr.splitlines():
                if line.startswith("warning:") and "unknown font family" not in line:
                    warns.append(f"Typst: {line[8:].strip()}")
            print(pdf)
    except DataError as e:
        fail(str(e))
    for w in warns:
        print(f"Предупреждение: {w}")


if __name__ == "__main__":
    main()
