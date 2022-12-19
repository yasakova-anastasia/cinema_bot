from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from creds import TELEGRAM_TOKEN
from db import (Session, add_history, add_movie, add_user, clear_database,
                get_history, get_stats)
from messages import (EMPTY_MESSAGE, HELP_MESSAGE, HISTORY_HEADER,
                      NO_HISTORY_MESSAGE, NO_STATS_MESSAGE, NOT_FOUND_MESSAGE,
                      START_MESSAGE, STATS_HEADER, TIP_MESSAGE)
from movie_api import KinopoiskAPI

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)
clear_database()
session = Session()


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message) -> None:
    await msg.answer(START_MESSAGE)


@dp.message_handler(commands=['help'])
async def send_help(msg: types.Message) -> None:
    await msg.answer(HELP_MESSAGE)


@dp.message_handler(commands=['history'])
async def send_history(msg: types.Message) -> None:
    history = get_history(msg.from_user.id, session)
    if not history:
        return await msg.answer(NO_HISTORY_MESSAGE)

    await msg.answer(HISTORY_HEADER + "\n".join([h[0]
                     for h in reversed(history[-15:])]), parse_mode="HTML")


@dp.message_handler(commands=['stats'])
async def send_stats(msg: types.Message) -> None:
    stats = get_stats(msg.from_user.id, session)
    if not stats:
        return await msg.answer(NO_STATS_MESSAGE)

    await msg.answer(STATS_HEADER + "\n".join([f"{stat[0]} ({stat[1]}): {stat[2]}"
                     for stat in stats[:15]]), parse_mode="HTML")


@dp.message_handler(commands=['movie'])
async def send_movie(msg: types.Message) -> None:
    text = msg.text.split(maxsplit=1)
    if len(text) < 2:
        return await msg.answer(EMPTY_MESSAGE)

    name = text[1]

    api = KinopoiskAPI()
    movie = await api.get_result(name)

    if movie is None:
        return await msg.answer(NOT_FOUND_MESSAGE)

    user = msg.from_user.id
    add_user(user, session)
    add_movie(movie.name, movie.year, movie.kinopoisk_id, session)
    add_history(user, name, movie.kinopoisk_id, session)

    await bot.send_photo(msg.chat.id, types.InputFile.from_url(movie.poster_url))
    await msg.answer(movie.get_movie_info(), parse_mode="HTML")


@dp.message_handler()
async def send_tip(msg: types.Message):
    await msg.answer(TIP_MESSAGE)


if __name__ == '__main__':
    executor.start_polling(dp)
