---
title: Attributes and languages
description: What openspective scores, in which languages, with which model.
---

## Supported

| Attribute | Languages | Model output |
| --- | --- | --- |
| `TOXICITY` | en, fr, es, it, pt, tr, ru | `toxicity` (English), `toxic` (others) |
| `SEVERE_TOXICITY` | en | `severe_toxicity` |
| `IDENTITY_ATTACK` | en | `identity_attack` |
| `INSULT` | en | `insult` |
| `PROFANITY` | en | `obscene` |
| `THREAT` | en | `threat` |
| `SEXUALLY_EXPLICIT` | en | `sexual_explicit` |

The `_EXPERIMENTAL` names Perspective used (`INSULT_EXPERIMENTAL`, `TOXICITY_EXPERIMENTAL` and so on) and `TOXICITY_FAST` are accepted as aliases. The response keeps the name you asked for.

A running server lists what it supports at `GET /v1alpha1/attributes`.

## Models

| Model | Used for | License |
| --- | --- | --- |
| [unitary/unbiased-toxic-roberta](https://huggingface.co/unitary/unbiased-toxic-roberta) | Every attribute in English | Apache-2.0 |
| [unitary/multilingual-toxic-xlm-roberta](https://huggingface.co/unitary/multilingual-toxic-xlm-roberta) | `TOXICITY` in fr, es, it, pt, tr, ru | Apache-2.0 |

Both come from the [Detoxify](https://github.com/unitaryai/detoxify) project and were trained on data from Jigsaw's Kaggle competitions, the same team behind Perspective. The English model was trained to reduce bias against identity terms. The multilingual model was trained for overall toxicity only, so openspective doesn't use it for the other attributes: a score from a head that was never trained in that language would look precise and mean nothing.

## Not supported yet

- **Other languages for TOXICITY.** Perspective also scored German, Arabic, Japanese, Korean, Chinese and others. Adding them is the top item on the roadmap.
- **Non-English INSULT, THREAT, PROFANITY and IDENTITY_ATTACK.**
- **FLIRTATION**, the New York Times attributes (`ATTACK_ON_AUTHOR`, `INFLAMMATORY`, `LIKELY_TO_REJECT`, …) and the bridging attributes (`AFFINITY_EXPERIMENTAL`, `REASONING_EXPERIMENTAL`, …). No open model covers them.

Requesting any of these returns the error Perspective returns for an unsupported language, so `dropUnsupportedAttributes` works as before.
