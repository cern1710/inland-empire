import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import *

@pytest.fixture(scope="module")
def db_connection():
    client, db = connect_to_mongodb(config_path="../config.json")
    yield db
    client.close()

def test_database_connection(db_connection):
    assert db_connection is not None

def test_insert_and_retrieve_movie(db_connection):
    test_movie = {"tmdb_id": 12345, "title": "Test Movie"}
    insert_movie(db_connection, test_movie)

    movies = get_all_movies(db_connection)
    assert any(movie['tmdb_id'] == 12345 for movie in movies)

    delete_movie_by_id(db_connection, 12345)
    movies_after_deletion = get_all_movies(db_connection)
    assert not any(movie['tmdb_id'] == 12345 for movie in movies_after_deletion)