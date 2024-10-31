from django.urls import path
from bookings.views import ConfirmBookingView, BookingDetailView, BookingListView

app_name = 'bookings'

urlpatterns = [
    path('', BookingListView.as_view(), name='booking-list'),
    path('<int:booking_id>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<int:booking_id>/confirm/', ConfirmBookingView.as_view(), name='booking-confirm'),
]
