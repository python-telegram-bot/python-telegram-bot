import pytest

from telegram import InputRichMessage


class TestInputRichMessage:
    def test_html_serialization(self):
        rich = InputRichMessage(html="<h1>Hello</h1>", is_rtl=False)
        assert rich.to_dict() == {"html": "<h1>Hello</h1>", "is_rtl": False}

    def test_markdown_serialization(self):
        rich = InputRichMessage(markdown="# Hello", skip_entity_detection=True)
        assert rich.to_dict() == {"markdown": "# Hello", "skip_entity_detection": True}

    def test_blocks_and_media_are_immutable_sequences(self):
        blocks = [{"type": "paragraph", "text": {"type": "plain", "text": "Hello"}}]
        media = [{"type": "photo", "media": "file-id"}]
        rich = InputRichMessage(blocks=blocks, media=media)
        assert isinstance(rich.blocks, tuple)
        assert isinstance(rich.media, tuple)
        assert rich.to_dict()["blocks"] == blocks

    @pytest.mark.parametrize(
        ("kwargs", "message"),
        [
            ({}, "Exactly one"),
            ({"html": "x", "markdown": "x"}, "Exactly one"),
            ({"blocks": []}, "must not be empty"),
        ],
    )
    def test_content_validation(self, kwargs, message):
        with pytest.raises(ValueError, match=message):
            InputRichMessage(**kwargs)

    def test_equality(self):
        assert InputRichMessage(html="<b>x</b>") == InputRichMessage(html="<b>x</b>")
        assert InputRichMessage(html="<b>x</b>") != InputRichMessage(markdown="**x**")
