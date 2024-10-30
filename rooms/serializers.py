from rest_framework import serializers

from rooms.enums import RoomType
from rooms.models import Room


class RoomSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Room
        fields = ['id', 'number', 'type', 'status', 'price', 'updated_at']
        read_only_fields = ['id', 'status', 'updated_at']


class RoomAvailabilityFilterSerializer(serializers.Serializer):
    check_in_date = serializers.DateField(required=True, input_formats=['%d/%m/%Y'])
    check_out_date = serializers.DateField(required=True, input_formats=['%d/%m/%Y'])
    type = serializers.ChoiceField(choices=RoomType.choices(), required=False)
    price = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)

    def validate(self, data):
        if data['check_in_date'] >= data['check_out_date']:
            raise serializers.ValidationError("check_out_date must be after check_in_date.")
        return data
