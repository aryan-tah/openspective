---
title: Configuration
description: Every setting, as an environment variable.
---

openspective reads its settings from environment variables. With Docker, pass them with `-e`:

```bash
docker run -p 8080:8080 -e OPENSPECTIVE_API_KEYS=key-one,key-two ghcr.io/aryan-tah/openspective
```

| Variable | Default | What it does |
| --- | --- | --- |
| `OPENSPECTIVE_API_KEYS` | unset | Comma-separated keys. When set, every request needs one, as `?key=` (like Perspective) or an `x-goog-api-key` header. When unset, no key is needed and any `key` a client sends is ignored. |
| `OPENSPECTIVE_DEFAULT_LANGUAGE` | `en` | Language to use when detection isn't confident, which is common for very short comments like "lol". Set it to an empty string to return Perspective's `LANGUAGE_DETECTION_FAILED` error instead. |
| `OPENSPECTIVE_MAX_COMMENT_BYTES` | `20480` | Longest comment accepted, in UTF-8 bytes. Perspective's limit is 20 KB. |
| `OPENSPECTIVE_FEEDBACK_PATH` | unset | File where `comments:suggestscore` feedback is appended as JSON lines. When unset, feedback is acknowledged and discarded. |
| `OPENSPECTIVE_PUBLIC_URL` | request URL | Base URL written into the discovery document. Set it when openspective runs behind a proxy that changes the host or scheme. |
| `OPENSPECTIVE_PRELOAD` | `1` | Load the models at startup. Set `0` to load them on the first request instead. |
| `OPENSPECTIVE_THREADS` | all cores | CPU threads per inference. |
| `OPENSPECTIVE_DEVICE` | `cpu` | `cuda` or `mps` to run on a GPU. |
| `PORT` | `8080` | Port to listen on. |

## Privacy

openspective doesn't store comment text or log request bodies. The only exception is `OPENSPECTIVE_FEEDBACK_PATH`: when you set it, the comments clients send to `comments:suggestscore` are written to that file. The `doNotStore` field is accepted and has no effect, because nothing is stored either way.
