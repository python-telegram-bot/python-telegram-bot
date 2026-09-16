#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains classes that represent Telegram Rich Messages and Rich Blocks."""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, ClassVar, Union

from telegram._copytextbutton import CopyTextButton
from telegram._disabledbutton import DisabledButton
from telegram._files.animation import Animation
from telegram._files.audio import Audio
from telegram._files.document import Document
from telegram._files.photosize import PhotoSize
from telegram._files.video import Video
from telegram._files.voice import Voice
from telegram._files.location import Location
from telegram._loginurl import LoginUrl
from telegram._switchinlinequerychosenchat import SwitchInlineQueryChosenChat
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.types import JSONDict
from telegram._webappinfo import WebAppInfo

from telegram._files.inputmedia import (
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
)

if TYPE_CHECKING:
    from telegram._files.inputfile import InputFile


class RichText(TelegramObject):
    """Base class for rich text elements.

    .. versionadded:: 22.9
    """

    __slots__ = ("type",)

    __DE_JSON_DISPATCH__: ClassVar[tuple[str, dict[str, str]] | None] = (
        "type",
        {
            "string": "RichTextPlain",
            "plain": "RichTextPlain",
            "bold": "RichTextBold",
            "italic": "RichTextItalic",
            "underline": "RichTextUnderline",
            "strikethrough": "RichTextStrikethrough",
            "spoiler": "RichTextSpoiler",
            "code": "RichTextCode",
            "preformatted": "RichTextPreformatted",
            "url": "RichTextUrl",
            "link": "RichTextLink",
            "mention": "RichTextMention",
            "hashtag": "RichTextHashtag",
            "cashtag": "RichTextCashtag",
            "bot_command": "RichTextBotCommand",
            "email_address": "RichTextEmailAddress",
            "phone_number": "RichTextPhoneNumber",
            "bank_card_number": "RichTextBankCardNumber",
            "custom_emoji": "RichTextCustomEmoji",
            "date_time": "RichTextDateTime",
            "button": "RichTextButton",
            "marked": "RichTextMarked",
            "reference": "RichTextReference",
            "reference_link": "RichTextReferenceLink",
            "anchor": "RichTextAnchor",
            "anchor_link": "RichTextAnchorLink",
            "mathematical_expression": "RichTextMathematicalExpression",
            "subscript": "RichTextSubscript",
            "superscript": "RichTextSuperscript",
            "text_mention": "RichTextTextMention",
        },
    )

    def __init__(self, type: str, *, api_kwargs: JSONDict | None = None):
        super().__init__(api_kwargs=api_kwargs)
        self.type: str = type
        self._id_attrs = (self.type,)

    @classmethod
    def de_json(cls, data: JSONDict | str | None, bot: Any | None = None) -> RichText | None:
        if data is None:
            return None
        if isinstance(data, str):
            return RichTextPlain(text=data)
        return super().de_json(data, bot=bot)


class RichMessageButton(TelegramObject):
    """This object represents a button in a RichMessage.

    .. versionadded:: 22.9
    """

    __slots__ = (
        "callback_data",
        "copy_text",
        "disabled",
        "login_url",
        "style",
        "switch_inline_query",
        "switch_inline_query_chosen_chat",
        "switch_inline_query_current_chat",
        "text",
        "url",
        "web_app",
    )

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        style: str | None = None,
        url: str | None = None,
        callback_data: str | None = None,
        web_app: WebAppInfo | None = None,
        login_url: LoginUrl | None = None,
        switch_inline_query: str | None = None,
        switch_inline_query_current_chat: str | None = None,
        switch_inline_query_chosen_chat: SwitchInlineQueryChosenChat | None = None,
        copy_text: CopyTextButton | None = None,
        disabled: DisabledButton | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.style: str | None = style
        self.url: str | None = url
        self.callback_data: str | None = callback_data
        self.web_app: WebAppInfo | None = web_app
        self.login_url: LoginUrl | None = login_url
        self.switch_inline_query: str | None = switch_inline_query
        self.switch_inline_query_current_chat: str | None = switch_inline_query_current_chat
        self.switch_inline_query_chosen_chat: SwitchInlineQueryChosenChat | None = (
            switch_inline_query_chosen_chat
        )
        self.copy_text: CopyTextButton | None = copy_text
        self.disabled: DisabledButton | None = disabled

        self._id_attrs = (
            self.text,
            self.style,
            self.url,
            self.callback_data,
            self.web_app,
            self.login_url,
            self.switch_inline_query,
            self.switch_inline_query_current_chat,
            self.switch_inline_query_chosen_chat,
            self.copy_text,
            self.disabled,
        )
        self._freeze()


class RichTextPlain(RichText):
    """Plain text element."""

    __slots__ = ("text",)

    def __init__(self, text: str, *, api_kwargs: JSONDict | None = None):
        super().__init__(type="string", api_kwargs=api_kwargs)
        self.text: str = text
        self._id_attrs = (self.type, self.text)
        self._freeze()

    def to_dict(self, *, recursive: bool = True) -> str:
        return self.text


RichTextString = RichTextPlain


