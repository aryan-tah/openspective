---
title: API
description: Endpoints, requests and responses.
---

openspective serves Perspective's `v1alpha1` API at the same paths. Field names are camelCase; snake_case is accepted too. Unknown fields are ignored.

## `POST /v1alpha1/comments:analyze`

Scores a comment.

### Request

| Field | Type | Notes |
| --- | --- | --- |
| `comment.text` | string | Required. Up to 20 KB of UTF-8. |
| `comment.type` | string | `PLAIN_TEXT` or `HTML`. HTML is scored as plain text. |
| `requestedAttributes` | object | Required. Attribute name → `{scoreType, scoreThreshold}`. `{}` uses the defaults. |
| `requestedAttributes.*.scoreType` | string | `PROBABILITY` (the default). Other types return a 400. |
| `requestedAttributes.*.scoreThreshold` | number | Leave out scores below this, for the summary and for each span. |
| `languages` | string[] | Languages of the comment. The first one decides the model. Detected when empty. |
| `spanAnnotations` | boolean | Score each sentence separately. |
| `dropUnsupportedAttributes` | boolean | Leave out attributes that can't be scored in the language, instead of returning an error. |
| `clientToken` | string | Echoed back in the response. |
| `context`, `doNotStore`, `sessionId`, `communityId` | | Accepted and ignored. |

### Response

```json
{
  "attributeScores": {
    "TOXICITY": {
      "summaryScore": {"value": 0.92, "type": "PROBABILITY"},
      "spanScores": [{"begin": 0, "end": 16, "score": {"value": 0.92, "type": "PROBABILITY"}}]
    }
  },
  "languages": ["en"],
  "detectedLanguages": ["en"],
  "clientToken": "abc"
}
```

- Keys in `attributeScores` are the names the client asked for, including `_EXPERIMENTAL` suffixes.
- `begin` and `end` are offsets in UTF-16 code units, and `end` is exclusive, as in Perspective. In JavaScript they index the string directly; in Python, convert from UTF-16 when the text has emoji or other characters outside the Basic Multilingual Plane.
- Without `spanAnnotations`, there's one span covering the whole comment.
- `detectedLanguages` is present only when the request didn't name languages.

## `POST /v1alpha1/comments:suggestscore`

Feedback on what a comment's scores should have been. Takes `comment`, `attributeScores` (same shape as the response above), `languages`, `communityId`, `sessionId` and `clientToken`. Returns `requestedLanguages`, `detectedLanguages` (when no languages were given) and `clientToken`.

Feedback is written to `OPENSPECTIVE_FEEDBACK_PATH` if set, and discarded otherwise.

## Discovery document

`GET /$discovery/rest?version=v1alpha1` (also at `/discovery/v1/apis/commentanalyzer/v1alpha1/rest`) returns a Google API discovery document for `commentanalyzer v1alpha1`, with `rootUrl` set to your server. Google's client libraries use it to build requests. See [Python](/migrate/python/).

## openspective extensions

- `GET /v1alpha1/attributes` lists which attributes the running server can score in which languages.
- `GET /healthz` returns `200` once the models are loaded.
- `GET /docs` is an interactive OpenAPI page.

## Authentication

When `OPENSPECTIVE_API_KEYS` is set, requests need a key as the `key` query parameter or an `x-goog-api-key` header. Requests without a valid key get a `403` with status `PERMISSION_DENIED`.
