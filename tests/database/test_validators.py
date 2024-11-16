from aoq_automation.database.models import *
import pytest


def test_category():
    valid = [
        "OP",
        "op",
        "opening",
        "Opening",
        "Ending",
        "ED",
        "ed",
        "ending",
        "Op",
        "Ed",
    ]
    invalid = [
        "opnening",
        "OpEd",
        "O",
        "End",
        "eding",
        "эндинг",
        "опенинг",
        "ОП",
        "оп",
        1,
    ]
    for category in valid:
        QItem(category=category)
    for category in invalid:
        with pytest.raises(ValueError):
            QItem(category=category)


def test_number():
    valid = [1, 2, 3, 4, 5]
    invalid = [0, -1, -2, -3, "OP", "2"]
    for number in valid:
        QItem(number=number)
    for number in invalid:
        with pytest.raises(ValueError):
            QItem(number=number)


def test_timestamp():
    valid = {
        "1": 1,
        "1.5": 1.5,
        "00:01.12": 1.12,
        "00:00:00.2": 0.2,
        "13.5": 13.5,
    }
    invalid = ["00.02.12", "00:00,5", "78.4", 1.5]
    for x, expected in valid.items():
        assert QItemSourceTiming(guess_start=x).guess_start == expected
    for x in invalid:
        with pytest.raises(ValueError):
            QItemSourceTiming(guess_start=x)


def test_difficulty():
    valid = {
        "1": 1,
        "99": 99,
        "Very Hard": 70,
        "EASY": 20,
    }
    invalid = ["-1", "veryhard", "Normal", 15]
    for x, expected in valid.items():
        assert QItemDifficulty(value=x).value == expected
    for x in invalid:
        with pytest.raises(ValueError):
            QItemDifficulty(value=x)
