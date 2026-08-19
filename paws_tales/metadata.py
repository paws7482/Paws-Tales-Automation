from __future__ import annotations

from .models import Language, StoryRecord


def build_metadata(record: StoryRecord) -> dict[str, object]:
    lang_label = "Hindi" if record.language is Language.HINDI else "English"
    tags = ["Paws and Tales", "animal story", "moral story", "YouTube Shorts", lang_label]
    tags.extend(record.animals)
    return {
        "title": f"{record.title} #Shorts",
        "description": f"An original {lang_label} animal story from Paws & Tales.\n\nMoral: {record.moral}\n\n#Shorts #AnimalStory #MoralStory",
        "tags": tags[:15],
        "keywords": tags,
        "playlist": record.playlist,
        "thumbnail_concept": f"Vertical close-up of {', '.join(record.animals)} at the story climax.",
        "altered_content_disclosure_required": True,
    }
