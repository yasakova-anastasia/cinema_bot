## Что умеет бот?

Бот откликается на следующие команды:
* `/start` -- знакомство с пользователем

  ![start](https://docs.google.com/uc?id=1tZYiOtfwAIVJVmgf0UdIdqQ18V3V6VR3)

* `/help` -- перечисление команд с описанием

  ![help](https://docs.google.com/uc?id=1CLsFdgTNQIKP3-gOuaK2HjodXzG5puTq)

* `/movie` <фильм или сериал> -- получение информации о фильме или сериале

  ![movie](https://docs.google.com/uc?id=1oUkw-nEogak7QEH4CpjJKeIPeNG8iJNh)

* `/stats` - получение статистики

  ![stats](https://docs.google.com/uc?id=1dHQJ62n7QBQje_lkWTqBHGBAnPwsktJ9)

* `/history` - получение истории запросов

  ![history](https://docs.google.com/uc?id=1XxxybuPNKAyFj2O03FuIzF5Xs3SG8wGp)

## Как устроен бот?

Для хранения данных (необходимо для запросов `/history` и `/stats`) используется `sqlite`. В БД три таблички: `User`, `Movie` и `History`.

Для поиска информации о фильмах используется [готовое API Кинопоиска](https://kinopoiskapiunofficial.tech/). Для получения ссылки для просмотра фильма выполняется гугл запрос.

Задеплоила с помощью AWS.
