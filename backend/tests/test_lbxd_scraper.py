import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.scrape_movie_gallery import _get_num_pages, _parse_gallery_page
from utils.scrape_movie_data import parse_movie_data

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def _load_fixture(name: str) -> str:
    with open(os.path.join(FIXTURE_DIR, name), encoding="utf-8") as f:
        return f.read()


@pytest.fixture(scope="module")
def gallery_html() -> str:
    return _load_fixture("user_films.html")


@pytest.fixture(scope="module")
def film_html() -> str:
    return _load_fixture("film_page.html")


def test_parse_gallery_extracts_slugs(gallery_html):
    films = _parse_gallery_page(gallery_html)

    assert films, "expected films in the poster grid"
    assert all(film["film_slug"] for film in films)


def test_parse_gallery_extracts_ratings_and_likes(gallery_html):
    films = _parse_gallery_page(gallery_html)

    ratings = [film["rating"] for film in films if film["rating"] is not None]
    assert ratings, "expected at least one rated film"
    # Letterboxd rates out of 10 (rated-10 == 5 stars)
    assert all(1 <= rating <= 10 for rating in ratings)
    assert any(film["liked"] for film in films)
    assert all(isinstance(film["liked"], bool) for film in films)


def test_get_num_pages(gallery_html):
    assert _get_num_pages(gallery_html) >= 1


def test_parse_movie_data(film_html):
    movie = {"liked": True, "rating": 8}
    data = parse_movie_data(
        film_html, "https://letterboxd.com/film/yeelen/", movie, "u"
    )

    assert data["tmdb_id"] == 71329
    assert data["title"] == "Yeelen"
    assert data["release_year"] == 1987
    assert data["directors"] == ["souleymane-cisse"]
    assert set(data["genres"]) == {"Fantasy", "Drama"}
    assert data["runtime"] == 105
    assert data["avg_rating"] is not None
    assert data["num_ratings"] is not None
    assert data["user_ratings"] == [{"username": "u", "liked": True, "rating": 8}]


def test_parse_movie_data_without_user(film_html):
    data = parse_movie_data(
        film_html, "https://letterboxd.com/film/yeelen/", None, None
    )

    assert data["user_ratings"] == []
