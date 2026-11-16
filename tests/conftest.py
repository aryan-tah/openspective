from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from openspective.app import create_app
from openspective.settings import Settings


def make_client(**overrides: object) -> TestClient:
    settings = Settings(**{"backend": "fake", **overrides})  # type: ignore[arg-type]
    return TestClient(create_app(settings))


@pytest.fixture
def client() -> TestClient:
    return make_client()


ANALYZE = "/v1alpha1/comments:analyze"
