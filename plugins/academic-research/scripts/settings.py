# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Настройки вуза: university/settings.yaml поверх норм КР по умолчанию.

    s = load_settings(<папка курса или работы>)        # из скриптов
    uv run settings.py [папка] [--diff]                 # показать действующие настройки

Порядок важности: course.yaml / work.yaml > university/settings.yaml >
university/brand.yaml (старый формат) > DEFAULTS (нормы КР).
Пустые значения ("", пустой {ru, ky, en}) в settings.yaml значат «по умолчанию».

Один и тот же файл лежит в academic-core/scripts и academic-research/scripts —
правьте оба (тест сверяет копии). Справочник ключей —
academic-core/references/university-settings.md, образец —
academic-core/templates/settings.example.yaml.
"""
from __future__ import annotations

import copy
import re
import sys
from pathlib import Path

import yaml

LANGS = ("ru", "ky", "en")
PAGE_NUMBERS = ("bottom-center", "bottom-right", "top-center", "top-right", "none")
HIDEABLE = ("sdg", "methods", "srs", "calendar", "policies", "literature")
POLICY_KEYS = ("attendance", "late_work", "academic_integrity", "ai_use")
TEST_FORMATS = ("docx", "xlsx", "gift", "moodle_xml")
STYLES = ("gost", "apa", "ieee")
BIB_ORDERS = ("auto", "alpha", "cite")
ASSESS_TYPES = ("current", "midterm", "final")
OS_NAMES = ("windows", "macos", "linux")


def _g(ru: str, ky: str, en: str) -> dict:
    return {"ru": ru, "ky": ky, "en": en}


KR_SCALE = [
    {"min": 87, "max": 100, "letter": "A", "grade": _g("отлично", "эң жакшы", "excellent")},
    {"min": 80, "max": 86, "letter": "B", "grade": _g("хорошо", "жакшы", "good")},
    {"min": 74, "max": 79, "letter": "C", "grade": _g("хорошо", "жакшы", "good")},
    {"min": 68, "max": 73, "letter": "D", "grade": _g("удовлетворительно", "канааттандырарлык", "satisfactory")},
    {"min": 61, "max": 67, "letter": "E", "grade": _g("удовлетворительно", "канааттандырарлык", "satisfactory")},
    {"min": 0, "max": 60, "letter": "F", "grade": _g("неудовлетворительно", "канааттандырарлык эмес", "fail")},
]

# Нормы КР по умолчанию — те же значения, что в settings.example.yaml.
DEFAULTS: dict = {
    "university": {
        "name": "", "name_ky": "", "name_en": "", "short": "", "city": "", "type": "state",
        "ministry": _g("", "", ""),
    },
    "brand": {"logo": "logo.png", "color": "#1F4E79"},
    "document": {
        "font": "Times New Roman", "size": 14, "table_size": 12, "line_spacing": 1.5, "indent_cm": 1.25,
        "margins_mm": {"left": 30, "right": 15, "top": 20, "bottom": 20},
        "page_numbers": "bottom-center", "title_page_logo": False,
    },
    "approval": {
        "enabled": True,
        "role": _g("Заведующий кафедрой", "Кафедра башчысы", "Head of Department"),
        "name": "", "agreed": [], "protocol": True,
    },
    "grading": {
        "credit_hours": 30,
        "scale": KR_SCALE,
        "assessment_template": [
            {"name": "Текущий контроль", "weight": 30, "type": "current"},
            {"name": "Рубежный контроль 1", "weight": 15, "type": "midterm", "week": 8},
            {"name": "Рубежный контроль 2", "weight": 15, "type": "midterm", "week": 15},
            {"name": "Итоговый экзамен", "weight": 40, "type": "final"},
        ],
    },
    "syllabus": {
        "hide_sections": [],
        "policies": {k: "" for k in POLICY_KEYS},
        "extra_sections": [],
    },
    "tests": {
        "formats": list(TEST_FORMATS), "variants": 2, "questions_per_variant": 0,
        "moodle": True, "moodle_version": "",
    },
    "research": {
        "citation_style": "gost", "bib_order": "auto",
        "thesis_pages": {"bachelor": [40, 60], "master": [60, 90]},
        "plagiarism_min": 75,
    },
    "manual": {
        "paper": "a5",
        "approval_body": _g("Учёный совет", "Илимий кеңеш", "Academic Council"),
    },
    "environment": {"os": ["windows", "macos"], "languages": ["ru", "ky"]},
}

# Ключи со свободным набором подключей (уровни ВКР).
FREE_KEYS = {"research.thesis_pages"}


class DataError(Exception):
    """Ошибка в данных пользователя — печатается по-русски, без трейсбека."""


def read_yaml(path: Path):
    try:
        return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise DataError(f"не найден файл {path}")
    except yaml.YAMLError as e:
        raise DataError(f"в {Path(path).name} ошибка разметки YAML: {e}")


def find_up(start: Path, name: str) -> Path | None:
    """Ищет файл или папку name в start и выше по дереву (рабочая папка)."""
    for d in [start, *start.parents]:
        if (d / name).exists():
            return d / name
    return None


# ---------- слияние ----------

def is_lang_dict(v) -> bool:
    return isinstance(v, dict) and bool(v) and set(v) <= set(LANGS)


def _empty(v) -> bool:
    if v is None or (isinstance(v, str) and not v.strip()):
        return True
    return is_lang_dict(v) and all(_empty(x) for x in v.values())


def merge(base: dict, over: dict) -> dict:
    """over поверх base: словари — вглубь, списки и {ru, ky, en} — целиком, пустое пропускается."""
    for k, v in over.items():
        if _empty(v):
            continue
        if isinstance(v, dict) and isinstance(base.get(k), dict) and not is_lang_dict(v):
            merge(base[k], v)
        else:
            base[k] = copy.deepcopy(v)
    return base


def get_key(d, path: str):
    for part in path.split("."):
        if not isinstance(d, dict):
            return None
        d = d.get(part)
    return d


def _set(d: dict, path: str, value) -> None:
    *head, last = path.split(".")
    for part in head:
        d = d.setdefault(part, {})
    d[last] = value


# ---------- чтение ----------

def load_settings(start: str | Path | None = None, *, strict: bool = True) -> dict:
    """Действующие настройки вуза для папки start (курс, работа или файл в них).

    Служебные ключи: _dir (папка university/ или None), _file (settings.yaml или None),
    _brand_file, _errors, _warnings. strict — при ошибках поднимает DataError.
    """
    s = copy.deepcopy(DEFAULTS)
    errors: list[str] = []
    warnings: list[str] = []
    uni = None
    if start is not None:
        p = Path(start).expanduser().resolve()
        uni = find_up(p if p.is_dir() else p.parent, "university")
        if uni is not None and not uni.is_dir():
            uni = None
    file = uni / "settings.yaml" if uni and (uni / "settings.yaml").exists() else None
    brand_file = uni / "brand.yaml" if uni and (uni / "brand.yaml").exists() else None

    brand = read_yaml(brand_file) if brand_file else {}
    if brand_file and not isinstance(brand, dict):
        errors.append("brand.yaml: ожидаются поля name, name_ky, name_en, logo, color")
        brand = {}
    brand = brand or {}
    merge(s, {"university": {k: brand.get(k) for k in ("name", "name_ky", "name_en")},
              "brand": {k: brand.get(k) for k in ("logo", "color")}})
    if file is None and brand.get("logo"):
        s["document"]["title_page_logo"] = True  # старый brand.yaml: логотип всегда был на титуле

    raw = read_yaml(file) if file else None
    if raw is not None and not isinstance(raw, dict):
        errors.append("settings.yaml: ожидаются разделы university:, document:, grading: … — см. образец")
        raw = None
    if raw:
        raw = _known(raw, DEFAULTS, "", warnings)
        for name in raw:
            if name in DEFAULTS and raw[name] is not None and not isinstance(raw[name], dict):
                errors.append(f"{name}: ожидается раздел с ключами ({', '.join(DEFAULTS[name])})")
        merge(s, {k: v for k, v in raw.items() if k in DEFAULTS and isinstance(v, dict)})
    if not s["grading"].get("scale"):
        s["grading"]["scale"] = copy.deepcopy(KR_SCALE)

    _validate(s, errors, warnings)
    logo = s["brand"].get("logo")
    logo_set = bool(brand.get("logo") or get_key(raw or {}, "brand.logo"))
    if logo_set and uni and isinstance(logo, str) and not (uni / logo).is_file():
        warnings.append(f"brand.logo: файла {logo} нет в папке university/ — логотип не ставится")

    s.update(_dir=uni, _file=file, _brand_file=brand_file, _errors=errors, _warnings=warnings)
    if errors and strict:
        where = file.name if file else "brand.yaml"
        raise DataError(f"в настройках вуза ({where}) ошибки — исправьте или запустите "
                        f"/academic-core:university:\n" + "\n".join(f"  ✗ {e}" for e in errors))
    return s


def _known(raw: dict, ref: dict, prefix: str, warnings: list[str]) -> dict:
    """raw без неизвестных ключей; о каждом пропущенном — предупреждение."""
    out = {}
    for k, v in raw.items():
        path = f"{prefix}{k}"
        if k not in ref:
            warnings.append(f"{path}: неизвестный ключ — пропущен (проверьте написание по образцу)")
            continue
        if isinstance(v, dict) and isinstance(ref[k], dict) and path not in FREE_KEYS:
            if is_lang_dict(ref[k]):
                for lk in v:
                    if lk not in LANGS:
                        warnings.append(f"{path}.{lk}: язык не ru, ky или en — пропущен")
                v = {lk: x for lk, x in v.items() if lk in LANGS}
            else:
                v = _known(v, ref[k], path + ".", warnings)
        out[k] = v
    return out


# ---------- проверка ----------

def _num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _text(v) -> bool:
    """Строка или {ru, ky, en} со строками."""
    return isinstance(v, str) or (isinstance(v, dict) and set(v) <= set(LANGS)
                                  and all(isinstance(x, str) or x is None for x in v.values()))


def _ranges(points: list[int]) -> str:
    out, start = [], None
    for i, p in enumerate(points):
        if start is None:
            start = p
        if i == len(points) - 1 or points[i + 1] != p + 1:
            out.append(f"{start}–{p}" if p != start else str(p))
            start = None
    return ", ".join(out)


def _validate(s: dict, err: list[str], warn: list[str]) -> None:
    for name, dflt in DEFAULTS.items():
        if not isinstance(s.get(name), dict):
            s[name] = copy.deepcopy(dflt)

    def check(path: str, ok, msg: str) -> bool:
        """ok — функция от значения; неверное значение сбрасывается на норму КР."""
        v = get_key(s, path)
        try:
            good = bool(ok(v))
        except (TypeError, ValueError, AttributeError):
            good = False
        if not good:
            shown = f"«{v}» — " if isinstance(v, (str, int, float)) and not isinstance(v, bool) else ""
            err.append(f"{path}: {shown}{msg}")
            _set(s, path, copy.deepcopy(get_key(DEFAULTS, path)))
        return good

    # вуз
    for k in ("name", "name_ky", "name_en", "short", "city"):
        check(f"university.{k}", lambda v: isinstance(v, str), "нужен текст")
    check("university.type", lambda v: v in ("state", "private"), "допустимо state (государственный) или private (частный)")
    check("university.ministry", _text, "текст или {ru: …, ky: …, en: …}")
    # стиль
    check("brand.logo", lambda v: isinstance(v, str), "имя файла логотипа в папке university/")
    s["brand"]["color"] = str(s["brand"].get("color") or "").strip()
    check("brand.color", lambda v: re.fullmatch(r"#[0-9A-Fa-f]{6}", v), "цвет в виде #RRGGBB, например #1F4E79")
    # документы
    d = "document"
    check(f"{d}.font", lambda v: isinstance(v, str) and v.strip(), "название шрифта, например Times New Roman")
    check(f"{d}.size", lambda v: _num(v) and 8 <= v <= 28, "кегль от 8 до 28")
    check(f"{d}.table_size", lambda v: _num(v) and 6 <= v <= 28, "кегль таблиц от 6 до 28")
    check(f"{d}.line_spacing", lambda v: _num(v) and 0.8 <= v <= 3, "межстрочный интервал от 0,8 до 3")
    check(f"{d}.indent_cm", lambda v: _num(v) and 0 <= v <= 5, "абзацный отступ от 0 до 5 см")
    if check(f"{d}.margins_mm", lambda v: isinstance(v, dict), "поля {left, right, top, bottom} в мм"):
        for side in ("left", "right", "top", "bottom"):
            check(f"{d}.margins_mm.{side}", lambda v: _num(v) and 0 < v <= 100, "поле в мм больше 0 и до 100")
    check(f"{d}.page_numbers", lambda v: v in PAGE_NUMBERS, "допустимо: " + ", ".join(PAGE_NUMBERS))
    check(f"{d}.title_page_logo", lambda v: isinstance(v, bool), "true или false")
    # утверждение
    a = "approval"
    check(f"{a}.enabled", lambda v: isinstance(v, bool), "true или false")
    check(f"{a}.role", _text, "должность: текст или {ru: …, ky: …, en: …}")
    check(f"{a}.name", lambda v: isinstance(v, str), "текст «И.И. Иванов» или пусто")
    check(f"{a}.agreed", lambda v: isinstance(v, list) and all(
        isinstance(x, dict) and _text(x.get("role")) and not _empty(x.get("role"))
        and isinstance(x.get("name", ""), str) for x in v),
        "список [{role: {ru: …}, name: …}] — у каждого нужна должность")
    check(f"{a}.protocol", lambda v: isinstance(v, bool), "true или false")
    # оценивание
    g = "grading"
    check(f"{g}.credit_hours", lambda v: _int(v) and 1 <= v <= 60, "целое число часов в кредите (обычно 30)")
    if check(f"{g}.scale", lambda v: isinstance(v, list) and all(
            isinstance(r, dict) and _int(r.get("min")) and _int(r.get("max")) and r["min"] <= r["max"]
            and _text(r.get("grade", "")) for r in v),
            "список строк {min, max, letter, grade} с целыми min ≤ max"):
        count: dict[int, int] = {}
        for r in s[g]["scale"]:
            for p in range(r["min"], r["max"] + 1):
                count[p] = count.get(p, 0) + 1
        gaps = [p for p in range(0, 101) if p not in count]
        overlaps = sorted(p for p, n in count.items() if n > 1)
        outside = sorted(p for p in count if not 0 <= p <= 100)
        bad = []
        if gaps:
            bad.append(f"нет оценки для баллов {_ranges(gaps)}")
        if overlaps:
            bad.append(f"баллы {_ranges(overlaps)} попадают в две строки")
        if outside:
            bad.append(f"баллы {_ranges(outside)} вне 0–100")
        if bad:
            err.append(f"{g}.scale: шкала должна покрывать 0–100 без пропусков и наложений — {'; '.join(bad)}")
            s[g]["scale"] = copy.deepcopy(KR_SCALE)
        else:
            s[g]["scale"] = sorted(s[g]["scale"], key=lambda r: -r["min"])
    if check(f"{g}.assessment_template", lambda v: isinstance(v, list) and all(
            isinstance(x, dict) and isinstance(x.get("name"), str) and x["name"].strip()
            and _num(x.get("weight")) and x["weight"] > 0 and x.get("type", "current") in ASSESS_TYPES
            and (x.get("week") is None or (_int(x["week"]) and 1 <= x["week"] <= 20)) for x in v),
            "список {name, weight > 0, type: current | midterm | final, week 1–20}"):
        total = sum(x["weight"] for x in s[g]["assessment_template"])
        if s[g]["assessment_template"] and total != 100:
            err.append(f"{g}.assessment_template: баллы дают {total:g}, а нужно 100")
            s[g]["assessment_template"] = copy.deepcopy(DEFAULTS[g]["assessment_template"])
    # силлабус
    y = "syllabus"
    hs = s[y].get("hide_sections")
    bad = [str(x) for x in hs if x not in HIDEABLE] if isinstance(hs, list) else []
    check(f"{y}.hide_sections", lambda v: isinstance(v, list) and not bad,
          (f"«{', '.join(bad)}» — " if bad else "") + "допустимо: " + ", ".join(HIDEABLE))
    if check(f"{y}.policies", lambda v: isinstance(v, dict), "{attendance, late_work, academic_integrity, ai_use}"):
        for k in POLICY_KEYS:
            s[y]["policies"].setdefault(k, "")
            check(f"{y}.policies.{k}", _text, "текст или {ru: …, ky: …, en: …}")
    check(f"{y}.extra_sections", lambda v: isinstance(v, list) and all(
        isinstance(x, dict) and _text(x.get("title")) and not _empty(x.get("title")) and _text(x.get("text", ""))
        for x in v), "список [{title: {ru: …}, text: {ru: …}}] — у каждого раздела нужен заголовок")
    # тесты
    t_ = "tests"
    fs = s[t_].get("formats")
    bad = [str(x) for x in fs if x not in TEST_FORMATS] if isinstance(fs, list) else []
    check(f"{t_}.formats", lambda v: isinstance(v, list) and v and not bad,
          (f"«{', '.join(bad)}» — " if bad else "") + "непустой список из: " + ", ".join(TEST_FORMATS))
    check(f"{t_}.variants", lambda v: _int(v) and 1 <= v <= 30, "целое число вариантов от 1 до 30")
    check(f"{t_}.questions_per_variant", lambda v: _int(v) and v >= 0, "целое число ≥ 0 (0 — все вопросы банка)")
    check(f"{t_}.moodle", lambda v: isinstance(v, bool), "true или false")
    if _num(s[t_].get("moodle_version")):
        s[t_]["moodle_version"] = str(s[t_]["moodle_version"])
    check(f"{t_}.moodle_version", lambda v: isinstance(v, str), "версия текстом, например \"4.1\"")
    # наука
    r = "research"
    check(f"{r}.citation_style", lambda v: v in STYLES, "допустимо gost, apa или ieee")
    check(f"{r}.bib_order", lambda v: v in BIB_ORDERS, "допустимо auto, alpha (по алфавиту) или cite (по упоминанию)")
    check(f"{r}.thesis_pages", lambda v: isinstance(v, dict) and all(
        isinstance(x, list) and len(x) == 2 and all(_int(n) and n > 0 for n in x) and x[0] <= x[1]
        for x in v.values()), "{bachelor: [от, до], master: [от, до]} — целые страницы, от ≤ до")
    check(f"{r}.plagiarism_min", lambda v: _num(v) and 0 <= v <= 100, "процент оригинальности от 0 до 100")
    # пособие
    if isinstance(s["manual"].get("paper"), str):
        s["manual"]["paper"] = s["manual"]["paper"].strip().lower()
    check("manual.paper", lambda v: v in ("a4", "a5"), "допустимо a4 или a5")
    check("manual.approval_body", _text, "текст или {ru: …, ky: …, en: …}")
    # окружение
    check("environment.os", lambda v: isinstance(v, list) and set(v) <= set(OS_NAMES),
          "список из: " + ", ".join(OS_NAMES))
    check("environment.languages", lambda v: isinstance(v, list) and v and set(v) <= set(LANGS),
          "непустой список из: ru, ky, en")

    # переводы: язык документов есть, а текста на нём нет
    langs = [x for x in s["environment"]["languages"] if x != "ru"]
    u = s["university"]
    for lg in langs:
        if u["name"] and not u.get(f"name_{lg}"):
            warn.append(f"university.name_{lg}: не заполнено — в документах на {lg} будет название на ru")
    for path in ("university.ministry", "approval.role", "manual.approval_body"):
        v = get_key(s, path)
        if isinstance(v, dict) and not _empty(v) and v != get_key(DEFAULTS, path):
            miss = [lg for lg in langs if not v.get(lg)]
            if miss:
                warn.append(f"{path}: нет текста на {', '.join(miss)} — будет взят текст ru")


# ---------- доступ ----------

def lang_text(v, lang: str, default: str = "") -> str:
    """Текст на языке lang из строки или {ru, ky, en}; нет — ru, затем default."""
    if isinstance(v, dict):
        return str(v.get(lang) or v.get("ru") or default)
    return str(v) if v else default


def university_name(s: dict, lang: str) -> str:
    u = s.get("university") or {}
    return u.get({"ru": "name", "ky": "name_ky", "en": "name_en"}.get(lang, "name")) or u.get("name") or ""


def logo_path(s: dict) -> Path | None:
    logo = (s.get("brand") or {}).get("logo")
    uni = s.get("_dir")
    if logo and uni and (Path(uni) / logo).is_file():
        return Path(uni) / logo
    return None


def scale_grade(row: dict, lang: str) -> str:
    return lang_text(row.get("grade", ""), lang)


def public(s: dict) -> dict:
    """Настройки без служебных ключей — для вывода."""
    return {k: v for k, v in s.items() if not k.startswith("_")}


def diff_from_defaults(s: dict) -> list[tuple[str, object]]:
    """Что отличается от норм КР: [(ключ через точку, значение)]."""
    out: list[tuple[str, object]] = []

    def walk(cur, ref, prefix):
        if isinstance(cur, dict) and isinstance(ref, dict) and not is_lang_dict(ref) and prefix not in FREE_KEYS:
            for k in cur:
                walk(cur[k], ref.get(k), f"{prefix}.{k}" if prefix else k)
        elif cur != ref and not (_empty(cur) and _empty(ref)):
            out.append((prefix, cur))

    walk(public(s), DEFAULTS, "")
    return out


def main() -> None:
    import argparse

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Действующие настройки вуза (university/settings.yaml)")
    ap.add_argument("folder", nargs="?", default=".", help="папка курса или работы (по умолчанию текущая)")
    ap.add_argument("--diff", action="store_true", help="только то, что отличается от норм КР")
    args = ap.parse_args()
    try:
        s = load_settings(args.folder, strict=False)
    except DataError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"# файл: {s['_file'] or 'нет university/settings.yaml — действуют нормы КР'}")
    data = dict(diff_from_defaults(s)) if args.diff else public(s)
    print(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100).rstrip() if data else "{}")
    for w in s["_warnings"]:
        print(f"Предупреждение: {w}", file=sys.stderr)
    for e in s["_errors"]:
        print(f"Ошибка: {e}", file=sys.stderr)
    if s["_errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
