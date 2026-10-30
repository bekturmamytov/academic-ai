# /// script
# requires-python = ">=3.10"
# dependencies = ["python-pptx>=1.0", "pyyaml>=6"]
# ///
"""Презентация .pptx → slides.yaml для видео-лекции (текст слайдов и заметки докладчика).

    uv run slides_from_pptx.py <файл.pptx> [--out slides.yaml]

Тип слайда угадывается: первый — title, таблица — table, без пунктов — section,
последний без пунктов — closing, остальные — bullets. Проверьте результат глазами.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import yaml

from common import DataError, fail

MAX_BULLETS = 8


def _shape_lines(shape) -> list[str]:
    if not shape.has_text_frame:
        return []
    return [p.text.strip() for p in shape.text_frame.paragraphs if p.text.strip()]


def _is_title(shape) -> bool:
    if not shape.is_placeholder:
        return False
    return "TITLE" in str(shape.placeholder_format.type)  # TITLE, CENTER_TITLE


def _is_subtitle(shape) -> bool:
    return shape.is_placeholder and "SUBTITLE" in str(shape.placeholder_format.type)


def _walk(shapes):
    for sh in shapes:
        if sh.shape_type == 6:  # MSO_SHAPE_TYPE.GROUP
            yield from _walk(sh.shapes)
        else:
            yield sh


def extract(path: Path) -> dict:
    from pptx import Presentation
    from pptx.exc import PackageNotFoundError

    try:
        prs = Presentation(str(path))
    except (PackageNotFoundError, KeyError, ValueError) as e:
        raise DataError(f"{path.name} не открывается как презентация PowerPoint: {e}")

    raw = list(prs.slides)
    if not raw:
        raise DataError(f"в {path.name} нет слайдов")
    slides = []
    for idx, slide in enumerate(raw):
        title, subtitle, bullets, table = "", "", [], None
        for sh in _walk(slide.shapes):
            if getattr(sh, "has_table", False) and sh.has_table and table is None:
                rows = [[c.text.strip() for c in r.cells] for r in sh.table.rows]
                table = {"header": rows[0], "rows": rows[1:]} if rows else None
            elif _is_title(sh) and not title:
                title = " ".join(_shape_lines(sh))
            elif _is_subtitle(sh):
                subtitle = " ".join(_shape_lines(sh))
            else:
                bullets.extend(_shape_lines(sh))
        notes = ""
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame is not None:
            notes = slide.notes_slide.notes_text_frame.text.strip()

        if idx == 0:
            kind = "title"
            if not subtitle and bullets:
                subtitle = bullets[0]
            bullets = []
        elif table:
            kind = "table"
        elif not bullets:
            kind = "closing" if idx == len(raw) - 1 else "section"
        else:
            kind = "bullets"
        item = {"type": kind, "title": title or (bullets[0] if bullets else f"Слайд {idx + 1}")}
        if subtitle:
            item["subtitle"] = subtitle
        if kind == "bullets":
            item["bullets"] = bullets[:MAX_BULLETS]
        if table:
            item["table"] = table
        item["notes"] = notes
        slides.append(item)

    props = prs.core_properties
    return {
        "title": slides[0]["title"],
        "course": (props.subject or "").strip(),
        "teacher": (props.author or "").strip(),
        "slides": slides,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="pptx → slides.yaml")
    ap.add_argument("pptx")
    ap.add_argument("--out", help="куда записать slides.yaml (по умолчанию рядом, <имя>.yaml)")
    a = ap.parse_args()
    src = Path(a.pptx).expanduser().resolve()
    out = Path(a.out) if a.out else src.with_suffix(".yaml")
    try:
        data = extract(src)
    except DataError as e:
        fail(str(e))
    out.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
    empty = [str(i) for i, s in enumerate(data["slides"], 1) if not s["notes"]]
    if empty:
        print(f"Внимание: без заметок докладчика слайды {', '.join(empty)} — озвучке нечего читать.", file=sys.stderr)
    print(out)


if __name__ == "__main__":
    main()
