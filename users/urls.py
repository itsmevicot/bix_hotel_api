from django.urls import path

from users.views import ClientRegistrationView

app_name = 'users'

urlpatterns = [
    path('register/', ClientRegistrationView.as_view(), name='client-register'),
]
