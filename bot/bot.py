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
 
 
class Bot:
    def __init__(self, token_fp: str, db_handler: Handler):
        with open(token_fp, 'r') as f:
            token = f.read()
        self.application = Application.builder().token(token).build()
        self.handler = db_handler
        self.setup()
    
    def setup(self):
        self.state_keys = [
            'MENU',
            'ANIME_INPUT',
            'ANIME_INFO',
            'QITEMS_LIST',
        ]
        
        self.states = { k: v for k, v in enumerate(self.state_keys) }
        
        self.conv_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.ALL, self.menu)],
            states={
                self.states['MENU']: [
                    E.MessageHandler(filters.Regex('^Add new anime$'), self.anime_input)
                ],
                self.states['ANIME_INPUT']: [
                    MessageHandler(filters.TEXT, self.anime_info)
                ],
                self.states['ANIME_INFO']: [
                    E.MessageHandler(filters.Regex('^Manage OP & ED$'), self.qitems_list),
                    E.MessageHandler(filters.Regex('^Find another anime$'), self.anime_input),
                    E.MessageHandler(filters.Regex('^Return to menu$'), self.menu),
                ],
            },
            fallbacks=[CommandHandler('stop', self.stop)]
        )
        
        self.application.add_handler(self.conv_handler)
    
    def start(self):
        self.application.run_polling(allowed_updates=T.Update.ALL_TYPES)
        
    # --- CALLBACKS
        
    async def menu(self, update: T.Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text(
            text='Choose action',
            reply_markup=T.ReplyKeyboardMarkup([
                ['Add new anime'],
            ])
        )

        return self.state['MENU']


    async def anime_input(self, update: T.Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text(
            text='Write anime url on MAL or Shikimori',
        )

        return self.states['ANIME_INPUT']


    async def stop(self, update: T.Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return ConversationHandler.END


    async def anime_info(self, update: T.Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        url = update.message.text
        try:
            anime, new = await self.handler.add_anime(url)
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
            
            return self.state['ANIME_INFO']
        except RuntimeError as e:
            await update.message.reply_text(text=e.args[0])
            return self.state['ANIME_INPUT']


    async def qitems_list(self, update: T.Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return await self.menu(update, context)