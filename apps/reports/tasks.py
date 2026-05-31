import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def generate_weekly_report():
    from apps.reports.selectors import get_requests_by_status_chart

    data = get_requests_by_status_chart()
    logger.info("Weekly report generated: %s", data)
    return data
