"""Model backends: what scores text for each attribute and language."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol


class Backend(Protocol):
    """Scores texts for core attributes (see `openspective.attributes.CORE`)."""

    name: str

    def support(self) -> Mapping[str, frozenset[str]]:
        """Core attribute → languages it can be scored in."""
        ...

    def score(self, texts: Sequence[str], language: str, attributes: set[str]) -> list[dict[str, float]]:
        """One `{attribute: probability}` dict per text, for the requested attributes."""
        ...


def load(name: str) -> Backend:
    if name == "fake":
        from openspective.backends.fake import FakeBackend

        return FakeBackend()
    if name == "detoxify":
        from openspective.backends.detoxify import DetoxifyBackend

        backend: Backend = DetoxifyBackend()
        return backend
    raise ValueError(f"Unknown backend {name!r}. Choose 'detoxify' or 'fake'.")
