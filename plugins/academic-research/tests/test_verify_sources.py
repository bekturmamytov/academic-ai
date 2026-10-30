"""verify_sources без сети (httpx.MockTransport) + одна живая проверка по ACADEMIC_LIVE=1."""
import os
from pathlib import Path

import httpx
import pytest

from scholarly import make_client
from verify_sources import verify_entry

LECUN_CR = {"message": {"DOI": "10.1038/nature14539", "type": "journal-article", "title": ["Deep learning"],
                        "author": [{"family": "LeCun", "given": "Yann"}, {"family": "Bengio", "given": "Yoshua"}],
                        "container-title": ["Nature"], "issued": {"date-parts": [[2015, 5, 27]]},
                        "volume": "521", "issue": "7553", "page": "436-444", "publisher": "Springer"}}
OA_RESNET = {"results": [{"id": "https://openalex.org/W1", "title": "Deep Residual Learning for Image Recognition",
                          "type": "article", "publication_year": 2016, "doi": "https://doi.org/10.1109/cvpr.2016.90",
                          "authorships": [{"author": {"display_name": "Kaiming He"}}],
                          "primary_location": {"source": {"display_name": "CVPR"}},
                          "biblio": {"first_page": "770", "last_page": "778"}}]}


def handler(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    if "api.crossref.org/works/10.1038/nature14539" in url:
        return httpx.Response(200, json=LECUN_CR)
    if "api.crossref.org/works/" in url and "/works?" not in url:
        return httpx.Response(404, text="Resource not found.")
    if url.startswith("https://doi.org/"):
        return httpx.Response(404, text="DOI Not Found")
    if "api.openalex.org/works" in url:
        if "residual" in url.lower():
            return httpx.Response(200, json=OA_RESNET)
        return httpx.Response(200, json={"results": []})
    if "api.crossref.org/works?" in url:
        return httpx.Response(200, json={"message": {"items": []}})
    if "cyberleninka.ru/article/n/real" in url:
        return httpx.Response(200, text='<html><head><meta name="citation_title" content="Цифровизация '
                                        'образования в Кыргызстане"></head><body>…</body></html>')
    if "cyberleninka.ru" in url:
        return httpx.Response(404)
    return httpx.Response(500)


@pytest.fixture
def client():
    with make_client(transport=httpx.MockTransport(handler)) as c:
        yield c


def test_real_doi_verified_and_filled(client):
    e = {"key": "lecun", "title": "Deep learning", "authors": ["LeCun, Yann"], "doi": "https://doi.org/10.1038/nature14539"}
    verify_entry(client, e, Path("."))
    assert e["verified"] is True and e["verified_by"] == "crossref"
    assert e["container"] == "Nature" and e["year"] == 2015 and e["pages"] == "436-444"


def test_fake_doi_not_verified(client):
    e = {"key": "fake", "title": "Нейросетевые методы прогнозирования урожайности в Чуйской долине",
         "year": 2019, "doi": "10.99999/kstu.2019.3.45", "verified": True}
    verify_entry(client, e, Path("."))
    assert e["verified"] is False
    assert "не найден" in e["verify_note"]


def test_doi_of_another_work_not_verified(client):
    e = {"key": "wrong", "title": "Quantum gravity in hydroponic tomatoes", "year": 2015, "doi": "10.1038/nature14539"}
    verify_entry(client, e, Path("."))
    assert e["verified"] is False and "другую работу" in e["verify_note"]


def test_title_search_without_doi(client):
    e = {"key": "he", "title": "Deep residual learning for image recognition", "authors": ["He, Kaiming"], "year": 2016}
    verify_entry(client, e, Path("."))
    assert e["verified"] is True and e["verified_by"] == "openalex"
    assert e["doi"] == "10.1109/cvpr.2016.90"


def test_title_found_but_year_differs(client):
    e = {"key": "he", "title": "Deep Residual Learning for Image Recognition", "year": 2010}
    verify_entry(client, e, Path("."))
    assert e["verified"] is False


def test_url_check(client):
    ok = {"key": "c1", "title": "Цифровизация образования в Кыргызстане", "url": "https://cyberleninka.ru/article/n/real"}
    bad = {"key": "c2", "title": "Чего нет", "url": "https://cyberleninka.ru/article/n/none"}
    verify_entry(client, ok, Path("."))
    verify_entry(client, bad, Path("."))
    assert ok["verified"] is True and ok["verified_by"] == "url"
    assert bad["verified"] is False and "не открылась" in bad["verify_note"]


def test_user_file(client, tmp_path):
    (tmp_path / "book.txt").write_text("Иванов И. И. ОСНОВЫ ВИБРОДИАГНОСТИКИ. Учебное пособие", encoding="utf-8")
    e = {"key": "b", "title": "Основы вибродиагностики", "file": "book.txt", "year": 1990}
    verify_entry(client, e, tmp_path)
    assert e["verified"] is True and e["verified_by"] == "file"


def test_network_error_leaves_status(tmp_path):
    def boom(request):
        raise httpx.ConnectError("offline")

    with make_client(transport=httpx.MockTransport(boom)) as c:
        e = {"key": "x", "title": "Deep learning", "doi": "10.1038/nature14539", "verified": True}
        verify_entry(c, e, tmp_path)
    assert e["verified"] is True and "нет связи" in e["verify_note"]


@pytest.mark.skipif(os.environ.get("ACADEMIC_LIVE") != "1", reason="живая проверка: ACADEMIC_LIVE=1")
def test_live_crossref():
    with make_client() as c:
        real = {"key": "lecun", "title": "Deep learning", "doi": "10.1038/nature14539"}
        fake = {"key": "fake", "title": "Нейросетевые методы прогнозирования урожайности в Чуйской долине",
                "doi": "10.99999/kstu.2019.3.45"}
        verify_entry(c, real, Path("."))
        verify_entry(c, fake, Path("."))
    assert real["verified"] is True and fake["verified"] is False
