from peewee import *
from .db import BaseModel
from .usertable import UserTable


class EventTable(BaseModel):
    creator = ForeignKeyField(UserTable, backref="events", on_delete="CASCADE")
    name = CharField(50)
    description = TextField()
    photo_id = TextField()
    google_sheet = TextField()
    date = DateTimeField()
    type = CharField(20)

    class Meta:
        table_name = "events"
