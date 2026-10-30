"""Проверка паспорта курса (course.yaml) по схеме и нормам КР.

    errors, warnings = validate_course(data)

errors — сборку документов останавливают; warnings — показываются преподавателю.
Схема — references/course-schema.md. Здесь же: глаголы Блума, график
контроля по неделям, шкала оценок.
"""
from __future__ import annotations

import re

from common import CREDIT_HOURS, HOUR_KINDS, check_hours

LANGS = ("ru", "ky", "en")
BLOOM_LEVELS = ("remember", "understand", "apply", "analyze", "evaluate", "create")
ASSESS_TYPES = ("current", "midterm", "final")
ENUMS = {
    "type": ("обязательная", "по выбору"),
    "cycle": ("гуманитарный", "естественнонаучный", "профессиональный"),
    "level": ("бакалавриат", "магистратура", "специалитет", "аспирантура"),
    "form": ("очная", "заочная", "дистанционная"),
}

# Шкала по умолчанию (типовая для вузов КР; вуз может задать свою в grading_scale).
KR_DEFAULT_SCALE = [
    {"min": 87, "max": 100, "letter": "A", "grade": {"ru": "отлично", "ky": "эң жакшы", "en": "excellent"}},
    {"min": 80, "max": 86, "letter": "B", "grade": {"ru": "хорошо", "ky": "жакшы", "en": "good"}},
    {"min": 74, "max": 79, "letter": "C", "grade": {"ru": "хорошо", "ky": "жакшы", "en": "good"}},
    {"min": 68, "max": 73, "letter": "D", "grade": {"ru": "удовлетворительно", "ky": "канааттандырарлык",
                                                     "en": "satisfactory"}},
    {"min": 61, "max": 67, "letter": "E", "grade": {"ru": "удовлетворительно", "ky": "канааттандырарлык",
                                                     "en": "satisfactory"}},
    {"min": 0, "max": 60, "letter": "F", "grade": {"ru": "неудовлетворительно", "ky": "канааттандырарлык эмес",
                                                    "en": "fail"}},
]

