#!/usr/bin/env bash
# Папка курса db-course с паспортом — копия templates/course.example.yaml (при правке образца обновить).
set -euo pipefail
mkdir -p db-course/lectures
cat > db-course/course.yaml <<'YAML'
# Паспорт курса — единый источник для силлабуса, РУП, тестов, лекций, УМКД.
# Пример заполнен полностью; пустые поля skill спросит у преподавателя.
schema: 1
language: ru                 # ru | ky | en — язык документов
languages_extra: [ky]        # параллельные версии (необязательно)

course:
  code: "ИС-201"
  title: "Базы данных"
  title_ky: "Маалымат базалары"
  title_en: "Databases"
  type: "обязательная"       # обязательная | по выбору
  cycle: "профессиональный"  # цикл ГОС: гуманитарный | естественнонаучный | профессиональный
  program: "710400 Программная инженерия"
  level: "бакалавриат"       # бакалавриат | магистратура | специалитет | аспирантура
  year: 2                    # курс обучения
  semester: 3
  academic_year: "2026-2027"
  form: "очная"              # очная | заочная | дистанционная
  language_of_instruction: "русский"
  prerequisites: ["Алгоритмы и структуры данных", "Дискретная математика"]
  postrequisites: ["Веб-разработка", "Проектирование информационных систем"]

credits: 5                   # 1 кредит = 30 ч (КР, ECTS)
hours:                       # сумма = credits × 30
  lectures: 30
  practicals: 15
  labs: 30
  srsp: 15                   # СРСП — СРС под руководством преподавателя
  srs: 60                    # СРС — самостоятельная работа
weeks: 15

teacher:                     # если пусто — берётся из profile.yaml
  name: ""
  degree: ""
  position: ""
  email: ""
  office_hours: "Вт, Чт 14:00–15:30"

description: >
  Курс знакомит с реляционной моделью данных, проектированием баз данных,
  языком SQL, транзакциями и основами NoSQL. Студенты проектируют и
  реализуют базу данных для реальной задачи.

goals:
  - "Сформировать навыки проектирования реляционных баз данных"
  - "Научить писать запросы SQL любой сложности"

outcomes:                    # результаты обучения — глагол по Блуму в начале
  - id: РО1
    bloom: understand        # remember | understand | apply | analyze | evaluate | create
    text: "Объясняет реляционную модель, ключи и нормальные формы"
  - id: РО2
    bloom: apply
    text: "Пишет SQL-запросы с соединениями, группировкой и подзапросами"
  - id: РО3
    bloom: create
    text: "Проектирует базу данных для предметной области до 3НФ"
  - id: РО4
    bloom: evaluate
    text: "Оценивает план выполнения запроса и выбирает индексы"

competencies: ["ПК-3", "ПК-5"]   # из ООП/ГОС, если известны

sdg: [4, 9]                  # ЦУР ООН: 4 — качественное образование, 9 — инновации
methods: ["flipped classroom", "case study", "PBL", "peer review"]

