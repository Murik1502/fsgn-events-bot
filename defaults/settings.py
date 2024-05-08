import os
from dataclasses import dataclass


@dataclass
class Bots:
    bot_token: str
    admin_id: int


@dataclass
class Database:
    name: str
    user: str
    password: str
    host: str
    port: int


@dataclass
class Settings:
    bots: Bots
#    database: Database


def get_settings():
    return Settings(
        bots=Bots(
            bot_token=os.getenv("BOT_TOKEN"),
            admin_id=int(os.getenv("ADMIN_ID")),
        ),
        # database=Database(
        #     name=os.getenv("POSTGRES_NAME"),
        #     user=os.getenv("POSTGRES_USER"),
        #     password=os.getenv("POSTGRES_PASSWORD"),
        #     host=os.getenv("POSTGRES_HOST"),
        #     port=int(os.getenv("POSTGRES_PORT")),
        # ),
    )

from cache.setenv import set_env
set_env()

settings = get_settings()
