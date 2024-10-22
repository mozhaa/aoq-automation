CREATE TABLE IF NOT EXISTS Anime(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title_en TEXT,
    title_ro TEXT,
    title_ru TEXT,
    aired_start TIMESTAMP,
    aired_end TIMESTAMP,

    shiki_url TEXT,
    shiki_poster_url TEXT,
    shiki_poster_thumbnail_url TEXT,
    shiki_rating REAL,
    shiki_rating_count INTEGER,
    shiki_plan_to_watch INTEGER,
    shiki_completed INTEGER,
    shiki_watching INTEGER,
    shiki_dropped INTEGER,
    shiki_on_hold INTEGER,
    shiki_favorites INTEGER,
    shiki_comments INTEGER,
    
    mal_url TEXT,
    mal_id INTEGER,
    mal_poster_url TEXT,
    mal_rating REAL,
    mal_favorites INTEGER,
    mal_popularity INTEGER,
    mal_ranked INTEGER,
    mal_plan_to_watch INTEGER,
    mal_completed INTEGER,
    mal_watching INTEGER,
    mal_dropped INTEGER,
    mal_on_hold INTEGER
);

CREATE TABLE IF NOT EXISTS QItem(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anime_id INTEGER REFERENCES Anime(id),
    item_type INTEGER, -- 0 = op, 1 = ed
    num INTEGER,
    song_name TEXT,
    song_artist TEXT,
    episodes TEXT,
    state INTEGER
);

CREATE TABLE IF NOT EXISTS QItemSource(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qitem_id INTEGER REFERENCES QItem(id),
    priority INTEGER,
    source_type INTEGER, -- 0 = youtube, 1 = torrent, 2 = file
    path TEXT
);

CREATE TABLE IF NOT EXISTS QitemSourceTiming(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qitemsource_id INTEGER REFERENCES QItemSource(id),
    author TEXT, -- manual, auto
    guess_time REAL,
    reveal_time REAL
);

CREATE TABLE IF NOT EXISTS QItemDifficulty(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qitem_id INTEGER REFERENCES QItem(id),
    author TEXT,
    value INTEGER -- very easy, easy, medium, hard, very hard
);