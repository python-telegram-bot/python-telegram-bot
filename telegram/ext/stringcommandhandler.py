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
"""This module contains the StringCommandHandler class."""

from future.utils import string_types

from .handler import Handler


class StringCommandHandler(Handler):
    """Handler class to handle string commands. Commands are string updates that start with ``/``.

    Note:
        This handler is not used to handle Telegram :attr:`telegram.Update`, but strings manually
        put in the queue. For example to send messages with the bot using command line or API.

    Attributes:
        command (:obj:`str`): The command this handler should listen for.
        callback (:obj:`callable`): The callback function for this handler.
        pass_args (:obj:`bool`): Determines whether the handler should be passed
            ``args``.
        pass_update_queue (:obj:`bool`): Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Determines whether ``job_queue`` will be passed to
            the callback function.

    Args:
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature for context based API:

            ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        pass_args (:obj:`bool`, optional): Determines whether the handler should be passed the
            arguments passed to the command as a keyword argument called ``args``. It will contain
            a list of strings, which is the text following the command split on single or
            consecutive whitespace characters. Default is ``False``
            DEPRECATED: Please switch to context based callbacks.
        pass_update_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the :class:`telegram.ext.Updater` and :class:`telegram.ext.Dispatcher`
            that contains new updates which can be used to insert updates. Default is ``False``.
            DEPRECATED: Please switch to context based callbacks.
        pass_job_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a
            class:`telegram.ext.JobQueue` instance created by the :class:`telegram.ext.Updater`
            which can be used to schedule new jobs. Default is ``False``.
            DEPRECATED: Please switch to context based callbacks.

    """

    def __init__(self,
                 command,
                 callback,
                 pass_args=False,
                 pass_update_queue=False,
                 pass_job_queue=False):
        super(StringCommandHandler, self).__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue)
        self.command = command
        self.pass_args = pass_args

    def check_update(self, update):
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:obj:`str`): An incoming command.

        Returns:
            :obj:`bool`

        """
        if isinstance(update, string_types) and update.startswith('/'):
            args = update[1:].split(' ')
            if args[0] == self.command:
                return args[1:]

    def collect_optional_args(self, dispatcher, update=None, check_result=None):
        optional_args = super(StringCommandHandler, self).collect_optional_args(dispatcher,
                                                                                update,
                                                                                check_result)
        if self.pass_args:
            optional_args['args'] = check_result
        return optional_args

    def collect_additional_context(self, context, update, dispatcher, check_result):
        context.args = check_result
