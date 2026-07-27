from urllib.parse import quote_plus

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConfigurationError, ConnectionFailure

from inland_empire.config import load_config

MONGO = "mongodb_local"


def get_mongodb_client(config: dict | None = None) -> tuple[MongoClient, dict]:
    """Create MongoDB client using specified configurations."""
    config = config or load_config()
    mongo_config = config[MONGO]
    if MONGO == "mongodb_atlas":
        username = quote_plus(mongo_config["username"])
        password = quote_plus(mongo_config["password"])
        uri = (
            mongo_config["uri"]
            .replace("<password>", password)
            .replace("<username>", username)
        )
    else:
        uri = mongo_config["uri"]
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)    # 5 seconds

    return client, config


def connect_to_mongodb(
    config: dict | None = None,
) -> tuple[MongoClient, Database]:
    """Connect to MongoDB and return the client and database."""
    try:
        client, config = get_mongodb_client(config)
        db_name = config[MONGO]["database"]
        db = client[db_name]
        client.admin.command("ismaster")    # Verify the connection
        return client, db
    except (ConnectionFailure, ConfigurationError) as e:
        print(f"Failed to connect to MongoDB: {str(e)}")
        raise
