from __future__ import annotations
from typing import Iterator
from datetime import datetime

from .role import Role
from .exceptions import *
from .tables.usertable import UserTable
from .tables.eventtable import EventTable
from .eventtype import EventType

from . import event


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
        return self.group

    @property
    def role(self) -> Role:
        return Role(self.table.role)

    def events(self) -> Iterator[event.Event]:
        return map(event.Event, self.table.events)

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
        self, creator: int, name: str, description: str, date: datetime, type: EventType
    ) -> event.Event:
        if User.fetch(creator).role != Role.ADMIN:
            raise NotEnoughPermission()
        return event.Event(
            EventTable.create(
                creator=creator,
                name=name,
                description=description,
                date=date,
                type=type.value,
            )
        )
