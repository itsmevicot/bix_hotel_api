from enum import Enum


class UserRole(Enum):
    CLIENT = 'CLIENT'
    STAFF = 'STAFF'
    ADMIN = 'ADMIN'

    @classmethod
    def choices(cls):
        return [(key.value, key.name.capitalize()) for key in cls]
