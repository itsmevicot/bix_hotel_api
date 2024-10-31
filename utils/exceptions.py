from typing import Optional

from rest_framework import status
from rest_framework.exceptions import APIException


class ExceptionInterface:
    title: Optional[str] = "Something went wrong"
    status_code: Optional[int] = 500
    message: Optional[str] = "An error occurred while processing your request"


class ExceptionMessageBuilder(APIException):
    def __init__(self, ex_info: ExceptionInterface):
        self.title = ex_info.title
        self.status_code = ex_info.status_code
        self.message = ex_info.message


class RoomNotFoundException(ExceptionMessageBuilder):
    def __init__(self):
        self.title = "Room Not Found"
        self.message = "The requested room does not exist."
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = {"title": self.title, "message": self.message}


class RoomNotAvailableException(ExceptionMessageBuilder):
    def __init__(self):
        self.title = "Room not available"
        self.message = "There are no available rooms for the selected dates."
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = {"title": self.title, "message": self.message}


class BookingCannotBeConfirmedException(ExceptionMessageBuilder):
    def __init__(self):
        self.title = "Booking Cannot Be Confirmed"
        self.message = "This booking cannot be confirmed due to its current status."
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = {"title": self.title, "message": self.message}


class UnauthorizedCancellationException(ExceptionMessageBuilder):
    def __init__(self):
        self.title = "Unauthorized Cancellation"
        self.message = "You are not authorized to cancel this booking."
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = {"title": self.title, "message": self.message}


class InvalidBookingModificationException(ExceptionMessageBuilder):
    def __init__(self):
        self.title = "Invalid Booking Modification"
        self.message = "Only non-confirmed bookings can be modified."
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = {"title": self.title, "message": self.message}


class InvalidBookingConfirmationException(ExceptionMessageBuilder):
    def __init__(self):
        self.title = "Invalid Booking Confirmation"
        self.message = "Only pending bookings can be confirmed."
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = {"title": self.title, "message": self.message}


class InvalidBookingStatusException(ExceptionMessageBuilder):
    def __init__(self):
        self.title = "Invalid Booking Status"
        self.message = "The booking status does not allow this action."
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = {"title": self.title, "message": self.message}


class AlreadyCheckedInException(ExceptionMessageBuilder):
    def __init__(self):
        self.title = "Already Checked-In"
        self.message = "This booking has already been checked in."
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = {"title": self.title, "message": self.message}


class AlreadyCheckedOutException(ExceptionMessageBuilder):
    def __init__(self):
        self.title = "Already Checked-Out"
        self.message = "This booking has already been checked out."
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = {"title": self.title, "message": self.message}
