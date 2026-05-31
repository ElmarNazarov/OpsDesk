from django.contrib import admin

from apps.organization.models import Department, Location, Team


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "manager", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "description")
    raw_id_fields = ("manager",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "lead", "created_at")
    list_filter = ("department",)
    search_fields = ("name",)
    raw_id_fields = ("lead",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "city", "timezone", "created_at")
    list_filter = ("country", "timezone")
    search_fields = ("name", "city", "country")
