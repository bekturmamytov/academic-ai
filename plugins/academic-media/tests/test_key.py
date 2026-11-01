"""Ключ ElevenLabs преподавателя: файл .env, проверка ключа, понятные ошибки. Сеть не нужна."""
import io
import json
import os
import urllib.error

import pytest

import key
from common import DataError, elevenlabs_error, env_path, get_setting


def _http_error(code: int, status: str, message: str = "msg") -> urllib.error.HTTPError:
    body = json.dumps({"detail": {"status": status, "message": message}}).encode()
    return urllib.error.HTTPError("https://api.elevenlabs.io", code, "err", {}, io.BytesIO(body))


class FakeResponse:
    def __init__(self, data: dict):
        self.data = json.dumps(data).encode()

    def read(self):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_env_file_created_with_template_and_private():
    path, created = key.ensure_env_file()
    assert created and path == env_path()
    assert "ELEVENLABS_API_KEY=" in path.read_text(encoding="utf-8")
    if os.name != "nt":
        assert path.stat().st_mode & 0o077 == 0
    assert get_setting("ELEVENLABS_API_KEY") is None  # пустой шаблон — ключа нет
    _, again = key.ensure_env_file()
    assert not again


def test_env_file_not_overwritten():
    env_path().parent.mkdir(parents=True)
    env_path().write_text("ELEVENLABS_API_KEY=sk_secret\n", encoding="utf-8")
    key.ensure_env_file()
    assert get_setting("ELEVENLABS_API_KEY") == "sk_secret"


def test_check_reports_tier_and_characters(monkeypatch):
    def fake(req, timeout):
        assert req.get_header("Xi-api-key") == "sk_test"
        if req.full_url.endswith("/subscription"):
            return FakeResponse({"tier": "creator", "character_count": 10000, "character_limit": 100000, "status": "active"})
        return FakeResponse({"name": "Мой голос"})

    monkeypatch.setattr(key.urllib.request, "urlopen", fake)
    out = "\n".join(key.check("sk_test", "voice123"))
    assert "принят" in out and "creator" in out and "90 000 из 100 000" in out
    assert "Мой голос" in out
    assert "sk_test" not in out


def test_check_tts_only_key_is_ok(monkeypatch):
    def fake(req, timeout):
        raise _http_error(401, "missing_permissions", "user_read")

    monkeypatch.setattr(key.urllib.request, "urlopen", fake)
    out = "\n".join(key.check("sk_test", None))
    assert "принят" in out


@pytest.mark.parametrize("code,status,expect", [
    (401, "invalid_api_key", "не принял ключ"),
    (401, "payment_required", "оплата"),
    (401, "quota_exceeded", "символы"),
    (404, "voice_not_found", "голос не найден"),
])
def test_check_errors_are_plain_russian(monkeypatch, code, status, expect):
    def fake(req, timeout):
        raise _http_error(code, status)

    monkeypatch.setattr(key.urllib.request, "urlopen", fake)
    with pytest.raises(DataError, match=expect):
        key.check("sk_test", None)


def test_error_text_without_json_body():
    assert "не принял ключ" in elevenlabs_error(401, "Unauthorized")
    assert "500" in elevenlabs_error(500, "oops")
