from aoq_automation.parser import MALUrlParser


def test_mal_valid():
    assert MALUrlParser(
        "https://myanimelist.net/anime/21/One_Piece?q=one%20piece&cat=anime"
    ).is_valid()


def test_mal_invalid():
    assert not MALUrlParser(
        "https://shikimori.one/animes/57181-ao-no-hako"
    ).is_mal_url()
    assert not MALUrlParser(
        "https://shikimori.one/animes/57181-ao-no-hako"
    ).is_mal_anime_url()


def test_mal_not_anime():
    assert MALUrlParser("https://myanimelist.net/news/71892880").is_mal_url()
    assert not MALUrlParser("https://myanimelist.net/news/71892880").is_mal_anime_url()


def test_mal_id():
    assert MALUrlParser("https://myanimelist.net/anime/57181").mal_id == 57181


def test_mal_invalid_id():
    assert not MALUrlParser("https://myanimelist.net/anime").is_valid()
    assert not MALUrlParser("https://myanimelist.net/anime/").is_valid()
    assert not MALUrlParser("https://myanimelist.net/anime/trsdp").is_valid()
