import asyncio
from typing import Any

from curl_cffi import requests
from lxml import html

from .http_utils import RateLimitError, fetch_with_backoff

IMPERSONATE = "chrome"
REQUEST_TIMEOUT = 30
MAX_CONCURRENT_REQUESTS = 16


def parse_movie_data(response: str, url: str, movie, username) -> dict[str, Any] | None:
    """Parses a Letterboxd film page into our movie schema."""
    tree = html.fromstring(response)

    try:
        tmdb_links = tree.xpath('//a[contains(@href, "themoviedb.org")]/@href')
        tmdb_links = [
            link for link in tmdb_links if "/movie/" in link or "/tv/" in link
        ]
        if not tmdb_links:
            print(f"No TMDb link found for {url}")
            return {"url": url, "tmdb_id": None}

        tmdb_link = tmdb_links[0]

        # TODO: Handle miniseries in the future
        if "/tv/" in tmdb_link:
            return {"film": None, "tmdb_id": -1}

        try:
            tmdb_id = int(tmdb_link.split("/movie")[1].strip("/").split("-")[0])
        except (IndexError, ValueError):
            print(f"Could not parse TMDB ID from {tmdb_link} for {url}")
            return None

        title = tree.xpath(
            '//h1[contains(@class, "primaryname")]\
                            //span[contains(@class, "name")]/text()'
        )[0].strip()

        year_elements = tree.xpath('//span[@class="releasedate"]//a/text()')
        year = int(year_elements[0].strip()) if year_elements else None

        directors_raw = tree.xpath('//a[contains(@href, "/director/")]/@href')
        directors = list(
            dict.fromkeys(director.split("/")[2] for director in directors_raw)
        )

        ratings = tree.xpath('//meta[@name="twitter:data2"]/@content')
        avg_rating = float(ratings[0].split()[0]) if ratings else None

        # Use find() for pattern matching and slicing
        num_ratings = None
        if (start_index := response.find('"ratingCount":')) != -1:
            end_index = response.find(",", start_index)
            if end_index == -1:
                end_index = response.find("}", start_index)
            try:
                num_ratings = int(
                    response[start_index + len('"ratingCount":') : end_index]
                )
            except ValueError:
                num_ratings = None

        runtime_raw = tree.xpath('//p[contains(@class, "text-link")]//text()')
        runtime = None
        if runtime_raw:
            runtime_str = runtime_raw[0].strip().split()[0].replace("\xa0", "")
            runtime = int(runtime_str) if runtime_str.isdigit() else None

        # Remove 'Show All...' if 'genre' includes it
        genres = tree.xpath('//a[contains(@href, "/films/genre/")]/text()')
        genres = list(
            dict.fromkeys(
                genre.strip() for genre in genres if genre.strip() != "Show All…"
            )
        )

        movie_data = {
            "tmdb_id": tmdb_id,
            "title": title,
            "directors": directors,
            "genres": genres,
            "release_year": year,
            "num_ratings": num_ratings,
            "avg_rating": avg_rating,
            "runtime": runtime,
            "user_ratings": [],
        }

        if movie is not None and username is not None:
            movie_data["user_ratings"].append(
                {
                    "username": username,
                    "liked": movie["liked"],
                    "rating": movie["rating"],
                }
            )

        return movie_data
    except IndexError:
        print(f"Error processing data for {url}!")
        return None


async def get_movie_data(url, session, movie, username) -> dict[str, Any] | None:
    """Gets a movie's TMDB ID from a Letterboxd URL."""
    try:
        response = await fetch_with_backoff(session, url, REQUEST_TIMEOUT)
    except RateLimitError as e:
        print(f"Giving up on {url}: {e}")
        return None
    return parse_movie_data(response, url, movie, username)


async def scrape_movies(movie_list: list, username: str) -> list[dict[str, Any]]:
    url = "https://letterboxd.com/film/{}/"
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async def _bounded(movie):
        # Cap in-flight requests so a large chunk doesn't trip rate limiting.
        async with semaphore:
            return await get_movie_data(
                url.format(movie["film_slug"]), session, movie, username
            )

    with requests.Session(impersonate=IMPERSONATE) as session:
        movie_info = await asyncio.gather(*(_bounded(movie) for movie in movie_list))
    return movie_info
