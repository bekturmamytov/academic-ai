#import "../lib.typ": *

= Установка

== План установки

Большую часть времени установки компьютер скачивает программы — нужен устойчивый
интернет. Порядок одинаковый для macOS и Windows:

#v(0.3em)
#flow(
  node(sub: [или VS Code])[Программа Claude],
  node(sub: [команда `claude`])[Claude Code в терминале],
  node(sub: [3 команды или промпт])[Плагины academicAI],
  node(sub: [закрыть и открыть])[Перезапуск Claude],
  node(sub: [проверка и профиль])[`/academic:setup`],
)
#v(0.3em)

#important[Claude Code в терминале нужен, даже если вы будете работать только в
Claude Desktop. Через него ставятся плагины. Desktop использует собственную копию
Claude Code, а команды установки плагинов выполняются в терминале.]

== Установка на macOS

=== Шаг 1. Программа Claude Desktop

+ Откройте в браузере claude.com/download и скачайте версию для macOS.
+ Откройте скачанный файл и перетащите Claude в папку «Программы».
+ Запустите Claude и войдите в свою учётную запись (с платной подпиской).
+ Вверху окна нажмите вкладку *Code*.

#see[Вкладку Code с полем для сообщения и кнопкой выбора папки рядом с ним.]

Предпочитаете VS Code — поставьте его вместо Desktop (#ref(<sec-vscode>, supplement: "раздел")), а шаги 2–5 те же.

=== Шаг 2. Claude Code в терминале

+ Откройте Терминал: #kbd[Cmd] + #kbd[Пробел], наберите «Терминал», #kbd[Enter].
+ Скопируйте команду, вставьте в Терминал (#kbd[Cmd] + #kbd[V]) и нажмите #kbd[Enter]:
  #cmd(label: "macOS — установка Claude Code")[`curl -fsSL https://claude.ai/install.sh | bash`]
  Во время скачивания установщик ничего не показывает — подождите, пока не появится
  снова строка для ввода.
+ Закройте Терминал и откройте новый. Проверьте установку:
  #cmd[`claude --version`]
+ Войдите в учётную запись: наберите `claude` и нажмите #kbd[Enter]. Откроется браузер —
  подтвердите вход. Вернитесь в Терминал.

#see[После `claude --version` — номер версии, например `2.1.211 (Claude Code)`.
После входа — приветствие Claude Code и поле для сообщения прямо в Терминале.]

Выйти из Claude Code в Терминале — наберите `/exit` и нажмите #kbd[Enter].

#tip[Если на ваш Mac программы ставят через Homebrew, можно и так:
`brew install --cask claude-code`. Но тогда Claude Code не обновляется сам —
время от времени выполняйте `brew upgrade claude-code`.]

=== Шаг 3. Плагины academicAI

Выберите один из двух способов.

*Способ А — промпт-установщик (проще).* Откройте Claude Desktop → вкладка Code (или
Claude Code в Терминале) и вставьте текст из #ref(<sec-prompt>, supplement: "раздела") целиком. Claude сам
выполнит команды и будет спрашивать разрешения. Разрешайте.

*Способ Б — три команды в Терминале.* Вставляйте по одной и ждите окончания каждой:

#cmd(label: "установка плагинов")[
  `claude plugin marketplace add anthropics/skills` \
  `claude plugin install document-skills@anthropic-agent-skills` \
  `claude plugin install academic --marketplace bekturmamytov/academic-ai`
]

#see[После каждой команды — строку об успехе, например «Successfully added marketplace»
или «Successfully installed plugin». Последняя команда ставит `academic` и вместе с
ним `academic-core`, `academic-research`, `academic-media`.]

=== Шаг 4. Перезапуск

