# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Состояние работы по главам: статус, объём, ссылки, метки «нужны данные» / «нужен источник».

    uv run status.py "<папка работы>/work.yaml"
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import DataError, fail, load_sources, load_work, thesis_pages, utf8_stdout  # noqa: E402

CITE = re.compile(r"\[(@[^\]]+)\]")
KEY = re.compile(r"@([\w:.\-]+)")


def main() -> None:
    utf8_stdout()
    ap = argparse.ArgumentParser(description="Состояние научной работы")
    ap.add_argument("work")
    args = ap.parse_args()
    try:
        w = load_work(args.work)
    except DataError as e:
        fail(str(e))
    sources = {s.get("key"): s for s in load_sources(w)}
    rows, total_words = [], 0
    unknown, unverified = set(), set()
    for item in w.get("structure") or []:
        f = w["_dir"] / item["file"] if item.get("file") else None
        text = f.read_text(encoding="utf-8") if f and f.exists() else ""
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        words = len(re.sub(r"[#*|\[\]@]", " ", text).split())
        total_words += words
        keys = [k for m in CITE.finditer(text) for k in KEY.findall(m.group(1))]
        for k in keys:
            if k not in sources:
                unknown.add(k)
            elif sources[k].get("verified") is not True:
                unverified.add(k)
        rows.append((item.get("title") or item.get("kind"), item.get("status", "plan"),
                     words, len(keys), len(re.findall(r"\[НУЖНЫ ВАШИ ДАННЫЕ", text, re.I)),
                     len(re.findall(r"\[НУЖЕН ИСТОЧНИК", text, re.I)), "" if text else "нет файла"))
    print(f"{w.get('title', '')} ({w['type']})\n")
    print(f"{'Раздел':42} {'статус':8} {'слов':>6} {'ссылок':>6} {'данные':>6} {'источн.':>7}")
    for r in rows:
        print(f"{str(r[0])[:42]:42} {r[1]:8} {r[2]:>6} {r[3]:>6} {r[4]:>6} {r[5]:>7} {r[6]}")
    ok = sum(1 for s in sources.values() if s.get("verified") is True)
    pages = round(total_words / 300)
    print(f"\nВсего ≈ {total_words} слов (≈ {pages} стр.). "
          f"Литература: проверено {ok} из {len(sources)}.")
    norm = thesis_pages(w)
    if norm:
        note = "" if norm[0] <= pages <= norm[1] else (" — меньше нормы" if pages < norm[0] else " — больше нормы")
        print(f"Объём по требованиям вуза: {norm[0]}–{norm[1]} стр. (university/settings.yaml){note}")
    if unverified:
        print(f"Ссылки на непроверенные: {', '.join(sorted(unverified))}")
    if unknown:
        print(f"Ссылки на ключи, которых нет в sources.yaml: {', '.join(sorted(unknown))}")


if __name__ == "__main__":
    main()
