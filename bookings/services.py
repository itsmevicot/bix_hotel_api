import logging
from datetime import datetime
from typing import Optional
from authentication.models import User
from bookings.enums import BookingStatus
from bookings.exceptions import RoomNotAvailableException
from bookings.models import Booking
from bookings.repository import BookingRepository
from rooms.models import Room, RoomStatus
from rooms.repository import RoomRepository

logger = logging.getLogger(__name__)


class BookingService:
    def __init__(
            self,
            booking_repository: Optional[BookingRepository] = None,
            room_repository: Optional[RoomRepository] = None
    ):
        self.booking_repository = booking_repository or BookingRepository()
        self.room_repository = room_repository or RoomRepository()

    def create(
            self,
            client: User,
            room: Room,
            check_in_date: datetime,
            check_out_date: datetime
    ) -> Booking:
        try:
            if room.status != RoomStatus.AVAILABLE.value:
                logger.error(f"Room {room.id} is not available for booking.")
                raise RoomNotAvailableException()

            booking = self.booking_repository.create_booking(
                client=client,
                room=room,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                status=BookingStatus.CONFIRMED.value
            )

            self.room_repository.set_status(
                room,
                RoomStatus.BOOKED.value
            )

            logger.info(f"Booking created successfully for client {client.id} in room {room.id}.")
            return booking

        except RoomNotAvailableException as e:
            logger.error(f"Failed to create booking for client {client.id}: {e}")
            raise

        except Exception as e:
            logger.error(f"An unexpected error occurred while creating a booking for client {client.id}: {e}")
            raise
