import typing as tp
from abc import ABC, abstractmethod

import aiohttp
import requests
from bs4 import BeautifulSoup
from creds import KINOPOISK_TOKEN


def get_movie_link(movie: str) -> tp.Optional[str]:
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru,rus,en-US,en;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/98.0.4758.82',
    }

    response = requests.get('https://www.google.com/search', headers=headers,
                            params={'q': f"{movie} смотреть онлайн"}).text
    search = BeautifulSoup(response, 'html.parser').find(id='search')
    if search is None:
        return None

    link = search.find('a')

    return link['href'] if link is not None else None


class Movie:
    def __init__(self, dict: dict[str, tp.Any]):
        self.name: str = dict.get("nameRu", "")
        self.year: tp.Optional[int] = dict.get("year", None)
        self.description: str = dict.get("description", "")
        self.length: str = dict.get("filmLength", "")
        self.countries: list[str] = [country['country'] for country in dict.get("countries", [])]
        self.genres: list[str] = [genres['genre'] for genres in dict.get("genres", [])]
        self.rating: tp.Optional[int] = dict.get("rating", None)
        self.poster_url: str = dict.get("posterUrl", "")
        self.kinopoisk_id: tp.Optional[int] = dict.get("filmId", None)
        self.link: str = "https://www.kinopoisk.ru/film/" + str(dict.get("filmId", ""))

    def get_movie_info(self) -> str:
        link = get_movie_link(f"{self.name} ({self.year})")

        movie_info = "".join([f"<b>{self.name} ({self.year})</b>\n\n",
                              f"{self.description}\n\n",
                              f"Страны: {', '.join(self.countries)}\n",
                              f"Жанры: {', '.join(self.genres)}\n",
                              f"Рейтинг: {self.rating}\n",
                              f"Длительность: {self.length}\n",
                              f"\nИнформацию можно найти тут: {self.link}\n",
                              f"Посмотреть можно тут: {link}\n"])

        return movie_info


async def get_response(url: str, params: dict["str", tp.Any],
                       headers: dict[str, tp.Any]) -> tp.Optional[dict[str, str]]:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url=url, params=params, headers=headers) as resp:
                return await resp.json()
        except aiohttp.InvalidURL:
            return None
        except AssertionError:
            return None


class MovieAPI(ABC):
    @abstractmethod
    def get_params(self, name: str) -> tuple[str, dict[str, str], dict[str, str]]:
        pass

    @abstractmethod
    def continue_response(self, req: tp.Optional[dict[str, str]]) -> None:
        pass

    async def get_result(self, name: str) -> tp.Optional[Movie]:
        url, params, headers = self.get_params(name)
        response = await get_response(url, params, headers)
        movie = self.continue_response(response)

        return movie


class KinopoiskAPI(MovieAPI):
    url = "https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword"

    def get_params(self, name: str) -> tuple[str, dict[str, str], dict[str, str]]:
        return self.url, {"keyword": name}, {"X-API-KEY": KINOPOISK_TOKEN}

    def continue_response(self, req: tp.Optional[dict[str, tp.Any]]) -> tp.Any:
        if req is None:
            return None

        if not req.get("films"):
            return None

        return Movie(req['films'][0])
