from typing import Callable
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Scheduler():
    def __init__(self):
        self.sched = AsyncIOScheduler(timezone="Europe/Moscow")
    async def add_periodic(self, bot: Bot, func: Callable, interval: int=60):
        self.sched.add_job(func, trigger='interval', seconds=interval, kwargs={'bot': bot})

    async def add_pending(self, bot: Bot, func: Callable, date):
        self.sched.add_job(func, trigger='date', next_run_time=date, kwargs={'bot': bot})

scheduler = Scheduler()