Закройте Claude Desktop полностью (#kbd[Cmd] + #kbd[Q]) и откройте снова. Если
работаете в Терминале — выйдите (`/exit`) и снова запустите `claude`. Плагины
загружаются при запуске.

=== Шаг 5. Настройка компьютера

Во вкладке Code выберите любую папку (например, «Документы») и напишите:

#cmd[`/academic:setup`]

Что делает эта команда — в #ref(<sec-setup>, supplement: "разделе").

== Установка на Windows

=== Шаг 1. Программа Claude Desktop

+ Откройте claude.com/download и скачайте версию для Windows (для обычных
  процессоров — x64; для ноутбуков на ARM — отдельный установщик ARM64).
+ Запустите установщик, затем откройте Claude и войдите в учётную запись.
+ Вверху окна нажмите вкладку *Code*.

=== Шаг 2. Claude Code в PowerShell

+ Нажмите «Пуск», наберите «PowerShell» и откройте *Windows PowerShell*.
  Запускать от имени администратора не нужно.
+ Вставьте команду (#kbd[Ctrl] + #kbd[V] или правая кнопка мыши) и нажмите #kbd[Enter]:
  #cmd(label: "Windows PowerShell — установка Claude Code")[`irm https://claude.ai/install.ps1 | iex`]
+ Закройте PowerShell и откройте новое окно. Проверьте:
  #cmd[`claude --version`]
+ Войдите: наберите `claude`, #kbd[Enter], подтвердите вход в браузере.

#note[Как отличить окна: в PowerShell строка начинается с `PS C:\Users\Имя>`, в
командной строке CMD — просто `C:\Users\Имя>`. Если открыли CMD, используйте другую
команду:

`curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd`

Ошибка `'irm' is not recognized` значит, что вы в CMD; ошибка
`The token '&&' is not a valid statement separator` — что вы в PowerShell.]

#tip[Желательно поставить ещё *Git for Windows* (git-scm.com). Без него Claude Code
тоже работает — выполняет команды через PowerShell, — но с ним некоторые команды
работают надёжнее.]

#note[Если после установки `claude --version` пишет, что команда не найдена, —
закройте все окна PowerShell и откройте новое. Не помогло — перезагрузите компьютер.
Подробнее — глава 10.]

=== Шаги 3–5

Те же, что для macOS: промпт-установщик (#ref(<sec-prompt>, supplement: "раздел")) или три команды в PowerShell,
затем полный перезапуск Claude и `/academic:setup`.

#cmd(label: "установка плагинов (PowerShell)")[
  `claude plugin marketplace add anthropics/skills` \
  `claude plugin install document-skills@anthropic-agent-skills` \
  `claude plugin install academic --marketplace bekturmamytov/academic-ai`
]

== Промпт-установщик <sec-prompt>

Скопируйте текст в рамке целиком и вставьте в Claude Code — во вкладку Code
программы Claude, в панель Claude в VS Code или в Claude Code в терминале.

#block(
  width: 100%,
  stroke: (left: 3pt + accent, rest: 0.5pt + line-c),
  fill: white,
  inset: 12pt,
  radius: (right: 4pt),
)[
  #set par(justify: false)
  #set text(size: 9pt)
  Установи мне academicAI — помощника преподавателя вуза.

  1. Выполни в терминале:
     - `claude plugin marketplace add anthropics/skills`
     - `claude plugin install document-skills@anthropic-agent-skills`
     - `claude plugin install academic --marketplace bekturmamytov/academic-ai`
  2. Если какая-то команда выдала ошибку — объясни мне простыми словами, что не так, и предложи, как исправить.
  3. Скажи, что нужно перезапустить Claude, и после перезапуска запусти `/academic:setup`.

  Говори со мной по-русски (или по-кыргызски, если я пишу по-кыргызски). Я не программист — объясняй каждый шаг одной фразой.
]

Этот же текст лежит в репозитории: `installer/PROMPT.md`.

#see[Claude напишет, что собирается сделать, и спросит разрешения на каждую
команду. Перед разрешением он объяснит команду одной фразой. В конце он попросит
перезапустить Claude.]

#tip[Как отвечать на запрос разрешения: прочитайте пояснение и подтвердите. Если
сомневаетесь — спросите прямо в чате «что делает эта команда?», Claude объяснит.]

== Работа в VS Code <sec-vscode>

+ Установите VS Code (code.visualstudio.com) — нужна версия 1.94 или новее.
+ Откройте панель расширений: #kbd[Ctrl] + #kbd[Shift] + #kbd[X] (Windows) или
  #kbd[Cmd] + #kbd[Shift] + #kbd[X] (macOS). Найдите «Claude Code» и нажмите *Install*.
+ Откройте рабочую папку: меню *File → Open Folder…*
+ Откройте панель Claude: значок-искра в левой боковой панели или надпись
  *Claude Code* со звёздочкой в правом нижнем углу окна.
+ При первом открытии нажмите *Sign in* и подтвердите вход в браузере.

