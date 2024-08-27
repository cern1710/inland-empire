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

async def get_user_movie_data(username: str) -> List[Dict[str, any]]:
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