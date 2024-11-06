import logging
from typing import Optional

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    BookingFilterSerializer, BookingUpdateSerializer
)
from bookings.services import BookingService
from utils.exceptions import RoomNotAvailableForSelectedDatesException, InvalidBookingModificationException, \
    UnauthorizedCancellationException, AlreadyCanceledException, \
    UnauthorizedOrInvalidBookingException

logger = logging.getLogger(__name__)


class BookingListView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(
            self,
            booking_service: Optional[BookingService] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.booking_service = booking_service or BookingService()

    @swagger_auto_schema(
        operation_description="Retrieve all bookings with optional filters for client or admin.",
        query_serializer=BookingFilterSerializer,
        responses={
            200: BookingSerializer(many=True),
            500: "An error occurred while retrieving bookings."
        }
    )
    def get(self, request):
        filters = request.query_params.dict()
        bookings = self.booking_service.get_filtered_bookings(
            filters,
            request.user
        )
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new booking with specified check-in and check-out dates.",
        request_body=BookingCreateSerializer,
        responses={
            201: "Booking created successfully.",
            400: "Validation error",
            409: "Room not available for booking.",
            500: "Internal server error."
        }
    )
    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        if serializer.is_valid():
            client = request.user
            check_in_date = serializer.validated_data['check_in_date']
            check_out_date = serializer.validated_data['check_out_date']
            room_type = serializer.validated_data['room_type']

            try:
                booking = self.booking_service.create_booking(
                    client=client,
                    check_in_date=check_in_date,
                    check_out_date=check_out_date,
                    room_type=room_type
                )
                return Response({
                    "status": "success",
                    "message": "Booking created successfully.",
                    "booking_id": booking.id,
                    "room_id": booking.room.id
                }, status=status.HTTP_201_CREATED)
            except RoomNotAvailableForSelectedDatesException as e:
                return Response({
                    "status": "error",
                    "message": str(e)
                }, status=status.HTTP_409_CONFLICT)

        return Response({
            "status": "error",
            "message": "Validation error.",
            "detail": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def __init__(
            self,
            booking_service: Optional[BookingService] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.booking_service = booking_service or BookingService()

    @swagger_auto_schema(
        operation_description="Retrieve a specific booking by ID.",
        responses={
            200: BookingSerializer,
            404: "Booking not found",
            500: "Internal server error."
        }
    )
    def get(self, request, booking_id):
        booking = self.booking_service.get_booking_by_id(
            booking_id,
            request.user
        )
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update booking check-in or check-out dates with room type.",
        request_body=BookingUpdateSerializer,
        responses={
            200: "Booking modified successfully.",
            400: "Invalid modification",
            409: "Room unavailable for modified dates.",
            500: "Internal server error."
        }
    )
    def put(self, request, booking_id):
        serializer = BookingUpdateSerializer(data=request.data)
        if serializer.is_valid():
            new_check_in_date = serializer.validated_data['check_in_date']
            new_check_out_date = serializer.validated_data['check_out_date']
            room_type = serializer.validated_data['room_type']

            try:
                booking = self.booking_service.modify_booking(
                    booking_id=booking_id,
                    new_check_in_date=new_check_in_date,
                    new_check_out_date=new_check_out_date,
                    room_type=room_type
                )
                return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)
            except (InvalidBookingModificationException, RoomNotAvailableForSelectedDatesException) as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Cancel a booking by ID.",
        responses={
            204: "Booking canceled successfully.",
            403: "Unauthorized cancellation attempt.",
            400: "Booking already canceled.",
            500: "Internal server error."
        }
    )
    def delete(self, request, booking_id):
        try:
            self.booking_service.cancel_booking(booking_id, request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (UnauthorizedCancellationException, AlreadyCanceledException) as e:
            return Response({"error": str(e.detail)}, status=e.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfirmBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(
            self,
            booking_service: Optional[BookingService] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.booking_service = booking_service or BookingService()

    @swagger_auto_schema(
        operation_description="Confirm a pending booking.",
        responses={
            200: BookingSerializer,
            400: "Cannot confirm booking.",
            500: "Internal server error."
        }
    )
    def post(self, request, booking_id):
        try:
            booking = self.booking_service.confirm_booking(booking_id, request.user)
            serializer = BookingSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UnauthorizedOrInvalidBookingException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
