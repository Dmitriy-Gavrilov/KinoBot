import sqlite3
import ast
from find_film import Genres

# Формирование кнопок клавиатуры

keys = list(Genres.keys())


async def form():
    inline_buttons = {}
    keys = list(Genres.keys())
    for key in keys:
        inline_buttons[key] = ["", Genres[key]]
    return inline_buttons


# БД - функции

connect = sqlite3.connect("Film_Selection")

#  Проверка и внесение пользователя в БД
async def check_user(id, name, nickname, date):
    cur = connect.cursor()
    res = cur.execute(f"select selected_genres from users where user_id = {id}").fetchall()
    if not res:
        in_btns = await form()
        cur.execute(f"""insert into users (user_id, user_name, user_nickname, selected_genres,
                        inline_buttons, favorites_films, similar_films, current_film, last_used,
                        found_films, flag_search)
                        values({id}, "{name}", "{nickname}", "", "{in_btns}",  "", "", "", "{date}", "", 0)""")

    else:
        cur.execute(f"""update users
                        set last_used = {date}
                        where user_id = {id}""")
    connect.commit()


# Функции получения значений
async def get_selected_genres(user_id):
    cur = connect.cursor()
    res = cur.execute(f"select selected_genres from users where user_id = {user_id}").fetchall()[0][0].split()
    return res


async def get_inline_buttons(user_id):
    cur = connect.cursor()
    res = cur.execute(f"select inline_buttons from users where user_id = {user_id}").fetchall()[0][0]
    d = ast.literal_eval(res)
    return d


async def get_current_film(user_id):
    cur = connect.cursor()
    res = cur.execute(f"select current_film from users where user_id = {user_id}").fetchall()[0][0].split("; ")
    return res


async def get_favorites_films(user_id):
    cur = connect.cursor()
    res = str(cur.execute(f"select favorites_films from users where user_id = {user_id}").fetchall()[0][0]).split()
    return res


async def get_similar_films(user_id):
    cur = connect.cursor()
    res = [i.split(";;") for i in
           cur.execute(f"select similar_films from users where user_id = {user_id}").fetchall()[0][0].split("; ")]
    return res


async def get_found_films(user_id):
    cur = connect.cursor()
    res = [i.split(";;") for i in
           cur.execute(f"select found_films from users where user_id = {user_id}").fetchall()[0][0].split("; ")]
    return res


async def get_flag_search(user_id):
    cur = connect.cursor()
    res = cur.execute(f"select flag_search from users where user_id = {user_id}").fetchall()[0][0]
    return res


# Функции обновления значений
async def push_selected_genres(user_id, selected_genres):
    cur = connect.cursor()
    cur.execute(f"""update users
                    set selected_genres = "{" ".join(selected_genres)}"
                    where user_id = {user_id}""")
    connect.commit()


async def push_inline_buttons(user_id, inline_buttons):
    cur = connect.cursor()
    cur.execute(f"""update users
                    set inline_buttons = "{inline_buttons}"
                    where user_id = {user_id}""")
    connect.commit()


async def push_current_film(user_id, current_film):
    cur = connect.cursor()
    cur.execute(f"""update users
                    set current_film = "{"; ".join(current_film)}"
                    where user_id = {user_id}""")
    connect.commit()


async def push_favorites_films(user_id, favorites_films):
    cur = connect.cursor()
    cur.execute(f"""update users
                    set favorites_films = "{" ".join(favorites_films)}"
                    where user_id = {user_id}""")
    connect.commit()


async def push_similar_films(user_id, similar_movies):
    cur = connect.cursor()
    cur.execute(f"""update users
                    set similar_films = "{"; ".join(similar_movies)}"
                    where user_id = {user_id}""")
    connect.commit()


async def push_found_films(user_id, found_films):
    cur = connect.cursor()
    cur.execute(f"""update users
                    set found_films = "{"; ".join(found_films)}"
                    where user_id = {user_id}""")
    connect.commit()


async def push_flag_search(user_id, value):
    cur = connect.cursor()
    cur.execute(f"""update users
                    set flag_search = {value}
                    where user_id = {user_id}""")
    connect.commit()


# Очистка отмеченных фильмов
async def clear_favorites_films(user_id):
    cur = connect.cursor()
    cur.execute(f"""update users
                    set favorites_films = ""
                    where user_id = {user_id}""")


# Приведение данных пользователя в начальное положение
async def clean(user_id):
    cur = connect.cursor()
    in_btns = await form()
    cur.execute(f"""update users
                    set selected_genres = "" ,
                        inline_buttons = "{in_btns}",
                        current_film = "",
                        similar_films = "",
                        found_films = "",
                        flag_search = 0
                    where user_id = {user_id}""")
    connect.commit()