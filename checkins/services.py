import logging
from typing import Optional

from django.db import transaction
from django.utils import timezone

from bookings.enums import BookingStatus
from bookings.repository import BookingRepository
from checkins.enums import CheckInStatus, CheckOutStatus
from checkins.repository import CheckInCheckOutRepository
from utils.email_service import EmailService
from utils.exceptions import AlreadyCheckedOutException, InvalidBookingStatusException, AlreadyCheckedInException

logger = logging.getLogger(__name__)


class CheckInCheckOutService:

    def __init__(
            self,
            check_in_out_repository: Optional[CheckInCheckOutRepository] = None,
            booking_repository: Optional[BookingRepository] = None
    ) -> None:
        self.check_in_out_repository = check_in_out_repository or CheckInCheckOutRepository()
        self.booking_repository = booking_repository or BookingRepository()

    @transaction.atomic
    def perform_check_in(
            self,
            booking_id: int
    ) -> CheckInStatus:
        try:
            booking = self.booking_repository.get_booking_by_id(booking_id)
            check_in_out = self.check_in_out_repository.get_by_booking(booking)

            if booking.status != BookingStatus.CONFIRMED.value:
                logger.warning(f"Attempted check-in on booking {booking_id} with status {booking.status}.")
                raise InvalidBookingStatusException()

            if check_in_out.check_in_status == CheckInStatus.COMPLETED.value:
                logger.warning(f"Attempted check-in on booking {booking_id} that is already checked in.")
                raise AlreadyCheckedInException()

            check_in_out.check_in_status = CheckInStatus.COMPLETED.value
            check_in_out.check_in_timestamp = timezone.now()
            check_in_out.save()

            EmailService.send_checkin(
                booking.client.email,
                {
                    "room_number": booking.room.number,
                    "check_in_date": check_in_out.check_in_timestamp,
                }
            )

            logger.info(f"Booking {booking_id} successfully checked in at {check_in_out.check_in_timestamp}.")
            return CheckInStatus.COMPLETED

        except (InvalidBookingStatusException, AlreadyCheckedInException) as e:
            logger.error(f"Error during check-in for booking {booking_id}: {str(e)}")
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error during check-in for booking {booking_id}.")
            raise Exception("An unexpected error occurred during check-in.") from e

    @transaction.atomic
    def perform_check_out(
            self,
            booking_id: int
    ) -> CheckOutStatus:
        try:
            booking = self.booking_repository.get_booking_by_id(booking_id)
            check_in_out = self.check_in_out_repository.get_by_booking(booking)

            if check_in_out.check_in_status != CheckInStatus.COMPLETED.value:
                logger.warning(f"Attempted check-out on booking {booking_id} without completed check-in.")
                raise InvalidBookingStatusException()

            if check_in_out.check_out_status == CheckOutStatus.COMPLETED.value:
                logger.warning(f"Attempted check-out on booking {booking_id} that is already checked out.")
                raise AlreadyCheckedOutException()

            check_in_out.check_out_status = CheckOutStatus.COMPLETED.value
            check_in_out.check_out_timestamp = timezone.now()
            check_in_out.save()

            booking.status = BookingStatus.COMPLETED.value
            booking.save()

            EmailService.send_checkout(
                booking.client.email,
                {
                    "room_number": booking.room.number,
                    "check_out_date": check_in_out.check_out_timestamp,
                }
            )

            logger.info(f"Booking {booking_id} successfully checked out at {check_in_out.check_out_timestamp}.")
            return CheckOutStatus.COMPLETED

        except (InvalidBookingStatusException, AlreadyCheckedOutException) as e:
            logger.error(f"Error during check-out for booking {booking_id}: {str(e)}")
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error during check-out for booking {booking_id}.")
            raise Exception("An unexpected error occurred during check-out.") from e
