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

def write_to_csv(username: str, user_movie_data: List[Dict[str, any]]) -> None:
    def _safe_get(data: Dict[str, any], key: str, default: str = ''):
        return str(data.get(key, default)).replace(',', ';')

    with open(f"{username}.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["tmdb_id", "title", "directors", "genres",
                         "release_year", "num_ratings", "avg_rating",
                         "runtime", "username", "liked", "rating"])

        for data in user_movie_data:
            try:
                writer.writerow([
                    _safe_get(data, 'tmdb_id'),
                    _safe_get(data, 'title'),
                    _safe_get(data, 'directors'),
                    _safe_get(data, 'genres'),
                    _safe_get(data, 'release_year'),
                    _safe_get(data, 'num_ratings'),
                    _safe_get(data, 'avg_rating'),
                    _safe_get(data, 'runtime'),
                    _safe_get(data['user_ratings'][0], 'username')
                                if data.get('user_ratings') else '',
                    _safe_get(data['user_ratings'][0], 'liked')
                                if data.get('user_ratings') else '',
                    _safe_get(data['user_ratings'][0], 'rating')
                                if data.get('user_ratings') else ''
                ])
            except Exception as e:
                print(f"Exception {e} caught when processing {data}")

    print(f"Data has been written to {username}.csv")

if __name__ == "__main__":
    username = "mscorsese"
    user_movie_data = asyncio.run(get_user_movie_data(username))
    write_to_csv(username, user_movie_data)