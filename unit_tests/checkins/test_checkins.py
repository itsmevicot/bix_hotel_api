from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone
from rest_framework import status

from bookings.enums import BookingStatus
from bookings.models import Booking
from checkins.enums import CheckInStatus, CheckOutStatus
from checkins.services import CheckInCheckOutService
from rooms.enums import RoomStatus, RoomType
from rooms.models import Room
from users.models import User
from utils.exceptions import AlreadyCheckedInException, AlreadyCheckedOutException, InvalidBookingStatusException


@pytest.fixture
def check_in_out_service():
    return CheckInCheckOutService()


@pytest.fixture
def mock_user(db):
    user = User.objects.create(
        name="Test User",
        email="testuser@example.com",
        cpf="12345678909",
        birth_date="1990-01-01"
    )
    user.set_password("password123")
    user.save()
    return user


@pytest.fixture
def access_token(api_client, mock_user):
    login_data = {
        "email": mock_user.email,
        "password": "password123"
    }
    response = api_client.post("/token/", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    return response.data["access_token"]


@pytest.fixture
def auth_api_client(api_client, access_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return api_client


@pytest.fixture
def mock_room(db):
    return Room.objects.create(
        number="101",
        status=RoomStatus.AVAILABLE.value,
        room_type=RoomType.SINGLE.value,
        price=100.0
    )


@pytest.fixture
def mock_booking(db, mock_user, mock_room):
    return Booking.objects.create(
        client=mock_user,
        room=mock_room,
        check_in_date=timezone.now(),
        check_out_date=timezone.now() + timedelta(days=1),
        status=BookingStatus.CONFIRMED.value
    )


@pytest.mark.django_db
def test_check_in_success(auth_api_client, mock_booking):
    with patch.object(CheckInCheckOutService, 'perform_check_in', return_value=CheckInStatus.COMPLETED):
        response = auth_api_client.post(f"/checkin/{mock_booking.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Checked in successfully."


@pytest.mark.django_db
def test_check_in_booking_not_found(auth_api_client):
    with patch.object(CheckInCheckOutService, 'perform_check_in', side_effect=Booking.DoesNotExist):
        response = auth_api_client.post("/checkin/9999/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "error" in response.data
    assert response.data["error"] == "Booking not found."


@pytest.mark.django_db
def test_check_in_invalid_status(auth_api_client, mock_booking):
    with patch.object(CheckInCheckOutService, 'perform_check_in', side_effect=InvalidBookingStatusException):
        response = auth_api_client.post(f"/checkin/{mock_booking.id}/")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "The booking status does not allow this action."


@pytest.mark.django_db
def test_check_in_already_checked_in(auth_api_client, mock_booking):
    with patch.object(CheckInCheckOutService, 'perform_check_in', side_effect=AlreadyCheckedInException):
        response = auth_api_client.post(f"/checkin/{mock_booking.id}/")
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.data["error"] == "This booking has already been checked in."


@pytest.mark.django_db
def test_check_out_success(auth_api_client, mock_booking):
    with patch.object(CheckInCheckOutService, 'perform_check_out', return_value=CheckOutStatus.COMPLETED):
        response = auth_api_client.post(f"/checkout/{mock_booking.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Checked out successfully."


@pytest.mark.django_db
def test_check_out_booking_not_found(auth_api_client):
    with patch.object(CheckInCheckOutService, 'perform_check_out', side_effect=Booking.DoesNotExist):
        response = auth_api_client.post("/checkout/9999/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "error" in response.data
    assert response.data["error"] == "Booking not found."


@pytest.mark.django_db
def test_check_out_invalid_status(auth_api_client, mock_booking):
    with patch.object(CheckInCheckOutService, 'perform_check_out', side_effect=InvalidBookingStatusException):
        response = auth_api_client.post(f"/checkout/{mock_booking.id}/")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "The booking status does not allow this action."


@pytest.mark.django_db
def test_check_out_already_checked_out(auth_api_client, mock_booking):
    with patch.object(CheckInCheckOutService, 'perform_check_out', side_effect=AlreadyCheckedOutException):
        response = auth_api_client.post(f"/checkout/{mock_booking.id}/")
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.data["error"] == "This booking has already been checked out."
