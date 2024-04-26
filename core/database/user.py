from __future__ import annotations
from typing import Iterator
from datetime import datetime

from .role import Role
from .exceptions import *
from .tables.usertable import UserTable
from .tables.eventtable import EventTable
from .tables.participanttable import ParticipantTable
from .eventtype import EventType
from .visit import Visit

from . import event
from . import participant


class User:
    table: UserTable

    def __init__(self, table: UserTable) -> None:
        self.table = table

    @property
    def id(self) -> int:
        return self.table.id

    @property
    def telegram_id(self) -> int:
        return self.table.telegram_id

    @property
    def first_name(self) -> str:
        return self.table.first_name

    @property
    def last_name(self) -> str:
        return self.table.last_name

    @property
    def middle_name(self) -> str:
        return self.table.middle_name

    @property
    def group(self) -> str:
        return self.table.group

    @property
    def role(self) -> Role:
        return Role(self.table.role)

    def events(self) -> Iterator[event.Event]:
        return map(event.Event, self.table.events)

    def participation(self) -> Iterator[participant.Participant]:
        return map(participant.Participant, self.table.participation)

    @staticmethod
    def create(
        first_name: str,
        last_name: str,
        middle_name: str | None,
        group: str,
        telegram_id: int,
        role: Role = Role.DEFAULT,
    ) -> User:
        return User(
            UserTable.create(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                group=group,
                telegram_id=telegram_id,
                role=role.value,
            )
        )

    @staticmethod
    def fetch(id: int) -> User:
        model = UserTable.select().where(UserTable.id == id).first()
        if model is None:
            raise UserNotFound()
        return User(model)

    def create_event(
        self, name: str, description: str, date: datetime, type: EventType
    ) -> event.Event:
        if User.fetch(self.id).role != Role.ADMIN:
            raise NotEnoughPermission()
        return event.Event(
            EventTable.create(
                creator=self.id,
                name=name,
                description=description,
                date=date,
                type=type.value,
            )
        )

    def join(
        self, event_id: int, visit: Visit = Visit.UNDEFINED
    ) -> participant.Participant:
        e = event.Event.fetch(event_id)
        if e.is_joined(self.id):
            raise UserAlreadyJoined()
        return participant.Participant(
            ParticipantTable.create(
                user=self.id,
                event=e.id,
                visit=visit.value,
            )
        )
