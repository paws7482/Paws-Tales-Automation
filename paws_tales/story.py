from __future__ import annotations

import random

from .config import AppConfig
from .models import Language, StoryRecord
from .llm import OpenAIStoryProvider, StoryProvider
from .originality import check_originality

ANIMALS = ["otter", "sparrow", "turtle", "fox", "elephant calf", "raccoon", "dolphin", "red panda", "camel", "firefly"]
SETTINGS = ["misty forest bridge", "desert well", "city rooftop garden", "snowy rescue trail", "moonlit mangrove", "farm after a storm"]
CONFLICTS = ["a lost map", "a broken promise", "a flooded path", "a missing bell", "a scary rumor", "a race that tempts cheating"]
MORALS_EN = ["Small courage can guide a whole community.", "Truth repairs trust faster than excuses.", "Teamwork turns a hard path into a shared victory."]
MORALS_HI = ["छोटी हिम्मत भी पूरे समूह को रास्ता दिखा सकती है।", "सच भरोसे को बहानों से जल्दी जोड़ता है।", "मिलकर काम करने से कठिन रास्ता भी आसान हो जाता है।"]


class StoryGenerationError(RuntimeError):
    pass


class StoryGenerator:
    def __init__(self, config: AppConfig, provider: StoryProvider | None = None):
        self.config = config
        self.provider = provider or OpenAIStoryProvider(config)

    def generate(self, language: Language, previous: list[StoryRecord]) -> StoryRecord:
        for _ in range(self.config.max_retries):
            record = self.provider.create_story(language, previous)
            if check_originality(record, previous, self.config.similarity_threshold).is_original:
                return record
        raise StoryGenerationError("Could not generate a sufficiently original story within retry limit.")


class TemplateStoryProvider:
    """Deterministic provider for tests and local smoke checks; production CLI uses OpenAIStoryProvider."""

    def __init__(self, config: AppConfig, rng: random.Random | None = None):
        self.config = config
        self.rng = rng or random.Random()

    def create_story(self, language: Language, previous: list[StoryRecord]) -> StoryRecord:
        _ = previous
        return self._draft(language)

    def _draft(self, language: Language) -> StoryRecord:
        animal = self.rng.choice(ANIMALS)
        helper = self.rng.choice([item for item in ANIMALS if item != animal])
        setting = self.rng.choice(SETTINGS)
        conflict = self.rng.choice(CONFLICTS)
        if language is Language.HINDI:
            moral = self.rng.choice(MORALS_HI)
            title = f"{animal.title()} और {helper.title()} की सच्ची मदद"
            script = (
                f"एक {setting} में {animal} को {conflict} के कारण सबके सामने मुश्किल दिखी। "
                f"शुरुआत में {helper} डर गया, लेकिन दोनों ने ध्यान से सुराग जोड़े। "
                f"तनाव तब बढ़ा जब समय खत्म होने लगा और बाकी जानवर उम्मीद छोड़ने लगे। "
                f"क्लाइमैक्स में {animal} ने अपनी गलती मानी और {helper} ने साहस दिखाकर रास्ता खोला। "
                f"अंत में पूरा जंगल सुरक्षित हुआ। Moral of the Story: {moral}"
            )
            playlist = self.config.hindi_playlist
            category = "Hindi animal moral story"
        else:
            moral = self.rng.choice(MORALS_EN)
            title = f"The {animal.title()} Who Listened First"
            script = (
                f"On a {setting}, a {animal} faced trouble because of {conflict}. "
                f"At first, a {helper} wanted to run away, but the two friends paused and listened. "
                f"The problem grew when the other animals started blaming one another. "
                f"At the climax, the {animal} admitted the missing clue and the {helper} used it to save the day. "
                f"By sunset, the group was safe and kinder than before. Moral of the Story: {moral}"
            )
            playlist = self.config.english_playlist
            category = "English animal moral story"
        return StoryRecord(language=language, title=title, script=script, animals=[animal, helper], category=category, moral=moral, playlist=playlist)
