from __future__ import annotations

from datetime import date, datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def month_bounds_utc(year: int, month: int) -> tuple[datetime, datetime]:
    if month < 1 or month > 12:
        raise ValueError("month must be 1..12")
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(year, month + 1, 1, tzinfo=timezone.utc)
    return start, end


def current_month_bounds_utc(now: datetime | None = None) -> tuple[datetime, datetime]:
    n = now or utc_now()
    return month_bounds_utc(n.year, n.month)


def parse_date_yyyy_mm_dd(value: str) -> date:
    return date.fromisoformat(value)
