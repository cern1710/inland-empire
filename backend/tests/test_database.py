import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import *
from utils import *

def test_database_connection():
    client, db = connect_to_mongodb(config_path="../config.json")
    assert db is not None
    return client, db

def test_insert_and_retrieve_movie(db):
    test_movie = {"tmdb_id": 12345, "title": "Test Movie"}
    insert_movie(db, test_movie)
    movies = get_all_movies(db)
    assert any(movie['tmdb_id'] == 12345 for movie in movies)
    delete_movie_by_id(db, 12345)

if __name__ == "__main__":
    client, db = test_database_connection()
    print("Connected to database!")

    test_insert_and_retrieve_movie(db)
    print("Inserted and retrieved movie!")

    print("All tests passed!")