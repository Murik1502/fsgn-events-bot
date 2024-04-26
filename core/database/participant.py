from __future__ import annotations

from .exceptions import *
from .tables.participanttable import ParticipantTable
from .visit import Visit

from . import user
from . import event


class Participant:
    table: ParticipantTable

    def __init__(self, table: ParticipantTable) -> None:
        self.table = table

    @property
    def id(self) -> int:
        return self.table.id

    @property
    def user(self) -> user.User:
        return user.User(self.table.user)

    @property
    def event(self) -> event.Event:
        return event.Event(self.table.event)

    @property
    def visit(self) -> Visit:
        return Visit(self.table.visit)

    @staticmethod
    def fetch(id: int) -> Participant:
        model = ParticipantTable.select().where(ParticipantTable.id == id).first()
        if model is None:
            raise UserNotFound()
        return Participant(model)
