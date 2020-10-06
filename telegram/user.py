#!/usr/bin/env python
# pylint: disable=C0103,W0622
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
"""This module contains an object that represents a Telegram User."""

from telegram import TelegramObject
from telegram.utils.helpers import mention_html as util_mention_html
from telegram.utils.helpers import mention_markdown as util_mention_markdown

from typing import Any, Optional, TYPE_CHECKING, List

if TYPE_CHECKING:
    from telegram import Bot, UserProfilePhotos, Message


class User(TelegramObject):
    """This object represents a Telegram user or bot.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Attributes:
        id (:obj:`int`): Unique identifier for this user or bot.
        is_bot (:obj:`bool`): :obj:`True`, if this user is a bot.
        first_name (:obj:`str`): User's or bot's first name.
        last_name (:obj:`str`): Optional. User's or bot's last name.
        username (:obj:`str`): Optional. User's or bot's username.
        language_code (:obj:`str`): Optional. IETF language tag of the user's language.
        can_join_groups (:obj:`str`): Optional. :obj:`True`, if the bot can be invited to groups.
            Returned only in :attr:`telegram.Bot.get_me` requests.
        can_read_all_group_messages (:obj:`str`): Optional. :obj:`True`, if privacy mode is
            disabled for the bot. Returned only in :attr:`telegram.Bot.get_me` requests.
        supports_inline_queries (:obj:`str`): Optional. :obj:`True`, if the bot supports inline
            queries. Returned only in :attr:`telegram.Bot.get_me` requests.
        bot (:class:`telegram.Bot`): Optional. The Bot to use for instance methods.

    Args:
        id (:obj:`int`): Unique identifier for this user or bot.
        is_bot (:obj:`bool`): :obj:`True`, if this user is a bot.
        first_name (:obj:`str`): User's or bot's first name.
        last_name (:obj:`str`, optional): User's or bot's last name.
        username (:obj:`str`, optional): User's or bot's username.
        language_code (:obj:`str`, optional): IETF language tag of the user's language.
        can_join_groups (:obj:`str`, optional): :obj:`True`, if the bot can be invited to groups.
            Returned only in :attr:`telegram.Bot.get_me` requests.
        can_read_all_group_messages (:obj:`str`, optional): :obj:`True`, if privacy mode is
            disabled for the bot. Returned only in :attr:`telegram.Bot.get_me` requests.
        supports_inline_queries (:obj:`str`, optional): :obj:`True`, if the bot supports inline
            queries. Returned only in :attr:`telegram.Bot.get_me` requests.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.

    """

    def __init__(self,
                 id: int,
                 first_name: str,
                 is_bot: bool,
                 last_name: str = None,
                 username: str = None,
                 language_code: str = None,
                 can_join_groups: bool = None,
                 can_read_all_group_messages: bool = None,
                 supports_inline_queries: bool = None,
                 bot: 'Bot' = None,
                 **kwargs: Any):
        # Required
        self.id = int(id)
        self.first_name = first_name
        self.is_bot = is_bot
        # Optionals
        self.last_name = last_name
        self.username = username
        self.language_code = language_code
        self.can_join_groups = can_join_groups
        self.can_read_all_group_messages = can_read_all_group_messages
        self.supports_inline_queries = supports_inline_queries
        self.bot = bot

        self._id_attrs = (self.id,)

    @property
    def name(self) -> str:
        """:obj:`str`: Convenience property. If available, returns the user's :attr:`username`
        prefixed with "@". If :attr:`username` is not available, returns :attr:`full_name`."""
        if self.username:
            return '@{}'.format(self.username)
        return self.full_name

    @property
    def full_name(self) -> str:
        """:obj:`str`: Convenience property. The user's :attr:`first_name`, followed by (if
        available) :attr:`last_name`."""

        if self.last_name:
            return u'{} {}'.format(self.first_name, self.last_name)
        return self.first_name

    @property
    def link(self) -> Optional[str]:
        """:obj:`str`: Convenience property. If :attr:`username` is available, returns a t.me link
        of the user."""

        if self.username:
            return "https://t.me/{}".format(self.username)
        return None

    def get_profile_photos(self, *args: Any, **kwargs: Any) -> 'UserProfilePhotos':
        """
        Shortcut for::

                bot.get_user_profile_photos(update.effective_user.id, *args, **kwargs)

        """

        return self.bot.get_user_profile_photos(self.id, *args, **kwargs)

    def mention_markdown(self, name: str = None) -> str:
        """
        Note:
            :attr:`telegram.ParseMode.MARKDOWN` is is a legacy mode, retained by Telegram for
            backward compatibility. You should use :meth:`mention_markdown_v2` instead.

        Args:
            name (:obj:`str`): The name used as a link for the user. Defaults to :attr:`full_name`.

        Returns:
            :obj:`str`: The inline mention for the user as markdown (version 1).

        """
        if name:
            return util_mention_markdown(self.id, name)
        return util_mention_markdown(self.id, self.full_name)

    def mention_markdown_v2(self, name: str = None) -> str:
        """
        Args:
            name (:obj:`str`): The name used as a link for the user. Defaults to :attr:`full_name`.

        Returns:
            :obj:`str`: The inline mention for the user as markdown (version 2).

        """
        if name:
            return util_mention_markdown(self.id, name, version=2)
        return util_mention_markdown(self.id, self.full_name, version=2)

    def mention_html(self, name: str = None) -> str:
        """
        Args:
            name (:obj:`str`): The name used as a link for the user. Defaults to :attr:`full_name`.

        Returns:
            :obj:`str`: The inline mention for the user as HTML.

        """
        if name:
            return util_mention_html(self.id, name)
        return util_mention_html(self.id, self.full_name)

    def send_message(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_message(self.id, *args, **kwargs)

    def send_photo(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_photo(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_photo(self.id, *args, **kwargs)

    def send_media_group(self, *args: Any, **kwargs: Any) -> List['Message']:
        """Shortcut for::

            bot.send_media_group(update.effective_user.id, *args, **kwargs)

        Returns:
            List[:class:`telegram.Message`:] On success, instance representing the message posted.

        """
        return self.bot.send_media_group(self.id, *args, **kwargs)

    def send_audio(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_audio(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_audio(self.id, *args, **kwargs)

    def send_chat_action(self, *args: Any, **kwargs: Any) -> bool:
        """Shortcut for::

            bot.send_chat_action(update.effective_user.id, *args, **kwargs)

        Returns:
            :obj:`True`: On success.

        """
        return self.bot.send_chat_action(self.id, *args, **kwargs)

    send_action = send_chat_action
    """Alias for :attr:`send_chat_action`"""

    def send_contact(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_contact(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_contact(self.id, *args, **kwargs)

    def send_dice(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_dice(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_dice(self.id, *args, **kwargs)

    def send_document(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_document(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_document(self.id, *args, **kwargs)

    def send_game(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_game(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_game(self.id, *args, **kwargs)

    def send_invoice(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_invoice(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_invoice(self.id, *args, **kwargs)

    def send_location(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_location(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_location(self.id, *args, **kwargs)

    def send_animation(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_animation(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_animation(self.id, *args, **kwargs)

    def send_sticker(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_sticker(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_sticker(self.id, *args, **kwargs)

    def send_video(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_video(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_video(self.id, *args, **kwargs)

    def send_venue(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_venue(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_venue(self.id, *args, **kwargs)

    def send_video_note(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_video_note(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_video_note(self.id, *args, **kwargs)

    def send_voice(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_voice(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_voice(self.id, *args, **kwargs)

    def send_poll(self, *args: Any, **kwargs: Any) -> 'Message':
        """Shortcut for::

            bot.send_poll(update.effective_user.id, *args, **kwargs)

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_poll(self.id, *args, **kwargs)
