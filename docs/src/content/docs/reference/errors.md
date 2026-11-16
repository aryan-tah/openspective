---
title: Errors
description: Error responses and when they happen.
---

Errors use Google's envelope, so code that handled Perspective's errors keeps working:

```json
{
  "error": {
    "code": 400,
    "message": "Attribute TOXICITY does not support request languages: fi",
    "status": "INVALID_ARGUMENT",
    "details": [{
      "@type": "type.googleapis.com/google.commentanalyzer.v1alpha1.Error",
      "errorType": "LANGUAGE_NOT_SUPPORTED_BY_ATTRIBUTE",
      "languageNotSupportedByAttributeError": {"detectedLanguages": ["fi"], "attribute": "TOXICITY"}
    }]
  }
}
```

| HTTP | `errorType` | When |
| --- | --- | --- |
| 400 | `LANGUAGE_NOT_SUPPORTED_BY_ATTRIBUTE` | An attribute can't be scored in the comment's language, or isn't available in openspective. Set `dropUnsupportedAttributes` to skip it instead. |
| 400 | `COMMENT_EMPTY` | `comment.text` is missing or only whitespace. |
| 400 | `COMMENT_TOO_LONG` | The comment is over `OPENSPECTIVE_MAX_COMMENT_BYTES` (20 KB by default). |
| 400 | `NO_REQUESTED_ATTRIBUTES` | `requestedAttributes` is missing or empty. |
| 400 | `LANGUAGE_DETECTION_FAILED` | No language given, detection wasn't confident, and `OPENSPECTIVE_DEFAULT_LANGUAGE` is empty. |
| 400 | `INVALID_REQUEST` | An unknown attribute name, an unsupported score type, or a body that isn't a JSON object. |
| 403 | — | API keys are required and the request has none, or the wrong one. Status `PERMISSION_DENIED`. |
| 404 | — | Unknown path. Status `NOT_FOUND`. |
