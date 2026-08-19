from __future__ import annotations

import random

import pytest

from paws_tales.config import AppConfig, ConfigError
from paws_tales.history import StoryHistory
from paws_tales.metadata import build_metadata
from paws_tales.models import Language, MediaAsset, VideoPackage
from paws_tales.originality import check_originality, jaccard_similarity
from paws_tales.story import StoryGenerator, TemplateStoryProvider
from paws_tales.validation import StoryValidator, UploadValidator


def test_generate_story_has_required_arc_and_metadata(tmp_path):
    config = AppConfig(data_dir=tmp_path, history_path=tmp_path / "history.jsonl", output_dir=tmp_path / "out")
    provider = TemplateStoryProvider(config, random.Random(7))
    story = StoryGenerator(config, provider=provider).generate(Language.ENGLISH, [])
    validation = StoryValidator().validate(story)
    metadata = build_metadata(story)
    assert validation.ok, validation.errors
    assert "Moral of the Story:" in story.script
    assert metadata["playlist"] == "English Animal Stories"
    assert metadata["altered_content_disclosure_required"] is True


def test_history_round_trip(tmp_path):
    history = StoryHistory(tmp_path / "history.jsonl")
    config = AppConfig(history_path=history.path)
    provider = TemplateStoryProvider(config, random.Random(2))
    story = StoryGenerator(config, provider=provider).generate(Language.HINDI, [])
    history.append(story)
    loaded = history.load()
    assert loaded[0].story_id == story.story_id
    assert loaded[0].language is Language.HINDI


def test_originality_detects_duplicates(tmp_path):
    config = AppConfig(history_path=tmp_path / "history.jsonl")
    provider = TemplateStoryProvider(config, random.Random(3))
    story = StoryGenerator(config, provider=provider).generate(Language.ENGLISH, [])
    result = check_originality(story, [story], threshold=0.72)
    assert not result.is_original
    assert result.max_similarity == pytest.approx(1.0)
    assert jaccard_similarity("brave otter", "brave otter") == pytest.approx(1.0)


def test_upload_validator_blocks_missing_media(tmp_path):
    config = AppConfig(history_path=tmp_path / "history.jsonl")
    provider = TemplateStoryProvider(config, random.Random(4))
    story = StoryGenerator(config, provider=provider).generate(Language.ENGLISH, [])
    package = VideoPackage(
        story=story,
        video=MediaAsset(tmp_path / "missing.mp4", "video"),
        narration=MediaAsset(tmp_path / "missing.wav", "narration"),
        captions=None,
        metadata=build_metadata(story),
    )
    result = UploadValidator(config).validate(package, [])
    assert not result.ok
    assert "missing or empty video" in result.errors
    assert "missing or empty narration" in result.errors


def test_config_requires_youtube_secrets(monkeypatch):
    monkeypatch.delenv("YOUTUBE_CLIENT_SECRETS_JSON", raising=False)
    monkeypatch.delenv("YOUTUBE_TOKEN_JSON", raising=False)
    with pytest.raises(ConfigError):
        AppConfig().validate(require_youtube=True)


def test_production_story_provider_requires_openai_key(monkeypatch):
    from paws_tales.llm import OpenAIStoryProvider

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        OpenAIStoryProvider(AppConfig()).create_story(Language.ENGLISH, [])
