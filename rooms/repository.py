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

    @staticmethod
    def get_all_rooms():
        return Room.objects.all()

    @staticmethod
    def create_room(
            number: str,
            status: RoomStatus,
            room_type: RoomType,
            price: float
    ) -> Room:
        return Room.objects.create(
            number=number,
            status=status,
            type=room_type,
            price=price
        )

    def update_room(
            self,
            room_id: int,
            **kwargs
    ) -> Room:
        room = self.get_room_by_id(room_id)
        for field, value in kwargs.items():
            setattr(room, field, value)
        room.save()
        return room

    @staticmethod
    def delete_room(
            room: Room
    ) -> None:
        room.delete()
