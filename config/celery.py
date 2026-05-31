import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("opsdesk")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "mark-overdue-requests": {
        "task": "apps.requests.tasks.mark_overdue_requests",
        "schedule": crontab(hour=8, minute=0),
    },
    "generate-weekly-report": {
        "task": "apps.reports.tasks.generate_weekly_report",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),
    },
    "cleanup-old-notifications": {
        "task": "apps.notifications.tasks.cleanup_old_notifications",
        "schedule": crontab(hour=2, minute=0),
    },
}
