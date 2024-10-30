from typing import Optional

from rooms.enums import RoomStatus, RoomType
from rooms.repository import RoomRepository
from utils.exceptions import RoomNotFoundException, RoomNotAvailableException


class RoomService:

    def __init__(
            self,
            room_repository: Optional[RoomRepository] = None,
    ):
        self.room_repository = room_repository or RoomRepository()

    def list_rooms(
            self,
            status: Optional[RoomStatus] = None,
            room_type: Optional[RoomType] = None
    ):
        queryset = self.room_repository.get_all_rooms()
        if status:
            queryset = queryset.filter(status=status)
        if room_type:
            queryset = queryset.filter(type=room_type)
        return queryset

    def get_room(self, room_id: int):
        room = self.room_repository.get_room_by_id(room_id)
        if not room:
            raise RoomNotFoundException()
        return room

    def create_room(self, number: str, status: str, room_type: str, price: float):
        return self.room_repository.create_room(number, status, room_type, price)

    def update_room(self, room_id: int, **kwargs):
        room = self.get_room(room_id)
        return self.room_repository.update_room(room, **kwargs)

    def delete_room(self, room_id: int):
        room = self.get_room(room_id)
        self.room_repository.delete_room(room)

    def check_availability(self, room_id: int) -> bool:
        room = self.get_room(room_id)
        if room.status != RoomStatus.AVAILABLE.value:
            raise RoomNotAvailableException()
        return True
