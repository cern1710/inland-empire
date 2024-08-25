import json
from tmdbv3api import TMDb, Movie, Genre
from typing import Dict, Any, Tuple

DEFAULT_CONFIG_PATH = "config.json"

def init_tmdb() -> Tuple[TMDb, Movie, Genre]:
    tmdb = TMDb()
    tmdb.api_key = load_config()['tmdb']['api_key']
    movie, genre = Movie(), Genre
    return tmdb, movie, genre

def load_config(config_path: str = DEFAULT_CONFIG_PATH) -> dict:
    with open(config_path, 'r') as file:
        return json.load(file)

def get_tmdb_data(film_name: str) -> Dict[str, Any]:
    """Get movie information from TMDB based on film name."""
    tmdb, movie, genre = init_tmdb()
    search = movie.search(film_name)
    if search:
        tmdb_data = {
            'tmdb_id': search[0].id,
            'original_language': search[0].original_language,
            'genre_ids': search[0].genre_ids,
            'release_date': search[0].release_date,
            'popularity': search[0].popularity,
            'vote_average': search[0].vote_average
        }
        return tmdb_data
    return None