import pytest
import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import *

@pytest.mark.asyncio
async def test_scrape_movies():
    username = "mscorsese"
    expected_info = [
        {
            'film_slug': 'yeelen',
            'title': 'yeelen',
        },
    ]
    user_ratings = await scrape_user_ratings(username)
    info = await scrape_movies(user_ratings, username=username)