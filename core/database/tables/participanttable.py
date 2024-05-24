from peewee import *
from .db import BaseModel
from .usertable import UserTable
from .eventtable import EventTable
from .teamtable import TeamTable


class ParticipantTable(BaseModel):
    user = ForeignKeyField(UserTable, backref="participation", on_delete="CASCADE")
    event = ForeignKeyField(EventTable, backref="participants", on_delete='CASCADE')
    team = ForeignKeyField(TeamTable, backref="teammates", null=True, on_delete="CASCADE")
    telegram_tag = CharField(50)
    visit = IntegerField()

    class Meta:
        table_name = "participants"
