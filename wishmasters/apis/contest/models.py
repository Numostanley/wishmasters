import uuid

from django.db import models
from django.conf import settings


class Competition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(null=True, upload_to="contest_image", blank=True)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2)
    max_players = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=400)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class PlayerEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    paid_entry_fee = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=255)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'competition')  # Prevent duplicate entries
        ordering = ['-joined_at']
