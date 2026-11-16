from __future__ import annotations

import json
import socket
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
import uvicorn
from fastapi.testclient import TestClient

from openspective.app import create_app
from openspective.settings import Settings
from tests.conftest import ANALYZE, make_client


def test_api_keys_are_enforced_when_configured() -> None:
    c = make_client(api_keys=frozenset({"secret"}))
    body = {"comment": {"text": "hi"}, "requestedAttributes": {"TOXICITY": {}}}
    denied = c.post(ANALYZE, json=body)
    assert denied.status_code == 403
    assert denied.json()["error"]["status"] == "PERMISSION_DENIED"
    assert c.post(f"{ANALYZE}?key=secret", json=body).status_code == 200
    assert c.post(ANALYZE, json=body, headers={"x-goog-api-key": "secret"}).status_code == 200


def test_suggestscore_acknowledges_and_stores_feedback_only_when_enabled(tmp_path: Path) -> None:
    path = tmp_path / "feedback.jsonl"
    body = {
        "comment": {"text": "you idiot"},
        "attributeScores": {"TOXICITY": {"summaryScore": {"value": 1}}},
        "languages": ["en"],
        "clientToken": "x",
    }
    r = make_client(feedback_path=str(path)).post("/v1alpha1/comments:suggestscore", json=body)
    assert r.json() == {"requestedLanguages": ["en"], "clientToken": "x"}
    assert json.loads(path.read_text())["comment"] == "you idiot"

    r = make_client().post("/v1alpha1/comments:suggestscore", json=body)
    assert r.status_code == 200


def test_unknown_paths_use_the_google_error_envelope(client: TestClient) -> None:
    r = client.get("/v1alpha1/nope")
    assert r.status_code == 404
    assert r.json()["error"]["status"] == "NOT_FOUND"


def test_lists_supported_attributes(client: TestClient) -> None:
    body = client.get("/v1alpha1/attributes").json()
    assert body["attributes"]["TOXICITY"] == ["en", "es", "fr"]


@pytest.fixture(scope="module")
def server_url() -> Iterator[str]:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    app = create_app(Settings(backend="fake"))
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=5)


def test_google_api_python_client_works_unchanged(server_url: str) -> None:
    """The exact code from Perspective's docs, pointed at openspective's discovery document."""
    from googleapiclient import discovery

    client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey="anything",
        discoveryServiceUrl=f"{server_url}/$discovery/rest?version=v1alpha1",
        static_discovery=False,
    )
    response = (
        client.comments()
        .analyze(body={"comment": {"text": "you idiot"}, "requestedAttributes": {"TOXICITY": {}}})
        .execute()
    )
    assert response["attributeScores"]["TOXICITY"]["summaryScore"]["value"] == 0.92
