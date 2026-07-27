import asyncio
import re
from typing import Any

from curl_cffi import requests
from lxml import html
from playwright.async_api import async_playwright

from .http_utils import fetch_with_backoff

PAGES_PER_BATCH = 12
BATCH_DELAY = 0.5
IMPERSONATE = "chrome"
REQUEST_TIMEOUT = 30

# Letterboxd stores ratings on a 1-10 scale (e.g., 9 == 4.5 stars)
RATING_SCALE = 2

# Letterboxd's followers/following lists render 25 people per page
PEOPLE_PER_PAGE = 25


def _parse_gallery_page(page_html: str) -> list[dict[str, Any]]:
    """Extracts film slugs, ratings and likes from a poster grid page."""
    tree = html.fromstring(page_html)
    film_data = []

    for item in tree.xpath('//li[contains(@class, "griditem")]'):
        slugs = item.xpath(".//div[@data-item-slug]/@data-item-slug")
        if not slugs:
            continue

        # Rating span carries a rated-N class; N is out of 10
        rating = None
        rating_classes = item.xpath(
            './/span[contains(concat(" ", normalize-space(@class), " "), " rating ")]'
            "/@class"
        )
        if rating_classes:
            rating = next(
                (
                    int(c.split("-")[1])
                    for c in rating_classes[0].split()
                    if c.startswith("rated-")
                ),
                None,
            )

        # Match the like icon specifically: a review link lives in the same
        # paragraph and also contains "-micro" in its class.
        liked = bool(item.xpath('.//span[contains(@class, "liked-micro")]'))

        film_data.append({"film_slug": slugs[0], "liked": liked, "rating": rating})

    return film_data


def _get_num_pages(page_html: str) -> int:
    tree = html.fromstring(page_html)
    pages = tree.xpath(
        "//div[contains(@class, 'paginate-pages')]"
        "//li[contains(@class, 'paginate-page')]/a/text()"
    )
    return int(pages[-1]) if pages else 1


async def scrape_user_ratings(username: str) -> list[dict[str, Any]]:
    """Scrapes every film in a user's profile with their rating and like."""
    base_url = f"https://letterboxd.com/{username}/films"

    async def _fetch_page_async(session, url: str) -> str:
        return await fetch_with_backoff(session, url, REQUEST_TIMEOUT)

    with requests.Session(impersonate=IMPERSONATE) as session:
        first_page_html = await _fetch_page_async(session, base_url)
        num_pages = _get_num_pages(first_page_html)

        urls = [f"{base_url}/page/{page_num}/" for page_num in range(2, num_pages + 1)]

        pages = [first_page_html]
        for i in range(0, len(urls), PAGES_PER_BATCH):
            batch_urls = urls[i : i + PAGES_PER_BATCH]
            batch_pages = await asyncio.gather(
                *(_fetch_page_async(session, url) for url in batch_urls)
            )
            pages.extend(batch_pages)
            if i + PAGES_PER_BATCH < len(urls):
                await asyncio.sleep(BATCH_DELAY)

    film_data = []
    for page in pages:
        film_data.extend(_parse_gallery_page(page))

    return film_data


def _parse_people_page(page_html: str) -> list[str]:
    """Extracts member usernames from a followers/following list page."""
    tree = html.fromstring(page_html)
    hrefs = tree.xpath(
        '//td[contains(@class, "table-person")]'
        '//h3[contains(@class, "title-3")]/a[contains(@class, "name")]/@href'
    )
    return [href.strip("/").split("/")[-1] for href in hrefs]


def _get_person_count(page_html: str, relation: str) -> int:
    """Reads the 'N people' count off the Followers/Following sub-nav tab."""
    tree = html.fromstring(page_html)
    titles = tree.xpath(
        f'//li[contains(@class, "selected")]/a[contains(@href, "/{relation}/")]/@title'
    )
    if not titles:
        return 0
    digits = re.sub(r"[^\d]", "", titles[0])
    return int(digits) if digits else 0


async def _scrape_people(username: str, relation: str) -> list[str]:
    """Scrapes every username in a user's followers or following list.

    `relation` must be "followers" or "following": it's the Letterboxd URL
    segment (https://letterboxd.com/<username>/<relation>/).
    """
    base_url = f"https://letterboxd.com/{username}/{relation}"

    async def _fetch_page_async(session, url: str) -> str:
        return await fetch_with_backoff(session, url, REQUEST_TIMEOUT)

    with requests.Session(impersonate=IMPERSONATE) as session:
        first_page_html = await _fetch_page_async(session, f"{base_url}/")
        total_people = _get_person_count(first_page_html, relation)
        num_pages = max(1, -(-total_people // PEOPLE_PER_PAGE)) # ceil division

        urls = [f"{base_url}/page/{page_num}/" for page_num in range(2, num_pages + 1)]

        pages = [first_page_html]
        for i in range(0, len(urls), PAGES_PER_BATCH):
            batch_urls = urls[i : i + PAGES_PER_BATCH]
            batch_pages = await asyncio.gather(
                *(_fetch_page_async(session, url) for url in batch_urls)
            )
            pages.extend(batch_pages)
            if i + PAGES_PER_BATCH < len(urls):
                await asyncio.sleep(BATCH_DELAY)

    usernames = []
    for page in pages:
        usernames.extend(_parse_people_page(page))

    # Dedup while preserving order, in case pagination overlaps by one row
    return list(dict.fromkeys(usernames))


async def scrape_followers(username: str) -> list[str]:
    """Scrapes the usernames of everyone following the given user."""
    return await _scrape_people(username, "followers")


async def scrape_following(username: str) -> list[str]:
    """Scrapes the usernames of everyone the given user follows."""
    return await _scrape_people(username, "following")


async def scrape_popular_pages(num_pages: int) -> list[dict[str, Any]]:
    """Scrapes Letterboxd by most popular movies.

    WARNING: Very Slow. The popular browser renders its grid client-side, so
    unlike the user galleries it cannot be fetched with a plain HTTP request.
    """

    async def _fetch_page(page, url):
        await page.goto(url)
        await page.wait_for_selector(".poster-container")
        return await page.content()

    base_url = "https://letterboxd.com/films/popular/"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        urls = [base_url] + [
            f"{base_url}page/{page_num}/" for page_num in range(2, num_pages + 1)
        ]

        film_data = []
        for url in urls:
            content = await _fetch_page(page, url)
            film_slugs = re.findall(r'data-film-slug="([^"]+)"', content)
            film_data.extend([{"film_slug": slug} for slug in film_slugs])

            if urls.index(url) < len(urls) - 1:
                await asyncio.sleep(BATCH_DELAY)

        await browser.close()
        return film_data
