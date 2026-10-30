"""Общий код скриптов academic-media: слайды, ключи, проверка окружения, подписи.

Скрипты импортируют его так:
    sys.path.insert(0, str(Path(__file__).parent)); from common import ...
Зависимости (pyyaml, python-pptx) объявляет сам скрипт в PEP 723.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

SLIDE_TYPES = ("title", "section", "bullets", "table", "closing")
DEFAULT_ACCENT = "#1F4E79"


class DataError(Exception):
    """Ошибка в данных пользователя — печатается по-русски, без трейсбека."""


def fail(msg: str, code: int = 1) -> None:
    print(f"Ошибка: {msg}", file=sys.stderr)
    sys.exit(code)


def warn(msg: str) -> None:
    print(f"Внимание: {msg}", file=sys.stderr)


def academic_home() -> Path:
    return Path(os.environ.get("ACADEMIC_HOME") or Path.home() / ".academic")


# Подписи в кадре. Ключ отсутствует в языке — берётся ru.
LABELS: dict[str, dict[str, str]] = {
    "part": {"ru": "Часть {k} из {n}", "ky": "{n} бөлүктүн {k}-бөлүгү", "en": "Part {k} of {n}"},
    "section": {"ru": "Раздел", "ky": "Бөлүм", "en": "Section"},
    "end": {"ru": "Спасибо за внимание", "ky": "Көңүл бурганыңыз үчүн рахмат", "en": "Thank you for your attention"},
    "teacher": {"ru": "Преподаватель", "ky": "Окутуучу", "en": "Instructor"},
}


def t(key: str, lang: str = "ru", **kw) -> str:
    entry = LABELS[key]
    return (entry.get(lang) or entry["ru"]).format(**kw)


# ---------- слайды ----------

def _table(raw) -> dict | None:
    if not raw:
        return None
    if isinstance(raw, dict):
        header = [str(c) for c in raw.get("header") or []]
        rows = [[str(c) for c in r] for r in raw.get("rows") or []]
    elif isinstance(raw, list) and raw and all(isinstance(r, list) for r in raw):
        header = [str(c) for c in raw[0]]
        rows = [[str(c) for c in r] for r in raw[1:]]
    else:
        raise DataError("таблица слайда — {header: [...], rows: [[...]]} или список строк таблицы")
    return {"header": header, "rows": rows}


CORE_TYPES = {"content": "bullets"}  # slides.yaml из academic-core (skill slides)


def _plain(text) -> str:
    return re.sub(r"\*\*(.+?)\*\*|__(.+?)__|\*(.+?)\*", lambda m: next(g for g in m.groups() if g), str(text)).strip()


def _bullet(b) -> str:
    """Пункт core бывает строкой или {text, sub: [...]} — в кадре одна строка."""
    if isinstance(b, dict):
        sub = [_plain(x) for x in b.get("sub") or []]
        return _plain(b.get("text") or "") + (f" — {', '.join(sub)}" if sub else "")
    return _plain(b)


def _diagram_bullets(d) -> list[str]:
    """Схема core (diagram.items) в видео показывается пунктами."""
    out = []
    for it in (d or {}).get("items") or []:
        if isinstance(it, dict):
            out.append(_plain(it.get("title") or "") + (f": {_plain(it['text'])}" if it.get("text") else ""))
        else:
            out.append(_plain(it))
    return [x for x in out if x]


def normalize(data: dict, source: str = "slides.yaml") -> dict:
    """Приводит slides.yaml к одному виду и проверяет обязательные поля."""
    if not isinstance(data, dict) or not isinstance(data.get("slides"), list) or not data["slides"]:
        raise DataError(f"в {source} нет списка slides")
    raw = list(data["slides"])
    if data.get("questions") and not any(isinstance(s, dict) and s.get("type") == "closing" for s in raw):
        raw.append({"type": "closing", "bullets": data["questions"]})
    slides = []
    for i, s in enumerate(raw, 1):
        if not isinstance(s, dict):
            raise DataError(f"слайд {i} в {source} — не словарь")
        s = dict(s)
        bullets = [_bullet(b) for b in s.get("bullets") or []]
        if not bullets and s.get("diagram"):
            bullets = _diagram_bullets(s["diagram"])
        s["bullets"] = bullets
        kind = str(s.get("type") or ("bullets" if s.get("bullets") else "section")).strip()
        kind = CORE_TYPES.get(kind, kind)
        if kind not in SLIDE_TYPES:
            raise DataError(f"слайд {i}: тип «{kind}» неизвестен, нужен один из {', '.join(SLIDE_TYPES)}")
        table = _table(s.get("table"))
        if kind == "table" and not table:
            raise DataError(f"слайд {i}: тип table, но таблицы нет")
        slides.append({
            "n": i,
            "type": kind,
            "title": str(s.get("title") or "").strip(),
            "subtitle": str(s.get("subtitle") or "").strip(),
            "bullets": [str(b).strip() for b in s.get("bullets") or [] if str(b).strip()],
            "table": table,
            "notes": str(s.get("notes") or "").strip(),
        })
    accent = str(data.get("accent") or DEFAULT_ACCENT).strip()
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", accent):
        warn(f"цвет accent «{accent}» не в виде #RRGGBB — беру {DEFAULT_ACCENT}")
        accent = DEFAULT_ACCENT
    return {
        "title": str(data.get("title") or slides[0]["title"]).strip(),
        "course": str(data.get("course") or "").strip(),
        "teacher": str(data.get("teacher") or "").strip(),
        "accent": accent,
        "lang": str(data.get("lang") or "").strip(),
        "slides": slides,
    }


def load_slides(path: str | Path) -> dict:
    """slides.yaml или .pptx → нормализованный словарь слайдов."""
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise DataError(f"не найден файл {p}")
    if p.suffix.lower() == ".pptx":
        from slides_from_pptx import extract
        return normalize(extract(p), p.name)
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        raise DataError(f"в {p.name} ошибка разметки YAML: {e}")
    return normalize(data, p.name)


# ---------- ключ ElevenLabs ----------

def read_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip().removeprefix("export ").strip()] = v.strip().strip('"').strip("'")
    return out


def get_setting(name: str) -> str | None:
    """Переменная окружения, затем ~/.academic/.env. Значение никогда не печатается."""
    val = os.environ.get(name) or os.environ.get(f"CLAUDE_PLUGIN_OPTION_{name}")
    if val:
        return val.strip()
    return read_env_file(academic_home() / ".env").get(name) or None


# ---------- окружение ----------

SETUP_HINT = "Запустите /academic:setup — он проверит и поставит недостающее."


def node_major() -> int | None:
    node = shutil.which("node")
    if not node:
        return None
    try:
        out = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    m = re.match(r"v(\d+)", out.strip())
    return int(m.group(1)) if m else None


def check_tools(need_node: bool = True, need_ffmpeg: bool = True) -> list[str]:
    """Список проблем окружения по-русски (пустой — всё есть)."""
    problems = []
    if need_node:
        major = node_major()
        if major is None:
            problems.append("не найден Node.js (нужна версия 20 или новее)")
        elif major < 20:
            problems.append(f"Node.js версии {major} устарел — нужна 20 или новее")
        elif not shutil.which("npx") or not shutil.which("npm"):
            problems.append("не найдены npm/npx (ставятся вместе с Node.js)")
    if need_ffmpeg:
        for tool in ("ffmpeg", "ffprobe"):
            if not shutil.which(tool):
                problems.append(f"не найден {tool} (программа для звука и видео)")
    return problems


def ensure_tools(need_node: bool = True, need_ffmpeg: bool = True) -> None:
    problems = check_tools(need_node, need_ffmpeg)
    if problems:
        fail("для видео-лекции не хватает программ:\n  - " + "\n  - ".join(problems) + f"\n{SETUP_HINT}")


def media_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(out.stdout.strip())
    except ValueError:
        raise DataError(f"не удалось прочитать длительность {path.name} — файл повреждён или не аудио")
