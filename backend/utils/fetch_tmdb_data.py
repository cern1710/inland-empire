import json
from tmdbv3api import TMDb, Movie
from typing import Dict, Any, Tuple

DEFAULT_CONFIG_PATH = "../config.json"

def init_tmdb() -> Tuple[TMDb, Movie]:
    tmdb = TMDb()
    tmdb.api_key = load_config()['tmdb']['api_key']
    movie = Movie()
    return tmdb, movie

def load_config(config_path: str = DEFAULT_CONFIG_PATH) -> dict:
    with open(config_path, 'r') as file:
        return json.load(file)

def get_tmdb_data(film_name: str) -> Dict[str, Any]:
    """Get movie information from TMDB based on film name."""
    tmdb, movie = init_tmdb()
    search = movie.search(film_name)

    if len(search.results) > 0:
        tmdb_id = search[0].id
        credits = movie.credits(tmdb_id)
        directors = [crew['id'] for crew in credits.get('crew', [])
                     if crew['job'] == 'Director']

        tmdb_data = {
            'tmdb_id': tmdb_id,
            'title': search[0].title,
            'directors': directors,
            'original_language': search[0].original_language,
            'genre_ids': search[0].genre_ids,
            'release_date': search[0].release_date,
            'popularity': search[0].popularity,
            'vote_average': search[0].vote_average
        }
        return tmdb_data
    return None