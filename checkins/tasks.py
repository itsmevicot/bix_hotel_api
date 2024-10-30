from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_checkin_email(client_email: str, booking_details: dict):
    send_mail(
        subject="Check-In Confirmation",
        message=f"Your check-in for Room {booking_details['room_number']} is confirmed!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[client_email],
    )


@shared_task
def send_checkout_email(client_email: str, booking_details: dict):
    send_mail(
        subject="Check-Out Confirmation",
        message=f"Your check-out for Room {booking_details['room_number']} is completed!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[client_email],
    )


@shared_task
def send_no_show_email(client_email: str, booking_details: dict):
    send_mail(
        subject="No Show",
        message=f"Your booking for Room {booking_details['room_number']} has been marked as No Show.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[client_email],
    )
