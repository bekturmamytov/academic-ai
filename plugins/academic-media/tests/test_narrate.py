import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import narrate
from common import DataError, get_setting, load_slides
from render import groups_by_section, split_parts

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SRT_BLOCK = re.compile(r"^\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n.+(\n.+)?$")


def test_none_timeline_is_contiguous(slides_yaml, tmp_path):
    deck = load_slides(slides_yaml)
    tl = narrate.build_timeline(deck, "none", tmp_path)
    slides = tl["slides"]
    assert len(slides) == 6
    t = 0.0
    for s, src in zip(slides, deck["slides"]):
        assert s["start"] == pytest.approx(t, abs=1e-3)
        assert s["audio"] is None
        assert s["duration"] >= narrate.MIN_SLIDE
        for c in s["cues"]:
            assert s["start"] <= c["start"] < c["end"] <= s["start"] + s["duration"] + 1e-6
        assert s["reveal"] == sorted(s["reveal"])
        items = src["bullets"] or (src["table"]["rows"] if src["table"] else [])
        assert len(s["reveal"]) == len(items)
        assert all(0 < r < s["duration"] for r in s["reveal"])
        t += s["duration"]
    assert tl["total"] == pytest.approx(t, abs=1e-3)


def test_none_duration_follows_speech_rate(slides_yaml, tmp_path):
    deck = load_slides(slides_yaml)
    tl = narrate.build_timeline(deck, "none", tmp_path)
    s = tl["slides"][2]
    words = narrate.count_words(deck["slides"][2]["notes"])
    assert s["duration"] == pytest.approx(narrate.LEAD + words / narrate.WPM * 60 + narrate.TAIL, abs=0.05)


def test_bullets_reveal_in_sync_with_narration(slides_yaml, tmp_path):
    deck = load_slides(slides_yaml)
    s = narrate.build_timeline(deck, "none", tmp_path)["slides"][2]
    for bullet, at in zip(deck["slides"][2]["bullets"], s["reveal"]):
        cue = next(c for c in s["cues"] if c["start"] - s["start"] == pytest.approx(at, abs=1e-3))
        assert bullet.split()[1][:5].lower() in cue["text"].lower()


def test_srt_format(slides_yaml, tmp_path):
    deck = load_slides(slides_yaml)
    tl = narrate.build_timeline(deck, "none", tmp_path)
    srt = narrate.to_srt(narrate.all_cues(tl))
    blocks = srt.strip().split("\n\n")
    assert len(blocks) == sum(len(s["cues"]) for s in tl["slides"])
    for i, b in enumerate(blocks, 1):
        assert SRT_BLOCK.match(b), b
        assert b.startswith(f"{i}\n")
        assert all(len(line) <= 60 for line in b.split("\n")[2:])


def test_srt_time():
    assert narrate.srt_time(0) == "00:00:00,000"
    assert narrate.srt_time(3723.4567) == "01:02:03,457"


def test_split_cues_respects_limit():
    text = "Короткая фраза. " + "очень длинное предложение без точек, " * 8 + "конец."
    cues = narrate.split_cues(text)
    assert cues[0] == "Короткая фраза."
    assert all(len(c) <= narrate.CUE_CHARS for c in cues)
    assert " ".join(cues).split() == text.split()


def test_wrap_line_two_lines():
    out = narrate.wrap_line("Аномалия обновления: одно и то же значение приходится менять в нескольких строках.")
    assert out.count("\n") == 1


def test_cut_points_takes_longest_pauses():
    silences = [(0.0, 0.5), (4.0, 4.6), (9.0, 11.0), (15.0, 15.3), (20.0, 22.0), (29.8, 30.0)]
    assert narrate.cut_points(silences, 30.0, 3) == [10.0, 21.0]
    with pytest.raises(DataError):
        narrate.cut_points(silences, 30.0, 6)


def test_elevenlabs_without_key_is_clear_error(slides_yaml, tmp_path):
    deck = load_slides(slides_yaml)
    with pytest.raises(DataError, match="ELEVENLABS_API_KEY"):
        narrate.build_timeline(deck, "elevenlabs", tmp_path)


def test_key_from_academic_env(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    (home / ".env").write_text('# ключи\nELEVENLABS_API_KEY="sk_test_123"\n', encoding="utf-8")
    assert get_setting("ELEVENLABS_API_KEY") == "sk_test_123"
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_env")
    assert get_setting("ELEVENLABS_API_KEY") == "sk_env"


def test_cli_none_writes_timeline_and_srt(slides_yaml, tmp_path):
    out = tmp_path / "nar"
    r = subprocess.run([sys.executable, str(SCRIPTS / "narrate.py"), str(slides_yaml), "--mode", "none", "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    tl = json.loads((out / "timeline.json").read_text(encoding="utf-8"))
    assert tl["mode"] == "none" and tl["lang"] == "ru"
    assert (out / "captions.srt").read_text(encoding="utf-8").startswith("1\n00:00:00,500 --> ")


def test_bad_slide_type_is_reported(tmp_path):
    bad = tmp_path / "s.yaml"
    bad.write_text("slides:\n  - type: chart\n    title: X\n", encoding="utf-8")
    with pytest.raises(DataError, match="chart"):
        load_slides(bad)


def _deck(types):
    return [{"type": t} for t in types]


def test_groups_by_section():
    slides = _deck(["title", "section", "bullets", "section", "bullets", "closing"])
    assert groups_by_section(slides) == [[0, 1, 2], [3, 4, 5]]


def test_split_parts_by_sections():
    slides = _deck(["title", "section", "bullets", "bullets", "section", "bullets", "section", "bullets", "closing"])
    minute = 60.0
    durations = [0.1 * minute, 0.1 * minute, 5 * minute, 4 * minute, 0.1 * minute, 7 * minute, 0.1 * minute, 9 * minute, 0.2 * minute]
    parts = split_parts(slides, durations)
    assert parts == [[0, 1, 2, 3], [4, 5], [6, 7, 8]]
    for p in parts:
        assert sum(durations[i] for i in p) <= 15 * minute


def test_short_lecture_is_one_part():
    slides = _deck(["title", "section", "bullets", "closing"])
    assert split_parts(slides, [60, 60, 300, 30]) == [[0, 1, 2, 3]]


def test_oversized_section_is_cut_by_slides():
    slides = _deck(["title"] + ["bullets"] * 10)
    parts = split_parts(slides, [30] + [180] * 10)
    assert all(sum(([30] + [180] * 10)[i] for i in p) <= 15 * 60 for p in parts)
    assert [i for p in parts for i in p] == list(range(11))


def test_spoken_fallback_skips_email_and_subpoint_dash():
    slide = {"notes": "", "title": "Вопросы", "subtitle": "a@b.kg", "bullets": ["Первый", "– подпункт"]}
    assert narrate.spoken_text(slide) == "Вопросы. Первый. подпункт."
