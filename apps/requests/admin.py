from django.contrib import admin

from apps.requests.models import (
    Request,
    RequestAttachment,
    RequestCategory,
    RequestComment,
    RequestStatusHistory,
)


@admin.register(RequestCategory)
class RequestCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "requires_manager_approval",
        "requires_ops_approval",
        "requires_hr_approval",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = (
        "public_id",
        "title",
        "category",
        "requester",
        "status",
        "priority",
        "current_approver",
        "created_at",
    )
    list_filter = ("status", "priority", "category")
    search_fields = ("public_id", "title", "requester__email")
    raw_id_fields = ("requester", "current_approver", "department")
    date_hierarchy = "created_at"
    readonly_fields = ("public_id", "submitted_at", "resolved_at", "cancelled_at")


@admin.register(RequestComment)
class RequestCommentAdmin(admin.ModelAdmin):
    list_display = ("request", "author", "is_internal", "created_at")
    list_filter = ("is_internal",)
    search_fields = ("body", "request__public_id")
    raw_id_fields = ("request", "author")


@admin.register(RequestAttachment)
class RequestAttachmentAdmin(admin.ModelAdmin):
    list_display = ("request", "original_filename", "uploaded_by", "created_at")
    raw_id_fields = ("request", "uploaded_by")


@admin.register(RequestStatusHistory)
class RequestStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("request", "from_status", "to_status", "changed_by", "created_at")
    list_filter = ("to_status",)
    raw_id_fields = ("request", "changed_by")
    date_hierarchy = "created_at"
