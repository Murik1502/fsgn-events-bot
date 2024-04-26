from __future__ import annotations
from typing import Iterator

from .exceptions import *
from .tables.teamtable import TeamTable

from . import user
from . import event
from . import participant


class Team:
    __id: int

    def __init__(self, id: int) -> None:
        self.__id = id

    @property
    def id(self):
        return self.__id

    @property
    def leader(self):
        return user.User(TeamTable.get_by_id(self.id).leader)

    @property
    def event(self):
        return event.Event(TeamTable.get_by_id(self.id).event)

    def teammates(self) -> Iterator[participant.Participant]:
        return map(participant.Participant, TeamTable.get_by_id(self.id).teammates)

    @staticmethod
    def fetch(id: int) -> Team:
        model = TeamTable.get_or_none(id=id)
        if model is None:
            raise TeamNotFound()
        return Team(model)
