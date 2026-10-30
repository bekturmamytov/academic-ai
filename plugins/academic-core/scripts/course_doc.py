"""Общие разделы docx из паспорта курса: силлабус и рабочая программа собираются из них.

Каждая функция sec_* дописывает раздел в документ; заголовок раздела ставит вызывающий.
"""
from __future__ import annotations

from pathlib import Path

from common import DataError, HOUR_KINDS, course_title, fail, load_course, loc, para, table
from course_check import assessment_plan, grading_scale, report, scale_grade, validate_course
from i18n import bloom_name, method_name, sdg_name, t, tv

DASH = "—"


def heading(doc, n: int, key: str, lang: str) -> None:
    doc.add_heading(f"{n}. {t(key, lang)}", level=2)


def label(doc, text: str) -> None:
    para(doc, text, bold=True, indent=False).paragraph_format.keep_with_next = True


def kv_table(doc, rows: list[tuple[str, str]]) -> None:
    """Таблица «поле — значение» без шапки."""
    table(doc, ["", ""], [[k, v or DASH] for k, v in rows], widths_cm=[6, 10.5])
    tbl = doc.tables[-1]
    tbl._tbl.remove(tbl.rows[0]._tr)


def topics_sorted(data: dict) -> list[dict]:
    return sorted(data.get("topics", []) or [], key=lambda x: x.get("week", 0))


def outcome_weeks(data: dict) -> dict[str, list[int]]:
    res: dict[str, list[int]] = {}
    for tp in topics_sorted(data):
        for ref in tp.get("outcomes", []) or []:
            res.setdefault(str(ref), []).append(tp.get("week"))
    return res


def lit_items(data: dict, cat: str, lang: str, final: bool) -> list[str]:
    out = []
    for item in (data.get("literature") or {}).get(cat, []) or []:
        text = item.get("text") if isinstance(item, dict) else str(item)
        ok = isinstance(item, dict) and item.get("verified") is True
        if not ok and final:
            continue
        out.append(text if ok else f"{t('unverified', lang)} {text}")
    return out


# ---------- разделы ----------

def sec_teacher(doc, data: dict, lang: str) -> None:
    tch = data.get("teacher") or {}
    kv_table(doc, [
        (t("f_name", lang), tch.get("name")),
        (t("f_degree", lang), tch.get("degree")),
        (t("f_position", lang), tch.get("position")),
        (t("f_email", lang), tch.get("email")),
        (t("f_office_hours", lang), loc(tch, "office_hours", lang, data)),
    ])


def sec_course_info(doc, data: dict, lang: str) -> None:
    c = data.get("course") or {}
    kv_table(doc, [
        (t("f_code", lang), c.get("code")),
        (t("f_title", lang), course_title(data, lang)),
        (t("f_type", lang), tv(c.get("type"), lang)),
        (t("f_cycle", lang), tv(c.get("cycle"), lang)),
        (t("f_program", lang), loc(c, "program", lang, data)),
        (t("f_level", lang), tv(c.get("level"), lang)),
        (t("f_year_sem", lang), f'{c.get("year", DASH)} / {c.get("semester", DASH)}'),
        (t("f_academic_year", lang), c.get("academic_year")),
        (t("f_form", lang), tv(c.get("form"), lang)),
        (t("f_lang", lang), tv(c.get("language_of_instruction"), lang)),
        (t("credits", lang), str(data.get("credits", ""))),
        (t("f_weeks", lang), str(data.get("weeks", ""))),
    ])


def sec_hours(doc, data: dict, lang: str) -> None:
    """Объём: кредиты, всего, по видам — одной строкой."""
    hours = data.get("hours") or {}
    total = sum(int(hours.get(k, 0) or 0) for k in HOUR_KINDS)
    table(doc, [t("credits", lang), t("all_hours", lang)] + [t(k, lang) for k in HOUR_KINDS],
          [[data.get("credits"), total] + [hours.get(k, 0) for k in HOUR_KINDS]])


def sec_goals(doc, data: dict, lang: str) -> None:
    goals = loc(data, "goals", lang, data) or []
    objectives = loc(data, "objectives", lang, data) or []
    if objectives:
        label(doc, f'{t("goals", lang)}:')
    for g in goals or [DASH]:
        para(doc, f"– {g}")
    if objectives:
        label(doc, f'{t("objectives", lang)}:')
        for o in objectives:
            para(doc, f"– {o}")


