import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def slides_yaml() -> Path:
    return FIXTURES / "slides.yaml"


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    """Ключи и движок — только из временной папки, не из ~/.academic разработчика."""
    monkeypatch.setenv("ACADEMIC_HOME", str(tmp_path / "home"))
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.delenv("CLAUDE_PLUGIN_OPTION_ELEVENLABS_API_KEY", raising=False)
