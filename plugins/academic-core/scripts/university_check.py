# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Проверка настроек вуза university/settings.yaml: что действует и что отличается от норм КР.

    uv run university_check.py [папка] [--yaml]

папка — рабочая папка, папка курса или сама university/ (по умолчанию текущая).
--yaml — напечатать все действующие настройки (для skills).
Код возврата ≠ 0, если в настройках ошибки. Справочник ключей — references/university-settings.md.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from settings import DEFAULTS, DataError, diff_from_defaults, get_key, lang_text, load_settings, public  # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# Что за ключ — по-человечески, для сводки.
KEY_NAMES = {
    "university": "вуз", "brand": "фирменный стиль", "document": "оформление Word",
    "approval": "«УТВЕРЖДАЮ» / «СОГЛАСОВАНО»", "grading": "оценивание", "syllabus": "силлабус",
    "tests": "тесты", "research": "научные работы", "manual": "пособие", "environment": "окружение",
    "university.name": "название вуза", "university.name_ky": "название на кыргызском",
    "university.name_en": "название на английском", "university.short": "краткое название",
    "university.city": "город на титуле", "university.type": "тип вуза",
    "university.ministry": "министерство на титуле",
    "brand.logo": "логотип", "brand.color": "акцентный цвет",
    "document.font": "шрифт", "document.size": "кегль", "document.table_size": "кегль таблиц",
    "document.line_spacing": "интервал", "document.indent_cm": "абзацный отступ, см",
    "document.margins_mm.left": "левое поле, мм", "document.margins_mm.right": "правое поле, мм",
    "document.margins_mm.top": "верхнее поле, мм", "document.margins_mm.bottom": "нижнее поле, мм",
    "document.page_numbers": "номера страниц", "document.title_page_logo": "логотип на титуле",
    "approval.enabled": "«УТВЕРЖДАЮ» на титуле", "approval.role": "кто утверждает",
    "approval.name": "ФИО утверждающего", "approval.agreed": "«СОГЛАСОВАНО»",
    "approval.protocol": "строка о протоколе кафедры",
    "grading.credit_hours": "часов в кредите", "grading.scale": "шкала оценок",
    "grading.assessment_template": "шаблон БРС",
    "syllabus.hide_sections": "скрытые разделы силлабуса", "syllabus.extra_sections": "свои разделы силлабуса",
    "tests.formats": "форматы тестов", "tests.variants": "вариантов", "tests.questions_per_variant":
    "вопросов в варианте", "tests.moodle": "Moodle", "tests.moodle_version": "версия Moodle",
    "research.citation_style": "стиль ссылок", "research.bib_order": "порядок списка литературы",
    "research.thesis_pages": "объём ВКР", "research.plagiarism_min": "оригинальность не ниже, %",
    "manual.paper": "формат пособия", "manual.approval_body": "кто рекомендует пособие к изданию",
    "environment.os": "ОС преподавателей", "environment.languages": "языки документов",
}


def name(key: str) -> str:
    if key in KEY_NAMES:
        return KEY_NAMES[key]
    if key.startswith("syllabus.policies."):
        return "политика курса: " + key.rsplit(".", 1)[1]
    return KEY_NAMES.get(key.rsplit(".", 1)[0], key)


def show(v) -> str:
    if isinstance(v, bool):
        return "да" if v else "нет"
    if isinstance(v, dict) and set(v) <= {"ru", "ky", "en"}:
        return lang_text(v, "ru")
    if isinstance(v, list) and v and all(isinstance(x, (str, int, float)) for x in v):
        return ", ".join(map(str, v))
    if isinstance(v, (list, dict)):
        text = " ".join(yaml.safe_dump(v, allow_unicode=True, default_flow_style=True, width=1000).split())
        return text if len(text) <= 90 else text[:87] + "…"
    return str(v)


def summary(s: dict) -> list[str]:
    lines = []
    u = s["university"]
    if u["name"]:
        lines.append(f'Вуз: {u["name"]}' + (f' ({u["short"]})' if u["short"] else "")
                     + (", частный" if u["type"] == "private" else ", государственный"))
    scale = "; ".join(f'{r.get("letter", "")} {r["min"]}–{r["max"]} {lang_text(r.get("grade"), "ru")}'.strip()
                      for r in s["grading"]["scale"])
    lines.append(f"Шкала оценок: {scale}")
    tpl = s["grading"]["assessment_template"]
    lines.append("Шаблон БРС: " + ("; ".join(f'{a["name"]} {a["weight"]:g}' for a in tpl) if tpl
                                   else "не задан — /academic-core:new-course спросит"))
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(description="Проверка university/settings.yaml")
    ap.add_argument("folder", nargs="?", default=".", help="рабочая папка или папка курса")
    ap.add_argument("--yaml", action="store_true", help="все действующие настройки в YAML")
    args = ap.parse_args()
    start = Path(args.folder).expanduser().resolve()
    if start.name == "university" and start.is_dir():
        start = start.parent
    try:
        s = load_settings(start, strict=False)
    except DataError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    if args.yaml:
        print(yaml.safe_dump(public(s), allow_unicode=True, sort_keys=False, width=100).rstrip())
    else:
        if s["_file"]:
            print(f"Настройки вуза: {s['_file']}")
        elif s["_brand_file"]:
            print(f"Настройки вуза: только {s['_brand_file']} (старый формат) — остальное по нормам КР")
        else:
            print("Файла university/settings.yaml нет — действуют нормы КР по умолчанию.")
            print("Настроить под свой вуз: /academic-core:university")
        for line in summary(s):
            print(line)
        diff = diff_from_defaults(s)
        if diff:
            print(f"\nОтличается от норм КР ({len(diff)}):")
            for key, v in diff:
                if key in ("grading.scale", "grading.assessment_template"):
                    print(f"  • {name(key)} [{key}]: своя — см. выше")
                    continue
                dflt = get_key(DEFAULTS, key)
                tail = f" (по умолчанию: {show(dflt)})" if show(dflt) not in ("", "[]", "{}") else ""
                print(f"  • {name(key)} [{key}]: {show(v)}{tail}")
        else:
            print("\nВсё по нормам КР по умолчанию.")
    if s["_errors"]:
        print(f"\nОшибки ({len(s['_errors'])}):", file=sys.stderr if args.yaml else sys.stdout)
        for e in s["_errors"]:
            print(f"  ✗ {e}", file=sys.stderr if args.yaml else sys.stdout)
    if s["_warnings"]:
        print(f"\nПредупреждения ({len(s['_warnings'])}):", file=sys.stderr if args.yaml else sys.stdout)
        for w in s["_warnings"]:
            print(f"  ! {w}", file=sys.stderr if args.yaml else sys.stdout)
    if s["_errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
