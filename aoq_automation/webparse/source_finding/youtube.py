import re
from typing import *

from rapidfuzz import fuzz
from youtubesearchpython.__future__ import VideosSearch

from aoq_automation.database.database import db
from aoq_automation.database.models import *
from aoq_automation.database.utils import parse_time_as_seconds

from .strategy import SourceFindingStrategy


def similarity(
    x: float, y: float, sigma: float = -2, p: float = 2, k: float = 0
) -> float:
    return max(0, 1 - abs(x - y) * k) / (1 + 10**sigma * abs(x - y) ** p)


def assymetrical_similarity(
    x: float,
    y: float,
    sigma_left: float = -1,
    p_left: float = 4,
    k_left: float = 0,
    sigma_right: float = -8,
    p_right: float = 6,
    k_right: float = 0.008,
) -> float:
    if x < y:
        return similarity(x, y, sigma=sigma_left, p=p_left, k=k_left)
    else:
        return similarity(x, y, sigma=sigma_right, p=p_right, k=k_right)


def contrast(x: float, k: float = 2) -> float:
    if x < 0.5:
        return (x * 2) ** k / 2
    else:
        return 1 - ((1 - x) * 2) ** k / 2


def preprocess(title: str, num_w: int = 1) -> str:
    title = title.lower().strip()
    title = re.sub("[^A-Za-z0-9 \\-!?:/]", " ", title)
    title = re.sub("\\bopening\\b", "op", title)
    title = re.sub("\\bending\\b", "ed", title)
    title = re.sub("\\b(op|ed)\\b +([0-9]+)", "\\1\\2", title)
    title = re.sub("\\b(op|ed)\\b", "\\g<1>1", title)
    title = re.sub("\\bseason\\b +([0-9]+)", "s\\1", title)
    numerals = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"]
    for i, s in enumerate(numerals):
        title = re.sub(f"{s} +\\bseason\\b", f"s{i+1}", title)
    if num_w > 1:
        title = re.sub("[0-9]", "\\g<0>" * num_w, title)
    title = re.sub(" {2,}", " ", title)
    return title


def helpers_score(helpers: List[str], s: str) -> float:
    return len(re.findall("|".join([re.escape(w) for w in helpers]), s)) / len(helpers)


class YoutubeSearchStrategy(SourceFindingStrategy):
    def __init__(
        self,
        title_algorithm: Callable[[str, str], float] = fuzz.token_ratio,
        score_threshold: float = 0.0,
    ) -> None:
        self.title_algorithm = title_algorithm
        self.score_threshold = score_threshold
        self.possible_durations = [90, 150]
        self.helpers = ["Creditless", "4K", "HD", "1080p"]
        self.negative_helpers = ["Cover", "AMV", "Full", "Lyrics"]

    async def get_sorted_sources(
        self, qitem_id: int
    ) -> List[Tuple[QItemSource, float]]:
        async with db.async_session() as session:
            qitem = await session.get(QItem, qitem_id)
            anime = await qitem.awaitable_attrs.anime
            p_anime_mal = await anime.awaitable_attrs.p_mal
            title_ro = anime.title_ro
            title_en = p_anime_mal.title_en

            scores = {}
            for title in [title_ro, title_en]:
                category = self._extended_category(qitem.category)
                query = f"{title} {category} {qitem.number}"
                results = (await VideosSearch(query=query, limit=10).next())["result"]
                for video in results:
                    score = self._score(video, query)
                    link = video["link"]
                    scores[link] = max(scores.get(link, 0), score)

            scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            scores = [
                (
                    QItemSource(
                        qitem=qitem,
                        platform="youtube",
                        path=link,
                        added_by=self.__class__.__name__,
                    ),
                    score,
                )
                for link, score in scores
            ]

        return scores

    async def find_source(self, qitem_id: int) -> Optional[QItemSource]:
        sources = await self.get_sorted_sources(qitem_id)
        best_source = sources[0]
        if best_source[1] > self.score_threshold:
            return best_source[0]

    def _title_score(self, title: str, query: str) -> float:
        return self.title_algorithm(preprocess(query), preprocess(title)) / 100

    def _helpers_score(self, title: str) -> float:
        return helpers_score(self.helpers, title)

    def _negative_helpers_score(self, title: str) -> float:
        return helpers_score(self.negative_helpers, title)

    def _duration_score(self, duration: str) -> float:
        s = parse_time_as_seconds(duration)
        return max([assymetrical_similarity(s, d) for d in self.possible_durations])

    def _score(self, video: Dict[str, Any], query: str) -> float:
        negative_helpers_score = self._negative_helpers_score(video["title"])
        if negative_helpers_score > 0:
            return 0

        title_score = self._title_score(video["title"], query)
        helpers_score = self._helpers_score(video["title"])
        duration_score = self._duration_score(video["duration"])

        total_score = (
            contrast(title_score, 2.5) ** 2 * duration_score + 0.5 * helpers_score
        )

        return total_score

    def _extended_category(self, category: str) -> str:
        return {"OP": "Opening", "ED": "Ending"}[category]
