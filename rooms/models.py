from django.db import models

from rooms.enums import RoomType, RoomStatus


class Room(models.Model):
    number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=20, choices=RoomType.choices())
    status = models.CharField(max_length=20, choices=RoomStatus.choices(), default=RoomStatus.AVAILABLE.value)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Room {self.number} - {self.get_room_type_display()} ({self.get_status_display()})"
