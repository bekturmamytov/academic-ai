"""Подписи документов на ru / ky / en. Ключ отсутствует в языке — берётся ru.

Скрипт может дополнить словарь своими метками: LABELS.update({...}) у себя.
Кыргызские формулировки проверить носителем (термины Минобрнауки КР).
"""
LABELS: dict[str, dict[str, str]] = {
    "ministry": {
        "ru": "Министерство науки, высшего образования и инноваций Кыргызской Республики",
        "ky": "Кыргыз Республикасынын Илим, жогорку билим берүү жана инновациялар министрлиги",
        "en": "Ministry of Science, Higher Education and Innovation of the Kyrgyz Republic",
    },
    "department": {"ru": "Кафедра", "ky": "Кафедра", "en": "Department of"},
    "approve": {"ru": "«УТВЕРЖДАЮ»", "ky": "«БЕКИТЕМИН»", "en": "APPROVED"},
    "approve_role": {"ru": "Заведующий кафедрой", "ky": "Кафедра башчысы", "en": "Head of Department"},
    "agreed": {"ru": "«СОГЛАСОВАНО»", "ky": "«МАКУЛДАШЫЛДЫ»", "en": "AGREED"},
    "discipline": {"ru": "по дисциплине", "ky": "сабак боюнча", "en": "course"},
    "course_year": {"ru": "курс", "ky": "курс", "en": "year"},
    "semester": {"ru": "семестр", "ky": "семестр", "en": "semester"},
    "credits": {"ru": "Кредиты", "ky": "Кредиттер", "en": "Credits"},
    "hours": {"ru": "Часы", "ky": "Сааттар", "en": "Hours"},
    "week": {"ru": "Неделя", "ky": "Апта", "en": "Week"},
    "topic": {"ru": "Тема", "ky": "Тема", "en": "Topic"},
    "lectures": {"ru": "Лекции", "ky": "Лекциялар", "en": "Lectures"},
    "practicals": {"ru": "Практические", "ky": "Практикалык", "en": "Seminars"},
    "labs": {"ru": "Лабораторные", "ky": "Лабораториялык", "en": "Labs"},
    "srsp": {"ru": "СРСП", "ky": "ОӨИ (окутуучу менен)", "en": "Guided self-study"},
    "srs": {"ru": "СРС", "ky": "СӨИ", "en": "Self-study"},
    "total": {"ru": "Итого", "ky": "Бардыгы", "en": "Total"},
    "outcomes": {"ru": "Результаты обучения", "ky": "Окутуунун натыйжалары", "en": "Learning outcomes"},
    "literature": {"ru": "Литература", "ky": "Адабияттар", "en": "References"},
    "main_lit": {"ru": "Основная", "ky": "Негизги", "en": "Core"},
    "extra_lit": {"ru": "Дополнительная", "ky": "Кошумча", "en": "Further reading"},
    "online_lit": {"ru": "Интернет-ресурсы", "ky": "Интернет-ресурстар", "en": "Online resources"},
    "teacher": {"ru": "Преподаватель", "ky": "Окутуучу", "en": "Instructor"},
    "assessment": {"ru": "Оценивание", "ky": "Баалоо", "en": "Assessment"},
    "unverified": {"ru": "[НЕ ПРОВЕРЕНО]", "ky": "[ТЕКШЕРИЛГЕН ЭМЕС]", "en": "[UNVERIFIED]"},
}


def t(key: str, lang: str = "ru") -> str:
    entry = LABELS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry["ru"]


# ---------- силлабус, РУП, тесты (academic-core) ----------

