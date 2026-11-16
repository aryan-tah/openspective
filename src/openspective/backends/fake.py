"""A keyword-based backend for tests and demos. It needs no model download."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from openspective.attributes import CORE

_WORDS: dict[str, tuple[str, ...]] = {
    "TOXICITY": ("idiot", "stupid", "hate", "kill", "damn", "mierda", "idiota", "imbécile"),
    "SEVERE_TOXICITY": ("kill",),
    "IDENTITY_ATTACK": ("those people",),
    "INSULT": ("idiot", "stupid", "idiota", "imbécile"),
    "PROFANITY": ("damn", "mierda"),
    "THREAT": ("kill",),
    "SEXUALLY_EXPLICIT": ("explicit",),
}


class FakeBackend:
    name = "fake"

    def support(self) -> Mapping[str, frozenset[str]]:
        multi = frozenset({"en", "es", "fr"})
        return {attr: (multi if attr == "TOXICITY" else frozenset({"en"})) for attr in CORE}

    def score(self, texts: Sequence[str], language: str, attributes: set[str]) -> list[dict[str, float]]:
        out = []
        for text in texts:
            lower = text.lower()
            out.append({attr: 0.92 if any(w in lower for w in _WORDS[attr]) else 0.04 for attr in attributes})
        return out
