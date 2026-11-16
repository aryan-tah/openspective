---
title: Python (googleapiclient)
description: Use Google's own Python client with openspective.
---

Perspective's documentation used Google's API client. It works against openspective unchanged, because openspective serves the same discovery document format. Point `discoveryServiceUrl` at your server:

```python
from googleapiclient import discovery

client = discovery.build(
    "commentanalyzer",
    "v1alpha1",
    developerKey=API_KEY,
    discoveryServiceUrl="https://your-server.example.com/$discovery/rest?version=v1alpha1",
    static_discovery=False,
)

response = client.comments().analyze(body={
    "comment": {"text": "friendly greetings from python"},
    "requestedAttributes": {"TOXICITY": {}},
}).execute()
```

`static_discovery=False` makes the client fetch the document from your server instead of looking for a bundled copy. openspective's test suite runs exactly this code.

## Plain `requests`

```python
import requests

r = requests.post(
    "https://your-server.example.com/v1alpha1/comments:analyze",
    params={"key": API_KEY},
    json={"comment": {"text": "friendly greetings"}, "requestedAttributes": {"TOXICITY": {}}},
    timeout=10,
)
r.raise_for_status()
score = r.json()["attributeScores"]["TOXICITY"]["summaryScore"]["value"]
```
