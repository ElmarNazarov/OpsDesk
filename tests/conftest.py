import pytest

from tests.factories import (
    DepartmentFactory,
    EmployeeProfileFactory,
    ManagerUserFactory,
    OpsUserFactory,
    RequestCategoryFactory,
    RequestFactory,
    TeamFactory,
    UserFactory,
)


@pytest.fixture
def employee_user(db):
    user = UserFactory()
    EmployeeProfileFactory(user=user)
    return user


@pytest.fixture
def manager_user(db):
    return ManagerUserFactory()


@pytest.fixture
def ops_user(db):
    return OpsUserFactory()


@pytest.fixture
def department(db):
    return DepartmentFactory()


@pytest.fixture
def team(db, department):
    return TeamFactory(department=department)


@pytest.fixture
def category(db):
    return RequestCategoryFactory()


@pytest.fixture
def draft_request(db, employee_user, category):
    return RequestFactory(
        requester=employee_user,
        category=category,
        status="DRAFT",
    )
