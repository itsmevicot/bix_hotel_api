from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.serializers import BookingSerializer
from users.services import ClientService
from utils.exceptions import BookingCannotBeConfirmedException, UnauthorizedCancellationException


class ClientBookingsView(APIView):
    permission_classes = [IsAuthenticated]
    service = ClientService()

    def get(self, request):
        bookings = self.service.list_bookings(request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ConfirmBookingView(APIView):
    permission_classes = [IsAuthenticated]
    service = ClientService()

    def post(self, request, booking_id):
        try:
            booking = self.service.confirm_booking(booking_id, request.user)
            serializer = BookingSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BookingCannotBeConfirmedException as e:
            return Response(e.detail, status=e.status_code)
        except Exception as e:
            return Response(
                {"title": "Error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]
    service = ClientService()

    def post(self, request, booking_id):
        try:
            booking = self.service.cancel_booking(booking_id, request.user)
            serializer = BookingSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UnauthorizedCancellationException as e:
            return Response(e.detail, status=e.status_code)
        except Exception as e:
            return Response(
                {"title": "Error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
