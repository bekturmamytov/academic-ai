from format_refs import cite, format_entry, parse_name, plain, sort_entries

LECUN = {"key": "lecun2015", "type": "article", "authors": ["LeCun, Yann", "Bengio, Yoshua", "Hinton, Geoffrey"],
         "title": "Deep learning", "container": "Nature", "year": 2015, "volume": "521", "issue": "7553",
         "pages": "436-444", "doi": "10.1038/nature14539", "lang": "en"}
BOOK = {"key": "ivanov2020", "type": "book", "authors": ["Иванов, Иван Иванович"], "title": "Основы вибродиагностики",
        "subtitle": "учебное пособие", "edition": "2-е изд., перераб. и доп.", "city": "Бишкек",
        "publisher": "Илим", "year": 2020, "total_pages": 320, "isbn": "978-9967-00-000-0", "lang": "ru"}
FIVE = {"key": "five", "type": "article", "lang": "ru", "title": "Анализ данных", "container": "Вестник КГТУ",
        "year": 2021, "issue": "3", "pages": "10-20",
        "authors": ["Асанов А. А.", "Бекова Б. Б.", "Петров П. П.", "Сидоров С. С.", "Кузнецов К. К."]}
WEB = {"key": "web", "type": "web", "title": "Численность населения", "container": "Нацстатком КР",
       "url": "https://stat.gov.kg", "accessed": "2026-10-30", "lang": "ru"}
CONF = {"key": "he2016", "type": "conference", "authors": ["He, Kaiming", "Zhang, Xiangyu", "Ren, Shaoqing", "Sun, Jian"],
        "title": "Deep Residual Learning for Image Recognition", "container": "Proc. CVPR", "year": 2016,
        "pages": "770-778", "doi": "10.1109/CVPR.2016.90"}


def test_gost_article():
    assert plain(format_entry(LECUN, "gost")) == (
        "LeCun, Y. Deep learning / Y. LeCun, Y. Bengio, G. Hinton // Nature. – 2015. – "
        "Vol. 521, No. 7553. – P. 436–444. – DOI 10.1038/nature14539.")


def test_gost_book():
    assert plain(format_entry(BOOK, "gost")) == (
        "Иванов, И. И. Основы вибродиагностики : учебное пособие / И. И. Иванов. – "
        "2-е изд., перераб. и доп. – Бишкек : Илим, 2020. – 320 с. – ISBN 978-9967-00-000-0.")


def test_gost_five_authors_title_first():
    s = plain(format_entry(FIVE, "gost"))
    assert s == ("Анализ данных / А. А. Асанов, Б. Б. Бекова, П. П. Петров [и др.] // Вестник КГТУ. – "
                 "2021. – № 3. – С. 10–20.")


def test_gost_four_authors_all_listed_title_first():
    s = plain(format_entry(CONF, "gost"))
    assert s.startswith("Deep Residual Learning for Image Recognition / K. He, X. Zhang, S. Ren, J. Sun // Proc. CVPR")


def test_gost_web():
    assert plain(format_entry(WEB, "gost")) == (
        "Численность населения. – Текст : электронный // Нацстатком КР. – "
        "URL: https://stat.gov.kg (дата обращения: 30.10.2026).")


def test_apa_article_italics():
    runs = format_entry(LECUN, "apa")
    assert plain(runs) == ("LeCun, Y., Bengio, Y., & Hinton, G. (2015). Deep learning. Nature, 521(7553), "
                           "436–444. https://doi.org/10.1038/nature14539")
    assert ("Nature", True) in runs and ("521", True) in runs


def test_apa_book():
    assert plain(format_entry(BOOK, "apa")) == (
        "Иванов, И. И. (2020). Основы вибродиагностики (2-е изд., перераб. и доп.). Илим.")


def test_ieee_article():
    assert plain(format_entry(LECUN, "ieee")) == (
        "Y. LeCun, Y. Bengio, and G. Hinton, “Deep learning,” Nature, vol. 521, no. 7553, "
        "pp. 436–444, 2015, doi: 10.1038/nature14539.")


def test_ieee_many_authors_et_al():
    e = dict(LECUN, authors=[f"Author{i}, A." for i in range(8)])
    assert plain(format_entry(e, "ieee")).startswith("A. Author0 et al., ")


def test_parse_name_variants():
    assert parse_name("Иванов Иван Иванович") == ("Иванов", ["И.", "И."])
    assert parse_name("Иванов И.И.") == ("Иванов", ["И.", "И."])
    assert parse_name("И. И. Иванов") == ("Иванов", ["И.", "И."])
    assert parse_name("Yann LeCun") == ("LeCun", ["Y."])
    assert parse_name({"family": "Dupont", "given": "Jean-Pierre"}) == ("Dupont", ["J.-P."])


def test_sort_cyrillic_first():
    keys = [e["key"] for e in sort_entries([LECUN, BOOK, FIVE], "alpha")]
    assert keys == ["five", "ivanov2020", "lecun2015"]


def test_sort_by_citation():
    keys = [e["key"] for e in sort_entries([LECUN, BOOK, FIVE], "cite", ["lecun2015", "five"])]
    assert keys == ["lecun2015", "five", "ivanov2020"]


def test_cite_styles():
    refs = [(BOOK, 3, ""), (LECUN, 1, "с. 437")]
    assert cite(refs, "gost") == "[1, с. 437; 3]"
    assert cite(refs, "ieee") == "[1, с. 437], [3]"
    assert cite([(LECUN, 1, "")], "apa") == "(LeCun et al., 2015)"
    assert cite([(BOOK, 1, "с. 5")], "apa") == "(Иванов, 2020, с. 5)"
