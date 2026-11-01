#import "../lib.typ": *

= Шпаргалка

#set text(size: 8.8pt)
#set par(justify: false)

#let sec(t) = table.cell(colspan: 3, fill: accent-soft, inset: (x: 7pt, y: 4pt), text(weight: "bold", fill: accent, size: 8.6pt, t))

#table-style(
  columns: (auto, 1fr, auto),
  inset: (x: 6pt, y: 4.2pt),
  th[Команда], th[Как попросить словами], th[Результат],
  sec[Начало],
  [`/academic:setup`], [«Настрой academicAI», «Проверь установку»], [`profile.yaml`],
  [`/academic-core:university`], [«Настрой academicAI под наш вуз по образцам»], [`settings.yaml`],
  sec[Курс],
  [`/academic-core:new-course`], [«Новый курс», «Вот мой старый силлабус», «Жаңы курс»], [`course.yaml`],
  [`/academic-core:syllabus`], [«Составь силлабус», «Силлабусту кыргызча жаса»], [`syllabus_ru.docx`],
  [`/academic-core:rup`], [«Сделай РУП», «Тематический план в Excel», «РУП түз»], [`rup.xlsx`, `.docx`],
  [`/academic-core:tests`], [«Тест на рубежный контроль 1», «Moodle үчүн тест»], [`tests.*`, GIFT, XML],
  [`/academic-core:lecture`], [«Напиши лекцию по теме 3», «Курс лекций», «Лекция жаз»], [`lectures/03.docx`],
  [`/academic-core:slides`], [«Презентация к лекции 3», «Лекцияга слайддар»], [`slides/03.pptx`],
  [`/academic-core:srs`], [«Задания СРС с критериями», «СӨИ тапшырмалары»], [`srs.docx`],
  [`/academic-core:umkd`], [«Собери УМКД», «УМКД чогулт»], [`umkd.docx`],
  [`/academic-core:manual`], [«Учебно-методическое пособие из лекций»], [`manual.pdf`, `.docx`],
  [`/academic-core:report`], [«Индивидуальный план», «Отчёт по дисциплине», «Жеке план»], [`report_*.docx`],
  sec[Наука],
  [`/academic-research:new-work`], [«Начинаю статью», «Жаңы макала»], [`work.yaml`],
  [`/academic-research:sources`], [«Подбери литературу», «Проверь список литературы»], [`sources.yaml`],
  [`/academic-research:paper`], [«Пишу статью в журнал», «Макала жазам»], [docx],
  [`/academic-research:thesis`], [«Пишу главу диссертации», «Автореферат»], [docx по ГОСТ],
  [`/academic-research:student-work`], [«Задание на курсовую», «Рецензия на диплом»], [docx],
  [`/academic-research:format-check`], [«Проверь оформление по ГОСТ», «ГОСТ боюнча текшер»], [замечания, копия],
  sec[Видео],
  [`/academic-media:video-lecture`], [«Сделай видео-лекцию из слайдов», «Озвучь слайды»], [mp4 + srt],
)

#v(0.6em)

#grid(
  columns: (1fr, 1fr),
  column-gutter: 10pt,
  block(width: 100%, fill: code-bg, radius: 4pt, inset: 9pt)[
    #text(weight: "bold", fill: accent)[Полезные фразы] \
    «Покажи, что уже готово по курсу» \
    «Пересобери силлабус после правок» \
    «Собери чистовик без непроверенной литературы» \
    «Что делать дальше?» \
    «Объясни, что делает эта команда»
  ],
  block(width: 100%, fill: code-bg, radius: 4pt, inset: 9pt)[
    #text(weight: "bold", fill: accent)[Терминал] \
    `claude --version` — версия Claude Code \
    `claude plugin list` — что установлено \
    `claude update` — обновить Claude Code \
    `claude plugin marketplace update academic-ai` \
    `claude plugin update academic@academic-ai`
  ],
)
