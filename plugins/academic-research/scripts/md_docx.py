# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1", "pyyaml>=6"]
# ///
"""Документ преподавателя из markdown в docx по ГОСТ: задание, методичка, критерии, рецензия, отзыв.

    uv run md_docx.py "<файл>.md" [--org] [--out "<файл>.docx"]

# Заголовок — по центру жирным, ## — подраздел, таблицы | … |, списки, **жирный**, *курсив*.
--org — шапка: министерство, вуз, факультет, кафедра из profile.yaml (ищется выше по дереву).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import DataError, fail, find_up, read_yaml, utf8_stdout  # noqa: E402
from docxkit import Ctx, heading, new_document, para, render_markdown  # noqa: E402
from i18n import t  # noqa: E402


def build(md: Path, out: Path | None = None, org: bool = False) -> Path:
    if not md.exists():
        raise DataError(f"не найден файл {md}")
    text = md.read_text(encoding="utf-8")
    prof_path = find_up(md.parent, "profile.yaml")
    prof = read_yaml(prof_path) if prof_path else {}
    lang = prof.get("language", "ru")
    doc = new_document()
    if org:
        para(doc, t("ministry", lang), align="center", spacing=1.0)
        if prof.get("university"):
            para(doc, prof["university"], bold=True, align="center", spacing=1.0)
        if prof.get("faculty"):
            para(doc, prof["faculty"], align="center", spacing=1.0)
        if prof.get("department"):
            para(doc, f'{t("department", lang)} «{prof["department"]}»', align="center", spacing=1.0)
        para(doc)
    ctx = Ctx(base_dir=md.parent, lang=lang)
    chunks = re.split(r"^#\s+(.+)$", text, flags=re.M)
    render_markdown(doc, chunks[0], ctx)
    for title, body in zip(chunks[1::2], chunks[2::2]):
        heading(doc, title.strip(), 1)
        render_markdown(doc, body, ctx)
    out = out or md.with_suffix(".docx")
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    return out


def main() -> None:
    utf8_stdout()
    ap = argparse.ArgumentParser(description="markdown → docx по ГОСТ")
    ap.add_argument("md")
    ap.add_argument("--org", action="store_true", help="шапка вуза из profile.yaml")
    ap.add_argument("--out")
    args = ap.parse_args()
    try:
        out = build(Path(args.md).expanduser().resolve(), Path(args.out) if args.out else None, args.org)
    except DataError as e:
        fail(str(e))
    print(f"Готово: {out}")


if __name__ == "__main__":
    main()
