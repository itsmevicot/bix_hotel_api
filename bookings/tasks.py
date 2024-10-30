import logging

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from bookings.services import BookingService
from bookings.repository import BookingRepository

logger = logging.getLogger(__name__)


@shared_task
def expire_pending_bookings(booking_service: BookingService = None):
    booking_service = booking_service or BookingService()
    now = timezone.now()
    threshold_time = now + timedelta(hours=24)

    pending_bookings = BookingRepository.get_expiring_pending_bookings(threshold_time.date())

    for booking in pending_bookings:
        booking_service.cancel_booking(booking)
