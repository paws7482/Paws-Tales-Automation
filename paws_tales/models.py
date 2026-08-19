from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4


class Language(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"


class PublicationStatus(str, Enum):
    DRAFT = "draft"
    RENDERED = "rendered"
    VALIDATED = "validated"
    UPLOADED = "uploaded"
    FAILED = "failed"


@dataclass(frozen=True)
class PublishingSlot:
    language: Language
    local_time: str
    timezone: str
    audience: str
    label: str


@dataclass
class StoryRecord:
    language: Language
    title: str
    script: str
    animals: list[str]
    category: str
    moral: str
    playlist: str
    story_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    publication_status: PublicationStatus = PublicationStatus.DRAFT
    youtube_video_id: str | None = None
    scheduled_publish_time: str | None = None
    published_at: str | None = None
    upload_fingerprint: str | None = None
    performance_metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        data["language"] = self.language.value
        data["publication_status"] = self.publication_status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StoryRecord":
        payload = data.copy()
        payload["language"] = Language(payload["language"])
        payload["publication_status"] = PublicationStatus(payload.get("publication_status", "draft"))
        return cls(**payload)


@dataclass(frozen=True)
class MediaAsset:
    path: Path
    kind: str


@dataclass(frozen=True)
class VideoPackage:
    story: StoryRecord
    video: MediaAsset
    narration: MediaAsset
    captions: MediaAsset | None
    metadata: dict[str, Any]
