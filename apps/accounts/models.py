from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.accounts.constants import (
    GROUP_ADMIN,
    GROUP_EMPLOYEE,
    GROUP_HR,
    GROUP_MANAGER,
    GROUP_OPS,
)
from apps.accounts.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def _in_group(self, name: str) -> bool:
        return self.groups.filter(name=name).exists()

    @property
    def is_admin_role(self) -> bool:
        return self.is_superuser or self._in_group(GROUP_ADMIN)

    @property
    def is_manager(self) -> bool:
        return self._in_group(GROUP_MANAGER)

    @property
    def is_employee(self) -> bool:
        return self._in_group(GROUP_EMPLOYEE)

    @property
    def is_ops(self) -> bool:
        return self._in_group(GROUP_OPS)

    @property
    def is_hr(self) -> bool:
        return self._in_group(GROUP_HR)


class EmploymentType(models.TextChoices):
    FULL_TIME = "FULL_TIME", "Full Time"
    PART_TIME = "PART_TIME", "Part Time"
    CONTRACTOR = "CONTRACTOR", "Contractor"
    INTERN = "INTERN", "Intern"


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    department = models.ForeignKey(
        "organization.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )
    team = models.ForeignKey(
        "organization.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="direct_reports",
    )
    job_title = models.CharField(max_length=200, blank=True)
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    start_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__email"]

    def __str__(self):
        return f"{self.user.email} profile"
