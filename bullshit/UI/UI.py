from enum import Enum

class User:
    class Role(Enum):
        ADMIN = 0
        SUPERVISOR = 1
        MASTER = 2

    def __init__(self, name: str, role: Role, id: int):
        self._name = name
        self._role = role
        self._id = id

    @property
    def name(self):
        return self._name

    @property
    def role(self):
        return self._role

    @property
    def id(self):
        return self._id
