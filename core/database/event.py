from __future__ import annotations
from datetime import datetime
from typing import Iterator

from .tables.eventtable import EventTable
from .tables.participanttable import ParticipantTable
from .eventtype import EventType
from .exceptions import *

from . import user
from . import participant
from . import team


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

    @name.setter
    def name(self, name: str):
        self.__set_field(name=name)

    @property
    def description(self) -> str:
        return self.table.description

    @description.setter
    def description(self, description: str):
        self.__set_field(description=description)

    @property
    def date(self) -> datetime:
        return self.table.date

    @date.setter
    def date(self, date: datetime):
        self.__set_field(date=date)

    @property
    def type(self) -> EventType:
        return EventType(self.table.type)

    @type.setter
    def type(self, type: EventType):
        self.__set_field(type=type.value)

    @property
    def photo_id(self) -> str:
        return self.table.photo_id

    @photo_id.setter
    def photo_id(self, value: str):
        self.__set_field(photo_id=value)

    @property
    def google_sheet(self) -> str:
        return self.table.google_sheet

    @google_sheet.setter
    def google_sheet(self, value: str):
        self.__set_field(google_sheet=value)

    def __set_field(self, **values):
        id = self.id
        EventTable.update(**values).where(EventTable.id == id).execute()
        self.table = EventTable.get_by_id(id)

    def teams(self) -> Iterator[team.Team]:
        return map(lambda x: team.Team(x.id), self.table.teams)

    @staticmethod
    def fetch(id: int) -> Event:
        model = EventTable.select().where(EventTable.id == id).first()
        if model is None:
            raise EventNotFound()
        return Event(model)

    @staticmethod
    def fetch_all() -> list[Event]:
        events = []
        models = EventTable.select()
        if not models:
            raise EventNotFound()
        for model in models:
            events.append(Event(model))
        return events

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
