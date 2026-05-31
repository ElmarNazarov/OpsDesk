from django import template

register = template.Library()

STATUS_BADGES = {
    "DRAFT": "secondary",
    "SUBMITTED": "primary",
    "IN_REVIEW": "info",
    "APPROVED": "success",
    "REJECTED": "danger",
    "OPS_PROCESSING": "warning",
    "FULFILLED": "success",
    "CANCELLED": "dark",
}

PRIORITY_BADGES = {
    "LOW": "secondary",
    "MEDIUM": "primary",
    "HIGH": "warning",
    "URGENT": "danger",
}


@register.filter
def status_badge(status):
    return STATUS_BADGES.get(status, "secondary")


@register.filter
def priority_badge(priority):
    return PRIORITY_BADGES.get(priority, "secondary")


@register.filter
def status_label(status):
    return status.replace("_", " ").title()
