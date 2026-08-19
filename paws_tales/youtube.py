from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .config import AppConfig
from .media import fingerprint_file
from .models import VideoPackage


class DuplicateUploadError(RuntimeError):
    pass


class YouTubeUploader:
    def __init__(self, config: AppConfig):
        self.config = config

    def upload(self, package: VideoPackage, known_fingerprints: set[str]) -> str:
        self.config.validate(require_youtube=True)
        fingerprint = fingerprint_file(package.video.path)
        if fingerprint in known_fingerprints:
            raise DuplicateUploadError("Video fingerprint was already uploaded.")
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            from google.oauth2.credentials import Credentials
        except ImportError as exc:
            raise RuntimeError("Install the 'youtube' extra to enable YouTube uploads.") from exc

        credentials = Credentials.from_authorized_user_info(json.loads(os.environ["YOUTUBE_TOKEN_JSON"]))
        youtube = build("youtube", "v3", credentials=credentials)
        request_body: dict[str, Any] = {
            "snippet": {
                "title": package.metadata["title"],
                "description": package.metadata["description"],
                "tags": package.metadata["tags"],
                "categoryId": "15",
            },
            "status": {"privacyStatus": self.config.youtube_privacy_status, "selfDeclaredMadeForKids": False},
        }
        media = MediaFileUpload(str(Path(package.video.path)), chunksize=-1, resumable=True)
        response = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media).execute()
        return str(response["id"])
