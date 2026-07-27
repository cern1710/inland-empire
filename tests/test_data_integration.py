import pytest

from inland_empire.utils import get_user_movie_data, save_user_data_to_db, write_to_csv


@pytest.mark.asyncio
async def test_get_user_movie_data():
    username = "mscorsese"
    user_movie_data = await get_user_movie_data(username)

    assert isinstance(user_movie_data, list), "Expected a list of movie data"
    assert len(user_movie_data) > 0, "Expected at least one movie in the list"

    fields = [
        "tmdb_id",
        "title",
        "directors",
        "genres",
        "release_year",
        "num_ratings",
        "avg_rating",
        "runtime",
        "user_ratings",
    ]

    for movie in user_movie_data:
        for field in fields:
            assert field in movie
