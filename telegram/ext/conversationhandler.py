#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
"""This module contains the ConversationHandler."""

import logging

from telegram import Update
from telegram.ext import (Handler, CallbackQueryHandler, InlineQueryHandler,
                          ChosenInlineResultHandler)
from telegram.utils.promise import Promise


class ConversationHandler(Handler):
    """
    A handler to hold a conversation with a single user by managing four collections of other
    handlers. Note that neither posts in Telegram Channels, nor group interactions with multiple
    users are managed by instances of this class.

    The first collection, a ``list`` named :attr:`entry_points`, is used to initiate the
    conversation, for example with a :class:`telegram.ext.CommandHandler` or
    :class:`telegram.ext.RegexHandler`.

    The second collection, a ``dict`` named :attr:`states`, contains the different conversation
    steps and one or more associated handlers that should be used if the user sends a message when
    the conversation with them is currently in that state. You will probably use mostly
    :class:`telegram.ext.MessageHandler` and :class:`telegram.ext.RegexHandler` here.

    The third collection, a ``list`` named :attr:`fallbacks`, is used if the user is currently in a
    conversation but the state has either no associated handler or the handler that is associated
    to the state is inappropriate for the update, for example if the update contains a command, but
    a regular text message is expected. You could use this for a ``/cancel`` command or to let the
    user know their message was not recognized.

    The fourth, optional collection of handlers, a ``list`` named :attr:`timed_out_behavior` is
    used if the wait for ``run_async`` takes longer than defined in :attr:`run_async_timeout`.
    For example, you can let the user know that they should wait for a bit before they can
    continue.

    To change the state of conversation, the callback function of a handler must return the new
    state after responding to the user. If it does not return anything (returning ``None`` by
    default), the state will not change. To end the conversation, the callback function must
    return :attr`END` or ``-1``.

    Attributes:
        entry_points (List[:class:`telegram.ext.Handler`]): A list of ``Handler`` objects that can
            trigger the start of the conversation.
        states (Dict[:obj:`object`, List[:class:`telegram.ext.Handler`]]): A :obj:`dict` that
            defines the different states of conversation a user can be in and one or more
            associated ``Handler`` objects that should be used in that state.
        fallbacks (List[:class:`telegram.ext.Handler`]): A list of handlers that might be used if
            the user is in a conversation, but every handler for their current state returned
            ``False`` on :attr:`check_update`.
        allow_reentry (:obj:`bool`): Optional. Determines if a user can restart a conversation with
            an entry point.
        run_async_timeout (:obj:`float`): Optional. The time-out for ``run_async`` decorated
            Handlers.
        timed_out_behavior (List[:class:`telegram.ext.Handler`]): Optional. A list of handlers that
            might be used if the wait for ``run_async`` timed out.
        per_chat (:obj:`bool`): Optional. If the conversationkey should contain the Chat's ID.
        per_user (:obj:`bool`): Optional. If the conversationkey should contain the User's ID.
        per_message (:obj:`bool`): Optional. If the conversationkey should contain the Message's
            ID.

    Args:
        entry_points (List[:class:`telegram.ext.Handler`]): A list of ``Handler`` objects that can
            trigger the start of the conversation. The first handler which :attr:`check_update`
            method returns ``True`` will be used. If all return ``False``, the update is not
            handled.
        states (Dict[:obj:`object`, List[:class:`telegram.ext.Handler`]]): A :obj:`dict` that
            defines the different states of conversation a user can be in and one or more
            associated ``Handler`` objects that should be used in that state. The first handler
            which :attr:`check_update` method returns ``True`` will be used.
        fallbacks (List[:class:`telegram.ext.Handler`]): A list of handlers that might be used if
            the user is in a conversation, but every handler for their current state returned
            ``False`` on :attr:`check_update`. The first handler which :attr:`check_update` method
            returns ``True`` will be used. If all return ``False``, the update is not handled.
        allow_reentry (:obj:`bool`, optional): If set to ``True``, a user that is currently in a
            conversation can restart the conversation by triggering one of the entry points.
        run_async_timeout (:obj:`float`, optional): If the previous handler for this user was
            running asynchronously using the ``run_async`` decorator, it might not be finished when
            the next message arrives. This timeout defines how long the conversation handler should
            wait for the next state to be computed. The default is ``None`` which means it will
            wait indefinitely.
        timed_out_behavior (List[:class:`telegram.ext.Handler`], optional): A list of handlers that
            might be used if the wait for ``run_async`` timed out. The first handler which
            :attr:`check_update` method returns ``True`` will be used. If all return ``False``,
            the update is not handled.
        per_chat (:obj:`bool`, optional): If the conversationkey should contain the Chat's ID.
            Default is ``True``.
        per_user (:obj:`bool`, optional): If the conversationkey should contain the User's ID.
            Default is ``True``.
        per_message (:obj:`bool`, optional): If the conversationkey should contain the Message's
            ID. Default is ``False``.

    Raises:
        ValueError

    """
    END = -1
    """:obj:`int`: Used as a constant to return when a conversation is ended."""

    def __init__(self,
                 entry_points,
                 states,
                 fallbacks,
                 allow_reentry=False,
                 run_async_timeout=None,
                 timed_out_behavior=None,
                 per_chat=True,
                 per_user=True,
                 per_message=False):

        self.entry_points = entry_points
        self.states = states
        self.fallbacks = fallbacks

        self.allow_reentry = allow_reentry
        self.run_async_timeout = run_async_timeout
        self.timed_out_behavior = timed_out_behavior
        self.per_user = per_user
        self.per_chat = per_chat
        self.per_message = per_message

        self.conversations = dict()
        self.current_conversation = None
        self.current_handler = None

        self.logger = logging.getLogger(__name__)

        if not any((self.per_user, self.per_chat, self.per_message)):
            raise ValueError("'per_user', 'per_chat' and 'per_message' can't all be 'False'")

        if self.per_message and not self.per_chat:
            logging.warning("If 'per_message=True' is used, 'per_chat=True' should also be used, "
                            "since message IDs are not globally unique.")

        all_handlers = list()
        all_handlers.extend(entry_points)
        all_handlers.extend(fallbacks)

        for state_handlers in states.values():
            all_handlers.extend(state_handlers)

        if self.per_message:
            for handler in all_handlers:
                if not isinstance(handler, CallbackQueryHandler):
                    logging.warning("If 'per_message=True', all entry points and state handlers"
                                    " must be 'CallbackQueryHandler', since no other handlers "
                                    "have a message context.")
        else:
            for handler in all_handlers:
                if isinstance(handler, CallbackQueryHandler):
                    logging.warning("If 'per_message=False', 'CallbackQueryHandler' will not be "
                                    "tracked for every message.")

        if self.per_chat:
            for handler in all_handlers:
                if isinstance(handler, (InlineQueryHandler, ChosenInlineResultHandler)):
                    logging.warning("If 'per_chat=True', 'InlineQueryHandler' can not be used, "
                                    "since inline queries have no chat context.")

    def _get_key(self, update):
        chat = update.effective_chat
        user = update.effective_user

        key = list()

        if self.per_chat:
            key.append(chat.id)

        if self.per_user and user is not None:
            key.append(user.id)

        if self.per_message:
            key.append(update.callback_query.inline_message_id
                       or update.callback_query.message.message_id)

        return tuple(key)

    def check_update(self, update):
        """
        Determines whether an update should be handled by this conversationhandler, and if so in
        which state the conversation currently is.

        Args:
            update (:class:`telegram.Update`): Incoming telegram update.

        Returns:
            :obj:`bool`

        """
        # Ignore messages in channels
        if (not isinstance(update, Update) or update.channel_post or self.per_chat
                and (update.inline_query or update.chosen_inline_result) or self.per_message
                and not update.callback_query or update.callback_query and self.per_chat
                and not update.callback_query.message):
            return False

        key = self._get_key(update)
        state = self.conversations.get(key)

        # Resolve promises
        if isinstance(state, tuple) and len(state) is 2 and isinstance(state[1], Promise):
            self.logger.debug('waiting for promise...')

            old_state, new_state = state
            error = False
            try:
                res = new_state.result(timeout=self.run_async_timeout)
            except Exception as exc:
                self.logger.exception("Promise function raised exception")
                self.logger.exception("{}".format(exc))
                error = True

            if not error and new_state.done.is_set():
                self.update_state(res, key)
                state = self.conversations.get(key)

            else:
                for candidate in (self.timed_out_behavior or []):
                    if candidate.check_update(update):
                        # Save the current user and the selected handler for handle_update
                        self.current_conversation = key
                        self.current_handler = candidate

                        return True

                else:
                    return False

        self.logger.debug('selecting conversation %s with state %s' % (str(key), str(state)))

        handler = None

        # Search entry points for a match
        if state is None or self.allow_reentry:
            for entry_point in self.entry_points:
                if entry_point.check_update(update):
                    handler = entry_point
                    break

            else:
                if state is None:
                    return False

        # Get the handler list for current state, if we didn't find one yet and we're still here
        if state is not None and not handler:
            handlers = self.states.get(state)

            for candidate in (handlers or []):
                if candidate.check_update(update):
                    handler = candidate
                    break

            # Find a fallback handler if all other handlers fail
            else:
                for fallback in self.fallbacks:
                    if fallback.check_update(update):
                        handler = fallback
                        break

                else:
                    return False

        # Save the current user and the selected handler for handle_update
        self.current_conversation = key
        self.current_handler = handler

        return True

    def handle_update(self, update, dispatcher):
        """Send the update to the callback for the current state and Handler

        Args:
            update (:class:`telegram.Update`): Incoming telegram update.
            dispatcher (:class:`telegram.ext.Dispatcher`): Dispatcher that originated the Update.

        """
        new_state = self.current_handler.handle_update(update, dispatcher)

        self.update_state(new_state, self.current_conversation)

    def update_state(self, new_state, key):
        if new_state == self.END:
            if key in self.conversations:
                del self.conversations[key]
            else:
                pass

        elif isinstance(new_state, Promise):
            self.conversations[key] = (self.conversations.get(key), new_state)

        elif new_state is not None:
            self.conversations[key] = new_state
