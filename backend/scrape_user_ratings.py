from bs4 import BeautifulSoup
import requests

def scrape_user_ratings(username: str):
    url = f"https://letterboxd.com/{username}/films/by/date"

    soup = BeautifulSoup(requests.get(url).text, "lxml")
    body = soup.find("body")

    col_main_section = body.find("section", attrs={"col-main"})
    num_pages = int(col_main_section.select_one("div.pagination li.paginate-page:last-child a").text.strip())

    poster_containers = col_main_section.find_all("li", class_="poster-container")
    pages = [poster_containers]

    if num_pages > 1:
        url_alt = url + "/page/{}"
        for i in range(2, num_pages + 1):
            soup = BeautifulSoup(requests.get(url_alt.format(i)).text, "lxml")
            body = soup.find("body")
            col_main_section = body.find("section", attrs={"col-main"})
            poster_containers = col_main_section.find_all("li", class_="poster-container")
            pages.append(poster_containers)

    film_data = []
    for page in pages:
        for container in page:
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