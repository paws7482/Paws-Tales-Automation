from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .models import StoryRecord


@dataclass(frozen=True)
class PerformanceSnapshot:
    story_id: str
    captured_at: str
    views: int = 0
    average_view_duration_seconds: float = 0.0
    percentage_viewed: float = 0.0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    subscribers_gained: int = 0
    countries: tuple[str, ...] = ()

    @classmethod
    def from_youtube_metrics(cls, story_id: str, metrics: dict[str, Any]) -> "PerformanceSnapshot":
        return cls(
            story_id=story_id,
            captured_at=datetime.now(timezone.utc).isoformat(),
            views=int(metrics.get("views", 0)),
            average_view_duration_seconds=float(metrics.get("average_view_duration_seconds", 0.0)),
            percentage_viewed=float(metrics.get("percentage_viewed", 0.0)),
            likes=int(metrics.get("likes", 0)),
            comments=int(metrics.get("comments", 0)),
            shares=int(metrics.get("shares", 0)),
            subscribers_gained=int(metrics.get("subscribers_gained", 0)),
            countries=tuple(metrics.get("countries", ())),
        )

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


def attach_snapshot(record: StoryRecord, snapshot: PerformanceSnapshot) -> StoryRecord:
    record.performance_metrics[snapshot.captured_at] = snapshot.to_dict()
    return record
