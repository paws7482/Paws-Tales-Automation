from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from .config import AppConfig
from .history import StoryHistory
from .metadata import build_metadata
from .models import Language
from .llm import OpenAIStoryProvider
from .story import StoryGenerator, TemplateStoryProvider
from .validation import StoryValidator
from .media import RenderManifestBuilder

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Paws & Tales automation CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate-story", help="Generate and persist an original story draft")
    gen.add_argument("--language", choices=[item.value for item in Language], required=True)
    gen.add_argument("--manifest", action="store_true", help="Write a production manifest for media generation handoff")
    gen.add_argument("--template-provider", action="store_true", help="Use deterministic local provider for smoke tests only")
    sub.add_parser("validate-config", help="Validate local configuration")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = AppConfig.from_env()
    config.validate(require_youtube=False)
    if args.command == "validate-config":
        LOGGER.info("Configuration is valid")
        return 0
    history = StoryHistory(config.history_path)
    records = history.load()
    provider = TemplateStoryProvider(config) if args.template_provider else OpenAIStoryProvider(config)
    record = StoryGenerator(config, provider=provider).generate(Language(args.language), records)
    result = StoryValidator().validate(record)
    if not result.ok:
        raise SystemExit(f"Story validation failed: {result.errors}")
    history.append(record)
    metadata = build_metadata(record)
    if args.manifest:
        manifest = RenderManifestBuilder(config.output_dir).write_manifest(record, metadata)
        LOGGER.info("Wrote production manifest: %s", manifest)
    print(json.dumps({"story": record.to_dict(), "metadata": metadata}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
