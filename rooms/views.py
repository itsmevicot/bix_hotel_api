from typing import Optional
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.serializers import (
    RoomAvailabilityFilterSerializer,
    RoomListSerializer,
    RoomCreateSerializer,
    RoomDetailSerializer, RoomAvailabilitySerializer,
)
from rooms.services import RoomService
from users.enums import UserRole
from utils.custom_permissions import IsAdminUser
from utils.exceptions import RoomNotAvailableException, RoomNotFoundException


class RoomListView(APIView):
    permission_classes = [AllowAny]

    def __init__(
            self,
            room_service: Optional[RoomService] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.room_service = room_service or RoomService()

    @swagger_auto_schema(
        operation_description="Retrieve a list of rooms with optional filters for status and type.",
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, description="Room status", type=openapi.TYPE_STRING),
            openapi.Parameter('type', openapi.IN_QUERY, description="Room type", type=openapi.TYPE_STRING),
        ],
        responses={200: RoomListSerializer(many=True)}
    )
    def get(self, request):
        status_filter = request.query_params.get("status")
        room_type_filter = request.query_params.get("type")
        rooms = self.room_service.list_rooms(status=status_filter, room_type=room_type_filter)
        serializer = RoomListSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new room. Admin access required.",
        request_body=RoomCreateSerializer,
        responses={
            201: RoomDetailSerializer,
            400: "Invalid data provided",
            403: "Forbidden"
        }
    )
    def post(self, request):
        self.check_permissions(request)

        serializer = RoomCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        room = self.room_service.create_room(**serializer.validated_data)
        response_serializer = RoomDetailSerializer(room)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def check_permissions(self, request):
        if request.method == 'POST' and not request.user.role == UserRole.ADMIN.value:
            self.permission_denied(request, message="Only admins can create rooms")
        super().check_permissions(request)


class RoomDetailView(APIView):
    permission_classes = [IsAdminUser]

    def __init__(
            self,
            room_service: Optional[RoomService] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.room_service = room_service or RoomService()

    @swagger_auto_schema(
        operation_description="Retrieve a specific room by ID.",
        responses={200: RoomDetailSerializer, 404: "Room not found"}
    )
    def get(self, request, room_id):
        room = self.room_service.get_room(room_id)
        serializer = RoomDetailSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update room details by ID. Admin access required.",
        request_body=RoomCreateSerializer,
        responses={200: RoomDetailSerializer, 400: "Invalid data provided", 404: "Room not found", 403: "Forbidden"}
    )
    def put(self, request, room_id):
        serializer = RoomCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        updated_room = self.room_service.update_room(room_id, **serializer.validated_data)
        response_serializer = RoomDetailSerializer(updated_room)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete a room by ID. Admin access required.",
        responses={204: "No Content", 404: "Room not found", 403: "Forbidden"}
    )
    def delete(self, request, room_id):
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

    @swagger_auto_schema(
        operation_description="Check if a specific room is available by room number.",
        responses={
            200: RoomAvailabilitySerializer,
            404: "Room not found"
        }
    )
    def get(self, request, room_number):
        serializer = RoomAvailabilitySerializer(data={"room_number": room_number})
        serializer.is_valid(raise_exception=True)

        try:
            is_available = self.room_service.check_availability_by_number(serializer.validated_data['room_number'])
            return Response(
                RoomAvailabilitySerializer(
                    {
                        "room_number": room_number,
                        "available": is_available
                    }).data, status=status.HTTP_200_OK)
        except RoomNotAvailableException as e:
            return Response({"error": e.message}, status=e.status_code)

        except RoomNotFoundException as e:
            return Response({"error": e.message}, status=e.status_code)


class RoomAvailabilityFilterView(APIView):
    def __init__(
            self,
            room_service: Optional[RoomService] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.room_service = room_service or RoomService()

    @swagger_auto_schema(
        operation_description="Check room availability within a date range with optional filters"
                              " for room type and price.",
        query_serializer=RoomAvailabilityFilterSerializer,
        responses={
            200: RoomListSerializer(many=True),
            400: "Invalid request",
            404: "No rooms available for the specified criteria",
            500: "Internal server error."
        }
    )
    def get(self, request):
        serializer = RoomAvailabilityFilterSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        room_type = validated_data.get('type')
        max_price = validated_data.get('price')
        check_in_date = validated_data['check_in_date']
        check_out_date = validated_data['check_out_date']

        try:
            available_rooms = self.room_service.get_available_rooms(
                room_type=room_type,
                price=max_price,
                check_in_date=check_in_date,
                check_out_date=check_out_date
            )

            if available_rooms.exists():
                serialized_rooms = RoomListSerializer(available_rooms, many=True)
                return Response(serialized_rooms.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No rooms available for the specified criteria."},
                                status=status.HTTP_404_NOT_FOUND)

        except RoomNotAvailableException as e:
            return Response({"error": e.message}, status=e.status_code)
