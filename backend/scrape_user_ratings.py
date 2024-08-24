import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def scrape_user_ratings(username: str):
    # Inner function fetching page content from a specified URL
    async def _fetch_page(session, url):
        async with session.get(url) as response:
            return await response.text()

    base_url = f"https://letterboxd.com/{username}/films/by/date"

    # Use async sessions to make HTTP requests
    async with aiohttp.ClientSession() as session:
        soup = BeautifulSoup(await _fetch_page(session, base_url), "lxml")
        body = soup.find("body")
        col_main_section = body.find("section", attrs={"col-main"})
        num_pages_tag = col_main_section.select_one(
            "div.pagination li.paginate-page:last-child a"
        )

        num_pages = int(num_pages_tag.text.strip()) if num_pages_tag else 1
        urls = [base_url] + [f"{base_url}/page/{page_num}"
                             for page_num in range(2, num_pages + 1)]

        # Fetch all pages concurrently
        pages = await asyncio.gather(*(_fetch_page(session, url) for url in urls))

        film_data = []
        for page in pages:
            first_page = BeautifulSoup(page, "lxml")
            containers = first_page.find_all("li", class_="poster-container")
            for container in containers:
                film_name = container.select_one("div.linked-film-poster")["data-film-slug"]
                liked = container.select_one("span.like") is not None

                rating = None
                if rating_tag := container.find("span", class_="rating"):
                    rating_class = rating_tag["class"]
                    rating = next((c for c in rating_class
                                   if c.startswith("rated-")), None)
                    rating = rating.split("-")[1] if rating else None

                film_data.append({
                    "film_name": film_name,
                    "liked": liked,
                    "rating": rating
                })

        return film_data