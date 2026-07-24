import csv
import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.scrape_movie_gallery import scrape_user_ratings
from utils.user_movie_preprocessing import get_user_movie_data, write_to_csv

USERNAME = "cern1710"


@pytest.mark.live
@pytest.mark.asyncio
async def test_scrape_user_gallery_pages():
    """Every page of the user's gallery is fetched and parsed."""
    films = await scrape_user_ratings(USERNAME)

    assert len(films) > 1000, f"expected a full library, got {len(films)}"

    slugs = [film["film_slug"] for film in films]
    assert all(slugs), "every film must have a slug"
    # Pagination bugs typically show up as repeated pages.
    assert len(set(slugs)) == len(slugs), "duplicate slugs suggest a paging bug"

    ratings = [f["rating"] for f in films if f["rating"] is not None]
    assert ratings, "expected rated films"
    assert all(1 <= rating <= 10 for rating in ratings)
    assert any(film["liked"] for film in films)


@pytest.mark.live
@pytest.mark.asyncio
async def test_scrape_user_data_to_csv(tmp_path):
    """Full pipeline: scrape every film, then write it out as CSV."""
    user_movie_data = await get_user_movie_data(USERNAME)
    assert len(user_movie_data) > 1000

    resolved = [m for m in user_movie_data if m and m.get("title")]
    # Allow a small tail of unresolvable entries (TV, deleted films).
    assert len(resolved) > 0.95 * len(user_movie_data), (
        f"only {len(resolved)}/{len(user_movie_data)} films resolved"
    )

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        write_to_csv(USERNAME, user_movie_data)
    finally:
        os.chdir(cwd)

    csv_path = tmp_path / f"{USERNAME}.csv"
    assert csv_path.exists()

    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == len(user_movie_data)
    populated = [r for r in rows if r["title"]]
    assert len(populated) > 0.95 * len(rows)
    assert all(r["username"] == USERNAME for r in populated)
    assert any(r["rating"] not in ("", "None") for r in populated)
