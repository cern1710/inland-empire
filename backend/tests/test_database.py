import fetch_tmdb_data, database, db_utils

if __name__ == "__main__":
    film_data = fetch_tmdb_data.get_tmdb_data("Inland Empire")
    client, db = database.connect_to_mongodb()
    # db_utils.insert_movie(db, film_data)
    movies = db_utils.get_all_movies(db)
    print(movies)