from peewee import *
from .db import BaseModel
from .usertable import UserTable
from .eventtable import EventTable


class ParticipantTable(BaseModel):
    user = ForeignKeyField(UserTable, backref="participation")
    event = ForeignKeyField(EventTable, backref="participants")
    visit = IntegerField()


    class Meta:
        table_name = "participants"
