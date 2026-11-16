---
title: Deploy
description: Run openspective in production.
---

## Sizing

One container uses about 2.5 GB of memory with both models loaded. On a modern CPU core, a one-sentence comment takes around 20 ms; long comments and `spanAnnotations` take longer, because every sentence is scored too.

Perspective's default quota was 1 request per second, so a single small instance usually covers what you used before. For more throughput, run more containers behind a load balancer. Each container is stateless.

## Docker Compose

```yaml
services:
  openspective:
    image: ghcr.io/aryan-tah/openspective:0.1
    ports: ["8080:8080"]
    environment:
      OPENSPECTIVE_API_KEYS: ${OPENSPECTIVE_API_KEYS}
    restart: unless-stopped
```

Pin a version (`:0.1` or `:0.1.0`) in production. `latest` follows releases and `edge` follows the main branch.

## Health checks

`GET /healthz` returns `200` with the version and backend once the models are loaded. The image has a Docker `HEALTHCHECK` that uses it.

## Behind a proxy

If clients use the [discovery document](/reference/api/#discovery-document) (Google's Python client does), set `OPENSPECTIVE_PUBLIC_URL` to the URL clients reach, for example `https://toxicity.example.com`. Otherwise the document points at the address the proxy forwards to.

## API keys

Set `OPENSPECTIVE_API_KEYS` if the server is reachable from outside your network. Clients that already send a Perspective key with `?key=` only need the key changed. To rotate keys, add the new one, update clients, then remove the old one.
