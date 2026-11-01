#import "../lib.typ": *

= Поддержка и лицензия

== Лицензия academicAI

academicAI распространяется по лицензии *PolyForm Noncommercial 1.0.0*.

- *Бесплатно* для преподавателей, вузов и других образовательных учреждений.
- *Коммерческое использование и перепродажа* — только по договору с AI Lab
  (ОсОО «Девлайн»).

Исходный код открыт: github.com/bekturmamytov/academic-ai. Полный текст лицензии —
файл `LICENSE` в репозитории. Текущая версия — *#version, beta*: шаблоны построены по
общим нормам КР, видео-лекции — отдельная beta-функция.

== Сторонние программы и сервисы

#table-style(
  columns: (auto, 1fr),
  th[Что], th[Условия],
  [Claude, Claude Code], [Платная подписка Claude (глава 2), условия Anthropic],
  [`document-skills`], [Набор Anthropic, ставится отдельно из каталога `anthropics/skills`],
  [Remotion (видео-лекции)], [Бесплатно для частных лиц, некоммерческих организаций и компаний до 3 сотрудников; частному коммерческому вузу больше 3 сотрудников нужна Company License (глава 8)],
  [ElevenLabs (голос)], [Ваш собственный аккаунт и тариф],
  [OpenAlex, Crossref], [Открытые реестры научных публикаций для проверки литературы],
)

== Поддержка

Внедрение в вузе, настройка под положения вуза, обучение преподавателей и
сопровождение — AI Lab.

#block(
  width: 100%,
  fill: accent,
  radius: 6pt,
  inset: 14pt,
)[
  #set text(fill: white)
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 16pt,
    [
      #text(size: 14pt, weight: "bold")[AI Lab] \
      #text(size: 9pt)[ОсОО «Девлайн»]
    ],
    [
      #text(size: 9pt, fill: white.transparentize(20%))[Почта] \
      #text(size: 11pt, weight: "semibold")[#link("mailto:info@ailab.kg")[#text(fill: white)[info\@ailab.kg]]] \
      #text(size: 9pt, fill: white.transparentize(20%))[Сайт] \
      #text(size: 11pt, weight: "semibold")[#link("https://ailab.kg")[#text(fill: white)[https:\/\/ailab.kg]]]
    ],
  )
]

*Что написать в письме, чтобы помочь быстрее:*

+ Система: Windows или macOS, и где вы работаете (Claude Desktop, VS Code, терминал).
+ Какую команду запускали и что просили.
+ Точный текст ошибки — скопируйте из чата.
+ Версии: результат `claude --version` и `claude plugin list`.

*Не присылайте* в письме ключ ElevenLabs, пароли и личные данные студентов.
