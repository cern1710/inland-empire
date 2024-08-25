# Inland Empire

A movie recommender system based on Letterboxd data. Inland Empire provides tailored movie suggestions to cinephiles based on their film ratings and personal preferences.

## Setting up

Create a `config.json` file in `/backend` with the following:

```json
{
  "tmdb": {
    "api_key": "YOUR_TMDB_API_KEY"
  },

  "mongodb": {
    "uri": "mongodb+srv://<username>:<password>@<username>.ivddo.mongodb.net/?retryWrites=true&w=majority",
    "database": "letterboxd_db",
    "username": "YOUR_CLUSTER_NAME",
    "password": "YOUR_CLUSTER_PASSWORD"
  }
}
```

This will allow the application to connect to your MongoDB Atlas cluster.
