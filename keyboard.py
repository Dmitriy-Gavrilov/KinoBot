from aiogram import types
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
                           CallbackQuery)
from random import choice
from create_bot import bot, dp
from find_film import *
from recommendations import *
from search_by_title import *
from db_functions import *


# Сохранение изображения - обложки фильма
async def save_image(url):
    img = requests.get(url)
    img_file = open('images/image.jpg', 'wb')
    img_file.write(img.content)
    img_file.close()


# Создание клавиатуры (выбор жанра)
async def create_keyboard(user_id):
    choice = InlineKeyboardMarkup(row_width=2)
    inline_buttons = await get_inline_buttons(user_id)
    inline_keyboard = [InlineKeyboardButton(text=inline_buttons[i][0] + inline_buttons[i][1],
                                            callback_data=f"{i}",
                                            resize_keyboard=True) for i in inline_buttons.keys()]
    inline_keyboard.append(InlineKeyboardButton(text="➡️ Далее", callback_data="next", resize_keyboard=True))

    for i in inline_keyboard:
        choice.add(i)

    return choice


# Обновление кнопок при выборе / удалении жанра
async def update_buttons(param, genre, user_id):
    inline_buttons = await get_inline_buttons(user_id)
    for key in keys:
        if key == genre:
            if param == "append":
                inline_buttons[key][0] = "✅"
            else:
                inline_buttons[key][0] = ""
            break
    await push_inline_buttons(user_id, inline_buttons)


# Сортировка рекомендаций
async def sort_recommendations(arr):
    arr.reverse()
    d = {}
    arr1 = []
    for i in arr:
        if i[0] not in d:
            d[i[0]] = arr.count(i)
            arr1.append(i)
            arr1 = sorted(arr1, key=lambda x: d[x[0]], reverse=True)
    if len(arr1) > 50:
        arr1 = arr1[:50]
    return arr1


# Обработчики кнопок

# Команды start и help
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = str(message.from_user.id)
    user_name = str(message.from_user.first_name)
    username = str(message.from_user.username)
    date = str(message.date).split()[0]

    await check_user(user_id, user_name, username, date)
    await clean(user_id)

    reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    reply_keyboard.row(KeyboardButton(text="🏠 Главное меню", callback_data="\start"),
                       KeyboardButton(text="❓Помощь", callback_data="\help"))
    reply_keyboard.row(KeyboardButton(text="🎬 Подбор фильма", callback_data="\\find_film"),
                       KeyboardButton(text="🔝 Рекомендации", callback_data="\\recommendations"))
    reply_keyboard.add(KeyboardButton(text="🔎 Поиск по названию", callback_data="\search_film"))

    await message.answer("Главное меню",
                         reply_markup=reply_keyboard)


@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    await bot.send_message(message.from_user.id, "Это бот для удобного подбора фильмов.\n"
                                                 "🎬 Подбор фильма - предлагаются фильмы из жанров, которые будут выбраны"
                                                 " (если не выбрано ни одного жанра, считается что были выбраны все)\n"
                                                 "🔝 Рекомендации - предлагаются фильмы, похожие на те, что уже были когда-то отмечены\n"
                                                 "🔎 Поиск по названию - введите название фильма полностью или его часть. Вы получите все фильмы, подходящие под этот запрос")


@dp.message_handler(lambda message: message.text == "🏠 Главное меню")
async def start(message: types.Message):
    await start_command(message)


@dp.message_handler(lambda message: message.text == "❓Помощь")
async def help(message: types.Message):
    await help_command(message)


# Режимы бота
@dp.message_handler(lambda message: message.text == "🎬 Подбор фильма")
async def find_film(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Выбери один или несколько жанров, которые хочешь посмотреть сегодня",
                           reply_markup=await create_keyboard(message.from_user.id))


@dp.message_handler(lambda message: message.text == "🔝 Рекомендации")
async def recommendations(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="Очистить избранные фильмы", callback_data="clear_fav_films", resize_keyboard=True))
    keyboard.add(
        InlineKeyboardButton(text="К рекомендациям", callback_data="show_recommendations", resize_keyboard=True))

    await bot.send_message(message.from_user.id, "Выберите действие", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "🔎 Поиск по названию")
async def search_film(message: types.Message):
    await push_flag_search(message.from_user.id, 1)
    await bot.send_message(message.from_user.id, "Введите название фильма")


