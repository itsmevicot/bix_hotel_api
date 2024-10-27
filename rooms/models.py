from django.db import models


class Room(models.Model):
    STATUS_AVAILABLE = 'available'
    STATUS_OCCUPIED = 'occupied'
    STATUS_MAINTENANCE = 'maintenance'

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_OCCUPIED, 'Occupied'),
        (STATUS_MAINTENANCE, 'Maintenance'),
    ]

    TYPE_SINGLE = 'single'
    TYPE_DOUBLE = 'double'
    TYPE_SUITE = 'suite'

    TYPE_CHOICES = [
        (TYPE_SINGLE, 'Single'),
        (TYPE_DOUBLE, 'Double'),
        (TYPE_SUITE, 'Suite'),
    ]

    number = models.PositiveIntegerField(unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Room {self.number} - {self.type} ({self.status})"
