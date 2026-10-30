"""slides.yaml из academic-core (skill slides) должен приниматься как есть."""
from pathlib import Path

from common import normalize

CORE_EXAMPLE = Path(__file__).resolve().parents[2] / "academic-core/skills/slides/templates/slides.example.yaml"


def test_core_example_normalizes():
    import yaml

    data = normalize(yaml.safe_load(CORE_EXAMPLE.read_text(encoding="utf-8")))
    kinds = [s["type"] for s in data["slides"]]
    assert "content" not in kinds
    assert kinds[-1] == "closing"  # из questions


def test_core_bullets_and_diagram():
    data = normalize({"slides": [
        {"type": "content", "title": "A", "bullets": ["**Жирный** пункт", {"text": "Главный", "sub": ["x", "y"]}]},
        {"type": "content", "title": "B", "diagram": {"kind": "steps", "items": ["Шаг 1", {"title": "Шаг 2", "text": "пояснение"}]}},
    ]})
    assert data["slides"][0]["bullets"] == ["Жирный пункт", "Главный — x, y"]
    assert data["slides"][1]["bullets"] == ["Шаг 1", "Шаг 2: пояснение"]
