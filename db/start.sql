CREATE TABLE IF NOT EXISTS Anime(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title_en TEXT,
    title_ro TEXT,
    title_ru TEXT,
    mal_url TEXT,
    shiki_url TEXT,
    poster_url TEXT
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