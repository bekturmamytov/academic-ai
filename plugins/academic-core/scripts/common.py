"""Общий код скриптов academic-core: данные курса, профиль, бренд вуза, оформление docx.

Скрипты импортируют его так:
    sys.path.insert(0, str(Path(__file__).parent)); from common import ...
Зависимости (python-docx, pyyaml) объявляет сам скрипт в PEP 723.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

from i18n import t, tv

CREDIT_HOURS = 30
HOUR_KINDS = ("lectures", "practicals", "labs", "srsp", "srs")

# Windows: вывод в канал по умолчанию в cp1251 — печатаем всегда в UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


class DataError(Exception):
    """Ошибка в данных пользователя — печатается по-русски, без трейсбека."""


def fail(msg: str) -> None:
    print(f"Ошибка: {msg}", file=sys.stderr)
    sys.exit(1)


def read_yaml(path: Path) -> dict:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except FileNotFoundError:
        raise DataError(f"не найден файл {path}")
    except yaml.YAMLError as e:
        raise DataError(f"в {path.name} ошибка разметки YAML: {e}")


def find_up(start: Path, name: str) -> Path | None:
    """Ищет файл или папку name в start и выше по дереву (рабочая папка)."""
    for d in [start, *start.parents]:
        if (d / name).exists():
            return d / name
    return None


def load_course(course_yaml: str | Path) -> dict:
    """Паспорт курса + профиль + бренд вуза в одном словаре.

    Возвращает dict с ключами course-паспорта и служебными:
    _dir (папка курса), _profile, _brand, _brand_dir.
    """
    path = Path(course_yaml).expanduser().resolve()
    data = read_yaml(path)
    data["_dir"] = path.parent
    prof = find_up(path.parent, "profile.yaml")
    data["_profile"] = read_yaml(prof) if prof else {}
    uni = find_up(path.parent, "university")
    brand_file = uni / "brand.yaml" if uni else None
    data["_brand"] = read_yaml(brand_file) if brand_file and brand_file.exists() else {}
    data["_brand_dir"] = uni
    teacher = data.setdefault("teacher", {}) or {}
    for k in ("name", "degree", "position", "email"):
        if not teacher.get(k):
            teacher[k] = data["_profile"].get(k, "")
    data["teacher"] = teacher
    data.setdefault("language", data["_profile"].get("language", "ru"))
    return data


def check_hours(data: dict) -> list[str]:
    """Сверка часов: сумма видов = кредиты × 30, сумма по темам = итог по видам."""
    problems = []
    hours = data.get("hours", {}) or {}
    credits = data.get("credits")
    total = sum(int(hours.get(k, 0) or 0) for k in HOUR_KINDS)
    if credits and total != credits * CREDIT_HOURS:
        problems.append(
            f"часы по видам дают {total}, а {credits} кр. × {CREDIT_HOURS} = {credits * CREDIT_HOURS}"
        )
    topics = data.get("topics", []) or []
    kinds = ["lectures", "practicals", "labs", "srs"]
    if any("srsp" in tp for tp in topics):
        kinds.insert(3, "srsp")
    for k in kinds:
        if k in hours and topics:
            s = sum(int(tp.get(k, 0) or 0) for tp in topics)
            if s != int(hours[k] or 0):
                problems.append(f"{k}: по темам {s} ч, в паспорте {hours[k]} ч")
    weights = sum(int(a.get("weight", 0) or 0) for a in data.get("assessment", []) or [])
    if data.get("assessment") and weights != 100:
        problems.append(f"веса оценивания дают {weights}, а нужно 100")
    return problems


def university_name(data: dict, lang: str) -> str:
    b = data.get("_brand", {})
    key = {"ru": "name", "ky": "name_ky", "en": "name_en"}[lang]
    return b.get(key) or b.get("name") or data.get("_profile", {}).get("university", "")


def loc(obj: dict, key: str, lang: str, data: dict | None = None):
    """Поле на языке lang: key_<lang>, иначе key (язык паспорта).

    Если язык документа не совпадает с языком паспорта и перевода нет —
    запоминает поле в data["_missing_tr"], чтобы скрипт предупредил.
    """
    if not isinstance(obj, dict):
        return obj
    base = (data or {}).get("language", "ru")
    if lang != base:
        v = obj.get(f"{key}_{lang}")
        if v:
            return v
        if obj.get(key) and data is not None:
            data.setdefault("_missing_tr", set()).add(key)
    return obj.get(key)


def course_title(data: dict, lang: str) -> str:
    c = data.get("course", {})
    return c.get(f"title_{lang}") or c.get("title", "")


def out_dir(data: dict) -> Path:
    d = data["_dir"] / (data.get("files", {}) or {}).get("out", "out")
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------- docx по ГОСТ ----------

def new_document():
    """Пустой docx: Times New Roman 14, интервал 1,5, поля 30/15/20/20, номера страниц."""
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt

    doc = Document()
    for s in doc.sections:
        s.left_margin, s.right_margin = Cm(3), Cm(1.5)
        s.top_margin, s.bottom_margin = Cm(2), Cm(2)
        p = s.footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # поле PAGE: begin, код, separate, текущее значение, end — каждое в своём run
        for kind, text in (("begin", None), (None, "PAGE"), ("separate", None), ("value", "1"), ("end", None)):
            run = p.add_run("1" if kind == "value" else None)
            if kind in ("begin", "separate", "end"):
                el = OxmlElement("w:fldChar")
                el.set(qn("w:fldCharType"), kind)
                run._r.append(el)
            elif kind is None:
                el = OxmlElement("w:instrText")
                el.set(qn("xml:space"), "preserve")
                el.text = text
                run._r.append(el)

    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(14)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        st.element.rPr.rFonts.attrib.pop(qn(attr), None)
    pf = st.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(0)
    pf.first_line_indent = Cm(1.25)
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for lvl, size in ((1, 14), (2, 14), (3, 14)):
        h = doc.styles[f"Heading {lvl}"]
        h.font.name = "Times New Roman"
        h.font.size = Pt(size)
        h.font.bold = True
        h.font.color.rgb = None
        rf = h.element.rPr.rFonts
        rf.set(qn("w:eastAsia"), "Times New Roman")
        for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            rf.attrib.pop(qn(attr), None)  # иначе Word/LibreOffice берут шрифт темы (Calibri Light)
        h.paragraph_format.first_line_indent = Cm(0)
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.alignment = (
            WD_ALIGN_PARAGRAPH.CENTER if lvl == 1 else WD_ALIGN_PARAGRAPH.LEFT
        )
        h.paragraph_format.keep_with_next = True
    return doc


def para(doc, text: str = "", *, bold=False, italic=False, align=None, indent=True, size=None):
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Cm, Pt

    p = doc.add_paragraph()
    if text:
        r = p.add_run(text)
        r.bold, r.italic = bold, italic
        if size:
            r.font.size = Pt(size)
    if align:
        p.alignment = {"center": WD_ALIGN_PARAGRAPH.CENTER, "right": WD_ALIGN_PARAGRAPH.RIGHT,
                       "left": WD_ALIGN_PARAGRAPH.LEFT}[align]
    if not indent or align:
        p.paragraph_format.first_line_indent = Cm(0)
    return p


def table(doc, header: list[str], rows: list[list], widths_cm: list[float] | None = None):
    """Таблица 12 pt, интервал 1,0, шапка жирная, текст в ячейках — влево."""
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Cm, Pt

    tbl = doc.add_table(rows=1, cols=len(header))
    tbl.style = "Table Grid"
    for i, h in enumerate(header):
        tbl.rows[0].cells[i].text = str(h)
    for row in rows:
        cells = tbl.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = "" if v is None else str(v)
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    hdr = OxmlElement("w:tblHeader")  # шапка повторяется на каждой странице
    hdr.set(qn("w:val"), "true")
    tbl.rows[0]._tr.get_or_add_trPr().append(hdr)
    if widths_cm:
        tbl.autofit = False  # без этого Word и LibreOffice делят ширину поровну
        for ci, col in enumerate(tbl.columns):
            col.width = Cm(widths_cm[ci])
    for ri, r in enumerate(tbl.rows):
        r._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))  # строка не рвётся между страницами
        for ci, c in enumerate(r.cells):
            if widths_cm:
                c.width = Cm(widths_cm[ci])
            for p in c.paragraphs:
                p.paragraph_format.first_line_indent = Cm(0)
                p.paragraph_format.line_spacing = 1.0
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for run in p.runs:
                    run.font.size = Pt(12)
                    run.bold = ri == 0
    doc.add_paragraph()
    return tbl


def title_page(doc, data: dict, lang: str, doc_title: str, *, approve: bool = True):
    """Титульный лист: министерство, вуз, кафедра, «УТВЕРЖДАЮ», название, город, год."""
    from docx.enum.text import WD_BREAK
    from docx.shared import Cm

    prof = data.get("_profile", {})
    logo = data.get("_brand", {}).get("logo")
    has_logo = bool(logo and data.get("_brand_dir") and (data["_brand_dir"] / logo).exists())
    if has_logo:
        doc.add_picture(str(data["_brand_dir"] / logo), width=Cm(3))
        doc.paragraphs[-1].alignment = 1

    def gap(n: int) -> None:
        """Пустые строки титула — одинарным интервалом; с логотипом их меньше, чтобы титул влез на лист."""
        for _ in range(max(1, n // 2) if has_logo else n):
            para(doc).paragraph_format.line_spacing = 1.0
    para(doc, t("ministry", lang), align="center")
    para(doc, university_name(data, lang), bold=True, align="center")
    if prof.get("faculty"):
        para(doc, prof["faculty"], align="center")
    if prof.get("department"):
        para(doc, f'{t("department", lang)} «{prof["department"]}»', align="center")
    para(doc)
    if approve:
        for line in (t("approve", lang), t("approve_role", lang), "________________________",
                     f'«___» ____________ {str(data.get("course", {}).get("academic_year", ""))[:4]} г.'):
            para(doc, line, align="right")
    gap(4)
    para(doc, doc_title.upper(), bold=True, align="center")
    para(doc, f'{t("discipline", lang)}: «{course_title(data, lang)}»', bold=True, align="center")
    c = data.get("course", {})
    meta = [c.get("program"), f'{tv(c.get("level", ""), lang)}, {t("course_year", lang)} {c.get("year", "")}, '
            f'{t("semester", lang)} {c.get("semester", "")}', f'{t("credits", lang)}: {data.get("credits", "")}']
    for m in meta:
        if m:
            para(doc, m, align="center")
    gap(6)
    city = prof.get("city", "")
    para(doc, f'{city} {str(c.get("academic_year", ""))[:4]}'.strip(), align="center")
    doc.paragraphs[-1].runs[-1].add_break(WD_BREAK.PAGE)
