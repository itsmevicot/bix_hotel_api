from rest_framework import serializers
from rooms.models import Room


class RoomSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Room
        fields = ['id', 'number', 'type', 'status', 'price', 'updated_at']
        read_only_fields = ['id', 'status', 'updated_at']
