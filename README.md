# academicAI

Помощник преподавателя вуза для [Claude Code](https://claude.com/claude-code):
силабусы, рабочие учебные планы, тесты, лекции и презентации, УМКД,
учебно-методические пособия, отчёты, научные работы и видео-лекции.
По нормам Кыргызской Республики, на русском, кыргызском и английском.

Работает в Claude Desktop (вкладка Code) и в VS Code.

## Установка

**Проще всего:** откройте Claude Code и вставьте текст из
[`installer/PROMPT.md`](installer/PROMPT.md) — Claude всё поставит сам.

**Вручную, в терминале:**

```
claude plugin marketplace add anthropics/skills
claude plugin install document-skills@anthropic-agent-skills
claude plugin install academic --marketplace bekturmamytov/academic-ai
```

Перезапустите Claude и выполните `/academic:setup`.

## Что внутри

| Плагин | Для чего |
|---|---|
| `academic` | всё сразу + настройка компьютера |
| `academic-core` | паспорт курса, силабус, РУП, тесты, СРС, лекции, презентации, УМКД, пособия, отчёты |
| `academic-research` | реферат, доклад, курсовая, диплом, магистерская, статья, кандидатская |
| `academic-media` | видео-лекции из слайдов с озвучкой (beta) |

## Команды

Начните с `/academic:setup`, затем `/academic-core:new-course` — паспорт курса,
из которого собирается всё остальное.

| Команда | Что делает | Результат |
|---|---|---|
| `/academic-core:new-course` | паспорт курса: вопросы или перенос старого силлабуса | `course.yaml` |
| `/academic-core:syllabus` | силлабус по нормам КР, ru / ky / en | docx |
| `/academic-core:rup` | рабочая программа и тематический план с часами | xlsx, docx |
| `/academic-core:tests` | банк тестов по темам и результатам обучения, варианты, ключ | xlsx, docx, Moodle GIFT / XML |
| `/academic-core:lecture` | текст лекции или курс лекций с активными методами и ЦУР | docx |
| `/academic-core:slides` | презентация к лекции с заметками докладчика | pptx |
| `/academic-core:srs` | СРС, практические и лабораторные с рубриками | docx |
| `/academic-core:umkd` | УМКД из всех материалов курса | docx |
| `/academic-core:manual` | учебно-методическое пособие с вёрсткой | PDF (Typst), docx |
| `/academic-core:report` | индивидуальный план, отчёт преподавателя, отчёт по дисциплине | docx |
| `/academic-research:new-work` | паспорт научной работы | `work.yaml` |
| `/academic-research:sources` | поиск и проверка литературы (OpenAlex, Crossref), ГОСТ / APA / IEEE | `sources.yaml` |
| `/academic-research:paper` | статья, тезисы, доклад — в режиме соавтора | docx |
| `/academic-research:thesis` | магистерская, кандидатская, автореферат | docx по ГОСТ |
| `/academic-research:student-work` | задание, методичка, критерии, рецензия и отзыв на работу студента | docx |
| `/academic-research:format-check` | проверка и исправление оформления по ГОСТ | список замечаний |
| `/academic-media:video-lecture` | видео-лекция из слайдов: ElevenLabs, своя запись или титры (beta) | mp4 + srt |

## Принципы

- Документы собираются из **паспорта курса** — часы, темы и результаты сходятся во всех файлах.
- **Литература только проверенная**, данные исследований не выдумываются.
- Для студенческих работ — задания, критерии и рецензии, а не готовые работы.
- Документы принадлежат преподавателю: в них нет нашего логотипа или подписи.

## Лицензия

[PolyForm Noncommercial 1.0.0](LICENSE). Бесплатно для преподавателей, вузов и
образовательных учреждений. Коммерческое использование и перепродажа — по
договору с AI Lab (ОсОО «Девлайн»), [ailab.kg](https://ailab.kg), info@ailab.kg.

Видео-лекции собираются на [Remotion](https://www.remotion.dev/license): он
бесплатен для частных лиц, некоммерческих организаций и компаний до 3 человек;
остальным организациям нужна лицензия Remotion.

> Статус: beta (v0.1.0). Шаблоны построены по общим нормам КР — сверяйте с
> положениями своего вуза. Спецификация — [`docs/SPEC.md`](docs/SPEC.md).
