from aoq.parse.mal import *
from pyquery import PyQuery
from pathlib import Path
import pytest

@pytest.fixture
def page_1():
    page = MALAnimeParser('https://myanimelist.net/anime/57181')
    with open(Path('.') / 'tests' / 'files' / 'mal-ao-no-hako.html', 'r') as f:
        page.page = PyQuery(f.read())
    with open(Path('.') / 'tests' / 'files' / 'mal-stats-ao-no-hako.html', 'r') as f:
        page.stats_page = PyQuery(f.read())
    return page

def test_mal_id(page_1):
    assert page_1.mal_id == 57181

def test_url(page_1):
    assert page_1.url == 'https://myanimelist.net/anime/57181/Ao_no_Hako'

def test_stats_url(page_1):
    assert page_1.stats_url == 'https://myanimelist.net/anime/57181/Ao_no_Hako/stats'

def test_poster_url(page_1):
    assert page_1.poster_url == 'https://cdn.myanimelist.net/images/anime/1341/145349.jpg'

def test_rating(page_1):
    assert page_1.rating == 8.4
    
def test_ranked(page_1):
    assert page_1.ranked == 193

def test_popularity(page_1):
    assert page_1.popularity == 1807

def test_favorites(page_1):
    assert page_1.favorites == 916

def test_title_en(page_1):
    assert page_1.title_en == 'Blue Box'

def test_title_ro(page_1):
    assert page_1.title_ro == 'Ao no Hako'

def test_watching(page_1):
    assert page_1.watching == 71897

def test_completed(page_1):
    assert page_1.completed == 11

def test_on_hold(page_1):
    assert page_1.on_hold == 1061

def test_dropped(page_1):
    assert page_1.dropped == 835

def test_plan_to_watch(page_1):
    assert page_1.plan_to_watch == 54638



