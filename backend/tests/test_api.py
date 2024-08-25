import requests

if __name__ == "__main__":
    r = requests.get("http://localhost:5000/movies")
    data = r.json()
    print(data)