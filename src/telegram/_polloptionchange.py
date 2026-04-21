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
"""This module contains objects related to poll option changes."""

from collections.abc import Sequence
from typing import TYPE_CHECKING

from telegram._messageentity import MessageEntity
from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import de_json_optional, de_list_optional, parse_sequence_arg
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot, MaybeInaccessibleMessage


class _PollOptionChange(TelegramObject):
    __slots__ = ("option_persistent_id", "option_text", "option_text_entities", "poll_message")

    def __init__(
        self,
        option_persistent_id: str,
        option_text: str,
        poll_message: "MaybeInaccessibleMessage | None" = None,
        option_text_entities: Sequence[MessageEntity] | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.poll_message: MaybeInaccessibleMessage | None = poll_message
        self.option_persistent_id: str = option_persistent_id
        self.option_text: str = option_text
        self.option_text_entities: tuple[MessageEntity, ...] = parse_sequence_arg(
            option_text_entities
        )

        self._id_attrs = (self.option_persistent_id, self.option_text, self.poll_message)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: "Bot | None" = None):
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        # Unfortunately, this needs to be here due to cyclic imports
        from telegram._message import (  # pylint: disable=C0415  # noqa: PLC0415
            MaybeInaccessibleMessage,
        )

        data["poll_message"] = de_json_optional(
            data.get("poll_message"), MaybeInaccessibleMessage, bot
        )
        data["option_text_entities"] = de_list_optional(
            data.get("option_text_entities"), MessageEntity, bot
        )

        return super().de_json(data=data, bot=bot)


class PollOptionAdded(_PollOptionChange):
    """Describes a service message about an option added to a poll.

    .. versionadded:: 22.8
    """

    __slots__ = ()


class PollOptionDeleted(_PollOptionChange):
    """Describes a service message about an option deleted from a poll.

    .. versionadded:: 22.8
    """

    __slots__ = ()
