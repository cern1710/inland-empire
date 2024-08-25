import json
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ConfigurationError
from urllib.parse import quote_plus
from typing import Tuple

DEFAULT_CONFIG_PATH = "config.json"

def get_mongodb_client(config_path: str) -> Tuple[MongoClient, dict]:
    """Create MongoDB Atlas client using specified configurations."""
    def _load_config(config_path: str) -> dict:
        with open(config_path, 'r') as file:
            return json.load(file)

    config = _load_config(config_path)
    mongo_config = config['mongodb']
    username = quote_plus(mongo_config['username'])
    password = quote_plus(mongo_config['password'])

    # Construct full connection URI
    uri = mongo_config['uri'].replace('<password>', password).replace('<username>', username)
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)

    return client, config

def connect_to_mongodb(config_path: str = DEFAULT_CONFIG_PATH) -> Tuple[MongoClient, Database]:
    """Connect to MongoDB Atlas and return the client and database."""
    try:
        client, config = get_mongodb_client(config_path)
        db_name = config['mongodb']['database']
        db = client[db_name]
        client.admin.command('ismaster')    # Verify the connection
        print("Successfully connected to MongoDB Atlas!")
        return client, db
    except (ConnectionFailure, ConfigurationError) as e:
        print(f"Failed to connect to MongoDB Atlas: {str(e)}")
        raise