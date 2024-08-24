from bs4 import BeautifulSoup
import requests

def scrape_user_ratings(username: str):
    url = "https://letterboxd.com/{}/films/by/date"
    soup = BeautifulSoup(requests.get(url.format(username)).text, "lxml")
    body = soup.find("body")
    print(body)

scrape_user_ratings("mscorsese")