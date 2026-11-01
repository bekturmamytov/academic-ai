// Оформление руководства academicAI: цвета, врезки, блоки команд, схемы.
// Подключается из guide.typ и из каждой главы: #import "../lib.typ": *

// Версия academicAI, о которой написано руководство (plugin.json пакета academic).
#let version = "0.2.0"

#let accent = rgb("#1F4E79")
#let accent-soft = rgb("#E9F0F7")
#let accent-mid = rgb("#9FB7CF")
#let ink = rgb("#1B1F24")
#let muted = rgb("#5B6470")
#let line-c = rgb("#D5DCE3")
#let code-bg = rgb("#F3F5F8")
#let green = rgb("#2E7D4F")
#let green-soft = rgb("#EAF5EE")
#let red = rgb("#B3261E")
#let red-soft = rgb("#FCEDEB")
#let amber = rgb("#8A5A00")
#let amber-soft = rgb("#FFF5DF")

#let sans = ("IBM Plex Sans",)
#let mono = ("IBM Plex Mono",)

// ---------- врезки ----------

#let callout(label, color, fill, body) = block(
  width: 100%,
  breakable: false,
  above: 1.1em,
  below: 1.1em,
  fill: fill,
  stroke: (left: 3pt + color),
  inset: (left: 12pt, right: 12pt, top: 9pt, bottom: 10pt),
  radius: (right: 4pt),
)[
  #text(weight: "semibold", fill: color, size: 9pt, tracking: 0.04em, upper(label))
  #v(-0.35em)
  #set par(justify: false)
  #body
]

#let tip(body) = callout("Совет", green, green-soft, body)
#let important(body) = callout("Важно", red, red-soft, body)
#let see(body) = callout("Что вы увидите", accent, accent-soft, body)
#let note(body) = callout("Обратите внимание", amber, amber-soft, body)

// ---------- команда и фраза ----------

// Команда для терминала или чата — моноширинным блоком с подписью.
#let cmd(label: none, body) = block(width: 100%, above: 0.8em, below: 0.9em, breakable: false)[
  #if label != none {
    text(size: 8pt, fill: muted, weight: "medium", label)
    v(-0.5em)
  }
  #block(
    width: 100%,
    fill: code-bg,
    stroke: 0.5pt + line-c,
    radius: 4pt,
    inset: (x: 10pt, y: 8pt),
    text(font: mono, size: 8.8pt, fill: ink, body),
  )
]

// Как можно попросить Claude — фраза в кавычках-«ёлочках».
#let say(..phrases) = block(above: 0.6em, below: 0.8em)[
  #for p in phrases.pos() [
    #box(
      fill: white,
      stroke: 0.6pt + accent-mid,
      radius: 10pt,
      inset: (x: 8pt, y: 4pt),
      outset: (y: 1pt),
      text(size: 9pt, fill: accent)[«#p»],
    )#h(4pt)
  ]
]

// Карточка «паспорта» команды: когда, результат, где лежит.
#let facts(..rows) = {
  let cells = ()
  for (k, v) in rows.pos() {
    cells.push(text(size: 8.6pt, weight: "semibold", fill: accent, k))
    cells.push(text(size: 9pt, v))
  }
  block(
    width: 100%,
    above: 0.6em,
    below: 0.9em,
    stroke: 0.6pt + line-c,
    radius: 4pt,
    inset: 0pt,
    clip: true,
  )[
    #set par(justify: false)
    #grid(
      columns: (30%, 1fr),
      inset: (x: 9pt, y: 6pt),
      fill: (x, y) => if x == 0 { accent-soft } else { white },
      stroke: (x, y) => if y > 0 { (top: 0.5pt + line-c) },
      ..cells
    )
  ]
}

// Заголовок команды внутри главы: имя команды и короткое пояснение.
#let command-title(name, what) = block(above: 1.4em, below: 0.6em, breakable: false)[
  #text(font: mono, size: 10.5pt, weight: "bold", fill: accent, name)
  #h(6pt)
  #text(size: 9.5pt, fill: muted, what)
]

// ---------- таблицы ----------

#let table-style(..args) = table(
  stroke: (x, y) => (
    top: if y == 0 { 0pt } else { 0.5pt + line-c },
    bottom: 0.5pt + line-c,
  ),
  fill: (x, y) => if y == 0 { accent } else if calc.odd(y) { white } else { rgb("#F8FAFC") },
  inset: (x: 7pt, y: 5.5pt),
  ..args,
)

