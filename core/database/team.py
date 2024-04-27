from __future__ import annotations
from typing import Iterator
import random, string

from .exceptions import *
from .tables.teamtable import TeamTable, CODE_LENGTH

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
        return user.User(TeamTable.get_by_id(self.id).leader.id)

    @property
    def event(self):
        return event.Event(TeamTable.get_by_id(self.id).event.id)

    def teammates(self) -> Iterator[participant.Participant]:
        return map(lambda x: participant.Participant(x.id), TeamTable.get_by_id(self.id).teammates)

    @property
    def code(self):
        return TeamTable.get_by_id(self.id).code

    @staticmethod
    def generate_code() -> str:
        code = None
        while code is None or TeamTable.get_or_none(code=code) is not None:
            code = "".join(
                random.choice(string.ascii_letters) for i in range(CODE_LENGTH)
            )
        return code

    @staticmethod
    def fetch(id: int) -> Team:
        model = TeamTable.get_or_none(id=id)
        if model is None:
            raise TeamNotFound()
        return Team(model)

    @staticmethod
    def fetch_by_code(code: str) -> Team:
        model = TeamTable.get_or_none(code=code)
        if model is None:
            raise TeamNotFound()
        return Team(model)
