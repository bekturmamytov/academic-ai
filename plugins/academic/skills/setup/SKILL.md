---
name: setup
description: Проверяет и готовит компьютер преподавателя к academicAI — плагины, нативные skills документов, Python, Typst, Node, ffmpeg, рабочая папка с profile.yaml. Используй после установки, когда что-то не собирается, или по просьбе «настрой academicAI», «проверь установку», «/academic:setup».
---

# Настройка academicAI

Говори с пользователем на его языке (ru или ky), простыми словами — он преподаватель,
не программист. Каждую установку объясни одной фразой и спроси разрешения.

## 1. Определи ОС

macOS или Windows (`uname` / `$env:OS`). Дальше команды — для этой ОС:
macOS — Homebrew (`brew`), Windows — `winget`.

## 2. Проверь окружение и покажи таблицу

| Что | Зачем | Проверка | Обязательно |
|---|---|---|---|
| плагины `academic-core`, `academic-research`, `academic-media` | наши skills | `claude plugin list` | да (media — нет) |
| `document-skills@anthropic-agent-skills` | сборка docx/xlsx/pptx/pdf | `claude plugin list` | да |
| Python 3.10+ | скрипты документов | `python3 --version` / `py --version` | да |
| Typst | вёрстка пособий и чистовиков PDF | `typst --version` | нет |
| Node 20+ и ffmpeg | видео-лекции | `node --version`, `ffmpeg -version` | только для видео |

Чего нет в плагинах — поставь:

```
claude plugin marketplace add anthropics/skills
claude plugin install document-skills@anthropic-agent-skills
claude plugin install academic --marketplace bekturmamytov/academic-ai
```

Необязательное ставь только если пользователь будет делать пособия (Typst) или
видео (Node, ffmpeg). Спроси.

## 3. Рабочая папка

Спроси, где держать материалы (по умолчанию `Документы/Мои курсы`, можно в
OneDrive / Google Drive). Создай в ней `profile.yaml`, задавая вопросы по одному:

```yaml
name: ""            # ФИО
degree: ""          # учёная степень, звание
position: ""        # должность
department: ""      # кафедра
faculty: ""         # факультет / институт
university: ""      # вуз
city: ""
language: ru        # ru | ky | en — язык документов по умолчанию
```

Папка `university/` (логотип, шапка, положения вуза) — необязательна; скажи, что
её можно добавить позже.

## 4. Итог

Таблица «что готово / что пропущено» и одна следующая команда — например,
«создайте первый курс: `/academic-core:new-course`».
