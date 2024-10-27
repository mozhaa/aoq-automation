from dataclasses import dataclass
from db.objects import DBObject

@dataclass
class Anime(DBObject):
	title_en = None
	title_ro = None
	title_ru = None
	aired_start = None
	aired_end = None
	shiki_url = None
	shiki_poster_url = None
	shiki_poster_thumbnail_url = None
	shiki_rating = None
	shiki_rating_count = None
	shiki_plan_to_watch = None
	shiki_completed = None
	shiki_watching = None
	shiki_dropped = None
	shiki_on_hold = None
	shiki_favorites = None
	shiki_comments = None
	mal_url = None
	mal_id = None
	mal_poster_url = None
	mal_rating = None
	mal_favorites = None
	mal_popularity = None
	mal_ranked = None
	mal_plan_to_watch = None
	mal_completed = None
	mal_watching = None
	mal_dropped = None
	mal_on_hold = None

@dataclass
class QItem(DBObject):
	anime_id = None
	id = None
	item_type = None
	num = None
	song_name = None
	song_artist = None
	episodes = None
	state = None

@dataclass
class QItemSource(DBObject):
	qitem_id = None
	id = None
	priority = None
	source_type = None
	path = None

@dataclass
class QItemSourceTiming(DBObject):
	qitemsource_id = None
	id = None
	author = None
	guess_time = None
	reveal_time = None

@dataclass
class QItemDifficulty(DBObject):
	qitem_id = None
	id = None
	author = None
	value = None
