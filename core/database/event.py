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
    __id: int

    def __init__(self, id: int) -> None:
        self.__id = id

    @property
    def id(self) -> int:
        return self.__id

    @property
    def creator(self) -> user.User:
        return user.User(EventTable.get_by_id(self.id).creator.id)

    @property
    def name(self) -> str:
        return EventTable.get_by_id(self.id).name

    @name.setter
    def name(self, name: str):
        self.__set_field(name=name)

    @property
    def description(self) -> str:
        return EventTable.get_by_id(self.id).description

    @description.setter
    def description(self, description: str):
        self.__set_field(description=description)

    @property
    def date(self) -> datetime:
        return EventTable.get_by_id(self.id).date

    @date.setter
    def date(self, date: datetime):
        self.__set_field(date=date)

    @property
    def type(self) -> EventType:
        return EventType(EventTable.get_by_id(self.id).type)

    @type.setter
    def type(self, type: EventType):
        self.__set_field(type=type.value)

    @property
    def photo_id(self) -> str:
        return EventTable.get_by_id(self.id).photo_id

    @photo_id.setter
    def photo_id(self, value: str):
        self.__set_field(photo_id=value)

    @property
    def google_sheet(self) -> str:
        return EventTable.get_by_id(self.id).google_sheet

    @google_sheet.setter
    def google_sheet(self, value: str):
        self.__set_field(google_sheet=value)

    def __set_field(self, **values):
        EventTable.update(**values).where(EventTable.id == self.id).execute()

    def teams(self) -> Iterator[team.Team]:
        return map(lambda x: team.Team(x.id), EventTable.get_by_id(self.id).teams)

    @staticmethod
    def fetch(id: int) -> Event:
        model = EventTable.get_or_none(id=id)
        if model is None:
            raise EventNotFound()
        return Event(model)

    def participants(self) -> Iterator[participant.Participant]:
        return map(participant.Participant, EventTable.get_by_id(self.id).participants)

    def is_joined(self, user_id: int) -> bool:
        return (
            len(
                ParticipantTable.select().where(
                    ParticipantTable.user == user_id, ParticipantTable.event == self.id
                )
            )
            > 0
        )
