from rest_framework import serializers

from rooms.enums import RoomType, RoomStatus
from rooms.models import Room


class RoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['number', 'status', 'room_type', 'price']


class RoomUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['number', 'status', 'room_type', 'price']


class RoomListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing rooms without sensitive/internal fields.
    """
    room_type = serializers.CharField(source='get_room_type_display')
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Room
        fields = ['number', 'room_type', 'status', 'price']


class RoomDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed room information, used for retrieving a single room.
    """
    room_type = serializers.CharField(source='get_room_type_display')
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Room
        fields = ['id', 'number', 'room_type', 'status', 'price', 'updated_at']
        read_only_fields = ['id', 'status', 'updated_at']


class RoomAvailabilityFilterSerializer(serializers.Serializer):
    """
    Serializer for validating the input filters for checking room availability.
    """
    check_in_date = serializers.DateField(required=True, input_formats=['%d/%m/%Y'])
    check_out_date = serializers.DateField(required=True, input_formats=['%d/%m/%Y'])
    room_type = serializers.ChoiceField(choices=RoomType.choices(), required=False)
    price = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)

    def validate(self, data):
        if data['check_in_date'] >= data['check_out_date']:
            raise serializers.ValidationError("check_out_date must be after check_in_date.")
        return data


class RoomAvailabilitySerializer(serializers.Serializer):
    room_number = serializers.CharField(
        max_length=10,
        help_text="The room number to check availability for."
    )
    available = serializers.BooleanField(read_only=True)

    def validate_room_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Room number must be numeric.")
        return value


class RoomListFilterSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=RoomStatus.choices(), required=False)
    room_type = serializers.ChoiceField(choices=RoomType.choices(), required=False)
