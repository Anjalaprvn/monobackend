from rest_framework import serializers
from .models import Slot

class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = [
            'id',
            'name',
            'date',
            'start_time',
            'end_time',
            # 'status',      # optional if you add it in your model
            'booked_by',
                
            'is_booked',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class SlotCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new slots"""
    
    class Meta:
        model = Slot
        fields = [
            'name', 'description', 'start_time', 'end_time', 'date', 'status',
            'booked_by', 'notes'
        ]


# Response Serializers
class SlotListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    count = serializers.IntegerField()
    slots = SlotSerializer(many=True)


class SlotDetailResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    slot = SlotSerializer()


class SlotCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    slot = SlotSerializer()


class APIResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)