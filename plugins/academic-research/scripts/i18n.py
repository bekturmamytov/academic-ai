"""Подписи научных документов на ru / ky / en. Ключ отсутствует в языке — берётся ru.

Кыргызские формулировки проверить носителем и по образцам НАК КР / вуза.
"""
LABELS: dict[str, dict[str, str]] = {
    "ministry": {
        "ru": "Министерство науки, высшего образования и инноваций Кыргызской Республики",
        "ky": "Кыргыз Республикасынын Илим, жогорку билим берүү жана инновациялар министрлиги",
        "en": "Ministry of Science, Higher Education and Innovation of the Kyrgyz Republic",
    },
    "department": {"ru": "Кафедра", "ky": "Кафедра", "en": "Department of"},
    "faculty": {"ru": "", "ky": "", "en": ""},
    "label_referat": {"ru": "РЕФЕРАТ", "ky": "РЕФЕРАТ", "en": "ESSAY"},
    "label_doklad": {"ru": "ДОКЛАД", "ky": "БАЯНДАМА", "en": "REPORT"},
    "label_kursovaya": {"ru": "КУРСОВАЯ РАБОТА", "ky": "КУРСТУК ИШ", "en": "COURSE PAPER"},
    "label_diplom": {"ru": "ВЫПУСКНАЯ КВАЛИФИКАЦИОННАЯ РАБОТА", "ky": "БҮТҮРҮҮ КВАЛИФИКАЦИЯЛЫК ИШИ",
                     "en": "GRADUATION THESIS"},
    "label_magistr": {"ru": "МАГИСТЕРСКАЯ ДИССЕРТАЦИЯ", "ky": "МАГИСТРДИК ДИССЕРТАЦИЯ",
                      "en": "MASTER'S THESIS"},
    "label_kandidat": {
        "ru": "Диссертация на соискание ученой степени кандидата {science}",
        "ky": "{science} илимдеринин кандидаты илимий даражасын изденип алуу үчүн диссертация",
        "en": "Dissertation for the degree of Candidate of {science}",
    },
    "label_avtoreferat": {
        "ru": "АВТОРЕФЕРАТ\nдиссертации на соискание ученой степени кандидата {science}",
        "ky": "{science} илимдеринин кандидаты илимий даражасын изденип алуу үчүн жазылган "
              "диссертациянын\nАВТОРЕФЕРАТЫ",
        "en": "ABSTRACT\nof the dissertation for the degree of Candidate of {science}",
    },
    "manuscript": {"ru": "На правах рукописи", "ky": "Кол жазма укугунда", "en": "As a manuscript"},
    "udc": {"ru": "УДК", "ky": "УДК", "en": "UDC"},
    "discipline": {"ru": "по дисциплине", "ky": "сабак боюнча", "en": "Course"},
    "on_topic": {"ru": "на тему", "ky": "темасы", "en": "Topic"},
    "program": {"ru": "Направление", "ky": "Багыт", "en": "Programme"},
    "specialty": {"ru": "Специальность", "ky": "Адистик", "en": "Specialty"},
    "author": {"ru": "Выполнил(а)", "ky": "Аткарган", "en": "Author"},
    "supervisor": {"ru": "Научный руководитель", "ky": "Илимий жетекчи", "en": "Supervisor"},
    "supervisor_short": {"ru": "Руководитель", "ky": "Жетекчи", "en": "Supervisor"},
    "consultant": {"ru": "Научный консультант", "ky": "Илимий консультант", "en": "Scientific consultant"},
    "admit": {"ru": "Допустить к защите", "ky": "Коргоого жиберилсин", "en": "Admitted to defence"},
    "head": {"ru": "Заведующий кафедрой", "ky": "Кафедра башчысы", "en": "Head of Department"},
    "toc": {"ru": "СОДЕРЖАНИЕ", "ky": "МАЗМУНУ", "en": "CONTENTS"},
    "toc_diss": {"ru": "ОГЛАВЛЕНИЕ", "ky": "МАЗМУНУ", "en": "CONTENTS"},
    "toc_hint": {
        "ru": "Оглавление появится после обновления поля: правый щелчок → «Обновить поле» (или F9).",
        "ky": "Мазмуну талааны жаңырткандан кийин чыгат: оң баскыч → «Талааны жаңыртуу» (же F9).",
        "en": "Right-click → Update Field (or F9) to build the table of contents.",
    },
    "intro": {"ru": "ВВЕДЕНИЕ", "ky": "КИРИШҮҮ", "en": "INTRODUCTION"},
    "conclusion": {"ru": "ЗАКЛЮЧЕНИЕ", "ky": "КОРУТУНДУ", "en": "CONCLUSION"},
    "chapter": {"ru": "ГЛАВА", "ky": "БАП", "en": "CHAPTER"},
    "appendix": {"ru": "ПРИЛОЖЕНИЕ", "ky": "ТИРКЕМЕ", "en": "APPENDIX"},
    "bibliography": {"ru": "СПИСОК ИСПОЛЬЗОВАННОЙ ЛИТЕРАТУРЫ",
                     "ky": "ПАЙДАЛАНЫЛГАН АДАБИЯТТАРДЫН ТИЗМЕСИ", "en": "REFERENCES"},
    "bibliography_short": {"ru": "Список литературы", "ky": "Адабияттар", "en": "References"},
    "publications": {"ru": "СПИСОК ОПУБЛИКОВАННЫХ РАБОТ ПО ТЕМЕ ДИССЕРТАЦИИ",
                     "ky": "ДИССЕРТАЦИЯНЫН ТЕМАСЫ БОЮНЧА ЖАРЫЯЛАНГАН ЭМГЕКТЕРДИН ТИЗМЕСИ",
                     "en": "LIST OF PUBLICATIONS ON THE DISSERTATION TOPIC"},
    "summary": {"ru": "РЕЗЮМЕ", "ky": "РЕЗЮМЕ", "en": "SUMMARY"},
    "figure": {"ru": "Рисунок", "ky": "Сүрөт", "en": "Figure"},
    "table": {"ru": "Таблица", "ky": "Таблица", "en": "Table"},
    "abstract": {"ru": "Аннотация", "ky": "Аннотация", "en": "Abstract"},
    "keywords": {"ru": "Ключевые слова", "ky": "Негизги сөздөр", "en": "Keywords"},
    "ai_title": {"ru": "Использование инструментов искусственного интеллекта",
                 "ky": "Жасалма интеллект куралдарын колдонуу",
                 "en": "Use of artificial intelligence tools"},
    "ai_default": {
        "ru": "При подготовке работы использовался инструмент {tools}: {how}. "
              "Все данные, результаты и выводы получены и проверены автором.",
        "ky": "Ишти даярдоодо {tools} куралы колдонулду: {how}. "
              "Бардык маалыматтар, натыйжалар жана жыйынтыктар автор тарабынан алынып, текшерилди.",
        "en": "{tools} was used in preparing this work for: {how}. "
              "All data, results and conclusions were obtained and verified by the author.",
    },
    "executed_at": {"ru": "Работа выполнена в", "ky": "Иш аткарылган жер:", "en": "The work was carried out at"},
    "opponents": {"ru": "Официальные оппоненты:", "ky": "Расмий оппоненттер:", "en": "Official opponents:"},
    "lead_org": {"ru": "Ведущая организация:", "ky": "Жетектөөчү мекеме:", "en": "Leading organization:"},
    "defense": {
        "ru": "Защита состоится {date} на заседании диссертационного совета {council} при {org} по адресу: {address}.",
        "ky": "Коргоо {date} {org} алдындагы {council} диссертациялык кеңешинин отурумунда болот. Дареги: {address}.",
        "en": "The defence will take place on {date} at the meeting of dissertation council {council} at {org}, {address}.",
    },
    "library": {"ru": "С диссертацией можно ознакомиться в библиотеке {org}.",
                "ky": "Диссертация менен {org} китепканасынан таанышууга болот.",
                "en": "The dissertation is available in the library of {org}."},
    "sent_out": {"ru": "Автореферат разослан «___» ____________ 20___ г.",
                 "ky": "Авторефераты 20___ ж. «___» ____________ таратылды.",
                 "en": "The abstract was distributed on «___» ____________ 20___."},
    "secretary": {"ru": "Ученый секретарь диссертационного совета",
                  "ky": "Диссертациялык кеңештин окумуштуу катчысы",
                  "en": "Scientific secretary of the dissertation council"},
    "blank": {"ru": "________________________", "ky": "________________________", "en": "________________________"},
    "unverified": {"ru": "[НЕ ПРОВЕРЕНО]", "ky": "[ТЕКШЕРИЛГЕН ЭМЕС]", "en": "[UNVERIFIED]"},
    "et_al": {"ru": "и др.", "ky": "ж. б.", "en": "et al."},
    "page_abbr": {"ru": "с.", "ky": "б.", "en": "p."},
}


def t(key: str, lang: str = "ru", **kw) -> str:
    entry = LABELS.get(key)
    if not entry:
        return key
    s = entry.get(lang) or entry["ru"]
    return s.format(**kw) if kw else s