# ---------- глаголы Блума ----------
# Основы глаголов (начало слова). Списки пересекаются — это нормально:
# «сравнивает» бывает и пониманием, и анализом.
BLOOM_STEMS = {
    "ru": {
        "remember": ["назыв", "назов", "назва", "перечисл", "воспроизв", "распозна", "вспомин", "вспомн",
                     "указыв", "укаж", "запомин", "определя", "формулир", "обознач"],
        "understand": ["объясн", "опис", "интерпрет", "классифиц", "обобщ", "пересказ", "иллюстрир", "привод",
                       "характериз", "излаг", "излож", "раскры", "толку", "сравн", "различ", "поясн", "обсужд",
                       "демонстрир", "трактует"],
        "apply": ["примен", "использ", "выполн", "реш", "вычисл", "рассчит", "пиш", "пис", "напис", "реализ",
                  "демонстрир", "стро", "постро", "оформл", "провод", "осуществл", "настр", "программир",
                  "внедр", "управл", "состав", "иллюстрир", "моделир"],
        "analyze": ["анализ", "проанализ", "сравн", "сопостав", "различ", "дифференц", "выявл", "выяв",
                    "исследу", "исслед", "классифиц", "структурир", "декомпоз", "тестир", "отлаж", "диагност",
                    "устанавл", "интерпрет"],
        "evaluate": ["оцен", "крити", "обосн", "аргумент", "провер", "выбир", "выбер", "защищ", "рецензир",
                     "ранжир", "экспертир", "прогнозир", "верифиц", "оптимиз", "контролир", "сопостав"],
        "create": ["созда", "разраб", "проектир", "спроектир", "конструир", "сконструир", "планир", "сплан",
                   "синтез", "формулир", "составл", "состав", "предлаг", "предлож", "генерир", "моделир",
                   "сочин", "организ", "комбинир", "стро", "постро"],
    },
    "en": {
        "remember": ["defin", "list", "recall", "name", "identif", "state", "recogni", "label", "reproduc"],
        "understand": ["explain", "describ", "summari", "classif", "interpret", "discuss", "illustrat",
                       "paraphras", "compar", "outlin", "exemplif", "infer"],
        "apply": ["appl", "use", "using", "implement", "writ", "solv", "calculat", "comput", "demonstrat",
                  "execut", "construct", "perform", "configur", "operat", "carr", "conduct", "model"],
        "analyze": ["analy", "compar", "contrast", "differentiat", "distinguish", "examin", "investigat",
                    "test", "debug", "organi", "deconstruct", "diagnos", "categori"],
        "evaluate": ["evaluat", "assess", "justif", "critiqu", "critici", "judg", "select", "choos", "defend",
                     "argu", "recommend", "validat", "verif", "prioriti", "optimi"],
        "create": ["design", "creat", "develop", "formulat", "plan", "build", "compos", "propos", "construct",
                   "produc", "generat", "model", "synthes", "devis", "invent", "author"],
    },
    # В кыргызском глагол обычно в конце: «…моделди түшүндүрөт».
    "ky": {
        "remember": ["ата", "санап", "санай", "аныкта", "эсте", "тааны", "айтып"],
        "understand": ["түшүндүр", "сүрөттө", "келтир", "классификацияла", "жалпыла", "чечмеле", "баянда",
                       "баяндай", "салыштыр"],
        "apply": ["колдон", "пайдалан", "аткар", "чеч", "эсепте", "жаз", "ашыр", "көрсөт", "кур", "орнот"],
        "analyze": ["талда", "салыштыр", "ажырат", "изилде", "айырмала", "текшер", "аныкта"],
        "evaluate": ["баала", "негизде", "текшер", "танда", "сына", "далилде"],
        "create": ["түз", "чыга", "чыгар", "долбоорло", "пландаштыр", "жарат", "сунуш", "моделде", "кур"],
    },
}
# Неизмеримые глаголы — РО с ними не проверить.
NON_MEASURABLE = {
    "ru": ("знает", "знать", "знают", "понимает", "понимать", "понимают", "владеет", "владеть", "владеют",
           "имеет", "иметь", "ознакомлен", "ознакомится", "знаком", "осознаёт", "осознает", "изучает", "изучит",
           "узнает", "узнаёт", "представляет"),
    "en": ("know", "knows", "understand", "understands", "learn", "learns", "appreciate", "appreciates",
           "familiar", "aware"),
    "ky": ("билет", "билүү", "түшүнөт", "түшүнүү", "тааныш", "үйрөнөт", "биле"),
}
FILLERS = {
    "ru": {"студент", "студенты", "обучающийся", "обучающиеся", "будет", "будут", "умеет", "уметь", "умеют",
           "может", "могут", "способен", "способна", "способны", "сможет", "смогут", "должен", "самостоятельно",
           "грамотно", "корректно", "успешно", "уверенно", "-"},
    "en": {"students", "student", "will", "be", "able", "to", "can", "the", "learner", "learners", "-"},
    "ky": {"студент", "студенттер", "-"},
}


def _words(text: str) -> list[str]:
    return [w for w in re.split(r"[\s,.;:!?()«»\"]+", str(text).lower()) if w]


def bloom_verb(text: str, lang: str) -> tuple[str, set[str] | None]:
    """Глагол РО и уровни Блума, к которым он относится.

    Возвращает (слово, уровни); уровни None — глагол неизмеримый («знает»),
    пустое множество — глагол не узнан.
    """
    words = _words(text)
    lang = lang if lang in BLOOM_STEMS else "ru"
    if lang == "ky":
        cand = [w for w in reversed(words) if w not in FILLERS["ky"]][:1]
        # «…жөндөмдүү/мүмкүн» в конце — смотрим предыдущее слово
        if cand and cand[0] in ("жөндөмдүү", "мүмкүн", "алат"):
            cand = [w for w in reversed(words) if w not in FILLERS["ky"]][1:2]
    else:
        cand = [w for w in words if w not in FILLERS[lang]][:1]
    if not cand:
        return "", set()
    w = cand[0]
    if w in NON_MEASURABLE[lang] or any(w.startswith(nm) for nm in NON_MEASURABLE[lang] if len(nm) > 5):
        return w, None
    levels = {lvl for lvl, stems in BLOOM_STEMS[lang].items() if any(w.startswith(s) for s in stems)}
    return w, levels


