import asyncio

from aiogram.utils import executor

from keyboard import *


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
