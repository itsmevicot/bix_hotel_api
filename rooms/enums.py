from enum import Enum


class RoomStatus(Enum):
    AVAILABLE = 'AVAILABLE'
    BOOKED = 'BOOKED'
    OCCUPIED = 'OCCUPIED'
    MAINTENANCE = 'MAINTENANCE'

    @classmethod
    def choices(cls):
        return [(key.value, key.name.capitalize()) for key in cls]


class RoomType(Enum):
    SINGLE = 'SINGLE'
    DOUBLE = 'DOUBLE'
    SUITE = 'SUITE'

    @classmethod
    def choices(cls):
        return [(key.value, key.name.capitalize()) for key in cls]
