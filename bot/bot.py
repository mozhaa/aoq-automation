import logging
import textwrap
from typing import *

from db.handler import Handler

import telegram
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

(
    CHOOSING_ACTION,
    ADDING_NEW_ANIME,
    
) = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        text='Choose action',
        reply_markup=ReplyKeyboardMarkup([['Add new anime']])
    )

    return CHOOSING_ACTION


async def action_add_new_anime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        text='Write anime url on MAL or Shikimori',
    )

    return ADDING_NEW_ANIME


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END


async def add_new_anime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.message.text
    try:
        anime, new = await db.add_anime(url)
        await update.message.reply_photo(
            caption=textwrap.dedent(f'''
            {'<i>New!</i>' if new else ''}
            
            <b>Romaji title:</b> {anime.title_ro}
            <b>English title:</b> {anime.title_en}
            <b>Russian title:</b> {anime.title_ru}
            
            On Shikimori: <i>{anime.shiki_rating:.2f}</i>
            '''),
            photo=anime.shiki_poster_url,
            parse_mode='HTML',
        )
        return CHOOSING_ACTION
    except ValueError as e:
        await update.message.reply_text(text=e.args[0])
        return ADDING_NEW_ANIME


def main(handler: Handler):
    global db
    db = handler
    
    with open('bot/token.hidden', 'r') as f:
        token = f.read()
        
    start_logger()

    application = Application.builder().token(token).build()
    
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.ALL, start)],
        states={
            CHOOSING_ACTION: [
                MessageHandler(filters.Regex('^Add new anime$'), action_add_new_anime)
            ],
            ADDING_NEW_ANIME: [
                MessageHandler(filters.TEXT, add_new_anime)
            ]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    
def start_logger():
    global logger
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)


# if __name__ == '__main__':
#    asyncio.run(main())