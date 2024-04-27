from defaults.settings import settings
from peewee import PostgresqlDatabase, Model
from playhouse.shortcuts import ReconnectMixin


class ReconnectDatabse(ReconnectMixin, PostgresqlDatabase):
    pass


db = ReconnectDatabse(
    database=settings.database.name,
    user=settings.database.user,
    password=settings.database.password,
    host=settings.database.host,
    port=settings.database.port,
)


class BaseModel(Model):
    class Meta:
        database = db
