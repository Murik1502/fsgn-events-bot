from defaults.settings import settings
from peewee import Model
from peewee_async import PostgresqlDatabase, Manager


# Windows Fix
import sys, asyncio

if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

db = PostgresqlDatabase(
    database=settings.database.name,
    user=settings.database.user,
    password=settings.database.password,
    host=settings.database.host,
    port=settings.database.port,
)

objects = Manager(db)

db.set_allow_sync(False)

class BaseModel(Model):
    class Meta:
        database = db
