from django.conf import settings
from django.db import models


class AuditAction(models.TextChoices):
    REQUEST_CREATED = "request.created", "Request Created"
    REQUEST_SUBMITTED = "request.submitted", "Request Submitted"
    REQUEST_APPROVED = "request.approved", "Request Approved"
    REQUEST_REJECTED = "request.rejected", "Request Rejected"
    REQUEST_CANCELLED = "request.cancelled", "Request Cancelled"
    REQUEST_FULFILLED = "request.fulfilled", "Request Fulfilled"
    ASSET_ASSIGNED = "asset.assigned", "Asset Assigned"
    ASSET_RETURNED = "asset.returned", "Asset Returned"
    USER_ROLE_CHANGED = "user.role_changed", "User Role Changed"
    NOTIFICATION_CREATED = "notification.created", "Notification Created"


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50, choices=AuditAction.choices)
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} by {self.actor_id} at {self.created_at}"
