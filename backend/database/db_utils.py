from typing import Dict, Any, List
from pymongo.database import Database
from pymongo.results import UpdateResult, DeleteResult

def insert_movie(db: Database, movie_data: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a movie into the database. Update it if already in database."""
    collection = db['movies']
    query = {'tmdb_id': movie_data['tmdb_id']}  # TMDB DB = identifier

    # Enable upsert: either insert a new document or update an existing one
    result: UpdateResult = collection.update_one(query,
                                                 {'$set': movie_data},
                                                 upsert=True)

    return {
        'acknowledged': result.acknowledged,
        'matched_count': result.matched_count,
        'modified_count': result.modified_count,
        'upserted_id': str(result.upserted_id) if result.upserted_id else None
    }

def get_movie_by_id(db: Database, tmdb_id: int) -> Dict[str, Any]:
    """Retrieve a movie from the database by its TMDB ID."""
    return db['movies'].find_one({'tmdb_id': tmdb_id})

def get_all_movies(db: Database) -> List[Dict[str, Any]]:
    """Retrieve all movies from the database."""
    return list(db['movies'].find())

def delete_movie_by_id(db: Database, tmdb_id: int) -> Dict[str, Any]:
    """Delete a movie from the database by its TMDB ID."""
    result: DeleteResult = db['movies'].delete_one({'tmdb_id': tmdb_id})
    return {
        'acknowledged': result.acknowledged,
        'deleted_count': result.deleted_count
    }

def purge_db(db: Database) -> Dict[str, Any]:
    """Delete entire movies collection from the database.

    WARNING: Use with extreme caution. This operation will
             delete everything from the database.
    """
    result: DeleteResult = db['movies'].delete_many({})
    return {
        'acknowledged': result.acknowledged,
        'deleted_count': result.deleted_count
    }