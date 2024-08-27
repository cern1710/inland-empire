import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import *

if __name__ == "__main__":
    movies = [{'film_slug':'inland-empire'}, {'film_slug':'satantango'},
              {'film_slug':'sicily'}]
    info = asyncio.run(scrape_movies(movies))
    print(info)