from rooms.enums import RoomStatus, RoomType
from rooms.models import Room
from utils.exceptions import RoomNotAvailableException


class RoomRepository:
    @staticmethod
    def set_status(
            room: Room,
            status: RoomStatus
    ) -> None:
        room.status = status
        room.save()

    @staticmethod
    def get_room_by_id(
            room_id: int
    ) -> Room:
        room = Room.objects.get(id=room_id)

        if not room:
            raise Room.DoesNotExist

        return room

    @staticmethod
    def get_available_room(
            room_type: RoomType = None
    ) -> Room:
        room = Room.objects.filter(status=RoomStatus.AVAILABLE.value, type=room_type).first()

        if not room:
            raise RoomNotAvailableException()

        return room
