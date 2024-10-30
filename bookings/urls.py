from django.urls import path
from bookings.views import ConfirmBookingView, CancelBookingView, BookingDetailView, BookingListView

app_name = 'bookings'

urlpatterns = [
    path('', BookingListView.as_view(), name='booking-list'),
    path('<int:booking_id>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<int:booking_id>/confirm/', ConfirmBookingView.as_view(), name='booking-confirm'),
    path('<int:booking_id>/cancel/', CancelBookingView.as_view(), name='booking-cancel'),
]
