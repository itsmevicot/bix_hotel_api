from django.urls import path
from rooms.views import RoomListView, RoomDetailView, RoomAvailabilityView, RoomAvailabilityFilterView

app_name = 'rooms'


urlpatterns = [
    path('', RoomListView.as_view(), name='room-list'),
    path('<int:room_id>/', RoomDetailView.as_view(), name='room-detail'),
    path('<str:room_number>/availability/', RoomAvailabilityView.as_view(), name='room-availability'),
    path('availability/filter/', RoomAvailabilityFilterView.as_view(), name='room-availability-filter'),
]
