import asyncio
from aiohttp import ClientSession
from lxml import html

async def get_movie_data(url, session, movie, username):
    """Gets a movie's TMDB ID from a Letterboxd URL."""
    async with session.get(url) as r:
        response = await r.text()
        tree = html.fromstring(response)

        try:
            # Some lxml magic to fetch all our required data here
            tmdb_links = tree.xpath('//a[@data-track-action="TMDb"]/@href')
            if not tmdb_links:
                print(f"No TMDb link found for {url}")
                return {'url': url, 'tmdb_id': None}

            tmdb_link = tmdb_links[0]

            # TODO: Handle miniseries in the future
            if '/tv/' in tmdb_link:
                return {'film': None, 'tmdb_id': -1}

            tmdb_id = tmdb_link.split('/movie')[1].strip('/').split('-')[0]

            title = tree.xpath('//h1[contains(@class, "headline-1") \
                                and contains(@class, "filmtitle")] \
                                //span[contains(@class, "name")]/text()')[0].strip()

            year_elements = tree.xpath('//div[@class="releaseyear"]/a/text()')
            year = int(year_elements[0].strip()) if year_elements else None

            directors_raw = tree.xpath('//span[@class="directorlist"]\
                                       //a[@class="contributor"]/@href')
            directors = [director.split('/')[2] for director in directors_raw
                         if director.startswith('/director/')]
            ratings = tree.xpath('//meta[@name="twitter:data2"]/@content')
            avg_rating = float(ratings[0].split()[0]) if ratings else None

            # Use find() for pattern matching and slicing
            num_ratings = None
            if (start_index := response.find('"ratingCount":')) != -1:
                end_index = response.find(',', start_index)
                num_ratings = int(response[start_index + len('"ratingCount":') : end_index])

            runtime_raw = tree.xpath('//p[contains(@class, "text-link")]//text()')
            runtime = None
            if runtime_raw:
                runtime_str = runtime_raw[0].strip().split()[0]
                runtime = int(runtime_str) if runtime_str.isdigit() else None

            # Remove 'Show All...' if 'genre' includes it
            genres = tree.xpath('//div[@class="text-sluglist capitalize"]//a/text()')
            genres = [genre for genre in genres if genre != "Show All…"]

            movie_data = {
                'tmdb_id': tmdb_id,
                'title': title,
                'directors': directors,
                'genres': genres,
                'release_year': year,
                'num_ratings': num_ratings,
                'avg_rating': avg_rating,
                'runtime': runtime,
                'user_ratings': []
            }

            if movie != None:
                movie_data['user_ratings'].append({
                    'username': username,
                    'liked': movie['liked'],
                    'rating': movie['rating']
                })

            return movie_data
        except IndexError:
            print(f"Error processing data for {url}!")
            return None

async def scrape_movies(movie_list: list, username: str):
    url = "https://letterboxd.com/film/{}/"

    async with ClientSession() as session:
        tasks = []
        for movie in movie_list:
            tasks.append(get_movie_data(
                url.format(movie['film_slug']), session, movie, username
            ))
        movie_info = await asyncio.gather(*tasks)
    return movie_info