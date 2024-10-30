from enum import Enum


class CheckInStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"

    @classmethod
    def choices(cls):
        return [(status.value, status.name.capitalize()) for status in cls]


class CheckOutStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"

    @classmethod
    def choices(cls):
        return [(status.value, status.name.capitalize()) for status in cls]
