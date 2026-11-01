# slides.yaml для видео-лекции

Файл пишет `/academic-core:slides` (`out/slides/NN.yaml`). Видео читает:

```yaml
title: Нормализация реляционных баз данных   # тема лекции — в заставке и концовке
course: Базы данных                           # курс — в заставке
teacher: Асанова Айгуль Токтогуловна          # ФИО — в заставке и концовке
accent: "#1F4E79"                             # один акцентный цвет; нет — brand.color вуза (university/settings.yaml)
lang: ru                                      # ru | ky | en, необязательно
slides:
  - type: title          # title | section | bullets | table | closing
    title: …
    subtitle: …          # для title / section / closing, необязательно
    notes: …             # полный текст докладчика = озвучка и титры
  - type: bullets
    title: …
    bullets: [ …, … ]    # до 6 пунктов; появляются, когда о них заговорили
    notes: …
  - type: table
    title: …
    table:
      header: [Форма, Требование]
      rows: [[1НФ, …], [2НФ, …]]   # или список строк, первая — шапка
    notes: …
```

- `section` начинает новый раздел — по разделам лекция режется на ролики.
- Подпункт — строка `bullets` с префиксом «– »: в кадре с отступом и мельче.
- `closing` с `bullets` (вопросы для обсуждения) показывается списком, `subtitle` (email) — внизу
  мелко; email голос не читает.
- Пункт появляется, когда в заметках звучит фраза с его словами; не нашлось — по порядку.
- Из `.pptx` типы угадываются (первый слайд — title, таблица — table, без текста — section,
  последний без текста — closing); перевести и проверить глазами:
  `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/slides_from_pptx.py" "<файл.pptx>"` → `<файл>.yaml`.
- Картинки и схемы из pptx в видео пока не переносятся (beta).
