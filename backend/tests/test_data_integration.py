import sys
import os
import asyncio
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import *
from database import *

def split_list(lst, chunk_size):
    return [lst[i:i + chunk_size]
            for i in range(0, len(lst), chunk_size)]

async def scrape_with_delay(film_slugs_chunk):
    tmdb_ids = await scrape_movies(film_slugs_chunk)
    return tmdb_ids

async def main():
    print("Scraping user ratings...")
    film_slugs = await scrape_user_ratings("schaffrillas")
    print(f"Found {len(film_slugs)} films")

    # TODO: Doesn't quite work for users with many ratings
    sleep_time = 0.5
    chunk_size = 200
    chunks = split_list(film_slugs, chunk_size)

    all_tmdb_ids = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1} of {len(chunks)}")
        chunk_tmdb_ids = await scrape_with_delay(chunk)
        all_tmdb_ids.extend(chunk_tmdb_ids)
        if i < len(chunks) - 1:
            print(f"Sleeping for {sleep_time} second(s)...")
            await asyncio.sleep(sleep_time)

    print("Test complete. All chunks processed!")
    return all_tmdb_ids

if __name__ == "__main__":
    tmdb_ids = asyncio.run(main())
    init_tmdb()
    tmdb_data = []

    count = 0
    for tmdb_id in tmdb_ids:
        tmdb_data.append(get_tmdb_data(tmdb_id['tmdb_id']))
        count += 1
        if count >= 50:
            time.sleep(2.0)
            count = 0

    print(tmdb_data)