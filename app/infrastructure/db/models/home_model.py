#app/infrastructure/db/models/home_model.py
import uuid

from django.conf import settings
from django.db import models


class Home(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(max_length=255)

    address = models.TextField()

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_homes",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "homes"

    def __str__(self):
        return self.name