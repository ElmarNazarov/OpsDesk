from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from apps.accounts.constants import ALL_GROUPS
from apps.accounts.models import EmployeeProfile, User


@receiver(post_migrate)
def create_role_groups(sender, **kwargs):
    if sender.name != "apps.accounts":
        return
    for name in ALL_GROUPS:
        Group.objects.get_or_create(name=name)


@receiver(post_save, sender=User)
def create_employee_profile(sender, instance, created, **kwargs):
    if created:
        EmployeeProfile.objects.get_or_create(user=instance)
