import contextlib
import random

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.accounts.constants import (
    GROUP_ADMIN,
    GROUP_EMPLOYEE,
    GROUP_HR,
    GROUP_MANAGER,
    GROUP_OPS,
)
from apps.accounts.models import EmployeeProfile, User
from apps.approvals.services import approve_request
from apps.assets.constants import DEFAULT_ASSET_CATEGORIES
from apps.assets.models import Asset, AssetCategory, AssetStatus
from apps.audit.models import AuditAction
from apps.audit.services import audit_log
from apps.notifications.models import Notification, NotificationType
from apps.notifications.services import create_notification
from apps.organization.models import Department, Location, Team
from apps.requests.constants import DEFAULT_CATEGORIES
from apps.requests.models import Request, RequestCategory, RequestPriority, RequestStatus
from apps.requests.services import create_request, submit_request


class Command(BaseCommand):
    help = "Seed demo data for OpsDesk"

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Delete existing demo data first")

    def handle(self, *args, **options):
        if options["flush"]:
            self._flush()
        self._ensure_groups()
        loc = self._create_locations()
        depts, teams = self._create_org()
        self._create_categories()
        self._create_asset_categories()
        users = self._create_users(depts, teams)
        self._create_assets(loc, users["ops"])
        self._create_requests(users, depts)
        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write("Demo users (password: password123):")
        for email in [
            "admin@opsdesk.local",
            "ops@opsdesk.local",
            "manager@opsdesk.local",
            "employee@opsdesk.local",
        ]:
            self.stdout.write(f"  - {email}")

    def _flush(self):
        Request.objects.all().delete()
        RequestCategory.objects.all().delete()
        Asset.objects.all().delete()
        AssetCategory.objects.all().delete()
        EmployeeProfile.objects.all().delete()
        User.objects.filter(email__endswith="@opsdesk.local").delete()
        Team.objects.all().delete()
        Department.objects.all().delete()
        Location.objects.all().delete()
        Notification.objects.all().delete()

    def _ensure_groups(self):
        for name in [GROUP_ADMIN, GROUP_MANAGER, GROUP_EMPLOYEE, GROUP_OPS, GROUP_HR]:
            Group.objects.get_or_create(name=name)

    def _create_locations(self):
        loc, _ = Location.objects.get_or_create(
            name="HQ",
            defaults={
                "country": "USA",
                "city": "New York",
                "address": "100 Main St",
                "timezone": "America/New_York",
            },
        )
        return loc

    def _create_org(self):
        depts = []
        for name in ["Engineering", "Operations", "Human Resources"]:
            d, _ = Department.objects.get_or_create(
                name=name, defaults={"description": f"{name} dept"}
            )
            depts.append(d)
        teams = []
        team_names = [
            ("Platform", depts[0]),
            ("Backend", depts[0]),
            ("DevOps", depts[1]),
            ("Support", depts[1]),
            ("People Ops", depts[2]),
        ]
        for tname, dept in team_names:
            t, _ = Team.objects.get_or_create(name=tname, department=dept)
            teams.append(t)
        return depts, teams

    def _create_categories(self):
        for cat in DEFAULT_CATEGORIES:
            RequestCategory.objects.get_or_create(slug=cat["slug"], defaults=cat)

    def _create_asset_categories(self):
        for name in DEFAULT_ASSET_CATEGORIES:
            AssetCategory.objects.get_or_create(name=name)

    def _create_user(self, email, first, last, group_name, dept=None, team=None, manager=None):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"first_name": first, "last_name": last, "is_active": True},
        )
        if created:
            user.set_password("password123")
            user.save()
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        profile, _ = EmployeeProfile.objects.get_or_create(user=user)
        if dept:
            profile.department = dept
        if team:
            profile.team = team
        if manager:
            profile.manager = manager
        profile.job_title = group_name
        profile.save()
        return user

    def _create_users(self, depts, teams):
        admin = self._create_user("admin@opsdesk.local", "Admin", "User", GROUP_ADMIN, depts[0])
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        ops = self._create_user("ops@opsdesk.local", "Ops", "User", GROUP_OPS, depts[1], teams[2])
        mgr1 = self._create_user(
            "manager@opsdesk.local", "Manager", "One", GROUP_MANAGER, depts[0], teams[0]
        )
        mgr2 = self._create_user(
            "manager2@opsdesk.local", "Manager", "Two", GROUP_MANAGER, depts[1], teams[2]
        )
        depts[0].manager = mgr1
        depts[0].save()
        depts[1].manager = mgr2
        depts[1].save()
        teams[0].lead = mgr1
        teams[0].save()
        employee = self._create_user(
            "employee@opsdesk.local",
            "Employee",
            "Demo",
            GROUP_EMPLOYEE,
            depts[0],
            teams[0],
            mgr1,
        )
        employees = [employee]
        for i in range(2, 9):
            emp = self._create_user(
                f"employee{i}@opsdesk.local",
                f"Employee{i}",
                "User",
                GROUP_EMPLOYEE,
                depts[i % 3],
                teams[i % 5],
                mgr1 if i % 2 == 0 else mgr2,
            )
            employees.append(emp)
        hr = self._create_user("hr@opsdesk.local", "HR", "User", GROUP_HR, depts[2], teams[4])
        return {
            "admin": admin,
            "ops": ops,
            "mgr1": mgr1,
            "mgr2": mgr2,
            "employee": employee,
            "employees": employees,
            "hr": hr,
        }

    def _create_assets(self, location, ops_user):
        cats = list(AssetCategory.objects.all())
        for i in range(10):
            Asset.objects.get_or_create(
                serial_number=f"SN-{1000 + i}",
                defaults={
                    "name": f"Asset {i + 1}",
                    "category": cats[i % len(cats)],
                    "status": AssetStatus.AVAILABLE,
                    "location": location,
                },
            )

    def _create_requests(self, users, depts):
        categories = list(RequestCategory.objects.all())
        statuses = [
            RequestStatus.DRAFT,
            RequestStatus.IN_REVIEW,
            RequestStatus.APPROVED,
            RequestStatus.OPS_PROCESSING,
            RequestStatus.FULFILLED,
            RequestStatus.REJECTED,
        ]
        for i in range(20):
            requester = random.choice(users["employees"])
            cat = random.choice(categories)
            req = create_request(
                requester,
                title=f"Sample request {i + 1}",
                description=f"Description for request {i + 1}",
                category=cat,
                priority=random.choice(list(RequestPriority.values)),
            )
            target_status = statuses[i % len(statuses)]
            if target_status != RequestStatus.DRAFT:
                submit_request(requester, req)
            if (
                target_status
                in (
                    RequestStatus.APPROVED,
                    RequestStatus.OPS_PROCESSING,
                    RequestStatus.FULFILLED,
                )
                and req.status == RequestStatus.IN_REVIEW
                and users["mgr1"]
            ):
                with contextlib.suppress(Exception):
                    approve_request(users["mgr1"], req, comment="Approved in seed")
            if target_status == RequestStatus.REJECTED and req.status == RequestStatus.IN_REVIEW:
                from apps.approvals.services import reject_request

                with contextlib.suppress(Exception):
                    reject_request(users["mgr1"], req, comment="Rejected in seed")
            audit_log(users["admin"], AuditAction.REQUEST_CREATED, entity=req)
        create_notification(
            users["employee"],
            "Welcome to OpsDesk",
            "Your demo account is ready.",
            NotificationType.REQUEST_SUBMITTED,
        )
