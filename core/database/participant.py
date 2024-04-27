from __future__ import annotations

from .exceptions import *
from .tables.participanttable import ParticipantTable
from .visit import Visit

from . import user
from . import event
from . import team


class Participant:
    __id: int

    def __init__(self, id: int) -> None:
        self.__id = id

    @property
    def id(self) -> int:
        return self.__id

    @property
    def user(self) -> user.User:
        return user.User(ParticipantTable.get_by_id(self.id).user.id)

    @property
    def event(self) -> event.Event:
        return event.Event(ParticipantTable.get_by_id(self.id).event.id)

    @property
    def visit(self) -> Visit:
        return Visit(ParticipantTable.get_by_id(self.id).visit)

    @property
    def team(self) -> team.Team:
        result = ParticipantTable.get_by_id(self.id)
        if result.team is None:
            return None
        return team.Team(result.team.id)

    @visit.setter
    def visit(self, visit: Visit):
        ParticipantTable.update(visit=visit.value).where(
            ParticipantTable.id == self.id
        ).execute()

    @staticmethod
    def fetch(id: int) -> Participant:
        model = ParticipantTable.get_or_none(id=id)
        if model is None:
            raise UserNotFound()
        return Participant(model.id)
