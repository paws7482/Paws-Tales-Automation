from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol

from .config import AppConfig, ConfigError
from .models import Language, StoryRecord
from .retry import RetryPolicy, run_with_retries


class StoryProvider(Protocol):
    def create_story(self, language: Language, previous: list[StoryRecord]) -> StoryRecord:
        """Create one complete, original story record."""


@dataclass(frozen=True)
class OpenAIStoryProvider:
    """Production story provider using OpenAI's Chat Completions-compatible HTTP API."""

    config: AppConfig
    model: str | None = None
    api_url: str | None = None

    def create_story(self, language: Language, previous: list[StoryRecord]) -> StoryRecord:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ConfigError("OPENAI_API_KEY is required for production story generation.")
        prompt = self._prompt(language, previous)
        payload = {
            "model": self.model or self.config.openai_model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "You create original, family-friendly YouTube Shorts animal stories only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.95,
        }
        response = self._post_json(payload, api_key)
        content = response["choices"][0]["message"]["content"]
        data = json.loads(content)
        return StoryRecord(
            language=language,
            title=str(data["title"]).strip(),
            script=str(data["script"]).strip(),
            animals=[str(item).strip() for item in data["animals"] if str(item).strip()],
            category=str(data["category"]).strip(),
            moral=str(data["moral"]).strip(),
            playlist=self.config.hindi_playlist if language is Language.HINDI else self.config.english_playlist,
        )

    def _post_json(self, payload: dict[str, object], api_key: str) -> dict[str, object]:
        body = json.dumps(payload).encode("utf-8")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        def request_once() -> dict[str, object]:
            request = urllib.request.Request(self.api_url or self.config.openai_api_url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(request, timeout=self.config.request_timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))

        try:
            return run_with_retries(
                request_once,
                RetryPolicy(attempts=self.config.max_retries),
                (urllib.error.HTTPError, urllib.error.URLError, TimeoutError),
                retryable_statuses={408, 409, 429, 500, 502, 503, 504},
                status_getter=lambda exc: exc.code if isinstance(exc, urllib.error.HTTPError) else 408,
            )
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"OpenAI story request failed with HTTP {exc.code}.") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError("OpenAI story request failed after retries.") from exc

    def _prompt(self, language: Language, previous: list[StoryRecord]) -> str:
        recent = [
            {"title": item.title, "animals": item.animals, "category": item.category, "moral": item.moral}
            for item in previous[-25:]
        ]
        language_name = "Hindi" if language is Language.HINDI else "English"
        return json.dumps(
            {
                "task": f"Create one genuinely original {language_name} YouTube Short story for Paws & Tales.",
                "requirements": [
                    "45-140 words",
                    "complete arc: beginning, conflict, development, climax, resolution",
                    "include exact phrase 'Moral of the Story:' before the moral",
                    "family friendly, no celebrities, no copyrighted characters",
                    "avoid similarity to recent stories",
                    "return valid JSON only with keys: title, script, animals, category, moral",
                ],
                "recent_stories_to_avoid": recent,
            },
            ensure_ascii=False,
        )
