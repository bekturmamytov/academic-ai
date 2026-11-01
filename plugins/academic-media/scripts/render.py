# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6", "python-pptx>=1.0"]
# ///
"""Видео-лекция из слайдов: озвучка → нарезка на части → Remotion → out/video/NN-partK.mp4 + .srt.

    uv run render.py <slides.yaml|.pptx> --mode none|elevenlabs|recording
        [--lang ru] [--voice ID] [--recording <файл или папка>] [--out <папка>]
        [--max-min 15] [--single] [--no-captions] [--only-part K] [--check]

--check только проверяет Node 20+, ffmpeg и движок видео. Первый запуск копирует
движок (Remotion) в ~/.academic/remotion и ставит его зависимости — нужен интернет, 1–3 минуты.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from common import DataError, academic_home, ensure_tools, fail, get_setting, load_slides, media_duration, t
from narrate import build_timeline, estimate, to_srt

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REMOTION_SRC = PLUGIN_ROOT / "remotion"
FPS = 30
INTRO = 5.0
OUTRO = 4.0


# ---------- части ----------

def groups_by_section(slides: list[dict]) -> list[list[int]]:
    """Индексы слайдов по разделам: новый раздел — со слайда section; title и closing — к соседям."""
    groups: list[list[int]] = [[]]
    for i, s in enumerate(slides):
        if s["type"] == "section" and any(slides[j]["type"] != "title" for j in groups[-1]):
            groups.append([])
        groups[-1].append(i)
    if len(groups) > 1 and all(slides[j]["type"] == "closing" for j in groups[-1]):
        groups[-2] += groups.pop()
    return [g for g in groups if g]


def split_parts(slides: list[dict], durations: list[float], max_sec: float = 15 * 60) -> list[list[int]]:
    """Части до max_sec: целые разделы подряд; раздел длиннее max_sec — на равные куски по слайдам.
    Часть короче 8 мин бывает, только когда короток сам раздел или остаток лекции."""
    if sum(durations) <= max_sec:
        return [list(range(len(slides)))]
    dur = lambda idx: sum(durations[i] for i in idx)
    units: list[list[int]] = []
    for g in groups_by_section(slides):
        if dur(g) <= max_sec:
            units.append(g)
            continue
        k = math.ceil(dur(g) / max_sec)
        target = dur(g) / k
        chunks: list[list[int]] = [[]]
        for i in g:
            cur = dur(chunks[-1])
            if chunks[-1] and len(chunks) < k and abs(cur + durations[i] - target) > abs(cur - target):
                chunks.append([])
            chunks[-1].append(i)
        units += chunks
    parts: list[list[int]] = []
    for u in units:
        if parts and dur(parts[-1]) + dur(u) <= max_sec:
            parts[-1] += u
        else:
            parts.append(list(u))
    return parts


def part_props(deck: dict, tl: dict, idx: list[int], k: int, n: int, lang: str) -> dict:
    items = [tl["slides"][i] for i in idx]
    base = items[0]["start"]
    sections = [deck["slides"][i]["title"] for i in idx if deck["slides"][i]["type"] == "section"]
    slides, cues = [], []
    for i, it in zip(idx, items):
        s = deck["slides"][i]
        start = INTRO + it["start"] - base
        slides.append({
            "n": s["n"], "type": s["type"], "title": s["title"], "subtitle": s["subtitle"],
            "bullets": s["bullets"], "table": s["table"],
            "start": round(start, 3), "duration": it["duration"],
            "audio": it["audio"], "audioOffset": it["audio_offset"], "reveal": it["reveal"],
        })
        cues += [{"start": round(c["start"] - base + INTRO, 3), "end": round(c["end"] - base + INTRO, 3),
                  "text": c["text"]} for c in it["cues"]]
    body = sum(it["duration"] for it in items)
    total = INTRO + body + OUTRO
    return {
        "meta": {
            "title": deck["title"], "course": deck["course"], "teacher": deck["teacher"],
            "accent": deck["accent"], "lang": lang,
            "partLabel": t("part", lang, k=k, n=n) if n > 1 else "",
            "topic": " · ".join(sections[:2]) if n > 1 else "",
            "sectionLabel": t("section", lang), "endLabel": t("end", lang),
            "slideCount": len(deck["slides"]),
        },
        "intro": INTRO, "outro": OUTRO, "slides": slides, "cues": cues,
        "totalFrames": int(round(total * FPS)),
    }, cues


# ---------- Remotion ----------

def _hash_dir(d: Path) -> str:
    h = hashlib.sha1()
    for f in sorted(p for p in d.rglob("*") if p.is_file() and "node_modules" not in p.parts):
        h.update(f.relative_to(d).as_posix().encode())
        h.update(f.read_bytes())
    return h.hexdigest()[:12]


def ensure_engine() -> Path:
    """Копия remotion/ в ~/.academic/remotion; npm install — только если сменился package.json."""
    dest = academic_home() / "remotion"
    stamp = dest / ".installed"
    pkg_hash = hashlib.sha1((REMOTION_SRC / "package.json").read_bytes()).hexdigest()[:12]
    src_hash = _hash_dir(REMOTION_SRC)
    marker = dest / ".src"
    if not marker.exists() or marker.read_text(encoding="utf-8").strip() != src_hash:
        dest.mkdir(parents=True, exist_ok=True)
        for item in REMOTION_SRC.iterdir():
            if item.name in ("node_modules", "out"):
                continue
            target = dest / item.name
            if item.is_dir():
                shutil.rmtree(target, ignore_errors=True)
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)
        marker.write_text(src_hash, encoding="utf-8")
    if not (dest / "node_modules").exists() or not stamp.exists() or stamp.read_text().strip() != pkg_hash:
        print("Ставлю движок видео (Remotion) — первый раз 1–3 минуты…", file=sys.stderr)
        r = subprocess.run([shutil.which("npm") or "npm", "install", "--no-audit", "--no-fund", "--loglevel=error"],
                           cwd=dest)
        if r.returncode != 0:
            raise DataError("не удалось установить движок видео (npm install). Проверьте интернет и "
                            "повторите; если не поможет — /academic:setup.")
        stamp.write_text(pkg_hash, encoding="utf-8")
    return dest


def remotion_render(engine: Path, props: Path, public_dir: Path, out_mp4: Path) -> None:
    cmd = [shutil.which("npx") or "npx", "remotion", "render", "src/index.ts", "LectureVideo", str(out_mp4),
           f"--props={props}", f"--public-dir={public_dir}", "--log=error"]
    r = subprocess.run(cmd, cwd=engine)
    if r.returncode != 0:
        raise DataError(f"движок видео завершился с ошибкой при сборке {out_mp4.name}. "
                        "Текст ошибки — выше; пришлите его в поддержку или запустите /academic:setup.")


def default_out(src: Path) -> Path:
    if src.parent.name == "slides" and src.parent.parent.name == "out":
        return src.parent.parent / "video"
    return src.parent / "out" / "video"


def main() -> None:
    ap = argparse.ArgumentParser(description="Видео-лекция из слайдов")
    ap.add_argument("slides", nargs="?", help="slides.yaml или .pptx")
    ap.add_argument("--mode", choices=("none", "elevenlabs", "recording"), default="none")
    ap.add_argument("--lang", choices=("ru", "ky", "en"))
    ap.add_argument("--voice", help="ID голоса ElevenLabs")
    ap.add_argument("--model", default="eleven_v3")
    ap.add_argument("--recording", help="своя запись: файл или папка с файлом на слайд")
    ap.add_argument("--out", help="папка для mp4 и srt (по умолчанию out/video рядом)")
    ap.add_argument("--max-min", type=float, default=15)
    ap.add_argument("--single", action="store_true", help="одним роликом, без нарезки")
    ap.add_argument("--no-captions", action="store_true", help="без титров в кадре и без .srt")
    ap.add_argument("--only-part", type=int, help="собрать только часть K")
    ap.add_argument("--estimate", action="store_true", help="оценить длительность и символы ElevenLabs")
    ap.add_argument("--check", action="store_true", help="проверить окружение и движок видео")
    a = ap.parse_args()

    if a.check:
        ensure_tools(need_node=True, need_ffmpeg=True)
        try:
            ensure_engine()
        except DataError as e:
            fail(str(e))
        print("Окружение для видео готово: Node.js, ffmpeg, движок Remotion.")
        print("Ключ ElevenLabs: " + ("найден (проверить — key.py --check)" if get_setting("ELEVENLABS_API_KEY")
                                    else "не найден (создать файл для ключа — key.py --open)"))
        return
    if not a.slides:
        fail("укажите файл слайдов: slides.yaml или .pptx")
    if a.mode == "none" and a.no_captions:
        fail("без голоса титры обязательны — уберите --no-captions или выберите голос")

    src = Path(a.slides).expanduser().resolve()
    try:
        deck = load_slides(src)
        if a.estimate:
            print(estimate(deck, a.mode))
            return
        ensure_tools(need_node=True, need_ffmpeg=a.mode != "none")
        lang = a.lang or deck["lang"] or "ru"
        out = Path(a.out).expanduser().resolve() if a.out else default_out(src)
        build = out / ".build" / src.stem
        build.mkdir(parents=True, exist_ok=True)
        tl = build_timeline(deck, a.mode, build, lang, a.voice, a.model,
                            Path(a.recording).expanduser().resolve() if a.recording else None)
        (build / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")

        durations = [s["duration"] for s in tl["slides"]]
        parts = [list(range(len(durations)))] if a.single else \
            split_parts(deck["slides"], durations, a.max_min * 60)
        engine = ensure_engine()
        made = []
        for k, idx in enumerate(parts, 1):
            if a.only_part and k != a.only_part:
                continue
            props, cues = part_props(deck, tl, idx, k, len(parts), lang)
            if a.no_captions:
                props["cues"] = []
            pfile = build / f"part{k}.json"
            pfile.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
            mp4 = out / f"{src.stem}-part{k}.mp4"
            print(f"Собираю часть {k} из {len(parts)} (слайды {idx[0] + 1}–{idx[-1] + 1})…", file=sys.stderr)
            remotion_render(engine, pfile, build, mp4)
            if not a.no_captions:
                (out / f"{src.stem}-part{k}.srt").write_text(to_srt(cues), encoding="utf-8")
            made.append(mp4)
    except DataError as e:
        fail(str(e))
    for mp4 in made:
        dur = media_duration(mp4) if shutil.which("ffprobe") else 0
        print(f"{mp4}  ({dur / 60:.1f} мин)" if dur else mp4)


if __name__ == "__main__":
    main()
