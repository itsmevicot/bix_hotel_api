import logging
from datetime import date, timedelta
from unittest.mock import patch, Mock

import pytest
from django.conf import settings
from django.core import mail
from django.utils import timezone

from bookings.enums import BookingStatus
from bookings.models import Booking
from bookings.services import BookingService
from bookings.tasks import send_booking_creation_email, send_booking_confirmation_email, expire_pending_bookings, \
    manage_room_availability
from checkins.models import CheckInCheckOut
from rooms.enums import RoomStatus, RoomType
from rooms.models import Room
from users.enums import UserRole
from users.models import User
from utils.exceptions import RoomNotAvailableException, InvalidBookingConfirmationException


@pytest.fixture
def booking_service():
    return BookingService()


@pytest.fixture
def mock_booking(db, mock_user: User, mock_room: Room, status=BookingStatus.PENDING.value):
    return Booking.objects.create(
        client=mock_user,
        room=mock_room,
        check_in_date=timezone.now().date(),
        check_out_date=timezone.now().date() + timedelta(days=2),
        status=status
    )


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
def test_confirm_booking_success(booking_service: BookingService, mock_booking):
    confirmed_booking = booking_service.confirm_booking(mock_booking)
    assert confirmed_booking.status == BookingStatus.CONFIRMED.value
    assert CheckInCheckOut.objects.filter(booking=confirmed_booking).exists()


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


@pytest.mark.django_db
def test_confirm_booking_creates_checkin_checkout_instance(booking_service: BookingService, mock_booking):
    with patch.object(booking_service.check_in_out_repository, 'create_check_in_out') as mock_create_check_in_out:
        confirmed_booking = booking_service.confirm_booking(mock_booking)
        mock_create_check_in_out.assert_called_once_with(confirmed_booking)
        assert confirmed_booking.status == BookingStatus.CONFIRMED.value


@pytest.mark.django_db
def test_confirm_booking_non_pending_status_raises_exception(booking_service, booking_data):
    with patch.object(booking_service.booking_repository, 'get_booking_by_id') as mock_get_booking:
        mock_booking = Mock(**booking_data)
        mock_booking.status = BookingStatus.CONFIRMED.value
        mock_get_booking.return_value = mock_booking

        with pytest.raises(InvalidBookingConfirmationException):
            booking_service.confirm_booking(mock_booking)


@pytest.mark.django_db
def test_confirm_booking_sends_confirmation_email(booking_service: BookingService, mock_booking):
    with patch('utils.email_service.EmailService.send_booking_confirmation') as mock_send_email:
        booking_service.confirm_booking(mock_booking)
        mock_send_email.assert_called_once_with(mock_booking.client.email, {
            "room_number": mock_booking.room.number,
            "check_in_date": mock_booking.check_in_date
        })


@pytest.mark.django_db
def test_confirm_booking_logs_success_information(booking_service, booking_data, caplog):
    with patch.object(booking_service.booking_repository, 'get_booking_by_id') as mock_get_booking, \
            patch.object(booking_service.check_in_out_repository, 'create_check_in_out'):
        mock_booking = Mock(**booking_data)
        mock_booking.status = BookingStatus.PENDING.value
        mock_booking.room.number = "101"
        mock_get_booking.return_value = mock_booking

        with caplog.at_level(logging.INFO):
            booking_service.confirm_booking(mock_booking)

        assert (f"Booking {mock_booking.id} confirmed"
                f" and CheckInCheckOut created for client {mock_booking.client.id}") in caplog.text


@pytest.mark.django_db
def test_manage_room_availability_task():
    fixed_now = timezone.now()
    no_show_threshold = fixed_now - timedelta(hours=24)

    no_show_booking = Mock(id=1, room=Mock(id=101))
    completed_checkout_booking = Mock(id=2, room=Mock(id=102))

    with patch('bookings.repository.BookingRepository.get_no_show_bookings') as mock_get_no_show, \
         patch('bookings.repository.BookingRepository.get_completed_checkouts') as mock_get_completed_checkouts, \
         patch('bookings.repository.BookingRepository.mark_booking_as_no_show') as mock_mark_no_show, \
         patch('bookings.repository.BookingRepository.free_up_room') as mock_free_up_room, \
         patch('django.utils.timezone.now', return_value=fixed_now):

        mock_get_no_show.return_value = [no_show_booking]
        mock_get_completed_checkouts.return_value = [completed_checkout_booking]

        manage_room_availability()

        mock_get_no_show.assert_called_once_with(no_show_threshold)
        mock_mark_no_show.assert_called_once_with(no_show_booking)

        mock_get_completed_checkouts.assert_called_once_with(fixed_now)
        mock_free_up_room.assert_called_once_with(completed_checkout_booking)
