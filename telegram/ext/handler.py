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
"""This module contains the base class for handlers as used by the Dispatcher."""


class Handler(object):
    """The base class for all update handlers. Create custom handlers by inheriting from it.

    Attributes:
        callback (:obj:`callable`): The callback function for this handler.

    Args:
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature for context based API:

            ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.

    """

    def __init__(self, callback):
        self.callback = callback

    def check_update(self, update):
        """
        This method is called to determine if an update should be handled by
        this handler instance. It should always be overridden.

        Args:
            update (:obj:`str` | :class:`telegram.Update`): The update to be tested.

        Returns:
            Either ``None`` or ``False`` if the update should not be handled. Otherwise an object
            that will be passed to :attr:`handle_update` and :attr:`collect_additional_context`
            when the update gets handled.

        """
        raise NotImplementedError

    def handle_update(self, update, dispatcher, check_result, context):
        """
        This method is called if it was determined that an update should indeed
        be handled by this instance. Calls :attr:`self.callback` along with its respectful
        arguments. To work with the :class:`telegram.ext.ConversationHandler`, this method
        returns the value returned from ``self.callback``.
        Note that it can be overridden if needed by the subclassing handler.

        Args:
            update (:obj:`str` | :class:`telegram.Update`): The update to be handled.
            dispatcher (:class:`telegram.ext.Dispatcher`): The calling dispatcher.
            check_result: The result from :attr:`check_update`.
            context (:class:`telegram.ext.CallbackContext`): The callback context as provided by
                the calling dispatcher.

        """
        self.collect_additional_context(context, update, dispatcher, check_result)
        return self.callback(update, context)

    def collect_additional_context(self, context, update, dispatcher, check_result):
        """Prepares additional arguments for the context. Override if needed.

        Args:
            context (:class:`telegram.ext.CallbackContext`): The context object.
            update (:class:`telegram.Update`): The update to gather chat/user id from.
            dispatcher (:class:`telegram.ext.Dispatcher`): The calling dispatcher.
            check_result: The result (return value) from :attr:`check_update`.

        """
        pass
