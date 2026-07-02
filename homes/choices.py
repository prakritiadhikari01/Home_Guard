from django import models


class MemberStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACTIVE = "active", "Active"
    REJECTED = "rejected", "Rejected"