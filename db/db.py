import sqlite3
import logging
from pathlib import Path
from typing import Type, List
import db.objects

logger = logging.getLogger(__name__)

class SmartCursor(sqlite3.Cursor):
    def __init__(self, cur: sqlite3.Cursor, con: sqlite3.Connection):
        self.cur = cur
        self.con = con
    
    def execute(self, sql: str, parameters):
        logger.info(sql)
        result = self.cur.execute(sql, parameters)
        self.con.commit()
        return result
        
    def insert(self, obj: db.objects.DBObject):
        return self.execute(
            sql=f'INSERT INTO {type(obj).__name__} {obj.as_sql_keys()} VALUES {obj.as_sql_placeholders()};', 
            parameters=obj.as_sql_values()
        )
    
    def exists(self, obj_type: Type[db.objects.DBObject], conditions: List[str], parameters) -> bool:
        return self.execute(
            sql=f'SELECT id FROM {obj_type.__name__} WHERE {" AND ".join(conditions)}',
            parameters=parameters
        ).fetchone() is not None


class DB:
    def __init__(self, fp: str = 'db/database.db') -> None:
        exist = Path(fp).is_file()
        
        self.con = sqlite3.connect(fp)
        self.cur = self.con.cursor()
        
        if not exist:
            with open('db/start.sql', 'r') as f:
                self.cur.executescript(f.read())
    
    def get_cursor(self) -> SmartCursor:
        return SmartCursor(self.con.cursor(), self.con)

    def close(self):
        self.con.close()