class RichTextBold(RichText):
    """Bold text element."""

    __slots__ = ("text",)

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="bold", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self._id_attrs = (self.type, self.text)
        self._freeze()


class RichTextItalic(RichText):
    """Italic text element."""

    __slots__ = ("text",)

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="italic", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self._id_attrs = (self.type, self.text)
        self._freeze()


class RichTextUnderline(RichText):
    """Underline text element."""

    __slots__ = ("text",)

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="underline", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self._id_attrs = (self.type, self.text)
        self._freeze()


class RichTextStrikethrough(RichText):
    """Strikethrough text element."""

    __slots__ = ("text",)

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="strikethrough", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self._id_attrs = (self.type, self.text)
        self._freeze()


class RichTextSpoiler(RichText):
    """Spoiler text element."""

    __slots__ = ("text",)

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="spoiler", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self._id_attrs = (self.type, self.text)
        self._freeze()


class RichTextCode(RichText):
    """Inline code text element."""

    __slots__ = ("text",)

    def __init__(self, text: str, *, api_kwargs: JSONDict | None = None):
        super().__init__(type="code", api_kwargs=api_kwargs)
        self.text: str = text
        self._id_attrs = (self.type, self.text)
        self._freeze()


class RichTextPreformatted(RichText):
    """Preformatted text element."""

    __slots__ = ("language", "text")

    def __init__(
        self,
        text: str,
        language: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="preformatted", api_kwargs=api_kwargs)
        self.text: str = text
        self.language: str | None = language
        self._id_attrs = (self.type, self.text, self.language)
        self._freeze()


class RichTextMention(RichText):
    """Mention text element."""

    __slots__ = ("text", "username")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        username: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="mention", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.username: str = username if username is not None else (text if isinstance(text, str) else "")
        self._id_attrs = (self.type, self.text, self.username)
        self._freeze()


