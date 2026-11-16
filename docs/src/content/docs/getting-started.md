---
title: Getting started
description: Run openspective and score your first comment.
---

## Run it

The Docker image includes the models, so it starts without downloading anything:

```bash
docker run -p 8080:8080 ghcr.io/aryan-tah/openspective
```

It runs on any machine with about 3 GB of free memory, CPU only. Startup takes 10 to 20 seconds while the models load. Check it's ready:

```bash
curl localhost:8080/healthz
```

To run it without Docker, you need Python 3.11 or newer:

```bash
pip install openspective
openspective serve --host 0.0.0.0 --port 8080
```

The first start downloads the models (about 1.6 GB) from Hugging Face.

## Score a comment

Send the same request you'd send to Perspective:

```bash
curl -s localhost:8080/v1alpha1/comments:analyze \
  -H 'content-type: application/json' \
  -d '{
    "comment": {"text": "Thanks for the article. You are a clueless idiot though."},
    "requestedAttributes": {"TOXICITY": {}, "INSULT": {}},
    "spanAnnotations": true
  }'
```

With `spanAnnotations`, each sentence gets its own score, so you can see which part of a comment is the problem:

```json
"TOXICITY": {
  "spanScores": [
    {"begin": 0, "end": 23, "score": {"value": 0.0004, "type": "PROBABILITY"}},
    {"begin": 24, "end": 56, "score": {"value": 0.9966, "type": "PROBABILITY"}}
  ],
  "summaryScore": {"value": 0.9965, "type": "PROBABILITY"}
}
```

From the command line, without a server:

```bash
openspective score "You are a clueless idiot"
```

## Point your app at it

Replace `https://commentanalyzer.googleapis.com` with your server's URL wherever your app or library calls Perspective. How to do that depends on the client: see [Migrate from Perspective](/migrate/overview/).

## Next

- [Configuration](/guides/configuration/): API keys, language fallback, feedback storage.
- [Attributes and languages](/reference/attributes/): what's scored in which language.
- [Compatibility](/reference/compatibility/): where openspective knowingly differs from Perspective.
