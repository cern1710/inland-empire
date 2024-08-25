import json
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ConfigurationError
from urllib.parse import quote_plus
from typing import Tuple

DEFAULT_CONFIG_PATH = "../config.json"
MONGO = "mongodb_local"

def get_mongodb_client(config_path: str) -> Tuple[MongoClient, dict]:
    """Create MongoDB client using specified configurations."""
    def _load_config(config_path: str) -> dict:
        with open(config_path, 'r') as file:
            return json.load(file)

    config = _load_config(config_path)
    mongo_config = config[MONGO]
    if MONGO == "mongodb_atlas":
        username = quote_plus(mongo_config['username'])
        password = quote_plus(mongo_config['password'])
        uri = mongo_config['uri'].replace('<password>', password).replace('<username>', username)
    else:
        uri = mongo_config['uri']
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)

    return client, config

def connect_to_mongodb(config_path: str = DEFAULT_CONFIG_PATH) -> Tuple[MongoClient, Database]:
    """Connect to MongoDB and return the client and database."""
    try:
        client, config = get_mongodb_client(config_path)
        db_name = config[MONGO]['database']
        db = client[db_name]
        client.admin.command('ismaster')    # Verify the connection
        return client, db
    except (ConnectionFailure, ConfigurationError) as e:
        print(f"Failed to connect to MongoDB: {str(e)}")
        raise