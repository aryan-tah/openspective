"""Perspective's attribute names, and how they map to the attributes openspective scores."""

from __future__ import annotations

# The attributes a backend can score. Every name a client sends resolves to one of these,
# or to nothing (known to Perspective, not available here).
CORE = (
    "TOXICITY",
    "SEVERE_TOXICITY",
    "IDENTITY_ATTACK",
    "INSULT",
    "PROFANITY",
    "THREAT",
    "SEXUALLY_EXPLICIT",
)

_ALIASES: dict[str, str] = {
    **{f"{name}_EXPERIMENTAL": name for name in CORE},
    "TOXICITY_FAST": "TOXICITY",
}

# Attributes Perspective offered that no open model covers yet. Requesting one returns the
# same error Perspective returns for an unsupported language, so `dropUnsupportedAttributes`
# and existing error handling keep working.
UNAVAILABLE = frozenset(
    {
        "FLIRTATION",
        "ATTACK_ON_AUTHOR",
        "ATTACK_ON_COMMENTER",
        "INCOHERENT",
        "INFLAMMATORY",
        "LIKELY_TO_REJECT",
        "OBSCENE",
        "SPAM",
        "UNSUBSTANTIAL",
        "AFFINITY_EXPERIMENTAL",
        "ALIENATION_EXPERIMENTAL",
        "COMPASSION_EXPERIMENTAL",
        "CURIOSITY_EXPERIMENTAL",
        "FEARMONGERING_EXPERIMENTAL",
        "GENERALIZATION_EXPERIMENTAL",
        "MORAL_OUTRAGE_EXPERIMENTAL",
        "NUANCE_EXPERIMENTAL",
        "PERSONAL_STORY_EXPERIMENTAL",
        "REASONING_EXPERIMENTAL",
        "RESPECT_EXPERIMENTAL",
        "SCAPEGOATING_EXPERIMENTAL",
    }
)


class Unknown(Exception):
    """Not an attribute name Perspective ever accepted."""


def resolve(name: str) -> str | None:
    """The core attribute behind a requested name, `None` if it's a Perspective attribute
    openspective can't score, or `Unknown` if it isn't a Perspective attribute at all."""
    upper = name.upper()
    if upper in CORE:
        return upper
    if upper in _ALIASES:
        return _ALIASES[upper]
    if upper in UNAVAILABLE:
        return None
    raise Unknown(name)
