"""Sentence spans, with offsets in UTF-16 code units as the Perspective API reports them."""

from __future__ import annotations

import re

# A sentence ends at terminal punctuation followed by whitespace, after CJK terminal punctuation
# (which isn't followed by a space), or at a newline.
_BOUNDARY = re.compile(r"(?<=[.!?…])[\"'”’)\]]*\s+|(?<=[。！？])\s*|\n+")


def sentences(text: str) -> list[tuple[int, int]]:
    """Python string index ranges `[begin, end)` of each sentence, without surrounding space."""
    out: list[tuple[int, int]] = []
    start = 0
    for m in _BOUNDARY.finditer(text):
        _append(text, start, m.start() if m.group(0).isspace() else m.end(), out)
        start = m.end()
    _append(text, start, len(text), out)
    return out


def _append(text: str, begin: int, end: int, out: list[tuple[int, int]]) -> None:
    while begin < end and text[begin].isspace():
        begin += 1
    while end > begin and text[end - 1].isspace():
        end -= 1
    if begin < end:
        out.append((begin, end))


def utf16_offsets(text: str) -> list[int]:
    """`offsets[i]` is the UTF-16 offset of Python index `i`; one extra entry for the end."""
    offsets = [0] * (len(text) + 1)
    pos = 0
    for i, ch in enumerate(text):
        offsets[i] = pos
        pos += 2 if ord(ch) > 0xFFFF else 1
    offsets[len(text)] = pos
    return offsets
