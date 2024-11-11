from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.schema import CreateTable
from database import Base
from typing import List
import sys
import inspect
from datetime import datetime


class Anime(Base):
    """Anime"""

    __tablename__ = "anime"

    title_ro: Mapped[str]
    mal_url: Mapped[str]

    qitems: Mapped[List["QItem"]] = relationship(
        back_populates="qitem", cascade="all, delete-orphan"
    )
    p_mal: Mapped["PAnimeMAL"] = relationship(
        back_populates="p_anime_mal", cascade="all, delete-orphan"
    )


class QItem(Base):
    """Quiz Item"""

    __tablename__ = "qitem"

    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.id"))
    category: Mapped[str]  # opening, ending
    number: Mapped[int]

    anime: Mapped["Anime"] = relationship(back_populates="anime")
    sources: Mapped[List["QItemSource"]] = relationship(
        back_populates="qitem_source", cascade="all, delete-orphan"
    )
    difficulties: Mapped[List["QItemDifficulty"]] = relationship(
        back_populates="qitem_difficulty", cascade="all, delete-orphan"
    )
    __table_args__ = (UniqueConstraint("category", "number", "_category_number_uc"),)


class QItemSource(Base):
    """Source for Quiz Item"""

    __tablename__ = "qitem_source"

    qitem_id: Mapped[int] = mapped_column(ForeignKey("qitem.id"))
    platform: Mapped[str]  # youtube, torrent, local_file
    path: Mapped[str]  # youtube: url, torrent: magnet-url?, local_file: path
    added_by: Mapped[str]  # manual (user_id from bot), auto (script name)

    qitem: Mapped["QItem"] = relationship(back_populates="qitem")
    timings: Mapped[List["QItemSourceTiming"]] = relationship(
        back_populates="qitem_source_timing", cascade="all, delete-orphan"
    )


class QItemSourceTiming(Base):
    """Timing (guess/reveal start) for Quiz Item Source"""

    __tablename__ = "qitem_source_timing"

    qitem_source_id: Mapped[int] = mapped_column(ForeignKey("qitem_source.id"))
    guess_start: Mapped[float]
    reveal_start: Mapped[float]

    qitem_source: Mapped["QItemSource"] = relationship(back_populates="qitem_source")


class QItemDifficulty(Base):
    """Quiz Difficulty for Quiz Item"""

    __tablename__ = "qitem_difficulty"

    qitem_id: Mapped[int] = mapped_column(ForeignKey("qitem.id"))
    value: Mapped[int]  # 0 - 100
    added_by: Mapped[str]  # manual (user_id from bot), auto (script name)

    qitem: Mapped["QItem"] = relationship(back_populates="qitem")


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

    anime: Mapped["Anime"] = relationship(back_populates="anime")


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

    anime: Mapped["Anime"] = relationship(back_populates="anime")


class PAnimeAniDB(Base):
    """Parsed Anime information from AniDB"""

    __tablename__ = "p_anime_anidb"

    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.id"))

    url: Mapped[str]
    airing_start: Mapped[datetime]
    airing_end: Mapped[datetime]

    anime: Mapped["Anime"] = relationship(back_populates="anime")


class PQItemAniDB(Base):
    """Parsed Quiz Item information from AniDB"""

    __tablename__ = "p_qitem_anidb"

    qitem_id: Mapped[int] = mapped_column(ForeignKey("qitem.id"))

    url: Mapped[str]
    main_title: Mapped[str]
    official_name: Mapped[str]
    performer: Mapped[str]
    rating_value: Mapped[float]

    qitem: Mapped["QItem"] = relationship(back_populates="qitem")


def print_tables():
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and issubclass(obj, Base) and name != "Base":
            print(CreateTable(obj.__table__))


if __name__ == "__main__":
    print_tables()
