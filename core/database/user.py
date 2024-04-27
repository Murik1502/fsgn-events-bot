from __future__ import annotations
from typing import Iterator
from datetime import datetime

from .role import Role
from .exceptions import *
from .tables.usertable import UserTable
from .tables.eventtable import EventTable
from .tables.participanttable import ParticipantTable
from .tables.teamtable import TeamTable
from .eventtype import EventType
from .visit import Visit

from . import event
from . import participant
from . import team

class User:
    __id: int

    def __init__(self, id: int) -> None:
        self.__id = id

    @property
    def id(self) -> int:
        return self.__id

    @property
    def telegram_id(self) -> int:
        return UserTable.get_by_id(self.id).telegram_id

    @property
    def first_name(self) -> str:
        return UserTable.get_by_id(self.id).first_name

    @first_name.setter
    def first_name(self, first_name: str):
        self.__set_field(first_name=first_name)

    @property
    def last_name(self) -> str:
        return UserTable.get_by_id(self.id).last_name

    @last_name.setter
    def last_name(self, last_name: str):
        self.__set_field(last_name=last_name)

    @property
    def middle_name(self) -> str | None:
        return UserTable.get_by_id(self.id).middle_name

    @middle_name.setter
    def middle_name(self, middle_name: str | None):
        self.__set_field(middle_name=middle_name)

    @property
    def group(self) -> str:
        return UserTable.get_by_id(self.id).group

    @group.setter
    def group(self, group: str):
        self.__set_field(group=group)

    @property
    def role(self) -> Role:
        return Role(UserTable.get_by_id(self.id).role)

    @role.setter
    def role(self, role: Role):
        self.__set_field(role=role.value)

    def __set_field(self, **values):
        UserTable.update(**values).where(UserTable.id == self.id).execute()

    def events(self) -> Iterator[event.Event]:
        return map(lambda x: event.Event(x.id), UserTable.get_by_id(self.id).events)

    def participation(self) -> Iterator[participant.Participant]:
        return map(participant.Participant, UserTable.get_by_id(self.id).participation)

    def teams(self) -> Iterator[team.Team]:
        return map(lambda x: team.Team(x.id), UserTable.get_by_id(self.id).teams)

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
            ).id
        )

    @staticmethod
    def fetch(id: int) -> User:
        result = UserTable.get_or_none(id=id)
        if result is None:
            raise UserNotFound()
        return User(result.id)

    def create_event(
        self,
        name: str,
        description: str,
        date: datetime,
        type: EventType,
        google_sheet: str,
        photo_id: str,
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
                google_sheet=google_sheet,
                photo_id=photo_id,
            ).id
        )

    def create_team(self, event_id: int) -> tuple[team.Team, participant.Participant]:
        e = event.Event.fetch(event_id)
        if e.is_joined(self.id):
            raise UserAlreadyJoined()
        t = team.Team(
            team.TeamTable.create(
                leader=self.id, event=event_id, code=team.Team.generate_code()
            ).id
        )
        return t, self.join(event_id, team_code=t.code)

    def join(
        self,
        event_id: int,
        visit: Visit = Visit.UNDEFINED,
        team_code: str | None = None,
    ) -> participant.Participant:
        e = event.Event.fetch(event_id)
        if e.is_joined(self.id):
            raise UserAlreadyJoined()
        if e.type == EventType.TEAM and team_code is None:
            raise TeamIsRequired()
        team_id: int | None = None
        if e.type == EventType.TEAM:
            t = team.Team.fetch_by_code(team_code)
            if t.event.id != e.id:
                raise TeamAnotherEvent()
            team_id = t.id
        return participant.Participant(
            ParticipantTable.create(
                user=self.id,
                event=e.id,
                visit=visit.value,
                team=team_id,
            )
        )
