"""Language detection for comments that don't say which language they're in."""

from __future__ import annotations

from collections.abc import Iterable

from py3langid.langid import MODEL_FILE, LanguageIdentifier

# Restricting the detector to languages people commonly comment in avoids confident
# nonsense on short text (Spanish detected as Occitan, French as Extremaduran).
DEFAULT_CANDIDATES = (
    "ar", "bg", "ca", "cs", "da", "de", "el", "en", "es", "fa", "fi", "fr", "he", "hi", "hr",
    "hu", "id", "it", "ja", "ko", "nl", "no", "pl", "pt", "ro", "ru", "sk", "sl", "sr", "sv",
    "th", "tl", "tr", "uk", "ur", "vi", "zh",
)  # fmt: skip


def normalize(code: str) -> str:
    """`en-US` → `en`, `zh_Hant` → `zh`, `PT` → `pt`."""
    return code.replace("_", "-").split("-")[0].strip().lower()


class LanguageDetector:
    def __init__(
        self,
        candidates: Iterable[str] = DEFAULT_CANDIDATES,
        *,
        min_confidence: float = 0.5,
        fallback: str | None = "en",
    ) -> None:
        self._identifier = LanguageIdentifier.from_model_file(MODEL_FILE, norm_probs=True)
        self._identifier.set_languages(sorted(set(candidates)))
        self.min_confidence = min_confidence
        self.fallback = fallback

    def detect(self, text: str) -> tuple[str | None, list[str]]:
        """The language to score `text` in, and every plausible language, most likely first.

        Returns `None` as the language when detection isn't confident and there's no fallback.
        """
        if not any(ch.isalpha() for ch in text):
            return self.fallback, []
        ranked = self._identifier.rank(text)
        plausible = [lang for lang, p in ranked if p >= 0.1][:3]
        best_lang, best_p = ranked[0]
        if best_p >= self.min_confidence:
            return best_lang, plausible or [best_lang]
        return self.fallback, plausible
