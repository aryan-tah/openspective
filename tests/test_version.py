import openspective


def test_version_is_a_string() -> None:
    assert isinstance(openspective.__version__, str)
