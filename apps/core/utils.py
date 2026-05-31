from datetime import date, timedelta


def add_business_days(start_date: date, days: int) -> date:
    """Add business days (Mon-Fri) to a date."""
    current = start_date
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


def business_days_between(start_date: date, end_date: date) -> int:
    """Count business days between two dates (exclusive of end)."""
    if start_date >= end_date:
        return 0
    count = 0
    current = start_date
    while current < end_date:
        current += timedelta(days=1)
        if current.weekday() < 5:
            count += 1
    return count
