from typing import Optional

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.models import Booking
from checkins.services import CheckInCheckOutService
from checkins.enums import CheckInStatus, CheckOutStatus
from utils.exceptions import (
    AlreadyCheckedInException,
    InvalidBookingStatusException,
    AlreadyCheckedOutException
)


class CheckInView(APIView):

    def __init__(
            self,
            check_in_out_service: Optional[CheckInCheckOutService] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.check_in_out_service = check_in_out_service or CheckInCheckOutService()

    def post(self, request, booking_id):
        try:
            result = self.check_in_out_service.perform_check_in(booking_id)
            if result == CheckInStatus.COMPLETED:
                return Response({"message": "Checked in successfully."}, status=status.HTTP_200_OK)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        except InvalidBookingStatusException as e:
            return Response({"error": e.message}, status=e.status_code)
        except AlreadyCheckedInException as e:
            return Response({"error": e.message}, status=e.status_code)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {e} "},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckOutView(APIView):

    def __init__(
            self,
            check_in_out_service: Optional[CheckInCheckOutService] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.check_in_out_service = check_in_out_service or CheckInCheckOutService()

    def post(self, request, booking_id):
        try:
            result = self.check_in_out_service.perform_check_out(booking_id)
            if result == CheckOutStatus.COMPLETED:
                return Response({"message": "Checked out successfully."}, status=status.HTTP_200_OK)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        except InvalidBookingStatusException as e:
            return Response({"error": e.message}, status=e.status_code)
        except AlreadyCheckedOutException as e:
            return Response({"error": e.message}, status=e.status_code)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {e}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
