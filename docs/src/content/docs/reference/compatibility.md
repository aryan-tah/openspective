---
title: Compatibility
description: Where openspective knowingly behaves differently from Perspective.
---

The goal is that a client written for Perspective works without changes. Where openspective differs, it's listed here.

| Area | Perspective | openspective | Why |
| --- | --- | --- | --- |
| Scores | Google's models | Detoxify models | Scores are close, not identical. Re-check thresholds. |
| Languages | About 18 for TOXICITY | 7 for TOXICITY, English for the rest | See [attributes and languages](/reference/attributes/). |
| Short comments | Often `LANGUAGE_DETECTION_FAILED` | Falls back to English | Short comments like "lol" are where detection fails most. Set `OPENSPECTIVE_DEFAULT_LANGUAGE=` to get the error instead. |
| Unavailable attributes | — | Same error as an unsupported language | So existing error handling and `dropUnsupportedAttributes` keep working. |
| Score types | `PROBABILITY` (others documented, rarely available) | `PROBABILITY` only | Other types return a 400. |
| `context` | Accepted, used by some models | Accepted, ignored | The open models score the comment alone. |
| `doNotStore` | Controls storage | Accepted, no effect | openspective never stores comments, except `suggestscore` feedback when you turn it on. |
| `suggestscore` | Sent to Google | Discarded, or written to a file | Set `OPENSPECTIVE_FEEDBACK_PATH` to keep it. |
| Quota | 1 QPS by default | No limit | It's your server. |
| Long comments | Not documented | Scored in overlapping windows; each attribute takes its highest window score | So a toxic sentence at the end of a long comment isn't cut off. |
| Spans | Sentence level | Sentence level, split on terminal punctuation and newlines | Same units: UTF-16, end exclusive. |
| Auth | API key or OAuth | API key, optional | OAuth tokens aren't checked. |

Found another difference that breaks a client? [Report it](https://github.com/aryan-tah/openspective/issues/new?template=bug.yml).