LABELS.update({
    "syllabus": {"ru": "Силлабус", "ky": "Силлабус", "en": "Syllabus"},
    "rup": {"ru": "Рабочая программа дисциплины", "ky": "Сабактын жумушчу программасы",
            "en": "Course work programme"},
    "sec_teacher": {"ru": "Сведения о преподавателе", "ky": "Окутуучу жөнүндө маалымат",
                    "en": "Instructor information"},
    "sec_course": {"ru": "Сведения о дисциплине", "ky": "Сабак жөнүндө маалымат", "en": "Course information"},
    "sec_description": {"ru": "Описание дисциплины", "ky": "Сабактын сүрөттөмөсү", "en": "Course description"},
    "sec_goals": {"ru": "Цели и задачи дисциплины", "ky": "Сабактын максаттары жана милдеттери",
                  "en": "Course aims and objectives"},
    "sec_prereq": {"ru": "Пререквизиты и постреквизиты", "ky": "Пререквизиттер жана постреквизиттер",
                   "en": "Prerequisites and follow-up courses"},
    "sec_outcomes": {"ru": "Результаты обучения и компетенции", "ky": "Окутуунун натыйжалары жана компетенциялар",
                     "en": "Learning outcomes and competencies"},
    "sec_sdg_methods": {"ru": "Цели устойчивого развития и методы обучения",
                        "ky": "Туруктуу өнүгүү максаттары жана окутуу ыкмалары",
                        "en": "Sustainable Development Goals and teaching methods"},
    "sec_plan": {"ru": "Тематический план", "ky": "Тематикалык план", "en": "Course schedule"},
    "sec_srs": {"ru": "Задания для самостоятельной работы студентов",
                "ky": "Студенттердин өз алдынча иштөөсү үчүн тапшырмалар", "en": "Self-study assignments"},
    "sec_assessment": {"ru": "Оценивание: балльно-рейтинговая система",
                       "ky": "Баалоо: балл-рейтингдик система", "en": "Assessment: point-rating system"},
    "sec_scale": {"ru": "Шкала оценок", "ky": "Баалоо шкаласы", "en": "Grading scale"},
    "sec_policy": {"ru": "Политика курса", "ky": "Курстун саясаты", "en": "Course policy"},
    "sec_signatures": {"ru": "Согласование", "ky": "Макулдашуу", "en": "Approval"},
    "sec_place": {"ru": "Место дисциплины в структуре ООП", "ky": "Сабактын НББПдагы орду",
                  "en": "Place of the course in the curriculum"},
    "sec_volume": {"ru": "Объём дисциплины и виды учебной работы", "ky": "Сабактын көлөмү жана окуу иштеринин түрлөрү",
                   "en": "Course workload"},
    "sec_content": {"ru": "Содержание дисциплины по темам", "ky": "Темалар боюнча сабактын мазмуну",
                    "en": "Course content by topic"},
    "sec_support": {"ru": "Учебно-методическое обеспечение самостоятельной работы",
                    "ky": "Өз алдынча иштин окуу-методикалык камсыздоосу",
                    "en": "Teaching materials for self-study"},
    "sec_assess_tools": {"ru": "Оценочные средства", "ky": "Баалоо каражаттары", "en": "Assessment tools"},
    "f_name": {"ru": "ФИО", "ky": "Аты-жөнү", "en": "Name"},
    "f_degree": {"ru": "Учёная степень, звание", "ky": "Илимий даражасы, наамы", "en": "Academic degree"},
    "f_position": {"ru": "Должность", "ky": "Кызматы", "en": "Position"},
    "f_email": {"ru": "Электронная почта", "ky": "Электрондук почта", "en": "E-mail"},
    "f_office_hours": {"ru": "Консультации", "ky": "Консультациялар", "en": "Office hours"},
    "f_code": {"ru": "Код дисциплины", "ky": "Сабактын коду", "en": "Course code"},
    "f_title": {"ru": "Название дисциплины", "ky": "Сабактын аталышы", "en": "Course title"},
    "f_type": {"ru": "Статус дисциплины", "ky": "Сабактын статусу", "en": "Course status"},
    "f_cycle": {"ru": "Цикл", "ky": "Цикл", "en": "Curriculum block"},
    "f_program": {"ru": "Направление подготовки", "ky": "Даярдоо багыты", "en": "Programme"},
    "f_level": {"ru": "Уровень образования", "ky": "Билим берүү деңгээли", "en": "Level"},
    "f_year_sem": {"ru": "Курс, семестр", "ky": "Курс, семестр", "en": "Year, semester"},
    "f_academic_year": {"ru": "Учебный год", "ky": "Окуу жылы", "en": "Academic year"},
    "f_form": {"ru": "Форма обучения", "ky": "Окутуу формасы", "en": "Mode of study"},
    "f_lang": {"ru": "Язык обучения", "ky": "Окутуу тили", "en": "Language of instruction"},
    "f_weeks": {"ru": "Количество недель", "ky": "Апталардын саны", "en": "Weeks"},
    "prerequisites": {"ru": "Пререквизиты", "ky": "Пререквизиттер", "en": "Prerequisites"},
    "postrequisites": {"ru": "Постреквизиты", "ky": "Постреквизиттер", "en": "Follow-up courses"},
    "competencies": {"ru": "Компетенции", "ky": "Компетенциялар", "en": "Competencies"},
    "sdg": {"ru": "Цели устойчивого развития ООН", "ky": "БУУнун Туруктуу өнүгүү максаттары",
            "en": "UN Sustainable Development Goals"},
    "sdg_short": {"ru": "ЦУР", "ky": "ТӨМ", "en": "SDG"},
    "methods": {"ru": "Методы обучения", "ky": "Окутуу ыкмалары", "en": "Teaching methods"},
    "code": {"ru": "Код", "ky": "Код", "en": "Code"},
    "outcome": {"ru": "Результат обучения", "ky": "Окутуунун натыйжасы", "en": "Learning outcome"},
    "bloom_level": {"ru": "Уровень по Блуму", "ky": "Блум боюнча деңгээл", "en": "Bloom level"},
    "topics_weeks": {"ru": "Недели", "ky": "Апталар", "en": "Weeks"},
    "all_hours": {"ru": "Всего часов", "ky": "Бардык сааттар", "en": "Total hours"},
    "contact_hours": {"ru": "Аудиторные", "ky": "Аудиториялык", "en": "Contact hours"},
    "self_hours": {"ru": "СРСП + СРС", "ky": "ОӨИ + СӨИ", "en": "Guided + independent study"},
    "a_lectures": {"ru": "Л", "ky": "Л", "en": "L"},
    "a_practicals": {"ru": "П", "ky": "П", "en": "S"},
    "a_labs": {"ru": "Лаб", "ky": "Лаб", "en": "Lab"},
    "a_srsp": {"ru": "СРСП", "ky": "ОӨИ", "en": "GS"},
    "a_srs": {"ru": "СРС", "ky": "СӨИ", "en": "SS"},
    "legend": {"ru": "Л — лекции, П — практические (семинарские) занятия, Лаб — лабораторные, "
                     "СРСП — самостоятельная работа под руководством преподавателя, СРС — самостоятельная работа студента.",
               "ky": "Л — лекциялар, П — практикалык (семинардык) сабактар, Лаб — лабораториялык сабактар, "
                     "ОӨИ — окутуучунун жетекчилиги астындагы өз алдынча иш, СӨИ — студенттин өз алдынча иши.",
               "en": "L — lectures, S — seminars, Lab — laboratory work, GS — guided self-study, SS — independent self-study."},
    "task": {"ru": "Задание", "ky": "Тапшырма", "en": "Assignment"},
    "report_form": {"ru": "Форма отчёта", "ky": "Отчет формасы", "en": "Deliverable"},
    "due": {"ru": "Срок сдачи (неделя)", "ky": "Тапшыруу мөөнөтү (апта)", "en": "Due (week)"},
    "control_kind": {"ru": "Вид контроля", "ky": "Көзөмөлдүн түрү", "en": "Assessment component"},
    "control_form": {"ru": "Форма контроля", "ky": "Көзөмөлдүн формасы", "en": "Format"},
    "points": {"ru": "Баллы", "ky": "Баллдар", "en": "Points"},
    "max_points": {"ru": "Макс. балл", "ky": "Макс. балл", "en": "Max points"},
    "session": {"ru": "Сессия", "ky": "Сессия", "en": "Exam period"},
    "whole_semester": {"ru": "в течение семестра", "ky": "семестр бою", "en": "throughout the semester"},
    "score_range": {"ru": "Сумма баллов", "ky": "Баллдардын суммасы", "en": "Score"},
    "letter": {"ru": "Буквенная оценка", "ky": "Тамга менен баа", "en": "Letter grade"},
    "traditional": {"ru": "Традиционная оценка", "ky": "Салттуу баа", "en": "Traditional grade"},
    "assess_note": {"ru": "Итоговая оценка — сумма баллов по всем видам контроля (максимум 100).",
                    "ky": "Жыйынтык баа — көзөмөлдүн бардык түрлөрү боюнча баллдардын суммасы (эң көбү 100).",
                    "en": "The final grade is the sum of points for all components (maximum 100)."},
    "p_attendance": {"ru": "Посещаемость", "ky": "Сабакка катышуу", "en": "Attendance"},
    "p_late_work": {"ru": "Сроки сдачи работ", "ky": "Иштерди тапшыруу мөөнөттөрү", "en": "Deadlines"},
    "p_academic_integrity": {"ru": "Академическая честность", "ky": "Академиялык чынчылдык",
                             "en": "Academic integrity"},
    "p_ai_use": {"ru": "Использование инструментов ИИ", "ky": "Жасалма интеллект куралдарын колдонуу",
                 "en": "Use of AI tools"},
    "p_extra": {"ru": "Дополнительно", "ky": "Кошумча", "en": "Other"},
    "compiler": {"ru": "Составитель", "ky": "Түзгөн", "en": "Prepared by"},
    "dept_meeting": {"ru": "Рассмотрен и одобрен на заседании кафедры", "ky": "Кафедранын жыйынында каралып, жактырылган",
                     "en": "Reviewed and approved at the meeting of the department"},
    "protocol": {"ru": "Протокол № ____ от «___» ____________ 20___ г.",
                 "ky": "№ ____ протокол, «___» ____________ 20___ ж.",
                 "en": "Minutes No. ____ dated ____________ 20___"},
    "signature": {"ru": "подпись", "ky": "колу", "en": "signature"},
    "no_data": {"ru": "—", "ky": "—", "en": "—"},
    "goals": {"ru": "Цели", "ky": "Максаттар", "en": "Aims"},
    "objectives": {"ru": "Задачи", "ky": "Милдеттер", "en": "Objectives"},
    "content": {"ru": "Содержание", "ky": "Мазмуну", "en": "Content"},
    "lab_work": {"ru": "Лабораторная работа", "ky": "Лабораториялык иш", "en": "Laboratory work"},
    "practical_work": {"ru": "Практическое занятие", "ky": "Практикалык сабак", "en": "Seminar"},
    "place_text": {"ru": "Дисциплина относится к циклу «{cycle}», статус — {type}.",
                   "ky": "Сабак «{cycle}» циклына кирет, статусу — {type}.",
                   "en": "The course belongs to the «{cycle}» block; status: {type}."},
    # тесты
    "test": {"ru": "Тест", "ky": "Тест", "en": "Test"},
    "variant": {"ru": "Вариант", "ky": "Вариант", "en": "Version"},
    "student": {"ru": "ФИО студента", "ky": "Студенттин аты-жөнү", "en": "Student name"},
    "group": {"ru": "Группа", "ky": "Топ", "en": "Group"},
    "date": {"ru": "Дата", "ky": "Күнү", "en": "Date"},
    "answer_key": {"ru": "Ключ ответов", "ky": "Жооптордун ачкычы", "en": "Answer key"},
    "answer": {"ru": "Ответ", "ky": "Жооп", "en": "Answer"},
    "question": {"ru": "Вопрос", "ky": "Суроо", "en": "Question"},
    "options": {"ru": "Варианты ответа", "ky": "Жооп варианттары", "en": "Options"},
    "q_type": {"ru": "Тип", "ky": "Түрү", "en": "Type"},
    "difficulty": {"ru": "Сложность", "ky": "Татаалдыгы", "en": "Difficulty"},
    "count": {"ru": "Вопросов", "ky": "Суроолор", "en": "Questions"},
    "bank": {"ru": "Банк вопросов", "ky": "Суроолор банкы", "en": "Question bank"},
    "coverage": {"ru": "Покрытие", "ky": "Камтуу", "en": "Coverage"},
    "variants": {"ru": "Варианты", "ky": "Варианттар", "en": "Versions"},
    "true": {"ru": "Верно", "ky": "Туура", "en": "True"},
    "false": {"ru": "Неверно", "ky": "Туура эмес", "en": "False"},
    "total_points": {"ru": "Всего баллов", "ky": "Бардык баллдар", "en": "Total points"},
    "instructions": {"ru": "Внимательно прочитайте вопросы. Ответы отмечайте на этом бланке.",
                     "ky": "Суроолорду кунт коюп окуңуз. Жоопторду ушул бланкка белгилеңиз.",
                     "en": "Read each question carefully. Mark your answers on this sheet."},
    "h_single": {"ru": "выберите один ответ", "ky": "бир жоопту тандаңыз", "en": "choose one answer"},
    "h_multiple": {"ru": "выберите все верные ответы", "ky": "бардык туура жоопторду тандаңыз",
                   "en": "choose all correct answers"},
    "h_truefalse": {"ru": "верно или неверно", "ky": "туурабы же туура эмеспи", "en": "true or false"},
    "h_matching": {"ru": "установите соответствие", "ky": "дал келүүнү табыңыз", "en": "match the items"},
    "h_short": {"ru": "впишите краткий ответ", "ky": "кыска жооп жазыңыз", "en": "write a short answer"},
    "h_open": {"ru": "дайте развёрнутый ответ", "ky": "толук жооп бериңиз", "en": "give an extended answer"},
    "model_answer": {"ru": "Эталон / критерии", "ky": "Үлгү / критерийлер", "en": "Model answer / criteria"},
})

