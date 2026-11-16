---
title: Discourse
description: Use openspective with the discourse-perspective-api plugin.
---

The [discourse-perspective-api](https://github.com/discourse/discourse-perspective-api) plugin has Google's domain written into its code (`GOOGLE_API_DOMAIN` in `lib/discourse_perspective.rb`), and there's no setting to change it.

Until the plugin accepts a configurable URL, install a fork with the constant changed:

1. Fork the plugin.
2. In `lib/discourse_perspective.rb`, change `GOOGLE_API_DOMAIN` from `https://commentanalyzer.googleapis.com` to your openspective URL.
3. In your Discourse `app.yml`, install the plugin from your fork instead of the original, and rebuild.
4. In the plugin settings, set the API key to one of your `OPENSPECTIVE_API_KEYS`, or any value if your server doesn't require keys.

A change to make the URL a site setting is tracked in openspective's issues. Once the plugin supports it, this page will switch to the setting.
