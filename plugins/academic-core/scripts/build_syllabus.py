# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1", "pyyaml>=6"]
# ///
"""Силлабус дисциплины из паспорта курса → out/syllabus_<lang>.docx.

    uv run build_syllabus.py "<папка курса>/course.yaml" [--lang ru|ky|en] [--final]

--final — чистовик: непроверенная литература не попадает в документ.
Структура — skills/syllabus/references/structure.md. Форма вуза — university/settings.yaml →
syllabus: hide_sections (убрать разделы), policies (политика по умолчанию), extra_sections (свои разделы).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import loc, new_document, out_dir, para, settings, title_page  # noqa: E402
from course_check import report  # noqa: E402
from course_doc import (  # noqa: E402
    DASH, load_checked, save, sec_assessment, sec_course_info, sec_extra, sec_goals, sec_hours,
    sec_literature, sec_outcomes, sec_plan, sec_policy, sec_prereq, sec_sdg_methods, sec_signatures, sec_srs,
    sec_teacher, translation_warning,
)
from settings import lang_text  # noqa: E402
from i18n import t  # noqa: E402


def build(data: dict, lang: str, final: bool):
    doc = new_document(data)
    title_page(doc, data, lang, t("syllabus", lang))
    ys = settings(data)["syllabus"]
    hide = set(ys["hide_sections"])
    sdg_key = "methods" if "sdg" in hide else "sdg" if "methods" in hide else "sec_sdg_methods"
    # (заголовок, ключ hide_sections или None, раздел)
    sections = [
        (t("sec_teacher", lang), None, lambda: sec_teacher(doc, data, lang)),
        (t("sec_course", lang), None, lambda: (sec_course_info(doc, data, lang), sec_hours(doc, data, lang))),
        (t("sec_description", lang), None,
         lambda: para(doc, str(loc(data, "description", lang, data) or DASH).strip())),
        (t("sec_goals", lang), None, lambda: sec_goals(doc, data, lang)),
        (t("sec_prereq", lang), None, lambda: sec_prereq(doc, data, lang)),
        (t("sec_outcomes", lang), None, lambda: sec_outcomes(doc, data, lang)),
        (t(sdg_key, lang), "sdg+methods", lambda: sec_sdg_methods(doc, data, lang, hide)),
        (t("sec_plan", lang), "calendar", lambda: sec_plan(doc, data, lang)),
        (t("sec_srs", lang), "srs", lambda: sec_srs(doc, data, lang)),
        (t("sec_assessment", lang), None, lambda: sec_assessment(doc, data, lang)),
        (t("sec_policy", lang), "policies", lambda: sec_policy(doc, data, lang)),
        (t("literature", lang), "literature", lambda: sec_literature(doc, data, lang, final)),
    ]
    sections = [x for x in sections if not x[1] or not set(x[1].split("+")) <= hide]
    for item in ys["extra_sections"]:
        sections.append((lang_text(item.get("title"), lang), None,
                         lambda item=item: sec_extra(doc, data, lang, item)))
    sections.append((t("sec_signatures", lang), None, lambda: sec_signatures(doc, data, lang)))
    for n, (title, _, render) in enumerate(sections, 1):
        doc.add_heading(f"{n}. {title}", level=2)
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
