# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1", "pyyaml>=6"]
# ///
"""Лекция из markdown → docx по ГОСТ; режим «курс лекций» — все лекции в один файл с оглавлением.

    uv run build_lecture.py <lectures/03-тема.md> [--course course.yaml]
    uv run build_lecture.py <lectures/ | course.yaml> [--course course.yaml]   # курс лекций
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import DataError, course_title, fail, load_course, new_document, out_dir, para, title_page  # noqa: E402
from content_kit import (  # noqa: E402
    MARKER_RE, add_toc, find_course, literature_status, parse_md, render_docx, runs_text,
    split_frontmatter,
)
from i18n import t  # noqa: E402

LIT_WORDS = ("литератур", "адабият", "reference", "reading")
REQUIRED = {
    "план": ("план",),
    "цели / результаты обучения": ("цел", "результат", "максат", "натыйжа", "outcome", "objective"),
    "ключевые понятия": ("понят", "термин", "түшүн", "concept", "glossary"),
    "вопросы для самопроверки": ("самопровер", "контрол", "өз алдынча текш", "суроо", "self-check", "review question"),
    "литература": LIT_WORDS,
}


def lecture_no(path: Path, fm: dict, fallback: int) -> int:
    if fm.get("week"):
        return int(fm["week"])
    m = re.match(r"(\d+)", path.stem)
    return int(m.group(1)) if m else fallback


def check_literature(blocks: list[dict], data: dict | None, name: str) -> list[str]:
    """Помечает в тексте источники не из паспорта; возвращает предупреждения."""
    warns, inside, lvl = [], False, 0
    unverified = t("unverified", (data or {}).get("language", "ru"))
    for b in blocks:
        if b["t"] == "h":
            if inside and b["level"] <= lvl:
                inside = False
            if any(w in runs_text(b["runs"]).lower() for w in LIT_WORDS):
                inside, lvl = True, b["level"]
            continue
        if not inside or b["t"] not in ("ul", "ol", "p"):
            continue
        items = b["items"] if b["t"] in ("ul", "ol") else [b]
        for it in items:
            text = runs_text(it["runs"])
            if data is None:
                continue
            status = literature_status(text, data)
            if status != "ok" and not MARKER_RE.search(text):
                it["runs"].append({"text": f" {unverified}"})
                why = "нет в паспорте курса" if status == "absent" else "в паспорте не проверен"
                warns.append(f"{name}: источник «{text[:60]}…» — {why}, помечен {unverified}")
    if data is None:
        warns.append(f"{name}: паспорт курса не найден — литература не сверена")
    return warns


def check_structure(blocks: list[dict], name: str) -> list[str]:
    heads = " | ".join(runs_text(b["runs"]).lower() for b in blocks if b["t"] == "h")
    return [f"{name}: нет раздела «{sec}»" for sec, words in REQUIRED.items()
            if not any(w in heads for w in words)]


def load_lecture(path: Path, data: dict | None) -> tuple[dict, list[dict], list[str]]:
    try:
        fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise DataError(f"не найден файл лекции {path}")
    blocks = parse_md(body)
    if not blocks:
        raise DataError(f"файл {path.name} пустой")
    warns = check_structure(blocks, path.name) + check_literature(blocks, data, path.name)
    return fm, blocks, warns


def lectures_out(data: dict | None, anchor: Path) -> Path:
    d = (out_dir(data) if data else anchor / "out") / "lectures"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_one(md: Path, data: dict | None) -> tuple[Path, list[str], int]:
    fm, blocks, warns = load_lecture(md, data)
    doc = new_document()
    if data:
        lang = data.get("language", "ru")
        para(doc, f'{t("discipline", lang).capitalize()}: «{course_title(data, lang)}»', italic=True, align="right", size=12)
    marks = render_docx(doc, blocks, md.parent)
    no = lecture_no(md, fm, 1)
    anchor = data["_dir"] if data else md.parent.parent
    path = lectures_out(data, anchor) / f"{no:02d}.docx"
    doc.save(path)
    return path, warns, marks


def build_book(files: list[Path], data: dict | None, anchor: Path) -> tuple[Path, list[str], int]:
    doc = new_document()
    lang = (data or {}).get("language", "ru")
    if data:
        title_page(doc, data, lang, t("lectures_book", lang), approve=False)
    add_toc(doc, lang)
    warns, marks = [], 0
    for md in files:
        _, blocks, w = load_lecture(md, data)
        warns += w
        marks += render_docx(doc, blocks, md.parent, new_page=True)
    path = lectures_out(data, anchor) / "lectures.docx"
    doc.save(path)
    return path, warns, marks


def main() -> None:
    ap = argparse.ArgumentParser(description="Сборка лекции (или курса лекций) в docx")
    ap.add_argument("source", help="файл лекции .md, папка lectures/ или course.yaml (курс лекций)")
    ap.add_argument("--course", help="путь к course.yaml (по умолчанию ищется выше по папкам)")
    a = ap.parse_args()
    src = Path(a.source).expanduser().resolve()
    try:
        if not src.exists():
            raise DataError(f"не найден {src}")
        course = Path(a.course).expanduser().resolve() if a.course else find_course(src)
        data = load_course(course) if course else None
        if src.suffix.lower() == ".md":
            path, warns, marks = build_one(src, data)
        else:
            lec_dir = src if src.is_dir() else src.parent / "lectures"
            if src.is_dir() and src.name != "lectures" and (src / "lectures").is_dir():
                lec_dir = src / "lectures"
            files = sorted(p for p in lec_dir.glob("*.md") if not p.name.startswith("_"))
            if not files:
                raise DataError(f"в {lec_dir} нет лекций (*.md) — сначала напишите их skill'ом lecture")
            anchor = data["_dir"] if data else lec_dir.parent
            path, warns, marks = build_book(files, data, anchor)
    except DataError as e:
        fail(str(e))
    print(path)
    for w in warns:
        print(f"Предупреждение: {w}")
    if marks:
        print(f"Предупреждение: в тексте {marks} пометок вроде [нужен источник] — проверьте до выдачи студентам")


if __name__ == "__main__":
    main()