topics:                      # по неделям; часы по видам, РО — какие закрывает
  - week: 1
    title: "Введение в базы данных. Виды СУБД"
    content: "Данные и информация, файловые системы и СУБД, архитектура ANSI/SPARC, виды моделей данных, обзор PostgreSQL, MySQL, SQLite, MongoDB."
    lab: "Установка PostgreSQL, работа в psql и pgAdmin"
    lectures: 2
    practicals: 1
    labs: 2
    srsp: 1
    srs: 4
    outcomes: [РО1]
    srs_task: "Сравнить три СУБД по пяти критериям (модель данных, лицензия, масштабирование, транзакции, инструменты), таблица 1–2 стр."
    srs_form: "таблица сравнения"
    srs_due: 2
  - week: 2
    title: "Реляционная модель. Ключи и связи"
    content: "Отношение, кортеж, атрибут, домен; первичный, внешний, потенциальный ключ; связи 1:1, 1:N, M:N; целостность данных."
    lab: "Создание учебной базы данных «Университет»"
    lectures: 2
    practicals: 1
    labs: 2
    srsp: 1
    srs: 4
    outcomes: [РО1]
    srs_task: "Описать 5 сущностей выбранной предметной области, их атрибуты и ключи"
    srs_form: "описание сущностей"
    srs_due: 3
  - week: 3
    title: "Проектирование: ER-модель предметной области"
    content: "Сущности, атрибуты, связи, кардинальность; нотации Чена и Crow's Foot; переход от ER-модели к таблицам."
    lab: "ER-диаграмма предметной области в draw.io"
    lectures: 2
    practicals: 1
    labs: 2
    srsp: 1
    srs: 4
    outcomes: [РО1, РО3]
    srs_task: "Построить ER-диаграмму для своей предметной области (проект курса)"
    srs_form: "ER-диаграмма"
    srs_due: 4
  - week: 4
    title: "Нормализация: 1НФ, 2НФ, 3НФ"
    content: "Аномалии вставки, обновления и удаления; функциональные зависимости; первая, вторая и третья нормальные формы; НФБК."
    lab: "Нормализация схемы проекта до 3НФ"
    lectures: 2
    practicals: 1
    labs: 2
    srsp: 1
    srs: 4
    outcomes: [РО1, РО3]
    srs_task: "Привести схему своего проекта к 3НФ, обосновать каждый шаг"
    srs_form: "схема с пояснениями"
    srs_due: 5
  - week: 5
    title: "SQL: создание таблиц и ограничения (DDL)"
    content: "CREATE, ALTER, DROP; типы данных PostgreSQL; ограничения PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK, NOT NULL; каскадные действия."
    lab: "DDL-скрипт базы данных проекта"
    lectures: 2
    practicals: 1
    labs: 2
    srsp: 1
    srs: 4
    outcomes: [РО2, РО3]
    srs_task: "Написать DDL-скрипт для схемы проекта и заполнить таблицы тестовыми данными"
    srs_form: "SQL-скрипт"
    srs_due: 6
  - week: 6
    title: "SQL: выборка, фильтрация, сортировка"
    content: "SELECT, WHERE, операторы сравнения, LIKE, IN, BETWEEN, NULL; ORDER BY, LIMIT; вычисляемые поля."
    lab: "Запросы SELECT к учебной базе"
    lectures: 2
    practicals: 1
    labs: 2
    srsp: 1
    srs: 4
    outcomes: [РО2]
    srs_task: "Решить 15 задач на выборку данных из учебной базы"
    srs_form: "SQL-файл с ответами"
    srs_due: 7
  - week: 7
    title: "Соединения таблиц (JOIN). Рубежный контроль 1"
    content: "INNER, LEFT, RIGHT, FULL JOIN; самосоединение; соединение нескольких таблиц; типичные ошибки."
    lab: "Запросы с соединениями"
    control: "Рубежный контроль 1"
    lectures: 2
    practicals: 1
    labs: 2
    srsp: 1
    srs: 4
    outcomes: [РО1, РО2]
    srs_task: "Подготовиться к рубежному контролю 1: задачи на JOIN и нормализацию"
    srs_form: "рубежный контроль"
    srs_due: 7
  - week: 8
    title: "Группировка и агрегатные функции"
    content: "COUNT, SUM, AVG, MIN, MAX; GROUP BY, HAVING; оконные функции ROW_NUMBER, RANK, SUM OVER."
    lab: "Отчёты с GROUP BY и оконными функциями"
    lectures: 2
    practicals: 1
    labs: 2
    srsp: 1
    srs: 4
    outcomes: [РО2]
    srs_task: "Построить 5 аналитических отчётов по базе проекта"
    srs_form: "SQL-файл и результаты"
    srs_due: 9
  - week: 9
    title: "Подзапросы и представления"
    content: "Скалярные и коррелированные подзапросы, EXISTS, IN; общие табличные выражения (WITH); представления и их обновляемость."
    lab: "Подзапросы, CTE и представления"
    lectures: 2
    practicals: 1
    labs: 2
    srsp: 1
    srs: 4
    outcomes: [РО2]
    srs_task: "Переписать три запроса с подзапросами через CTE, сравнить читаемость"
    srs_form: "SQL-файл с комментариями"
    srs_due: 10
  - week: 10
    title: "Индексы и план выполнения запроса"
    content: "B-tree и hash-индексы, составные и частичные индексы; EXPLAIN и EXPLAIN ANALYZE; стоимость плана; когда индекс вредит."
    lab: "EXPLAIN ANALYZE до и после индексов"
    lectures: 2
    practicals: 1
    labs: 2
    srsp: 1
    srs: 4
    outcomes: [РО4]
    srs_task: "Найти три медленных запроса в базе проекта, предложить индексы и показать план до и после"
    srs_form: "отчёт 2–3 стр."
    srs_due: 11
  - week: 11
    title: "Транзакции и уровни изоляции"
    content: "ACID; COMMIT, ROLLBACK, SAVEPOINT; аномалии параллельного доступа; уровни изоляции; блокировки и MVCC в PostgreSQL."
    lab: "Эксперимент с уровнями изоляции в двух сессиях"
    lectures: 2
    practicals: 1
    labs: 2
    srsp: 1
    srs: 4
    outcomes: [РО1, РО4]
    srs_task: "Воспроизвести неповторяющееся чтение и фантом, описать, какой уровень изоляции их устраняет"
    srs_form: "протокол эксперимента"
    srs_due: 12
  - week: 12
    title: "Хранимые процедуры, функции и триггеры"
    content: "PL/pgSQL; функции и процедуры; триггеры BEFORE/AFTER; журнал изменений (аудит)."
    lab: "Триггер аудита изменений"
    lectures: 2
    practicals: 1
    labs: 2
    srsp: 1
    srs: 4
    outcomes: [РО2]
    srs_task: "Реализовать в базе проекта одну функцию и один триггер, объяснить их назначение"
    srs_form: "SQL-скрипт"
    srs_due: 13
  - week: 13
    title: "Безопасность, права доступа и резервное копирование"
    content: "Роли и привилегии, GRANT и REVOKE; защита от SQL-инъекций; резервное копирование pg_dump и восстановление."
    lab: "Роли, права и резервная копия базы"
    lectures: 2
    practicals: 1
    labs: 2
    srsp: 1
    srs: 4
    outcomes: [РО1, РО4]
    srs_task: "Спроектировать роли и права доступа для базы проекта, сделать резервную копию и восстановить её"
    srs_form: "скрипт и скриншоты"
    srs_due: 14
  - week: 14
    title: "NoSQL: документные базы и ключ-значение. Рубежный контроль 2"
    content: "Ограничения реляционной модели; документная модель (MongoDB), ключ-значение (Redis); CAP-теорема; выбор модели под задачу."
    lab: "CRUD-операции в MongoDB"
    control: "Рубежный контроль 2"
    lectures: 2
    practicals: 1
    labs: 2
    srsp: 1
    srs: 4
    outcomes: [РО1, РО4]
    srs_task: "Обосновать, какие данные проекта стоит хранить в NoSQL и почему (1 стр.)"
    srs_form: "эссе"
    srs_due: 15
  - week: 15
    title: "Защита проекта базы данных"
    content: "Презентация проекта: ER-модель, схема в 3НФ, запросы, индексы, права доступа; взаимное рецензирование."
    lab: "Защита проекта"
    lectures: 2
    practicals: 1
    labs: 2
    srsp: 1
    srs: 4
    outcomes: [РО3, РО4]
    srs_task: "Подготовить проект к защите: пояснительная записка и презентация"
    srs_form: "проект, презентация"
    srs_due: 15

