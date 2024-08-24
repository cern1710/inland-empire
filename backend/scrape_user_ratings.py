from bs4 import BeautifulSoup
import requests

def scrape_user_ratings(username: str):
    url = "https://letterboxd.com/{}/films/by/date"
    soup = BeautifulSoup(requests.get(url.format(username)).text, "lxml")
    body = soup.find("body")

    profile_header = body.find("section", attrs={"class": "profile-header"})

    display_name = (
        profile_header.find("h1", attrs={"class": "title-3"})
        .text.strip()
    )
    avatar_link = (
        profile_header.find("a", attrs={"class": "avatar -a24"})
        .find("img")["src"].strip()
    )

scrape_user_ratings("mscorsese")