import asyncio
import csv
import os
from typing import Any

from inland_empire.database import connect_to_mongodb, insert_movie

from .scrape_movie_data import scrape_movies
from .scrape_movie_gallery import scrape_user_ratings

CHUNK_SIZE = 200


async def get_user_movie_data(username: str) -> list[dict[str, Any]]:
    film_slugs = await scrape_user_ratings(username)
    print(f"Found {len(film_slugs)} films for {username}!")

    chunks = [
        film_slugs[i : i + CHUNK_SIZE] for i in range(0, len(film_slugs), CHUNK_SIZE)
    ]
    chunk_len = len(chunks)

    user_movie_data = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1} of {chunk_len}")

        # TODO: what if another user's data is already in the database?
        chunk_data = await scrape_movies(chunk, username)
        user_movie_data.extend(chunk_data)

    return user_movie_data


def write_to_csv(
    username: str,
    user_movie_data: list[dict[str, Any]],
    output_dir: str | None = None,
) -> None:
    def _safe_get(data: dict[str, any], key: str, default: str = ""):
        return str(data.get(key, default)).replace(",", ";")

    filename = f"{username}.csv"
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, filename)
    fieldnames = [
        "tmdb_id",
        "title",
        "directors",
        "genres",
        "release_year",
        "num_ratings",
        "avg_rating",
        "runtime",
        "username",
        "liked",
        "rating",
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for data in user_movie_data:
            try:
                row = {field: _safe_get(data, field) for field in fieldnames[:8]}
                if data.get("user_ratings"):
                    user_rating = data["user_ratings"][0]
                    row.update(
                        {
                            "username": _safe_get(user_rating, "username"),
                            "liked": _safe_get(user_rating, "liked"),
                            "rating": _safe_get(user_rating, "rating"),
                        }
                    )
                writer.writerow(row)
            except Exception as e:
                print(f"Error processing movie data: {e}")
                print(f"Problematic data: {data}")

    print(f"Data has been written to {filename}")


def scrape_user(username: str) -> list[dict[str, Any]]:
    """Scrapes every film a user has logged, with their rating and like.

    This is the synchronous entry point: given a Letterboxd username, it
    returns the fully populated movie data.

        >>> movies = scrape_user("<username>")
    """
    return asyncio.run(get_user_movie_data(username))


def scrape_user_to_csv(
    username: str, output_dir: str | None = None
) -> list[dict[str, Any]]:
    """Scrapes a user's films and writes them to <username>.csv."""
    user_movie_data = scrape_user(username)
    write_to_csv(username, user_movie_data, output_dir=output_dir)
    return user_movie_data


def save_user_data_to_db(username: str) -> None:
    """Saves a user's movie ratings into the database."""
    user_movie_data = scrape_user(username)
    _, db = connect_to_mongodb()
    for movie in user_movie_data:
        insert_movie(db, movie)
    print(f"All movies in {username}'s diary have been added to the database.")
