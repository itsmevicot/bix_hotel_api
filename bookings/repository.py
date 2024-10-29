from datetime import datetime
from django.utils import timezone
from authentication.models import User
from bookings.models import Booking
from rooms.models import Room
from bookings.enums import BookingStatus
from typing import Optional


class BookingRepository:

    @staticmethod
    def create_booking(
            client: User,
            room: Room,
            check_in_date: datetime,
            check_out_date: datetime,
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
    def update_room_status(
            room: Room,
            status: str
    ) -> None:
        room.status = status
        room.save()
