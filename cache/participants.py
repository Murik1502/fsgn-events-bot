from typing import Dict, List

# Минимальное количество новых участников для обновления
update_limit = 5
class MapPartisipants:

    """
    Класс для храненя зарегестрированных с момента последнего обновления участников

    используется для проверки количества новых учатников перед их внесением в БД

    атрибут dict: словарь, ключи - id мероприятий, значения - списки из id участников

    методы:
        getEvents - получить список мероприятий
        getPartisipants - получить список всех участников мероприятия по его id или всех участников по умолчанию
        addPartisipant - добавить нового участника
        addEvent - добавить новое мероприятие
        getCount - получить количество участников по id мероприятия или всех участников по умолчанию
        clear - зачистить список для мероприятия по его id или весь словарь по умолчанию

    Внимание!
    Для работы с конкретным мероприятием:
        Добавлять пользователя при регестрации хендлера     partisipants.addPartisipant(user_id=user_info.id, event_id=event_id)
        Проверять на количество новых участников перед обновлением     if partisipants.getCount(event_id=event_id) > n
        После обновления очистить список    partisipants.clear(event_id=event_id)

        В случае удаления мероприятия или остановки регистрации на очистить аналогично
    """
    def __init__(self):
        self.dict = Dict[int, List[int]]
        self.dict = {}

    def getEvents(self) -> List[int]:
        return list(self.dict.keys())

    def getPartisipants(self, event_id: int=None) -> List[int]:
        if event_id is None:
            return list(self.dict.values())
        elif event_id in self.dict.keys():
            return self.dict[event_id]

    def addPartisipant(self, user_id: int, event_id: int) -> None:
        self.addEvent(event_id=event_id)
        if not user_id in self.dict[event_id]:
            self.dict[event_id].append(user_id)

    def addEvent(self, event_id: int) -> None:
        if event_id not in self.dict.keys():
            self.dict[event_id] = []

    def getCount(self, event_id: int=None) -> int:
        return len(self.getPartisipants(event_id=event_id))

    def clear(self, event_id: int=None) -> None:
        if event_id is None:
            self.dict.clear()
        elif event_id in self.dict.keys():
            self.dict.pop(event_id)

partisipants = MapPartisipants()