def sec_prereq(doc, data: dict, lang: str) -> None:
    c = data.get("course") or {}
    pre = loc(c, "prerequisites", lang, data) or []
    post = loc(c, "postrequisites", lang, data) or []
    para(doc, f'{t("prerequisites", lang)}: {", ".join(pre) or DASH}.')
    para(doc, f'{t("postrequisites", lang)}: {", ".join(post) or DASH}.')


def sec_outcomes(doc, data: dict, lang: str) -> None:
    ow = outcome_weeks(data)
    rows = []
    for o in data.get("outcomes", []) or []:
        comp = ", ".join(map(str, o.get("competencies", []) or []))
        rows.append([o.get("id"), loc(o, "text", lang, data), bloom_name(o.get("bloom"), lang),
                     ", ".join(str(w) for w in ow.get(str(o.get("id")), [])) or DASH, comp or DASH])
    header = [t("code", lang), t("outcome", lang), t("bloom_level", lang), t("topics_weeks", lang)]
    if any(r[4] != DASH for r in rows):
        table(doc, header + [t("competencies", lang)], rows, widths_cm=[1.6, 7.4, 2.6, 2.4, 2.5])
    else:
        table(doc, header, [r[:4] for r in rows], widths_cm=[1.6, 9.0, 3.0, 2.9])
    comps = data.get("competencies") or []
    if comps:
        items = [f'{x.get("code")} — {loc(x, "text", lang, data)}' if isinstance(x, dict) else str(x) for x in comps]
        para(doc, f'{t("competencies", lang)}: {"; ".join(items)}.')


def sec_sdg_methods(doc, data: dict, lang: str) -> None:
    sdg = data.get("sdg") or []
    label(doc, f'{t("sdg", lang)}:')
    for s in sdg or []:
        para(doc, f'– {t("sdg_short", lang)} {s} «{sdg_name(s, lang)}»')
    if not sdg:
        para(doc, DASH)
    label(doc, f'{t("methods", lang)}:')
    for m in data.get("methods") or [DASH]:
        para(doc, f"– {method_name(m, lang)}")


def sec_plan(doc, data: dict, lang: str) -> None:
    topics = topics_sorted(data)
    kinds = [k for k in HOUR_KINDS if any(tp.get(k) for tp in topics)]
    rows, sums = [], {k: 0 for k in kinds}
    for tp in topics:
        title = str(loc(tp, "title", lang, data))
        ctrl = loc(tp, "control", lang, data)
        if ctrl and str(ctrl) not in title:
            title = f"{title}. {ctrl}"
        rows.append([tp.get("week"), title] + [tp.get(k, 0) or 0 for k in kinds]
                    + [", ".join(map(str, tp.get("outcomes", []) or []))])
        for k in kinds:
            sums[k] += int(tp.get(k, 0) or 0)
    rows.append(["", t("total", lang)] + [sums[k] for k in kinds] + [""])
    kw = {"lectures": 1.0, "practicals": 1.0, "labs": 1.3, "srsp": 1.6, "srs": 1.5}
    table(doc, [t("week", lang), t("topic", lang)] + [t(f"a_{k}", lang) for k in kinds]
          + ["LO" if lang == "en" else "РО"],
          rows, widths_cm=[1.8, 16.5 - 1.8 - 2.6 - sum(kw[k] for k in kinds)] + [kw[k] for k in kinds] + [2.6])
    p = para(doc, t("legend", lang), italic=True, indent=False, size=12)
    p.paragraph_format.line_spacing = 1.0


def sec_srs(doc, data: dict, lang: str) -> None:
    rows = []
    for tp in topics_sorted(data):
        if tp.get("srs_task"):
            rows.append([tp.get("week"), loc(tp, "srs_task", lang, data), tp.get("srs", ""),
                         loc(tp, "srs_form", lang, data) or DASH, tp.get("srs_due") or tp.get("week")])
    if rows:
        table(doc, [t("week", lang), t("task", lang), t("hours", lang), t("report_form", lang), t("due", lang)],
              rows, widths_cm=[1.8, 7.3, 1.7, 3.2, 2.5])
    else:
        para(doc, DASH)


