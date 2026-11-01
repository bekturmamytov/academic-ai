# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6", "python-pptx>=1.0"]
# ///
"""Озвучка слайдов и тайминг: slides.yaml (или .pptx) → timeline.json + captions.srt + audio/.

    uv run narrate.py <slides.yaml> --mode none|elevenlabs|recording --out <папка>
        [--lang ru] [--voice ID] [--model eleven_v3] [--recording <файл или папка>] [--estimate]

Режимы:
  none        — без голоса: длительность слайда по тексту заметок (~150 слов/мин), только титры;
  elevenlabs  — голос ElevenLabs по ключу ELEVENLABS_API_KEY (переменная окружения или ~/.academic/.env);
  recording   — своя запись: папка с файлом на слайд (01.mp3, 02.m4a …) или один файл
                с паузами 2–3 с между слайдами (режется по тишине).

timeline.json: {"total", "slides": [{"n", "type", "start", "duration", "audio", "audio_offset",
"text", "cues": [{"start", "end", "text"}], "reveal": [...]}]}. start и cues — секунды от начала
лекции, reveal (появление пунктов) — секунды от начала слайда, audio — путь от папки --out.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from common import (DataError, elevenlabs_error, ensure_tools, fail, get_setting, load_slides,
                    media_duration, warn)

WPM = 150
LEAD = 0.5            # пауза в начале слайда до голоса
TAIL = 0.8            # пауза после голоса до смены слайда
MIN_SLIDE = 4.0
TITLE_SLIDE = 5.0
CUE_CHARS = 84        # две строки титров по ~42 знака
LINE_CHARS = 42
MIN_CUE = 1.0

DEFAULT_MODEL = "eleven_v3"
DEFAULT_VOICE = "JBFqnCBsd6RMkjVDRZzb"  # премиум-голос библиотеки ElevenLabs; свой — --voice или ELEVENLABS_VOICE_ID
TTS_CHUNK = 2500
VOICE_SETTINGS = {"stability": 0.5, "similarity_boost": 0.75}

WORD_RE = re.compile(r"\w+(?:[-'’]\w+)*", re.UNICODE)


# ---------- текст ----------

def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def speech_seconds(text: str, wpm: int = WPM) -> float:
    return count_words(text) / wpm * 60


def spoken_text(slide: dict) -> str:
    """Что произносит голос: заметки, а без них — заголовок и пункты."""
    if slide["notes"]:
        return slide["notes"]
    subtitle = "" if "@" in slide["subtitle"] else slide["subtitle"]  # email на closing не читаем
    parts = [slide["title"], subtitle, *(re.sub(r"^[–-]\s+", "", b) for b in slide["bullets"])]
    return " ".join(p.rstrip(".") + "." for p in parts if p)


def _split_long(text: str, limit: int) -> list[str]:
    if len(text) <= limit:
        return [text]
    pieces = [p.strip() for p in re.split(r"(?<=[,;:—–])\s+", text) if p.strip()]
    out, cur = [], ""
    for p in pieces:
        if len(p) > limit:
            if cur:
                out.append(cur)
                cur = ""
            words, line = p.split(), ""
            for w in words:
                if line and len(line) + 1 + len(w) > limit:
                    out.append(line)
                    line = w
                else:
                    line = f"{line} {w}".strip()
            if line:
                out.append(line)
        elif cur and len(cur) + 1 + len(p) > limit:
            out.append(cur)
            cur = p
        else:
            cur = f"{cur} {p}".strip()
    if cur:
        out.append(cur)
    return out


def split_cues(text: str, limit: int = CUE_CHARS) -> list[str]:
    """Текст → фразы титров не длиннее limit знаков, по предложениям и запятым."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    sentences = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text) if s.strip()]
    out = []
    for s in sentences:
        out.extend(_split_long(s, limit))
    return out


def wrap_line(text: str, width: int = LINE_CHARS) -> str:
    """Фраза титров → не больше двух строк, разрыв у пробела ближе к середине."""
    if len(text) <= width:
        return text
    mid = len(text) // 2
    spaces = [i for i, ch in enumerate(text) if ch == " "]
    if not spaces:
        return text
    cut = min(spaces, key=lambda i: abs(i - mid))
    return text[:cut] + "\n" + text[cut + 1:]


def _weight(chunk: str) -> float:
    return len(chunk) + (6 if re.search(r"[.!?…]$", chunk) else 2 if re.search(r"[,;:—]$", chunk) else 0)


