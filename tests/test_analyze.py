from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from tests.conftest import ANALYZE, make_client


def analyze(client: TestClient, **body: Any) -> Any:
    return client.post(ANALYZE, json=body)


def test_scores_a_comment_in_perspective_format(client: TestClient) -> None:
    r = analyze(client, comment={"text": "You are an idiot"}, requestedAttributes={"TOXICITY": {}})
    assert r.status_code == 200
    assert r.json() == {
        "attributeScores": {
            "TOXICITY": {
                "spanScores": [{"begin": 0, "end": 16, "score": {"value": 0.92, "type": "PROBABILITY"}}],
                "summaryScore": {"value": 0.92, "type": "PROBABILITY"},
            }
        },
        "languages": ["en"],
        "detectedLanguages": ["en"],
    }


def test_requested_languages_are_reported_and_not_detected(client: TestClient) -> None:
    r = analyze(client, comment={"text": "hola"}, requestedAttributes={"TOXICITY": {}}, languages=["es"])
    body = r.json()
    assert body["languages"] == ["es"]
    assert "detectedLanguages" not in body


def test_region_subtags_are_accepted(client: TestClient) -> None:
    r = analyze(client, comment={"text": "hi"}, requestedAttributes={"INSULT": {}}, languages=["en-US"])
    assert r.status_code == 200
    assert r.json()["languages"] == ["en-US"]


def test_echoes_client_token(client: TestClient) -> None:
    r = analyze(client, comment={"text": "hi"}, requestedAttributes={"TOXICITY": {}}, clientToken="abc")
    assert r.json()["clientToken"] == "abc"


def test_accepts_snake_case_fields(client: TestClient) -> None:
    r = analyze(client, comment={"text": "you idiot"}, requested_attributes={"INSULT": {}}, client_token="t")
    assert r.status_code == 200
    assert r.json()["clientToken"] == "t"


def test_experimental_names_keep_the_requested_key(client: TestClient) -> None:
    r = analyze(client, comment={"text": "you idiot"}, requestedAttributes={"INSULT_EXPERIMENTAL": {}})
    assert list(r.json()["attributeScores"]) == ["INSULT_EXPERIMENTAL"]


def test_threshold_omits_low_scores(client: TestClient) -> None:
    r = analyze(
        client,
        comment={"text": "you idiot"},
        requestedAttributes={"INSULT": {"scoreThreshold": 0.5}, "THREAT": {"scoreThreshold": 0.5}},
    )
    assert list(r.json()["attributeScores"]) == ["INSULT"]


def test_span_annotations_score_each_sentence_with_utf16_offsets(client: TestClient) -> None:
    text = "Nice post 👍. You are an idiot!"
    r = analyze(client, comment={"text": text}, requestedAttributes={"TOXICITY": {}}, spanAnnotations=True)
    spans = r.json()["attributeScores"]["TOXICITY"]["spanScores"]
    assert [(s["begin"], s["end"], s["score"]["value"]) for s in spans] == [(0, 13, 0.04), (14, 31, 0.92)]
    # The emoji is two UTF-16 code units, so offsets run one past Python's indexes.
    assert len(text) == 30


def test_unsupported_language_matches_perspective_error(client: TestClient) -> None:
    r = analyze(client, comment={"text": "hei"}, requestedAttributes={"TOXICITY": {}}, languages=["fi"])
    assert r.status_code == 400
    assert r.json() == {
        "error": {
            "code": 400,
            "message": "Attribute TOXICITY does not support request languages: fi",
            "status": "INVALID_ARGUMENT",
            "details": [
                {
                    "@type": "type.googleapis.com/google.commentanalyzer.v1alpha1.Error",
                    "errorType": "LANGUAGE_NOT_SUPPORTED_BY_ATTRIBUTE",
                    "languageNotSupportedByAttributeError": {
                        "detectedLanguages": ["fi"],
                        "attribute": "TOXICITY",
                    },
                }
            ],
        }
    }


def test_drop_unsupported_attributes(client: TestClient) -> None:
    r = analyze(
        client,
        comment={"text": "eres un idiota"},
        requestedAttributes={"TOXICITY": {}, "INSULT": {}, "FLIRTATION": {}},
        languages=["es"],
        dropUnsupportedAttributes=True,
    )
    assert r.status_code == 200
    assert list(r.json()["attributeScores"]) == ["TOXICITY"]


def test_attributes_openspective_lacks_behave_like_unsupported_languages(client: TestClient) -> None:
    r = analyze(client, comment={"text": "hi"}, requestedAttributes={"FLIRTATION": {}})
    assert r.json()["error"]["details"][0]["errorType"] == "LANGUAGE_NOT_SUPPORTED_BY_ATTRIBUTE"


def test_unknown_attribute(client: TestClient) -> None:
    r = analyze(client, comment={"text": "hi"}, requestedAttributes={"NOPE": {}})
    assert r.status_code == 400
    assert r.json()["error"]["message"] == "Unknown requested attribute: NOPE"


def test_empty_comment(client: TestClient) -> None:
    r = analyze(client, comment={"text": "   "}, requestedAttributes={"TOXICITY": {}})
    assert r.json()["error"]["details"][0]["errorType"] == "COMMENT_EMPTY"


def test_comment_too_long(client: TestClient) -> None:
    r = analyze(client, comment={"text": "a" * 20481}, requestedAttributes={"TOXICITY": {}})
    assert r.json()["error"]["details"][0]["errorType"] == "COMMENT_TOO_LONG"


def test_no_requested_attributes(client: TestClient) -> None:
    r = analyze(client, comment={"text": "hi"})
    assert r.json()["error"]["details"][0]["errorType"] == "NO_REQUESTED_ATTRIBUTES"


def test_unsupported_score_type(client: TestClient) -> None:
    r = analyze(client, comment={"text": "hi"}, requestedAttributes={"TOXICITY": {"scoreType": "PERCENTILE"}})
    assert r.status_code == 400


def test_invalid_json(client: TestClient) -> None:
    r = client.post(ANALYZE, content=b"{not json", headers={"content-type": "application/json"})
    assert r.status_code == 400
    assert r.json()["error"]["status"] == "INVALID_ARGUMENT"


def test_undetectable_language_errors_without_a_fallback() -> None:
    c = make_client(default_language=None)
    r = analyze(c, comment={"text": "lol"}, requestedAttributes={"TOXICITY": {}})
    assert r.json()["error"]["details"][0]["errorType"] == "LANGUAGE_DETECTION_FAILED"


def test_low_confidence_detection_falls_back_to_the_default_language(client: TestClient) -> None:
    r = analyze(client, comment={"text": "lol"}, requestedAttributes={"TOXICITY": {}})
    assert r.json()["languages"] == ["en"]
