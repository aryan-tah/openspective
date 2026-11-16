"""Real-model tests. Run with `uv run pytest -m models` (downloads about 1.5 GB once)."""

from __future__ import annotations

import pytest

from openspective.backends.detoxify import DetoxifyBackend

pytestmark = pytest.mark.models

ALL = {"TOXICITY", "SEVERE_TOXICITY", "IDENTITY_ATTACK", "INSULT", "PROFANITY", "THREAT", "SEXUALLY_EXPLICIT"}


@pytest.fixture(scope="module")
def backend() -> DetoxifyBackend:
    return DetoxifyBackend()


def test_english_scores_every_attribute(backend: DetoxifyBackend) -> None:
    kind, rude = backend.score(["Thanks, this was really helpful.", "You are a pathetic idiot."], "en", ALL)
    assert set(kind) == ALL
    assert kind["TOXICITY"] < 0.1
    assert rude["TOXICITY"] > 0.8
    assert rude["INSULT"] > 0.8


def test_profanity_maps_to_obscene(backend: DetoxifyBackend) -> None:
    (row,) = backend.score(["This is fucking great"], "en", {"PROFANITY"})
    assert row["PROFANITY"] > 0.8


@pytest.mark.parametrize(
    ("language", "kind", "rude"),
    [
        ("es", "Gracias por tu ayuda.", "Eres un idiota de mierda."),
        ("fr", "Merci pour ton aide.", "Tu es un pauvre imbécile."),
    ],
)
def test_multilingual_toxicity(backend: DetoxifyBackend, language: str, kind: str, rude: str) -> None:
    low, high = backend.score([kind, rude], language, {"TOXICITY"})
    assert low["TOXICITY"] < 0.5 < high["TOXICITY"]


def test_long_comments_are_scored_in_windows(backend: DetoxifyBackend) -> None:
    filler = "The committee met on Tuesday to review the budget for next year. " * 120
    (row,) = backend.score([filler + "You are a pathetic idiot."], "en", {"TOXICITY"})
    assert row["TOXICITY"] > 0.5
