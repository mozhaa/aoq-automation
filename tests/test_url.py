from aoq.parse.url import *


def test_mal_valid():
    url = 'https://myanimelist.net/anime/21/One_Piece?q=one%20piece&cat=anime'
    url_parser = MALUrlParser(url)
    assert url_parser.is_valid()

def test_mal_invalid():
    url = 'https://shikimori.one/animes/57181-ao-no-hako'
    url_parser = MALUrlParser(url)
    assert not url_parser.is_mal_url()
    assert not url_parser.is_mal_anime_url()

def test_mal_not_anime():
    url = 'https://myanimelist.net/news/71892880'
    url_parser = MALUrlParser(url)
    assert url_parser.is_mal_url()
    assert not url_parser.is_mal_anime_url()

def test_mal_to_shiki():
    url = 'https://myanimelist.net/anime/57181'
    url_parser = MALUrlParser(url)
    assert url_parser.shiki_url == 'https://shikimori.one/animes/57181'

def test_mal_id():
    url = 'https://myanimelist.net/anime/57181'
    url_parser = MALUrlParser(url)
    assert url_parser.mal_id == 57181

def test_shiki_valid():
    url = 'https://shikimori.one/animes/57181-ao-no-hako'
    url_parser = ShikiUrlParser(url)
    assert url_parser.is_valid()

def test_shiki_invalid():
    url = 'https://myanimelist.net/animes/57181'
    url_parser = ShikiUrlParser(url)
    assert not url_parser.is_shiki_url()
    assert not url_parser.is_shiki_anime_url()

def test_shiki_not_anime():
    url = 'https://shikimori.one/forum/animanga/anime-57181-ao-no-hako/566430-epizod-4'
    url_parser = ShikiUrlParser(url)
    assert url_parser.is_shiki_url()
    assert not url_parser.is_shiki_anime_url()
    
def test_shiki_to_mal():
    url = 'https://shikimori.one/animes/57181-ao-no-hako'
    url_parser = ShikiUrlParser(url)
    assert url_parser.mal_url == 'https://myanimelist.net/anime/57181'