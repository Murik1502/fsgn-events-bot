import betterlogging as logging
import asyncio
from aiogram import Bot, Dispatcher
from defaults.settings import settings
from core.utils.commands import set_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cache.apsched import periodic


async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(settings.bots.admin_id, text="Start")


async def stop_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, text="Stop")


def start_sched(bot: Bot):
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(periodic, trigger='interval', seconds=60, kwargs={'bot': bot})
    scheduler.start()


async def start():
    logging.basic_colorized_config(level=logging.DEBUG,
                                   format="%(astime)s - [%(levelname)s] - %(name)s - "
                                          "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")

    bot = Bot(token=settings.bots.bot_token)
    dp = Dispatcher()
    start_sched(bot)
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    try:
        await dp.start_polling(bot)
    except Exception as ex:
        logging.error(f"EXCEPTION: {ex}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
