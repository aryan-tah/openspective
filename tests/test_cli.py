import json

import pytest

from openspective.cli import main


def test_score_prints_an_api_response(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["score", "you idiot", "--backend", "fake", "-a", "INSULT", "FLIRTATION"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["attributeScores"]["INSULT"]["summaryScore"]["value"] == 0.92
    assert "FLIRTATION" not in out["attributeScores"]
