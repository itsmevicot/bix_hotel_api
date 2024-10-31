from datetime import date, datetime
from rest_framework import serializers
from bookings.enums import BookingStatus
from bookings.models import Booking
from rooms.enums import RoomType
from rooms.serializers import RoomListSerializer
from users.serializers import UserSerializer

DATE_INPUT_FORMATS = ['%d/%m/%Y']


class BookingSerializer(serializers.ModelSerializer):
    room = RoomListSerializer(read_only=True)
    client = UserSerializer(read_only=True)
    check_in_date = serializers.DateField(input_formats=DATE_INPUT_FORMATS)
    check_out_date = serializers.DateField(input_formats=DATE_INPUT_FORMATS)

    class Meta:
        model = Booking
        fields = ['id', 'client', 'room', 'check_in_date', 'check_out_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']


class BookingCreateSerializer(serializers.Serializer):
    check_in_date = serializers.DateField(input_formats=DATE_INPUT_FORMATS)
    check_out_date = serializers.DateField(input_formats=DATE_INPUT_FORMATS)
    room_type = serializers.ChoiceField(choices=RoomType.choices(), required=True)

    def validate(self, data):
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')
        today = date.today()

        if check_in_date <= today:
            raise serializers.ValidationError("Check-in date must be in the future.")
        if check_out_date <= today:
            raise serializers.ValidationError("Check-out date must be in the future.")
        if check_in_date >= check_out_date:
            raise serializers.ValidationError("Check-out date must be after check-in date.")

        return data


class BookingFilterSerializer(serializers.Serializer):
    check_in_date = serializers.DateField(input_formats=DATE_INPUT_FORMATS, required=False)
    check_out_date = serializers.DateField(input_formats=DATE_INPUT_FORMATS, required=False)
    status = serializers.ChoiceField(choices=BookingStatus.choices(), required=False)
    room_type = serializers.ChoiceField(choices=RoomType.choices(), required=False)
    client_id = serializers.IntegerField(required=False)

    def validate(self, data):
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')

        if check_in_date and check_out_date and check_in_date >= check_out_date:
            raise serializers.ValidationError("Check-out date must be after check-in date.")

        return data
