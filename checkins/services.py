import logging
from datetime import datetime
from typing import Optional
from django.db import transaction
from bookings.enums import BookingStatus
from bookings.repository import BookingRepository
from checkins.enums import CheckInStatus, CheckOutStatus
from checkins.repository import CheckInCheckOutRepository
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

    def perform_check_in(
            self,
            booking_id: int
    ) -> CheckInStatus:
        try:
            booking = self.booking_repository.get_booking_by_id(booking_id)

            if booking.status != BookingStatus.CONFIRMED.value:
                logger.warning(f"Attempted check-in on booking {booking_id} with status {booking.status}.")
                raise InvalidBookingStatusException()

            if booking.check_in_date:
                logger.warning(f"Attempted check-in on booking {booking_id} that is already checked in.")
                raise AlreadyCheckedInException()

            with transaction.atomic():
                booking.check_in_date = datetime.now()
                self.booking_repository.update_booking(booking)
                logger.info(f"Booking {booking_id} successfully checked in at {booking.check_in_date}.")

            return CheckInStatus.COMPLETED

        except (InvalidBookingStatusException, AlreadyCheckedInException) as e:
            logger.error(f"Error during check-in for booking {booking_id}: {str(e)}")
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error during check-in for booking {booking_id}.")
            raise Exception("An unexpected error occurred during check-in.") from e

    def perform_check_out(
            self,
            booking_id: int
    ) -> CheckOutStatus:
        try:
            booking = self.booking_repository.get_booking_by_id(booking_id)

            if not booking.check_in_date:
                logger.warning(f"Attempted check-out on booking {booking_id} without a check-in date.")
                raise InvalidBookingStatusException()

            if booking.check_out_date:
                logger.warning(f"Attempted check-out on booking {booking_id} that is already checked out.")
                raise AlreadyCheckedOutException()

            with transaction.atomic():
                booking.check_out_date = datetime.now()
                booking.status = BookingStatus.COMPLETED.value
                self.booking_repository.update_booking(booking)
                logger.info(f"Booking {booking_id} successfully checked out at {booking.check_out_date}.")

            return CheckOutStatus.COMPLETED

        except (InvalidBookingStatusException, AlreadyCheckedOutException) as e:
            logger.error(f"Error during check-out for booking {booking_id}: {str(e)}")
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error during check-out for booking {booking_id}.")
            raise Exception("An unexpected error occurred during check-out.") from e
