# Паспорт научной работы — `work.yaml`

Один файл в папке работы — единый источник для docx, списка литературы и
автореферата. Пример: `templates/work.example.yaml`. Папка работы:

```
Научная работа/<тема>/
  work.yaml          ← паспорт
  sources.yaml       ← литература (схема — references/sources-schema.md)
  chapters/          ← текст: 00-intro.md, 01.md, 02.md, 09-conclusion.md, A.md
  avtoreferat/       ← только для кандидатской
  data/              ← ваши данные (таблицы, замеры, анкеты)
  figures/           ← рисунки
  out/               ← собранные docx
```

## Поля

| Поле | Обязательно | Что |
|---|---|---|
| `schema` | да | версия схемы, сейчас `1` |
| `type` | да | `referat` · `doklad` · `tezisy` · `statya` · `kursovaya` · `diplom` · `magistr` · `kandidat` · `avtoreferat` |
| `language` | да | `ru` · `ky` · `en` — язык документа |
| `title`, `title_ky`, `title_en` | да / нет | тема; переводы — для аннотаций и автореферата |
| `authors[]` | да | `name`, `degree`, `position`, `affiliation`, `city`, `email`, `orcid`. Первый — автор (берётся из `profile.yaml`); в статье — все соавторы по порядку |
| `supervisor` | для работ с руководителем | `name`, `degree` |
| `consultant` | нет | научный консультант |
| `university`, `faculty`, `department`, `city` | нет | пусто — из `profile.yaml` и `university/brand.yaml` |
| `year` | да | год защиты / публикации |
| `specialty` | magistr, kandidat, avtoreferat | `code` — шифр по номенклатуре НАК КР, `name`, `science` — отрасль в родительном падеже («технических наук») |
| `program` | kursovaya, diplom, magistr | направление подготовки |
| `discipline` | referat, kursovaya | дисциплина |
| `doc_label` | нет | своя надпись на титуле, если вуз требует иначе |
| `keywords.{ru,ky,en}` | статья, тезисы, автореферат | 5–10 слов |
| `abstract.{ru,ky,en}` | статья, автореферат (резюме) | аннотация — пишется по готовому тексту, не заранее |
| `journal` | statya, tezisy | см. ниже |
| `conference` | doklad, tezisy | `name`, `date`, `place`, `section` |
| `udc` | статья | УДК — подбирает автор или библиотека |
| `citation_style` | да | `gost` (ГОСТ Р 7.0.100-2018) · `apa` (APA 7) · `ieee` |
| `bib_order` | нет | `alpha` — по алфавиту, кириллица впереди (по умолчанию для gost и apa); `cite` — по порядку первой ссылки (по умолчанию для ieee) |
| `numbering` | нет | `chapter` — «Рисунок 1.2», «Таблица 2.1» (по умолчанию для magistr, kandidat); `through` — сквозная |
| `sources` | да | путь к `sources.yaml` |
| `data[]` | нет | `file`, `description` — собственные данные автора. Результаты и выводы пишутся **только** по ним |
| `structure[]` | да | главы по порядку (см. ниже) |
| `avtoreferat` | kandidat | структура автореферата, публикации, сведения о защите |
| `ai_disclosure` | да | см. ниже |
| `output` | нет | папка для docx, по умолчанию `out` |

### `structure[]`

| Поле | Что |
|---|---|
| `kind` | `intro` (введение) · `chapter` (нумеруемая глава) · `conclusion` · `appendix` · `section` (ненумеруемый раздел — для статьи, тезисов, автореферата) |
| `title` | заголовок; для `intro` и `conclusion` можно не писать — подставится «ВВЕДЕНИЕ» / «ЗАКЛЮЧЕНИЕ» на языке работы |
| `file` | markdown-файл с текстом |
| `plan` | пункты плана главы — каркас до текста |
| `status` | `plan` · `draft` · `review` · `done` |

### `journal` (статья, тезисы)

```yaml
journal:
  name: "Вестник КГТУ им. И. Раззакова"
  issn: ""
  requirements_url: ""       # страница «Требования к авторам»
  requirements_file: ""      # или скачанный файл требований
  structure: imrad           # imrad | journal — свой шаблон журнала
  volume_pages: "5–10"       # объём
  abstract_words: "150–250"
  keywords_count: "5–7"
  abstract_languages: [ru, ky, en]
  citation_style: gost
  ai_policy: ""              # что журнал требует о раскрытии ИИ — дословно из требований
  in_nak_list: null          # входит ли в перечень НАК КР — проверить на сайте НАК
```

### `ai_disclosure`

```yaml
ai_disclosure:
  used: true                 # пользовались ли ИИ при подготовке
  tools: "Claude (Anthropic)"
  how: "структура, редактура языка, оформление"   # что именно делал ИИ
  include: false             # вставить заявление в документ (раздел перед списком литературы)
  statement: ""              # готовый текст; пусто — собирается из tools + how
```

Мы не пишем об ИИ в документе сами и не прячем его: `include` включает автор,
когда этого требует журнал, вуз или НАК.

## Метки в тексте глав

| Метка | Что значит |
|---|---|
| `[НУЖНЫ ВАШИ ДАННЫЕ: что именно]` | здесь должны быть данные автора — сами их не придумываем |
| `[НУЖЕН ИСТОЧНИК: утверждение]` | утверждению нужна проверенная ссылка |
| `[@key]`, `[@key, с. 25]`, `[@a; @b]` | ссылка на источник из `sources.yaml` |
| `Таблица: Название` перед таблицей | подпись таблицы |
| `![Название](figures/x.png)` | рисунок с подписью |
| `<!-- … -->` | заметка автору, в docx не попадает |
| `>> текст` | строка справа (гриф «УТВЕРЖДАЮ», подписи) |

`build_docx.py` подсвечивает метки жёлтым и печатает их счёт; `check_format.py`
считает оставленные метки критической ошибкой чистовика.
