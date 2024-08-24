from bs4 import BeautifulSoup
import requests

def scrape_user_ratings(username: str):
    url = "https://letterboxd.com/{}/films/by/date"
    soup = BeautifulSoup(requests.get(url.format(username)).text, "lxml")
    body = soup.find("body")

    profile_header_section = body.find("section", attrs={"class": "profile-header"})

    display_name = profile_header_section.select_one("h1.title-3").text.strip()
    avatar_link = profile_header_section.select_one("a.avatar.-a24 img")["src"].strip()

    print(f"Display name: {display_name}, avatar link: {avatar_link}")

scrape_user_ratings("mscorsese")