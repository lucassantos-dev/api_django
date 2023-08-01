from django.db import models
from attendants.models import Attendant


class Protocol(models.Model):
    """Representa um protocolo no digisac."""
    protocol_number = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    number = models.CharField(max_length=100)
    attendant = models.ForeignKey(Attendant, on_delete=models.SET_NULL, null=True)
    tags = models.CharField(max_length=255)
    department = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    total_attendance_time = models.DurationField()
    first_waiting_time = models.DurationField(null=True, blank=True)
    average_waiting_time = models.DurationField(null=True, blank=True)
    call_type = models.CharField(max_length=50)

    def __str__(self):
        return self.number_protocol

    class Meta:
        db_table = "protocols"