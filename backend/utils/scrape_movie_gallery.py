import asyncio
import aiohttp
from lxml import html
from typing import List, Dict, Any
from playwright.async_api import async_playwright
import re

PAGES_PER_BATCH = 30
BATCH_DELAY = 0.5

async def scrape_user_ratings(username: str) -> List[Dict[str, Any]]:
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

        # Fetch pages in batches with delay
        pages = []
        for i in range(0, len(urls), PAGES_PER_BATCH):
            batch_urls = urls[i:i+PAGES_PER_BATCH]
            batch_pages = await asyncio.gather(
                *(_fetch_page(session, url) for url in batch_urls)
            )
            pages.extend(batch_pages)
            if i + PAGES_PER_BATCH < len(urls):
                await asyncio.sleep(BATCH_DELAY)

        film_data = []
        for page in pages:
            tree = html.fromstring(page)
            containers = tree.xpath("//li[@class='poster-container']")
            for container in containers:
                film_slug = container.xpath(".//div[contains(@class, \
                                            'linked-film-poster')]/@data-film-slug")[0]
                liked = bool(container.xpath(".//span[contains(@class, 'like')]"))

                # Check if a rating exists and fetch the rating if there is one
                rating = None
                has_rating = container.xpath(".//span[contains(@class, 'rating')]/@class")
                if has_rating:
                    has_rating = has_rating[0].split()
                    rating = next((c for c in has_rating if c.startswith("rated-")), None)
                    rating = rating.split("-")[1] if rating else None

                film_data.append({
                    "film_slug": film_slug,
                    "liked": liked,
                    "rating": rating
                })

        return film_data

async def scrape_popular_pages(num_pages: int) -> List[Dict[str, Any]]:
    async def _fetch_page(page, url):
        await page.goto(url)
        await page.wait_for_selector('.poster-container')
        return await page.content()

    base_url = "https://letterboxd.com/films/popular/"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        urls = [base_url] + [f"{base_url}page/{page_num}/"
                             for page_num in range(2, num_pages + 1)]

        film_data = []
        for url in urls:
            content = await _fetch_page(page, url)
            film_slugs = re.findall(r'data-film-slug="([^"]+)"', content)
            film_data.extend([{"film_slug": slug} for slug in film_slugs])


            if urls.index(url) < len(urls) - 1:
                await asyncio.sleep(BATCH_DELAY)

        await browser.close()
        return film_data