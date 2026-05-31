from django.conf import settings
from django.db import models


class NotificationType(models.TextChoices):
    REQUEST_SUBMITTED = "REQUEST_SUBMITTED", "Request Submitted"
    REQUEST_APPROVED = "REQUEST_APPROVED", "Request Approved"
    REQUEST_REJECTED = "REQUEST_REJECTED", "Request Rejected"
    REQUEST_COMMENTED = "REQUEST_COMMENTED", "Request Commented"
    REQUEST_FULFILLED = "REQUEST_FULFILLED", "Request Fulfilled"
    MANAGER_ACTION_REQUIRED = "MANAGER_ACTION_REQUIRED", "Manager Action Required"
    OPS_ACTION_REQUIRED = "OPS_ACTION_REQUIRED", "Ops Action Required"


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=300)
    message = models.TextField()
    type = models.CharField(max_length=30, choices=NotificationType.choices)
    is_read = models.BooleanField(default=False)
    related_request = models.ForeignKey(
        "requests.Request",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} -> {self.recipient.email}"
