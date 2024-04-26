from .db import db
from .usertable import UserTable
from .eventtable import EventTable
from .participanttable import ParticipantTable


def connect():
    db.connect()
    db.create_tables([UserTable, EventTable, ParticipantTable])


def disconnect():
    db.close()


connect()
