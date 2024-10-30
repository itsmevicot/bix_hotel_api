from django.db import models
from bookings.models import Booking
from checkins.enums import CheckInStatus, CheckOutStatus


class CheckInCheckOut(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="check_in_out")
    check_in_timestamp = models.DateTimeField(null=True, blank=True)
    check_out_timestamp = models.DateTimeField(null=True, blank=True)
    check_in_status = models.CharField(max_length=20, choices=CheckInStatus.choices(),
                                       default=CheckInStatus.PENDING.value)
    check_out_status = models.CharField(max_length=20, choices=CheckOutStatus.choices(),
                                        default=CheckOutStatus.PENDING.value)

    def __str__(self):
        return f"CheckInCheckOut for Booking {self.booking.id}"
