// Руководство пользователя academicAI (ru).
//
// Сборка из корня репозитория:
//   typst compile --ignore-system-fonts --font-path docs/guide/fonts docs/guide/guide.typ docs/guide/academicAI-guide-ru.pdf
//
// Шрифты — IBM Plex Sans и IBM Plex Mono (SIL OFL 1.1, лицензия — docs/guide/fonts/OFL.txt),
// лежат в docs/guide/fonts, поэтому PDF одинаково собирается на любом компьютере.

#import "lib.typ": *

#let edition = "ноябрь 2026"

#set document(
  title: "academicAI — руководство пользователя",
  author: "AI Lab",
  keywords: ("academicAI", "Claude Code", "преподаватель", "силлабус", "УМКД"),
)

#set text(font: sans, size: 10pt, lang: "ru", fill: ink, hyphenate: true)
#set par(justify: true, leading: 0.68em, spacing: 0.95em)
#show raw: set text(font: mono)
#show raw.where(block: false): it => box(
  fill: code-bg,
  inset: (x: 2.5pt, y: 0pt),
  outset: (y: 2.5pt),
  radius: 2pt,
  text(size: 0.9em, fill: rgb("#24384F"), it),
)
#show raw.where(block: true): it => block(
  width: 100%,
  fill: code-bg,
  stroke: 0.5pt + line-c,
  radius: 4pt,
  inset: (x: 10pt, y: 8pt),
  text(size: 8.6pt, it),
)
#show link: it => text(fill: accent, it)
#set list(indent: 4pt, body-indent: 6pt, marker: text(fill: accent)[•])
#set enum(
  indent: 2pt,
  body-indent: 7pt,
  numbering: n => box(
    width: 14pt,
    height: 14pt,
    radius: 7pt,
    fill: accent,
    baseline: 3pt,
    align(center + horizon, text(fill: white, size: 7.8pt, weight: "bold", str(n))),
  ),
)
#set terms(separator: [ — ], hanging-indent: 1.2em, spacing: 0.75em)
#show terms: set par(justify: false)
#show terms.item: it => block(above: 0.55em)[#text(weight: "semibold", fill: accent, it.term) — #it.description]
#show table: set par(justify: false)
#show table: set text(size: 9pt)

// ---------- заголовки ----------

#set heading(numbering: "1.1")
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  v(1.2cm)
  block(width: 100%, below: 1.4em)[
    #if it.numbering != none [
      #text(size: 11pt, weight: "semibold", fill: accent, tracking: 0.08em)[ГЛАВА #counter(heading).display("1")]
      #v(-0.2em)
    ]
    #text(size: 24pt, weight: "bold", fill: ink, it.body)
    #v(-0.3em)
    #line(length: 3cm, stroke: 2.5pt + accent)
  ]
}
#show heading.where(level: 2): it => block(above: 1.8em, below: 0.9em, breakable: false)[
  #text(size: 14pt, weight: "bold", fill: accent)[
    #if it.numbering != none [#counter(heading).display("1.1")#h(8pt)]#it.body
  ]
]
#show heading.where(level: 3): it => block(above: 1.4em, below: 0.7em, breakable: false)[
  #text(size: 11pt, weight: "semibold", fill: ink, it.body)
]

// ---------- страница ----------

#let running-header = context {
  let here-page = here().page()
  let starts = query(heading.where(level: 1)).filter(h => h.location().page() == here-page)
  if starts.len() > 0 { return none }
  let before = query(heading.where(level: 1).before(here()))
  if before.len() == 0 { return none }
  let h = before.last()
  set text(size: 8pt, fill: muted)
  grid(
    columns: (1fr, auto),
    [academicAI · руководство пользователя],
    [#if h.numbering != none [Глава #numbering("1", ..counter(heading).at(h.location()).slice(0, 1)). ]#h.body],
  )
  v(-0.4em)
  line(length: 100%, stroke: 0.4pt + line-c)
}

#let running-footer = context {
  set text(size: 8.5pt, fill: muted)
  align(center, counter(page).display("1"))
}

#set page(
  paper: "a4",
  margin: (top: 2.2cm, bottom: 2cm, left: 2.2cm, right: 2.2cm),
  header: running-header,
  footer: running-footer,
)

