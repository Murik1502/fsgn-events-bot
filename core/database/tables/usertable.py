from peewee import *
from .db import BaseModel

class UserTable(BaseModel):
    telegram_id = BigIntegerField()
    first_name = CharField(50)
    last_name = CharField(50)
    middle_name = CharField(50, null=True)
    group = CharField(50)
    role = CharField(20)

    class Meta:
        table_name = 'users'
