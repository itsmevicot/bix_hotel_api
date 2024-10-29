from rooms.enums import RoomStatus
from rooms.models import Room


class RoomRepository:
    @staticmethod
    def set_status(
            room: Room,
            status: RoomStatus
    ) -> None:
        room.status = status
        room.save()
