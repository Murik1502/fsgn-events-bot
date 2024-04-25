from peewee import *
from .db import BaseModel
from .usertable import UserTable

class EventTable(BaseModel):
    creator = ForeignKeyField(UserTable, backref='events')
    name = CharField(50)
    description = TextField()
    date = DateField()
    type = CharField(20)

    class Meta:
        table_name = 'events'
