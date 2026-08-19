from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import AppConfig
from .models import StoryRecord, VideoPackage
from .originality import check_originality


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: tuple[str, ...]


class StoryValidator:
    def validate(self, record: StoryRecord) -> ValidationResult:
        errors: list[str] = []
        if not record.title.strip():
            errors.append("missing title")
        if "Moral of the Story:" not in record.script:
            errors.append("missing explicit moral")
        if not record.animals:
            errors.append("missing animals")
        if len(record.script.split()) < 45:
            errors.append("story too short for complete short-form arc")
        return ValidationResult(not errors, tuple(errors))


class UploadValidator:
    def __init__(self, config: AppConfig):
        self.config = config

    def validate(self, package: VideoPackage, history: list[StoryRecord]) -> ValidationResult:
        errors: list[str] = []
        for asset_name, asset in (("video", package.video), ("narration", package.narration)):
            if not Path(asset.path).is_file() or Path(asset.path).stat().st_size == 0:
                errors.append(f"missing or empty {asset_name}")
        if package.captions and not Path(package.captions.path).is_file():
            errors.append("missing captions")
        for key in ("title", "description", "tags", "playlist"):
            if not package.metadata.get(key):
                errors.append(f"missing metadata {key}")
        originality = check_originality(package.story, [item for item in history if item.story_id != package.story.story_id], self.config.similarity_threshold)
        if not originality.is_original:
            errors.append(f"excessive similarity to {originality.matching_story_id}")
        return ValidationResult(not errors, tuple(errors))
