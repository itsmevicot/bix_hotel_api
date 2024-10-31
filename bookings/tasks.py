import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from bookings.services import BookingService
from bookings.repository import BookingRepository

logger = logging.getLogger(__name__)


@shared_task
def expire_pending_bookings(
        booking_service: BookingService = None,
        booking_repository: BookingRepository = None
):
    booking_service = booking_service or BookingService()
    booking_repository = booking_repository or BookingRepository()
    now = timezone.now()
    threshold_time = now + timedelta(hours=24)

    pending_bookings = booking_repository.get_expiring_pending_bookings(threshold_time.date())

    for booking in pending_bookings:
        try:
            booking_service.cancel_booking(booking)
            logger.info(f"Booking {booking.id} canceled due to unconfirmed status within 24 hours before check-in.")
        except Exception as e:
            logger.error(f"Failed to cancel booking {booking.id}: {e}")


@shared_task
def send_booking_confirmation_email(
        client_email: str,
        booking_details: dict
):
    try:
        send_mail(
            subject="Booking Confirmation",
            message=f"Your booking for Room {booking_details['room_number']} is confirmed!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client_email],
        )
        logger.info(f"Booking confirmation email sent to {client_email} for room {booking_details['room_number']}.")
    except Exception as e:
        logger.error(f"Failed to send booking confirmation email to {client_email}: {e}")


@shared_task
def send_booking_cancellation_email(
        client_email: str,
        booking_details: dict
):
    try:
        send_mail(
            subject="Booking Cancellation",
            message=f"Your booking for Room {booking_details['room_number']} has been canceled.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client_email],
        )
        logger.info(f"Booking cancellation email sent to {client_email} for room {booking_details['room_number']}.")
    except Exception as e:
        logger.error(f"Failed to send booking cancellation email to {client_email}: {e}")


@shared_task
def send_booking_creation_email(
        client_email: str,
        booking_details: dict
):
    try:
        send_mail(
            subject="Booking Created",
            message=f"Your booking for Room {booking_details['room_number']} is pending confirmation.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client_email],
        )
        logger.info(f"Booking creation email sent to {client_email} for room {booking_details['room_number']}.")
    except Exception as e:
        logger.error(f"Failed to send booking creation email to {client_email}: {e}")


@shared_task
def send_booking_modification_email(client_email: str, booking_details: dict):
    try:
        send_mail(
            subject="Booking Modification",
            message=(
                f"Your booking has been modified.\n\n"
                f"Before Modification:\n"
                f"Room Number: {booking_details['room_number_before']}\n"
                f"Check-in Date: {booking_details['check_in_date_before']}\n"
                f"Check-out Date: {booking_details['check_out_date_before']}\n\n"
                f"After Modification:\n"
                f"Room Number: {booking_details['room_number_after']}\n"
                f"Check-in Date: {booking_details['check_in_date_after']}\n"
                f"Check-out Date: {booking_details['check_out_date_after']}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client_email],
        )
        logger.info(
            f"Booking modification email sent to {client_email} for room "
            f"{booking_details['room_number_after']}."
        )
    except Exception as e:
        logger.error(f"Failed to send booking modification email to {client_email}: {e}")


@shared_task
def manage_room_availability():
    now = timezone.now()
    no_show_threshold = now - timedelta(hours=24)
    booking_repository = BookingRepository()

    no_show_bookings = booking_repository.get_no_show_bookings(no_show_threshold)
    for booking in no_show_bookings:
        booking_repository.mark_booking_as_no_show(booking)
        logger.info(f"Booking {booking.id} marked as NO_SHOW and room {booking.room.id} set to AVAILABLE.")

    completed_checkouts = booking_repository.get_completed_checkouts(now)
    for booking in completed_checkouts:
        booking_repository.free_up_room(booking)
        logger.info(f"Room {booking.room.id} freed up after booking {booking.id} checkout.")
