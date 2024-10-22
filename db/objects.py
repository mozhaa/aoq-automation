from typing import *

class DBObject:
    def __init__(self):
        pass

    def select_parameters(self) -> Dict:
        '''Example output: {"title_en": "aa", "title_ru": "sdf", ...}'''
        return {key: value for key, value in self.__dict__.items() if value is not None}
    
    def select_placeholders(self) -> str:
        '''Example output: "(:title_en, :title_ru, :title_ro, :year)"'''
        return '(' + ', '.join([f':{key}' for key, value in self.__dict__.items() if value is not None]) + ')'
    
    def select_columns(self) -> str:
        '''Example output: "(title_en, title_ru, title_ro, year)"'''
        return '(' + ', '.join([key for key, value in self.__dict__.items() if value is not None]) + ')'
    
    def where_parameters(self, key_columns: List[str]) -> Dict:
        return {f'{col}': getattr(self, col) for col in key_columns}
    
    def where_placeholders(self, key_columns: List[str]):
        return ' AND '.join(["{col} = :{col}".format(col=col) for col in key_columns])
    
    def set_placeholders(self):
        return self.where_placeholders(self.__dict__.keys())
    
    def set_parameters(self):
        return self.where_parameters(self.__dict__.keys())
    
    def from_sql(cls, sql):
        return cls(*sql)