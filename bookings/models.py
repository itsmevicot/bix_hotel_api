from django.db import models
from django.utils import timezone

from clients.models import Client
from rooms.models import Room


class Booking(models.Model):
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    check_in_date = models.DateTimeField()
    check_out_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CONFIRMED)
    client = models.ForeignKey(Client, related_name='bookings', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, related_name='bookings', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Reservation for {self.client.user.username} - Room {self.room.number}"

    class Meta:
        unique_together = ('check_in_date', 'room')

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_CONFIRMED and self.room.status == Room.STATUS_AVAILABLE:
            self.room.status = Room.STATUS_OCCUPIED
            self.room.save()
        elif self.status == self.STATUS_CANCELLED:
            self.room.status = Room.STATUS_AVAILABLE
            self.room.save()
        super().save(*args, **kwargs)
