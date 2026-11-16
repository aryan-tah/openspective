<p align="center">
  <img src="assets/logo.svg" width="96" height="96" alt="openspective">
</p>

<h1 align="center">openspective</h1>

<p align="center">
  <b>Google's Perspective API shuts down on December 31, 2026. This is the drop-in replacement you run yourself.</b>
</p>

<p align="center">
  <a href="https://github.com/aryan-tah/openspective/actions/workflows/ci.yml"><img src="https://github.com/aryan-tah/openspective/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/openspective/"><img src="https://img.shields.io/pypi/v/openspective?color=0a0a0a" alt="PyPI"></a>
  <a href="https://github.com/aryan-tah/openspective/pkgs/container/openspective"><img src="https://img.shields.io/badge/docker-ghcr.io-0a0a0a" alt="Docker image"></a>
  <a href="https://scorecard.dev/viewer/?uri=github.com/aryan-tah/openspective"><img src="https://api.scorecard.dev/projects/github.com/aryan-tah/openspective/badge" alt="OpenSSF Scorecard"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-0a0a0a" alt="Apache-2.0 license"></a>
</p>

<p align="center">
  <a href="https://openspective.aryantah.com">Docs</a> ·
  <a href="https://openspective.aryantah.com/getting-started/">Getting started</a> ·
  <a href="https://openspective.aryantah.com/migrate/overview/">Migrate a client</a> ·
  <a href="https://openspective.aryantah.com/reference/compatibility/">Compatibility</a>
</p>

---

Comment sections, forums, Discord bots and LLM safety benchmarks score text with [Perspective](https://perspectiveapi.com). Jigsaw is [shutting it down](https://perspectiveapi.com/) at the end of 2026 and isn't offering a successor or migration support.

openspective answers the same requests with the same JSON. Change the URL your client calls, and keep the rest of your code.

```bash
docker run -p 8080:8080 ghcr.io/aryan-tah/openspective
```

```bash
curl -s localhost:8080/v1alpha1/comments:analyze \
  -H 'content-type: application/json' \
  -d '{"comment": {"text": "Thanks for the article. You are a clueless idiot though."},
       "requestedAttributes": {"TOXICITY": {}, "INSULT": {}},
       "spanAnnotations": true}'
```

```json
{
  "attributeScores": {
    "TOXICITY": {
      "spanScores": [
        {"begin": 0,  "end": 23, "score": {"value": 0.0004, "type": "PROBABILITY"}},
        {"begin": 24, "end": 56, "score": {"value": 0.9966, "type": "PROBABILITY"}}
      ],
      "summaryScore": {"value": 0.9965, "type": "PROBABILITY"}
    },
    "INSULT": { … }
  },
  "languages": ["en"],
  "detectedLanguages": ["en"]
}
```

## Why openspective

|  | openspective | Other open-source options | Hosted moderation APIs |
| --- | --- | --- | --- |
| Perspective's request and response format | ✅ Same paths, fields, spans, errors and discovery document | ❌ Their own formats | ❌ Different APIs and categories |
| Works with Google's own client library | ✅ Tested in CI | ❌ | ❌ |
| Languages | English, plus TOXICITY in fr, es, it, pt, tr, ru | English only | Varies |
| Runs on your servers | ✅ One container, CPU only, works offline | ✅ | ❌ Comments leave your network |
| Cost | Your hardware | Your hardware | Per request |
| Model license | Apache-2.0 | Varies | Closed |

## What it scores

| Attribute | Languages |
| --- | --- |
| `TOXICITY` | en, fr, es, it, pt, tr, ru |
| `SEVERE_TOXICITY`, `IDENTITY_ATTACK`, `INSULT`, `PROFANITY`, `THREAT`, `SEXUALLY_EXPLICIT` | en |

Scores come from [Detoxify](https://github.com/unitaryai/detoxify)'s Apache-2.0 models, which were trained on Jigsaw's own Kaggle data. In published comparisons, Detoxify's scores correlate with Perspective's at r = 0.85 to 0.91. Perspective's `_EXPERIMENTAL` attribute names are accepted too.

Attributes no open model covers yet (FLIRTATION, the NYT and bridging attributes), and languages not listed above, return the same error Perspective returns for an unsupported language, so `dropUnsupportedAttributes` and your existing error handling keep working. More languages are the top item on the [roadmap](https://github.com/aryan-tah/openspective/issues?q=is%3Aopen+label%3A%22priority%3A+high%22).

## Switching your client

| Client | How to switch |
| --- | --- |
| Your own code calling the REST API | Change `https://commentanalyzer.googleapis.com` to your server's URL |
| Python `googleapiclient` | Pass `discoveryServiceUrl="https://your-server/$discovery/rest?version=v1alpha1"` |
| [Coral Talk](https://openspective.aryantah.com/migrate/coral/) | Change the endpoint in admin settings |
| [Discourse](https://openspective.aryantah.com/migrate/discourse/), [HELM, RealToxicityPrompts, lm-evaluation-harness](https://openspective.aryantah.com/migrate/research/), [npm, R and Discord bot clients](https://openspective.aryantah.com/migrate/other-clients/) | One-line patch; the URL is hard-coded |

Scores come from different models, so re-check any thresholds on a sample of your own comments while Perspective still runs. The [compatibility page](https://openspective.aryantah.com/reference/compatibility/) lists every known difference.

## Run it

```bash
# Docker: models included, starts offline, ~2.5 GB of memory
docker run -p 8080:8080 -e OPENSPECTIVE_API_KEYS=your-key ghcr.io/aryan-tah/openspective

# Python 3.11+
pip install openspective
openspective serve --host 0.0.0.0 --port 8080

# Score from the command line
openspective score "You are a clueless idiot"
```

A one-sentence comment takes about 20 ms on a laptop CPU. All settings are [environment variables](https://openspective.aryantah.com/guides/configuration/). Comments are never stored.

## Contributing

The most useful contributions right now:

- **Scores from Perspective**, while it still runs, for text you're allowed to share. They're how openspective's calibration gets checked. Use the [wrong score](https://github.com/aryan-tah/openspective/issues/new?template=score-report.yml) form.
- **A client that breaks** against openspective. That's a compatibility bug; [report it](https://github.com/aryan-tah/openspective/issues/new?template=bug.yml).
- **Migration guides** for clients not covered yet.

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

## License

[Apache-2.0](LICENSE) © Aryan Tah. Model licenses are listed in [NOTICE](NOTICE).

openspective is an independent project. It is not affiliated with or endorsed by Google or Jigsaw. "Perspective API" is used only to describe the API it's compatible with.
