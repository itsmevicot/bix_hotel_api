from enum import Enum


class BookingStatus(Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"

    @classmethod
    def choices(cls):
        return [(status.value, status.name.capitalize()) for status in cls]
