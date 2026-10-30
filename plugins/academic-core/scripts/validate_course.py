# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Проверка паспорта курса: часы = кредиты × 30, темы, РО по Блуму, оценивание = 100.

    uv run validate_course.py "<папка курса>/course.yaml"

Печатает ошибки и предупреждения списком; код возврата 1, если есть ошибки.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import DataError, fail, load_course  # noqa: E402
from course_check import report, validate_course  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="Проверка course.yaml")
    ap.add_argument("course", help="путь к course.yaml")
    args = ap.parse_args()
    try:
        data = load_course(args.course)
    except DataError as e:
        fail(str(e))
    errors, warnings = validate_course(data)
    report(errors, warnings)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
