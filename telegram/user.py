#!/usr/bin/env python
# pylint: disable=C0103,W0622
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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


class User(TelegramObject):
    """This object represents a Telegram user or bot.

    Attributes:
        id (:obj:`int`): Unique identifier for this user or bot.
        is_bot (:obj:`bool`): True, if this user is a bot
        first_name (:obj:`str`): User's or bot's first name.
        last_name (:obj:`str`): Optional. User's or bot's last name.
        username (:obj:`str`): Optional. User's or bot's username.
        language_code (:obj:`str`): Optional. IETF language tag of the user's language.
        bot (:class:`telegram.Bot`): Optional. The Bot to use for instance methods.

    Args:
        id (:obj:`int`): Unique identifier for this user or bot.
        is_bot (:obj:`bool`): True, if this user is a bot
        first_name (:obj:`str`): User's or bot's first name.
        last_name (:obj:`str`, optional): User's or bot's last name.
        username (:obj:`str`, optional): User's or bot's username.
        language_code (:obj:`str`, optional): IETF language tag of the user's language.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.

    """

    def __init__(self,
                 id,
                 first_name,
                 is_bot,
                 last_name=None,
                 username=None,
                 language_code=None,
                 bot=None,
                 **kwargs):
        # Required
        self.id = int(id)
        self.first_name = first_name
        self.is_bot = is_bot
        # Optionals
        self.last_name = last_name
        self.username = username
        self.language_code = language_code

        self.bot = bot

        self._id_attrs = (self.id,)

    @property
    def name(self):
        """
        :obj:`str`: Convenience property. If available, returns the user's :attr:`username`
            prefixed with "@". If :attr:`username` is not available, returns :attr:`full_name`.

        """
        if self.username:
            return '@{}'.format(self.username)
        return self.full_name

    @property
    def full_name(self):
        """
        :obj:`str`: Convenience property. The user's :attr:`first_name`, followed by (if available)
            :attr:`last_name`.

        """
        if self.last_name:
            return '{} {}'.format(self.first_name, self.last_name)
        return self.first_name

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super(User, cls).de_json(data, bot)

        return cls(bot=bot, **data)

    def get_profile_photos(self, *args, **kwargs):
        """
        Shortcut for::

                bot.get_user_profile_photos(update.message.from_user.id, *args, **kwargs)

        """

        return self.bot.get_user_profile_photos(self.id, *args, **kwargs)

    @classmethod
    def de_list(cls, data, bot):
        if not data:
            return []

        users = list()
        for user in data:
            users.append(cls.de_json(user, bot))

        return users

    def mention_markdown(self, name=None):
        """
        Args:
            name (:obj:`str`): If provided, will overwrite the user's name.

        Returns:
            :obj:`str`: The inline mention for the user as markdown.
        """
        if not name:
            return util_mention_markdown(self.id, self.name)
        else:
            return util_mention_markdown(self.id, name)

    def mention_html(self, name=None):
        """
        Args:
            name (:obj:`str`): If provided, will overwrite the user's name.

        Returns:
            :obj:`str`: The inline mention for the user as HTML.
        """
        if not name:
            return util_mention_html(self.id, self.name)
        else:
            return util_mention_html(self.id, name)

    def send_message(self, *args, **kwargs):
        """Shortcut for::

            bot.send_message(User.chat_id, *args, **kwargs)

        Where User is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_message(chat_id=self.id, *args, **kwargs)

    def send_photo(self, *args, **kwargs):
        """Shortcut for::

            bot.send_photo(User.chat_id, *args, **kwargs)

        Where User is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_photo(chat_id=self.id, *args, **kwargs)

    def send_audio(self, *args, **kwargs):
        """Shortcut for::

            bot.send_audio(User.chat_id, *args, **kwargs)

        Where User is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_audio(chat_id=self.id, *args, **kwargs)

    def send_document(self, *args, **kwargs):
        """Shortcut for::

            bot.send_document(User.chat_id, *args, **kwargs)

        Where User is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_document(chat_id=self.id, *args, **kwargs)

    def send_sticker(self, *args, **kwargs):
        """Shortcut for::

            bot.send_sticker(User.chat_id, *args, **kwargs)

        Where User is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_sticker(chat_id=self.id, *args, **kwargs)

    def send_video(self, *args, **kwargs):
        """Shortcut for::

            bot.send_video(User.chat_id, *args, **kwargs)

        Where User is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_video(chat_id=self.id, *args, **kwargs)

    def send_video_note(self, *args, **kwargs):
        """Shortcut for::

            bot.send_video_note(User.chat_id, *args, **kwargs)

        Where User is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_video_note(chat_id=self.id, *args, **kwargs)

    def send_voice(self, *args, **kwargs):
        """Shortcut for::

            bot.send_voice(User.chat_id, *args, **kwargs)

        Where User is the current instance.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_voice(chat_id=self.id, *args, **kwargs)
