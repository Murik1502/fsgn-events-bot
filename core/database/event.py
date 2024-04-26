from __future__ import annotations
from datetime import datetime
from typing import Iterator

from .tables.eventtable import EventTable
from .tables.participanttable import ParticipantTable
from .eventtype import EventType
from .exceptions import *

from . import user
from . import participant


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

    def participants(self) -> Iterator[participant.Participant]:
        return map(participant.Participant, self.table.participants)

    def is_joined(self, user_id: int) -> bool:
        return (
            len(
                ParticipantTable.select().where(
                    ParticipantTable.user == user_id, ParticipantTable.event == self.id
                )
            )
            > 0
        )
