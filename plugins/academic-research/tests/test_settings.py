"""Настройки вуза university/settings.yaml в научных работах: ссылки, оформление, титул, объём."""
import subprocess
import sys
from pathlib import Path

import yaml
from docx import Document

import check_format
from build_docx import build
from common import load_work
from conftest import PLUGIN, set_yaml
from test_check_format import bad_docx

UNI = {
    "university": {"name": "Университет Настроек", "ministry": {"ru": "Министерство образования и науки КР"}},
    "document": {"font": "Arial", "size": 12, "line_spacing": 1.0, "margins_mm": {"left": 20, "right": 20}},
    "research": {"citation_style": "apa", "bib_order": "cite", "thesis_pages": {"bachelor": [5, 10]}},
}


def write_settings(root: Path, data: dict) -> None:
    (root / "university").mkdir(exist_ok=True)
    (root / "university" / "settings.yaml").write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")


def drop_keys(path: Path, *keys) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for k in keys:
        data.pop(k, None)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def test_citation_defaults_from_settings(workspace):
    drop_keys(workspace / "work.yaml", "citation_style", "bib_order")
    w = load_work(workspace / "work.yaml")
    assert w["citation_style"] == "gost" and "bib_order" not in w  # нет настроек — ГОСТ, порядок по стилю
    write_settings(workspace.parent, UNI)
    w = load_work(workspace / "work.yaml")
    assert w["citation_style"] == "apa" and w["bib_order"] == "cite"
    set_yaml(workspace / "work.yaml", citation_style="ieee")  # work.yaml главнее
    assert load_work(workspace / "work.yaml")["citation_style"] == "ieee"


def test_docx_and_title_follow_settings(workspace):
    write_settings(workspace.parent, UNI)
    set_yaml(workspace / "work.yaml", type="diplom")
    out, _, _ = build(workspace / "work.yaml")
    doc = Document(str(out))
    s = doc.sections[0]
    assert round(s.left_margin.mm) == 20 and round(s.right_margin.mm) == 20 and round(s.top_margin.mm) == 20
    normal = doc.styles["Normal"]
    assert normal.font.name == "Arial" and normal.font.size.pt == 12
    assert normal.paragraph_format.line_spacing == 1.0
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "Министерство образования и науки КР" in text
    assert "Кыргызский государственный технический университет" not in text.split("\n")[1]  # вуз из настроек
    assert "Университет Настроек" in text


def test_status_shows_thesis_norm(workspace):
    write_settings(workspace.parent, UNI)
    set_yaml(workspace / "work.yaml", type="diplom")
    r = subprocess.run([sys.executable, str(PLUGIN / "scripts" / "status.py"), str(workspace / "work.yaml")],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    assert "Объём по требованиям вуза: 5–10 стр." in r.stdout


def test_check_format_uses_settings(tmp_path, monkeypatch):
    path = bad_docx(tmp_path / "work.docx")  # Arial 12, поля 20 мм
    probs, _ = check_format.check(path)
    assert any(p.area == "поля" for p in probs)
    write_settings(tmp_path, {"document": {"font": "Arial", "size": 12,
                                           "margins_mm": {"left": 20, "right": 20, "top": 20, "bottom": 20}}})
    for name in ("FONT", "SIZE", "SPACING", "INDENT_CM", "MARGINS"):
        monkeypatch.setattr(check_format, name, getattr(check_format, name))  # вернуть после теста
    check_format.use_settings(tmp_path)
    probs, _ = check_format.check(path)
    assert not any(p.area == "поля" for p in probs)  # поля 20 мм — как требует вуз
    font = next(p.text for p in probs if p.area == "шрифт")
    assert font.startswith("не Arial: 1 из")  # Arial не замечание; остался лишь абзац с меткой
