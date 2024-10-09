#!/usr/bin/env python
# pylint: disable=redefined-builtin
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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
# along with this program.  If not, see [http://www.gnu.org/licenses/]
"""This module contains the Telegram Business related classes."""

from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from telegram._chat import Chat
from telegram._files.location import Location
from telegram._files.sticker import Sticker
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.datetime import extract_tzinfo_from_defaults, from_timestamp
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class BusinessConnection(TelegramObject):
    """
    Describes the connection of the bot with a business account.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`id`, :attr:`user`, :attr:`user_chat_id`, :attr:`date`,
    :attr:`can_reply`, and :attr:`is_enabled` are equal.

    .. versionadded:: 21.1

    Args:
        id (:obj:`str`): Unique identifier of the business connection.
        user (:class:`telegram.User`): Business account user that created the business connection.
        user_chat_id (:obj:`int`): Identifier of a private chat with the user who created the
            business connection.
        date (:obj:`datetime.datetime`): Date the connection was established in Unix time.
        can_reply (:obj:`bool`): True, if the bot can act on behalf of the business account in
            chats that were active in the last 24 hours.
        is_enabled (:obj:`bool`): True, if the connection is active.

    Attributes:
        id (:obj:`str`): Unique identifier of the business connection.
        user (:class:`telegram.User`): Business account user that created the business connection.
        user_chat_id (:obj:`int`): Identifier of a private chat with the user who created the
            business connection.
        date (:obj:`datetime.datetime`): Date the connection was established in Unix time.
        can_reply (:obj:`bool`): True, if the bot can act on behalf of the business account in
            chats that were active in the last 24 hours.
        is_enabled (:obj:`bool`): True, if the connection is active.
    """

    __slots__ = (
        "can_reply",
        "date",
        "id",
        "is_enabled",
        "user",
        "user_chat_id",
    )

    def __init__(
        self,
        id: str,
        user: "User",
        user_chat_id: int,
        date: datetime,
        can_reply: bool,
        is_enabled: bool,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.id: str = id
        self.user: User = user
        self.user_chat_id: int = user_chat_id
        self.date: datetime = date
        self.can_reply: bool = can_reply
        self.is_enabled: bool = is_enabled

        self._id_attrs = (
            self.id,
            self.user,
            self.user_chat_id,
            self.date,
            self.can_reply,
            self.is_enabled,
        )

        self._freeze()

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["BusinessConnection"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        # Get the local timezone from the bot if it has defaults
        loc_tzinfo = extract_tzinfo_from_defaults(bot)

        data["date"] = from_timestamp(data.get("date"), tzinfo=loc_tzinfo)
        data["user"] = User.de_json(data.get("user"), bot)

        return super().de_json(data=data, bot=bot)


class BusinessMessagesDeleted(TelegramObject):
    """
    This object is received when messages are deleted from a connected business account.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`business_connection_id`, :attr:`message_ids`, and
    :attr:`chat` are equal.

    .. versionadded:: 21.1

    Args:
        business_connection_id (:obj:`str`): Unique identifier of the business connection.
        chat (:class:`telegram.Chat`): Information about a chat in the business account. The bot
            may not have access to the chat or the corresponding user.
        message_ids (Sequence[:obj:`int`]): A list of identifiers of the deleted messages in the
            chat of the business account.

    Attributes:
        business_connection_id (:obj:`str`): Unique identifier of the business connection.
        chat (:class:`telegram.Chat`): Information about a chat in the business account. The bot
            may not have access to the chat or the corresponding user.
        message_ids (tuple[:obj:`int`]): A list of identifiers of the deleted messages in the
            chat of the business account.
    """

    __slots__ = (
        "business_connection_id",
        "chat",
        "message_ids",
    )

    def __init__(
        self,
        business_connection_id: str,
        chat: Chat,
        message_ids: Sequence[int],
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.business_connection_id: str = business_connection_id
        self.chat: Chat = chat
        self.message_ids: tuple[int, ...] = parse_sequence_arg(message_ids)

        self._id_attrs = (
            self.business_connection_id,
            self.chat,
            self.message_ids,
        )

        self._freeze()

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["BusinessMessagesDeleted"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["chat"] = Chat.de_json(data.get("chat"), bot)

        return super().de_json(data=data, bot=bot)


class BusinessIntro(TelegramObject):
    """
    This object contains information about the start page settings of a Telegram Business account.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their
    :attr:`title`, :attr:`message` and :attr:`sticker` are equal.

    .. versionadded:: 21.1

    Args:
        title (:obj:`str`, optional): Title text of the business intro.
        message (:obj:`str`, optional): Message text of the business intro.
        sticker (:class:`telegram.Sticker`, optional): Sticker of the business intro.

    Attributes:
        title (:obj:`str`): Optional. Title text of the business intro.
        message (:obj:`str`): Optional. Message text of the business intro.
        sticker (:class:`telegram.Sticker`): Optional. Sticker of the business intro.
    """

    __slots__ = (
        "message",
        "sticker",
        "title",
    )

    def __init__(
        self,
        title: Optional[str] = None,
        message: Optional[str] = None,
        sticker: Optional[Sticker] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.title: Optional[str] = title
        self.message: Optional[str] = message
        self.sticker: Optional[Sticker] = sticker

        self._id_attrs = (self.title, self.message, self.sticker)

        self._freeze()

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["BusinessIntro"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["sticker"] = Sticker.de_json(data.get("sticker"), bot)

        return super().de_json(data=data, bot=bot)


class BusinessLocation(TelegramObject):
    """
    This object contains information about the location of a Telegram Business account.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their
    :attr:`address` is equal.

    .. versionadded:: 21.1

    Args:
        address (:obj:`str`): Address of the business.
        location (:class:`telegram.Location`, optional): Location of the business.

    Attributes:
        address (:obj:`str`): Address of the business.
        location (:class:`telegram.Location`): Optional. Location of the business.
    """

    __slots__ = (
        "address",
        "location",
    )

    def __init__(
        self,
        address: str,
        location: Optional[Location] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.address: str = address
        self.location: Optional[Location] = location

        self._id_attrs = (self.address,)

        self._freeze()

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["BusinessLocation"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["location"] = Location.de_json(data.get("location"), bot)

        return super().de_json(data=data, bot=bot)


class BusinessOpeningHoursInterval(TelegramObject):
    """
    This object describes an interval of time during which a business is open.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their
    :attr:`opening_minute` and :attr:`closing_minute` are equal.

    .. versionadded:: 21.1

    Examples:
        A day has (24 * 60 =) 1440 minutes, a week has (7 * 1440 =) 10080 minutes.
        Starting the the minute's sequence from Monday, example values of
        :attr:`opening_minute`, :attr:`closing_minute` will map to the following day times:

        * Monday - 8am to 8:30pm:
            - ``opening_minute = 480`` :guilabel:`8 * 60`
            - ``closing_minute = 1230`` :guilabel:`20 * 60 + 30`
        * Tuesday - 24 hours:
            - ``opening_minute = 1440`` :guilabel:`24 * 60`
            - ``closing_minute = 2879`` :guilabel:`2 * 24 * 60 - 1`
        * Sunday - 12am - 11:58pm:
            - ``opening_minute = 8640`` :guilabel:`6 * 24 * 60`
            - ``closing_minute = 10078`` :guilabel:`7 * 24 * 60 - 2`

    Args:
        opening_minute (:obj:`int`): The minute's sequence number in a week, starting on Monday,
            marking the start of the time interval during which the business is open;
            0 - 7 * 24 * 60.
        closing_minute (:obj:`int`): The minute's
            sequence number in a week, starting on Monday, marking the end of the time interval
            during which the business is open; 0 - 8 * 24 * 60

    Attributes:
        opening_minute (:obj:`int`): The minute's sequence number in a week, starting on Monday,
            marking the start of the time interval during which the business is open;
            0 - 7 * 24 * 60.
        closing_minute (:obj:`int`): The minute's
            sequence number in a week, starting on Monday, marking the end of the time interval
            during which the business is open; 0 - 8 * 24 * 60
    """

    __slots__ = ("_closing_time", "_opening_time", "closing_minute", "opening_minute")

    def __init__(
        self,
        opening_minute: int,
        closing_minute: int,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.opening_minute: int = opening_minute
        self.closing_minute: int = closing_minute

        self._opening_time: Optional[tuple[int, int, int]] = None
        self._closing_time: Optional[tuple[int, int, int]] = None

        self._id_attrs = (self.opening_minute, self.closing_minute)

        self._freeze()

    def _parse_minute(self, minute: int) -> tuple[int, int, int]:
        return (minute // 1440, minute % 1440 // 60, minute % 1440 % 60)

    @property
    def opening_time(self) -> tuple[int, int, int]:
        """Convenience attribute. A :obj:`tuple` parsed from :attr:`opening_minute`. It contains
        the `weekday`, `hour` and `minute` in the same ranges as :attr:`datetime.datetime.weekday`,
        :attr:`datetime.datetime.hour` and :attr:`datetime.datetime.minute`

        Returns:
            tuple[:obj:`int`, :obj:`int`, :obj:`int`]:
        """
        if self._opening_time is None:
            self._opening_time = self._parse_minute(self.opening_minute)
        return self._opening_time

    @property
    def closing_time(self) -> tuple[int, int, int]:
        """Convenience attribute. A :obj:`tuple` parsed from :attr:`closing_minute`. It contains
        the `weekday`, `hour` and `minute` in the same ranges as :attr:`datetime.datetime.weekday`,
        :attr:`datetime.datetime.hour` and :attr:`datetime.datetime.minute`

        Returns:
            tuple[:obj:`int`, :obj:`int`, :obj:`int`]:
        """
        if self._closing_time is None:
            self._closing_time = self._parse_minute(self.closing_minute)
        return self._closing_time


class BusinessOpeningHours(TelegramObject):
    """
    This object describes the opening hours of a business.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their
    :attr:`time_zone_name` and :attr:`opening_hours` are equal.

    .. versionadded:: 21.1

    Args:
        time_zone_name (:obj:`str`): Unique name of the time zone for which the opening
            hours are defined.
        opening_hours (Sequence[:class:`telegram.BusinessOpeningHoursInterval`]): List of
            time intervals describing business opening hours.

    Attributes:
        time_zone_name (:obj:`str`): Unique name of the time zone for which the opening
            hours are defined.
        opening_hours (Sequence[:class:`telegram.BusinessOpeningHoursInterval`]): List of
            time intervals describing business opening hours.
    """

    __slots__ = ("opening_hours", "time_zone_name")

    def __init__(
        self,
        time_zone_name: str,
        opening_hours: Sequence[BusinessOpeningHoursInterval],
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.time_zone_name: str = time_zone_name
        self.opening_hours: Sequence[BusinessOpeningHoursInterval] = parse_sequence_arg(
            opening_hours
        )

        self._id_attrs = (self.time_zone_name, self.opening_hours)

        self._freeze()

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["BusinessOpeningHours"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["opening_hours"] = BusinessOpeningHoursInterval.de_list(
            data.get("opening_hours"), bot
        )

        return super().de_json(data=data, bot=bot)
