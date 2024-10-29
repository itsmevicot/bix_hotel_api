from django.db import models
from bookings.enums import BookingStatus
from rooms.models import Room, RoomStatus


class Booking(models.Model):
    check_in_date = models.DateTimeField()
    check_out_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=BookingStatus.choices(), default=BookingStatus.CONFIRMED.value)
    client = models.ForeignKey('authentication.User', related_name='bookings', on_delete=models.CASCADE)
    room = models.ForeignKey('rooms.Room', related_name='bookings', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reservation for {self.client.email} - Room {self.room.number}"

    class Meta:
        unique_together = ('check_in_date', 'room')

    def save(self, *args, **kwargs):
        if self.status == BookingStatus.CONFIRMED.value and self.room.status == RoomStatus.AVAILABLE.value:
            self.room.status = RoomStatus.BOOKED.value
            self.room.save()
        elif self.status == BookingStatus.CANCELLED.value:
            self.room.status = RoomStatus.AVAILABLE.value
            self.room.save()
        super().save(*args, **kwargs)
