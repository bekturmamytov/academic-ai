// Учебно-методическое пособие. Данные — data.json рядом (собирает scripts/build_manual.py).
// Обложка, выходные данные (УДК/ББК, рецензенты, ISBN), оглавление, главы, литература.
#let data = json("data.json")
#let m = data.meta
#let L = data.labels
#let a5 = m.paper == "a5"
#let base = if a5 { 10.5pt } else { 13pt }

#set document(title: m.title, author: m.authors)
#set page(
  paper: if a5 { "a5" } else { "a4" },
  margin: if a5 { (top: 18mm, bottom: 20mm, left: 20mm, right: 15mm) }
          else { (top: 20mm, bottom: 20mm, left: 30mm, right: 15mm) },
  footer: context {
    if here().page() > 2 { align(center, text(size: base - 1pt, counter(page).display())) }
  },
)
#set text(
  font: ("Times New Roman", "Liberation Serif", "PT Serif", "DejaVu Serif"),
  size: base,
  lang: m.lang,
  hyphenate: true,
)
#set par(justify: true, first-line-indent: (amount: if a5 { 1cm } else { 1.25cm }, all: true), leading: 0.75em, spacing: 0.75em)
#set heading(numbering: none)
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  set align(center)
  set text(size: base + 1pt)
  block(above: 0pt, below: 1.4em, upper(it.body))
}
#show heading.where(level: 2): it => block(above: 1.3em, below: 0.8em, text(size: base, it.body))
#show heading.where(level: 3): it => block(above: 1.1em, below: 0.6em, emph(it.body))
#show table.cell: set par(justify: false, first-line-indent: 0pt)
#show table.cell: set text(size: base - 1.5pt)

#let runs(rs) = {
  for r in rs {
    let x = [#r.text]
    if r.at("code", default: false) { x = raw(r.text) }
    if r.at("b", default: false) { x = strong(x) }
    if r.at("i", default: false) { x = emph(x) }
    if r.at("mark", default: false) { x = highlight(fill: rgb("#FFF2A8"), x) }
    x
  }
}

#let render(blocks) = {
  for b in blocks {
    if b.t == "h" { heading(level: calc.min(b.level, 3), runs(b.runs)) }
    else if b.t == "p" { par(runs(b.runs)) }
    else if b.t == "quote" { pad(left: 1.25cm, emph(runs(b.runs))) }
    else if b.t == "ul" {
      for it in b.items { pad(left: it.level * 1.2em, list(tight: true, runs(it.runs))) }
    }
    else if b.t == "ol" {
      for it in b.items { pad(left: it.level * 1.2em, enum(start: int(it.n), tight: true, runs(it.runs))) }
    }
    else if b.t == "table" {
      let n = b.header.len()
      table(
        columns: n,
        inset: 5pt,
        align: left,
        table.header(..b.header.map(c => strong(runs(c)))),
        ..b.rows.map(r => r.map(c => runs(c))).flatten(),
      )
    }
    else if b.t == "img" {
      if b.at("file", default: none) != none {
        figure(image(b.file, width: 85%), caption: if b.alt != "" { b.alt } else { none })
      } else {
        align(center, emph[\[#L.figure: #b.alt\]])
      }
    }
    else if b.t == "pagebreak" { pagebreak() }
  }
}

// ---------- обложка ----------
#page(footer: none)[
  #set par(first-line-indent: 0pt, justify: false)
  #set text(hyphenate: false)
  #align(center)[
    #text(size: base - 1pt, m.ministry) \
    #v(0.3em)
    #if m.university != "" { strong(m.university) } \
    #if m.department != "" { text(size: base - 1pt, m.department) }
  ]
  #v(1fr)
  #align(center, text(size: base + 1pt, m.authors.join(", ")))
  #v(1.5em)
  #align(center, text(size: base + 7pt, weight: "bold", upper(m.title)))
  #if m.subtitle != "" { v(0.6em); align(center, text(size: base + 1pt, m.subtitle)) }
  #v(1em)
  #align(center, text(size: base + 1pt, m.kind))
  #v(1fr)
  #align(center)[#m.city #m.year]
]

// ---------- выходные данные ----------
#page(footer: none)[
  #set par(first-line-indent: 0pt, justify: false)
  #set text(size: base - 1pt)
  УДК #m.udk \
  ББК #m.bbk \
  #m.author_sign
  #v(1em)
  #align(center, emph(m.recommended))
  #v(1em)
  #if m.reviewers.len() > 0 [
    #strong[#L.reviewers:] \
    #for r in m.reviewers [#r \ ]
  ]
  #v(1em)
  #set par(justify: true, first-line-indent: 1cm)
  #strong(m.authors.join(", ")). #m.title: #m.kind / #m.authors.join(", "). — #m.city, #m.year. —
  #context counter(page).final().first() #L.pages
  #v(0.8em)
  #if m.annotation != "" { par(m.annotation) }
  #v(1fr)
  #set par(first-line-indent: 0pt)
  #if m.isbn_line != "" [ISBN #m.isbn_line #h(1fr)]
  #align(right)[
    © #m.authors.join(", "), #m.year \
    #if m.university != "" [© #m.university, #m.year]
  ]
]

// ---------- оглавление ----------
#outline(title: L.toc, depth: 2, indent: auto)

// ---------- главы ----------
#for ch in data.chapters { render(ch) }

// ---------- литература ----------
#if data.literature.len() > 0 {
  heading(level: 1, L.literature)
  set par(first-line-indent: 0pt)
  enum(..data.literature.map(it => runs(it)))
}
