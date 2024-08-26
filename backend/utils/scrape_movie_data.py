import asyncio
from aiohttp import ClientSession
from lxml import html

async def get_movie_data(url, session):
    """Gets a movie's TMDB ID from a Letterboxd URL."""
    async with session.get(url) as r:
        response = await r.text()
        tree = html.fromstring(response)

        # Some lxml magic to fetch all our required data here
        tmdb_links = tree.xpath('//a[@data-track-action="TMDb"]/@href')
        if not tmdb_links:
            print(f"No TMDb link found for {url}")
            return {'url': url, 'tmdb_id': None}
        tmdb_link = tmdb_links[0]
        media_type = '/tv/' if ('/tv/' in tmdb_link) else '/movie/'
        tmdb_id = tmdb_link.split(media_type)[1].strip('/').split('-')[0]

        movie_data = {
            'film': url,
            'tmdb_id': tmdb_id,
        }
        return movie_data

async def scrape_movies(movie_list: list):
    url = "https://letterboxd.com/film/{}/"

    async with ClientSession() as session:
        tasks = []
        for movie in movie_list:
            tasks.append(get_movie_data(url.format(movie['film_slug']), session))
        movie_info = await asyncio.gather(*tasks)
    return movie_info