# Значения перечислений паспорта (хранятся по-русски) → ky / en.
VALUES: dict[str, dict[str, str]] = {
    "обязательная": {"ky": "милдеттүү", "en": "compulsory"},
    "по выбору": {"ky": "тандоо боюнча", "en": "elective"},
    "гуманитарный": {"ky": "гуманитардык", "en": "humanities and social sciences"},
    "естественнонаучный": {"ky": "табигый-илимий", "en": "mathematics and natural sciences"},
    "профессиональный": {"ky": "кесиптик", "en": "professional"},
    "бакалавриат": {"ky": "бакалавриат", "en": "bachelor's"},
    "магистратура": {"ky": "магистратура", "en": "master's"},
    "специалитет": {"ky": "адистик", "en": "specialist degree"},
    "аспирантура": {"ky": "аспирантура", "en": "postgraduate"},
    "очная": {"ky": "күндүзгү", "en": "full-time"},
    "заочная": {"ky": "сырттан", "en": "part-time (extramural)"},
    "дистанционная": {"ky": "аралыктан", "en": "distance"},
    "русский": {"ky": "орус тили", "en": "Russian"},
    "кыргызский": {"ky": "кыргыз тили", "en": "Kyrgyz"},
    "английский": {"ky": "англис тили", "en": "English"},
    "current": {"ru": "текущий", "ky": "агымдагы", "en": "continuous"},
    "midterm": {"ru": "рубежный", "ky": "аралык", "en": "midterm"},
    "final": {"ru": "итоговый", "ky": "жыйынтыктоочу", "en": "final"},
    "single": {"ru": "один ответ", "ky": "бир жооп", "en": "single choice"},
    "multiple": {"ru": "несколько ответов", "ky": "бир нече жооп", "en": "multiple choice"},
    "truefalse": {"ru": "верно / неверно", "ky": "туура / туура эмес", "en": "true / false"},
    "matching": {"ru": "соответствие", "ky": "дал келтирүү", "en": "matching"},
    "short": {"ru": "краткий ответ", "ky": "кыска жооп", "en": "short answer"},
    "open": {"ru": "открытый вопрос", "ky": "ачык суроо", "en": "open question"},
    "easy": {"ru": "базовый", "ky": "базалык", "en": "easy"},
    "medium": {"ru": "средний", "ky": "орто", "en": "medium"},
    "hard": {"ru": "повышенный", "ky": "жогорку", "en": "hard"},
}

