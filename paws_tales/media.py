from __future__ import annotations

import hashlib
from pathlib import Path

from .models import MediaAsset, StoryRecord, VideoPackage


def fingerprint_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class RenderManifestBuilder:
    """Creates a production handoff package for external AI media/rendering services."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def write_manifest(self, record: StoryRecord, metadata: dict[str, object]) -> Path:
        story_dir = self.output_dir / record.story_id
        story_dir.mkdir(parents=True, exist_ok=True)
        manifest = story_dir / "production_manifest.md"
        manifest.write_text(
            "\n".join([
                f"# {record.title}",
                f"Language: {record.language.value}",
                f"Animals: {', '.join(record.animals)}",
                f"Playlist: {record.playlist}",
                "",
                "## Script",
                record.script,
                "",
                "## Metadata",
                str(metadata),
            ]),
            encoding="utf-8",
        )
        return manifest

    def package_existing_assets(self, record: StoryRecord, video_path: Path, narration_path: Path, captions_path: Path | None, metadata: dict[str, object]) -> VideoPackage:
        return VideoPackage(record, MediaAsset(video_path, "video"), MediaAsset(narration_path, "narration"), MediaAsset(captions_path, "captions") if captions_path else None, metadata)
