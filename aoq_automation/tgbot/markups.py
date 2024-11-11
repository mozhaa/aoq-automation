from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from typing import List
import math


default_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/start")]])
menu_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Find anime")]])
anime_page_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Manage OP & ED")],
        [KeyboardButton(text="Find another anime")],
        [KeyboardButton(text="Back to menu")],
    ]
)
qitem_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Back to OP & ED page")],
        [KeyboardButton(text="Back to Anime page")],
        [KeyboardButton(text="Back to menu")],
    ]
)


class QItemsKeyboardMarkup:
    rows: int = 2
    cols: int = 5

    def __init__(self, qitems: List[str], page: int = 0) -> None:
        self.qitems = qitems
        self.page = page

    def as_markup(self) -> ReplyKeyboardMarkup:
        page_size = self.rows * self.cols
        current_qitems = self.qitems[
            page_size * self.page : page_size * (self.page + 1)
        ]

        keyboard = [
            [KeyboardButton(text="-") for _ in range(self.cols)]
            for _ in range(self.rows)
        ]
        row, col = 0, 0
        for qitem in current_qitems:
            keyboard[row][col] = KeyboardButton(text=qitem)
            col += 1
            if col >= self.cols:
                col = 0
                row += 1

        qitems_page_markup = ReplyKeyboardBuilder.from_markup(
            ReplyKeyboardMarkup(keyboard=keyboard)
        )
        qitems_page_markup.adjust(*([self.cols] * self.rows))

        qitems_page_markup.attach(
            ReplyKeyboardBuilder.from_markup(
                markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Previous page"),
                            KeyboardButton(text="Next page"),
                        ],
                        [KeyboardButton(text="Add new")],
                        [KeyboardButton(text="Back to Anime page")],
                        [KeyboardButton(text="Back to menu")],
                    ]
                )
            )
        )

        return qitems_page_markup.as_markup()

    def next_page(self) -> None:
        self.page = self._clamp_page(self.page + 1)

    def previous_page(self) -> None:
        self.page = self._clamp_page(self.page - 1)

    @property
    def _n_pages(self) -> int:
        return math.ceil(len(self.qitems) / self.rows / self.cols)

    def _clamp_page(self, page: int) -> int:
        return max(0, min(page, self._n_pages - 1))
