import logging
from decimal import Decimal
from typing import Optional, List
from django.db import transaction

from rooms.enums import RoomStatus, RoomType
from rooms.models import Room
from rooms.repository import RoomRepository
from utils.exceptions import RoomNotFoundException, RoomNotAvailableException

logger = logging.getLogger(__name__)


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
    ) -> List[Room]:
        try:
            logger.info(f"Listing rooms with status={status} and room_type={room_type}")
            queryset = self.room_repository.get_all_rooms()
            if status:
                queryset = queryset.filter(status=status)
            if room_type:
                queryset = queryset.filter(type=room_type)
            logger.info(f"Listed {queryset.count()} rooms")
            return list(queryset)
        except Exception as e:
            logger.error(f"Error listing rooms: {e}")
            raise

    def get_room(
            self,
            room_id: int
    ) -> Room:
        try:
            logger.info(f"Getting room with ID={room_id}")
            room = self.room_repository.get_room_by_id(room_id)
            if not room:
                raise RoomNotFoundException()
            logger.info(f"Retrieved room with ID={room_id}")
            return room
        except RoomNotFoundException as e:
            logger.error(f"Room not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving room: {e}")
            raise

    @transaction.atomic
    def create_room(
            self,
            number: str,
            status: RoomStatus,
            room_type: RoomType,
            price: float
    ) -> Room:
        try:
            logger.info(f"Creating room with number={number}, status={status}, type={room_type}, price={price}")
            room = self.room_repository.create_room(
                number,
                status,
                room_type,
                price
            )
            logger.info(f"Created room with ID={room.id}")
            return room
        except Exception as e:
            logger.error(f"Error creating room: {e}")
            raise

    @transaction.atomic
    def update_room(
            self,
            room_id: int,
            **kwargs
    ) -> Room:
        try:
            if "price" in kwargs:
                if isinstance(kwargs["price"], list):
                    kwargs["price"] = Decimal(kwargs["price"][0])
                elif isinstance(kwargs["price"], str):
                    kwargs["price"] = Decimal(kwargs["price"])

            logger.info(f"Updating room with ID={room_id} with data={kwargs}")
            room = self.room_repository.update_room(room_id, **kwargs)
            logger.info(f"Room updated successfully with ID={room_id}")
            return room
        except RoomNotFoundException as e:
            logger.error(f"Room not found for update: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating room: {e}")
            raise

    @transaction.atomic
    def delete_room(
            self,
            room_id: int
    ) -> None:
        try:
            logger.info(f"Deleting room with ID={room_id}")
            room = self.get_room(room_id)
            self.room_repository.delete_room(room)
            logger.info(f"Deleted room with ID={room_id}")
        except RoomNotFoundException as e:
            logger.error(f"Room not found for deletion: {e}")
            raise
        except Exception as e:
            logger.error(f"Error deleting room: {e}")
            raise

    def check_availability(
            self,
            room_id: int
    ) -> bool:
        try:
            logger.info(f"Checking availability for room with ID={room_id}")
            room = self.get_room(room_id)
            if room.status != RoomStatus.AVAILABLE.value:
                raise RoomNotAvailableException()
            logger.info(f"Room with ID={room_id} is available")
            return True
        except RoomNotAvailableException as e:
            logger.warning(f"Room not available: {e}")
            raise
        except Exception as e:
            logger.error(f"Error checking room availability: {e}")
            raise
