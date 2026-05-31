import factory
from django.contrib.auth.models import Group
from factory.django import DjangoModelFactory

from apps.accounts.constants import GROUP_EMPLOYEE, GROUP_MANAGER, GROUP_OPS
from apps.accounts.models import EmployeeProfile, User
from apps.organization.models import Department, Team


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@test.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "password123")


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department

    name = factory.Sequence(lambda n: f"Department {n}")


class TeamFactory(DjangoModelFactory):
    class Meta:
        model = Team

    name = factory.Sequence(lambda n: f"Team {n}")
    department = factory.SubFactory(DepartmentFactory)


class EmployeeProfileFactory(DjangoModelFactory):
    class Meta:
        model = EmployeeProfile
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory)
    department = factory.SubFactory(DepartmentFactory)
    team = factory.SubFactory(TeamFactory)


def _add_to_group(user, group_name):
    group, _ = Group.objects.get_or_create(name=group_name)
    user.groups.add(group)


class ManagerUserFactory(UserFactory):
    @factory.post_generation
    def groups(obj, create, extracted, **kwargs):
        if create:
            _add_to_group(obj, GROUP_MANAGER)
            EmployeeProfile.objects.get_or_create(user=obj)


class OpsUserFactory(UserFactory):
    @factory.post_generation
    def groups(obj, create, extracted, **kwargs):
        if create:
            _add_to_group(obj, GROUP_OPS)
            EmployeeProfile.objects.get_or_create(user=obj)


class EmployeeUserFactory(UserFactory):
    @factory.post_generation
    def groups(obj, create, extracted, **kwargs):
        if create:
            _add_to_group(obj, GROUP_EMPLOYEE)
            EmployeeProfile.objects.get_or_create(user=obj)
