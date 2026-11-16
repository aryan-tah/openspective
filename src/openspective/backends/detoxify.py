"""Detoxify models (Apache-2.0) from Hugging Face.

- `unitary/unbiased-toxic-roberta` scores every core attribute in English.
- `unitary/multilingual-toxic-xlm-roberta` scores TOXICITY in French, Spanish, Italian,
  Portuguese, Turkish and Russian. It was only trained for overall toxicity, so it is not
  used for the other attributes.
"""

from __future__ import annotations

import os
import threading
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from openspective.attributes import CORE

ENGLISH_MODEL = "unitary/unbiased-toxic-roberta"
MULTILINGUAL_MODEL = "unitary/multilingual-toxic-xlm-roberta"
MULTILINGUAL_LANGUAGES = frozenset({"fr", "es", "it", "pt", "tr", "ru"})

# Perspective attribute → Detoxify label.
ENGLISH_LABELS = {
    "TOXICITY": "toxicity",
    "SEVERE_TOXICITY": "severe_toxicity",
    "IDENTITY_ATTACK": "identity_attack",
    "INSULT": "insult",
    "PROFANITY": "obscene",
    "THREAT": "threat",
    "SEXUALLY_EXPLICIT": "sexual_explicit",
}

MAX_TOKENS = 512
STRIDE = 64
BATCH = 16


@dataclass
class _Model:
    tokenizer: Any
    model: Any
    labels: dict[str, int]


class DetoxifyBackend:
    name = "detoxify"

    def __init__(self, device: str | None = None, threads: int | None = None) -> None:
        self.device = device or os.environ.get("OPENSPECTIVE_DEVICE", "cpu")
        threads = threads or int(os.environ.get("OPENSPECTIVE_THREADS", "0"))
        if threads:
            import torch

            torch.set_num_threads(threads)
        self._models: dict[str, _Model] = {}
        self._lock = threading.Lock()

    def support(self) -> Mapping[str, frozenset[str]]:
        out = {attr: frozenset({"en"}) for attr in CORE}
        out["TOXICITY"] = frozenset({"en"} | MULTILINGUAL_LANGUAGES)
        return out

    def preload(self) -> None:
        self._get(ENGLISH_MODEL)
        self._get(MULTILINGUAL_MODEL)

    def _get(self, name: str) -> _Model:
        with self._lock:
            if name not in self._models:
                from transformers import AutoModelForSequenceClassification, AutoTokenizer

                tokenizer = AutoTokenizer.from_pretrained(name)
                model = AutoModelForSequenceClassification.from_pretrained(name).to(self.device).eval()
                labels = {label: int(i) for i, label in model.config.id2label.items()}
                self._models[name] = _Model(tokenizer, model, labels)
            return self._models[name]

    def score(self, texts: Sequence[str], language: str, attributes: set[str]) -> list[dict[str, float]]:
        if language == "en":
            m = self._get(ENGLISH_MODEL)
            columns = {attr: m.labels[ENGLISH_LABELS[attr]] for attr in attributes}
        else:
            m = self._get(MULTILINGUAL_MODEL)
            columns = {"TOXICITY": m.labels["toxic"]}
        probs = self._probabilities(m, texts)
        return [{attr: float(row[col]) for attr, col in columns.items()} for row in probs]

    def _probabilities(self, m: _Model, texts: Sequence[str]) -> list[list[float]]:
        """Sigmoid probabilities per text. Texts longer than the model's window are scored in
        overlapping windows and each label takes its highest window score, so a toxic sentence
        at the end of a long comment isn't cut off."""
        import torch

        enc = m.tokenizer(
            list(texts),
            truncation=True,
            max_length=MAX_TOKENS,
            stride=STRIDE,
            return_overflowing_tokens=True,
            padding=True,
            return_tensors="pt",
        )
        owners: list[int] = enc.pop("overflow_to_sample_mapping").tolist()
        inputs = {k: v.to(self.device) for k, v in enc.items() if k in ("input_ids", "attention_mask")}
        rows: list[list[float]] = []
        with torch.inference_mode():
            for start in range(0, len(owners), BATCH):
                batch = {k: v[start : start + BATCH] for k, v in inputs.items()}
                rows.extend(torch.sigmoid(m.model(**batch).logits).cpu().tolist())
        best: list[list[float] | None] = [None] * len(texts)
        for owner, row in zip(owners, rows, strict=True):
            current = best[owner]
            best[owner] = row if current is None else [max(a, b) for a, b in zip(current, row, strict=True)]
        return [r if r is not None else [] for r in best]
