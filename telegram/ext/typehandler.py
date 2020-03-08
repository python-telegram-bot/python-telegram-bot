#!/usr/bin/env python
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
"""This module contains the TypeHandler class."""

from .handler import Handler


class TypeHandler(Handler):
    """Handler class to handle updates of custom types.

    Attributes:
        type (:obj:`type`): The ``type`` of updates this handler should process.
        callback (:obj:`callable`): The callback function for this handler.
        strict (:obj:`bool`): Use ``type`` instead of ``isinstance``. Default is ``False``.

    Args:
        type (:obj:`type`): The ``type`` of updates this handler should process, as
            determined by ``isinstance``
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature for context based API:

            ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        strict (:obj:`bool`, optional): Use ``type`` instead of ``isinstance``.
            Default is ``False``

    """

    def __init__(self, type, callback, strict=False):
        super(TypeHandler, self).__init__(callback)
        self.type = type
        self.strict = strict

    def check_update(self, update):
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:class:`telegram.Update`): Incoming telegram update.

        Returns:
            :obj:`bool`

        """
        if not self.strict:
            return isinstance(update, self.type)
        else:
            return type(update) is self.type
