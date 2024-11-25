from aoq_automation.webparse.mal import MALUrlParser


def test_valid():
    valid_urls = [
        "https://myanimelist.net/anime/21/One_Piece?q=one%20piece&cat=anime",
        "https://myanimelist.net/anime/57181",
        "http://myanimelist.net/anime/57181",
        "myanimelist.net/anime/57181",
        "www.myanimelist.net/anime/57181",
    ]
    for url in valid_urls:
        assert MALUrlParser(url).is_valid()


def test_invalid():
    invalid_urls = [
        "https://shikimori.one/animes/60022-one-piece-fan-letter",
        "https://shikimori.one/animes/57181-ao-no-hako"
        "https://myanimelist.net/news/71892880",
        "http://shikiori.one/animes/1",
        "https://stackoverflow.com/questions/1263451/python-decorators-in-classes",
        "https://myanimelist.net/anime",
        "https://myanimelist.net/anime/",
        "https://myanimelist.net/anime/trsdp",
        "https://myanimelist.net/animes/3255",
    ]
    for url in invalid_urls:
        assert not MALUrlParser(url).is_valid()


def test_mal_id():
    assert MALUrlParser("https://myanimelist.net/anime/57181").mal_id == 57181
