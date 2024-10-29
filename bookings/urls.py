from django.urls import path
from bookings.views import ClientBookingsView, ConfirmBookingView, CancelBookingView

app_name = 'bookings'

urlpatterns = [
    path('', ClientBookingsView.as_view(), name='client-bookings'),
    path('<int:booking_id>/confirm/', ConfirmBookingView.as_view(), name='confirm-booking'),
    path('<int:booking_id>/cancel/', CancelBookingView.as_view(), name='cancel-booking'),
]
