from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Department(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_departments",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Team(TimeStampedModel):
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="teams")
    lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_teams",
    )

    class Meta:
        ordering = ["department__name", "name"]
        unique_together = [["name", "department"]]

    def __str__(self):
        return f"{self.name} ({self.department.name})"


class Location(TimeStampedModel):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    timezone = models.CharField(max_length=50, default="UTC")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
