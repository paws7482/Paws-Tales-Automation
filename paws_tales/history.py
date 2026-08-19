from __future__ import annotations

import json
from pathlib import Path

from .models import StoryRecord


class StoryHistory:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[StoryRecord]:
        if not self.path.exists():
            return []
        records: list[StoryRecord] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(StoryRecord.from_dict(json.loads(line)))
        return records

    def append(self, record: StoryRecord) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")

    def has_upload_fingerprint(self, fingerprint: str) -> bool:
        return any(record.upload_fingerprint == fingerprint for record in self.load())