// ---------- обложка ----------

#page(header: none, footer: none, margin: 0pt, fill: white)[
  #place(top + left, rect(width: 100%, height: 58%, fill: accent))
  #place(top + left, dx: 2.2cm, dy: 2.4cm)[
    #text(size: 10pt, fill: white.transparentize(25%), weight: "semibold", tracking: 0.12em)[РУКОВОДСТВО ПОЛЬЗОВАТЕЛЯ]
  ]
  #place(top + left, dx: 2.2cm, dy: 6.2cm)[
    #block(width: 15cm)[
      #text(size: 46pt, weight: "bold", fill: white)[academicAI]
      #v(0.2em)
      #set par(justify: false, leading: 0.55em)
      #text(size: 17pt, fill: white)[Помощник преподавателя вуза \ в Claude Code]
      #v(1.4em)
      #text(size: 10.5pt, fill: white.transparentize(15%))[
        Силлабус, РУП, тесты для Moodle, лекции, презентации, СРС, УМКД, пособия, отчёты,
        научные работы и видео-лекции — по нормам Кыргызской Республики, на русском,
        кыргызском и английском.
      ]
    ]
  ]
  // Схема на обложке: паспорт курса → документы.
  #place(top + left, dx: 2.2cm, dy: 13.1cm)[
    #set text(fill: white)
    #let pill(t) = box(
      stroke: 0.8pt + white.transparentize(30%),
      radius: 10pt,
      inset: (x: 8pt, y: 4pt),
      text(size: 8.5pt, fill: white, t),
    )
    #box(fill: white, radius: 5pt, inset: (x: 10pt, y: 7pt), text(size: 9pt, weight: "bold", fill: accent)[course.yaml — паспорт курса])
    #h(6pt) #text(size: 14pt, fill: white)[→] #h(6pt)
    #pill[силлабус] #pill[РУП] #pill[тесты] #pill[лекции] #pill[слайды] #pill[УМКД]
  ]
  #place(top + left, dx: 2.2cm, dy: 17.6cm)[
    #block(width: 16.6cm)[
      #set par(justify: false)
      #grid(
        columns: (1fr, 1fr, 1fr),
        column-gutter: 14pt,
        ..(
          ([Для кого], [Преподаватели вузов и методисты, которые настраивают систему для кафедры]),
          ([Где работает], [Claude Desktop (вкладка Code), VS Code или терминал — на Windows и macOS]),
          ([Что нужно], [Платная подписка Claude, интернет и компьютер с Windows 10+ или macOS 13+]),
        ).map(((h, t)) => [
          #text(size: 8.5pt, weight: "semibold", fill: accent, tracking: 0.06em, upper(h))
          #v(-0.3em)
          #line(length: 100%, stroke: 0.6pt + accent-mid)
          #v(-0.2em)
          #text(size: 9.5pt, t)
        ])
      )
    ]
  ]
  #place(bottom + left, dx: 2.2cm, dy: -1.8cm)[
    #text(size: 8.5pt, fill: muted)[Версия academicAI #version (beta) · редакция: #edition · github.com/bekturmamytov/academic-ai]
  ]
]

// ---------- оглавление ----------

#page(header: none)[
  #v(1cm)
  #text(size: 24pt, weight: "bold")[Содержание]
  #v(-0.3em)
  #line(length: 3cm, stroke: 2.5pt + accent)
  #v(0.8em)
  #show outline.entry.where(level: 1): it => {
    v(0.55em)
    text(weight: "semibold", size: 10.5pt, it)
  }
  #show outline.entry.where(level: 2): set text(size: 9.5pt)
  #outline(title: none, depth: 2, indent: 1.4em)
]

#include "chapters/00-intro.typ"
#include "chapters/01-what.typ"
#include "chapters/02-requirements.typ"
#include "chapters/03-install.typ"
#include "chapters/04-folder.typ"
#include "chapters/05-university.typ"
#include "chapters/06-course.typ"
#include "chapters/07-research.typ"
#include "chapters/08-video.typ"
#include "chapters/09-honesty.typ"
#include "chapters/10-faq.typ"
#include "chapters/11-cheatsheet.typ"
#include "chapters/12-support.typ"
