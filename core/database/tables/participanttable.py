from peewee import *
from .db import BaseModel
from .usertable import UserTable
from .eventtable import EventTable
from .teamtable import TeamTable

class ParticipantTable(BaseModel):
    user = ForeignKeyField(UserTable, backref="participation")
    event = ForeignKeyField(EventTable, backref="participants")
    team = ForeignKeyField(TeamTable, backref="teammates", null=True)
    visit = IntegerField()

    class Meta:
        table_name = "participants"
