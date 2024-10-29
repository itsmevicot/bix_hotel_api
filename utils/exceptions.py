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


class RoomNotAvailableException(ExceptionMessageBuilder):
    def __init__(self):
        self.title = "Room not available"
        self.message = "This room is not available for booking at the moment."
        self.status_code = status.HTTP_400_BAD_REQUEST
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

