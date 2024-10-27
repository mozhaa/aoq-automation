import os
import re
import sys
import json
import time
import asyncio
import threading
import parser.mal as mal
from db.db import DB
from db.handler import Handler
from db.types import *
from termcolor import colored
from datetime import datetime, timedelta

def main():
    global search_results
    
    json_fp = sys.argv[1]
    with open(json_fp, 'r') as f:
        data = json.load(f)
    
    db = DB()
    cur = db.get_cursor()
    handler = Handler(db.get_cursor())
    
    search_results = dict()
    cond = threading.Condition()
    t = threading.Thread(target=search_mal, args=(data, cond))
    t.daemon = True
    t.start()
    
    for qitem in data:
        os.system('clear')
        title = qitem['title']
        print(f'Opening title: {qitem["title"]}')
        with cond:
            cond.wait_for(lambda: title in search_results.keys())
        current_search_results = search_results[title]
        print(f'Search results:')
        preferred_choice = None
        db_results = dict()
        for i, (href, atitle) in enumerate(current_search_results):
            mal_url_parser = mal.MALUrlParser(href)
            if not mal_url_parser.is_valid():
                color = 'red'
            else:
                mal_id = mal_url_parser.get_mal_id()
                db_result = cur.exists(Anime(mal_id=mal_id), key_columns=['mal_id'])
                if db_result is not None:
                    db_results[i] = db_result
                    if preferred_choice is None:
                        preferred_choice = i
                        color = 'green'
                    else:
                        color = 'cyan'
                else:
                    color = 'white'
            print(colored(f'{i}. {atitle} ({href})', color=color))
        choice = None
        while choice is None:
            choice = input(f'Select anime{"" if preferred_choice is None else " [" + str(preferred_choice) + "]"}: ')
            if choice == '':
                choice = preferred_choice
            elif choice.isdigit():
                choice = int(choice)
            else:
                choice = None
        if choice not in db_results.keys():
            anime_id = handler.add_anime(current_search_results[0])
        else:
            anime_id = db_results[choice]
        
        op_match = re.match('.*OP ([0-9]*)')
        op_num = None
        if op_match is not None:
            op_num = int(op_match.group(1))
        else:
            while (op_num is None) or ((op_num != '') and (not op_num.isdigit())):
                op_num = input(f'Opening number [1]: ')
            op_num = int(op_num)
        qitem_id = cur.insert(QItem(anime_id=anime_id, item_type=0, num=op_num))
        if 'url' in qitem.keys():
            qitemsource_id = cur.insert(QItemSource(qitem_id=qitem_id, priority=5, source_type=0, path=qitem['url']))
        else:
            qitemsource_id = cur.insert(QItemSource(qitem_id=qitem_id, priority=5, source_type=2, path=qitem['path']))
        guess_time = convert_str_to_seconds(qitem['guess_time'])
        reveal_time = convert_str_to_seconds(qitem['reveal_time'])
        cur.insert(QItemSourceTiming(qitemsource_id=qitemsource_id, author='aoq_tk', guess_time=guess_time, reveal_time=reveal_time))
        
        difficulties = ['very easy', 'easy', 'medium', 'hard', 'very hard']
        diff = qitem['difficulty']
        diff = difficulties.index(diff)
        cur.insert(QItemDifficulty(qitem_id=qitem_id, author='aoq_tk', value=diff))
        
def convert_str_to_seconds(s: str) -> float:
    d = datetime.strptime('%H:%M:%S.%f', s)
    t = timedelta(hours=d.hour, minutes=d.minute, seconds=d.second, microseconds=d.microsecond)
    return t.total_seconds()

def possible_titles(qitem):
    titles = qitem['title'].split(' ')
    titles = [' '.join(titles[:i]) for i in range(1, len(titles) + 1)]
    return titles

def search_mal(data, cond):
    global search_results
    BATCH_SIZE = 5
    all_titles = [qitem['title'] for qitem in data]
    for i in range(0, len(all_titles), BATCH_SIZE):
        titles = all_titles[i:i + BATCH_SIZE]
        asyncio.run(asyncio.gather([search_title(title, i, cond) for i, title in enumerate(titles)]))
        time.sleep(1)
        
async def search_title(title, starttime, cond):
    global search_results
    time.sleep(starttime)
    result = await mal.search(title)
    with cond:
        search_results[title] = result
        cond.notify_all()
        
if __name__ == '__main__':
    main()