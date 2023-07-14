from rest_framework import serializers
from .models import Protocol
from attendants.models import Attendant


class ProtocolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Protocol
        attendant = serializers.PrimaryKeyRelatedField(queryset=Attendant.objects.all())
        fields = (
            "number_protocol",
            "number",
            "name",
            "attendant",
            "department",
            "start_date",
            "end_date",
            "handling_time",
            "tags",
            "waiting_time",
            "average_waiting_time",
            "protocol_type",
        )

