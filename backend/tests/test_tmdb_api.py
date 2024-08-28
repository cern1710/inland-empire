import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import *

@pytest.fixture(scope="module")
def tmdb_setup():
    init_tmdb("../config.json")

def remove_key_from_list_of_dicts(lst, key):
    """Remove specified key from all dictionaries in a list."""
    for item in lst:
        if key in item:
            del item[key]
    return lst

def test_get_tmdb_data(tmdb_setup):
    movies = [1730, 104871, 31414, 76819]
    expected_info = [
        {
            'tmdb_id': 1730,
            'title': 'Inland Empire',
            'directors': [{'id': 5602, 'name': 'David Lynch'}],
            'genres': ['Thriller', 'Mystery', 'Fantasy', 'Horror'],
            'release_year': 2006,
            'runtime': 180,
            'user_rating': []
        },
        {
            'tmdb_id': 104871,
            'title': 'Sicily!',
            'directors': [{'id': 935136, 'name': 'Jean-Marie Straub'},
                          {'id': 935137, 'name': 'Danièle Huillet'}],
            'genres': ['Drama'],
            'release_year': 1999,
            'runtime': 66,
            'user_rating': []
        },
        {
            'tmdb_id': 31414,
            'title': 'Satantango',
            'directors': [{'id': 85637, 'name': 'Béla Tarr'}],
            'genres': ['Drama'],
            'release_year': 1994,
            'runtime': 432,
            'user_rating': []
        },
        {
            'tmdb_id': 76819,
            'title': 'Teenage Hooker Became A Killing Machine In Daehakro',
            'directors': [{'id': 1371835, 'name': 'Nam Gee-woong'}],
            'genres': ['Science Fiction', 'Horror'],
            'release_year': 2000,
            'runtime': 60,
            'user_rating': []
        }
    ]

    info = [get_tmdb_data(movie) for movie in movies]
    info_filtered = remove_key_from_list_of_dicts(info, 'popularity')
    assert info_filtered == expected_info