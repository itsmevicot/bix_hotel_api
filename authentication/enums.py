from enum import Enum


class UserRole(Enum):
    CLIENT = 'CLIENT'
    STAFF = 'STAFF'
    MANAGER = 'MANAGER'
    ADMIN = 'ADMIN'

    @classmethod
    def choices(cls):
        return [(key.value, key.name.capitalize()) for key in cls]
