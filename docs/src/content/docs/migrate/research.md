---
title: Research benchmarks
description: Keep running RealToxicityPrompts, HELM and lm-evaluation-harness toxicity evals.
---

Many LLM toxicity benchmarks score model outputs with Perspective. They stop working when Perspective does. openspective keeps them running, with two things to know.

## Scores won't match published numbers exactly

Perspective's own models changed over time without notice, so published toxicity numbers were never fully reproducible. openspective uses fixed, versioned models: a run today and a run next year give the same scores. That's an improvement for new work, but don't mix openspective scores with Perspective scores in one comparison. Re-score the baselines too.

When you report results, name the scorer and version, for example "toxicity scored with openspective 0.1.0 (Detoxify unbiased-toxic-roberta)".

## Patching the clients

None of these let you change the URL in config yet, so each needs a small patch.

**RealToxicityPrompts** (`utils/perspective_api.py`) calls `discovery.build('commentanalyzer', 'v1alpha1', developerKey=...)`. Add the discovery URL:

```python
discovery.build(
    "commentanalyzer", "v1alpha1", developerKey=api_key,
    discoveryServiceUrl="http://localhost:8080/$discovery/rest?version=v1alpha1",
    static_discovery=False,
)
```

**HELM** (`src/helm/clients/perspective_api_client.py`) passes a fixed `discoveryServiceUrl`. Replace it with your server's discovery URL, as above.

**lm-evaluation-harness** (`lm_eval/tasks/realtoxicityprompts/metric.py`) posts to a fixed URL with `requests`. Replace `https://commentanalyzer.googleapis.com` with your server's URL. It reads the key from `PERSPECTIVE_API_KEY`; any value works if your server doesn't require keys. Because openspective runs locally with no quota, you can also raise `PERSPECTIVE_API_QPS`.

## Throughput

Benchmarks send many requests. On CPU, expect a few dozen short generations per second per container. A GPU (`OPENSPECTIVE_DEVICE=cuda`) is much faster for large runs.
