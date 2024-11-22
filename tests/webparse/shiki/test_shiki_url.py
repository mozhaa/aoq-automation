from aoq_automation.webparse.shiki import ShikiUrlParser


def test_valid():
    valid_urls = [
        "https://shikimori.one/animes/y590-kage-kara-mamoru",
        "https://shikimori.one/animes/60022-one-piece-fan-letter",
        "https://shikimori.org/animes/60022",
        "shikimori.one/animes/21",
        "http://shikimori.one/animes/y28851",
        "http://www.shikimori.one/animes/y28851",
        "www.shikimori.one/animes/y28851",
    ]
    for url in valid_urls:
        assert ShikiUrlParser(url).is_valid()


def test_invalid():
    invalid_urls = [
        "https://myanimelist.net/anime/1254/Saint_Seiya",
        "https://shikimori.one/mangas/1706-jojo-no-kimyou-na-bouken-part-7-steel-ball-run",
        "http://shikiori.one/animes/1",
        "https://stackoverflow.com/questions/1263451/python-decorators-in-classes",
    ]
    for url in invalid_urls:
        assert not ShikiUrlParser(url).is_valid()
