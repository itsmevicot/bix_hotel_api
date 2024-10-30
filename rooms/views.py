from typing import Optional

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.serializers import RoomSerializer
from rooms.services import RoomService
from utils.custom_permissions import IsAdminUser
from utils.exceptions import RoomNotAvailableException


class RoomListView(APIView):
    permission_classes = [AllowAny]

    def __init__(
            self,
            room_service: Optional[RoomService] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.room_service = room_service or RoomService()

    def get(self, request):
        status_filter = request.query_params.get("status")
        room_type_filter = request.query_params.get("type")
        rooms = self.room_service.list_rooms(
            status=status_filter,
            room_type=room_type_filter
        )
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        self.permission_classes = [IsAdminUser]
        data = request.data
        room = self.room_service.create_room(
            number=data["number"],
            status=data["status"],
            room_type=data["type"],
            price=data["price"],
        )
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RoomDetailView(APIView):
    def __init__(
            self,
            room_service: Optional[RoomService] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.room_service = room_service or RoomService()

    def get(self, request, room_id):
        room = self.room_service.get_room(room_id)
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, room_id):
        self.permission_classes = [IsAdminUser]
        updated_room = self.room_service.update_room(
            room_id,
            **request.data
        )
        serializer = RoomSerializer(updated_room)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, room_id):
        self.permission_classes = [IsAdminUser]
        self.room_service.delete_room(room_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoomAvailabilityView(APIView):
    def __init__(
            self,
            room_service: Optional[RoomService] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.room_service = room_service or RoomService()

    def get(self, request, room_id):
        try:
            is_available = self.room_service.check_availability(room_id)
            return Response({"available": is_available}, status=status.HTTP_200_OK)
        except RoomNotAvailableException as e:
            return Response({"error": e.message}, status=e.status_code)
