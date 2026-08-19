from __future__ import annotations

import re
from dataclasses import dataclass

from .models import StoryRecord

WORD_RE = re.compile(r"[\w']+", re.UNICODE)


@dataclass(frozen=True)
class OriginalityResult:
    is_original: bool
    max_similarity: float
    matching_story_id: str | None = None


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in WORD_RE.findall(text) if len(token) > 2}


def jaccard_similarity(left: str, right: str) -> float:
    a = tokenize(left)
    b = tokenize(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def check_originality(candidate: StoryRecord, previous: list[StoryRecord], threshold: float) -> OriginalityResult:
    max_score = 0.0
    match_id = None
    candidate_text = f"{candidate.title}\n{candidate.script}\n{candidate.moral}"
    for record in previous:
        score = jaccard_similarity(candidate_text, f"{record.title}\n{record.script}\n{record.moral}")
        if score > max_score:
            max_score = score
            match_id = record.story_id
    return OriginalityResult(max_score < threshold, max_score, match_id)
