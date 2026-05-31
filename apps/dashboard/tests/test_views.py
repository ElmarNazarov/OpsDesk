import pytest
from django.contrib.auth.models import Group
from django.urls import reverse

from apps.accounts.constants import GROUP_EMPLOYEE
from apps.approvals.selectors import get_pending_approvals_for_manager
from tests.factories import ManagerUserFactory, RequestFactory, UserFactory
from tests.factories.accounts import EmployeeProfileFactory


@pytest.mark.django_db
def test_login_required_for_dashboard(client):
    response = client.get(reverse("dashboard:employee"))
    assert response.status_code == 302
    assert "/accounts/login/" in response.url


@pytest.mark.django_db
def test_manager_sees_pending_approvals():
    mgr = ManagerUserFactory()
    emp = UserFactory()
    group, _ = Group.objects.get_or_create(name=GROUP_EMPLOYEE)
    emp.groups.add(group)
    EmployeeProfileFactory(user=emp, department=mgr.profile.department, manager=mgr)
    from tests.factories import RequestCategoryFactory

    cat = RequestCategoryFactory()
    RequestFactory(
        requester=emp,
        category=cat,
        status="IN_REVIEW",
        current_approver=mgr,
        department=mgr.profile.department,
    )
    pending = get_pending_approvals_for_manager(mgr)
    assert pending.count() >= 1
