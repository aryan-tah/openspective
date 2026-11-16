"""Request and response models for the Perspective `v1alpha1` API.

Field names follow the API's JSON (camelCase). Like Google's proto JSON parser, snake_case
names are accepted too, and unknown fields are ignored rather than rejected.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class _Model(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    def to_json(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_none=True)


class TextEntry(_Model):
    text: str | None = None
    type: str | None = None


class ArticleAndParentComment(_Model):
    article: TextEntry | None = None
    parent_comment: TextEntry | None = None


class Context(_Model):
    entries: list[TextEntry] | None = None
    article_and_parent_comment: ArticleAndParentComment | None = None


class AttributeParameters(_Model):
    score_type: str | None = None
    score_threshold: float | None = None


class AnalyzeCommentRequest(_Model):
    comment: TextEntry | None = None
    context: Context | None = None
    requested_attributes: dict[str, AttributeParameters | None] | None = None
    languages: list[str] | None = None
    do_not_store: bool | None = None
    client_token: str | None = None
    session_id: str | None = None
    community_id: str | None = None
    span_annotations: bool | None = None
    drop_unsupported_attributes: bool | None = None


class Score(_Model):
    value: float
    type: str = "PROBABILITY"


class SpanScore(_Model):
    begin: int | None = None
    end: int | None = None
    score: Score


class AttributeScores(_Model):
    span_scores: list[SpanScore] | None = None
    summary_score: Score | None = None


class AnalyzeCommentResponse(_Model):
    attribute_scores: dict[str, AttributeScores] = Field(default_factory=dict)
    languages: list[str] | None = None
    detected_languages: list[str] | None = None
    client_token: str | None = None

    def to_json(self) -> dict[str, Any]:
        # Attribute names are keys chosen by the client; keep them exactly as requested.
        out = super().to_json()
        out["attributeScores"] = {k: v.to_json() for k, v in self.attribute_scores.items()}
        return out


class SuggestCommentScoreRequest(_Model):
    comment: TextEntry | None = None
    context: Context | None = None
    attribute_scores: dict[str, AttributeScores] | None = None
    languages: list[str] | None = None
    community_id: str | None = None
    client_token: str | None = None
    session_id: str | None = None


class SuggestCommentScoreResponse(_Model):
    detected_languages: list[str] | None = None
    requested_languages: list[str] | None = None
    client_token: str | None = None
