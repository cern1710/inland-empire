from bs4 import BeautifulSoup
import requests

def scrape_user_ratings(username: str):
    url = f"https://letterboxd.com/{username}/films/by/date"

    soup = BeautifulSoup(requests.get(url).text, "lxml")
    body = soup.find("body")

    col_main_section = body.find("section", attrs={"col-main"})
    num_pages = int(col_main_section.select_one("div.pagination li.paginate-page:last-child a").text.strip())

    def _fetch_page(page_num):
        if page_num == 1:
            return col_main_section.find_all("li", class_="poster-container")
        else:
            page_url = f"{url}/page/{page_num}"
            page_soup = BeautifulSoup(requests.get(page_url).text, "lxml")
            page_body = page_soup.find("body")
            page_col_main_section = page_body.find("section", class_="col-main")
            return page_col_main_section.find_all("li", class_="poster-container")

    containers = [container for i in range(num_pages+1) for container in _fetch_page(i)]

    film_data = []
    for container in containers:
        film_name = container.select_one("div.linked-film-poster")["data-film-slug"]
        liked = container.select_one("span.like") is not None

        if rating_tag := container.find("span", class_="rating"):
            rating_class = rating_tag["class"]
            rating = next((c for c in rating_class if c.startswith("rated-")), None)
            rating = rating.split("-")[1] if rating else None
        else:
            rating = None

        film_data.append({
            "film_name": film_name,
            "liked": liked,
            "rating": rating
        })

    return film_data