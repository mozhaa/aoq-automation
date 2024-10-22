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
        logger.info(sql + '; ' + str(parameters))
        result = self.cur.execute(sql, parameters)
        return result
        
    def insert(self, obj: db.objects.DBObject):
        result = self.execute(
            sql=f'INSERT INTO {type(obj).__name__} {obj.select_columns()} VALUES {obj.select_placeholders()} RETURNING id;', 
            parameters=obj.select_parameters()
        ).fetchall()[0][0]
        self.con.commit()
        return result
    
    def exists(self, obj: db.objects.DBObject, key_columns: List[str]) -> bool:
        '''Check if element with key_columns same as obj exists in DB'''
        return self.execute(
            sql=f'SELECT id FROM {type(obj).__name__} WHERE {obj.where_placeholders(key_columns)}',
            parameters=obj.where_parameters(key_columns)
        ).fetchone() is not None
    
    def update(self, obj: db.objects.DBObject, key_columns: List[str]):
        '''Find element by key_columns and update it with obj data'''
        parameters = obj.where_parameters(key_columns)
        parameters.update(obj.set_parameters())
        result = self.execute(
            sql=f'UPDATE {type(obj).__name__} SET {obj.set_placeholders()} WHERE {obj.where_placeholders(key_columns)} RETURNING id;',
            parameters=parameters
        ).fetchall()[0][0]
        self.con.commit()
        return result


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