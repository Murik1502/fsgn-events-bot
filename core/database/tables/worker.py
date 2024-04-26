from .db import db
from .usertable import UserTable
from .eventtable import EventTable
from .teamtable import TeamTable
from .participanttable import ParticipantTable


def connect():
    db.connect()
    db.create_tables([UserTable, EventTable, TeamTable, ParticipantTable])


def disconnect():
    db.close()


connect()