def time_cues(chunks: list[str], start: float, end: float, words: list[dict] | None = None) -> list[dict]:
    """Тайминг фраз: по словам ElevenLabs, если есть, иначе пропорционально длине."""
    if not chunks:
        return []
    cues = []
    if words:
        i = 0
        for ch in chunks:
            n = len(ch.split())
            seg = words[i:i + n] or words[-1:]
            cues.append({"start": start + seg[0]["start"], "end": start + seg[-1]["end"], "text": ch})
            i += n
    else:
        span = max(end - start, MIN_CUE * len(chunks) * 0.5)
        total = sum(_weight(c) for c in chunks)
        t = start
        for ch in chunks:
            d = span * _weight(ch) / total
            cues.append({"start": t, "end": t + d, "text": ch})
            t += d
    for a, b in zip(cues, cues[1:]):
        a["end"] = min(max(a["end"], a["start"] + MIN_CUE), b["start"])
    for c in cues:
        c["start"], c["end"] = round(c["start"], 3), round(max(c["end"], c["start"] + 0.3), 3)
    return cues


def _stems(text: str) -> set[str]:
    return {w.lower()[:5] for w in WORD_RE.findall(text) if len(w) > 3}


def bullet_reveals(slide: dict, cues: list[dict], slide_start: float, duration: float) -> list[float]:
    """Когда появляется каждый пункт (секунды от начала слайда): по совпадению слов с фразой голоса."""
    items = slide["bullets"] or ([" ".join(r) for r in slide["table"]["rows"]] if slide["table"] else [])
    n = len(items)
    if not n:
        return []
    if not cues:
        return [round(min(0.5 + i * 1.2, max(0.5, duration - 1.5)), 3) for i in range(n)]
    a = cues[0]["start"] - slide_start
    b = cues[-1]["end"] - slide_start
    default = [a + (b - a) * 0.8 * i / n for i in range(n)]
    out, last = [], 0.0
    for i, item in enumerate(items):
        want = _stems(item)
        best, best_t = 0.0, None
        if want:
            for c in cues:
                ct = c["start"] - slide_start
                if ct < last:
                    continue
                score = len(want & _stems(c["text"])) / len(want)
                if score > best:
                    best, best_t = score, ct
        t = best_t if best_t is not None and best >= 0.5 else default[i]
        t = max(t, last, 0.3)
        out.append(round(min(t, max(0.3, duration - 1.0)), 3))
        last = out[-1]
    return out


# ---------- голос ----------

def _http_error(e: urllib.error.HTTPError) -> str:
    return elevenlabs_error(e.code, e.read().decode(errors="replace"))


def _words_from_chars(chars, starts, ends) -> list[dict]:
    words, cur, s, prev = [], "", None, 0.0
    for ch, a, b in zip(chars, starts, ends):
        if ch.isspace():
            if cur:
                words.append({"text": cur, "start": s, "end": prev})
            cur, s = "", None
        else:
            s = a if s is None else s
            cur += ch
            prev = b
    if cur:
        words.append({"text": cur, "start": s, "end": prev})
    return words


def _chunks_for_tts(text: str, limit: int = TTS_CHUNK) -> list[str]:
    out, cur = [], ""
    for s in split_cues(text, limit):
        if cur and len(cur) + 1 + len(s) > limit:
            out.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        out.append(cur)
    return out


def tts_elevenlabs(text: str, out_mp3: Path, key: str, voice: str, model: str) -> list[dict]:
    """Озвучивает текст (кусками ≤ TTS_CHUNK), склеивает в out_mp3, возвращает тайминги слов."""
    words_all: list[dict] = []
    with tempfile.TemporaryDirectory() as tmp:
        parts, offset = [], 0.0
        for k, chunk in enumerate(_chunks_for_tts(text)):
            body = {"text": chunk, "model_id": model, "voice_settings": VOICE_SETTINGS}
            req = urllib.request.Request(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128",
                data=json.dumps(body).encode(), method="POST",
                headers={"xi-api-key": key, "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    data = json.loads(r.read())
            except urllib.error.HTTPError as e:
                raise DataError(_http_error(e))
            except urllib.error.URLError as e:
                raise DataError(f"нет связи с ElevenLabs: {e.reason}")
            part = Path(tmp) / f"{k:03d}.mp3"
            part.write_bytes(base64.b64decode(data["audio_base64"]))
            al = data.get("alignment") or data.get("normalized_alignment") or {}
            ws = _words_from_chars(al.get("characters", []), al.get("character_start_times_seconds", []),
                                   al.get("character_end_times_seconds", []))
            words_all += [{**w, "start": w["start"] + offset, "end": w["end"] + offset} for w in ws]
            offset += media_duration(part)
            parts.append(part)
        if len(parts) == 1:
            out_mp3.write_bytes(parts[0].read_bytes())
        else:
            lst = Path(tmp) / "list.txt"
            lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                            "-c", "copy", str(out_mp3)], check=True)
    return words_all


