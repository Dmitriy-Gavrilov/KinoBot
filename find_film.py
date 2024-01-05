import requests
from random import randint
from config import API_KEY

Genres = {"boevik": "боевик",
          "fentezi": "фэнтези",
          "fantastika": "фантастика",
          "triller": "триллер",
          "voennyj": "военный",
          "detektiv": "детектив",
          "komediya": "комедия",
          "drama": "драма",
          "uzhasy": "ужасы",
          "kriminal": "криминал",
          "melodrama": "мелодрама",
          "biografiya": "биография",
          "anime": "аниме",
          "multfilm": "мультфильм",
          # "dlya-vzroslyh": "для взрослых",
          "dokumentalnyj": "документальный",
          "istoriya": "история",
          "korotkometrazhka": "короткометражка",
          "myuzikl": "мюзикл",
          "priklyucheniya": "приключения",
          "sport": "спорт"}

headers = {"X-API-KEY": API_KEY}


# Поиск рандомного фильма по выбранному жанру
async def get_films_by_genre(genre):
    params = {"selectFields": ["id", "name", "year", "description", "shortDescription", "rating.kp",
                               "movieLength", "ageRating", "poster.url", "videos.trailers.url"],
              "genres.name": genre}
    url = ('https://api.kinopoisk.dev/v1.3/movie?page=1&limit=1&year=2005-2023&shortDescription=%21null'
           '&rating.kp=6-10&movieLength=%21null&videos.trailers.url=%21null')
    response = requests.get(url, params=params, headers=headers)

    movie = response.json()
    total_pages = movie["total"]
    random_page = randint(1, total_pages)

    url = f'''https://api.kinopoisk.dev/v1.3/movie?page={random_page}&limit=1&year=2005-2023
    &shortDescription=%21null&rating.kp=6-10&movieLength=%21null&videos.trailers.url=%21null'''
    response1 = requests.get(url, params=params, headers=headers)

    return response1


# Обработка полученного фильма
async def handle_response(response, i):
    try:
        res_json = response.json()
        title = res_json["docs"][i]["name"]
        short_description = res_json["docs"][i]["shortDescription"]
        rating = str(res_json["docs"][i]["rating"]["kp"])
        id = str(res_json["docs"][i]["id"])
        film_url = "https://www.kinopoisk.ru/film/" + id
        description = res_json["docs"][i]["description"]
        year = str(res_json["docs"][i]["year"])
        length = str(res_json["docs"][i]["movieLength"])
        age_rating = str(res_json["docs"][i]["ageRating"])
        trailer_url = str(res_json["docs"][i]["videos"]["trailers"][0]["url"])
        image = res_json["docs"][i]["poster"]["url"]

        if any(x is None for x in
               [title, short_description, rating, description, year, length, age_rating, trailer_url, image, id]):
            raise Exception

        return [title, short_description, rating, film_url, description, year, length, age_rating, trailer_url, image,
                id]
    except:
        return False