assessment:                  # балльно-рейтинговая система, сумма weight = 100
  - name: "Лабораторные работы"
    type: current            # current — текущий | midterm — рубежный | final — итоговый
    weight: 20               # без week/weeks текущий контроль делится поровну по неделям
    form: "отчёт и защита лабораторной"
  - name: "Рубежный контроль 1"
    type: midterm
    weight: 15
    week: 7
    form: "тест + задачи SQL"
  - name: "Рубежный контроль 2"
    type: midterm
    weight: 15
    week: 14
    form: "тест + задачи SQL"
  - name: "СРС: проект базы данных"
    type: current
    weight: 10
    weeks: [4, 10, 15]       # контрольные точки проекта
    form: "проект, защита"
  - name: "Итоговый экзамен"
    type: final
    weight: 40
    form: "тест + практическое задание"
grading_scale: kr_default    # шкала: 87–100 «отлично» (A), 80–86 B, 74–79 C, 68–73 D, 61–67 E, 0–60 F

policies:
  attendance: "Пропуск более 20% занятий — недопуск к экзамену"
  late_work: "Работа после срока — минус 10% за каждую неделю"
  academic_integrity: "Плагиат и списывание — 0 баллов за работу"
  ai_use: "Использование ИИ допускается для поиска идей, с указанием; сдача сгенерированного текста — нарушение"

literature:                  # проверенные источники; verified: false — не попадёт в чистовик
  main:
    - text: "Дейт К. Дж. Введение в системы баз данных. 8-е изд. — М.: Вильямс, 2005. — 1328 с."
      verified: true
  extra:
    - text: "Silberschatz A., Korth H., Sudarshan S. Database System Concepts. 7th ed. — McGraw-Hill, 2019."
      verified: true
  online:
    - text: "PostgreSQL Documentation. — URL: https://www.postgresql.org/docs/ (дата обращения: 01.09.2026)."
      verified: true

files:                       # куда skills складывают результаты (относительно папки курса)
  out: "out"
YAML
