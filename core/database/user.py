from __future__ import annotations
from typing import Iterator

from .role import Role
from .exceptions import *
from .tables.usertable import UserTable
from .tables.db import objects

from . import event


class User:
    model: UserTable

    def __init__(self, model: UserTable) -> None:
        self.model = model

    @property
    def id(self) -> int:
        return self.model.id

    @property
    def telegram_id(self) -> int:
        return self.model.telegram_id

    @property
    def first_name(self) -> str:
        return self.model.first_name

    @property
    def last_name(self) -> str:
        return self.model.last_name

    @property
    def middle_name(self) -> str:
        return self.model.middle_name

    @property
    def group(self) -> str:
        return self.group

    @property
    def role(self) -> Role:
        return Role(self.model.role)

    async def events(self) -> Iterator[event.Event]:
        return map(event.Event, await objects.execute(self.model.events))

    @staticmethod
    async def create(
        first_name: str,
        last_name: str,
        middle_name: str | None,
        group: str,
        telegram_id: int,
        role: Role = Role.DEFAULT,
    ) -> User:
        return User(
            await objects.create(
                UserTable,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                group=group,
                telegram_id=telegram_id,
                role=role.value,
            )
        )

    @staticmethod
    async def fetch(id: int) -> User:
        model = await objects.get_or_none(UserTable, id=id)
        if model is None:
            raise UserNotFound()
        return User(model)
