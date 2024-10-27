from db.db import DB
from db.handler import Handler
from bot.bot import Bot

def main():
    db = DB()
    handler = Handler(db.get_cursor())

    bot = Bot('bot/token.hidden', handler)
    bot.start()

    db.close()

if __name__ == '__main__':
    main()