# Отправка фильма
async def send_film(user_id, msg_id, answer, cb_data_no, cb_data_yes):
    yes_or_no = InlineKeyboardMarkup(row_width=2)
    yes_or_no.row(InlineKeyboardButton(text="✅", callback_data=f"{cb_data_yes}", resize_keyboard=True),
                  InlineKeyboardButton(text="❌", callback_data=f"{cb_data_no}", resize_keyboard=True))
    if len(answer) > 1:
        text = f"⁃ {answer[0]}\n⁃ {answer[1]}\n⁃ Рейтинг KP: {answer[2]}"
    else:
        return False
    try:
        if cb_data_no != "no_s":
            await bot.delete_message(chat_id=user_id, message_id=msg_id)
    except:
        pass
    try:
        await save_image(answer[9])
        await bot.send_photo(chat_id=user_id,
                             photo=types.InputFile("images/image.jpg"),
                             caption=text,
                             reply_markup=yes_or_no)
        return True
    except:
        return False
    # await call.answer()


# Очистка отмеченных фильмов
@dp.callback_query_handler(text="clear_fav_films")
async def clear_fav_films(call: CallbackQuery):
    await clear_favorites_films(call.from_user.id)
    await bot.send_message(call.from_user.id, "Отмеченных фильмов больше нет")
    await call.answer()


# Подбор и показ рекомендованных фильмов
@dp.callback_query_handler(text="show_recommendations")
async def show_recommendations(call: CallbackQuery):
    fav_films = [int(i) for i in await get_favorites_films(call.from_user.id)]
    if fav_films:
        sm = [i for i in await find_similar_movies(fav_films) if i not in fav_films]
        if not sm:
            await bot.send_message(call.from_user.id,
                                   "Рекомендации для вас еще не собраны, отмечайте больше фильмов")
            return
        similar_movies = [";;".join(i) for i in await sort_recommendations(await get_movies_by_id(sm))]

        await push_similar_films(call.from_user.id, similar_movies)
        await no_r(call)
    else:
        await bot.send_message(call.from_user.id,
                               "Необходимо отметить хотя бы 1 фильм, чтобы получать рекомендации")
    await call.answer()


# Подбор и показ найденных по запросу фильмов
@dp.callback_query_handler(text="show_recommendations")
async def show_found_films(call: CallbackQuery, text):
    movies_ids = await search_film_by_title(text)
    if movies_ids:
        movies = await get_movies_by_id(movies_ids)
        if movies:
            movies = [";;".join(i) for i in movies]
            await push_found_films(call.from_user.id, movies)
            await no_s(call)
        else:
            await bot.send_message(call.from_user.id, "Не могу предложить фильмы с таким названием")
    else:
        await bot.send_message(call.from_user.id, "Некорректное название фильма")

    # await call.answer()


# Кнопка - переход к выбору фильмов
@dp.callback_query_handler(text="next")
async def next_step(call: CallbackQuery):
    # await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    await call.message.answer("Выбери понравившийся фильм")
    await no(call)
    await call.answer()


# Отметить фильм
@dp.callback_query_handler(text=["yes", "yes_r", "yes_s"])
async def yes(call: CallbackQuery):
    answer = await get_current_film(call.from_user.id)
    film_id = answer[10]
    fav_films = await get_favorites_films(call.from_user.id)
    if film_id not in fav_films:
        fav_films.append(film_id)
        await push_favorites_films(call.from_user.id, fav_films[:50])  # Изменено на [:50]

    if call.data == "yes":
        cb_data = "no"
    elif call.data == "yes_r":
        cb_data = "no_r"
    else:
        cb_data = "no_s"

    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(InlineKeyboardButton(text="Ссылка на фильм", callback_data="get_film_url", resize_keyboard=True))
    keyboard.add(InlineKeyboardButton(text="Полное описание", callback_data="get_description", resize_keyboard=True))
    keyboard.add(InlineKeyboardButton(text="Трейлер", callback_data="get_trailer_url", resize_keyboard=True))
    keyboard.add(InlineKeyboardButton(text="➡️ Следующий фильм", callback_data=f"{cb_data}", resize_keyboard=True))

    await call.message.answer("Отличный выбор!", reply_markup=keyboard)
    await call.answer()


# Получение дополнительной информации о фильме
@dp.callback_query_handler(text="get_film_url")
async def get_film_url(call: CallbackQuery):
    answer = await get_current_film(call.from_user.id)
    await call.message.answer(f"{answer[3]}")
    await call.answer()


