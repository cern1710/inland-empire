import json
from tmdbv3api import TMDb, Movie
from typing import Dict, Any, Optional
from datetime import datetime

DEFAULT_CONFIG_PATH = "../config.json"

def init_tmdb(config_path: str = DEFAULT_CONFIG_PATH) -> None:
    """Initialize TMDb API by setting up the API key."""
    tmdb = TMDb()
    with open(config_path, 'r') as file:
        tmdb.api_key = json.load(file)['tmdb']['api_key']
    return

def get_tmdb_data(tmdb_id: int) -> Optional[Dict[str, Any]]:
    """Get movie information from TMDB based on TMDB ID."""
    movie = Movie()
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
        release_date = datetime.strptime(details.release_date, "%Y-%m-%d")
        release_year = release_date.year
    except (ValueError, TypeError):
        release_date = release_year = None

    # Only extract relevant data here (may change later)
    tmdb_data = {
        'tmdb_id': tmdb_id,
        'title': details.title,
        'directors': directors,
        'original_language': details.original_language,
        'genres': genres,
        'release_year': release_year,
        'popularity': details.popularity,
        'runtime': details.runtime,
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