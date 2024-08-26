import asyncio
from aiohttp import ClientSession
from lxml import html

async def get_movie_data(url, session):
    async with session.get(url) as r:
        response = await r.text()
        tree = html.fromstring(response)

        # Some lxml magic to fetch all our required data here
        tmdb_link = tree.xpath('//a[@data-track-action="TMDb"]/@href')[0]
        tmdb_id = tmdb_link.split('/movie')[1].strip('/').split('/')[0]
        title = tree.xpath('//h1[contains(@class, "headline-1") \
                            and contains(@class, "filmtitle")] \
                            //span[contains(@class, "name")]/text()')[0].strip()
        year = int(tree.xpath('//div[@class="releaseyear"]/a/text()')[0].strip())
        directors = tree.xpath('//span[@class="directorlist"]//a[@class="contributor"]/@href')
        ratings = tree.xpath('//meta[@name="twitter:data2"]/@content')
        avg_rating = float(ratings[0].split()[0]) if ratings else None

        # Use find() for pattern matching and slicing
        num_ratings = None
        if (start_index := response.find('"ratingCount":')) != -1:
            end_index = response.find(',', start_index)
            num_ratings = int(response[start_index + len('"ratingCount":') : end_index])

        # We'll fetch genres and original languages from TMDB
        movie_data = {
            'tmdb_id': tmdb_id,
            'title': title,
            'directors': directors,
            'release_year': year,
            'num_ratings': num_ratings,
            'avg_rating': avg_rating
        }
        return movie_data

async def scrape_movies(movie_list: list):
    url = "https://letterboxd.com/film/{}/"

    async with ClientSession() as session:
        tasks = []
        for movie in movie_list:
            tasks.append(get_movie_data(url.format(movie), session))
        movie_info = await asyncio.gather(*tasks)
    return movie_info