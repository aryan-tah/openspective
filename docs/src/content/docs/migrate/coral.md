---
title: Coral Talk
description: Point Coral's toxic comment filter at openspective.
---

Coral calls Perspective through its toxic comment integration, and the endpoint is a setting (`PerspectiveExternalIntegration.endpoint` in Coral's schema). Its default is `https://commentanalyzer.googleapis.com/v1alpha1`.

1. Run openspective somewhere your Coral server can reach.
2. In Coral's admin, open the moderation settings for the Perspective toxic comment filter.
3. Set the endpoint to your server with the same path, for example `https://openspective.internal.example.com/v1alpha1`.
4. Set the API key to one of your `OPENSPECTIVE_API_KEYS`, or leave it as is if your server doesn't require keys.

Coral also sends moderator decisions back through `comments:suggestscore`. openspective accepts these. To keep them, for example to tune thresholds later, set `OPENSPECTIVE_FEEDBACK_PATH`.

Coral compares the TOXICITY score against your threshold. Check the threshold on a sample of your comments after switching: see [before you switch](/migrate/overview/#before-you-switch).
