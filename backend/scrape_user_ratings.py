from bs4 import BeautifulSoup
import requests

def scrape_user_ratings(username: str):
    url = "https://letterboxd.com/{}/films/by/date".format(username)

    soup = BeautifulSoup(requests.get(url).text, "lxml")
    body = soup.find("body")

    profile_header_section = body.find("section", attrs={"class": "profile-header"})

    display_name = profile_header_section.select_one("h1.title-3").text.strip()
    avatar_link = profile_header_section.select_one("a.avatar.-a24 img")["src"].strip()

    print(f"Display name: {display_name}, avatar link: {avatar_link}")

    col_main_section = body.find("section", attrs={"col-main"})
    num_pages = col_main_section.select_one("div.pagination li.paginate-page:last-child a").text.strip()

    pages = []
    poster_containers = col_main_section.find_all("li", class_="poster-container")

    pages.append(poster_containers)

    url_alt = url + "/page/{}"
    for i in range(2, int(num_pages) + 1):
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

            rating_tag = container.find("span", class_="rating")
            if rating_tag:
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

    for film in film_data:
        print(f"Film: {film['film_name']}, Liked: {film['liked']}, Rating: {film['rating']}")

scrape_user_ratings("mscorsese")