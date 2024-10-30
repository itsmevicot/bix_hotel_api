from datetime import date
import pytest
from django.urls import reverse
from rest_framework import status

from bookings.enums import BookingStatus
from bookings.models import Booking
from rooms.enums import RoomStatus, RoomType
from rooms.models import Room
from rooms.serializers import RoomCreateSerializer
from users.enums import UserRole
from users.models import User
import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def sample_room(db):
    return Room.objects.create(
        number="101",
        status=RoomStatus.AVAILABLE.value,
        room_type=RoomType.SINGLE.value,
        price=100.00
    )


@pytest.fixture
def available_room(db):
    """Fixture for a room available for booking without any conflicting reservations."""
    return Room.objects.create(
        number="201",
        room_type=RoomType.SINGLE.value,
        status=RoomStatus.AVAILABLE.value,
        price=100.00
    )


@pytest.fixture
def room_with_booking(db):
    """Fixture for a room that has a conflicting booking."""
    room = Room.objects.create(
        number="202",
        room_type=RoomType.SINGLE.value,
        status=RoomStatus.AVAILABLE.value,
        price=120.00
    )

    client = User.objects.create(
        name="Test Client",
        email="testclient@example.com",
        cpf="12345678910",
        birth_date="1990-01-01",
        role=UserRole.CLIENT.value,
        is_active=True
    )

    Booking.objects.create(
        client=client,
        room=room,
        check_in_date=date(2024, 11, 12),
        check_out_date=date(2024, 11, 14),
        status=BookingStatus.CONFIRMED.value
    )
    return room


@pytest.mark.django_db
def test_list_rooms(auth_api_client, sample_room):
    url = reverse("rooms:room-list")
    response = auth_api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["number"] == str(sample_room.number)


@pytest.mark.django_db
def test_retrieve_room(auth_api_client, sample_room):
    url = reverse("rooms:room-detail", args=[sample_room.id])
    response = auth_api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["number"] == str(sample_room.number)
    assert response.data["status"] == sample_room.get_status_display()
    assert response.data["room_type"] == sample_room.get_room_type_display()
    assert response.data["price"] == "{:.2f}".format(float(sample_room.price))


@pytest.mark.django_db
def test_check_room_availability(auth_api_client, sample_room):
    url = reverse("rooms:room-availability", args=[sample_room.id])
    response = auth_api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["available"] is True


@pytest.mark.django_db
def test_check_room_not_available(auth_api_client, sample_room):
    sample_room.status = RoomStatus.OCCUPIED.value
    sample_room.save()

    url = reverse("rooms:room-availability", args=[sample_room.id])
    response = auth_api_client.get(url)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "error" in response.data
    assert response.data["error"] == "There are no available rooms for the selected dates."


@pytest.mark.django_db
def test_create_room(auth_api_client):
    Room.objects.filter(number="102").delete()

    url = reverse("rooms:room-list")
    data = {
        "number": "102",
        "status": RoomStatus.AVAILABLE.value,
        "room_type": RoomType.DOUBLE.value,
        "price": '150.00'
    }

    serializer = RoomCreateSerializer(data=data)
    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"

    response = auth_api_client.post(url, data=data)

    logger.info(f"Response Status: {response.status_code}")
    logger.info(f"Response Data: {response.data}")

    assert response.status_code == status.HTTP_201_CREATED
    created_room = Room.objects.get(number="102")
    assert created_room.number == data["number"]
    assert created_room.status == data["status"]
    assert created_room.room_type == data["room_type"]
    assert "{:.2f}".format(float(created_room.price)) == data["price"]


@pytest.mark.django_db
def test_update_room(auth_api_client, sample_room):
    url = reverse("rooms:room-detail", args=[sample_room.id])
    data = {
        "number": "105",
        "status": RoomStatus.OCCUPIED.value,
        "room_type": RoomType.SUITE.value,
        "price": "200.00"
    }

    response = auth_api_client.put(url, data=data)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_room_availability_with_valid_dates_and_type(auth_api_client, available_room, room_with_booking):
    url = reverse("rooms:room-availability-filter")

    params = {
        "check_in_date": "10/11/2024",
        "check_out_date": "15/11/2024",
        "room_type": RoomType.SINGLE.value,
        "price": "120.00"
    }
    response = auth_api_client.get(url, params)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["number"] == available_room.number


@pytest.mark.django_db
def test_room_availability_with_missing_dates(auth_api_client):
    url = reverse("rooms:room-availability-filter")
    response = auth_api_client.get(url, {"room_type": RoomType.SINGLE.value, "price": "120.00"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "check_in_date" in response.data
    assert "check_out_date" in response.data


@pytest.mark.django_db
def test_room_availability_with_invalid_date_format(auth_api_client):
    url = reverse("rooms:room-availability-filter")
    response = auth_api_client.get(url, {"check_in_date": "2024/11/10", "check_out_date": "2024-11-15"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "check_in_date" in response.data
    assert "Formato inválido para data" in response.data["check_in_date"][0]


@pytest.mark.django_db
def test_room_availability_check_out_before_check_in(auth_api_client):
    url = reverse("rooms:room-availability-filter")
    response = auth_api_client.get(url, {
        "check_in_date": "15/11/2024",
        "check_out_date": "10/11/2024",
        "room_type": RoomType.SINGLE.value
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "non_field_errors" in response.data
    assert response.data["non_field_errors"][0] == "check_out_date must be after check_in_date."


@pytest.mark.django_db
def test_no_rooms_available_for_criteria(auth_api_client):
    url = reverse("rooms:room-availability-filter")
    Room.objects.create(number="301", room_type=RoomType.SINGLE.value, status=RoomStatus.BOOKED.value, price=100.00)

    params = {
        "check_in_date": "10/11/2024",
        "check_out_date": "15/11/2024",
        "room_type": RoomType.SINGLE.value,
        "price": "80.00"
    }
    response = auth_api_client.get(url, params)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["message"] == "No rooms available for the specified criteria."


@pytest.mark.django_db
def test_room_availability_with_price_filter(auth_api_client):
    url = reverse("rooms:room-availability-filter")
    Room.objects.create(number="401", room_type=RoomType.SINGLE.value, status=RoomStatus.AVAILABLE.value, price=100.00)
    Room.objects.create(number="402", room_type=RoomType.SINGLE.value, status=RoomStatus.AVAILABLE.value, price=150.00)

    params = {
        "check_in_date": "10/11/2024",
        "check_out_date": "15/11/2024",
        "room_type": RoomType.SINGLE.value,
        "price": "120.00"
    }
    response = auth_api_client.get(url, params)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["number"] == "401"
    assert response.data[0]["price"] == "100.00"
