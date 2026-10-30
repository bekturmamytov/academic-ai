# Список литературы — `sources.yaml`

Лежит рядом с `work.yaml`. Пример: `templates/sources.example.yaml`.

```yaml
sources:
  - key: lecun2015             # ключ для ссылок в тексте: [@lecun2015]
    type: article              # article | book | chapter | conference | thesis | web | law | other
    authors: ["LeCun, Yann", "Bengio, Yoshua", "Hinton, Geoffrey"]
    title: "Deep learning"
    container: "Nature"        # журнал / сборник / книга (для chapter) / сайт (для web)
    year: 2015
    volume: "521"
    issue: "7553"
    pages: "436-444"           # для article/chapter/conference — страницы; для book — total_pages
    doi: "10.1038/nature14539"
    lang: en
    origin: openalex           # откуда взяли: crossref | openalex | cyberleninka | elibrary | user | manual
    verified: true             # ставит ТОЛЬКО verify_sources.py
    verified_by: crossref      # crossref | doi.org | openalex | url | file
    verified_at: "2026-10-30"
    match: {title: "Deep learning", year: 2015, doi: "10.1038/nature14539", score: 1.0}
```

## Поля

| Поле | Для каких типов | Что |
|---|---|---|
| `key` | все | латиница, уникальный |
| `type` | все | вид издания — от него зависит описание |
| `authors[]` | все, кроме безавторских | `"Фамилия, Имя Отчество"` или `"Фамилия, И. О."`; для латиницы `"Family, Given"` |
| `editors[]` | chapter, conference | редакторы сборника |
| `title` | все | заглавие как в источнике |
| `subtitle` | book | сведения к заглавию: «учебное пособие», «монография» |
| `container` | article, chapter, conference, web | журнал, сборник, книга, сайт |
| `year`, `volume`, `issue`, `pages` | article, conference, chapter | выходные данные |
| `edition` | book | «2-е изд., перераб. и доп.» |
| `city`, `publisher` | book, chapter, conference, thesis | место и издательство |
| `total_pages` | book, thesis | объём, с. |
| `isbn`, `issn` | book / article | необязательно |
| `doi` | любые | без `https://doi.org/` |
| `url`, `accessed` | web, law, электронные | дата обращения `ГГГГ-ММ-ДД` |
| `degree`, `specialty` | thesis | «канд. техн. наук», «05.13.01» |
| `note` | law, other | вид и дата документа: «Закон Кыргызской Республики от 30 апреля 2003 года № 92» |
| `file` | любые | путь к PDF/docx источника у автора — тогда проверка по тексту файла |
| `lang` | все | `ru` · `ky` · `en` · … — для сортировки и «и др.» / «et al.» |
| `origin` | все | откуда запись |
| `verified`, `verified_by`, `verified_at`, `match` | все | ставит `verify_sources.py`, руками не правим |
| `verify_note` | все | почему не подтверждено / что расходится |

## Правило проверки

`verified: true` появляется **только** когда `verify_sources.py` нашёл запись:

1. есть `doi` → Crossref `/works/{doi}`, если там нет — doi.org (DataCite и др.);
   заглавие записи должно совпасть с `title` (похожесть ≥ 0,85), иначе DOI
   ведёт на другую работу → `verified: false`;
2. нет DOI → поиск по заглавию в OpenAlex, затем в Crossref; совпадение
   заглавия ≥ 0,85, год ±1, фамилия первого автора;
3. есть `url` (КиберЛенинка, сайт журнала, cbd.minjust.gov.kg) → страница
   открывается и заглавие есть в `citation_title` / `<title>` / тексте;
4. есть `file` → заглавие найдено в тексте файла автора.

Ничего не совпало — `verified: false` и `verify_note`. В чистовик такой
источник не попадает, в тексте ссылка на него печатается как `[НЕ ПРОВЕРЕНО]`.

## Где искать без API

- **КиберЛенинка** (cyberleninka.ru) — официального API нет. Автор ищет на
  сайте сам и даёт ссылку на страницу статьи; запись — `origin: cyberleninka`,
  `url: …`; проверка — по странице (п. 3).
- **eLibrary** (elibrary.ru) — API нет, сайт закрыт для скриптов. Автор даёт
  ссылку и выходные данные; если у статьи есть DOI — проверяем по DOI, иначе
  нужен файл статьи (п. 4) или ссылка на сайт журнала.
- **Законы и постановления КР** — Централизованный банк данных правовой
  информации (cbd.minjust.gov.kg): `type: law`, `url`, `note`.
- **Книги без DOI** — по ISBN и выходным данным из файла / фото титула (п. 4).
