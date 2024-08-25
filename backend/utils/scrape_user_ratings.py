import asyncio
import aiohttp
from lxml import html

async def scrape_user_ratings(username: str):
    # Inner function fetching page content from a specified URL
    async def _fetch_page(session, url):
        async with session.get(url) as response:
            return await response.text()

    base_url = f"https://letterboxd.com/{username}/films/by/date"

    # Use async sessions to make HTTP requests
    async with aiohttp.ClientSession() as session:
        first_page_html = await _fetch_page(session, base_url)
        root_tree = html.fromstring(first_page_html)

        if num_pages_res := root_tree.xpath("//div[@class='pagination']//li[@class='paginate-page']/a/text()"):
            num_pages = int(num_pages_res[-1])
        else:
            num_pages = 1
        urls = [base_url] + [f"{base_url}/page/{page_num}"
                             for page_num in range(2, num_pages + 1)]

        # Fetch all pages concurrently
        pages = await asyncio.gather(*(_fetch_page(session, url) for url in urls))

        film_data = []
        for page in pages:
            tree = html.fromstring(page)
            containers = tree.xpath("//li[@class='poster-container']")
            for container in containers:
                # film_name = container.xpath(".//div[@class='linked-film-poster']/@data-film-slug")
                film_name = container.xpath(".//img[@class='image']/@alt")[0]
                liked = bool(container.xpath(".//span[contains(@class, 'like')]"))

                # Check if a rating exists and fetch the rating if there is one
                rating = None
                has_rating = container.xpath(".//span[contains(@class, 'rating')]/@class")
                if has_rating:
                    has_rating = has_rating[0].split()
                    rating = next((c for c in has_rating if c.startswith("rated-")), None)
                    rating = rating.split("-")[1] if rating else None

                film_data.append({
                    "film_name": film_name,
                    "liked": liked,
                    "rating": rating
                })

        return film_data