@dp.callback_query_handler(text="get_description")
async def get_description(call: CallbackQuery):
    answer = await get_current_film(call.from_user.id)
    await call.message.answer(f"• Дата выхода: {answer[5]}\n"
                              f"• Продолжительность: {answer[6]} мин\n"
                              f"• Возрастное ограничение: {answer[7]}+\n"
                              f"• Полное описание: {answer[4]}")
    await call.answer()


@dp.callback_query_handler(text="get_trailer_url")
async def get_trailer_url(call: CallbackQuery):
    answer = await get_current_film(call.from_user.id)
    await call.message.answer(f"{answer[8]}")
    await call.answer()


# Пропустить фильм
@dp.callback_query_handler(text="no")
async def no(call: CallbackQuery):
    selected_genres = await get_selected_genres(call.from_user.id)
    if not selected_genres:
        selected_genres = [i for i in keys]
    await push_current_film(call.from_user.id, await handle_response(
        await get_films_by_genre(Genres[choice(selected_genres)]), 0))
    answer = await get_current_film(call.from_user.id)
    # print(answer)

    ans = await send_film(call.from_user.id, call.message.message_id, answer, "no", "yes")
    if not ans:
        await no(call)

    await call.answer()


@dp.callback_query_handler(text="no_r")
async def no_r(call: CallbackQuery):
    movies = await get_similar_films(call.from_user.id)
    if movies[0][0]:
        movie = movies[0]
        # print(movie)
        await push_similar_films(call.from_user.id, [";;".join(i) for i in movies[1:]])
        await push_current_film(call.from_user.id, movie)

        if type(call) == CallbackQuery:
            msg_id = call.message.message_id
        else:
            msg_id = call.message_id
        ans = await send_film(call.from_user.id, msg_id, movie, "no_r", "yes_r")

        if not ans:
            await no_r(call)

    else:
        await bot.send_message(call.from_user.id,
                               "На этом все :(\n"
                               "Чтобы рекомендации становились точнее, а количество предложенных фильмов было больше,"
                               " отмечайте больше фильмов")


@dp.callback_query_handler(text="no_s")
async def no_s(call: CallbackQuery):
    await push_flag_search(call.from_user.id, 0)
    movies = await get_found_films(call.from_user.id)
    if movies[0][0]:
        movie = movies[0]
        await push_found_films(call.from_user.id, [";;".join(i) for i in movies[1:]])
        await push_current_film(call.from_user.id, movie)

        if type(call) == CallbackQuery:
            msg_id = call.message.message_id
        else:
            msg_id = call.message_id

        ans = await send_film(call.from_user.id, msg_id, movie, "no_s", "yes_s")

        if not ans:
            await no_r(call)
    else:
        await bot.send_message(call.from_user.id, "Больше нет фильмов, подходящих под это название")


# Изменение кнопок с жанрами
async def edit_message(call: CallbackQuery, param, genre, user_id):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await update_buttons(param, genre, user_id)
    await bot.send_message(call.from_user.id,
                           "Выбери один или несколько жанров, которые хочешь посмотреть сегодня",
                           reply_markup=await create_keyboard(call.from_user.id))


# Обработка кнопок выбора жанров
@dp.callback_query_handler(text=keys)
async def add_film(call: CallbackQuery):
    user_id = call.from_user.id
    selected_genres = await get_selected_genres(user_id)
    for i in keys:
        if i == call.data:
            if i not in selected_genres:
                selected_genres.append(i)
                param = "append"
            else:
                del selected_genres[selected_genres.index(i)]
                param = "delete"
    await push_selected_genres(user_id, selected_genres)
    await edit_message(call, param, call.data, user_id)
    await call.answer()


# Всегда внизу:
# Обработка поискового запроса и остальных сообщений
@dp.message_handler()
async def other_messages(message: types.Message):
    if await get_flag_search(message.from_user.id):
        await show_found_films(message, message.text)
    else:
        await bot.send_message(message.from_user.id, "Я не реагирую на сообщения")
        # await bot.send_sticker(message.from_user.id,
        #                        sticker="CAACAgIAAxkBAAEB-CRlU3YpsjgJPT6Kedby3RTfV-nzSwACARUAAqyhAAFIx5Tw3fxIQ-MzBA")