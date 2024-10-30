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
        try:
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

        except RoomNotAvailableException as e:
            logger.error("Room not available for booking: %s", e)
            raise
        except Exception as e:
            logger.exception("Failed to create booking")
            raise e

    def modify_booking(
            self,
            booking_id: int,
            new_check_in_date: date,
            new_check_out_date: date
    ) -> Booking:
        try:
            booking = self.booking_repository.get_booking_by_id(booking_id)

            if booking.status != BookingStatus.CONFIRMED.value:
                raise InvalidBookingModificationException()

            if not self.booking_repository.is_room_available(
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

        except RoomNotAvailableException as e:
            logger.error("Modification failed: room unavailable for new dates")
            raise
        except InvalidBookingModificationException as e:
            logger.error("Invalid modification: Booking %s status is not confirmed", booking_id)
            raise
        except Exception as e:
            logger.exception("Failed to modify booking %s", booking_id)
            raise e

    @transaction.atomic
    def confirm_booking(self, booking: Booking) -> Booking:
        try:
            if booking.status != BookingStatus.PENDING.value:
                logger.error("Only pending bookings can be confirmed.")
                raise InvalidBookingConfirmationException()

            booking.status = BookingStatus.CONFIRMED.value
            booking.save()

            EmailService.send_booking_confirmation(booking.client.email, {
                "room_number": booking.room.number,
                "check_in_date": booking.check_in_date
            })

            logger.info("Booking %s confirmed for client %s", booking.id, booking.client.id)
            return booking

        except InvalidBookingConfirmationException as e:
            logger.error("Cannot confirm booking: %s", e)
            raise
        except Exception as e:
            logger.exception("Failed to confirm booking %s", booking.id)
            raise e

    @transaction.atomic
    def cancel_booking(
            self,
            booking: Booking
    ) -> Booking:
        try:
            booking.status = BookingStatus.CANCELLED.value
            booking.room.status = RoomStatus.AVAILABLE.value
            booking.room.save()
            booking.save()

            EmailService.send_booking_cancellation(booking.client.email, {
                "room_number": booking.room.number,
                "check_in_date": booking.check_in_date
            })

            logger.info("Booking %s canceled for client %s", booking.id, booking.client.id)
            return booking

        except Exception as e:
            logger.exception("Failed to cancel booking %s", booking.id)
            raise e

    def get_filtered_bookings(
            self,
            filters: dict,
            user: User
    ):
        """
        Retrieve bookings based on filters. Clients see only their bookings, while managers and admins see all.
        """
        try:
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

            if user.role in [UserRole.STAFF.value, UserRole.ADMIN.value] and filters.get("client_id"):
                filter_criteria["client_id"] = filters["client_id"]

            return self.booking_repository.get_filtered_bookings(filter_criteria)

        except Exception as e:
            logger.exception("Failed to retrieve filtered bookings with filters: %s", filters)
            raise e

    def get_booking_by_id(
            self,
            booking_id: int,
            user: User
    ) -> Booking:
        """
        Retrieves a single booking by ID, allowing clients to view only their own bookings,
        while managers and admins can access all bookings.
        """
        try:
            booking = self.booking_repository.get_booking_by_id(booking_id)

            if user.role == UserRole.CLIENT.value and booking.client != user:
                raise PermissionError("You do not have permission to access this booking.")

            return booking

        except PermissionError as e:
            logger.error("Unauthorized access to booking %s by user %s", booking_id, user.id)
            raise e
        except Exception as e:
            logger.exception("Failed to retrieve booking by ID %s", booking_id)
            raise e
