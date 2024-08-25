# Inland Empire

A movie recommender system based on Letterboxd data. Inland Empire provides tailored movie suggestions to cinephiles based on their film ratings and personal preferences.

## Setting up

### Redis

You can install Redis [here](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/).

### MongoDB

Make sure you downloaded MongoDB Community Server from [here](https://www.mongodb.com/try/download/community).

Create a `config.json` file in `/backend` with the following:

```json
{
  "tmdb": {
    "api_key": "YOUR_TMDB_API_KEY"
  },
  "mongodb_local": {
    "uri": "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.0.2",
    "database": "letterboxd_db"
  },
  "mongodb_atlas": {
    "uri": "mongodb+srv://<username>:<password>@<username>.ivddo.mongodb.net/?retryWrites=true&w=majority",
    "database": "letterboxd_db",
    "username": "YOUR_CLUSTER_NAME",
    "password": "YOUR_CLUSTER_PASSWORD"
  }
}
```

This will allow the application to connect to either your local MongoDB server by default. If you want to connect to your MongoDB Atlas cluster, change this line in `database.py`:

```py
MONGO = "mongodb_atlas" # Change the "mongodb_local" string
```
