import sys
import os
import asyncio
import csv
from typing import List, Dict, Any

SLEEP_INTERVAL = 0.5
CHUNK_SIZE = 200

# Add parent directory to Python path
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PARENT_DIR)

from utils import scrape_user_ratings, scrape_movies
from database import connect_to_mongodb, insert_movie

async def get_user_movie_data(username: str) -> List[Dict[str, Any]]:
    film_slugs = await scrape_user_ratings(username)
    print(f"Found {len(film_slugs)} films for {username}!")

    chunks = [film_slugs[i : i + CHUNK_SIZE]
              for i in range(0, len(film_slugs), CHUNK_SIZE)]
    chunk_len = len(chunks)

    user_movie_data = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1} of {chunk_len}")

        # TODO: what if another user's data is already in the database?
        chunk_data = await scrape_movies(chunk, username)
        user_movie_data.extend(chunk_data)
        if i < chunk_len - 1:
            await asyncio.sleep(SLEEP_INTERVAL)

    return user_movie_data

def write_to_csv(username: str, user_movie_data: List[Dict[str, Any]]) -> None:
    def _safe_get(data: Dict[str, any], key: str, default: str = ''):
        return str(data.get(key, default)).replace(',', ';')

    filename = f"{username}.csv"
    fieldnames = ["tmdb_id", "title", "directors", "genres",
                    "release_year", "num_ratings", "avg_rating",
                    "runtime", "username", "liked", "rating"]

    with open(filename, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for data in user_movie_data:
            try:
                row = {field: _safe_get(data, field)
                        for field in fieldnames[:8]}
                if data.get('user_ratings'):
                    user_rating = data['user_ratings'][0]
                    row.update({
                        'username': _safe_get(user_rating, 'username'),
                        'liked': _safe_get(user_rating, 'liked'),
                        'rating': _safe_get(user_rating, 'rating')
                    })
                writer.writerow(row)
            except Exception as e:
                print(f"Error processing movie data: {e}")
                print(f"Problematic data: {data}")

    print(f"Data has been written to {username}.csv")

def save_user_data_to_db(username: str) -> None:
    """Saves a user's movie ratings into the database."""
    user_movie_data = asyncio.run(get_user_movie_data(username))
    _, db = connect_to_mongodb()
    for movie in user_movie_data:
        insert_movie(db, movie)
    print(f"All movies in {username}'s diary have been added to the database.")