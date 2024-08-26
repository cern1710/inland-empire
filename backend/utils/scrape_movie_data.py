import asyncio
from aiohttp import ClientSession
from lxml import html

async def get_movie_data(url, session):
    async with session.get(url) as r:
        response = await r.text()
        tree = html.fromstring(response)

        title = tree.xpath('//h1[contains(@class, "headline-1") \
                            and contains(@class, "filmtitle")] \
                            //span[contains(@class, "name")]/text()')[0].strip()
        print(title)
        # movie_data = {
        #     'tmdb_id': tmdb_id,
        #     'title': title,
        #     'directors': directors,
        #     # 'original_language': original_language,
        #     'genres': genres,
        #     'release_year': release_year,
        #     'rating_count': rating_count,
        #     'avg_rating': avg_rating
        # }
        # return movie_data

async def get_movies(movie_list: list):
    url = "https://letterboxd.com/film/{}/"

    async with ClientSession() as session:
        tasks = []
        for movie in movie_list:
            tasks.append(get_movie_data(url.format(movie), session))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    movies = ['inland-empire', 'satantango', 'sicily']
    asyncio.run(get_movies(movies))