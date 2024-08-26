import json
from tmdbv3api import TMDb, Movie, TV
from typing import Dict, Any, Optional
from datetime import datetime

DEFAULT_CONFIG_PATH = "../config.json"

def init_tmdb(config_path: str = DEFAULT_CONFIG_PATH) -> None:
    """Initialize TMDb API by setting up the API key."""
    tmdb = TMDb()
    with open(config_path, 'r') as file:
        tmdb.api_key = json.load(file)['tmdb']['api_key']
    return

def get_tmdb_data(tmdb_id: int, is_movie: bool = True) -> Optional[Dict[str, Any]]:
    """Get movie information from TMDB based on TMDB ID."""
    movie = Movie() if is_movie else TV()

    # TODO: Not sure if I'm being rate limited; can't parse 155292
    #       without getting:
    #
    #   File "/opt/homebrew/lib/python3.11/site-packages/tmdbv3api/objs/movie.py", line 41, in details
    #     return self._request_obj(
    #            ^^^^^^^^^^^^^^^^^^
    #   File "/opt/homebrew/lib/python3.11/site-packages/tmdbv3api/tmdb.py", line 192, in _request_obj
    #     raise TMDbException(json["status_message"])
    # tmdbv3api.exceptions.TMDbException: The resource you requested could not be found.
    details, credits = movie.details(tmdb_id), movie.credits(tmdb_id)

    # Get directors and genres (can have multiple)
    directors = [
        {"id": crew['id'], "name": crew['name']}
        for crew in credits.get('crew', [])
        if crew['job'] == 'Director'
    ]
    genres = [genre['name'] for genre in details.genres]

    # Parse release date using datetime.strptime()
    try:
        if not is_movie:
            release_date = datetime.strptime(details.first_air_date, "%Y-%m-%d")
        else:
            release_date = datetime.strptime(details.release_date, "%Y-%m-%d")
        release_year = release_date.year
    except (ValueError, TypeError):
        release_date = release_year = None

    # Only extract relevant data here (may change later)
    tmdb_data = {
        'tmdb_id': tmdb_id,
        'title': details.title if is_movie else details.original_name,
        'directors': directors,
        'original_language': details.original_language,
        'genres': genres,
        'release_year': release_year,
        'popularity': details.popularity,
        'runtime': details.runtime if is_movie else None,
        # 'num_ratings': details.vote_count,
        # 'avg_rating': details.vote_average,
        # 'release_date': release_date,
        # 'overview': details.overview,
        # 'budget': details.budget,
        # 'revenue': details.revenue,
        # 'poster_path': details.poster_path,
        # 'backdrop_path': details.backdrop_path
        'user_rating': []   # Initialized as an empty list
    }
    return tmdb_data