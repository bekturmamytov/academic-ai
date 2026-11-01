"""Общий код скриптов academic-research: паспорт работы, профиль, настройки вуза.

Скрипты импортируют его так:
    sys.path.insert(0, str(Path(__file__).parent)); from common import ...
Зависимости (pyyaml и др.) объявляет сам скрипт в PEP 723.
Часть кода скопирована из academic-core/scripts/common.py — пути между плагинами не делим.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

from settings import DataError, lang_text, load_settings
from settings import university_name as settings_university_name

WORK_TYPES = ("referat", "doklad", "tezisy", "statya", "kursovaya", "diplom",
              "magistr", "kandidat", "avtoreferat")
STYLES = ("gost", "apa", "ieee")
SHORT_TYPES = ("statya", "tezisy", "doklad")
DISSERTATIONS = ("magistr", "kandidat")
# Тип работы → ключ объёма в settings.yaml → research.thesis_pages.
THESIS_LEVELS = {"kursovaya": "coursework", "diplom": "bachelor", "magistr": "master", "kandidat": "phd"}

DATA_MARK = "НУЖНЫ ВАШИ ДАННЫЕ"
SOURCE_MARK = "НУЖЕН ИСТОЧНИК"
UNVERIFIED_MARK = "НЕ ПРОВЕРЕНО"


def fail(msg: str) -> None:
    print(f"Ошибка: {msg}", file=sys.stderr)
    sys.exit(1)


def utf8_stdout() -> None:
    """Windows-консоль по умолчанию не utf-8 — кириллица ломается."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def read_yaml(path: Path) -> dict:
    try:
        return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except FileNotFoundError:
        raise DataError(f"не найден файл {path}")
    except yaml.YAMLError as e:
        raise DataError(f"в {Path(path).name} ошибка разметки YAML: {e}")


def write_yaml(path: Path, data) -> None:
    Path(path).write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )


def find_up(start: Path, name: str) -> Path | None:
    """Ищет файл или папку name в start и выше по дереву (рабочая папка)."""
    for d in [start, *start.parents]:
        if (d / name).exists():
            return d / name
    return None


def load_work(work_yaml: str | Path) -> dict:
    """Паспорт работы + профиль + настройки вуза в одном словаре.

    Служебные ключи: _dir (папка работы), _profile, _settings (university/settings.yaml
    поверх норм КР), _brand_dir. Порядок: work.yaml > settings.yaml > profile.yaml.
    """
    path = Path(work_yaml).expanduser().resolve()
    data = read_yaml(path)
    if data.get("type") not in WORK_TYPES:
        raise DataError(f"type = «{data.get('type')}», а нужно одно из: {', '.join(WORK_TYPES)}")
    s = load_settings(path.parent)
    data["_settings"] = s
    style = data.setdefault("citation_style", s["research"]["citation_style"])
    if style not in STYLES:
        raise DataError(f"citation_style = «{style}», а нужно gost, apa или ieee")
    if not data.get("bib_order") and s["research"]["bib_order"] != "auto":
        data["bib_order"] = s["research"]["bib_order"]
    data["_dir"] = path.parent
    prof = find_up(path.parent, "profile.yaml")
    data["_profile"] = read_yaml(prof) if prof else {}
    data["_brand_dir"] = s["_dir"]
    p = data["_profile"]
    if not data.get("authors"):
        data["authors"] = [{k: p.get(k, "") for k in ("name", "degree", "position", "email")}
                           | {"affiliation": s["university"]["name"] or p.get("university", ""),
                              "city": s["university"]["city"] or p.get("city", "")}]
    if not data.get("city"):
        data["city"] = s["university"]["city"]
    for k in ("faculty", "department", "city"):
        if not data.get(k):
            data[k] = p.get(k, "")
    data.setdefault("language", p.get("language") or s["environment"]["languages"][0])
    return data


def university_name(data: dict, lang: str) -> str:
    """Вуз: work.yaml → university, settings.yaml / brand.yaml на языке lang, иначе profile.yaml."""
    if data.get("university"):
        return data["university"]
    name = settings_university_name(data.get("_settings") or load_settings(None), lang)
    return name or data.get("_profile", {}).get("university", "")


def thesis_pages(data: dict) -> tuple[int, int] | None:
    """Объём работы по нормам вуза (страниц от, до) или None, если вуз его не задал."""
    level = THESIS_LEVELS.get(data.get("type", ""))
    rng = (data.get("_settings") or load_settings(None))["research"]["thesis_pages"].get(level or "")
    return (int(rng[0]), int(rng[1])) if rng else None


def ministry_name(data: dict, lang: str, default: str) -> str:
    """Министерство на титуле: settings.yaml → university.ministry, иначе default (норма КР)."""
    return lang_text((data.get("_settings") or load_settings(None))["university"].get("ministry"), lang, default)


def out_dir(data: dict) -> Path:
    d = data["_dir"] / (data.get("output") or "out")
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_sources(data: dict) -> list[dict]:
    rel = data.get("sources") or "sources.yaml"
    path = data["_dir"] / rel
    if not path.exists():
        return []
    return list(read_yaml(path).get("sources") or [])