BLOOM: dict[str, dict[str, str]] = {
    "remember": {"ru": "запоминание", "ky": "эстеп калуу", "en": "remember"},
    "understand": {"ru": "понимание", "ky": "түшүнүү", "en": "understand"},
    "apply": {"ru": "применение", "ky": "колдонуу", "en": "apply"},
    "analyze": {"ru": "анализ", "ky": "талдоо", "en": "analyze"},
    "evaluate": {"ru": "оценка", "ky": "баалоо", "en": "evaluate"},
    "create": {"ru": "создание", "ky": "түзүү", "en": "create"},
}

# Короткие названия ЦУР ООН. Кыргызские — проверить по материалам ООН в КР.
SDG: dict[int, dict[str, str]] = {
    1: {"ru": "Ликвидация нищеты", "ky": "Жакырчылыкты жоюу", "en": "No Poverty"},
    2: {"ru": "Ликвидация голода", "ky": "Ачарчылыкты жоюу", "en": "Zero Hunger"},
    3: {"ru": "Хорошее здоровье и благополучие", "ky": "Ден соолук жана бакубаттуулук",
        "en": "Good Health and Well-being"},
    4: {"ru": "Качественное образование", "ky": "Сапаттуу билим берүү", "en": "Quality Education"},
    5: {"ru": "Гендерное равенство", "ky": "Гендердик теңчилик", "en": "Gender Equality"},
    6: {"ru": "Чистая вода и санитария", "ky": "Таза суу жана санитария", "en": "Clean Water and Sanitation"},
    7: {"ru": "Недорогостоящая и чистая энергия", "ky": "Жеткиликтүү жана таза энергия",
        "en": "Affordable and Clean Energy"},
    8: {"ru": "Достойная работа и экономический рост", "ky": "Татыктуу эмгек жана экономикалык өсүш",
        "en": "Decent Work and Economic Growth"},
    9: {"ru": "Индустриализация, инновации и инфраструктура", "ky": "Индустрия, инновациялар жана инфраструктура",
        "en": "Industry, Innovation and Infrastructure"},
    10: {"ru": "Уменьшение неравенства", "ky": "Теңсиздикти кыскартуу", "en": "Reduced Inequalities"},
    11: {"ru": "Устойчивые города и населённые пункты", "ky": "Туруктуу шаарлар жана калктуу конуштар",
         "en": "Sustainable Cities and Communities"},
    12: {"ru": "Ответственное потребление и производство", "ky": "Жоопкерчиликтүү керектөө жана өндүрүш",
         "en": "Responsible Consumption and Production"},
    13: {"ru": "Борьба с изменением климата", "ky": "Климаттын өзгөрүшүнө каршы күрөш", "en": "Climate Action"},
    14: {"ru": "Сохранение морских экосистем", "ky": "Деңиз экосистемаларын сактоо", "en": "Life Below Water"},
    15: {"ru": "Сохранение экосистем суши", "ky": "Кургактагы экосистемаларды сактоо", "en": "Life on Land"},
    16: {"ru": "Мир, правосудие и эффективные институты", "ky": "Тынчтык, адилеттүүлүк жана натыйжалуу институттар",
         "en": "Peace, Justice and Strong Institutions"},
    17: {"ru": "Партнёрство в интересах устойчивого развития", "ky": "Туруктуу өнүгүү үчүн өнөктөштүк",
         "en": "Partnerships for the Goals"},
}

