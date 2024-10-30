from django.urls import path

from checkins.views import CheckInView, CheckOutView

urlpatterns = [
    path('checkin/<int:booking_id>/', CheckInView.as_view(), name='checkin'),
    path('checkout/<int:booking_id>/', CheckOutView.as_view(), name='checkout'),
]
