import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User
from datetime import date, timedelta


@pytest.fixture
def user_data():
    """Fixture to provide valid user data for testing."""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "cpf": "71882006020",
        "birth_date": (date.today() - timedelta(days=365 * 20)).strftime("%d/%m/%Y"),
        "password": "SecurePass123!"
    }


@pytest.mark.django_db
def test_successful_user_registration(api_client, user_data):
    """Test successful user registration."""
    url = reverse("users:client-register")
    response = api_client.post(url, data=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email=user_data["email"]).exists()
    assert response.data["status"] == "success"
    assert response.data["message"] == "Client successfully created."


@pytest.mark.django_db
def test_duplicate_email_registration(api_client, user_data):
    """Test registration with duplicate email."""

    User.objects.create_user(
        name=user_data["name"],
        email=user_data["email"],
        cpf=user_data["cpf"],
        birth_date=(date.today() - timedelta(days=365 * 20)).strftime("%Y-%m-%d"),
        password=user_data["password"]
    )

    url = reverse("users:client-register")
    response = api_client.post(url, data=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "A user with this email already exists." in response.data["detail"]["email"][0]


@pytest.mark.django_db
def test_underage_user_registration(api_client, user_data):
    """Test registration for an underage user."""
    user_data["birth_date"] = (date.today() - timedelta(days=365 * 17)).strftime("%d/%m/%Y")
    url = reverse("users:client-register")
    response = api_client.post(url, data=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "You must be at least 18 years old to register." in response.data["detail"]["birth_date"][0]


@pytest.mark.django_db
def test_invalid_cpf_format_registration(api_client, user_data):
    """Test registration with invalid CPF format."""
    user_data["cpf"] = "invalid_cpf"
    url = reverse("users:client-register")
    response = api_client.post(url, data=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid CPF number." in response.data["detail"]["cpf"][0]