# Частые активные методы: ключ — как пишут в паспорте (нижний регистр).
METHODS: dict[str, dict[str, str]] = {
    "flipped classroom": {"ru": "перевёрнутый класс (flipped classroom)", "ky": "оодарылган класс (flipped classroom)",
                          "en": "flipped classroom"},
    "case study": {"ru": "кейс-метод (case study)", "ky": "кейс-ыкма (case study)", "en": "case study"},
    "pbl": {"ru": "проектное / проблемное обучение (PBL)", "ky": "долбоордук / көйгөйлүү окутуу (PBL)",
            "en": "project/problem-based learning (PBL)"},
    "peer review": {"ru": "взаимное рецензирование (peer review)", "ky": "өз ара рецензиялоо (peer review)",
                    "en": "peer review"},
    "team-based learning": {"ru": "командное обучение (TBL)", "ky": "командалык окутуу (TBL)",
                            "en": "team-based learning"},
    "gamification": {"ru": "геймификация", "ky": "геймификация", "en": "gamification"},
}


def tv(value, lang: str = "ru") -> str:
    """Значение перечисления на языке lang; неизвестное — как есть."""
    if value is None:
        return ""
    entry = VALUES.get(str(value).strip().lower())
    if not entry:
        return str(value)
    return entry.get(lang) or (str(value) if lang == "ru" else entry.get("ru", str(value)))


def bloom_name(level: str, lang: str = "ru") -> str:
    return BLOOM.get(level, {}).get(lang, level or "")


def sdg_name(n: int, lang: str = "ru") -> str:
    return SDG.get(int(n), {}).get(lang, "")


def method_name(m: str, lang: str = "ru") -> str:
    entry = METHODS.get(str(m).strip().lower())
    return entry.get(lang, m) if entry else str(m)
