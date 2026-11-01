# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1", "pyyaml>=6"]
# ///
"""Задания СРС и практических / лабораторных занятий: srs.yaml → out/srs.docx.

    uv run build_srs.py <srs.yaml> [--course course.yaml]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import (  # noqa: E402
    DataError, fail, find_up, load_course, load_settings, new_document, out_dir, para, read_yaml, table, title_page,
)
from content_kit import add_runs, literature_status, parse_inline  # noqa: E402
from i18n import LABELS, t  # noqa: E402

LABELS.update({
    "srs_title": {"ru": "Задания для самостоятельной работы студентов и практических занятий",
                  "ky": "Студенттердин өз алдынча иштөөсү жана практикалык сабактар үчүн тапшырмалар",
                  "en": "Self-study and practical assignments"},
    "srs_summary": {"ru": "Сводный график заданий", "ky": "Тапшырмалардын жалпы графиги", "en": "Assignment schedule"},
    "s_task": {"ru": "Задание", "ky": "Тапшырма", "en": "Assignment"},
    "kind": {"ru": "Вид работы", "ky": "Иштин түрү", "en": "Type"},
    "goal": {"ru": "Цель", "ky": "Максаты", "en": "Goal"},
    "task_text": {"ru": "Содержание задания", "ky": "Тапшырманын мазмуну", "en": "Task"},
    "steps": {"ru": "Порядок выполнения", "ky": "Аткаруу тартиби", "en": "Procedure"},
    "submission": {"ru": "Форма сдачи", "ky": "Тапшыруу формасы", "en": "Submission"},
    "deadline": {"ru": "Срок сдачи", "ky": "Тапшыруу мөөнөтү", "en": "Deadline"},
    "deadline_week": {"ru": "неделя", "ky": "апта", "en": "week"},
    "criteria": {"ru": "Критерии оценивания", "ky": "Баалоо критерийлери", "en": "Assessment rubric"},
    "criterion": {"ru": "Критерий", "ky": "Критерий", "en": "Criterion"},
    "s_points": {"ru": "Баллы", "ky": "Упай", "en": "Points"},
    "lvl_excellent": {"ru": "Отлично", "ky": "Эң жакшы", "en": "Excellent"},
    "lvl_good": {"ru": "Хорошо", "ky": "Жакшы", "en": "Good"},
    "lvl_satisfactory": {"ru": "Удовл.", "ky": "Канааттанд.", "en": "Satisfactory"},
    "lvl_poor": {"ru": "Неудовл.", "ky": "Канааттанд. эмес", "en": "Unsatisfactory"},
    "s_max_points": {"ru": "Максимум баллов", "ky": "Эң көп упай", "en": "Maximum points"},
    "hours_short": {"ru": "Часы", "ky": "Саат", "en": "Hours"},
})
LEVELS = ("excellent", "good", "satisfactory", "poor")


def lit_line(text: str, data: dict | None, lang: str, warns: list[str], where: str) -> str:
    if not data:
        return text
    status = literature_status(text, data)
    if status == "ok":
        return text
    warns.append(f"{where}: источник «{text[:50]}…» — {'нет в паспорте' if status == 'absent' else 'не проверен'}")
    return f"{text} {t('unverified', lang)}"


def check_task(tk: dict, where: str, data: dict | None) -> list[str]:
    warns = []
    for key, name in (("goal", "цели"), ("task", "задания"), ("submission", "формы сдачи"),
                      ("deadline_week", "срока"), ("criteria", "критериев оценивания")):
        if not tk.get(key):
            warns.append(f"{where}: нет {name} ({key})")
    if data:
        known = {str(o.get("id")) for o in data.get("outcomes", []) or []}
        for o in tk.get("outcomes", []) or []:
            if str(o) not in known:
                warns.append(f"{where}: РО «{o}» нет в паспорте курса")
        weeks = int(data.get("weeks") or 0)
        if weeks and int(tk.get("deadline_week") or 0) > weeks:
            warns.append(f"{where}: срок — неделя {tk['deadline_week']}, а в курсе {weeks} недель")
    return warns


def task_section(doc, n: int, tk: dict, data: dict | None, lang: str, warns: list[str], *, new_page=False) -> None:
    where = f"задание {n}"
    warns += check_task(tk, where, data)
    h = doc.add_heading(f'{t("s_task", lang)} {n}. {tk.get("topic", "")}', level=2)
    h.paragraph_format.page_break_before = new_page

    def field(label: str, value):
        if not value:
            return
        p = para(doc, indent=False)
        add_runs(p, [{"text": f"{label}: ", "b": True}] + parse_inline(str(value).strip()))

    field(t("kind", lang), tk.get("kind"))
    if tk.get("week"):
        field(t("week", lang), tk["week"])
    field(t("goal", lang), tk.get("goal"))
    if tk.get("outcomes"):
        names = {str(o.get("id")): o.get("text", "") for o in (data or {}).get("outcomes", []) or []}
        field(t("outcomes", lang), "; ".join(f"{o} — {names[str(o)]}" if names.get(str(o)) else str(o)
                                              for o in tk["outcomes"]))
    if tk.get("sdg"):
        field("ЦУР", ", ".join(str(x) for x in tk["sdg"]))
    if tk.get("task"):
        para(doc, f'{t("task_text", lang)}:', bold=True, indent=False)
        for chunk in str(tk["task"]).strip().split("\n\n"):
            add_runs(para(doc), parse_inline(" ".join(chunk.split())))
    if tk.get("steps"):
        para(doc, f'{t("steps", lang)}:', bold=True, indent=False)
        for i, st in enumerate(tk["steps"], 1):
            p = para(doc)
            add_runs(p, [{"text": f"{i}. "}] + parse_inline(str(st)))
    field(t("submission", lang), tk.get("submission"))
    if tk.get("deadline_week"):
        field(t("deadline", lang), f'{tk["deadline_week"]} {t("deadline_week", lang)}')
    if tk.get("hours"):
        field(t("hours_short", lang), tk["hours"])
    crit = tk.get("criteria") or []
    if crit:
        para(doc, f'{t("criteria", lang)}:', bold=True, indent=False)
        header = [f'{t("criterion", lang)} ({t("s_points", lang).lower()})'] + [t(f"lvl_{lv}", lang) for lv in LEVELS]
        rows, total = [], 0
        for c in crit:
            lv = c.get("levels") or {}
            pts = c.get("points", "")
            total += int(pts or 0)
            rows.append([f'{c.get("criterion", "")} ({pts})'] + [lv.get(k, "") for k in LEVELS])
            missing = [k for k in LEVELS if not lv.get(k)]
            if missing:
                warns.append(f"{where}: у критерия «{c.get('criterion', '')}» нет уровней {', '.join(missing)}")
        rows.append([f'{t("s_max_points", lang)}: {total}', "", "", "", ""])
        table(doc, header, rows, widths_cm=[3.7, 3.2, 3.2, 3.2, 3.2])
        if tk.get("max_points") and int(tk["max_points"]) != total:
            warns.append(f"{where}: сумма баллов критериев {total}, а max_points {tk['max_points']}")
    if tk.get("literature"):
        para(doc, f'{t("literature", lang)}:', bold=True, indent=False)
        for i, lit in enumerate(tk["literature"], 1):
            para(doc, f"{i}. " + lit_line(str(lit), data, lang, warns, where))


def build(spec: dict, data: dict | None, base: Path) -> tuple[Path, list[str]]:
    lang = spec.get("language") or (data or {}).get("language", "ru")
    tasks = spec.get("tasks") or []
    if not tasks:
        raise DataError("в srs.yaml нет списка tasks")
    warns: list[str] = []
    doc = new_document(data or load_settings(base))
    if data:
        title_page(doc, data, lang, spec.get("title") or t("srs_title", lang), approve=False)
    else:
        para(doc, (spec.get("title") or t("srs_title", lang)).upper(), bold=True, align="center")
    if spec.get("intro"):
        for chunk in str(spec["intro"]).strip().split("\n\n"):
            add_runs(para(doc), parse_inline(" ".join(chunk.split())))
    doc.add_heading(t("srs_summary", lang), level=1)
    rows = [[i, tk.get("topic", ""), tk.get("kind", ""), tk.get("week", ""), tk.get("deadline_week", ""),
             tk.get("hours", ""), sum(int(c.get("points") or 0) for c in tk.get("criteria") or []) or ""]
            for i, tk in enumerate(tasks, 1)]
    table(doc, ["№", t("topic", lang), t("kind", lang), t("week", lang), t("deadline", lang),
                t("hours_short", lang), t("s_points", lang)], rows, widths_cm=[0.9, 5.8, 3.0, 1.9, 1.9, 1.4, 1.6])
    if data:
        srs_hours = int((data.get("hours") or {}).get("srs") or 0)
        planned = sum(int(tk.get("hours") or 0) for tk in tasks if "срс" in str(tk.get("kind", "")).lower()
                      or "сөи" in str(tk.get("kind", "")).lower())
        if srs_hours and planned and planned != srs_hours:
            warns.append(f"часы СРС по заданиям {planned}, в паспорте {srs_hours}")
    for i, tk in enumerate(tasks, 1):
        task_section(doc, i, tk, data, lang, warns, new_page=True)
    d = out_dir(data) if data else base / "out"
    d.mkdir(parents=True, exist_ok=True)
    path = d / (spec.get("output") or "srs.docx")
    doc.save(path)
    return path, warns


def main() -> None:
    ap = argparse.ArgumentParser(description="Сборка заданий СРС в docx")
    ap.add_argument("srs", help="путь к srs.yaml")
    ap.add_argument("--course", help="путь к course.yaml (по умолчанию ищется выше по папкам)")
    a = ap.parse_args()
    src = Path(a.srs).expanduser().resolve()
    try:
        spec = read_yaml(src)
        course = Path(a.course).expanduser().resolve() if a.course else find_up(src.parent, "course.yaml")
        data = load_course(course) if course else None
        path, warns = build(spec, data, src.parent)
    except DataError as e:
        fail(str(e))
    print(path)
    for w in warns:
        print(f"Предупреждение: {w}")


if __name__ == "__main__":
    main()
