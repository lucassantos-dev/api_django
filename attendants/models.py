from django.db import models

class Attendant(models.Model):
    """Representa um atendente no digisac."""
    name = models.CharField(max_length=255)
    class Meta:
        db_table = "attendant"

    def __str__(self):
        return self.name