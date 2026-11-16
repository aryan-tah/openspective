"""Configuration, read from `OPENSPECTIVE_*` environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _keys(raw: str | None) -> frozenset[str]:
    return frozenset(k.strip() for k in (raw or "").split(",") if k.strip())


@dataclass(frozen=True)
class Settings:
    backend: str = "detoxify"
    """`detoxify` (real models) or `fake` (keyword matching, for tests)."""
    api_keys: frozenset[str] = field(default_factory=frozenset)
    """Accepted API keys. Empty means no key is required."""
    default_language: str | None = "en"
    """Language used when detection isn't confident. `None` returns Perspective's error instead."""
    max_comment_bytes: int = 20480
    feedback_path: str | None = None
    """Where `comments:suggestscore` appends feedback as JSON lines. Unset means it's discarded."""
    public_url: str | None = None
    """Base URL written into the discovery document. Defaults to the URL the request came in on."""

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Settings:
        e = os.environ if env is None else env
        default_language = e.get("OPENSPECTIVE_DEFAULT_LANGUAGE", "en").strip()
        return cls(
            backend=e.get("OPENSPECTIVE_BACKEND", "detoxify"),
            api_keys=_keys(e.get("OPENSPECTIVE_API_KEYS")),
            default_language=default_language or None,
            max_comment_bytes=int(e.get("OPENSPECTIVE_MAX_COMMENT_BYTES", "20480")),
            feedback_path=e.get("OPENSPECTIVE_FEEDBACK_PATH") or None,
            public_url=(e.get("OPENSPECTIVE_PUBLIC_URL") or "").rstrip("/") or None,
        )
