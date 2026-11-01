"""Цвет видео из настроек вуза: slides.yaml → university/settings.yaml → brand.yaml → #1F4E79."""
from common import DEFAULT_ACCENT, load_slides, university_info


def deck_in(tmp_path, slides_yaml, accent=None):
    d = tmp_path / "course" / "out" / "slides"
    d.mkdir(parents=True)
    text = slides_yaml.read_text(encoding="utf-8")
    text = "\n".join(line for line in text.splitlines() if not line.startswith("accent:"))
    if accent:
        text = f'accent: "{accent}"\n' + text
    (d / "slides.yaml").write_text(text, encoding="utf-8")
    return d / "slides.yaml"


def test_default_accent(tmp_path, slides_yaml):
    assert load_slides(deck_in(tmp_path, slides_yaml))["accent"] == DEFAULT_ACCENT


def test_accent_from_settings_then_brand(tmp_path, slides_yaml):
    path = deck_in(tmp_path, slides_yaml)
    uni = tmp_path / "university"
    uni.mkdir()
    (uni / "brand.yaml").write_text('color: "#AA0000"\n', encoding="utf-8")
    assert load_slides(path)["accent"] == "#AA0000"
    (uni / "settings.yaml").write_text('brand:\n  color: "#00AA00"\nuniversity:\n  type: private\n', encoding="utf-8")
    assert load_slides(path)["accent"] == "#00AA00"
    assert university_info(path.parent)["type"] == "private"


def test_slides_accent_wins(tmp_path, slides_yaml):
    path = deck_in(tmp_path, slides_yaml, accent="#123456")
    (tmp_path / "university").mkdir()
    (tmp_path / "university" / "settings.yaml").write_text('brand: {color: "#00AA00"}\n', encoding="utf-8")
    assert load_slides(path)["accent"] == "#123456"


def test_bad_university_color_ignored(tmp_path, slides_yaml):
    path = deck_in(tmp_path, slides_yaml)
    (tmp_path / "university").mkdir()
    (tmp_path / "university" / "settings.yaml").write_text('brand: {color: "синий"}\n', encoding="utf-8")
    assert load_slides(path)["accent"] == DEFAULT_ACCENT
