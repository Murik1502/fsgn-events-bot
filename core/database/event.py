from __future__ import annotations
from datetime import datetime

from .tables.eventtable import EventTable
from .tables.db import objects
from .eventtype import EventType
from .exceptions import *
from .role import Role

from . import user


class Event:
    model: EventTable

    def __init__(self, model: EventTable) -> None:
        self.model = model

    @property
    def id(self) -> int:
        return self.model.id

    @property
    def creator(self) -> user.User:
        return user.User(self.model.creator)

    @property
    def name(self) -> str:
        return self.model.name

    @property
    def description(self) -> str:
        return self.model.description

    @property
    def date(self) -> datetime:
        return self.model.date

    @property
    def type(self) -> EventType:
        return EventType(self.model.type)

    @staticmethod
    async def create(
        creator: int, name: str, description: str, date: datetime, type: EventType
    ) -> Event:
        if user.User.fetch(creator).role != Role.ADMIN:
            raise NotEnoughPermission()
        return Event(
            await objects.create(
                EventTable,
                creator=creator,
                name=name,
                description=description,
                date=date,
                type=type.value,
            )
        )

    @staticmethod
    async def fetch(id: int) -> Event:
        model = await objects.get_or_none(EventTable, id=id)
        if model is None:
            raise EventNotFound()
        return Event(model)
