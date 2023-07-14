from django.db import models
from attendants.models import Attendant


class Protocol(models.Model):
    """Representa um protocolo no digisac."""
    number_protocol = models.CharField(max_length=255, primary_key=True)
    number = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    attendant = models.ForeignKey(
        Attendant, on_delete=models.CASCADE, related_name="protocols"
    )
    department = models.CharField(max_length=255)
    start_date = models.CharField(max_length=255)
    end_date = models.CharField(max_length=255)
    handling_time = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    waiting_time = models.CharField(max_length=255)
    average_waiting_time = models.CharField(max_length=255)
    protocol_type = models.CharField(max_length=255)

    def __str__(self):
        return self.number_protocol

    class Meta:
        db_table = "protocols"