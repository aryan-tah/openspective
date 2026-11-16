---
title: Other clients
description: Node, R, Discord bots and anything else that calls Perspective.
---

These clients have Google's URL written into their code. Each one needs the URL changed, either with a patch or by calling the API directly.

## perspective-api-client (npm)

[perspective-api-client](https://github.com/sloria/perspective-api-client) posts to a fixed URL. The API is small enough to call directly:

```js
const res = await fetch("https://your-server.example.com/v1alpha1/comments:analyze?key=" + key, {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ comment: { text }, requestedAttributes: { TOXICITY: {} } }),
});
const score = (await res.json()).attributeScores.TOXICITY.summaryScore.value;
```

## peRspective (R)

[peRspective](https://github.com/favstats/peRspective) builds its request URL in `R/prsp_score.R`. Change the base URL there, or call the API with `httr2`:

```r
library(httr2)
resp <- request("https://your-server.example.com/v1alpha1/comments:analyze") |>
  req_body_json(list(comment = list(text = "hello"), requestedAttributes = list(TOXICITY = setNames(list(), character())))) |>
  req_perform() |>
  resp_body_json()
```

## Red-DiscordBot Defender (x26-Cogs)

Defender's Perspective auto-module posts to a fixed URL in `defender/core/automodules.py`. Change it to your server's URL. The [shutdown issue](https://github.com/Twentysix26/x26-Cogs/issues/106) on its repository tracks a longer-term fix.

## Anything else

Search the client's code for `commentanalyzer.googleapis.com` and replace it with your server's URL, keeping the path. If the client uses Google's discovery document, point it at `https://your-server/$discovery/rest?version=v1alpha1` instead.
