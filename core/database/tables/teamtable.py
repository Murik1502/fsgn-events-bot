from peewee import *
from .db import BaseModel
from .usertable import UserTable
from .eventtable import EventTable

CODE_LENGTH = 8


class TeamTable(BaseModel):
    leader = ForeignKeyField(UserTable, backref="teams", on_delete="CASCADE")
    event = ForeignKeyField(EventTable, backref="teams", on_delete="CASCADE")
    code = CharField(CODE_LENGTH)

    class Meta:
        table_name = "teams"
