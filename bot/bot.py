import logging
import textwrap
from typing import *

from db.handler import Handler

import telegram as T
import telegram.ext as E
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

(
    MENU,
    ANIME_INPUT,
    ANIME_INFO,
    QITEMS_LIST,
) = range(4)
    

async def menu(update: T.Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        text='Choose action',
        reply_markup=T.ReplyKeyboardMarkup([
            ['Add new anime'],
        ])
    )

    return MENU


async def anime_input(update: T.Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        text='Write anime url on MAL or Shikimori',
    )

    return ANIME_INPUT


async def stop(update: T.Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END


async def anime_info(update: T.Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.message.text
    try:
        anime, new = await db.add_anime(url)
        debug_msg = '\n'.join(['{} = {}'.format(key, value) for key, value in anime.__dict__.items()])
        
        msg = textwrap.dedent(f'''
            {'<i>New!</i>' if new else ''}
            
            <b>Romaji title:</b> {anime.title_ro}
            <b>English title:</b> {anime.title_en}
            <b>Russian title:</b> {anime.title_ru}
            
            On Shikimori: <i>{anime.shiki_rating:.2f}</i>
            '''
        )
        
        await update.message.reply_photo(
            caption=debug_msg,
            photo=anime.shiki_poster_url,
            parse_mode='HTML',
            reply_markup=T.ReplyKeyboardMarkup([
                ['Manage OP & ED'],
                ['Find another anime'],
                ['Return to menu'],
            ]),
        )
        
        return ANIME_INFO
    except RuntimeError as e:
        logger.info(e.args[0])
        await update.message.reply_text(text=e.args[0])
        return ANIME_INPUT


async def qitems_list(update: T.Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await menu(update, context)


def main(handler: Handler):
    global db
    db = handler
    start_logger()
    
    with open('bot/token.hidden', 'r') as f:
        token = f.read()
    application = Application.builder().token(token).build()
    
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.ALL, menu)],
        states={
            MENU: [
                E.MessageHandler(filters.Regex('^Add new anime$'), anime_input)
            ],
            ANIME_INPUT: [
                MessageHandler(filters.TEXT, anime_info)
            ],
            ANIME_INFO: [
                E.MessageHandler(filters.Regex('^Manage OP & ED$'), qitems_list),
                E.MessageHandler(filters.Regex('^Find another anime$'), anime_input),
                E.MessageHandler(filters.Regex('^Return to menu$'), menu),
            ],
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=T.Update.ALL_TYPES)
    
    
def start_logger():
    global logger
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)