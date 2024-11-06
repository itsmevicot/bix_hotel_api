import logging
from datetime import date, datetime
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction

from bookings.enums import BookingStatus
from bookings.models import Booking
from bookings.repository import BookingRepository
from checkins.repository import CheckInCheckOutRepository
from rooms.enums import RoomStatus, RoomType
from rooms.repository import RoomRepository
from users.enums import UserRole
from users.models import User
from utils.email_service import EmailService
from utils.exceptions import RoomNotAvailableForSelectedDatesException, InvalidBookingModificationException, \
    UnauthorizedCancellationException, AlreadyCanceledException, \
    UnauthorizedOrInvalidBookingException

logger = logging.getLogger(__name__)


class BookingService:
    def __init__(
            self,
            booking_repository: Optional[BookingRepository] = None,
            room_repository: Optional[RoomRepository] = None,
            check_in_out_repository: Optional[CheckInCheckOutRepository] = None
    ):
        self.booking_repository = booking_repository or BookingRepository()
        self.room_repository = room_repository or RoomRepository()
        self.check_in_out_repository = check_in_out_repository or CheckInCheckOutRepository()

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
                raise RoomNotAvailableForSelectedDatesException()

            booking = self.booking_repository.create_booking(
                client=client,
                room=room,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                status=BookingStatus.PENDING.value
            )

            room.status = RoomStatus.BOOKED.value
            room.save()

            EmailService.send_booking_creation(client.email, {
                "room_number": room.number,
                "check_in_date": check_in_date,
                "check_out_date": check_out_date
            })
            return booking

        except RoomNotAvailableForSelectedDatesException as e:
            logger.error("Room not available for booking: %s", e)
            raise
        except Exception as e:
            logger.exception("Failed to create booking")
            raise e

    def modify_booking(
            self,
            booking_id: int,
            new_check_in_date: date,
            new_check_out_date: date,
            room_type: RoomType
    ) -> Booking:
        try:
            booking = self.booking_repository.get_booking_by_id(booking_id)

            if booking.status != BookingStatus.PENDING.value:
                raise InvalidBookingModificationException()

            original_room_number = booking.room.number
            original_check_in_date = booking.check_in_date
            original_check_out_date = booking.check_out_date
            original_room_price = booking.room.price

            if booking.room.room_type != room_type:
                new_room = self.room_repository.get_available_room(room_type=room_type)
                if not new_room:
                    raise RoomNotAvailableForSelectedDatesException()

                booking.room.status = RoomStatus.AVAILABLE.value
                booking.room.save()

                booking.room = new_room
                booking.room.status = RoomStatus.BOOKED.value
                booking.room.save()

            if not self.booking_repository.is_room_available_excluding_booking(
                    booking.room.id, new_check_in_date, new_check_out_date, exclude_booking_id=booking_id
            ):
                raise RoomNotAvailableForSelectedDatesException()

            booking.check_in_date = new_check_in_date
            booking.check_out_date = new_check_out_date
            booking.save()

            EmailService.send_booking_modification(
                booking.client.email,
                {
                    "room_number_before": original_room_number,
                    "check_in_date_before": original_check_in_date,
                    "check_out_date_before": original_check_out_date,
                    "room_price_before": original_room_price,
                    "room_number_after": booking.room.number,
                    "check_in_date_after": new_check_in_date,
                    "check_out_date_after": new_check_out_date,
                    "room_price_after": booking.room.price,
                }
            )
            return booking

        except RoomNotAvailableForSelectedDatesException:
            logger.error("Modification failed: room unavailable for new dates")
            raise
        except InvalidBookingModificationException:
            logger.error(f"Invalid modification: Booking {booking_id} status is not pending")
            raise
        except Exception as e:
            logger.exception(f"Failed to modify booking {booking_id}")
            raise e

    @transaction.atomic
    def confirm_booking(self, booking_id: int, user) -> Booking:
        try:
            booking = self.booking_repository.get_booking_by_id(booking_id)

            if booking.client != user:
                logger.error("User does not own this booking.")
                raise UnauthorizedOrInvalidBookingException()

            if booking.status != BookingStatus.PENDING.value:
                logger.error("Only pending bookings can be confirmed.")
                raise UnauthorizedOrInvalidBookingException()

            self.booking_repository.confirm_booking(booking)

            self.check_in_out_repository.create_check_in_out(booking)

            EmailService.send_booking_confirmation(booking.client.email, {
                "room_number": booking.room.number,
                "check_in_date": booking.check_in_date
            })

            logger.info(f"Booking {booking.id} confirmed and CheckInCheckOut created for client {booking.client.id}")
            return booking

        except UnauthorizedOrInvalidBookingException as e:
            logger.error(f"Cannot confirm booking: {e}")
            raise
        except Exception as e:
            logger.exception(f"Failed to confirm booking {booking_id}")
            raise e

    @transaction.atomic
    def cancel_booking(self, booking_id: int, user) -> Booking:
        try:
            booking = self.booking_repository.get_booking_by_id(booking_id)

            if booking.client != user and user.role != UserRole.ADMIN.value:
                logger.warning(f"User {user.id} attempted to cancel booking {booking_id} they do not own.")
                raise UnauthorizedCancellationException()

            if booking.status == BookingStatus.CANCELLED.value:
                logger.info(f"Booking {booking_id} is already canceled.")
                raise AlreadyCanceledException()

            self.booking_repository.cancel_booking(booking)

            EmailService.send_booking_cancellation(booking.client.email, {
                "room_number": booking.room.number,
                "check_in_date": booking.check_in_date
            })

            logger.info(f"Booking {booking.id} canceled for client {booking.client.id}")
            return booking

        except (UnauthorizedCancellationException, AlreadyCanceledException):
            raise
        except Exception as e:
            logger.exception(f"Failed to cancel booking {booking_id}")
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
                check_in_date = filters["check_in_date"]
                if isinstance(check_in_date, str):
                    try:
                        check_in_date = datetime.strptime(check_in_date, "%d/%m/%Y").date()
                    except ValueError:
                        raise ValidationError("Invalid check-in date format. Use dd/mm/yyyy.")
                filter_criteria["check_in_date__gte"] = check_in_date

            if filters.get("check_out_date"):
                check_out_date = filters["check_out_date"]
                if isinstance(check_out_date, str):
                    try:
                        check_out_date = datetime.strptime(check_out_date, "%d/%m/%Y").date()
                    except ValueError:
                        raise ValidationError("Invalid check-out date format. Use dd/mm/yyyy.")
                filter_criteria["check_out_date__lte"] = check_out_date

            if filters.get("status"):
                filter_criteria["status"] = filters["status"]
            if filters.get("room_type"):
                filter_criteria["room__room_type"] = filters["room_type"]

            if user.role in [UserRole.STAFF.value, UserRole.ADMIN.value] and filters.get("client_id"):
                filter_criteria["client_id"] = filters["client_id"]

            return self.booking_repository.get_filtered_bookings(filter_criteria)

        except Exception as e:
            logger.exception(f"Failed to retrieve filtered bookings with filters: {filters}")
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
