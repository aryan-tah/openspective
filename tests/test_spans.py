from openspective.spans import sentences, utf16_offsets


def cut(text: str) -> list[str]:
    return [text[b:e] for b, e in sentences(text)]


def test_splits_on_terminal_punctuation_and_newlines() -> None:
    assert cut("Hi there. How are you?  Fine!\nThanks") == ["Hi there.", "How are you?", "Fine!", "Thanks"]


def test_keeps_closing_quotes_with_their_sentence() -> None:
    assert cut('He said "no." Then left.') == ['He said "no."', "Then left."]


def test_does_not_split_decimals_or_urls() -> None:
    assert cut("It costs 3.50 at example.com today.") == ["It costs 3.50 at example.com today."]


def test_cjk_punctuation() -> None:
    assert cut("你好。你是谁？") == ["你好。", "你是谁？"]


def test_utf16_offsets_count_astral_characters_twice() -> None:
    assert utf16_offsets("a😀b") == [0, 1, 3, 4]