def sec_assessment(doc, data: dict, lang: str) -> None:
    rows, tot = [], 0.0
    n_weeks = int(data.get("weeks", 15) or 15)
    for r in assessment_plan(data):
        a = r["item"]
        if r["session"]:
            when = t("session", lang)
        elif len(r["weeks"]) == n_weeks and not (a.get("weeks") or a.get("week")):
            when = t("whole_semester", lang)
        else:
            when = ", ".join(str(w) for w in r["weeks"])
        rows.append([loc(a, "name", lang, data), tv(r["type"], lang), loc(a, "form", lang, data) or DASH, when,
                     a.get("weight")])
        tot += float(a.get("weight", 0) or 0)
    rows.append([t("total", lang), "", "", "", int(tot) if tot == int(tot) else tot])
    table(doc, [t("control_kind", lang), t("q_type", lang), t("control_form", lang), t("topics_weeks", lang),
                t("max_points", lang)], rows, widths_cm=[5.0, 2.6, 4.4, 2.5, 2.0])
    para(doc, t("assess_note", lang))
    label(doc, t("sec_scale", lang))
    table(doc, [t("score_range", lang), t("letter", lang), t("traditional", lang)],
          [[f'{r["min"]}–{r["max"]}', r.get("letter", ""), scale_grade(r, lang)] for r in grading_scale(data)],
          widths_cm=[4, 4, 8.5])


def sec_policy(doc, data: dict, lang: str) -> None:
    pol = data.get("policies") or {}
    for k in ("attendance", "late_work", "academic_integrity", "ai_use"):
        text = loc(pol, k, lang, data)
        p = para(doc)
        p.add_run(f'{t("p_" + k, lang)}. ').bold = True
        p.add_run(str(text) if text else DASH)
    for extra in loc(pol, "extra", lang, data) or []:
        para(doc, f"– {extra}")


def sec_literature(doc, data: dict, lang: str, final: bool) -> None:
    num = 0
    for cat, key in (("main", "main_lit"), ("extra", "extra_lit"), ("online", "online_lit")):
        items = lit_items(data, cat, lang, final)
        if not items:
            continue
        label(doc, t(key, lang))
        for text in items:
            num += 1
            para(doc, f"{num}. {text}")
    if not num:
        para(doc, DASH)


def sec_signatures(doc, data: dict, lang: str) -> None:
    tch = data.get("teacher") or {}
    start = len(doc.paragraphs)
    who = ", ".join(x for x in (tch.get("position"), tch.get("degree")) if x)
    para(doc, f'{t("compiler", lang)}: {who} ____________ {tch.get("name") or "____________"}', indent=False)
    para(doc)
    dept = (data.get("_profile") or {}).get("department")
    para(doc, f'{t("dept_meeting", lang)}{" «" + dept + "»" if dept else ""}', indent=False)
    para(doc, t("protocol", lang), indent=False)
    para(doc)
    para(doc, f'{t("approve_role", lang)} ____________ ____________', indent=False)
    for p in doc.paragraphs[start:-1]:
        p.paragraph_format.keep_with_next = True


# ---------- запуск ----------

def load_checked(course_yaml: str, what: str) -> tuple[dict, list[str]]:
    """Паспорт + проверка; при ошибках печатает их и выходит с кодом 1."""
    try:
        data = load_course(course_yaml)
    except DataError as e:
        fail(str(e))
    errors, warnings = validate_course(data)
    if errors:
        report(errors, warnings)
        fail(f"{what} не собран(а) — исправьте ошибки в course.yaml")
    return data, warnings


def save(doc_or_wb, path: Path) -> None:
    try:
        doc_or_wb.save(path)
    except PermissionError:
        fail(f"не удалось записать {path} — закройте файл в Word/Excel и запустите снова")


def translation_warning(data: dict, lang: str, warnings: list[str]) -> None:
    missing = sorted(data.get("_missing_tr", set()))
    if missing:
        warnings.append(f"нет перевода на {lang} для полей: {', '.join(missing)} — взят текст паспорта "
                        f"(добавьте поля <имя>_{lang} в course.yaml)")
