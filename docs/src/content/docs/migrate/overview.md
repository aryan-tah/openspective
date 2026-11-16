---
title: Migrating from Perspective
description: What changes when you switch, and where each client hard-codes Google's URL.
---

openspective answers the same requests as Perspective. Switching means changing one thing: the URL your client sends requests to.

```text
https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze
                    ↓
https://your-server.example.com/v1alpha1/comments:analyze
```

The request body, the response, the `key` parameter and the error format stay the same.

## The catch: most clients hard-code the URL

Few Perspective clients let you change the URL in settings. Coral does; most others have Google's URL written into their code, so switching takes a one-line patch or a newer version of the client.

| Client | URL configurable? | Guide |
| --- | --- | --- |
| Coral Talk | Yes, in admin settings | [Coral](/migrate/coral/) |
| Discourse (discourse-perspective-api) | No | [Discourse](/migrate/discourse/) |
| `googleapiclient` (Python) | Yes, `discoveryServiceUrl` | [Python](/migrate/python/) |
| HELM, RealToxicityPrompts, lm-evaluation-harness | No | [Research benchmarks](/migrate/research/) |
| perspective-api-client (npm), peRspective (R), Red-DiscordBot Defender | No | [Other clients](/migrate/other-clients/) |
| Your own code calling the REST API | Yes | Change the URL |

If a client you rely on isn't listed, [open an issue](https://github.com/aryan-tah/openspective/issues/new?template=feature.yml) with a link to it.

## Before you switch

1. **Check your languages and attributes.** openspective scores every attribute in English, and TOXICITY in French, Spanish, Italian, Portuguese, Turkish and Russian. See [attributes and languages](/reference/attributes/). Requests outside that get the same error Perspective returns for an unsupported language.
2. **Re-check your thresholds.** Scores come from different models, so a comment Perspective scored 0.7 won't score exactly 0.7 here. If you hide comments above a threshold, compare both on a sample of your own comments while Perspective still runs (until December 31, 2026).
3. **Read the [compatibility notes](/reference/compatibility/)** for the places openspective knowingly differs.
