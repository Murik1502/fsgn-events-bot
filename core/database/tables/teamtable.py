from peewee import *
from .db import BaseModel
from .usertable import UserTable
from .eventtable import EventTable


class TeamTable(BaseModel):
    leader = ForeignKeyField(UserTable, backref="teams")
    event = ForeignKeyField(EventTable, backref="teams")

    class Meta:
        table_name = "teams"
