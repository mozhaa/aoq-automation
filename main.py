from db.db import DB
from db.handler import Handler
from bot import bot

def main():
    db = DB()
    handler = Handler(db.get_cursor())
    bot.main(handler)

if __name__ == '__main__':
    main()