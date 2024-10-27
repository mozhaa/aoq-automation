from typing import *
import textwrap
import telegram as T
import telegram.ext as E

from aoq.database import DatabaseCursor, Database
from .handler import Handler

PAGE_LIMIT: Final[int] = 10


class Bot:
    def __init__(self, token_fp: str, db: Database):
        with open(token_fp, 'r') as f:
            token = f.read()
        self.application = E.Application.builder().token(token).build()
        self.db = db
        self.setup()

    def setup(self):
        self.state_keys = [
            'MENU',
            'ANIME_INPUT',
            'ANIME_INFO',
            'LIST_QITEMS',
            'SHOW_QITEM',
            'EDIT_QITEM_PROPERTY',
            'DELETE_QITEM',
        ]

        self.states = {key: i for i, key in enumerate(self.state_keys)}

        self.conv_handler = E.ConversationHandler(
            entry_points=[E.MessageHandler(E.filters.ALL, self.menu)],
            states={
                self.states['MENU']: [
                    E.MessageHandler(E.filters.Regex('^Find anime$'), self.anime_input)
                ],
                self.states['ANIME_INPUT']: [
                    E.MessageHandler(E.filters.TEXT, self.anime_info)
                ],
                self.states['ANIME_INFO']: [
                    E.MessageHandler(E.filters.Regex('^Manage OP & ED$'), self.list_qitems),
                    E.MessageHandler(E.filters.Regex('^Find another anime$'), self.anime_input),
                    E.MessageHandler(E.filters.Regex('^Return to menu$'), self.menu),
                ],
                self.states['LIST_QITEMS']: [
                    E.CallbackQueryHandler(self.add_qitem, '^add$'),
                    E.CallbackQueryHandler(self.anime_info, '^back$'),
                    E.CallbackQueryHandler(self.anime_info, '^next$'),
                    E.CallbackQueryHandler(self.anime_info, '^prev$'),
                    E.CallbackQueryHandler(self.show_qitem, '^[0-9]$'),
                ],
            },
            fallbacks=[E.CommandHandler('stop', self.stop)]
        )

        self.application.add_handler(self.conv_handler)

    def start(self):
        self.application.run_polling(allowed_updates=T.Update.ALL_TYPES)

    # --- CALLBACKS

    async def menu(self, update: T.Update, context: E.ContextTypes.DEFAULT_TYPE) -> int:
        if context.user_data.get('handler') is None:
            context.user_data['handler'] = Handler(self.db.get_cursor())

        await update.message.reply_text(
            text='Choose action',
            reply_markup=T.ReplyKeyboardMarkup([
                ['Find anime'],
            ])
        )

        return self.states['MENU']


    async def anime_input(self, update: T.Update, context: E.ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text(
            text='Write anime url on MAL or Shikimori',
        )

        return self.states['ANIME_INPUT']


    async def stop(self, update: T.Update, context: E.ContextTypes.DEFAULT_TYPE) -> int:
        if context.user_data.get('handler') is not None:
            context.user_data['handler'].close()
            context.user_data['handler'] = None
        return E.ConversationHandler.END


    async def anime_info(self, update: T.Update, context: E.ContextTypes.DEFAULT_TYPE) -> int:
        url = update.message.text
        try:
            anime, already_in_database = await context.user_data['handler'].add_anime_by_url(url)

            debug_msg = '\n'.join(['{} = {}'.format(key, value) for key, value in anime.__dict__.items()])
            msg = textwrap.dedent(f'''
                {'<i>New!</i>' if not already_in_database else ''}
                
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

            return self.states['ANIME_INFO']
        except RuntimeError as e:
            await update.message.reply_text(text=e.args[0])
            return self.states['ANIME_INPUT']


    async def list_qitems(self, update: T.Update, context: E.ContextTypes.DEFAULT_TYPE) -> int:
        qitems = await context.user_data['handler'].list_qitems()

        # if no qitems, parse mal page and add them
        if len(qitems) == 0:
            qitems = await context.user_data['handler'].parse_and_add_qitems()

        if context.user_data.get('qitems_page') is None:
            context.user_data['qitems_page'] = 0
        
        total_pages = (len(qitems) - 1) // PAGE_LIMIT + 1
        anime_title = context.user_data["handler"].anime.title_ro
        
        if update.callback_query.data == 'prev':
            context.user_data['qitems_page'] = max(0, context.user_data['qitems_page'] - 1)
        elif update.callback_query.data == 'next':
            context.user_data['qitems_page'] = min(total_pages - 1, context.user_data['qitems_page'] + 1)
        
        page_idx = context.user_data.get('qitems_page')

        showed_qitems = qitems[page_idx * PAGE_LIMIT:(page_idx + 1) * PAGE_LIMIT]
        keyboard_markup = [
            [T.InlineKeyboardButton(
                f'{"OP" if qitem.item_type == 0 else "ED"} {qitem.num}',
                callback_data=str(qitem.num)
            )]
            for qitem in showed_qitems
        ]

        keyboard_markup.extend([
            [
                T.InlineKeyboardButton('< Previous page', callback_data='prev'),
                T.InlineKeyboardButton('Next page >', callback_data='next'),
            ],
            [T.InlineKeyboardButton('+ Add new +', callback_data='add')],
            [T.InlineKeyboardButton('Go back', callback_data='back')],
        ])

        await update.message.reply_text(
            text=f'Openings and endings for {anime_title}\nPage {page_idx + 1}/{total_pages}',
            reply_markup=T.InlineKeyboardMarkup(keyboard_markup),
        )

        return self.states['LIST_QITEMS']


    async def add_qitem(self, update: T.Update, context: E.ContextTypes.DEFAULT_TYPE) -> int:
        pass
    
    
    async def show_qitem(self, update: T.Update, context: E.ContextTypes.DEFAULT_TYPE) -> int:
        pass
    
    
    
    
