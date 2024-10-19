CREATE TABLE Anime(
    id integer primary key AUTOINCREMENT,
    title_en varchar(256),
    title_ro varchar(256),
    title_ru varchar(256),
    mal_url varchar(256),
    shiki_url varchar(256),
    poster_url varchar(256),
);

CREATE TABLE QItem(
    id integer primary key AUTOINCREMENT,
    anime_id integer references Anime(id),
    type integer, -- op, ed
    num integer,
    best_source integer references QItemSource(id),
);

CREATE TABLE QItemSource(
    id integer primary key AUTOINCREMENT,
    qitem_id integer references QItem(id),
    priority integer,
    type integer, -- youtube, torrent, file
    path varchar(512),
);

CREATE TABLE QitemSourceTiming(
    id integer primary key AUTOINCREMENT,
    qitemsource_id integer references QItemSource(id),
    type integer, -- manual, auto
    guess_time float,
    reveal_time float,
);

CREATE TABLE QItemDifficulty(
    id integer primary key AUTOINCREMENT,
    qitem_id integer references QItem(id),
    author integer, -- auto, id***, ...
    value integer, -- very easy, easy, medium, hard, very hard
);