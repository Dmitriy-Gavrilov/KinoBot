import requests
from random import randint
from config import API_KEY
from find_film import Genres, handle_response

headers = {"X-API-KEY": API_KEY}


# Поиск фильмов, похожих на избранные
async def find_similar_movies(ids):
    params = {"selectFields": ["id", "name", "year", "description", "shortDescription", "rating.kp",
                               "movieLength", "ageRating", "poster.url", "videos.trailers.url", "similarMovies"],
              "id": ids}
    url = ('https://api.kinopoisk.dev/v1.3/movie?limit=100')
    response = requests.get(url, params=params, headers=headers)
    response = response.json()
    ids1 = []
    for i in range(len(response["docs"])):
        similarMovies = response["docs"][i]["similarMovies"]
        ids1 += [similarMovies[j]["id"] for j in range(len(similarMovies))]

    return ids1


# Поиск фильмов по id
async def get_movies_by_id(ids):
    params = {"selectFields": ["id", "name", "year", "description", "shortDescription", "rating.kp",
                               "movieLength", "ageRating", "poster.url", "videos.trailers.url"],
              "id": ids}
    url = 'https://api.kinopoisk.dev/v1.3/movie?limit=100'
    response = requests.get(url, params=params, headers=headers)
    rec_movies = list(
        filter(lambda x: x, [await handle_response(response, i) for i in range(len(response.json()["docs"]))]))

    # Включение повторяющихся фильмов
    p_ids = [[i, ids.count(i)] for i in ids if ids.count(i) > 1]
    p_ids1 = [i for n, i in enumerate(p_ids) if i not in p_ids[:n]]
    while p_ids1:
        f_id = p_ids1[0][0]
        for i in range(len(rec_movies)):
            if int(rec_movies[i][-1]) == f_id:
                for _ in range(p_ids1[0][1] - 1):
                    rec_movies.insert(i, rec_movies[i])
                break
        del p_ids1[0]

    return rec_movies