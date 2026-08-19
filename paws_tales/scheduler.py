from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .models import PublishingSlot


def next_publish_time(slot: PublishingSlot, now: datetime | None = None) -> datetime:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    local_zone = ZoneInfo(slot.timezone)
    local_now = current.astimezone(local_zone)
    hour, minute = [int(part) for part in slot.local_time.split(":", maxsplit=1)]
    candidate = local_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= local_now:
        candidate = candidate + timedelta(days=1)
    return candidate.astimezone(timezone.utc)


def cron_minute_hour_for_slot(slot: PublishingSlot) -> tuple[int, int]:
    reference = datetime(2026, 1, 1, tzinfo=timezone.utc)
    scheduled = next_publish_time(slot, reference)
    return scheduled.minute, scheduled.hour
