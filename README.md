# Inland Empire

A movie recommender system based on Letterboxd data. Inland Empire provides tailored movie suggestions to cinephiles based on their film ratings and personal preferences.

## Layout

```text
src/inland_empire/   # application: server, database, recommender, scraping utils
scripts/             # one-off entry points (scrape a user, scrape a user's followers, ...)
tests/               # pytest suite
config/              # config.example.yaml (committed) + config.yaml (gitignored)
data/                # scrape output lands here (gitignored)
```

## Setting up

1. **Python 3.11+**, then install the project in editable mode along with its dependencies:

   ```sh
   python -m venv .venv && source .venv/bin/activate
   pip install -e .
   ```

2. **Redis**: install it via the [Redis install docs](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/).

3. **MongoDB**: install [MongoDB Community Server](https://www.mongodb.com/try/download/community).

4. **Config**: copy the template and fill in your own values.

   ```sh
   cp config/config.example.yaml config/config.yaml
   ```

   ```yaml
   tmdb:
     api_key: YOUR_TMDB_API_KEY

   mongodb_local:
     uri: "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.0.2"
     database: letterboxd_db

   mongodb_atlas:
     uri: "mongodb+srv://<username>:<password>@<username>.ivddo.mongodb.net/?retryWrites=true&w=majority"
     database: letterboxd_db
     username: YOUR_CLUSTER_NAME
     password: YOUR_CLUSTER_PASSWORD
   ```

   `config/config.yaml` is gitignored. By default the app connects to `mongodb_local`; to use Atlas instead, change `MONGO` in `src/inland_empire/database/connect_to_db.py`.

   You can also point at a config file somewhere else by setting `INLAND_EMPIRE_CONFIG=/path/to/config.yaml` instead of using `config/config.yaml`.

## Running it

```sh
scripts/init_backend.sh   # starts mongod + redis-server
python run.py             # starts the Flask app
scripts/exit_backend.sh   # stops mongod
```

## Scraping data

```sh
# One user's ratings -> data/<username>.csv
python scripts/scrape_user.py <username>

# One user's ratings -> MongoDB
python scripts/scrape_user.py <username> --to db

# Every one of a user's following' ratings -> data/following/<username>.csv each. Usernames that already have a CSV are skipped.
python scripts/scrape_following.py <username>
```

## Tests

```sh
pytest -m "not live"   # unit tests without network calls
pytest                 # includes tests that hit Letterboxd site (slow)
```
