import betterlogging as logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import core.database.user
from core.handlers import basic, new_event, registration, admin
from bot import bot
from defaults.settings import settings
from core.utils.commands import set_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cache.apsched import periodic, sheet


async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(settings.bots.admin_id, text="Start")


async def stop_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, text="Stop")


def start_sched(bot: Bot):
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(periodic, trigger='interval', seconds=60, kwargs={'bot': bot})
    scheduler.add_job(sheet, trigger='interval', seconds=60, kwargs={'bot': bot})
    scheduler.start()


async def start():
    logging.basic_colorized_config(level=logging.DEBUG,
                                   format="%(astime)s - [%(levelname)s] - %(name)s - "
                                          "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")

    dp = Dispatcher(storage=MemoryStorage())
    start_sched(bot)
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    dp.include_routers(basic.router, admin.give_admin_router, new_event.admin_router, registration.reg_router,)

    try:
        await dp.start_polling(bot)
    except Exception as ex:
        logging.error(f"EXCEPTION: {ex}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
