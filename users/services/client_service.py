import logging
from typing import Optional

from django.db import transaction
from django.db.models import QuerySet

from users.models import User
from bookings.enums import BookingStatus

from bookings.models import Booking
from bookings.repository import BookingRepository
from rooms.enums import RoomStatus
from rooms.repository import RoomRepository
from users.repository import UserRepository
from utils.exceptions import BookingCannotBeConfirmedException, UnauthorizedCancellationException

logger = logging.getLogger(__name__)


class ClientService:
    def __init__(
            self,
            booking_repository: Optional[BookingRepository] = None,
            room_repository: Optional[RoomRepository] = None,
            user_repository: Optional[UserRepository] = None
    ):
        self.booking_repository = booking_repository or BookingRepository()
        self.room_repository = room_repository or RoomRepository()
        self.user_repository = user_repository or UserRepository()

    @transaction.atomic
    def create_user(
            self,
            name: str,
            email: str,
            cpf: str,
            birth_date: str,
            password: str,
    ) -> User:
        try:
            user = self.user_repository.create_user(
                name=name,
                email=email,
                cpf=cpf,
                birth_date=birth_date,
                password=password
            )
            logger.info(f"User {user.id} created successfully.")
            return user

        except Exception as e:
            logger.error(f"Error during user creation: {e}")
            raise

    def list_bookings(
            self,
            client: User
    ) -> QuerySet[Booking]:
        try:
            return self.booking_repository.list_client_bookings(client)
        except Exception as e:
            logger.error(f"Error listing bookings for client {client.id}: {e}")
            raise

    @transaction.atomic
    def confirm_booking(
            self,
            booking_id: int,
            client: User
    ) -> Booking:
        try:
            booking = self.booking_repository.get_booking_by_id(booking_id)
            if booking.client != client:
                logger.error(f"Client {client.id} is not authorized to confirm booking {booking_id}.")
                raise BookingCannotBeConfirmedException()

            if booking.status != BookingStatus.PENDING.value:
                logger.error(f"Booking {booking.id} cannot be confirmed as it is not in PENDING status.")
                raise BookingCannotBeConfirmedException()

            booking.status = BookingStatus.CONFIRMED.value
            self.room_repository.set_status(booking.room, RoomStatus.BOOKED)
            booking.save()
            logger.info(f"Booking {booking.id} confirmed for client {client.id}.")
            return booking

        except BookingCannotBeConfirmedException as e:
            logger.error(f"Booking confirmation error: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error while confirming booking {booking_id} for client {client.id}: {e}")
            raise

    @transaction.atomic
    def cancel_booking(
            self,
            booking_id: int,
            client: User
    ) -> Booking:
        try:
            booking = self.booking_repository.get_booking_by_id(booking_id)
            if booking.client != client:
                logger.error(f"Client {client.id} is not authorized to cancel booking {booking_id}.")
                raise UnauthorizedCancellationException()

            self.booking_repository.cancel_booking(booking)
            logger.info(f"Booking {booking.id} cancelled by client {client.id}.")
            return booking

        except UnauthorizedCancellationException as e:
            logger.error(f"Unauthorized cancellation attempt: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error while cancelling booking {booking_id} for client {client.id}: {e}")
            raise
