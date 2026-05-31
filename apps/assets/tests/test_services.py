import pytest
from django.contrib.auth.models import Group

from apps.accounts.constants import GROUP_EMPLOYEE
from apps.assets.models import AssetStatus
from apps.assets.services import assign_asset_to_employee, fulfill_equipment_request
from apps.audit.models import AuditAction, AuditLog
from apps.core.exceptions import InvalidStateError
from apps.requests.models import RequestStatus
from tests.factories import AssetFactory, RequestCategoryFactory, RequestFactory
from tests.factories.accounts import EmployeeProfileFactory, OpsUserFactory, UserFactory


@pytest.mark.django_db
def test_ops_can_fulfill_approved_equipment_request():
    ops = OpsUserFactory()
    emp = UserFactory()
    group, _ = Group.objects.get_or_create(name=GROUP_EMPLOYEE)
    emp.groups.add(group)
    EmployeeProfileFactory(user=emp)
    cat = RequestCategoryFactory(
        slug="equipment", requires_manager_approval=False, requires_ops_approval=False
    )
    req = RequestFactory(
        requester=emp,
        category=cat,
        status=RequestStatus.OPS_PROCESSING,
    )
    asset = AssetFactory(status=AssetStatus.AVAILABLE)
    fulfill_equipment_request(ops, req, asset)
    req.refresh_from_db()
    asset.refresh_from_db()
    assert req.status == RequestStatus.FULFILLED
    assert asset.status == AssetStatus.ASSIGNED


@pytest.mark.django_db
def test_asset_cannot_be_assigned_twice():
    ops = OpsUserFactory()
    emp = UserFactory()
    asset = AssetFactory(status=AssetStatus.AVAILABLE)
    assign_asset_to_employee(asset, emp, ops)
    with pytest.raises(InvalidStateError):
        assign_asset_to_employee(asset, emp, ops)


@pytest.mark.django_db
def test_asset_assignment_creates_audit_log():
    ops = OpsUserFactory()
    emp = UserFactory()
    asset = AssetFactory(status=AssetStatus.AVAILABLE)
    assign_asset_to_employee(asset, emp, ops)
    assert AuditLog.objects.filter(action=AuditAction.ASSET_ASSIGNED).exists()