class RichTextHashtag(RichText):
    """Hashtag text element."""

    __slots__ = ("hashtag", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        hashtag: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="hashtag", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.hashtag: str = hashtag if hashtag is not None else (text if isinstance(text, str) else "")
        self._id_attrs = (self.type, self.text, self.hashtag)
        self._freeze()


class RichTextCashtag(RichText):
    """Cashtag text element."""

    __slots__ = ("cashtag", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        cashtag: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="cashtag", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.cashtag: str = cashtag if cashtag is not None else (text if isinstance(text, str) else "")
        self._id_attrs = (self.type, self.text, self.cashtag)
        self._freeze()


class RichTextBotCommand(RichText):
    """Bot command text element."""

    __slots__ = ("bot_command", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        bot_command: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="bot_command", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.bot_command: str = bot_command if bot_command is not None else (text if isinstance(text, str) else "")
        self._id_attrs = (self.type, self.text, self.bot_command)
        self._freeze()


class RichTextUrl(RichText):
    """URL text element."""

    __slots__ = ("text", "url")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        url: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="url", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.url: str = url if url is not None else (text if isinstance(text, str) else "")
        self._id_attrs = (self.type, self.text, self.url)
        self._freeze()


RichTextLink = RichTextUrl


class RichTextEmailAddress(RichText):
    """Email address text element."""

    __slots__ = ("email_address", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        email_address: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="email_address", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.email_address: str = email_address if email_address is not None else (text if isinstance(text, str) else "")
        self._id_attrs = (self.type, self.text, self.email_address)
        self._freeze()


class RichTextPhoneNumber(RichText):
    """Phone number text element."""

    __slots__ = ("phone_number", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        phone_number: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="phone_number", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.phone_number: str = phone_number if phone_number is not None else (text if isinstance(text, str) else "")
        self._id_attrs = (self.type, self.text, self.phone_number)
        self._freeze()


class RichTextBankCardNumber(RichText):
    """Bank card number text element."""

    __slots__ = ("bank_card_number", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        bank_card_number: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="bank_card_number", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.bank_card_number: str = bank_card_number if bank_card_number is not None else (text if isinstance(text, str) else "")
        self._id_attrs = (self.type, self.text, self.bank_card_number)
        self._freeze()


class RichTextCustomEmoji(RichText):
    """Custom emoji text element."""

    __slots__ = ("alternative_text", "custom_emoji_id")

    def __init__(
        self,
        custom_emoji_id: str,
        alternative_text: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="custom_emoji", api_kwargs=api_kwargs)
        self.custom_emoji_id: str = custom_emoji_id
        self.alternative_text: str | None = alternative_text
        self._id_attrs = (self.type, self.custom_emoji_id, self.alternative_text)
        self._freeze()


class RichTextDateTime(RichText):
    """Formatted date and time text element."""

    __slots__ = ("date_time_format", "text", "unix_time")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        unix_time: int,
        date_time_format: str,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="date_time", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.unix_time: int = unix_time
        self.date_time_format: str = date_time_format
        self._id_attrs = (self.type, self.text, self.unix_time, self.date_time_format)
        self._freeze()


class RichTextButton(RichText):
    """A button text element.

    .. versionadded:: 22.9
    """

    __slots__ = ("button",)

    def __init__(self, button: RichMessageButton, *, api_kwargs: JSONDict | None = None):
        super().__init__(type="button", api_kwargs=api_kwargs)
        self.button: RichMessageButton = button
        self._id_attrs = (self.type, self.button)
        self._freeze()


class RichTextMarked(RichText):
    """Marked text element."""

    __slots__ = ("text",)

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="marked", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self._id_attrs = (self.type, self.text)
        self._freeze()


class RichTextReference(RichText):
    """Reference text element."""

    __slots__ = ("name", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        name: str,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="reference", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.name: str = name
        self._id_attrs = (self.type, self.text, self.name)
        self._freeze()


class RichTextReferenceLink(RichText):
    """Reference link text element."""

    __slots__ = ("reference_name", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        reference_name: str,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="reference_link", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.reference_name: str = reference_name
        self._id_attrs = (self.type, self.text, self.reference_name)
        self._freeze()


class RichTextAnchor(RichText):
    """Anchor text element."""

    __slots__ = ("name",)

    def __init__(self, name: str, *, api_kwargs: JSONDict | None = None):
        super().__init__(type="anchor", api_kwargs=api_kwargs)
        self.name: str = name
        self._id_attrs = (self.type, self.name)
        self._freeze()


class RichTextAnchorLink(RichText):
    """Anchor link text element."""

    __slots__ = ("anchor_name", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        anchor_name: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="anchor_link", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.anchor_name: str | None = anchor_name
        self._id_attrs = (self.type, self.text, self.anchor_name)
        self._freeze()


class RichTextMathematicalExpression(RichText):
    """Mathematical expression text element."""

    __slots__ = ("expression",)

    def __init__(self, expression: str, *, api_kwargs: JSONDict | None = None):
        super().__init__(type="mathematical_expression", api_kwargs=api_kwargs)
        self.expression: str = expression
        self._id_attrs = (self.type, self.expression)
        self._freeze()


class RichTextSubscript(RichText):
    """Subscript text element."""

    __slots__ = ("text",)

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="subscript", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self._id_attrs = (self.type, self.text)
        self._freeze()


class RichTextSuperscript(RichText):
    """Superscript text element."""

    __slots__ = ("text",)

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="superscript", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self._id_attrs = (self.type, self.text)
        self._freeze()


class RichTextTextMention(RichText):
    """Mention of a Telegram user by their identifier text element."""

    __slots__ = ("text", "user")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        user: User,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="text_mention", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.user: User = user
        self._id_attrs = (self.type, self.text, self.user)
        self._freeze()


class RichBlock(TelegramObject):
    """Base class for rich message blocks.

    .. versionadded:: 22.9
    """

    __slots__ = ("type",)

    __DE_JSON_DISPATCH__: ClassVar[tuple[str, dict[str, str]] | None] = (
        "type",
        {
            "paragraph": "RichBlockParagraph",
            "heading": "RichBlockSectionHeading",
            "pre": "RichBlockPreformatted",
            "footer": "RichBlockFooter",
            "divider": "RichBlockDivider",
            "mathematical_expression": "RichBlockMathematicalExpression",
            "anchor": "RichBlockAnchor",
            "list": "RichBlockList",
            "blockquote": "RichBlockBlockQuotation",
            "expandable_blockquote": "RichBlockExpandableBlockQuotation",
            "pullquote": "RichBlockPullQuotation",
            "table": "RichBlockTable",
            "collage": "RichBlockCollage",
            "slideshow": "RichBlockSlideshow",
            "details": "RichBlockDetails",
            "map": "RichBlockMap",
            "buttons": "RichBlockButtons",
            "animation": "RichBlockAnimation",
            "audio": "RichBlockAudio",
            "document": "RichBlockDocument",
            "photo": "RichBlockPhoto",
            "video": "RichBlockVideo",
            "voice_note": "RichBlockVoiceNote",
            "thinking": "RichBlockThinking",
        },
    )

    def __init__(self, type: str, *, api_kwargs: JSONDict | None = None):
        super().__init__(api_kwargs=api_kwargs)
        self.type: str = type
        self._id_attrs = (self.type,)


class RichBlockParagraph(RichBlock):
    """Paragraph rich block."""

    __slots__ = ("text",)

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="paragraph", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self._id_attrs = (self.type, self.text)
        self._freeze()


class RichBlockSectionHeading(RichBlock):
    """Section heading rich block."""

    __slots__ = ("size", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        size: int | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="heading", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.size: int | None = size
        self._id_attrs = (self.type, self.text, self.size)
        self._freeze()


class RichBlockPreformatted(RichBlock):
    """Preformatted rich block."""

    __slots__ = ("language", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        language: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="pre", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.language: str | None = language
        self._id_attrs = (self.type, self.text, self.language)
        self._freeze()


class RichBlockFooter(RichBlock):
    """Footer rich block."""

    __slots__ = ("text",)

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="footer", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self._id_attrs = (self.type, self.text)
        self._freeze()


class RichBlockDivider(RichBlock):
    """Divider rich block."""

    __slots__ = ()

    def __init__(self, *, api_kwargs: JSONDict | None = None):
        super().__init__(type="divider", api_kwargs=api_kwargs)
        self._id_attrs = (self.type,)
        self._freeze()


class RichBlockMathematicalExpression(RichBlock):
    """Mathematical expression rich block."""

    __slots__ = ("expression",)

    def __init__(self, expression: str, *, api_kwargs: JSONDict | None = None):
        super().__init__(type="mathematical_expression", api_kwargs=api_kwargs)
        self.expression: str = expression
        self._id_attrs = (self.type, self.expression)
        self._freeze()


class RichBlockAnchor(RichBlock):
    """Anchor rich block."""

    __slots__ = ("name",)

    def __init__(self, name: str, *, api_kwargs: JSONDict | None = None):
        super().__init__(type="anchor", api_kwargs=api_kwargs)
        self.name: str = name
        self._id_attrs = (self.type, self.name)
        self._freeze()


class RichBlockListItem(TelegramObject):
    """An item of a list."""

    __slots__ = ("blocks", "has_checkbox", "is_checked", "label", "type", "value")

    def __init__(
        self,
        label: str,
        blocks: Sequence[RichBlock],
        has_checkbox: bool | None = None,
        is_checked: bool | None = None,
        value: int | None = None,
        type: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.label: str = label
        self.blocks: tuple[RichBlock, ...] = parse_sequence_arg(blocks)
        self.has_checkbox: bool | None = has_checkbox
        self.is_checked: bool | None = is_checked
        self.value: int | None = value
        self.type: str | None = type
        self._id_attrs = (
            self.label,
            self.blocks,
            self.has_checkbox,
            self.is_checked,
            self.value,
            self.type,
        )
        self._freeze()


class RichBlockList(RichBlock):
    """List rich block."""

    __slots__ = ("items",)

    def __init__(
        self,
        items: Sequence[RichBlockListItem],
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="list", api_kwargs=api_kwargs)
        self.items: tuple[RichBlockListItem, ...] = parse_sequence_arg(items)
        self._id_attrs = (self.type, self.items)
        self._freeze()


class RichBlockBlockQuotation(RichBlock):
    """Block quotation rich block."""

    __slots__ = ("blocks", "credit", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText], None] = None,
        credit: Union[str, RichText, Sequence[RichText], None] = None,
        blocks: Sequence[RichBlock] | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="blockquote", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText], None] = text
        self.credit: Union[str, RichText, Sequence[RichText], None] = credit
        self.blocks: tuple[RichBlock, ...] | None = (
            parse_sequence_arg(blocks) if blocks is not None else None
        )
        self._id_attrs = (self.type, self.text, self.credit, self.blocks)
        self._freeze()


class RichBlockExpandableBlockQuotation(RichBlock):
    """A block quotation which can be expanded or collapsed back.

    .. versionadded:: 22.9
    """

    __slots__ = ("blocks", "credit", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText], None] = None,
        credit: Union[str, RichText, Sequence[RichText], None] = None,
        blocks: Sequence[RichBlock] | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="expandable_blockquote", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText], None] = text
        self.credit: Union[str, RichText, Sequence[RichText], None] = credit
        self.blocks: tuple[RichBlock, ...] | None = (
            parse_sequence_arg(blocks) if blocks is not None else None
        )
        self._id_attrs = (self.type, self.text, self.credit, self.blocks)
        self._freeze()


class RichBlockPullQuotation(RichBlock):
    """Pull quotation rich block."""

    __slots__ = ("credit", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        credit: Union[str, RichText, Sequence[RichText], None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="pullquote", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.credit: Union[str, RichText, Sequence[RichText], None] = credit
        self._id_attrs = (self.type, self.text, self.credit)
        self._freeze()


class RichBlockCaption(TelegramObject):
    """Caption of a rich formatted block."""

    __slots__ = ("credit", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        credit: Union[str, RichText, Sequence[RichText], None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.credit: Union[str, RichText, Sequence[RichText], None] = credit
        self._id_attrs = (self.text, self.credit)
        self._freeze()


class RichBlockCollage(RichBlock):
    """Collage rich block."""

    __slots__ = ("blocks", "caption")

    def __init__(
        self,
        blocks: Sequence[RichBlock],
        caption: RichBlockCaption | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="collage", api_kwargs=api_kwargs)
        self.blocks: tuple[RichBlock, ...] = parse_sequence_arg(blocks)
        self.caption: RichBlockCaption | None = caption
        self._id_attrs = (self.type, self.blocks, self.caption)
        self._freeze()


class RichBlockSlideshow(RichBlock):
    """Slideshow rich block."""

    __slots__ = ("blocks", "caption")

    def __init__(
        self,
        blocks: Sequence[RichBlock],
        caption: RichBlockCaption | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="slideshow", api_kwargs=api_kwargs)
        self.blocks: tuple[RichBlock, ...] = parse_sequence_arg(blocks)
        self.caption: RichBlockCaption | None = caption
        self._id_attrs = (self.type, self.blocks, self.caption)
        self._freeze()


class RichBlockDetails(RichBlock):
    """Details disclosure rich block."""

    __slots__ = ("blocks", "is_open", "summary")

    def __init__(
        self,
        summary: Union[str, RichText, Sequence[RichText]],
        blocks: Sequence[RichBlock],
        is_open: bool | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="details", api_kwargs=api_kwargs)
        self.summary: Union[str, RichText, Sequence[RichText]] = summary
        self.blocks: tuple[RichBlock, ...] = parse_sequence_arg(blocks)
        self.is_open: bool | None = is_open
        self._id_attrs = (self.type, self.summary, self.blocks, self.is_open)
        self._freeze()


class RichBlockMap(RichBlock):
    """Map rich block."""

    __slots__ = ("caption", "height", "location", "width", "zoom")

    def __init__(
        self,
        location: Location,
        zoom: int,
        width: int,
        height: int,
        caption: RichBlockCaption | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="map", api_kwargs=api_kwargs)
        self.location: Location = location
        self.zoom: int = zoom
        self.width: int = width
        self.height: int = height
        self.caption: RichBlockCaption | None = caption
        self._id_attrs = (
            self.type,
            self.location,
            self.zoom,
            self.width,
            self.height,
            self.caption,
        )
        self._freeze()


class RichBlockButtons(RichBlock):
    """A block containing a list of buttons shown in one row.

    .. versionadded:: 22.9
    """

    __slots__ = ("align", "buttons")

    def __init__(
        self,
        buttons: Sequence[RichMessageButton],
        align: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="buttons", api_kwargs=api_kwargs)
        self.buttons: tuple[RichMessageButton, ...] = parse_sequence_arg(buttons)
        self.align: str | None = align
        self._id_attrs = (self.type, self.buttons, self.align)
        self._freeze()


class RichBlockTableCell(TelegramObject):
    """A table cell in a rich block table."""

    __slots__ = ("align", "colspan", "rowspan", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        align: str | None = None,
        colspan: int | None = None,
        rowspan: int | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.align: str | None = align
        self.colspan: int | None = colspan
        self.rowspan: int | None = rowspan
        self._id_attrs = (self.text, self.align, self.colspan, self.rowspan)
        self._freeze()


class RichBlockTable(RichBlock):
    """A table rich block.

    .. versionadded:: 22.9
    """

    __slots__ = ("caption", "cells", "is_bordered", "is_compact", "is_striped")

    def __init__(
        self,
        cells: Sequence[Sequence[RichBlockTableCell]],
        is_bordered: bool | None = None,
        is_striped: bool | None = None,
        is_compact: bool | None = None,
        caption: Union[str, RichText, Sequence[RichText], None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="table", api_kwargs=api_kwargs)
        self.cells: tuple[tuple[RichBlockTableCell, ...], ...] = tuple(
            tuple(row) for row in cells
        )
        self.is_bordered: bool | None = is_bordered
        self.is_striped: bool | None = is_striped
        self.is_compact: bool | None = is_compact
        self.caption: Union[str, RichText, Sequence[RichText], None] = caption
        self._id_attrs = (
            self.type,
            self.cells,
            self.is_bordered,
            self.is_striped,
            self.is_compact,
            self.caption,
        )
        self._freeze()


class RichBlockDocument(RichBlock):
    """A rich block containing a file.

    .. versionadded:: 22.9
    """

    __slots__ = ("caption", "document")

    def __init__(
        self,
        document: Document,
        caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="document", api_kwargs=api_kwargs)
        self.document: Document = document
        self.caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = (
            caption
        )
        self._id_attrs = (self.type, self.document, self.caption)
        self._freeze()


class RichBlockPhoto(RichBlock):
    """Photo rich block."""

    __slots__ = ("caption", "has_spoiler", "photo")

    def __init__(
        self,
        photo: Sequence[PhotoSize],
        caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = None,
        has_spoiler: bool | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="photo", api_kwargs=api_kwargs)
        self.photo: tuple[PhotoSize, ...] = parse_sequence_arg(photo)
        self.caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = (
            caption
        )
        self.has_spoiler: bool | None = has_spoiler
        self._id_attrs = (self.type, self.photo, self.caption, self.has_spoiler)
        self._freeze()


class RichBlockVideo(RichBlock):
    """Video rich block."""

    __slots__ = ("caption", "has_spoiler", "video")

    def __init__(
        self,
        video: Video,
        caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = None,
        has_spoiler: bool | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="video", api_kwargs=api_kwargs)
        self.video: Video = video
        self.caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = (
            caption
        )
        self.has_spoiler: bool | None = has_spoiler
        self._id_attrs = (self.type, self.video, self.caption, self.has_spoiler)
        self._freeze()


class RichBlockAudio(RichBlock):
    """Audio rich block."""

    __slots__ = ("audio", "caption")

    def __init__(
        self,
        audio: Audio,
        caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="audio", api_kwargs=api_kwargs)
        self.audio: Audio = audio
        self.caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = (
            caption
        )
        self._id_attrs = (self.type, self.audio, self.caption)
        self._freeze()


class RichBlockAnimation(RichBlock):
    """Animation rich block."""

    __slots__ = ("animation", "caption", "has_spoiler")

    def __init__(
        self,
        animation: Animation,
        caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = None,
        has_spoiler: bool | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="animation", api_kwargs=api_kwargs)
        self.animation: Animation = animation
        self.caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = (
            caption
        )
        self.has_spoiler: bool | None = has_spoiler
        self._id_attrs = (self.type, self.animation, self.caption, self.has_spoiler)
        self._freeze()


class RichBlockVoiceNote(RichBlock):
    """Voice note rich block."""

    __slots__ = ("caption", "voice_note")

    def __init__(
        self,
        voice_note: Voice,
        caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="voice_note", api_kwargs=api_kwargs)
        self.voice_note: Voice = voice_note
        self.caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = (
            caption
        )
        self._id_attrs = (self.type, self.voice_note, self.caption)
        self._freeze()


class RichBlockThinking(RichBlock):
    """Thinking placeholder rich block."""

    __slots__ = ()

    def __init__(self, *, api_kwargs: JSONDict | None = None):
        super().__init__(type="thinking", api_kwargs=api_kwargs)
        self._id_attrs = (self.type,)
        self._freeze()


class InputRichBlock(TelegramObject):
    """Base class for input rich blocks.

    .. versionadded:: 22.9
    """

    __slots__ = ("type",)

    def __init__(self, type: str, *, api_kwargs: JSONDict | None = None):
        super().__init__(api_kwargs=api_kwargs)
        self.type: str = type
        self._id_attrs = (self.type,)


class InputRichBlockParagraph(InputRichBlock):
    """Input paragraph rich block."""

    __slots__ = ("text",)

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="paragraph", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self._id_attrs = (self.type, self.text)
        self._freeze()


class InputRichBlockSectionHeading(InputRichBlock):
    """Input section heading rich block."""

    __slots__ = ("size", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        size: int | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="heading", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.size: int | None = size
        self._id_attrs = (self.type, self.text, self.size)
        self._freeze()


class InputRichBlockPreformatted(InputRichBlock):
    """Input preformatted rich block."""

    __slots__ = ("language", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        language: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="pre", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.language: str | None = language
        self._id_attrs = (self.type, self.text, self.language)
        self._freeze()


class InputRichBlockFooter(InputRichBlock):
    """Input footer rich block."""

    __slots__ = ("text",)

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="footer", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self._id_attrs = (self.type, self.text)
        self._freeze()


class InputRichBlockDivider(InputRichBlock):
    """Input divider rich block."""

    __slots__ = ()

    def __init__(self, *, api_kwargs: JSONDict | None = None):
        super().__init__(type="divider", api_kwargs=api_kwargs)
        self._id_attrs = (self.type,)
        self._freeze()


class InputRichBlockButtons(InputRichBlock):
    """Input block containing a list of buttons.

    .. versionadded:: 22.9
    """

    __slots__ = ("align", "buttons")

    def __init__(
        self,
        buttons: Sequence[RichMessageButton],
        align: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="buttons", api_kwargs=api_kwargs)
        self.buttons: tuple[RichMessageButton, ...] = parse_sequence_arg(buttons)
        self.align: str | None = align
        self._id_attrs = (self.type, self.buttons, self.align)
        self._freeze()


class InputRichBlockTable(InputRichBlock):
    """Input table rich block.

    .. versionadded:: 22.9
    """

    __slots__ = ("caption", "cells", "is_bordered", "is_compact", "is_striped")

    def __init__(
        self,
        cells: Sequence[Sequence[RichBlockTableCell]],
        is_bordered: bool | None = None,
        is_striped: bool | None = None,
        is_compact: bool | None = None,
        caption: Union[str, RichText, Sequence[RichText], None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="table", api_kwargs=api_kwargs)
        self.cells: tuple[tuple[RichBlockTableCell, ...], ...] = tuple(
            tuple(row) for row in cells
        )
        self.is_bordered: bool | None = is_bordered
        self.is_striped: bool | None = is_striped
        self.is_compact: bool | None = is_compact
        self.caption: Union[str, RichText, Sequence[RichText], None] = caption
        self._id_attrs = (
            self.type,
            self.cells,
            self.is_bordered,
            self.is_striped,
            self.is_compact,
            self.caption,
        )
        self._freeze()


class InputRichBlockBlockQuotation(InputRichBlock):
    """Input block quotation rich block."""

    __slots__ = ("credit", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        credit: Union[str, RichText, Sequence[RichText], None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="blockquote", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.credit: Union[str, RichText, Sequence[RichText], None] = credit
        self._id_attrs = (self.type, self.text, self.credit)
        self._freeze()


class InputRichBlockExpandableBlockQuotation(InputRichBlock):
    """Input expandable block quotation rich block.

    .. versionadded:: 22.9
    """

    __slots__ = ("credit", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        credit: Union[str, RichText, Sequence[RichText], None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="expandable_blockquote", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.credit: Union[str, RichText, Sequence[RichText], None] = credit
        self._id_attrs = (self.type, self.text, self.credit)
        self._freeze()


class InputRichBlockDocument(InputRichBlock):
    """Input rich block containing a file.

    .. versionadded:: 22.9
    """

    __slots__ = ("caption", "document")

    def __init__(
        self,
        document: Union[str, "InputFile", "InputMediaDocument"],
        caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="document", api_kwargs=api_kwargs)
        if isinstance(document, str):
            self.document: Union[str, InputFile, InputMediaDocument] = InputMediaDocument(media=document)
        else:
            self.document = document
        if caption is not None and not isinstance(caption, RichBlockCaption):
            self.caption: RichBlockCaption | None = RichBlockCaption(text=caption)
        else:
            self.caption = caption
        self._id_attrs = (self.type, self.document, self.caption)
        self._freeze()


class InputRichBlockPhoto(InputRichBlock):
    """Input photo rich block.

    .. versionadded:: 22.9
    """

    __slots__ = ("caption", "has_spoiler", "photo")

    def __init__(
        self,
        photo: Union[str, "InputFile", "InputMediaPhoto"],
        caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = None,
        has_spoiler: bool | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="photo", api_kwargs=api_kwargs)
        if isinstance(photo, str):
            self.photo: Union[str, InputFile, InputMediaPhoto] = InputMediaPhoto(media=photo)
        else:
            self.photo = photo
        if caption is not None and not isinstance(caption, RichBlockCaption):
            self.caption: RichBlockCaption | None = RichBlockCaption(text=caption)
        else:
            self.caption = caption
        self.has_spoiler: bool | None = has_spoiler
        self._id_attrs = (self.type, self.photo, self.caption, self.has_spoiler)
        self._freeze()


class InputRichBlockAudio(InputRichBlock):
    """Input audio rich block.

    .. versionadded:: 22.9
    """

    __slots__ = ("audio", "caption")

    def __init__(
        self,
        audio: Union[str, "InputFile", "InputMediaAudio"],
        caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="audio", api_kwargs=api_kwargs)
        if isinstance(audio, str):
            self.audio: Union[str, InputFile, InputMediaAudio] = InputMediaAudio(media=audio)
        else:
            self.audio = audio
        if caption is not None and not isinstance(caption, RichBlockCaption):
            self.caption: RichBlockCaption | None = RichBlockCaption(text=caption)
        else:
            self.caption = caption
        self._id_attrs = (self.type, self.audio, self.caption)
        self._freeze()


class InputRichBlockVideo(InputRichBlock):
    """Input video rich block.

    .. versionadded:: 22.9
    """

    __slots__ = ("caption", "has_spoiler", "video")

    def __init__(
        self,
        video: Union[str, "InputFile", "InputMediaVideo"],
        caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = None,
        has_spoiler: bool | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="video", api_kwargs=api_kwargs)
        if isinstance(video, str):
            self.video: Union[str, InputFile, InputMediaVideo] = InputMediaVideo(media=video)
        else:
            self.video = video
        if caption is not None and not isinstance(caption, RichBlockCaption):
            self.caption: RichBlockCaption | None = RichBlockCaption(text=caption)
        else:
            self.caption = caption
        self.has_spoiler: bool | None = has_spoiler
        self._id_attrs = (self.type, self.video, self.caption, self.has_spoiler)
        self._freeze()


class InputRichBlockAnimation(InputRichBlock):
    """Input animation rich block.

    .. versionadded:: 22.9
    """

    __slots__ = ("animation", "caption", "has_spoiler")

    def __init__(
        self,
        animation: Union[str, "InputFile", "InputMediaAnimation"],
        caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = None,
        has_spoiler: bool | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="animation", api_kwargs=api_kwargs)
        if isinstance(animation, str):
            self.animation: Union[str, InputFile, InputMediaAnimation] = InputMediaAnimation(media=animation)
        else:
            self.animation = animation
        if caption is not None and not isinstance(caption, RichBlockCaption):
            self.caption: RichBlockCaption | None = RichBlockCaption(text=caption)
        else:
            self.caption = caption
        self.has_spoiler: bool | None = has_spoiler
        self._id_attrs = (self.type, self.animation, self.caption, self.has_spoiler)
        self._freeze()


class InputRichBlockCollage(InputRichBlock):
    """Input collage rich block.

    .. versionadded:: 22.9
    """

    __slots__ = ("blocks", "caption")

    def __init__(
        self,
        blocks: Sequence[InputRichBlock],
        caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="collage", api_kwargs=api_kwargs)
        self.blocks: tuple[InputRichBlock, ...] = parse_sequence_arg(blocks)
        if caption is not None and not isinstance(caption, RichBlockCaption):
            self.caption: RichBlockCaption | None = RichBlockCaption(text=caption)
        else:
            self.caption: RichBlockCaption | None = caption
        self._id_attrs = (self.type, self.blocks, self.caption)
        self._freeze()


class InputRichBlockSlideshow(InputRichBlock):
    """Input slideshow rich block.

    .. versionadded:: 22.9
    """

    __slots__ = ("blocks", "caption")

    def __init__(
        self,
        blocks: Sequence[InputRichBlock],
        caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="slideshow", api_kwargs=api_kwargs)
        self.blocks: tuple[InputRichBlock, ...] = parse_sequence_arg(blocks)
        if caption is not None and not isinstance(caption, RichBlockCaption):
            self.caption: RichBlockCaption | None = RichBlockCaption(text=caption)
        else:
            self.caption: RichBlockCaption | None = caption
        self._id_attrs = (self.type, self.blocks, self.caption)
        self._freeze()


class InputRichBlockThinking(InputRichBlock):
    """Input thinking placeholder rich block."""

    __slots__ = ("text",)

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText], None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="thinking", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText], None] = text
        self._id_attrs = (self.type, self.text)
        self._freeze()


class InputRichBlockMap(InputRichBlock):
    """Input map rich block."""

    __slots__ = ("caption", "height", "location", "width", "zoom")

    def __init__(
        self,
        location: Location,
        zoom: int | None = None,
        width: int | None = None,
        height: int | None = None,
        caption: Union[str, RichText, Sequence[RichText], RichBlockCaption, None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="map", api_kwargs=api_kwargs)
        self.location: Location = location
        self.zoom: int | None = zoom
        self.width: int | None = width
        self.height: int | None = height
        if caption is not None and not isinstance(caption, RichBlockCaption):
            self.caption: RichBlockCaption | None = RichBlockCaption(text=caption)
        else:
            self.caption: RichBlockCaption | None = caption
        self._id_attrs = (self.type, self.location, self.zoom, self.width, self.height, self.caption)
        self._freeze()


class InputRichBlockMathematicalExpression(InputRichBlock):
    """Input LaTeX math block."""

    __slots__ = ("expression",)

    def __init__(self, expression: str, *, api_kwargs: JSONDict | None = None):
        super().__init__(type="mathematical_expression", api_kwargs=api_kwargs)
        self.expression: str = expression
        self._id_attrs = (self.type, self.expression)
        self._freeze()


class InputRichBlockDetails(InputRichBlock):
    """Input collapsible details rich block."""

    __slots__ = ("blocks", "is_open", "summary")

    def __init__(
        self,
        summary: Union[str, RichText, Sequence[RichText]],
        blocks: Sequence[InputRichBlock],
        is_open: bool | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="details", api_kwargs=api_kwargs)
        self.summary: Union[str, RichText, Sequence[RichText]] = summary
        self.blocks: tuple[InputRichBlock, ...] = parse_sequence_arg(blocks)
        self.is_open: bool | None = is_open
        self._id_attrs = (self.type, self.summary, self.blocks, self.is_open)
        self._freeze()


class InputRichBlockListItem(TelegramObject):
    """An item in an input list block."""

    __slots__ = ("blocks", "has_checkbox", "is_checked", "type", "value")

    def __init__(
        self,
        blocks: Sequence[InputRichBlock],
        has_checkbox: bool | None = None,
        is_checked: bool | None = None,
        value: int | None = None,
        type: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.blocks: tuple[InputRichBlock, ...] = parse_sequence_arg(blocks)
        self.has_checkbox: bool | None = has_checkbox
        self.is_checked: bool | None = is_checked
        self.value: int | None = value
        self.type: str | None = type
        self._id_attrs = (self.blocks, self.has_checkbox, self.is_checked, self.value, self.type)
        self._freeze()


class InputRichBlockList(InputRichBlock):
    """Input list rich block."""

    __slots__ = ("items",)

    def __init__(
        self,
        items: Sequence[InputRichBlockListItem],
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="list", api_kwargs=api_kwargs)
        self.items: tuple[InputRichBlockListItem, ...] = parse_sequence_arg(items)
        self._id_attrs = (self.type, self.items)
        self._freeze()


class InputRichBlockPullQuotation(InputRichBlock):
    """Input pull quotation rich block.

    .. versionadded:: 22.9
    """

    __slots__ = ("credit", "text")

    def __init__(
        self,
        text: Union[str, RichText, Sequence[RichText]],
        credit: Union[str, RichText, Sequence[RichText], None] = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(type="pullquote", api_kwargs=api_kwargs)
        self.text: Union[str, RichText, Sequence[RichText]] = text
        self.credit: Union[str, RichText, Sequence[RichText], None] = credit
        self._id_attrs = (self.type, self.text, self.credit)
        self._freeze()


class RichMessage(TelegramObject):
    """This object represents a rich message.

    .. versionadded:: 22.9
    """

    __slots__ = ("blocks",)

    def __init__(
        self,
        blocks: Sequence[RichBlock],
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.blocks: tuple[RichBlock, ...] = parse_sequence_arg(blocks)
        self._id_attrs = (self.blocks,)
        self._freeze()


class InputRichMessage(TelegramObject):
    """This object represents the content of a rich message to be sent.

    .. versionadded:: 22.9
    """

    __slots__ = ("blocks", "html", "markdown")

    def __init__(
        self,
        blocks: Sequence[InputRichBlock] | None = None,
        html: str | None = None,
        markdown: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.blocks: tuple[InputRichBlock, ...] | None = (
            parse_sequence_arg(blocks) if blocks is not None else None
        )
        self.html: str | None = html
        self.markdown: str | None = markdown
        self._id_attrs = (self.blocks, self.html, self.markdown)
        self._freeze()
