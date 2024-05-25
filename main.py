import betterlogging as logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from core.handlers import basic, new_event, registration, admin, excel
from bot import bot
from defaults.settings import settings
from core.utils.commands import set_commands
from cache.apsched import scheduler, sheet


async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(settings.bots.admin_id, text="Start")


async def stop_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, text="Stop")


async def start():
    logging.basic_colorized_config(level=logging.DEBUG,
                                   format="%(astime)s - [%(levelname)s] - %(name)s - "
                                          "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")

    dp = Dispatcher(storage=MemoryStorage())

    scheduler.sched.start()
    await scheduler.add_periodic(bot, func=sheet, interval=60)
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    dp.include_routers(basic.router, admin.give_admin_router, new_event.admin_router, registration.reg_router, excel.exel_router, )

    try:
        await dp.start_polling(bot)
    except Exception as ex:
        logging.error(f"EXCEPTION: {ex}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
