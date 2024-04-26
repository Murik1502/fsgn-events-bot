from __future__ import annotations
from datetime import datetime

from .tables.eventtable import EventTable
from .eventtype import EventType
from .exceptions import *
from .role import Role

from . import user


class Event:
    table: EventTable

    def __init__(self, table: EventTable) -> None:
        self.table = table

    @property
    def id(self) -> int:
        return self.table.id

    @property
    def creator(self) -> user.User:
        return user.User(self.table.creator)

    @property
    def name(self) -> str:
        return self.table.name

    @property
    def description(self) -> str:
        return self.table.description

    @property
    def date(self) -> datetime:
        return self.table.date

    @property
    def type(self) -> EventType:
        return EventType(self.table.type)

    @staticmethod
    def fetch(id: int) -> Event:
        model = EventTable.select().where(EventTable.id == id).first()
        if model is None:
            raise EventNotFound()
        return Event(model)