Плагины в VS Code можно ставить через терминал (шаг 3 выше) — они появятся и здесь.
Или прямо в панели: напишите `/plugins`, на вкладке *Marketplaces* добавьте
`anthropics/skills` и `bekturmamytov/academic-ai`, затем на вкладке *Plugins* найдите и
установите `document-skills` и `academic` (вариант *Install for you*).

== Первая настройка: /academic:setup <sec-setup>

Команда проверяет компьютер и готовит его к работе. Она говорит простыми словами и
перед каждой установкой спрашивает разрешения.

+ *Определяет систему* — macOS или Windows — и дальше предлагает команды для неё.
+ *Показывает таблицу*: что установлено, что нет, что обязательно.
  #table-style(
    columns: (auto, 1fr, auto),
    th[Что], th[Зачем], th[Обязательно],
    [плагины academicAI], [команды academicAI], [да (видео — нет)],
    [`document-skills`], [сборка docx / xlsx / pptx / pdf], [да],
    [`uv`], [запуск программ сборки документов], [да],
    [Typst], [вёрстка пособий в PDF], [нет],
    [Node.js 20+, ffmpeg], [видео-лекции], [только для видео],
    [LibreOffice], [PDF-копии и проверка вёрстки], [нет],
  )
+ *Ставит недостающее.* `uv` ставит всегда: на macOS — `brew install uv`, на Windows —
  `winget install --id astral-sh.uv -e`. Typst, Node.js, ffmpeg — только если вы
  собираетесь делать пособия или видео; спросит.
+ *Создаёт рабочую папку.* Спросит, где хранить материалы. По умолчанию —
  «Документы/Мои курсы»; можно в OneDrive или Google Drive.
+ *Заполняет профиль* `profile.yaml` — по одному вопросу: ФИО, учёная степень и
  звание, должность, кафедра, факультет или институт, вуз, город, язык документов по
  умолчанию (ru, ky или en).
+ *Напоминает о правилах вуза.* Без них документы собираются по нормам КР. Если у
  вуза свои требования или образцы, их настраивает команда `/academic-core:university`
  (глава 5) — сейчас или позже.
+ *Показывает итог*: что готово, что пропущено, и следующую команду — обычно
  `/academic-core:new-course`.

#see[В конце — таблица «готово / пропущено» и в рабочей папке файл `profile.yaml`
примерно такого вида:]

```yaml
name: "Асанова Айгуль Токтогуловна"
degree: "кандидат технических наук, доцент"
position: "доцент"
department: "Кафедра программной инженерии"
faculty: "Факультет информационных технологий"
university: "…"
city: "Бишкек"
language: ru
```

#note[Голос ElevenLabs для видео здесь не настраивается. Его подключают при первой
видео-лекции — команда `/academic-media:video-lecture` сама откроет файл для ключа
(глава 8).]

`/academic:setup` можно запускать сколько угодно раз — например, когда что-то
перестало собираться или после переезда на новый компьютер.

== Обновление

Новые версии academicAI сами не ставятся — обновляйте вручную, например раз в
месяц или когда об этом сообщит методист. В терминале выполните:

#cmd(label: "обновить список версий и плагины")[
  `claude plugin marketplace update academic-ai` \
  `claude plugin update academic@academic-ai` \
  `claude plugin update academic-core@academic-ai` \
  `claude plugin update academic-research@academic-ai` \
  `claude plugin update academic-media@academic-ai`
]

Затем перезапустите Claude. Можно попросить и самого Claude: «обнови плагины
academicAI» — он выполнит те же команды.

#tip[В Claude Code в терминале можно включить автообновление: наберите `/plugin`,
откройте вкладку *Marketplaces*, выберите `academic-ai` и пункт *Enable auto-update*.
Там же пункт *Update marketplace* обновляет все плагины academicAI сразу.]

Сам Claude Code, поставленный командой из шага 2, обновляется автоматически.
Обновить сразу: `claude update`.

== Удаление

#cmd(label: "удалить academicAI вместе с подтянутыми плагинами")[`claude plugin uninstall academic@academic-ai --prune`]

Удалить всё, что поставлено из каталога academicAI, одной командой:

#cmd[`claude plugin marketplace remove academic-ai`]

Ваши документы, паспорта курсов и рабочая папка при этом *не удаляются*. Остаются
и служебные файлы в папке `.academic` в домашней папке пользователя: ключ ElevenLabs
(`.env`) и движок видео (`remotion`). Если они больше не нужны, удалите папку
`~/.academic` (Windows: `%USERPROFILE%\.academic`) вручную.