def find_silences(path: Path, noise: str = "-35dB", min_len: float = 1.0) -> list[tuple[float, float]]:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                        f"silencedetect=noise={noise}:d={min_len}", "-f", "null", "-"],
                       capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return list(zip(starts, ends))


def cut_points(silences: list[tuple[float, float]], total: float, n_slides: int) -> list[float]:
    """n_slides-1 самых длинных внутренних пауз → точки разреза (середины пауз), по времени."""
    inner = [(s, e) for s, e in silences if s > 0.2 and e < total - 0.2]
    if len(inner) < n_slides - 1:
        raise DataError(
            f"в записи нашлось пауз: {len(inner)}, а переходов между слайдами: {n_slides - 1}. "
            "Сделайте паузу 2–3 секунды перед каждым новым слайдом или запишите по файлу на слайд.")
    longest = sorted(inner, key=lambda p: p[1] - p[0], reverse=True)[:n_slides - 1]
    return sorted((s + e) / 2 for s, e in longest)


# Тишина по краям куска записи срезается, чтобы голос начинался через LEAD после смены слайда.
TRIM = ("silenceremove=start_periods=1:start_threshold=-40dB,areverse,"
        "silenceremove=start_periods=1:start_threshold=-40dB,areverse")


def split_recording(src: Path, n: int, audio_dir: Path) -> list[Path]:
    total = media_duration(src)
    points = [0.0, *cut_points(find_silences(src), total, n), total]
    out = []
    for i in range(n):
        dst = audio_dir / f"{i + 1:02d}-rec.mp3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vn", "-af",
                        f"atrim=start={points[i]:.3f}:end={points[i + 1]:.3f},asetpts=PTS-STARTPTS,{TRIM}",
                        "-c:a", "libmp3lame", "-b:a", "128k", str(dst)], check=True)
        out.append(dst)
    return out


def recording_files(src: Path, n: int, audio_dir: Path) -> list[Path | None]:
    """Своя запись → файл на каждый слайд (None — для слайда записи нет)."""
    if src.is_file():
        return list(split_recording(src, n, audio_dir))
    if not src.is_dir():
        raise DataError(f"не найдена запись {src}")
    by_num: dict[int, Path] = {}
    for f in sorted(src.iterdir()):
        if f.suffix.lower() not in (".mp3", ".m4a", ".wav", ".ogg", ".aac", ".flac", ".webm", ".mp4"):
            continue
        m = re.search(r"(\d+)", f.stem)
        if m:
            by_num.setdefault(int(m.group(1)), f)
    if not by_num:
        raise DataError(f"в папке {src} нет аудиофайлов с номером слайда в имени (01.mp3, 02.m4a …)")
    out: list[Path | None] = []
    for i in range(1, n + 1):
        f = by_num.get(i)
        if f is None:
            out.append(None)
            continue
        dst = audio_dir / f"{i:02d}-rec.mp3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(f), "-vn", "-af", TRIM,
                        "-c:a", "libmp3lame", "-b:a", "128k", str(dst)], check=True)
        out.append(dst)
    return out


# ---------- тайминг ----------

def silent_duration(slide: dict) -> float:
    if slide["notes"]:
        return max(MIN_SLIDE, LEAD + speech_seconds(slide["notes"]) + TAIL)
    if slide["type"] in ("title", "section", "closing"):
        return TITLE_SLIDE
    shown = " ".join([slide["title"], *slide["bullets"]])
    if slide["table"]:
        shown += " " + " ".join(" ".join(r) for r in slide["table"]["rows"])
    return max(MIN_SLIDE + 2, speech_seconds(shown) + 2)


