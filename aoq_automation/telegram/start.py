from .logic import bot, dp


async def start() -> None:
    await dp.start_polling(bot)
