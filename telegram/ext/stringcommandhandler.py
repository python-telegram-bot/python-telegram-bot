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
        pass_args (:obj:`bool`): Optional. Determines whether the handler should be passed
            ``args``.
        pass_update_queue (:obj:`bool`): Optional. Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Optional. Determines whether ``job_queue`` will be passed to
            the callback function.


    Args:
        command (:obj:`str`): The command this handler should listen for.
        callback (:obj:`callable`): A function that takes ``bot, update`` as positional arguments.
            It will be called when the :attr:`check_update` has determined that a command should be
            processed by this handler.
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
            class:`telegram.ext.JobQueue` instance created by the :class:`telegram.ext.Updater`
            which can be used to schedule new jobs. Default is ``False``.

    """

    def __init__(self,
                 command,
                 callback,
                 pass_args=False,
                 pass_update_queue=False,
                 pass_job_queue=False):
        super(StringCommandHandler, self).__init__(
            callback, pass_update_queue=pass_update_queue, pass_job_queue=pass_job_queue)
        self.command = command
        self.pass_args = pass_args

    def check_update(self, update):
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:obj:`str`): An incomming command.

        Returns:
            :obj:`bool`

        """

        return (isinstance(update, string_types) and update.startswith('/')
                and update[1:].split(' ')[0] == self.command)

    def handle_update(self, update, dispatcher):
        """Send the update to the :attr:`callback`.

        Args:
            update (:obj:`str`): An incomming command.
            dispatcher (:class:`telegram.ext.Dispatcher`): Dispatcher that originated the command.

        """

        optional_args = self.collect_optional_args(dispatcher)

        if self.pass_args:
            optional_args['args'] = update.split()[1:]

        return self.callback(dispatcher.bot, update, **optional_args)
