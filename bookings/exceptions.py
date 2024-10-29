from rest_framework import status

from utils.exceptions import ExceptionMessageBuilder


class RoomNotAvailableException(ExceptionMessageBuilder):
    def __init__(self):
        self.title = "Room not available"
        self.message = "This room is not available for booking at the moment."
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = {"title": self.title, "message": self.message}
