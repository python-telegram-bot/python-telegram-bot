# ruff: noqa: INP001
import pytest

pytest.importorskip("chango")

from changes.config import ChangoSectionChangeNote


def test_author_urls():
    assert ChangoSectionChangeNote.get_author_url("Copilot") == (
        "https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-on-github"
    )
    assert ChangoSectionChangeNote.get_author_url("harshil21") == "https://github.com/harshil21"
