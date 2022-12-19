from pathlib import Path

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String,
                        create_engine, desc, func, insert, select)
from sqlalchemy.orm import declarative_base, sessionmaker

DB_PATH = Path('database')
DB_PATH.mkdir(parents=True, exist_ok=True)
DB_URL = f'sqlite:///{DB_PATH.as_posix()}/sqlite.db'


engine = create_engine(DB_URL, echo=False, future=True)
Session = sessionmaker(engine, future=True, expire_on_commit=False)
Base = declarative_base()


class User(Base):  # type: ignore
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)


class Movie(Base):  # type: ignore
    __tablename__ = 'movies'
    movie_id = Column(Integer, primary_key=True)
    name = Column(String)
    year = Column(Integer)


class History(Base):  # type: ignore
    __tablename__ = 'histories'
    request_id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey("users.user_id"))
    request = Column(String)
    timestamp = Column(DateTime)
    movie = Column(Integer, ForeignKey("movies.movie_id"))


def clear_database() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def add_user(user: int, session: Session) -> None:
    if session.execute(select(User).filter_by(user_id=user)).first() is None:
        session.execute(insert(User).values(user_id=user))
        session.commit()


def add_movie(name: str, year: int, movie_id: int, session: Session) -> None:
    if session.execute(select(Movie).filter_by(movie_id=movie_id)).first() is None:
        session.execute(insert(Movie).values(name=name, year=year, movie_id=movie_id))
        session.commit()


def add_history(user: int, request: str, movie: int, session: Session) -> None:
    session.execute(insert(History).values(user=user, request=request, movie=movie))
    session.commit()


def get_history(user: int, session: Session) -> list[tuple]:
    history = select(History.request).where(History.user == user) \
        .order_by(desc(History.timestamp))

    return session.execute(history).fetchall()


def get_stats(user: int, session: Session) -> list[tuple]:
    stats = select(Movie.name, Movie.year, func.count(History.user).label("cnt")) \
        .where(History.user == user).join(Movie, History.movie == Movie.movie_id) \
        .group_by(Movie.movie_id).order_by(desc("cnt"))

    return session.execute(stats).fetchall()