# ---------- оценивание ----------

def grading_scale(data: dict) -> list[dict]:
    gs = data.get("grading_scale", "kr_default")
    if gs in (None, "", "kr_default"):
        return KR_DEFAULT_SCALE
    return gs


def scale_grade(row: dict, lang: str) -> str:
    g = row.get("grade", "")
    if isinstance(g, dict):
        return g.get(lang) or g.get("ru", "")
    return str(g)


def assessment_plan(data: dict) -> list[dict]:
    """Каждый вид контроля с баллами по неделям.

    Возвращает [{item, type, weeks: {неделя: баллы}, session: баллы}].
    week / weeks из паспорта; нет недель: final → сессия, иначе поровну на весь семестр.
    """
    n = int(data.get("weeks", 15) or 15)
    plan = []
    for a in data.get("assessment", []) or []:
        w = float(a.get("weight", 0) or 0)
        typ = a.get("type") or ("final" if "экзамен" in str(a.get("name", "")).lower() else "current")
        weeks = a.get("weeks") or ([a["week"]] if a.get("week") else [])
        row = {"item": a, "type": typ, "weeks": {}, "session": 0.0}
        if weeks:
            share = round(w / len(weeks), 2)
            for i, wk in enumerate(weeks):
                row["weeks"][int(wk)] = share if i < len(weeks) - 1 else round(w - share * (len(weeks) - 1), 2)
        elif typ == "final":
            row["session"] = w
        else:
            share = round(w / n, 2)
            for wk in range(1, n + 1):
                row["weeks"][wk] = share if wk < n else round(w - share * (n - 1), 2)
        plan.append(row)
    return plan


# ---------- проверка паспорта ----------

