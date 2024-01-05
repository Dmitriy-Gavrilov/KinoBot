import requests
from config import API_KEY
from find_film import handle_response
from recommendations import get_movies_by_id

headers = {"X-API-KEY": API_KEY}


# Поиск фильма по названию
async def search_film_by_title(text):
    params = {"query": text}
    url = 'https://api.kinopoisk.dev/v1.4/movie/search?limit=30'
    response = requests.get(url, params=params, headers=headers).json()
    ids = []
    for i in range(len(response["docs"])):
        ids.append(response["docs"][i]["id"])
    return ids