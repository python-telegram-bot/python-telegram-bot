#!/usr/bin/env python
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
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains two objects used for request chats/users service messages."""
from typing import Optional, Sequence, Tuple

from telegram._bot import Bot
from telegram._files.photosize import PhotoSize
from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.types import JSONDict
from telegram._utils.warnings import warn
from telegram._utils.warnings_transition import (
    warn_about_deprecated_attr_in_property,
    build_deprecation_warning_message,
)
from telegram.warnings import PTBDeprecationWarning


class UsersShared(TelegramObject):
    """
    This object contains information about the user whose identifier was shared with the bot
    using a :class:`telegram.KeyboardButtonRequestUsers` button.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`request_id` and :attr:`user_ids` are equal.

    .. versionadded:: 20.8
       Bot API 7.0 replaces ``UserShared`` with this class. The only difference is that now
       the :attr:`user_ids` is a sequence instead of a single integer.

    Args:
        request_id (:obj:`int`): Identifier of the request.
        users (Sequence[:class:`telegram.SharedUser`]): Information about users shared with the
            bot. Mutually exclusive with :paramref:`user_ids`.

            .. versionadded:: NEXT.VERSION
        user_ids (Sequence[:obj:`int`], optional): Identifiers of the shared users. These numbers may have
            more than 32 significant bits and some programming languages may have difficulty/silent
            defects in interpreting them. But they have at most 52 significant bits, so 64-bit
            integers or double-precision float types are safe for storing these identifiers. The
            bot may not have access to the users and could be unable to use these identifiers,
            unless the users are already known to the bot by some other means. Mutually exclusive
            with :paramref:`users`.

            .. versionchanged:: NEXT.VERSION
                Bot API 7.2 introduced :paramref:`users` replacing this argument. PTB will
                automatically convert this to that one, but for advanced options, please use
                :paramref:`users` directly.

            .. deprecated:: NEXT.VERSION
                In future versions, this argument will become keyword only.

    Attributes:
        request_id (:obj:`int`): Identifier of the request.
        users (Sequence[:class:`telegram.SharedUser`]): Information about users shared with the
            bot. Mutually exclusive with :attr:`user_ids`.

            .. versionadded:: NEXT.VERSION
    """

    __slots__ = ("request_id", "users")

    def __init__(
        self,
        request_id: int,
        users: Sequence[SharedUser],
        user_ids: Optional[Sequence[int]] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.request_id: int = request_id
        self.users: Tuple[SharedUser, ...] = users
        self.user_ids: Optional[Tuple[int, ...]] = user_ids

        if user_ids is not None and users:
            raise ValueError("`users` and `user_ids` are mutually exclusive")

        if user_ids is not None:
            warn(
                build_deprecation_warning_message(
                    deprecated_name="user_ids",
                    new_name="users",
                    object_type="parameter",
                    bot_api_version="7.2",
                ),
                PTBDeprecationWarning,
                stacklevel=2,
            )

        self._id_attrs = (self.request_id, self.users)

        self._freeze()

    @property
    def user_ids(self) -> Optional[Tuple[int, ...]]:
        """
        Optional[Tuple[:obj:`int`]]:  Identifiers of the shared users. These numbers may have
        more than 32 significant bits and some programming languages may have difficulty/silent
        defects in interpreting them. But they have at most 52 significant bits, so 64-bit
        integers or double-precision float types are safe for storing these identifiers. The
        bot may not have access to the users and could be unable to use these identifiers,
        unless the users are already known to the bot by some other means.

        .. deprecated:: NEXT.VERSION
        """
        warn_about_deprecated_attr_in_property(
            deprecated_attr_name="user_ids",
            new_attr_name="users",
            bot_api_version="7.2",
            stacklevel=2,
        )
        return tuple(user.user_id for user in self.users)


class ChatShared(TelegramObject):
    """
    This object contains information about the chat whose identifier was shared with the bot
    using a :class:`telegram.KeyboardButtonRequestChat` button.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`request_id` and :attr:`chat_id` are equal.

    .. versionadded:: 20.1

    Args:
        request_id (:obj:`int`): Identifier of the request.
        chat_id (:obj:`int`): Identifier of the shared user. This number may be greater than 32
            bits and some programming languages may have difficulty/silent defects in interpreting
            it. But it is smaller than 52 bits, so a signed 64-bit integer or double-precision
            float type are safe for storing this identifier.
        title (:obj:`str`, optional): Title of the chat, if the title was requested by the bot.

            .. versionadded:: NEXT.VERSION
        username (:obj:`str`, optional): Username of the chat, if the username was requested by
            the bot and available.

            .. versionadded:: NEXT.VERSION
        photo (Sequence[:class:`telegram.PhotoSize`], optional): Available sizes of the chat photo,
            if the photo was requested by the bot

            .. versionadded:: NEXT.VERSION

    Attributes:
        request_id (:obj:`int`): Identifier of the request.
        chat_id (:obj:`int`): Identifier of the shared user. This number may be greater than 32
            bits and some programming languages may have difficulty/silent defects in interpreting
            it. But it is smaller than 52 bits, so a signed 64-bit integer or double-precision
            float type are safe for storing this identifier.
        title (:obj:`str`): Optional. Title of the chat, if the title was requested by the bot.

            .. versionadded:: NEXT.VERSION
        username (:obj:`str`): Optional. Username of the chat, if the username was requested by
            the bot and available.

            .. versionadded:: NEXT.VERSION
        photo (Tuple[:class:`telegram.PhotoSize`]): Optional. Available sizes of the chat photo,
            if the photo was requested by the bot

            .. versionadded:: NEXT.VERSION
    """

    __slots__ = ("chat_id", "request_id", "title", "username", "photo")

    def __init__(
        self,
        request_id: int,
        chat_id: int,
        title: Optional[str] = None,
        username: Optional[str] = None,
        photo: Optional[Sequence[PhotoSize]] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.request_id: int = request_id
        self.chat_id: int = chat_id
        self.title: Optional[str] = title
        self.username: Optional[str] = username
        self.photo: Optional[Tuple[PhotoSize, ...]] = parse_sequence_arg(photo)

        self._id_attrs = (self.request_id, self.chat_id)

        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["ChatShared"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["photo"] = PhotoSize.de_list(data.get("photo"), bot)
        return super().de_json(data=data, bot=bot)


class SharedUser(TelegramObject):
    """
    This object contains information about a user that was shared with the bot using a
    :class:`telegram.KeyboardButtonRequestUser` button.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`user_id` is equal.

    .. versionadded:: NEXT.VERSION

    Args:
        user_id (:obj:`int`): Identifier of the shared user. This number may have 32 significant
            bits and some programming languages may have difficulty/silent defects in interpreting
            it. But it has atmost 52 significant bits, so 64-bit integers or double-precision
            float types are safe for storing these identifiers. The bot may not have access to the
            user and could be unable to use this identifier, unless the user is already known to the
            bot by some other means.
        first_name (:obj:`str`, optional): First name of the user, if the name was requested by the bot.
        last_name (:obj:`str`, optional): Last name of the user, if the name was requested by the bot.
        username (:obj:`str`, optional): Username of the user, if the username was requested by the bot.
        photo (Sequence[:class:`telegram.PhotoSize`], optional): Available sizes of the chat photo, if
            the photo was requested by the bot.

    Attributes:
        user_id (:obj:`int`): Identifier of the shared user. This number may have 32 significant
            bits and some programming languages may have difficulty/silent defects in interpreting
            it. But it has atmost 52 significant bits, so 64-bit integers or double-precision
            float types are safe for storing these identifiers. The bot may not have access to the
            user and could be unable to use this identifier, unless the user is already known to the
            bot by some other means.
        first_name (:obj:`str`): Optional. First name of the user, if the name was requested by the bot.
        last_name (:obj:`str`): Optional. Last name of the user, if the name was requested by the bot.
        username (:obj:`str`): Optional. Username of the user, if the username was requested by the bot.
        photo (Tuple[:class:`telegram.PhotoSize`]): Optional. Available sizes of the chat photo, if
            the photo was requested by the bot.
    """

    __slots__ = ("user_id", "first_name", "last_name", "username", "photo")

    def __init__(
        self,
        ruser_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        photo: Optional[Sequence[PhotoSize]] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.user_id: int = user_id
        self.first_name: Optional[str] = first_name
        self.last_name: Optional[str] = title
        self.username: Optional[str] = username
        self.photo: Optional[Tuple[PhotoSize, ...]] = parse_sequence_arg(photo)

        self._id_attrs = self.user_id

        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["SharedUser"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["photo"] = PhotoSize.de_list(data.get("photo"), bot)
        return super().de_json(data=data, bot=bot)
