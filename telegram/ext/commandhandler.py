#!/usr/bin/env python
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
"""This module contains the CommandHandler class."""
import warnings

from future.utils import string_types

from .handler import Handler
from telegram import Update


class CommandHandler(Handler):
    """Handler class to handle Telegram commands.

    Commands are Telegram messages that start with ``/``, optionally followed by an ``@`` and the
    bot's name and/or some additional text.

    Attributes:
        command (:obj:`str` | List[:obj:`str`]): The command or list of commands this handler
            should listen for.
        callback (:obj:`callable`): The callback function for this handler.
        filters (:class:`telegram.ext.BaseFilter`): Optional. Only allow updates with these
            Filters.
        allow_edited (:obj:`bool`): Optional. Determines Whether the handler should also accept
            edited messages.
        pass_args (:obj:`bool`): Optional. Determines whether the handler should be passed
            ``args``.
        pass_update_queue (:obj:`bool`): Optional. Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Optional. Determines whether ``job_queue`` will be passed to
            the callback function.
        pass_user_data (:obj:`bool`): Optional. Determines whether ``user_data`` will be passed to
            the callback function.
        pass_chat_data (:obj:`bool`): Optional. Determines whether ``chat_data`` will be passed to
            the callback function.

    Note:
        :attr:`pass_user_data` and :attr:`pass_chat_data` determine whether a ``dict`` you
        can use to keep any data in will be sent to the :attr:`callback` function.. Related to
        either the user or the chat that the update was sent in. For each update from the same user
        or in the same chat, it will be the same ``dict``.

    Args:
        command (:obj:`str` | List[:obj:`str`]): The command or list of commands this handler
            should listen for.
        callback (:obj:`callable`): A function that takes ``bot, update`` as positional arguments.
            It will be called when the :attr:`check_update` has determined that an update should be
            processed by this handler.
        filters (:class:`telegram.ext.BaseFilter`, optional): A filter inheriting from
            :class:`telegram.ext.filters.BaseFilter`. Standard filters can be found in
            :class:`telegram.ext.filters.Filters`. Filters can be combined using bitwise
            operators (& for and, | for or, ~ for not).
        allow_edited (:obj:`bool`, optional): Determines whether the handler should also accept
            edited messages. Default is ``False``.
        pass_args (:obj:`bool`, optional): Determines whether the handler should be passed the
            arguments passed to the command as a keyword argument called ``args``. It will contain
            a list of strings, which is the text following the command split on single or
            consecutive whitespace characters. Default is ``False``
        pass_update_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the :class:`telegram.ext.Updater` and :class:`telegram.ext.Dispatcher`
            that contains new updates which can be used to insert updates. Default is ``False``.
        pass_job_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a
            :class:`telegram.ext.JobQueue` instance created by the :class:`telegram.ext.Updater`
            which can be used to schedule new jobs. Default is ``False``.
        pass_user_data (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``user_data`` will be passed to the callback function. Default is ``False``.
        pass_chat_data (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``chat_data`` will be passed to the callback function. Default is ``False``.

    """

    def __init__(self,
                 command,
                 callback,
                 filters=None,
                 allow_edited=False,
                 pass_args=False,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False):
        super(CommandHandler, self).__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data)

        if isinstance(command, string_types):
            self.command = [command.lower()]
        else:
            self.command = [x.lower() for x in command]
        self.filters = filters
        self.allow_edited = allow_edited
        self.pass_args = pass_args

        # We put this up here instead of with the rest of checking code
        # in check_update since we don't wanna spam a ton
        if isinstance(self.filters, list):
            warnings.warn('Using a list of filters in MessageHandler is getting '
                          'deprecated, please use bitwise operators (& and |) '
                          'instead. More info: https://git.io/vPTbc.')

    def check_update(self, update):
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:class:`telegram.Update`): Incoming telegram update.

        Returns:
            :obj:`bool`

        """
        if (isinstance(update, Update)
                and (update.message or update.edited_message and self.allow_edited)):
            message = update.message or update.edited_message

            if message.text and message.text.startswith('/') and len(message.text) > 1:
                first_word = message.text_html.split(None, 1)[0]
                if len(first_word) > 1 and first_word.startswith('/'):
                    command = first_word[1:].split('@')
                    command.append(
                        message.bot.username)  # in case the command was sent without a username

                    if not (command[0].lower() in self.command
                            and command[1].lower() == message.bot.username.lower()):
                        return False

                    if self.filters is None:
                        res = True
                    elif isinstance(self.filters, list):
                        res = any(func(message) for func in self.filters)
                    else:
                        res = self.filters(message)

                    return res

        return False

    def handle_update(self, update, dispatcher):
        """Send the update to the :attr:`callback`.

        Args:
            update (:class:`telegram.Update`): Incoming telegram update.
            dispatcher (:class:`telegram.ext.Dispatcher`): Dispatcher that originated the Update.

        """
        optional_args = self.collect_optional_args(dispatcher, update)

        message = update.message or update.edited_message

        if self.pass_args:
            optional_args['args'] = message.text.split()[1:]

        return self.callback(dispatcher.bot, update, **optional_args)
