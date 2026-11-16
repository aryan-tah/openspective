"""A Google API discovery document, so clients built with `googleapiclient.discovery.build`
or `googleapis.discoverAPI` work against openspective unchanged."""

from __future__ import annotations

from typing import Any

from openspective import __version__


def _ref(name: str) -> dict[str, str]:
    return {"$ref": name}


def _obj(description: str, **properties: Any) -> dict[str, Any]:
    return {"id": None, "type": "object", "description": description, "properties": properties}


def _str(description: str = "") -> dict[str, str]:
    return {"type": "string", "description": description}


def _schemas() -> dict[str, Any]:
    text_entry = _obj("Text and its format.", text=_str(), type=_str("PLAIN_TEXT or HTML."))
    schemas: dict[str, Any] = {
        "TextEntry": text_entry,
        "ArticleAndParentComment": _obj(
            "The article and parent comment a comment replies to.",
            article=_ref("TextEntry"),
            parentComment=_ref("TextEntry"),
        ),
        "Context": _obj(
            "Context for the comment. Accepted and ignored by openspective.",
            entries={"type": "array", "items": _ref("TextEntry")},
            articleAndParentComment=_ref("ArticleAndParentComment"),
        ),
        "AttributeParameters": _obj(
            "Per-attribute options.",
            scoreType=_str("PROBABILITY (the only type openspective returns)."),
            scoreThreshold={"type": "number", "format": "float"},
        ),
        "Score": _obj("A score.", value={"type": "number", "format": "float"}, type=_str()),
        "SpanScore": _obj(
            "A score for part of the text. begin and end are UTF-16 offsets; end is exclusive.",
            begin={"type": "integer", "format": "int32"},
            end={"type": "integer", "format": "int32"},
            score=_ref("Score"),
        ),
        "AttributeScores": _obj(
            "Scores for one attribute.",
            spanScores={"type": "array", "items": _ref("SpanScore")},
            summaryScore=_ref("Score"),
        ),
        "AnalyzeCommentRequest": _obj(
            "A comment to score.",
            comment=_ref("TextEntry"),
            context=_ref("Context"),
            requestedAttributes={"type": "object", "additionalProperties": _ref("AttributeParameters")},
            languages={"type": "array", "items": _str()},
            doNotStore={"type": "boolean"},
            clientToken=_str(),
            sessionId=_str(),
            communityId=_str(),
            spanAnnotations={"type": "boolean"},
            dropUnsupportedAttributes={"type": "boolean"},
        ),
        "AnalyzeCommentResponse": _obj(
            "Scores for a comment.",
            attributeScores={"type": "object", "additionalProperties": _ref("AttributeScores")},
            languages={"type": "array", "items": _str()},
            detectedLanguages={"type": "array", "items": _str()},
            clientToken=_str(),
        ),
        "SuggestCommentScoreRequest": _obj(
            "Feedback on what a comment's scores should be.",
            comment=_ref("TextEntry"),
            context=_ref("Context"),
            attributeScores={"type": "object", "additionalProperties": _ref("AttributeScores")},
            languages={"type": "array", "items": _str()},
            communityId=_str(),
            clientToken=_str(),
            sessionId=_str(),
        ),
        "SuggestCommentScoreResponse": _obj(
            "Acknowledges feedback.",
            detectedLanguages={"type": "array", "items": _str()},
            requestedLanguages={"type": "array", "items": _str()},
            clientToken=_str(),
        ),
    }
    for name, schema in schemas.items():
        schema["id"] = name
    return schemas


def _method(name: str, request: str, response: str, description: str) -> dict[str, Any]:
    return {
        "id": f"commentanalyzer.comments.{name}",
        "path": f"v1alpha1/comments:{name}",
        "flatPath": f"v1alpha1/comments:{name}",
        "httpMethod": "POST",
        "description": description,
        "parameters": {},
        "parameterOrder": [],
        "request": _ref(request),
        "response": _ref(response),
    }


def document(root_url: str) -> dict[str, Any]:
    root = root_url.rstrip("/") + "/"
    query = {"type": "string", "location": "query"}
    return {
        "kind": "discovery#restDescription",
        "discoveryVersion": "v1",
        "id": "commentanalyzer:v1alpha1",
        "name": "commentanalyzer",
        "canonicalName": "Comment Analyzer",
        "version": "v1alpha1",
        "revision": __version__,
        "title": "openspective (Perspective API compatible)",
        "description": "Self-hosted, Perspective API compatible comment scoring.",
        "documentationLink": "https://openspective.aryantah.com",
        "protocol": "rest",
        "rootUrl": root,
        "servicePath": "",
        "basePath": "",
        "baseUrl": root,
        "batchPath": "batch",
        "parameters": {
            "key": {**query, "description": "API key, if the server requires one."},
            "alt": {**query, "default": "json", "enum": ["json"]},
            "fields": query,
            "prettyPrint": {"type": "boolean", "location": "query", "default": "true"},
            "quotaUser": query,
            "access_token": query,
            "callback": query,
            "upload_protocol": query,
            "uploadType": query,
            "$.xgafv": {**query, "enum": ["1", "2"]},
        },
        "schemas": _schemas(),
        "resources": {
            "comments": {
                "methods": {
                    "analyze": _method(
                        "analyze", "AnalyzeCommentRequest", "AnalyzeCommentResponse", "Scores a comment."
                    ),
                    "suggestscore": _method(
                        "suggestscore",
                        "SuggestCommentScoreRequest",
                        "SuggestCommentScoreResponse",
                        "Records feedback on a comment's scores.",
                    ),
                }
            }
        },
    }
