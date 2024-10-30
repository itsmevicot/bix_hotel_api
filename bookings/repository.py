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
        booking = Booking.objects.get(id=booking_id)
        if not booking:
            raise Booking.DoesNotExist

        return booking

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
        return Booking.objects.filter(
            status=BookingStatus.PENDING.value,
            check_in_date__lte=threshold_date
        )

    @staticmethod
    def is_room_available(
            room_id: int,
            check_in_date: date,
            check_out_date: date
    ) -> bool:
        conflicting_bookings = Booking.objects.filter(
            room_id=room_id,
            status=BookingStatus.CONFIRMED.value,
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
        )

        return not conflicting_bookings.exists()

    @staticmethod
    def get_filtered_bookings(filter_criteria: dict):
        """
        Fetch bookings based on filter criteria.
        """
        queryset = Booking.objects.filter(**filter_criteria)
        return queryset