def _is_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def validate_course(data: dict) -> tuple[list[str], list[str]]:
    err: list[str] = []
    warn: list[str] = []
    lang = data.get("language", "ru")
    if lang not in LANGS:
        err.append(f"language: «{lang}» — допустимо ru, ky или en")
        lang = "ru"
    for extra in data.get("languages_extra", []) or []:
        if extra not in LANGS:
            err.append(f"languages_extra: «{extra}» — допустимо ru, ky или en")
    if data.get("schema") not in (None, 1):
        warn.append(f"schema: {data.get('schema')} — скрипт знает только версию 1")

    c = data.get("course") or {}
    if not c.get("title"):
        err.append("course.title: не указано название дисциплины")
    if not c.get("code"):
        warn.append("course.code: нет кода дисциплины (возьмите из учебного плана)")
    for k, allowed in ENUMS.items():
        v = c.get(k)
        if v and v not in allowed:
            warn.append(f"course.{k}: «{v}» — ожидается одно из: {', '.join(allowed)}")
    for k in ("year", "semester"):
        if c.get(k) is not None and not _is_int(c.get(k)):
            err.append(f"course.{k}: должно быть целым числом")

    credits = data.get("credits")
    if not _is_int(credits) or credits <= 0:
        err.append("credits: нужно целое число кредитов больше нуля")
    hours = data.get("hours")
    if not isinstance(hours, dict) or not hours:
        err.append("hours: нет распределения часов по видам занятий")
        hours = {}
    for k, v in hours.items():
        if k not in HOUR_KINDS:
            err.append(f"hours.{k}: неизвестный вид, допустимо {', '.join(HOUR_KINDS)}")
        elif not _is_int(v) or v < 0:
            err.append(f"hours.{k}: нужно целое число часов ≥ 0")
    weeks = data.get("weeks")
    if not _is_int(weeks) or not 1 <= weeks <= 20:
        err.append("weeks: число недель от 1 до 20")
        weeks = 15

    # результаты обучения
    outcomes = data.get("outcomes") or []
    ids: set[str] = set()
    if not outcomes:
        err.append("outcomes: нет результатов обучения")
    elif not 3 <= len(outcomes) <= 8:
        warn.append(f"outcomes: {len(outcomes)} РО — обычно формулируют 3–7")
    for i, o in enumerate(outcomes, 1):
        oid = str(o.get("id") or "")
        where = f"outcomes[{oid or i}]"
        if not oid:
            err.append(f"{where}: нет id (РО1, РО2…)")
        elif oid in ids:
            err.append(f"{where}: id повторяется")
        ids.add(oid)
        if o.get("bloom") not in BLOOM_LEVELS:
            err.append(f"{where}.bloom: «{o.get('bloom')}» — допустимо {', '.join(BLOOM_LEVELS)}")
        for lg in LANGS:
            key = "text" if lg == lang else f"text_{lg}"
            text = o.get(key)
            if not text:
                if key == "text":
                    err.append(f"{where}: нет формулировки (text)")
                continue
            word, levels = bloom_verb(text, lg)
            if levels is None:
                err.append(f"{where}.{key}: «{word}» — неизмеримый глагол; начните с глагола Блума "
                           f"(объясняет, применяет, анализирует, оценивает, проектирует…)")
            elif not levels:
                warn.append(f"{where}.{key}: глагол «{word}» не узнан как глагол Блума — проверьте формулировку")
            elif o.get("bloom") in BLOOM_LEVELS and o["bloom"] not in levels:
                warn.append(f"{where}.{key}: глагол «{word}» обычно уровня {', '.join(sorted(levels))}, "
                            f"а указан {o['bloom']}")

    # темы
    topics = data.get("topics") or []
    if not topics:
        err.append("topics: нет тематического плана по неделям")
    seen_weeks: set[int] = set()
    covered: set[str] = set()
    no_srs_task = []
    for i, tp in enumerate(topics, 1):
        wk = tp.get("week")
        where = f"topics[неделя {wk}]" if wk else f"topics[{i}]"
        if not _is_int(wk) or not 1 <= wk <= weeks:
            err.append(f"{where}: week должна быть от 1 до {weeks}")
        elif wk in seen_weeks:
            err.append(f"{where}: неделя повторяется")
        else:
            seen_weeks.add(wk)
        if not tp.get("title"):
            err.append(f"{where}: нет названия темы")
        for k in HOUR_KINDS:
            v = tp.get(k)
            if v is not None and (not _is_int(v) or v < 0):
                err.append(f"{where}.{k}: нужно целое число часов ≥ 0")
        tos = tp.get("outcomes") or []
        if not tos:
            warn.append(f"{where}: тема не привязана ни к одному РО")
        for ref in tos:
            if str(ref) not in ids:
                err.append(f"{where}: РО «{ref}» нет в outcomes")
            covered.add(str(ref))
        if int(tp.get("srs", 0) or 0) > 0 and not tp.get("srs_task"):
            no_srs_task.append(str(wk))
        due = tp.get("srs_due")
        if due is not None and (not _is_int(due) or not 1 <= due <= weeks):
            err.append(f"{where}.srs_due: неделя сдачи от 1 до {weeks}")
    if topics and len(seen_weeks) < weeks:
        missing = sorted(set(range(1, weeks + 1)) - seen_weeks)
        warn.append(f"topics: нет тем на неделях {', '.join(map(str, missing))}")
    for oid in sorted(ids - covered):
        warn.append(f"outcomes[{oid}]: ни одна тема не закрывает этот РО")
    if no_srs_task:
        warn.append(f"topics: есть часы СРС без задания (srs_task) на неделях {', '.join(no_srs_task)}")

    # часы и веса (общая сверка из common)
    err.extend(check_hours(data))
    if _is_int(credits) and hours:
        aud = sum(int(hours.get(k, 0) or 0) for k in ("lectures", "practicals", "labs"))
        if credits * CREDIT_HOURS and aud > credits * CREDIT_HOURS * 0.7:
            warn.append(f"hours: аудиторных {aud} ч — больше 70% объёма, проверьте по учебному плану")

    # оценивание
    assessment = data.get("assessment") or []
    if not assessment:
        err.append("assessment: нет видов контроля (балльно-рейтинговая система, сумма 100)")
    for a in assessment:
        where = f"assessment[{a.get('name', '?')}]"
        if not a.get("name"):
            err.append(f"{where}: нет названия")
        if not isinstance(a.get("weight"), (int, float)) or a.get("weight", 0) <= 0:
            err.append(f"{where}: weight — баллы больше нуля")
        if a.get("type") and a["type"] not in ASSESS_TYPES:
            err.append(f"{where}.type: «{a['type']}» — допустимо {', '.join(ASSESS_TYPES)}")
        wl = a.get("weeks") or ([a["week"]] if a.get("week") is not None else [])
        for wk in wl:
            if not _is_int(wk) or not 1 <= wk <= weeks:
                err.append(f"{where}: неделя {wk} вне 1–{weeks}")
    if assessment and not any((a.get("type") == "final") or "экзамен" in str(a.get("name", "")).lower()
                              for a in assessment):
        warn.append("assessment: нет итогового контроля (type: final)")

    gs = data.get("grading_scale", "kr_default")
    if gs not in (None, "", "kr_default"):
        if not isinstance(gs, list) or not gs:
            err.append("grading_scale: kr_default или список {min, max, letter, grade}")
        else:
            pts = set()
            for row in gs:
                if not _is_int(row.get("min")) or not _is_int(row.get("max")) or row["min"] > row["max"]:
                    err.append(f"grading_scale: строка {row} — нужны целые min ≤ max")
                    continue
                pts.update(range(row["min"], row["max"] + 1))
            if pts and pts != set(range(0, 101)):
                err.append("grading_scale: диапазоны должны покрывать 0–100 без пропусков")

    for n in data.get("sdg", []) or []:
        if not _is_int(n) or not 1 <= n <= 17:
            err.append(f"sdg: «{n}» — номер ЦУР от 1 до 17")
    if not data.get("sdg"):
        warn.append("sdg: не указаны ЦУР ООН (для силлабуса желательно 1–3 цели)")
    if not data.get("methods"):
        warn.append("methods: не указаны методы обучения")

    if not data.get("description"):
        warn.append("description: нет описания дисциплины")
    if not data.get("goals"):
        warn.append("goals: нет целей дисциплины")
    pol = data.get("policies") or {}
    for k in ("attendance", "late_work", "academic_integrity", "ai_use"):
        if not pol.get(k):
            warn.append(f"policies.{k}: не заполнено")
    teacher = data.get("teacher") or {}
    if not teacher.get("name"):
        warn.append("teacher.name: нет ФИО преподавателя (course.yaml или profile.yaml)")

    lit = data.get("literature") or {}
    if not (lit.get("main") or []):
        warn.append("literature.main: нет основной литературы")
    for cat in ("main", "extra", "online"):
        for item in lit.get(cat, []) or []:
            text = item.get("text") if isinstance(item, dict) else item
            if not text:
                err.append(f"literature.{cat}: пустая запись")
            elif not (isinstance(item, dict) and item.get("verified") is True):
                warn.append(f"literature.{cat}: [НЕ ПРОВЕРЕНО] {str(text)[:70]}")
    return err, warn


def report(errors: list[str], warnings: list[str]) -> None:
    """Печать итогов проверки списком."""
    if errors:
        print(f"Ошибки ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        print(f"Предупреждения ({len(warnings)}):")
        for w in warnings:
            print(f"  ! {w}")
    if not errors and not warnings:
        print("Паспорт курса в порядке.")
