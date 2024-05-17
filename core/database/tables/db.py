from typing import Any, Optional
from defaults.settings import settings
from peewee import PostgresqlDatabase, Model


class ReconnectDatabase(PostgresqlDatabase):
    def execute_sql(self, sql, params: Optional[Any] = ..., commit=...):
        try:
            cur = self.connection().cursor()
            cur.execute('SELECT 1')
        except:
            if self.connection().closed > 0:
                self.close()
                self.connect()
        return super().execute_sql(sql, params, commit)


db = ReconnectDatabase(
    database=settings.database.name,
    user=settings.database.user,
    password=settings.database.password,
    host=settings.database.host,
    port=settings.database.port,
)


class BaseModel(Model):
    class Meta:
        database = db
