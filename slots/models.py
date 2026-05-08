from django.db import models
from django.utils import timezone
import uuid

class Slot(models.Model):
    """Model for managing time slots"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='available')  # available/booked
    name = models.CharField(max_length=100, default='Slot')
    booked_by = models.CharField(max_length=100, blank=True)  # Who booked this slot
    notes = models.TextField(blank=True)  # Any notes for the slot

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.date} {self.start_time}-{self.end_time}"
    
    class Meta:
        unique_together = ('date', 'start_time', 'end_time')
