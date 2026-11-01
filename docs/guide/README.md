# Руководство пользователя academicAI

`academicAI-guide-ru.pdf` — руководство для преподавателя и методиста вуза (русский язык):
установка, рабочая папка, настройка под вуз, все команды, научные работы, видео-лекции,
частые ошибки, шпаргалка.

## Сборка

Нужен [Typst](https://typst.app) 0.14 или новее. Из корня репозитория:

```
typst compile --ignore-system-fonts --font-path docs/guide/fonts docs/guide/guide.typ docs/guide/academicAI-guide-ru.pdf
```

## Устройство

| Файл | Что внутри |
|---|---|
| `guide.typ` | страница, стили, обложка, оглавление, подключение глав |
| `lib.typ` | версия, цвета, врезки «Совет / Важно / Что вы увидите», блоки команд, схемы |
| `chapters/*.typ` | главы 0–12 по порядку |
| `fonts/` | IBM Plex Sans и IBM Plex Mono, лицензия SIL OFL 1.1 — `fonts/OFL.txt` |

Версия academicAI в тексте — переменная `version` в `lib.typ`. Источники фактов —
`README.md`, `installer/PROMPT.md`, `docs/SPEC.md`, `SKILL.md` и `references/` плагинов,
`plugins/academic-core/templates/settings.example.yaml` и
`plugins/academic-core/references/university-settings.md`. Поменялся skill — сверьте
соответствующую главу и пересоберите PDF.