def build_timeline(deck: dict, mode: str, out_dir: Path, lang: str = "ru", voice: str | None = None,
                   model: str = DEFAULT_MODEL, recording: Path | None = None) -> dict:
    audio_dir = out_dir / "audio"
    if mode != "none":
        audio_dir.mkdir(parents=True, exist_ok=True)
    slides = deck["slides"]
    rec: list[Path | None] = []
    key = None
    if mode == "elevenlabs":
        key = get_setting("ELEVENLABS_API_KEY")
        if not key:
            raise DataError(
                "нет ключа ElevenLabs. Добавьте строку ELEVENLABS_API_KEY=ваш_ключ в файл "
                "~/.academic/.env (или переменную окружения) — либо выберите режим без голоса.")
        voice = voice or get_setting("ELEVENLABS_VOICE_ID") or DEFAULT_VOICE
    elif mode == "recording":
        if recording is None:
            raise DataError("для режима recording укажите --recording <файл или папка>")
        rec = recording_files(recording, len(slides), audio_dir)

    items, t = [], 0.0
    for i, s in enumerate(slides):
        audio, words, offset = None, None, LEAD
        if mode == "none":
            text = s["notes"]
            duration = silent_duration(s)
            speech = (LEAD, duration - TAIL) if text else (0, 0)
        else:
            text = spoken_text(s) if mode == "elevenlabs" else s["notes"]
            if mode == "elevenlabs" and text:
                h = hashlib.sha1(json.dumps([text, voice, model, VOICE_SETTINGS], ensure_ascii=False)
                                 .encode()).hexdigest()[:10]
                mp3 = audio_dir / f"{s['n']:02d}-{h}.mp3"
                cache = mp3.with_suffix(".json")
                if mp3.exists() and cache.exists():
                    words = json.loads(cache.read_text(encoding="utf-8"))
                else:
                    print(f"Озвучиваю слайд {s['n']} из {len(slides)}…", file=sys.stderr)
                    words = tts_elevenlabs(text, mp3, key, voice, model)
                    cache.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
                audio = mp3
            elif mode == "recording":
                audio = rec[i]
                if audio is None:
                    warn(f"для слайда {s['n']} нет записи — он пойдёт без голоса")
            if audio is not None:
                dur = media_duration(audio)
                duration = LEAD + dur + TAIL
                speech = (LEAD, LEAD + dur)
            else:
                duration = silent_duration(s)
                speech = (LEAD, duration - TAIL) if text else (0, 0)
        if not s["notes"] and mode != "elevenlabs":
            warn(f"у слайда {s['n']} нет заметок докладчика — титров на нём не будет")
        chunks = split_cues(text) if text else []
        cues = time_cues(chunks, t + speech[0], t + speech[1], words)
        if words and len(words) != sum(len(c.split()) for c in chunks):
            cues = time_cues(chunks, t + speech[0], t + speech[1])
        duration = round(max(duration, (cues[-1]["end"] - t + TAIL) if cues else 0), 3)
        items.append({
            "n": s["n"], "type": s["type"], "start": round(t, 3), "duration": duration,
            "audio": audio.relative_to(out_dir).as_posix() if audio else None,
            "audio_offset": offset, "text": text, "cues": cues,
            "reveal": bullet_reveals(s, cues, t, duration),
        })
        t += duration
    return {"version": 1, "mode": mode, "lang": lang, "voice": voice if mode == "elevenlabs" else None,
            "model": model if mode == "elevenlabs" else None, "total": round(t, 3), "slides": items}


# ---------- титры ----------

def srt_time(sec: float) -> str:
    ms = int(round(max(sec, 0) * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def to_srt(cues: list[dict], shift: float = 0.0) -> str:
    blocks = []
    for i, c in enumerate(cues, 1):
        blocks.append(f"{i}\n{srt_time(c['start'] + shift)} --> {srt_time(c['end'] + shift)}\n{wrap_line(c['text'])}\n")
    return "\n".join(blocks)


def all_cues(timeline: dict) -> list[dict]:
    return [c for s in timeline["slides"] for c in s["cues"]]


def estimate(deck: dict, mode: str) -> str:
    chars = sum(len(spoken_text(s)) for s in deck["slides"]) if mode == "elevenlabs" else 0
    minutes = sum(silent_duration(s) for s in deck["slides"]) / 60
    line = f"Слайдов: {len(deck['slides'])}, примерно {minutes:.0f} мин видео."
    if chars:
        line += f" Для ElevenLabs — около {chars} символов (списываются с вашего тарифа)."
    return line


def main() -> None:
    ap = argparse.ArgumentParser(description="Озвучка и тайминг слайдов видео-лекции")
    ap.add_argument("slides", help="slides.yaml или .pptx")
    ap.add_argument("--mode", choices=("none", "elevenlabs", "recording"), default="none")
    ap.add_argument("--out", required=False, help="папка для timeline.json, captions.srt, audio/")
    ap.add_argument("--lang", default=None, choices=("ru", "ky", "en"))
    ap.add_argument("--voice", help="ID голоса ElevenLabs")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--recording", help="своя запись: файл или папка с файлом на слайд")
    ap.add_argument("--estimate", action="store_true", help="только оценить длительность и символы, без озвучки")
    a = ap.parse_args()
    try:
        deck = load_slides(a.slides)
        if a.estimate:
            print(estimate(deck, a.mode))
            return
        if a.mode != "none":
            ensure_tools(need_node=False, need_ffmpeg=True)
        out = Path(a.out or Path(a.slides).with_suffix("")).expanduser().resolve()
        out.mkdir(parents=True, exist_ok=True)
        tl = build_timeline(deck, a.mode, out, a.lang or deck["lang"] or "ru", a.voice, a.model,
                            Path(a.recording).expanduser().resolve() if a.recording else None)
    except DataError as e:
        fail(str(e))
    (out / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "captions.srt").write_text(to_srt(all_cues(tl)), encoding="utf-8")
    print(out / "timeline.json")


if __name__ == "__main__":
    main()
