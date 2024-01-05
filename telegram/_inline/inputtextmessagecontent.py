#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
"""This module contains the classes that represent Telegram InputTextMessageContent."""
from typing import Optional, Sequence, Tuple

from telegram._inline.inputmessagecontent import InputMessageContent
from telegram._linkpreviewoptions import LinkPreviewOptions
from telegram._messageentity import MessageEntity
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue
from telegram._utils.types import JSONDict, ODVInput
from telegram._utils.warnings import warn
from telegram.warnings import PTBDeprecationWarning


class InputTextMessageContent(InputMessageContent):
    """
    Represents the content of a text message to be sent as the result of an inline query.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`message_text` is equal.

    Examples:
        :any:`Inline Bot <examples.inlinebot>`

    Args:
        message_text (:obj:`str`): Text of the message to be sent,
            :tg-const:`telegram.constants.MessageLimit.MIN_TEXT_LENGTH`-
            :tg-const:`telegram.constants.MessageLimit.MAX_TEXT_LENGTH` characters after entities
            parsing.
        parse_mode (:obj:`str`, optional): |parse_mode|
        entities (Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|

            .. versionchanged:: 20.0
                |sequenceclassargs|

        disable_web_page_preview (:obj:`bool`, optional): Disables link previews for links in the
            sent message. Mutually exclusive with :paramref:`link_preview_options`.

            .. versionchanged:: NEXT.VERSION
                Bot API 7.0 introduced :paramref:`link_preview_options` replacing this
                argument. PTB will automatically convert this argument to that one, but
                you should update your code to use the new argument.

            .. deprecated:: NEXT.VERSION
                In future versions, this argument will become keyword only.

        link_preview_options (:obj:`LinkPreviewOptions`, optional): Link preview generation
            options for the message. Mutually exclusive with
            :paramref:`disable_web_page_preview`.

            .. versionadded:: NEXT.VERSION

    Attributes:
        message_text (:obj:`str`): Text of the message to be sent,
            :tg-const:`telegram.constants.MessageLimit.MIN_TEXT_LENGTH`-
            :tg-const:`telegram.constants.MessageLimit.MAX_TEXT_LENGTH` characters after entities
            parsing.
        parse_mode (:obj:`str`): Optional. |parse_mode|
        entities (Tuple[:class:`telegram.MessageEntity`]): Optional. |captionentitiesattr|

            .. versionchanged:: 20.0

                * |tupleclassattrs|
                * |alwaystuple|
        link_preview_options (:obj:`LinkPreviewOptions`): Optional. Link preview generation
            options for the message. Mutually exclusive with
            :attr:`disable_web_page_preview`.

            .. versionadded:: NEXT.VERSION

    """

    __slots__ = ("parse_mode", "entities", "message_text", "link_preview_options")

    def __init__(
        self,
        message_text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        entities: Optional[Sequence[MessageEntity]] = None,
        link_preview_options: ODVInput["LinkPreviewOptions"] = DEFAULT_NONE,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        if (
            disable_web_page_preview is not DEFAULT_NONE
            and link_preview_options is not DEFAULT_NONE
        ):
            raise ValueError(
                "`disable_web_page_preview` and `link_preview_options` are mutually exclusive."
            )

        # Convert to LinkPreviewOptions:
        if not isinstance(disable_web_page_preview, DefaultValue):
            link_preview_options = LinkPreviewOptions(is_disabled=disable_web_page_preview)

        with self._unfrozen():
            # Required
            self.message_text: str = message_text
            # Optionals
            self.parse_mode: ODVInput[str] = parse_mode
            self.entities: Tuple[MessageEntity, ...] = parse_sequence_arg(entities)
            self.link_preview_options = link_preview_options

            self._id_attrs = (self.message_text,)

    @property
    def disable_web_page_preview(self) -> Optional[bool]:
        """Optional[:obj:`bool`]: Disables link previews for links in the sent message.

        .. deprecated:: NEXT.VERSION
        """
        warn(
            "The `disable_web_page_preview` attribute is deprecated. "
            "Use `link_preview_options` instead.",
            PTBDeprecationWarning,
            stacklevel=2,
        )
        return (
            self.link_preview_options.is_disabled  # type: ignore[union-attr]
            if self.link_preview_options
            else None
        )
