from .db import db, objects
from .usertable import UserTable
from .eventtable import EventTable

async def connect():
    with objects.allow_sync():
        db.connect()
        db.create_tables([UserTable, EventTable])

async def disconnect():
    await objects.close()
    db.close()
