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

    @staticmethod
    def is_room_available(
            room: Room
    ) -> bool:
        return room.status == RoomStatus.AVAILABLE.value

    @staticmethod
    def get_room_by_id(
            room_id: int
    ) -> Room:
        return Room.objects.get(id=room_id)

    @staticmethod
    def get_available_room() -> Room:
        return Room.objects.filter(status=RoomStatus.AVAILABLE.value).first()
