from sqlalchemy import BigInteger, Integer, Text, ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.schema import CreateTable
from database import Base
from typing import List
import sys
import inspect


class Anime(Base):
    __tablename__ = "anime"

    title_ro: Mapped[str]
    mal_url: Mapped[str]

    qitems: Mapped[List["QItem"]] = relationship(
        back_populates="qitem", cascade="all, delete-orphan"
    )


class QItem(Base):
    __tablename__ = "qitem"

    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.id"))
    category: Mapped[str] # opening, ending
    number: Mapped[int]

    anime: Mapped["Anime"] = relationship(back_populates="anime")
    sources: Mapped[List["QItemSource"]] = relationship(
        back_populates="qitem_source", cascade="all, delete-orphan"
    )
    difficulties: Mapped[List["QItemDifficulty"]] = relationship(
        back_populates="qitem_difficulty", cascade="all, delete-orphan"
    )


class QItemSource(Base):
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
    __tablename__ = "qitem_source_timing"

    qitem_source_id: Mapped[int] = mapped_column(ForeignKey("qitem_source.id"))
    guess_start: Mapped[float]
    reveal_start: Mapped[float]

    qitem_source: Mapped["QItemSource"] = relationship(back_populates="qitem_source")


class QItemDifficulty(Base):
    __tablename__ = "qitem_difficulty"

    qitem_id: Mapped[int] = mapped_column(ForeignKey("qitem.id"))
    value: Mapped[int]  # 0 - 100
    added_by: Mapped[str]  # manual (user_id from bot), auto (script name)

    qitem: Mapped["QItem"] = relationship(back_populates="qitem")


def print_tables():
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and issubclass(obj, Base) and name != "Base":
            print(CreateTable(obj.__table__))


if __name__ == "__main__":
    print_tables()
