# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1", "pyyaml>=6"]
# ///
"""Силлабус дисциплины из паспорта курса → out/syllabus_<lang>.docx.

    uv run build_syllabus.py "<папка курса>/course.yaml" [--lang ru|ky|en] [--final]

--final — чистовик: непроверенная литература не попадает в документ.
Структура — skills/syllabus/references/structure.md.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import loc, new_document, out_dir, para, title_page  # noqa: E402
from course_check import report  # noqa: E402
from course_doc import (  # noqa: E402
    DASH, heading, load_checked, save, sec_assessment, sec_course_info, sec_goals, sec_hours, sec_literature,
    sec_outcomes, sec_plan, sec_policy, sec_prereq, sec_sdg_methods, sec_signatures, sec_srs, sec_teacher,
    translation_warning,
)
from i18n import t  # noqa: E402


def build(data: dict, lang: str, final: bool):
    doc = new_document()
    title_page(doc, data, lang, t("syllabus", lang))
    sections = [
        ("sec_teacher", lambda: sec_teacher(doc, data, lang)),
        ("sec_course", lambda: (sec_course_info(doc, data, lang), sec_hours(doc, data, lang))),
        ("sec_description", lambda: para(doc, str(loc(data, "description", lang, data) or DASH).strip())),
        ("sec_goals", lambda: sec_goals(doc, data, lang)),
        ("sec_prereq", lambda: sec_prereq(doc, data, lang)),
        ("sec_outcomes", lambda: sec_outcomes(doc, data, lang)),
        ("sec_sdg_methods", lambda: sec_sdg_methods(doc, data, lang)),
        ("sec_plan", lambda: sec_plan(doc, data, lang)),
        ("sec_srs", lambda: sec_srs(doc, data, lang)),
        ("sec_assessment", lambda: sec_assessment(doc, data, lang)),
        ("sec_policy", lambda: sec_policy(doc, data, lang)),
        ("literature", lambda: sec_literature(doc, data, lang, final)),
        ("sec_signatures", lambda: sec_signatures(doc, data, lang)),
    ]
    for n, (key, render) in enumerate(sections, 1):
        heading(doc, n, key, lang)
        render()
    return doc


def main() -> None:
    ap = argparse.ArgumentParser(description="Силлабус из course.yaml")
    ap.add_argument("course", help="путь к course.yaml")
    ap.add_argument("--lang", choices=["ru", "ky", "en"], help="язык документа (по умолчанию — язык паспорта)")
    ap.add_argument("--final", action="store_true", help="чистовик: без непроверенной литературы")
    args = ap.parse_args()
    data, warnings = load_checked(args.course, "силлабус")
    lang = args.lang or data.get("language", "ru")
    doc = build(data, lang, args.final)
    translation_warning(data, lang, warnings)
    path = out_dir(data) / f"syllabus_{lang}.docx"
    save(doc, path)
    if warnings:
        report([], warnings)
    print(f"Готово: {path}")


if __name__ == "__main__":
    main()
