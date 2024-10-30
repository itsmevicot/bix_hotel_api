from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rooms.models import Room
from rooms.enums import RoomStatus, RoomType


@pytest.fixture
def sample_room(db):
    return Room.objects.create(
        number="101",
        status=RoomStatus.AVAILABLE.value,
        type=RoomType.SINGLE.value,
        price=100.00
    )


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
    assert response.data["type"] == sample_room.get_type_display()
    assert response.data["price"] == "{:.2f}".format(sample_room.price)


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
    url = reverse("rooms:room-list")
    data = {
        "number": "102",
        "status": RoomStatus.AVAILABLE.value,
        "type": RoomType.DOUBLE.value,
        "price": 150.00
    }
    response = auth_api_client.post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Room.objects.filter(number="102").exists()
    assert response.data["number"] == str(data["number"])
    assert response.data["status"] == RoomStatus(data["status"]).name.capitalize()
    assert response.data["type"] == RoomType(data["type"]).name.capitalize()
    assert response.data["price"] == "{:.2f}".format(data["price"])


@pytest.mark.django_db
def test_update_room(auth_api_client, sample_room):
    url = reverse("rooms:room-detail", args=[sample_room.id])
    data = {
        "number": "101",
        "status": RoomStatus.OCCUPIED.value,
        "type": RoomType.SUITE.value,
        "price": "200.00"
    }
    response = auth_api_client.put(url, data=data)

    assert response.status_code == status.HTTP_200_OK
