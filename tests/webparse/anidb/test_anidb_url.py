from aoq_automation.webparse.anidb import AniDBUrlParser


def test_valid():
    valid_urls = [
        "https://anidb.net/perl-bin/animedb.pl?show=anime&aid=4112",
        "https://anidb.net/anime/4112",
        "http://anidb.net/anime/4112",
        "http://www.anidb.net/anime/4112",
        "www.anidb.net/anime/4112",
    ]
    for url in valid_urls:
        assert AniDBUrlParser(url).is_valid()


def test_invalid():
    invalid_urls = [
        "https://myanimelist.net/anime/1254/Saint_Seiya",
        "https://shikimori.one/mangas/1706-jojo-no-kimyou-na-bouken-part-7-steel-ball-run",
        "http://shikiori.one/animes/1",
        "https://stackoverflow.com/questions/1263451/python-decorators-in-classes",
        "https://anidb.net/perl-bin/animedb.pl?show=anime&",
        "http://anidb.net/animes/4112",
        "http://anidb.net/anime",
        "http://anidb.net/anime/",
    ]
    for url in invalid_urls:
        assert not AniDBUrlParser(url).is_valid()
