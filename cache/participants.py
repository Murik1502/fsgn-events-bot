from typing import Dict, List

class Partisipants:

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

partisipants = Partisipants()