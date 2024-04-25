from defaults.settings import settings
from peewee import PostgresqlDatabase, Model

db = PostgresqlDatabase(
    database=settings.database.name,
    user=settings.database.user,
    password=settings.database.password,
    host=settings.database.host,
    port=settings.database.port,
)

class BaseModel(Model):
    class Meta:
        database = db
