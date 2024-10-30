from datetime import date, timedelta
from unittest.mock import patch, Mock

import pytest
from django.conf import settings
from django.core import mail
from django.utils import timezone

from bookings.enums import BookingStatus
from bookings.services import BookingService
from bookings.tasks import send_booking_creation_email, send_booking_confirmation_email, expire_pending_bookings
from rooms.enums import RoomStatus, RoomType
from rooms.models import Room
from users.enums import UserRole
from users.models import User
from utils.exceptions import RoomNotAvailableException, InvalidBookingConfirmationException


@pytest.fixture
def booking_service():
    return BookingService()


@pytest.fixture
def mock_user(db):
    return User.objects.create(
        name="Test User",
        email="test@example.com",
        cpf="12345678909",
        birth_date="1990-01-01",
        role=UserRole.CLIENT.value
    )


@pytest.fixture
def mock_room(db):
    return Room.objects.create(
        number="101",
        status=RoomStatus.AVAILABLE.value,
        type=RoomType.SINGLE.value,
        price=100.0
    )


@pytest.fixture
def valid_check_in_date():
    return date.today() + timedelta(days=1)


@pytest.fixture
def valid_check_out_date():
    return date.today() + timedelta(days=3)


@pytest.fixture
def booking_data(mock_user, valid_check_in_date, valid_check_out_date):
    return {
        "client": mock_user,
        "check_in_date": valid_check_in_date,
        "check_out_date": valid_check_out_date,
        "status": BookingStatus.PENDING.value
    }


@pytest.mark.django_db
def test_create_booking_success(booking_service, booking_data, mock_room):
    with patch.object(booking_service.room_repository, 'get_available_room') as mock_get_room:
        mock_get_room.return_value = mock_room
        booking = booking_service.create_booking(
            client=booking_data["client"],
            check_in_date=booking_data["check_in_date"],
            check_out_date=booking_data["check_out_date"],
            room_type=RoomType.SINGLE
        )

        assert booking.client == booking_data["client"]
        assert booking.room == mock_room
        assert booking.status == BookingStatus.PENDING.value


@pytest.mark.django_db
def test_create_booking_no_room_available(booking_service, booking_data):
    with patch.object(booking_service.room_repository, 'get_available_room', return_value=None):
        with pytest.raises(RoomNotAvailableException):
            booking_service.create_booking(
                client=booking_data["client"],
                check_in_date=booking_data["check_in_date"],
                check_out_date=booking_data["check_out_date"]
            )


@pytest.mark.django_db
def test_modify_booking_success(booking_service, booking_data, mock_room):
    new_check_in_date = booking_data["check_in_date"] + timedelta(days=1)
    new_check_out_date = booking_data["check_out_date"] + timedelta(days=1)

    with patch.object(booking_service.booking_repository, 'get_booking_by_id') as mock_get_booking, \
         patch.object(booking_service.booking_repository, 'is_room_available', return_value=True):
        mock_booking = Mock(**booking_data)
        mock_booking.status = BookingStatus.CONFIRMED.value
        mock_booking.room = mock_room
        mock_get_booking.return_value = mock_booking

        modified_booking = booking_service.modify_booking(
            booking_id=1,
            new_check_in_date=new_check_in_date,
            new_check_out_date=new_check_out_date
        )

        assert modified_booking.check_in_date == new_check_in_date
        assert modified_booking.check_out_date == new_check_out_date


@pytest.mark.django_db
def test_confirm_booking_success(booking_service, booking_data):
    with patch.object(booking_service.booking_repository, 'get_booking_by_id') as mock_get_booking:
        mock_booking = Mock(**booking_data)
        mock_booking.status = BookingStatus.PENDING.value
        mock_booking.room.number = "101"
        mock_get_booking.return_value = mock_booking

        confirmed_booking = booking_service.confirm_booking(mock_booking)

        assert confirmed_booking.status == BookingStatus.CONFIRMED.value


@pytest.mark.django_db
def test_confirm_booking_not_pending(booking_service, booking_data):
    with patch.object(booking_service.booking_repository, 'get_booking_by_id') as mock_get_booking:
        mock_booking = Mock(**booking_data)
        mock_booking.status = BookingStatus.CONFIRMED.value
        mock_get_booking.return_value = mock_booking

        with pytest.raises(InvalidBookingConfirmationException):
            booking_service.confirm_booking(mock_booking)


@pytest.mark.django_db
def test_cancel_booking_success(booking_service, booking_data, mock_room):
    with patch.object(booking_service.booking_repository, 'get_booking_by_id') as mock_get_booking:
        mock_booking = Mock(**booking_data)
        mock_booking.status = BookingStatus.PENDING.value
        mock_booking.room = mock_room
        mock_room.status = RoomStatus.OCCUPIED.value
        mock_get_booking.return_value = mock_booking

        canceled_booking = booking_service.cancel_booking(mock_booking)

        assert canceled_booking.status == BookingStatus.CANCELLED.value
        assert canceled_booking.room.status == RoomStatus.AVAILABLE.value


def test_get_filtered_bookings_client(booking_service, mock_user):
    with patch.object(booking_service.booking_repository, 'get_filtered_bookings') as mock_get_bookings:
        mock_get_bookings.return_value = []
        bookings = booking_service.get_filtered_bookings(
            filters={"check_in_date": date.today()},
            user=mock_user
        )
        assert mock_get_bookings.called
        assert bookings == []


def test_get_booking_by_id_unauthorized(booking_service, mock_user):
    with patch.object(booking_service.booking_repository, 'get_booking_by_id') as mock_get_booking:
        mock_booking = Mock(client=Mock(id=2))
        mock_get_booking.return_value = mock_booking

        with pytest.raises(PermissionError):
            booking_service.get_booking_by_id(booking_id=1, user=mock_user)


@pytest.mark.django_db
def test_create_booking_no_room_available(booking_service, booking_data):
    with patch.object(booking_service.room_repository, 'get_available_room', return_value=None):
        with pytest.raises(RoomNotAvailableException):
            booking_service.create_booking(
                client=booking_data["client"],
                check_in_date=booking_data["check_in_date"],
                check_out_date=booking_data["check_out_date"]
            )


def test_send_booking_creation_email(mock_user):
    booking_details = {"room_number": "101"}
    send_booking_creation_email(mock_user.email, booking_details)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Booking Created"
    assert "Room 101" in mail.outbox[0].body


def test_celery_send_booking_confirmation_email_task():
    with patch('bookings.tasks.send_mail') as mock_send_mail:
        client_email = "client@example.com"
        booking_details = {"room_number": "101"}

        send_booking_confirmation_email(client_email, booking_details)

        mock_send_mail.assert_called_once_with(
            subject="Booking Confirmation",
            message="Your booking for Room 101 is confirmed!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client_email]
        )


@pytest.mark.django_db
def test_expire_pending_bookings(booking_service):
    expired_booking = Mock(id=1, status=BookingStatus.PENDING.value, check_in_date=timezone.now() + timedelta(hours=24))

    with patch.object(booking_service.booking_repository, 'get_expiring_pending_bookings',
                      return_value=[expired_booking]), \
            patch.object(booking_service, 'cancel_booking') as mock_cancel_booking:
        expire_pending_bookings(booking_service=booking_service, booking_repository=booking_service.booking_repository)

        mock_cancel_booking.assert_called_once_with(expired_booking)
