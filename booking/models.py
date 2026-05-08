from django.db import models
from django.utils import timezone
import uuid
from slots.models import Slot


class Booking(models.Model):
    """Model for managing bookings"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name='bookings')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Booking for {self.slot.name} by {self.name}"

    def save(self, *args, **kwargs):
        # Mark the slot as booked when a booking is made
        super().save(*args, **kwargs)
        self.slot.is_booked = True
        self.slot.save()

    def delete(self, *args, **kwargs):
        # Mark the slot as available when a booking is deleted
        slot = self.slot
        super().delete(*args, **kwargs)
        slot.is_booked = False
        slot.save()