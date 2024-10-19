import sqlite3
from pathlib import Path
import db.objects

class Cursor(sqlite3.Cursor):
    def insert(self, obj: db.objects.DBObject) -> None:
        self.execute(f'INSERT INTO {obj.__name__} {obj.as_sql_header()} VALUES {obj.as_sql};')
    
class DB:
    def __init__(self, fp: str = 'db/database.db') -> None:
        exist = Path(fp).is_file()
        
        self.con = sqlite3.connect(fp)
        self.cur = self.con.cursor()
        
        if not exist:
            with open('db/start.sql', 'r') as f:
                self.cur.executescript(f.read())
    
    def get_cursor(self) -> Cursor:
        return self.con.cursor()