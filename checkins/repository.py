from typing import Optional
from django.utils import timezone

from bookings.models import Booking
from checkins.enums import CheckInStatus, CheckOutStatus
from checkins.models import CheckInCheckOut


class CheckInCheckOutRepository:

    @staticmethod
    def create_check_in_out(booking: Booking) -> CheckInCheckOut:
        return CheckInCheckOut.objects.create(booking=booking)

    @staticmethod
    def get_by_booking(booking: Booking) -> Optional[CheckInCheckOut]:
        return CheckInCheckOut.objects.filter(booking=booking).first()

    @staticmethod
    def update_check_in_status(check_in_out: CheckInCheckOut) -> None:
        check_in_out.check_in_status = CheckInStatus.COMPLETED.value
        check_in_out.check_in_timestamp = timezone.now()
        check_in_out.save()

    @staticmethod
    def update_check_out_status(check_in_out: CheckInCheckOut) -> None:
        check_in_out.check_out_status = CheckOutStatus.COMPLETED.value
        check_in_out.check_out_timestamp = timezone.now()
        check_in_out.save()