import pytest
from django.contrib.auth.models import Group

from apps.accounts.constants import GROUP_EMPLOYEE
from apps.notifications.models import Notification
from apps.requests.models import RequestStatus
from apps.requests.permissions import user_can_view_request
from apps.requests.selectors import get_requests_for_user
from apps.requests.services import create_request, submit_request
from tests.factories import (
    ManagerUserFactory,
    RequestCategoryFactory,
    RequestFactory,
    UserFactory,
)
from tests.factories.accounts import EmployeeProfileFactory


@pytest.mark.django_db
def test_employee_can_create_request():
    user = UserFactory()
    group, _ = Group.objects.get_or_create(name=GROUP_EMPLOYEE)
    user.groups.add(group)
    EmployeeProfileFactory(user=user)
    cat = RequestCategoryFactory()
    req = create_request(
        user,
        title="Vacation",
        description="Need time off",
        category=cat,
        priority="MEDIUM",
    )
    assert req.status == RequestStatus.DRAFT
    assert req.requester == user


@pytest.mark.django_db
def test_employee_can_submit_draft_request():
    user = UserFactory()
    group, _ = Group.objects.get_or_create(name=GROUP_EMPLOYEE)
    user.groups.add(group)
    mgr = ManagerUserFactory()
    profile = user.profile
    profile.manager = mgr
    profile.department = mgr.profile.department
    profile.save()
    cat = RequestCategoryFactory(requires_manager_approval=True)
    req = create_request(user, title="Test", description="Desc", category=cat, priority="LOW")
    submit_request(user, req)
    req.refresh_from_db()
    assert req.status in (RequestStatus.IN_REVIEW, RequestStatus.SUBMITTED)
    assert req.submitted_at is not None


@pytest.mark.django_db
def test_employee_cannot_view_other_employee_request():
    user1 = UserFactory()
    user2 = UserFactory()
    group, _ = Group.objects.get_or_create(name=GROUP_EMPLOYEE)
    user1.groups.add(group)
    user2.groups.add(group)
    EmployeeProfileFactory(user=user1)
    EmployeeProfileFactory(user=user2)
    cat = RequestCategoryFactory()
    req = RequestFactory(requester=user2, category=cat)
    assert user_can_view_request(user1, req) is False


@pytest.mark.django_db
def test_submission_creates_manager_notification():
    user = UserFactory()
    group, _ = Group.objects.get_or_create(name=GROUP_EMPLOYEE)
    user.groups.add(group)
    mgr = ManagerUserFactory()
    profile = user.profile
    profile.manager = mgr
    profile.department = mgr.profile.department
    profile.save()
    cat = RequestCategoryFactory(requires_manager_approval=True)
    req = create_request(user, title="T", description="D", category=cat, priority="LOW")
    submit_request(user, req)
    assert Notification.objects.filter(recipient=mgr).exists()


@pytest.mark.django_db
def test_employee_sees_only_own_requests():
    user1 = UserFactory()
    user2 = UserFactory()
    group, _ = Group.objects.get_or_create(name=GROUP_EMPLOYEE)
    user1.groups.add(group)
    user2.groups.add(group)
    EmployeeProfileFactory(user=user1)
    EmployeeProfileFactory(user=user2)
    cat = RequestCategoryFactory()
    RequestFactory(requester=user1, category=cat)
    RequestFactory(requester=user2, category=cat)
    qs = get_requests_for_user(user1)
    assert qs.count() == 1
    assert qs.first().requester == user1
