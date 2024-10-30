
class EmailService:
    @staticmethod
    def send_booking_confirmation(client_email, booking_details):
        from bookings.tasks import send_booking_confirmation_email
        send_booking_confirmation_email.delay(client_email, booking_details)

    @staticmethod
    def send_booking_cancellation(client_email, booking_details):
        from bookings.tasks import send_booking_cancellation_email
        send_booking_cancellation_email.delay(client_email, booking_details)

    @staticmethod
    def send_booking_creation(client_email, booking_details):
        from bookings.tasks import send_booking_creation_email
        send_booking_creation_email.delay(client_email, booking_details)