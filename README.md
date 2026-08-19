# Paws & Tales Automation

Paws & Tales is a production-oriented automation project for original, family-friendly YouTube Shorts built around animal storytelling in English and Hindi.

## Current capabilities

- Generates complete original story drafts through a production OpenAI provider with a beginning, conflict, development, climax, resolution, and `Moral of the Story`.
- Maintains persistent JSONL story history to reduce repetition and support future analytics.
- Validates story completeness, metadata, media presence, duplicate similarity, and upload readiness before publishing.
- Produces unique metadata for each Short, including title, description, tags, keywords, playlist, thumbnail concept, and AI/altered-content disclosure flag.
- Provides a real YouTube upload integration boundary that requires OAuth secrets and the YouTube optional dependency; uploads are blocked when secrets are absent.
- Includes a GitHub Actions workflow using UTC cron entries for the initial India-time publishing schedule.
- Provides reusable retry, scheduling, and analytics snapshot helpers for production pipeline stages.

## Initial publishing schedule

| IST time | UTC cron | Language | Audience |
| --- | --- | --- | --- |
| 06:30 | `0 1 * * *` | English | USA-focused |
| 08:30 | `0 3 * * *` | English | USA/global |
| 13:30 | `0 8 * * *` | Hindi | India |
| 19:30 | `0 14 * * *` | Hindi | India |

## Local usage

```bash
python -m paws_tales.cli validate-config
OPENAI_API_KEY=... python -m paws_tales.cli generate-story --language en --manifest
OPENAI_API_KEY=... python -m paws_tales.cli generate-story --language hi --manifest
python -m paws_tales.cli generate-story --language en --manifest --template-provider  # smoke test only
```

Generated history is written to `data/story_history.jsonl`. Production handoff manifests are written under `out/<story_id>/production_manifest.md`.

## Required secrets for YouTube uploads

Do not hard-code secrets. Configure these through environment variables or GitHub Secrets:

- `OPENAI_API_KEY`: Required for production story generation.
- `OPENAI_MODEL`: Optional story model override; defaults to `gpt-4o-mini`.
- `OPENAI_API_URL`: Optional HTTPS endpoint override for compatible chat-completions deployments.
- `YOUTUBE_CLIENT_SECRETS_JSON`: OAuth client configuration JSON.
- `YOUTUBE_TOKEN_JSON`: Authorized OAuth token JSON.
- `YOUTUBE_PRIVACY_STATUS`: Optional; defaults to `private`.

The upload integration intentionally fails closed if secrets or optional YouTube dependencies are missing.
