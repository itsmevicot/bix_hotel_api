from typing import Optional

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.serializers import BookingSerializer, BookingCreateSerializer
from bookings.services import BookingService
from users.services.client_service import ClientService
from utils.exceptions import BookingCannotBeConfirmedException, UnauthorizedCancellationException, \
    RoomNotAvailableException


class ClientBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(
            self,
            client_service: Optional[ClientService] = None,
            booking_service: Optional[BookingService] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.service = client_service or ClientService()
        self.booking_service = booking_service or BookingService()

    @swagger_auto_schema(
        operation_description="Retrieve all bookings for the authenticated client.",
        responses={
            200: BookingSerializer(many=True),
            500: "An error occurred while retrieving bookings."
        }
    )
    def get(self, request):
        try:
            bookings = self.service.list_bookings(request.user)
            serializer = BookingSerializer(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"status": "error", "message": "An error occurred while retrieving bookings.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Create a new booking with the provided check-in and check-out dates.",
        request_body=BookingCreateSerializer,
        responses={
            201: "Booking created successfully.",
            400: "Validation error",
            409: "Room not available for booking in the selected dates.",
            500: "Internal server error."
        }
    )
    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        if serializer.is_valid():
            client = request.user
            check_in_date = serializer.validated_data['check_in_date']
            check_out_date = serializer.validated_data['check_out_date']

            try:
                booking = self.booking_service.create_booking(
                    client=client,
                    check_in_date=check_in_date,
                    check_out_date=check_out_date
                )
                return Response({
                    "status": "success",
                    "message": "Booking created successfully.",
                    "booking_id": booking.id,
                    "room_id": booking.room.id
                }, status=status.HTTP_201_CREATED)

            except RoomNotAvailableException as e:
                return Response({
                    "status": "error",
                    "message": str(e.message)
                }, status=e.status_code)

        return Response({
            "status": "error",
            "message": "Validation error.",
            "detail": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ConfirmBookingView(APIView):
    permission_classes = [IsAuthenticated]
    service = ClientService()

    @swagger_auto_schema(
        operation_description="Confirm a pending booking for the authenticated client.",
        responses={
            200: BookingSerializer,
            400: "Booking cannot be confirmed.",
            500: "Internal server error."
        }
    )
    def post(self, request, booking_id):
        try:
            booking = self.service.confirm_booking(booking_id, request.user)
            serializer = BookingSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BookingCannotBeConfirmedException as e:
            return Response(e.detail, status=e.status_code)
        except Exception as e:
            return Response(
                {"status": "error", "message": "An error occurred while confirming the booking.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]
    service = ClientService()

    @swagger_auto_schema(
        operation_description="Cancel a booking for the authenticated client.",
        responses={
            200: BookingSerializer,
            403: "Unauthorized cancellation attempt.",
            500: "Internal server error."
        }
    )
    def post(self, request, booking_id):
        try:
            booking = self.service.cancel_booking(booking_id, request.user)
            serializer = BookingSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UnauthorizedCancellationException as e:
            return Response(e.detail, status=e.status_code)
        except Exception as e:
            return Response(
                {"status": "error", "message": "An error occurred while cancelling the booking.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
