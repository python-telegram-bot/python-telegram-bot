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
from typing import TYPE_CHECKING, Optional, Sequence, Tuple

from telegram._inline.inputmessagecontent import InputMessageContent
from telegram._messageentity import MessageEntity
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue
from telegram._utils.types import JSONDict, ODVInput
from telegram._utils.warnings_transition import (
    warn_about_deprecated_attr_in_property,
    warn_for_link_preview_options,
)

if TYPE_CHECKING:
    from telegram._linkpreviewoptions import LinkPreviewOptions


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

            .. versionchanged:: 20.8
                Bot API 7.0 introduced :paramref:`link_preview_options` replacing this
                argument. PTB will automatically convert this argument to that one, but
                for advanced options, please use :paramref:`link_preview_options` directly.

            .. deprecated:: 20.8
                In future versions, this argument will become keyword only.

        link_preview_options (:obj:`LinkPreviewOptions`, optional): Link preview generation
            options for the message. Mutually exclusive with
            :paramref:`disable_web_page_preview`.

            .. versionadded:: 20.8

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

            .. versionadded:: 20.8

    """

    __slots__ = ("entities", "link_preview_options", "message_text", "parse_mode")

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

        with self._unfrozen():
            # Required
            self.message_text: str = message_text
            # Optionals
            self.parse_mode: ODVInput[str] = parse_mode
            self.entities: Tuple[MessageEntity, ...] = parse_sequence_arg(entities)
            self.link_preview_options: ODVInput["LinkPreviewOptions"] = (
                warn_for_link_preview_options(disable_web_page_preview, link_preview_options)
            )

            self._id_attrs = (self.message_text,)

    @property
    def disable_web_page_preview(self) -> Optional[bool]:
        """Optional[:obj:`bool`]: Disables link previews for links in the sent message.

        .. deprecated:: 20.8
        """
        warn_about_deprecated_attr_in_property(
            deprecated_attr_name="disable_web_page_preview",
            new_attr_name="link_preview_options",
            bot_api_version="7.0",
            stacklevel=2,
        )
        if (
            isinstance(self.link_preview_options, DefaultValue)
            or self.link_preview_options is None
        ):
            return None
        return bool(self.link_preview_options.is_disabled)
