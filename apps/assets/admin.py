from django.contrib import admin

from apps.assets.models import Asset, AssetAssignment, AssetCategory


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("name", "serial_number", "category", "status", "assigned_to", "location")
    list_filter = ("status", "category")
    search_fields = ("name", "serial_number")
    raw_id_fields = ("assigned_to",)


@admin.register(AssetAssignment)
class AssetAssignmentAdmin(admin.ModelAdmin):
    list_display = ("asset", "employee", "assigned_by", "assigned_at", "returned_at")
    list_filter = ("assigned_at",)
    raw_id_fields = ("asset", "employee", "assigned_by", "related_request")
