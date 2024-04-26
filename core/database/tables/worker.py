from .db import db
from .usertable import UserTable
from .eventtable import EventTable

def connect():
    db.connect()
    db.create_tables([UserTable, EventTable])

def disconnect():
    db.close()
