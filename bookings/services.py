import logging
from datetime import date

from django.db import transaction

from bookings.enums import BookingStatus
from bookings.models import Booking
from bookings.repository import BookingRepository
from rooms.enums import RoomStatus
from rooms.repository import RoomRepository
from users.models import User
from utils.email_service import EmailService
from utils.exceptions import RoomNotAvailableException

logger = logging.getLogger(__name__)


class BookingService:
    def __init__(
            self,
            booking_repository=None,
            room_repository=None
    ):
        self.booking_repository = booking_repository or BookingRepository()
        self.room_repository = room_repository or RoomRepository()

    @transaction.atomic
    def create_booking(self, client: User, check_in_date: date, check_out_date: date) -> Booking:
        room = self.room_repository.get_available_room()
        if not room:
            logger.error("No available rooms found.")
            raise RoomNotAvailableException()

        booking = self.booking_repository.create_booking(
            client=client,
            room=room,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            status=BookingStatus.PENDING.value
        )

        EmailService.send_booking_creation(client.email, {
            "room_number": room.number,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date
        })

        logger.info(f"Booking created for client {client.id} with room {room.id}.")
        return booking

    @transaction.atomic
    def confirm_booking(self, booking: Booking) -> Booking:
        if booking.status != BookingStatus.PENDING.value:
            logger.error("Only pending bookings can be confirmed.")
            raise ValueError("Booking cannot be confirmed.")

        booking.status = BookingStatus.CONFIRMED.value
        booking.save()

        EmailService.send_booking_confirmation(booking.client.email, {
            "room_number": booking.room.number,
            "check_in_date": booking.check_in_date
        })

        logger.info(f"Booking {booking.id} confirmed for client {booking.client.id}.")
        return booking

    @transaction.atomic
    def cancel_booking(self, booking: Booking) -> Booking:
        booking.status = BookingStatus.CANCELLED.value
        booking.room.status = RoomStatus.AVAILABLE.value
        booking.room.save()
        booking.save()

        EmailService.send_booking_cancellation(booking.client.email, {
            "room_number": booking.room.number,
            "check_in_date": booking.check_in_date
        })

        logger.info(f"Booking {booking.id} canceled for client {booking.client.id}.")
        return booking
