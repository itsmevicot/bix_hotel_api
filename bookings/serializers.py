from rest_framework import serializers

from bookings.models import Booking
from rooms.serializers import RoomSerializer
from users.serializers import UserSerializer


class BookingSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)
    client = UserSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'client', 'room', 'check_in_date', 'check_out_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']


class BookingCreateSerializer(serializers.Serializer):
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()

    def validate(self, data):
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')

        if check_in_date >= check_out_date:
            raise serializers.ValidationError("Check-out date must be after check-in date.")
        return data
