"""Errors in the Google API envelope that Perspective clients already parse."""

from __future__ import annotations

from typing import Any

ERROR_TYPE_URL = "type.googleapis.com/google.commentanalyzer.v1alpha1.Error"

_STATUS = {400: "INVALID_ARGUMENT", 403: "PERMISSION_DENIED", 404: "NOT_FOUND", 429: "RESOURCE_EXHAUSTED"}


class ApiError(Exception):
    """An error returned to the client as `{"error": {"code", "message", "status", "details"}}`."""

    def __init__(
        self,
        message: str,
        *,
        code: int = 400,
        error_type: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.error_type = error_type
        self.extra = extra or {}

    def body(self) -> dict[str, Any]:
        error: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "status": _STATUS.get(self.code, "UNKNOWN"),
        }
        if self.error_type:
            error["details"] = [{"@type": ERROR_TYPE_URL, "errorType": self.error_type, **self.extra}]
        return {"error": error}


def comment_empty() -> ApiError:
    return ApiError("Comment must be non-empty.", error_type="COMMENT_EMPTY")


def comment_too_long(size: int, limit: int) -> ApiError:
    return ApiError(
        f"Comment text too long: {size} bytes, the limit is {limit} bytes.", error_type="COMMENT_TOO_LONG"
    )


def no_requested_attributes() -> ApiError:
    return ApiError("Must request at least one attribute.", error_type="NO_REQUESTED_ATTRIBUTES")


def unknown_attribute(name: str) -> ApiError:
    return ApiError(f"Unknown requested attribute: {name}", error_type="INVALID_REQUEST")


def language_not_supported(attribute: str, languages: list[str], detected: list[str] | None) -> ApiError:
    return ApiError(
        f"Attribute {attribute} does not support request languages: {', '.join(languages)}",
        error_type="LANGUAGE_NOT_SUPPORTED_BY_ATTRIBUTE",
        extra={
            "languageNotSupportedByAttributeError": {
                "detectedLanguages": detected if detected is not None else languages,
                "attribute": attribute,
            }
        },
    )


def language_detection_failed() -> ApiError:
    return ApiError(
        "Attribute requests could not be processed: unable to detect language.",
        error_type="LANGUAGE_DETECTION_FAILED",
    )


def unsupported_score_type(score_type: str) -> ApiError:
    return ApiError(
        f"Score type {score_type} is not supported. Use PROBABILITY.", error_type="INVALID_REQUEST"
    )


def invalid_request(message: str) -> ApiError:
    return ApiError(message, error_type="INVALID_REQUEST")


def missing_key() -> ApiError:
    return ApiError(
        "The request is missing a valid API key.",
        code=403,
    )
