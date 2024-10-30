from django.core.mail import send_mail
from django.conf import settings


class EmailService:
    @staticmethod
    def send_booking_confirmation(client_email, booking_details):
        send_mail(
            subject="Booking Confirmation",
            message=f"Your booking for Room {booking_details['room_number']} is confirmed!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client_email],
        )

    @staticmethod
    def send_booking_cancellation(client_email, booking_details):
        send_mail(
            subject="Booking Cancellation",
            message=f"Your booking for Room {booking_details['room_number']} has been canceled.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client_email],
        )

    @staticmethod
    def send_booking_creation(client_email, booking_details):
        send_mail(
            subject="Booking Created",
            message=f"Your booking for Room {booking_details['room_number']} is pending confirmation.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client_email],
        )
