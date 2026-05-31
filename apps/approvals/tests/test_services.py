import pytest
from django.contrib.auth.models import Group

from apps.accounts.constants import GROUP_EMPLOYEE
from apps.approvals.services import (
    approve_request,
    reject_request,
)
from apps.audit.models import AuditAction, AuditLog
from apps.core.exceptions import PermissionDeniedError
from apps.requests.models import RequestStatus, RequestStatusHistory
from apps.requests.services import create_request, submit_request
from tests.factories import (
    DepartmentFactory,
    ManagerUserFactory,
    RequestCategoryFactory,
    UserFactory,
)


def _setup_employee(emp, dept, manager):
    group, _ = Group.objects.get_or_create(name=GROUP_EMPLOYEE)
    emp.groups.add(group)
    profile = emp.profile
    profile.department = dept
    profile.manager = manager
    profile.save()


@pytest.mark.django_db
def test_employee_cannot_approve_own_request():
    user = UserFactory()
    _setup_employee(user, DepartmentFactory(), None)
    cat = RequestCategoryFactory()
    req = create_request(user, title="T", description="D", category=cat, priority="LOW")
    submit_request(user, req)
    with pytest.raises(PermissionDeniedError):
        approve_request(user, req)


@pytest.mark.django_db
def test_manager_can_approve_team_request():
    dept = DepartmentFactory()
    mgr = ManagerUserFactory()
    mgr.profile.department = dept
    mgr.profile.save()
    emp = UserFactory()
    _setup_employee(emp, dept, mgr)
    cat = RequestCategoryFactory(
        requires_manager_approval=True, requires_ops_approval=False, requires_hr_approval=False
    )
    req = create_request(emp, title="T", description="D", category=cat, priority="LOW")
    submit_request(emp, req)
    approve_request(mgr, req)
    req.refresh_from_db()
    assert req.status in (
        RequestStatus.APPROVED,
        RequestStatus.OPS_PROCESSING,
        RequestStatus.IN_REVIEW,
    )


@pytest.mark.django_db
def test_manager_cannot_approve_other_department_request():
    dept1 = DepartmentFactory(name="Dept A")
    dept2 = DepartmentFactory(name="Dept B")
    mgr = ManagerUserFactory()
    mgr.profile.department = dept1
    mgr.profile.save()
    emp = UserFactory()
    _setup_employee(emp, dept2, None)
    cat = RequestCategoryFactory()
    req = create_request(emp, title="T", description="D", category=cat, priority="LOW")
    submit_request(emp, req)
    with pytest.raises(PermissionDeniedError):
        approve_request(mgr, req)


@pytest.mark.django_db
def test_reject_request_changes_status_to_rejected():
    dept = DepartmentFactory()
    mgr = ManagerUserFactory()
    mgr.profile.department = dept
    mgr.profile.save()
    emp = UserFactory()
    _setup_employee(emp, dept, mgr)
    cat = RequestCategoryFactory()
    req = create_request(emp, title="T", description="D", category=cat, priority="LOW")
    submit_request(emp, req)
    reject_request(mgr, req, comment="No")
    req.refresh_from_db()
    assert req.status == RequestStatus.REJECTED


@pytest.mark.django_db
def test_approve_request_creates_status_history():
    dept = DepartmentFactory()
    mgr = ManagerUserFactory()
    mgr.profile.department = dept
    mgr.profile.save()
    emp = UserFactory()
    _setup_employee(emp, dept, mgr)
    cat = RequestCategoryFactory(requires_ops_approval=False, requires_hr_approval=False)
    req = create_request(emp, title="T", description="D", category=cat, priority="LOW")
    submit_request(emp, req)
    approve_request(mgr, req)
    assert (
        RequestStatusHistory.objects.filter(request=req, to_status=RequestStatus.APPROVED).exists()
        or RequestStatusHistory.objects.filter(request=req).count() >= 2
    )


@pytest.mark.django_db
def test_approval_creates_audit_log():
    dept = DepartmentFactory()
    mgr = ManagerUserFactory()
    mgr.profile.department = dept
    mgr.profile.save()
    emp = UserFactory()
    _setup_employee(emp, dept, mgr)
    cat = RequestCategoryFactory(requires_ops_approval=False, requires_hr_approval=False)
    req = create_request(emp, title="T", description="D", category=cat, priority="LOW")
    submit_request(emp, req)
    approve_request(mgr, req)
    assert AuditLog.objects.filter(action=AuditAction.REQUEST_APPROVED).exists()
