from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .models import Language, PublishingSlot


class ConfigError(ValueError):
    """Raised when required runtime configuration is invalid."""


DEFAULT_SLOTS = (
    PublishingSlot(Language.ENGLISH, "06:30", "Asia/Kolkata", "USA-focused", "english_us_morning"),
    PublishingSlot(Language.ENGLISH, "08:30", "Asia/Kolkata", "USA/global", "english_global_morning"),
    PublishingSlot(Language.HINDI, "13:30", "Asia/Kolkata", "India", "hindi_india_afternoon"),
    PublishingSlot(Language.HINDI, "19:30", "Asia/Kolkata", "India", "hindi_india_evening"),
)


@dataclass(frozen=True)
class AppConfig:
    data_dir: Path = Path("data")
    history_path: Path = Path("data/story_history.jsonl")
    output_dir: Path = Path("out")
    similarity_threshold: float = 0.72
    max_duration_seconds: int = 60
    min_duration_seconds: int = 15
    request_timeout_seconds: int = 60
    max_retries: int = 3
    youtube_privacy_status: str = "private"
    openai_model: str = "gpt-4o-mini"
    openai_api_url: str = "https://api.openai.com/v1/chat/completions"
    english_playlist: str = "English Animal Stories"
    hindi_playlist: str = "Hindi Animal Stories"
    publishing_slots: tuple[PublishingSlot, ...] = field(default_factory=lambda: DEFAULT_SLOTS)

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            data_dir=Path(os.getenv("PAWS_DATA_DIR", "data")),
            history_path=Path(os.getenv("PAWS_HISTORY_PATH", "data/story_history.jsonl")),
            output_dir=Path(os.getenv("PAWS_OUTPUT_DIR", "out")),
            similarity_threshold=float(os.getenv("PAWS_SIMILARITY_THRESHOLD", "0.72")),
            max_duration_seconds=int(os.getenv("PAWS_MAX_DURATION_SECONDS", "60")),
            min_duration_seconds=int(os.getenv("PAWS_MIN_DURATION_SECONDS", "15")),
            request_timeout_seconds=int(os.getenv("PAWS_REQUEST_TIMEOUT_SECONDS", "60")),
            max_retries=int(os.getenv("PAWS_MAX_RETRIES", "3")),
            youtube_privacy_status=os.getenv("YOUTUBE_PRIVACY_STATUS", "private"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_url=os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions"),
        )

    def validate(self, require_youtube: bool = False) -> None:
        if not 0 < self.similarity_threshold < 1:
            raise ConfigError("PAWS_SIMILARITY_THRESHOLD must be between 0 and 1.")
        if self.min_duration_seconds <= 0 or self.max_duration_seconds <= self.min_duration_seconds:
            raise ConfigError("Video duration limits are invalid.")
        if self.max_retries < 1:
            raise ConfigError("PAWS_MAX_RETRIES must be at least 1.")
        if not self.openai_model.strip():
            raise ConfigError("OPENAI_MODEL must not be empty.")
        if not self.openai_api_url.startswith("https://"):
            raise ConfigError("OPENAI_API_URL must be an HTTPS URL.")
        if require_youtube:
            missing = [name for name in ("YOUTUBE_CLIENT_SECRETS_JSON", "YOUTUBE_TOKEN_JSON") if not os.getenv(name)]
            if missing:
                raise ConfigError(f"Missing YouTube secret(s): {', '.join(missing)}")
