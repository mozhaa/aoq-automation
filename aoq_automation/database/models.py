from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column,
    DeclarativeBase,
    validates,
)
from sqlalchemy.schema import CreateTable
from sqlalchemy.ext.asyncio import AsyncAttrs
from typing import List
from datetime import datetime
from .utils import raises_only
import sys
import inspect


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )


class Anime(Base):
    """Anime"""

    __tablename__ = "anime"

    title_ro: Mapped[str]
    mal_url: Mapped[str]

    qitems: Mapped[List["QItem"]] = relationship(
        back_populates="anime", cascade="all, delete"
    )
    p_mal: Mapped["PAnimeMAL"] = relationship(cascade="all, delete")
    p_shiki: Mapped["PAnimeShiki"] = relationship(cascade="all, delete")
    p_anidb: Mapped["PAnimeAniDB"] = relationship(cascade="all, delete")

    __table_args__ = (UniqueConstraint("mal_url", name="_mal_url_uc"),)


class QItem(Base):
    """Quiz Item"""

    __tablename__ = "qitem"

    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.id"))
    category: Mapped[str]  # opening, ending
    number: Mapped[int]

    anime: Mapped["Anime"] = relationship(back_populates="qitems")
    sources: Mapped[List["QItemSource"]] = relationship(cascade="all, delete")
    difficulties: Mapped[List["QItemDifficulty"]] = relationship(cascade="all, delete")
    p_anidb: Mapped["PQItemAniDB"] = relationship(cascade="all, delete")

    __table_args__ = (
        UniqueConstraint("category", "number", name="_category_number_uc"),
    )

    @validates("category")
    @raises_only(ValueError)
    def validate_category(self, key: str, value: str) -> str:
        if value.lower() in ["op", "opening"]:
            return "OP"
        if value.lower() in ["ed", "ending"]:
            return "ED"
        invalidate(key, value)

    @validates("number")
    @raises_only(ValueError)
    def validate_number(self, key: str, value: int) -> int:
        if value > 0:
            return value
        invalidate(key, value)


class QItemSource(Base):
    """Source for Quiz Item"""

    __tablename__ = "qitem_source"

    qitem_id: Mapped[int] = mapped_column(ForeignKey("qitem.id"))
    platform: Mapped[str]  # youtube, torrent, local_file
    path: Mapped[str]  # youtube: url, torrent: magnet-url?, local_file: path
    added_by: Mapped[str]  # manual (user_id from bot), auto (script name)

    qitem: Mapped["QItem"] = relationship(back_populates="sources")
    timings: Mapped[List["QItemSourceTiming"]] = relationship(cascade="all, delete")


class QItemSourceTiming(Base):
    """Timing (guess/reveal start) for Quiz Item Source"""

    __tablename__ = "qitem_source_timing"

    qitem_source_id: Mapped[int] = mapped_column(ForeignKey("qitem_source.id"))
    guess_start: Mapped[float]
    reveal_start: Mapped[float]
    added_by: Mapped[str]

    qitem_source: Mapped["QItemSource"] = relationship(back_populates="timings")

    @classmethod
    def validate_timestamp(cls, key: str, value: str) -> float:
        possible_formats = [
            "%H:%M:%S.%f",
            "%M:%S.%f",
            "%S.%f",
            "%H:%M:%S",
            "%M:%S",
            "%S",
        ]
        seconds = None
        for format in possible_formats:
            try:
                t = datetime.strptime(value, format).time()
                seconds = (
                    t.microsecond / 1000000 + t.second + 60 * (t.minute + 60 * (t.hour))
                )
                break
            except ValueError:
                continue
        if seconds is not None:
            return seconds
        invalidate(key, value)

    @validates("guess_start")
    @raises_only(ValueError)
    def validate_guess_start(self, key: str, value: str) -> float:
        return QItemSourceTiming.validate_timestamp(key, value)

    @validates("reveal_start")
    @raises_only(ValueError)
    def validate_reveal_start(self, key: str, value: str) -> float:
        return QItemSourceTiming.validate_timestamp(key, value)


class QItemDifficulty(Base):
    """Quiz Difficulty for Quiz Item"""

    __tablename__ = "qitem_difficulty"

    qitem_id: Mapped[int] = mapped_column(ForeignKey("qitem.id"))
    value: Mapped[int]  # 0 - 100
    added_by: Mapped[str]  # manual (user_id from bot), auto (script name)

    qitem: Mapped["QItem"] = relationship(back_populates="difficulties")

    @validates("value")
    @raises_only(ValueError)
    def validate_value(self, key: str, value: str) -> int:
        if value.isdigit() and int(value) >= 0 and int(value) <= 100:
            return int(value)
        difficulties = {
            "very easy": 10,
            "easy": 20,
            "medium": 30,
            "hard": 50,
            "very hard": 70,
        }
        if value.lower() in difficulties.keys():
            return difficulties[value.lower()]
        invalidate(key, value)


class PAnimeMAL(Base):
    """Parsed Anime information from MyAnimeList (MAL)"""

    __tablename__ = "p_anime_mal"

    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.id"))

    url: Mapped[str]
    title_en: Mapped[str]
    poster_url: Mapped[str]

    rating: Mapped[float]
    ratings_count: Mapped[int]
    favorites: Mapped[int]
    popularity: Mapped[int]
    ranked: Mapped[int]

    plan_to_watch: Mapped[int]
    completed: Mapped[int]
    watching: Mapped[int]
    dropped: Mapped[int]
    on_hold: Mapped[int]


class PAnimeShiki(Base):
    """Parsed Anime information from Shikimori"""

    __tablename__ = "p_anime_shiki"

    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.id"))

    url: Mapped[str]
    title_ru: Mapped[str]
    poster_url: Mapped[str]
    poster_thumb_url: Mapped[str]

    rating: Mapped[float]
    ratings_count: Mapped[int]
    favorites: Mapped[int]
    comments: Mapped[int]

    plan_to_watch: Mapped[int]
    completed: Mapped[int]
    watching: Mapped[int]
    dropped: Mapped[int]
    on_hold: Mapped[int]


class PAnimeAniDB(Base):
    """Parsed Anime information from AniDB"""

    __tablename__ = "p_anime_anidb"

    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.id"))

    url: Mapped[str]
    airing_start: Mapped[datetime]
    airing_end: Mapped[datetime]


class PQItemAniDB(Base):
    """Parsed Quiz Item information from AniDB"""

    __tablename__ = "p_qitem_anidb"

    qitem_id: Mapped[int] = mapped_column(ForeignKey("qitem.id"))

    url: Mapped[str]
    main_title: Mapped[str]
    official_name: Mapped[str]
    performer: Mapped[str]
    rating_value: Mapped[float]


def invalidate(key: str, value: str) -> None:
    raise ValueError(f'"{value}" is invalid value for {key}')


def print_tables():
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and issubclass(obj, Base) and name != "Base":
            print(CreateTable(obj.__table__))


if __name__ == "__main__":
    print_tables()
