from django.conf import settings
from django.db import models

from apps.accounts.constants import GROUP_HR, GROUP_MANAGER, GROUP_OPS
from apps.core.models import TimeStampedModel


class ApprovalPolicy(TimeStampedModel):
    category = models.OneToOneField(
        "requests.RequestCategory",
        on_delete=models.CASCADE,
        related_name="approval_policy",
    )
    requires_manager_approval = models.BooleanField(default=True)
    requires_ops_approval = models.BooleanField(default=False)
    requires_hr_approval = models.BooleanField(default=False)
    min_priority_for_extra_approval = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Policy for {self.category.name}"


class ApprovalStepStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    SKIPPED = "SKIPPED", "Skipped"


class RoleRequired(models.TextChoices):
    MANAGER = GROUP_MANAGER, "Manager"
    OPS = GROUP_OPS, "Ops"
    HR = GROUP_HR, "HR"


class ApprovalStep(TimeStampedModel):
    request = models.ForeignKey(
        "requests.Request", on_delete=models.CASCADE, related_name="approval_steps"
    )
    step_order = models.PositiveIntegerField()
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_steps",
    )
    role_required = models.CharField(max_length=20, choices=RoleRequired.choices)
    status = models.CharField(
        max_length=10,
        choices=ApprovalStepStatus.choices,
        default=ApprovalStepStatus.PENDING,
    )
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["step_order"]
        unique_together = [["request", "step_order"]]

    def __str__(self):
        return f"Step {self.step_order} for {self.request.public_id}"


class ApprovalActionType(models.TextChoices):
    APPROVE = "APPROVE", "Approve"
    REJECT = "REJECT", "Reject"
    RETURN_FOR_CHANGES = "RETURN_FOR_CHANGES", "Return for Changes"
    CANCEL = "CANCEL", "Cancel"
    FULFILL = "FULFILL", "Fulfill"


class ApprovalAction(models.Model):
    request = models.ForeignKey(
        "requests.Request", on_delete=models.CASCADE, related_name="approval_actions"
    )
    step = models.ForeignKey(ApprovalStep, on_delete=models.CASCADE, related_name="actions")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="approval_actions_taken",
    )
    action = models.CharField(max_length=30, choices=ApprovalActionType.choices)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} on {self.request.public_id}"
