from django.urls import path
from rooms.views import RoomListView, RoomDetailView, RoomAvailabilityView

app_name = 'rooms'


urlpatterns = [
    path('', RoomListView.as_view(), name='room-list'),
    path('<int:room_id>/', RoomDetailView.as_view(), name='room-detail'),
    path('<int:room_id>/availability/', RoomAvailabilityView.as_view(), name='room-availability'),
]
