"""Общий код скриптов academic-research: паспорт работы, профиль, бренд вуза.

Скрипты импортируют его так:
    sys.path.insert(0, str(Path(__file__).parent)); from common import ...
Зависимости (pyyaml и др.) объявляет сам скрипт в PEP 723.
Часть кода скопирована из academic-core/scripts/common.py — пути между плагинами не делим.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

WORK_TYPES = ("referat", "doklad", "tezisy", "statya", "kursovaya", "diplom",
              "magistr", "kandidat", "avtoreferat")
STYLES = ("gost", "apa", "ieee")
SHORT_TYPES = ("statya", "tezisy", "doklad")
DISSERTATIONS = ("magistr", "kandidat")

DATA_MARK = "НУЖНЫ ВАШИ ДАННЫЕ"
SOURCE_MARK = "НУЖЕН ИСТОЧНИК"
UNVERIFIED_MARK = "НЕ ПРОВЕРЕНО"


class DataError(Exception):
    """Ошибка в данных пользователя — печатается по-русски, без трейсбека."""


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
    """Паспорт работы + профиль + бренд вуза в одном словаре.

    Служебные ключи: _dir (папка работы), _profile, _brand, _brand_dir.
    """
    path = Path(work_yaml).expanduser().resolve()
    data = read_yaml(path)
    if data.get("type") not in WORK_TYPES:
        raise DataError(f"type = «{data.get('type')}», а нужно одно из: {', '.join(WORK_TYPES)}")
    style = data.setdefault("citation_style", "gost")
    if style not in STYLES:
        raise DataError(f"citation_style = «{style}», а нужно gost, apa или ieee")
    data["_dir"] = path.parent
    prof = find_up(path.parent, "profile.yaml")
    data["_profile"] = read_yaml(prof) if prof else {}
    uni = find_up(path.parent, "university")
    brand_file = uni / "brand.yaml" if uni else None
    data["_brand"] = read_yaml(brand_file) if brand_file and brand_file.exists() else {}
    data["_brand_dir"] = uni
    p = data["_profile"]
    if not data.get("authors"):
        data["authors"] = [{k: p.get(k, "") for k in ("name", "degree", "position", "email")}
                           | {"affiliation": p.get("university", ""), "city": p.get("city", "")}]
    for k in ("faculty", "department", "city"):
        if not data.get(k):
            data[k] = p.get(k, "")
    data.setdefault("language", p.get("language", "ru"))
    return data


def university_name(data: dict, lang: str) -> str:
    if data.get("university"):
        return data["university"]
    b = data.get("_brand", {})
    key = {"ru": "name", "ky": "name_ky", "en": "name_en"}.get(lang, "name")
    return b.get(key) or b.get("name") or data.get("_profile", {}).get("university", "")


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
