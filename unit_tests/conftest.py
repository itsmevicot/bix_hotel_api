import pytest
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        name="Admin User",
        email="admin@example.com",
        cpf="12345678909",
        birth_date="1985-01-01",
        password="AdminPass123!"
    )
    user.role = "ADMIN"
    user.save()
    return user


@pytest.fixture
def access_token_admin(api_client, admin_user):
    login_data = {
        "email": admin_user.email,
        "password": "AdminPass123!"
    }
    response = api_client.post("/token/", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    return response.data["access_token"]


@pytest.fixture
def auth_api_client(api_client, access_token_admin):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token_admin}')
    return api_client
