from flask import Flask, request, jsonify
from database.connect_to_db import connect_to_mongodb
from database.db_utils import *
from bson import json_util
import json

# Declare MongoDB connection here; avoid reconnection per request
client, db = connect_to_mongodb("config.json")

def create_app():
    app = Flask(__name__)

    @app.route('/movies', methods=['GET'])
    def get_movies():
        movies = get_all_movies(db)
        return json.loads(json_util.dumps(movies))

    @app.route('/movies/<int:tmdb_id>', methods=['GET'])
    def get_movie(tmdb_id: int):
        movie = get_movie_by_id(db, tmdb_id)
        if movie:
            return json.loads(json_util.dumps(movie))
        return jsonify({"error": "Movie not found"}), 404

    @app.route('/movies', methods=['POST'])
    def add_movie():
        result = insert_movie(db, request.json)
        return jsonify(result), 201

    @app.route('/movies/<int:tmdb_id>', methods=['DELETE'])
    def delete_movie(tmdb_id: int):
        result = delete_movie_by_id(db, tmdb_id)
        if result['deleted_count'] > 0:
            return jsonify({"message": "Movie deleted successfully"}), 200
        return jsonify({"error": "Movie not found"}), 404

    return app