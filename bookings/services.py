import logging
from datetime import date

from django.db import transaction

from bookings.enums import BookingStatus
from bookings.models import Booking
from bookings.repository import BookingRepository
from rooms.enums import RoomStatus, RoomType
from rooms.repository import RoomRepository
from users.enums import UserRole
from users.models import User
from utils.email_service import EmailService
from utils.exceptions import RoomNotAvailableException, InvalidBookingModificationException, \
    InvalidBookingConfirmationException

logger = logging.getLogger(__name__)


class BookingService:
    def __init__(
            self,
            booking_repository=None,
            room_repository=None
    ):
        self.booking_repository = booking_repository or BookingRepository()
        self.room_repository = room_repository or RoomRepository()

    def create_booking(
            self,
            client: User,
            check_in_date: date,
            check_out_date: date,
            room_type: RoomType = None
    ) -> Booking:
        room = self.room_repository.get_available_room(room_type=room_type)

        if not room:
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

        return booking

    def modify_booking(
            self,
            booking_id: int,
            new_check_in_date: date,
            new_check_out_date: date
    ) -> Booking:
        booking = self.booking_repository.get_booking_by_id(booking_id)

        if booking.status != BookingStatus.CONFIRMED.value:
            raise InvalidBookingModificationException()

        if not self.room_repository.is_room_available(
                booking.room.id, new_check_in_date, new_check_out_date
        ):
            raise RoomNotAvailableException()

        booking.check_in_date = new_check_in_date
        booking.check_out_date = new_check_out_date
        booking.save()

        EmailService.send_booking_modification(
            booking.client.email,
            {
                "room_number": booking.room.number,
                "new_check_in_date": new_check_in_date,
                "new_check_out_date": new_check_out_date
            }
        )

        return booking

    @transaction.atomic
    def confirm_booking(self, booking: Booking) -> Booking:
        if booking.status != BookingStatus.PENDING.value:
            logger.error("Only pending bookings can be confirmed.")
            raise InvalidBookingConfirmationException()

        booking.status = BookingStatus.CONFIRMED.value
        booking.save()

        EmailService.send_booking_confirmation(booking.client.email, {
            "room_number": booking.room.number,
            "check_in_date": booking.check_in_date
        })

        logger.info(f"Booking {booking.id} confirmed for client {booking.client.id}.")
        return booking

    @transaction.atomic
    def cancel_booking(
            self,
            booking: Booking
    ) -> Booking:
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

    def get_filtered_bookings(
            self,
            filters: dict,
            user: User
    ):
        """
        Retrieve bookings based on filters. Clients see only their bookings, while managers and admins see all.
        """
        filter_criteria = {}

        if user.role == UserRole.CLIENT.value:
            filter_criteria["client"] = user

        if filters.get("check_in_date"):
            filter_criteria["check_in_date__gte"] = filters["check_in_date"]
        if filters.get("check_out_date"):
            filter_criteria["check_out_date__lte"] = filters["check_out_date"]
        if filters.get("status"):
            filter_criteria["status"] = filters["status"]
        if filters.get("room_type"):
            filter_criteria["room__type"] = filters["room_type"]

        if user.role in [UserRole.MANAGER.value, UserRole.ADMIN.value] and filters.get("client_id"):
            filter_criteria["client_id"] = filters["client_id"]

        return self.booking_repository.get_filtered_bookings(filter_criteria)
