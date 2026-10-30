# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1", "pypdf>=4", "pyyaml>=6"]
# ///
"""Текст старого силлабуса / программы (docx, pdf) для переноса в course.yaml.

    uv run extract_text.py "<файл.docx|.pdf>" [--out текст.md]

Абзацы и таблицы docx — в порядке документа, таблицы строками «ячейка | ячейка».
Скан PDF без текстового слоя не читается — скрипт об этом скажет.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import fail  # noqa: E402


def docx_text(path: Path) -> str:
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    doc = Document(str(path))
    out = []
    for el in doc.element.body.iterchildren():
        tag = el.tag.rsplit("}", 1)[-1]
        if tag == "p":
            p = Paragraph(el, doc)
            text = p.text.strip()
            if text:
                style = (p.style.name or "") if p.style is not None else ""
                out.append(("## " if style.startswith("Heading") else "") + text)
        elif tag == "tbl":
            out.append("")
            for row in Table(el, doc).rows:
                cells, prev = [], None
                for c in row.cells:  # объединённые ячейки python-docx повторяет — убираем дубли
                    if c._tc is not prev:
                        cells.append(c.text.strip().replace("\n", " "))
                    prev = c._tc
                out.append(" | ".join(cells))
            out.append("")
    return "\n".join(out)


def pdf_text(path: Path) -> str:
    from pypdf import PdfReader

    pages = [(p.extract_text() or "").strip() for p in PdfReader(str(path)).pages]
    if not any(pages):
        fail(f"в {path.name} нет текстового слоя (скан). Откройте PDF через Read или пришлите docx")
    return "\n\n".join(f"<!-- стр. {i} -->\n{t}" for i, t in enumerate(pages, 1))


def main() -> None:
    ap = argparse.ArgumentParser(description="Текст из docx/pdf")
    ap.add_argument("file")
    ap.add_argument("--out", help="записать в файл вместо вывода на экран")
    args = ap.parse_args()
    path = Path(args.file).expanduser()
    if not path.exists():
        fail(f"не найден файл {path}")
    ext = path.suffix.lower()
    if ext == ".docx":
        text = docx_text(path)
    elif ext == ".pdf":
        text = pdf_text(path)
    elif ext == ".doc":
        fail("старый формат .doc не читается — сохраните файл в Word как .docx")
    else:
        fail(f"формат {ext} не поддерживается — нужен .docx или .pdf")
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Готово: {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
