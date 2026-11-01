# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Ключ ElevenLabs преподавателя: создать файл для ключа и проверить ключ.

    uv run key.py --open    создать ~/.academic/.env (если нет) и открыть его в текстовом редакторе
    uv run key.py --check   проверить ключ в ElevenLabs: принят ли, тариф, сколько символов осталось

Ключ живёт только в ~/.academic/.env (Windows: %USERPROFILE%\\.academic\\.env) или в переменной
окружения ELEVENLABS_API_KEY. Скрипт никогда не печатает ключ.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from common import ELEVENLABS_API, DataError, elevenlabs_error, env_path, fail, get_setting

TEMPLATE = """# Ключ ElevenLabs для озвучки видео-лекций (academic-media).
# Где взять: elevenlabs.io → профиль → API Keys → Create (право Text to Speech).
# Вставьте ключ после знака =, без кавычек и пробелов, и сохраните файл.
ELEVENLABS_API_KEY=
# Необязательно: ID своего голоса (Voices → голос → ID).
# ELEVENLABS_VOICE_ID=
"""


def ensure_env_file() -> tuple[Path, bool]:
    """Создаёт файл с шаблоном, если его нет. Возвращает (путь, создан ли сейчас)."""
    path = env_path()
    if path.exists():
        return path, False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TEMPLATE, encoding="utf-8")
    try:
        path.chmod(0o600)  # читать может только владелец (на Windows не действует — и не нужно)
    except OSError:
        pass
    return path, True


def open_in_editor(path: Path) -> None:
    if sys.platform == "darwin":
        cmd = ["open", "-t", str(path)]
    elif os.name == "nt":
        cmd = ["notepad", str(path)]
    else:
        cmd = ["xdg-open", str(path)]
    try:
        subprocess.Popen(cmd)
    except OSError:
        print(f"Откройте файл вручную: {path}")


class ApiError(Exception):
    def __init__(self, code: int, body: str):
        super().__init__(code)
        self.code, self.body = code, body

    @property
    def status(self) -> str:
        try:
            detail = json.loads(self.body).get("detail")
            return str(detail.get("status") or "") if isinstance(detail, dict) else ""
        except (ValueError, AttributeError):
            return ""


def api_get(path: str, key: str) -> dict:
    req = urllib.request.Request(ELEVENLABS_API + path, headers={"xi-api-key": key})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise ApiError(e.code, e.read().decode(errors="replace"))
    except urllib.error.URLError as e:
        raise DataError(f"нет связи с ElevenLabs: {e.reason}")


def check(key: str, voice: str | None) -> list[str]:
    """Проверяет ключ (и голос, если задан). Возвращает строки отчёта; при ошибке — DataError."""
    lines = []
    try:
        sub = api_get("/v1/user/subscription", key)
        used, limit = int(sub.get("character_count") or 0), int(sub.get("character_limit") or 0)
        lines.append("Ключ ElevenLabs: принят.")
        lines.append(f"Тариф: {sub.get('tier') or '—'}; символов осталось: {max(limit - used, 0):,} из {limit:,}."
                     .replace(",", " "))
        if sub.get("status") in ("past_due", "unpaid", "incomplete", "incomplete_expired"):
            lines.append("Внимание: не прошла оплата подписки — ElevenLabs не будет озвучивать, пока тариф "
                         "не оплачен (elevenlabs.io → Subscription).")
        elif sub.get("status") not in (None, "active", "free", "trialing"):
            lines.append(f"Внимание: статус подписки «{sub.get('status')}» — озвучка может не работать.")
        if limit and limit - used < 15000:
            lines.append("Внимание: осталось меньше ~15 000 символов — это примерно одна лекция на 15 минут.")
    except ApiError as e:
        if e.status != "missing_permissions":
            raise DataError(elevenlabs_error(e.code, e.body))
        # Ключ только с правом Text to Speech: тариф не прочитать, но сам ключ рабочий.
        lines.append("Ключ ElevenLabs: принят (у ключа нет права читать тариф — остаток символов не показать).")
    if voice:
        try:
            v = api_get(f"/v1/voices/{voice}", key)
            lines.append(f"Голос: {v.get('name') or voice} — найден.")
        except ApiError as e:
            if e.status == "missing_permissions":
                lines.append("Голос: не проверить (у ключа нет права Voices) — проверится при озвучке.")
            else:
                raise DataError(elevenlabs_error(e.code, e.body))
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(description="Ключ ElevenLabs: создать файл и проверить ключ")
    ap.add_argument("--open", action="store_true", help="создать ~/.academic/.env и открыть в редакторе")
    ap.add_argument("--check", action="store_true", help="проверить ключ в ElevenLabs")
    a = ap.parse_args()
    if not (a.open or a.check):
        ap.error("укажите --open или --check")

    if a.open:
        path, created = ensure_env_file()
        print(("Создан файл " if created else "Файл уже есть: ") + str(path))
        print("Вставьте ключ после ELEVENLABS_API_KEY= и сохраните файл. Ключ в чат не присылайте.")
        open_in_editor(path)
        return

    key = get_setting("ELEVENLABS_API_KEY")
    if not key:
        fail(f"ключ не найден. Запустите key.py --open, вставьте ключ в {env_path()} и сохраните.")
    try:
        for line in check(key, get_setting("ELEVENLABS_VOICE_ID")):
            print(line)
    except DataError as e:
        fail(str(e))


if __name__ == "__main__":
    main()
