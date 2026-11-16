"""The Perspective API's behaviour, independent of HTTP."""

from __future__ import annotations

import json
import threading
import time
from collections.abc import Mapping

from openspective import attributes, errors
from openspective.backends import Backend
from openspective.language import LanguageDetector, normalize
from openspective.schema import (
    AnalyzeCommentRequest,
    AnalyzeCommentResponse,
    AttributeScores,
    Score,
    SpanScore,
    SuggestCommentScoreRequest,
    SuggestCommentScoreResponse,
)
from openspective.spans import sentences, utf16_offsets

_SCORE_TYPES = {None, "", "PROBABILITY", "SCORE_TYPE_UNSPECIFIED"}


class Analyzer:
    def __init__(
        self,
        backend: Backend,
        detector: LanguageDetector,
        *,
        max_comment_bytes: int = 20480,
        feedback_path: str | None = None,
    ) -> None:
        self.backend = backend
        self.detector = detector
        self.max_comment_bytes = max_comment_bytes
        self.feedback_path = feedback_path
        self._support = backend.support()
        self._feedback_lock = threading.Lock()

    @property
    def support(self) -> Mapping[str, frozenset[str]]:
        return self._support

    def _text(self, text: str | None) -> str:
        if text is None or not text.strip():
            raise errors.comment_empty()
        size = len(text.encode("utf-8"))
        if size > self.max_comment_bytes:
            raise errors.comment_too_long(size, self.max_comment_bytes)
        return text

    def _languages(self, text: str, requested: list[str] | None) -> tuple[str, list[str], list[str] | None]:
        """(language to score in, languages to report, detected languages or None)."""
        if requested:
            return normalize(requested[0]), requested, None
        language, detected = self.detector.detect(text)
        if language is None:
            raise errors.language_detection_failed()
        return language, [language], detected or [language]

    def analyze(self, req: AnalyzeCommentRequest) -> AnalyzeCommentResponse:
        text = self._text(req.comment.text if req.comment else None)
        if not req.requested_attributes:
            raise errors.no_requested_attributes()
        language, reported, detected = self._languages(text, req.languages)

        wanted: dict[str, tuple[str, float | None]] = {}
        for name, params in req.requested_attributes.items():
            score_type = params.score_type if params else None
            if score_type not in _SCORE_TYPES:
                raise errors.unsupported_score_type(str(score_type))
            try:
                core = attributes.resolve(name)
            except attributes.Unknown:
                raise errors.unknown_attribute(name) from None
            if core is None or language not in self._support.get(core, frozenset()):
                if req.drop_unsupported_attributes:
                    continue
                raise errors.language_not_supported(name, reported, detected)
            wanted[name] = (core, params.score_threshold if params else None)

        response = AnalyzeCommentResponse(
            languages=reported, detected_languages=detected, client_token=req.client_token
        )
        if not wanted:
            return response

        spans = sentences(text) if req.span_annotations else []
        if len(spans) <= 1:
            spans = []
        texts = [text] + [text[b:e] for b, e in spans]
        scores = self.backend.score(texts, language, {core for core, _ in wanted.values()})
        offsets = utf16_offsets(text)

        for name, (core, threshold) in wanted.items():
            summary = scores[0][core]
            if threshold is not None and summary < threshold:
                continue
            if spans:
                span_scores = [
                    SpanScore(begin=offsets[b], end=offsets[e], score=Score(value=s[core]))
                    for (b, e), s in zip(spans, scores[1:], strict=True)
                    if threshold is None or s[core] >= threshold
                ]
            else:
                span_scores = [SpanScore(begin=0, end=offsets[-1], score=Score(value=summary))]
            response.attribute_scores[name] = AttributeScores(
                summary_score=Score(value=summary), span_scores=span_scores
            )
        return response

    def suggest(self, req: SuggestCommentScoreRequest) -> SuggestCommentScoreResponse:
        text = self._text(req.comment.text if req.comment else None)
        if not req.attribute_scores:
            raise errors.invalid_request("attributeScores must contain at least one attribute.")
        detected = None if req.languages else self.detector.detect(text)[1]
        if self.feedback_path:
            record = {
                "time": time.time(),
                "comment": text,
                "attributeScores": {k: v.to_json() for k, v in req.attribute_scores.items()},
                "languages": req.languages,
                "communityId": req.community_id,
                "sessionId": req.session_id,
            }
            with self._feedback_lock, open(self.feedback_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return SuggestCommentScoreResponse(
            detected_languages=detected, requested_languages=req.languages, client_token=req.client_token
        )
