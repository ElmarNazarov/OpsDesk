from django.contrib import admin

from apps.approvals.models import ApprovalAction, ApprovalPolicy, ApprovalStep


@admin.register(ApprovalPolicy)
class ApprovalPolicyAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "requires_manager_approval",
        "requires_ops_approval",
        "requires_hr_approval",
        "is_active",
    )
    list_filter = ("is_active",)


@admin.register(ApprovalStep)
class ApprovalStepAdmin(admin.ModelAdmin):
    list_display = ("request", "step_order", "role_required", "approver", "status", "decided_at")
    list_filter = ("status", "role_required")
    raw_id_fields = ("request", "approver")


@admin.register(ApprovalAction)
class ApprovalActionAdmin(admin.ModelAdmin):
    list_display = ("request", "step", "actor", "action", "created_at")
    list_filter = ("action",)
    raw_id_fields = ("request", "step", "actor")
    date_hierarchy = "created_at"