#let th(body) = text(fill: white, weight: "semibold", size: 8.8pt, body)

// ---------- схемы ----------

// Прямоугольник-шаг схемы.
#let node(body, fill: accent-soft, stroke: accent, w: auto, sub: none) = box(
  width: w,
  fill: fill,
  stroke: 0.8pt + stroke,
  radius: 5pt,
  inset: (x: 7pt, y: 6pt),
)[
  #set align(center)
  #set par(justify: false, leading: 0.45em)
  #text(size: 8.6pt, weight: "semibold", fill: ink, body)
  #if sub != none [
    #v(-0.45em)
    #text(size: 7.4pt, fill: muted, sub)
  ]
]

#let arrow-r = text(fill: accent, size: 13pt, weight: "bold")[→]
#let arrow-d = text(fill: accent, size: 13pt, weight: "bold")[↓]
#let arrow-l = text(fill: accent, size: 13pt, weight: "bold")[←]

// Цепочка шагов слева направо со стрелками.
#let flow(..items, w: 1fr, rev: false) = {
  let parts = items.pos()
  let cols = ()
  let cells = ()
  for (i, it) in parts.enumerate() {
    if i > 0 {
      cols.push(auto)
      cells.push(align(center + horizon, if rev { arrow-l } else { arrow-r }))
    }
    cols.push(w)
    cells.push(align(center + horizon, it))
  }
  grid(columns: cols, column-gutter: 4pt, ..cells)
}

// Дерево папок: items — массив (уровень, тип, имя, пояснение); тип "dir" или "file".
#let tree(items) = {
  let icon(kind) = if kind == "dir" {
    box(baseline: 1.5pt, width: 10pt, height: 8pt, fill: rgb("#F2C14E"), radius: (top-right: 2pt, bottom: 1.5pt), stroke: 0.4pt + rgb("#B88A1E"))
  } else {
    box(baseline: 1.5pt, width: 8pt, height: 10pt, fill: white, radius: 1pt, stroke: 0.6pt + muted)
  }
  block(
    width: 100%,
    fill: code-bg,
    stroke: 0.5pt + line-c,
    radius: 4pt,
    inset: (x: 12pt, y: 10pt),
    breakable: false,
  )[
    #set par(justify: false, leading: 0.5em)
    #grid(
      columns: (auto, 1fr),
      column-gutter: 10pt,
      row-gutter: 6.5pt,
      ..items
        .map(((lvl, kind, name, desc)) => (
          [#h(lvl * 16pt)#icon(kind)#h(5pt)#text(font: mono, size: 8.6pt, weight: if kind == "dir" { "bold" } else { "regular" }, name)],
          text(size: 8.4pt, fill: muted, desc),
        ))
        .flatten()
    )
  ]
}

// Ярлык-плашка (beta, обязательно и т. п.).
#let tag(body, color: accent) = box(
  fill: color.lighten(85%),
  stroke: 0.5pt + color,
  radius: 3pt,
  inset: (x: 4pt, y: 1.5pt),
  outset: (y: 1pt),
  text(size: 7.6pt, weight: "semibold", fill: color, body),
)
#let beta = tag("beta", color: amber)

// Метка в тексте документа: [НЕ ПРОВЕРЕНО] и т. п.
#let mark(body) = box(
  fill: amber-soft,
  inset: (x: 3pt, y: 1pt),
  outset: (y: 1.5pt),
  radius: 2pt,
  text(font: mono, size: 8.4pt, fill: amber, weight: "bold", body),
)

// Клавиша.
#let kbd(body) = box(
  fill: white,
  stroke: 0.6pt + muted,
  radius: 2.5pt,
  inset: (x: 3.5pt, y: 1pt),
  outset: (y: 1.5pt),
  text(font: mono, size: 8pt, body),
)

// Строка чек-листа самопроверки.
#let check(..items) = block(above: 0.6em, below: 0.8em)[
  #for it in items.pos() [
    #grid(
      columns: (14pt, 1fr),
      text(fill: green, weight: "bold", size: 10pt)[✓], it,
    )
    #v(-0.3em)
  ]
]
