CREATE TABLE IF NOT EXISTS Anime(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anime_id INTEGER,
    title_en TEXT,
    title_ro TEXT,
    title_ru TEXT,
    mal_url TEXT,
    shiki_url TEXT,
    mal_poster_url TEXT,
    shiki_poster_url TEXT,
    shiki_poster_thumbnail_url TEXT,
    aired_start TIMESTAMP,
    aired_end TIMESTAMP,
    shiki_rating REAL,
    shiki_rating_count INTEGER,
    shiki_plan_to_watch INTEGER DEFAULT 0,
    shiki_completed INTEGER DEFAULT 0,
    shiki_watching INTEGER DEFAULT 0,
    shiki_dropped INTEGER DEFAULT 0,
    shiki_on_hold INTEGER DEFAULT 0,
    shiki_favorites INTEGER,
    shiki_comments INTEGER,
    mal_rating REAL,
    mal_favorites INTEGER,
    mal_popularity INTEGER,
    mal_ranked INTEGER,
    mal_plan_to_watch INTEGER DEFAULT 0,
    mal_completed INTEGER DEFAULT 0,
    mal_watching INTEGER DEFAULT 0,
    mal_dropped INTEGER DEFAULT 0,
    mal_on_hold INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS QItem(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anime_id INTEGER REFERENCES Anime(id),
    type INTEGER, -- op, ed
    num INTEGER
);

CREATE TABLE IF NOT EXISTS QItemSource(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qitem_id INTEGER REFERENCES QItem(id),
    priority INTEGER,
    type INTEGER, -- youtube, torrent, file
    path TEXT
);

CREATE TABLE IF NOT EXISTS QitemSourceTiming(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qitemsource_id INTEGER REFERENCES QItemSource(id),
    type INTEGER, -- manual, auto
    guess_time REAL,
    reveal_time REAL
);

CREATE TABLE IF NOT EXISTS QItemDifficulty(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qitem_id INTEGER REFERENCES QItem(id),
    author INTEGER, -- auto, id***, ...
    value INTEGER -- very easy, easy, medium, hard, very hard
);