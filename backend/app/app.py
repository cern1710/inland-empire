from flask import Blueprint, Flask, request, jsonify
from database.connect_to_db import connect_to_mongodb
from database.db_utils import *
import redis
from bson import json_util
import json

CACHE_EXPIRATION = 3600

movies_bp = Blueprint('movies', __name__)
client, db = connect_to_mongodb("config.json")
redis_client = redis.Redis()

@movies_bp.route('/movies', methods=['GET'])
def get_movies():
    if cached_movies := redis_client.get('all_movies'):
        return json.loads(cached_movies)

    movies = get_all_movies(db)
    movies_json = json.loads(json_util.dumps(movies))
    redis_client.setex(
        'all_movies',
        CACHE_EXPIRATION,
        json.dumps(movies_json)
    )
    return movies_json

@movies_bp.route('/movies/<int:tmdb_id>', methods=['GET'])
def get_movie(tmdb_id: int):
    if cached_movie := redis_client.get(f'movie:{tmdb_id}'):
        return json.loads(cached_movie)

    movie = get_movie_by_id(db, tmdb_id)
    if movie:
        movie_json = json.loads(json_util.dumps(movie))
        redis_client.setex(
            f'movie:{tmdb_id}',
            CACHE_EXPIRATION,
            json.dumps(movie_json)
        )
        return movie_json
    return jsonify({"error": "Movie not found"}), 404

@movies_bp.route('/movies', methods=['POST'])
def add_movie():
    result = insert_movie(db, request.json)
    redis_client.delete('all_movies')
    return jsonify(result), 201

@movies_bp.route('/movies/<int:tmdb_id>', methods=['DELETE'])
def delete_movie(tmdb_id: int):
    result = delete_movie_by_id(db, tmdb_id)
    if result['deleted_count'] > 0:
        redis_client.delete(f'movie:{tmdb_id}')
        redis_client.delete('all_movies')
        return jsonify({"message": "Movie deleted successfully"}), 200
    return jsonify({"error": "Movie not found"}), 404

def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(movies_bp)
    return app