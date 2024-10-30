from datetime import datetime, date

from django.db.models import QuerySet
from django.utils import timezone
from users.models import User
from bookings.models import Booking
from rooms.enums import RoomStatus
from rooms.models import Room
from bookings.enums import BookingStatus
from typing import Optional, List


class BookingRepository:

    @staticmethod
    def create_booking(
            client: User,
            room: Room,
            check_in_date: date,
            check_out_date: date,
            status: Optional[str] = BookingStatus.CONFIRMED.value
    ) -> Booking:
        return Booking.objects.create(
            client=client,
            room=room,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            status=status,
            created_at=timezone.now(),
        )

    @staticmethod
    def list_client_bookings(
            client: User
    ) -> QuerySet[Booking]:
        return Booking.objects.filter(client=client)

    @staticmethod
    def get_booking_by_id(
            booking_id: int
    ) -> Booking:
        return Booking.objects.get(id=booking_id)

    @staticmethod
    def cancel_booking(
            booking: Booking
    ) -> None:
        booking.status = BookingStatus.CANCELLED.value
        booking.room.status = RoomStatus.AVAILABLE.value
        booking.cancelled_at = timezone.now()
        booking.room.save()
        booking.save()

    @staticmethod
    def get_expiring_pending_bookings(
            threshold_date: datetime.date
    ) -> List[Booking]:
        """
        Retrieves all pending bookings with a check-in date within the given threshold date.
        """
        return Booking.objects.filter(
            status=BookingStatus.PENDING.value,
            check_in_date__lte=threshold_date
        )
