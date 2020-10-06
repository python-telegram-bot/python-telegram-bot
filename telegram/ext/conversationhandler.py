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
"""This module contains the ConversationHandler."""

import logging
import warnings
from threading import Lock

from telegram import Update
from telegram.ext import (Handler, CallbackQueryHandler, InlineQueryHandler,
                          ChosenInlineResultHandler, CallbackContext, BasePersistence,
                          DispatcherHandlerStop)
from telegram.utils.promise import Promise

from telegram.utils.types import ConversationDict, HandlerArg
from typing import Dict, Any, List, Optional, Tuple, TYPE_CHECKING, cast, NoReturn

if TYPE_CHECKING:
    from telegram.ext import Dispatcher, Job
CheckUpdateType = Optional[Tuple[Tuple[int, ...], Handler, object]]


class _ConversationTimeoutContext:
    def __init__(self,
                 conversation_key: Tuple[int, ...],
                 update: Update,
                 dispatcher: 'Dispatcher',
                 callback_context: Optional[CallbackContext]):
        self.conversation_key = conversation_key
        self.update = update
        self.dispatcher = dispatcher
        self.callback_context = callback_context


class ConversationHandler(Handler):
    """
    A handler to hold a conversation with a single user by managing four collections of other
    handlers.

    The first collection, a ``list`` named :attr:`entry_points`, is used to initiate the
    conversation, for example with a :class:`telegram.ext.CommandHandler` or
    :class:`telegram.ext.MessageHandler`.

    The second collection, a ``dict`` named :attr:`states`, contains the different conversation
    steps and one or more associated handlers that should be used if the user sends a message when
    the conversation with them is currently in that state. Here you can also define a state for
    :attr:`TIMEOUT` to define the behavior when :attr:`conversation_timeout` is exceeded, and a
    state for :attr:`WAITING` to define behavior when a new update is received while the previous
    ``@run_async`` decorated handler is not finished.

    The third collection, a ``list`` named :attr:`fallbacks`, is used if the user is currently in a
    conversation but the state has either no associated handler or the handler that is associated
    to the state is inappropriate for the update, for example if the update contains a command, but
    a regular text message is expected. You could use this for a ``/cancel`` command or to let the
    user know their message was not recognized.

    To change the state of conversation, the callback function of a handler must return the new
    state after responding to the user. If it does not return anything (returning :obj:`None` by
    default), the state will not change. If an entry point callback function returns :obj:`None`,
    the conversation ends immediately after the execution of this callback function.
    To end the conversation, the callback function must return :attr:`END` or ``-1``. To
    handle the conversation timeout, use handler :attr:`TIMEOUT` or ``-2``.

    Note:
        In each of the described collections of handlers, a handler may in turn be a
        :class:`ConversationHandler`. In that case, the nested :class:`ConversationHandler` should
        have the attribute :attr:`map_to_parent` which allows to return to the parent conversation
        at specified states within the nested conversation.

        Note that the keys in :attr:`map_to_parent` must not appear as keys in :attr:`states`
        attribute or else the latter will be ignored. You may map :attr:`END` to one of the parents
        states to continue the parent conversation after this has ended or even map a state to
        :attr:`END` to end the *parent* conversation from within the nested one. For an example on
        nested :class:`ConversationHandler` s, see our `examples`_.

    .. _`examples`: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples

    Attributes:
        entry_points (List[:class:`telegram.ext.Handler`]): A list of ``Handler`` objects that can
            trigger the start of the conversation.
        states (Dict[:obj:`object`, List[:class:`telegram.ext.Handler`]]): A :obj:`dict` that
            defines the different states of conversation a user can be in and one or more
            associated ``Handler`` objects that should be used in that state.
        fallbacks (List[:class:`telegram.ext.Handler`]): A list of handlers that might be used if
            the user is in a conversation, but every handler for their current state returned
            :obj:`False` on :attr:`check_update`.
        allow_reentry (:obj:`bool`): Determines if a user can restart a conversation with
            an entry point.
        per_chat (:obj:`bool`): If the conversationkey should contain the Chat's ID.
        per_user (:obj:`bool`): If the conversationkey should contain the User's ID.
        per_message (:obj:`bool`): If the conversationkey should contain the Message's
            ID.
        conversation_timeout (:obj:`float` | :obj:`datetime.timedelta`): Optional. When this
            handler is inactive more than this timeout (in seconds), it will be automatically
            ended. If this value is 0 (default), there will be no timeout. When it's triggered, the
            last received update and the corresponding ``context`` will be handled by ALL the
            handler's who's :attr:`check_update` method returns :obj:`True` that are in the state
            :attr:`ConversationHandler.TIMEOUT`.
        name (:obj:`str`): Optional. The name for this conversationhandler. Required for
            persistence
        persistent (:obj:`bool`): Optional. If the conversations dict for this handler should be
            saved. Name is required and persistence has to be set in :class:`telegram.ext.Updater`
        map_to_parent (Dict[:obj:`object`, :obj:`object`]): Optional. A :obj:`dict` that can be
            used to instruct a nested conversationhandler to transition into a mapped state on
            its parent conversationhandler in place of a specified nested state.

    Args:
        entry_points (List[:class:`telegram.ext.Handler`]): A list of ``Handler`` objects that can
            trigger the start of the conversation. The first handler which :attr:`check_update`
            method returns :obj:`True` will be used. If all return :obj:`False`, the update is not
            handled.
        states (Dict[:obj:`object`, List[:class:`telegram.ext.Handler`]]): A :obj:`dict` that
            defines the different states of conversation a user can be in and one or more
            associated ``Handler`` objects that should be used in that state. The first handler
            which :attr:`check_update` method returns :obj:`True` will be used.
        fallbacks (List[:class:`telegram.ext.Handler`]): A list of handlers that might be used if
            the user is in a conversation, but every handler for their current state returned
            :obj:`False` on :attr:`check_update`. The first handler which :attr:`check_update`
            method returns :obj:`True` will be used. If all return :obj:`False`, the update is not
            handled.
        allow_reentry (:obj:`bool`, optional): If set to :obj:`True`, a user that is currently in a
            conversation can restart the conversation by triggering one of the entry points.
        per_chat (:obj:`bool`, optional): If the conversationkey should contain the Chat's ID.
            Default is :obj:`True`.
        per_user (:obj:`bool`, optional): If the conversationkey should contain the User's ID.
            Default is :obj:`True`.
        per_message (:obj:`bool`, optional): If the conversationkey should contain the Message's
            ID. Default is :obj:`False`.
        conversation_timeout (:obj:`float` | :obj:`datetime.timedelta`, optional): When this
            handler is inactive more than this timeout (in seconds), it will be automatically
            ended. If this value is 0 or :obj:`None` (default), there will be no timeout. The last
            received update and the corresponding ``context`` will be handled by ALL the handler's
            who's :attr:`check_update` method returns :obj:`True` that are in the state
            :attr:`ConversationHandler.TIMEOUT`.
        name (:obj:`str`, optional): The name for this conversationhandler. Required for
            persistence.
        persistent (:obj:`bool`, optional): If the conversations dict for this handler should be
            saved. Name is required and persistence has to be set in :class:`telegram.ext.Updater`
        map_to_parent (Dict[:obj:`object`, :obj:`object`], optional): A :obj:`dict` that can be
            used to instruct a nested conversationhandler to transition into a mapped state on
            its parent conversationhandler in place of a specified nested state.

    Raises:
        ValueError

    """
    END = -1
    """:obj:`int`: Used as a constant to return when a conversation is ended."""
    TIMEOUT = -2
    """:obj:`int`: Used as a constant to handle state when a conversation is timed out."""
    WAITING = -3
    """:obj:`int`: Used as a constant to handle state when a conversation is still waiting on the
    previous ``@run_sync`` decorated running handler to finish."""

    def __init__(self,
                 entry_points: List[Handler],
                 states: Dict[object, List[Handler]],
                 fallbacks: List[Handler],
                 allow_reentry: bool = False,
                 per_chat: bool = True,
                 per_user: bool = True,
                 per_message: bool = False,
                 conversation_timeout: int = None,
                 name: str = None,
                 persistent: bool = False,
                 map_to_parent: Dict[object, object] = None):
        self.run_async = False

        self._entry_points = entry_points
        self._states = states
        self._fallbacks = fallbacks

        self._allow_reentry = allow_reentry
        self._per_user = per_user
        self._per_chat = per_chat
        self._per_message = per_message
        self._conversation_timeout = conversation_timeout
        self._name = name
        if persistent and not self.name:
            raise ValueError("Conversations can't be persistent when handler is unnamed.")
        self.persistent: bool = persistent
        self._persistence: Optional[BasePersistence] = None
        """:obj:`telegram.ext.BasePersistence`: The persistence used to store conversations.
        Set by dispatcher"""
        self._map_to_parent = map_to_parent

        self.timeout_jobs: Dict[Tuple[int, ...], 'Job'] = dict()
        self._timeout_jobs_lock = Lock()
        self._conversations: ConversationDict = dict()
        self._conversations_lock = Lock()

        self.logger = logging.getLogger(__name__)

        if not any((self.per_user, self.per_chat, self.per_message)):
            raise ValueError("'per_user', 'per_chat' and 'per_message' can't all be 'False'")

        if self.per_message and not self.per_chat:
            warnings.warn("If 'per_message=True' is used, 'per_chat=True' should also be used, "
                          "since message IDs are not globally unique.")

        all_handlers = list()
        all_handlers.extend(entry_points)
        all_handlers.extend(fallbacks)

        for state_handlers in states.values():
            all_handlers.extend(state_handlers)

        if self.per_message:
            for handler in all_handlers:
                if not isinstance(handler, CallbackQueryHandler):
                    warnings.warn("If 'per_message=True', all entry points and state handlers"
                                  " must be 'CallbackQueryHandler', since no other handlers "
                                  "have a message context.")
                    break
        else:
            for handler in all_handlers:
                if isinstance(handler, CallbackQueryHandler):
                    warnings.warn("If 'per_message=False', 'CallbackQueryHandler' will not be "
                                  "tracked for every message.")
                    break

        if self.per_chat:
            for handler in all_handlers:
                if isinstance(handler, (InlineQueryHandler, ChosenInlineResultHandler)):
                    warnings.warn("If 'per_chat=True', 'InlineQueryHandler' can not be used, "
                                  "since inline queries have no chat context.")
                    break

    @property
    def entry_points(self) -> List[Handler]:
        return self._entry_points

    @entry_points.setter
    def entry_points(self, value: Any) -> NoReturn:
        raise ValueError('You can not assign a new value to entry_points after initialization.')

    @property
    def states(self) -> Dict[object, List[Handler]]:
        return self._states

    @states.setter
    def states(self, value: Any) -> NoReturn:
        raise ValueError('You can not assign a new value to states after initialization.')

    @property
    def fallbacks(self) -> List[Handler]:
        return self._fallbacks

    @fallbacks.setter
    def fallbacks(self, value: Any) -> NoReturn:
        raise ValueError('You can not assign a new value to fallbacks after initialization.')

    @property
    def allow_reentry(self) -> bool:
        return self._allow_reentry

    @allow_reentry.setter
    def allow_reentry(self, value: Any) -> NoReturn:
        raise ValueError('You can not assign a new value to allow_reentry after initialization.')

    @property
    def per_user(self) -> bool:
        return self._per_user

    @per_user.setter
    def per_user(self, value: Any) -> NoReturn:
        raise ValueError('You can not assign a new value to per_user after initialization.')

    @property
    def per_chat(self) -> bool:
        return self._per_chat

    @per_chat.setter
    def per_chat(self, value: Any) -> NoReturn:
        raise ValueError('You can not assign a new value to per_chat after initialization.')

    @property
    def per_message(self) -> bool:
        return self._per_message

    @per_message.setter
    def per_message(self, value: Any) -> NoReturn:
        raise ValueError('You can not assign a new value to per_message after initialization.')

    @property
    def conversation_timeout(self) -> Optional[int]:
        return self._conversation_timeout

    @conversation_timeout.setter
    def conversation_timeout(self, value: Any) -> NoReturn:
        raise ValueError('You can not assign a new value to conversation_timeout after '
                         'initialization.')

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: Any) -> NoReturn:
        raise ValueError('You can not assign a new value to name after initialization.')

    @property
    def map_to_parent(self) -> Optional[Dict[object, object]]:
        return self._map_to_parent

    @map_to_parent.setter
    def map_to_parent(self, value: Any) -> NoReturn:
        raise ValueError('You can not assign a new value to map_to_parent after initialization.')

    @property
    def persistence(self) -> Optional[BasePersistence]:
        return self._persistence

    @persistence.setter
    def persistence(self, persistence: BasePersistence) -> None:
        self._persistence = persistence
        # Set persistence for nested conversations
        for handlers in self.states.values():
            for handler in handlers:
                if isinstance(handler, ConversationHandler):
                    handler.persistence = self.persistence

    @property
    def conversations(self) -> ConversationDict:
        return self._conversations

    @conversations.setter
    def conversations(self, value: ConversationDict) -> None:
        self._conversations = value
        # Set conversations for nested conversations
        for handlers in self.states.values():
            for handler in handlers:
                if isinstance(handler, ConversationHandler) and self.persistence and handler.name:
                    handler.conversations = self.persistence.get_conversations(handler.name)

    def _get_key(self, update: Update) -> Tuple[int, ...]:
        chat = update.effective_chat
        user = update.effective_user

        key = list()

        if self.per_chat:
            key.append(chat.id)  # type: ignore[union-attr]

        if self.per_user and user is not None:
            key.append(user.id)

        if self.per_message:
            key.append(update.callback_query.inline_message_id  # type: ignore[union-attr]
                       or update.callback_query.message.message_id)  # type: ignore[union-attr]

        return tuple(key)

    def check_update(self, update: HandlerArg) -> CheckUpdateType:
        """
        Determines whether an update should be handled by this conversationhandler, and if so in
        which state the conversation currently is.

        Args:
            update (:class:`telegram.Update`): Incoming telegram update.

        Returns:
            :obj:`bool`

        """
        # Ignore messages in channels
        if (not isinstance(update, Update)
                or update.channel_post
                or self.per_chat and not update.effective_chat
                or self.per_message and not update.callback_query
                or update.callback_query and self.per_chat and not update.callback_query.message):
            return None

        key = self._get_key(update)
        with self._conversations_lock:
            state = self.conversations.get(key)

        # Resolve promises
        if isinstance(state, tuple) and len(state) == 2 and isinstance(state[1], Promise):
            self.logger.debug('waiting for promise...')

            old_state, new_state = state
            if new_state.done.wait(0):
                try:
                    res = new_state.result(0)
                    res = res if res is not None else old_state
                except Exception as exc:
                    self.logger.exception("Promise function raised exception")
                    self.logger.exception("{}".format(exc))
                    res = old_state
                finally:
                    if res is None and old_state is None:
                        res = self.END
                    self.update_state(res, key)
                    with self._conversations_lock:
                        state = self.conversations.get(key)
            else:
                hdlrs = self.states.get(self.WAITING, [])
                for hdlr in hdlrs:
                    check = hdlr.check_update(update)
                    if check is not None and check is not False:
                        return key, hdlr, check
                return None

        self.logger.debug('selecting conversation {} with state {}'.format(str(key), str(state)))

        handler = None

        # Search entry points for a match
        if state is None or self.allow_reentry:
            for entry_point in self.entry_points:
                check = entry_point.check_update(update)
                if check is not None and check is not False:
                    handler = entry_point
                    break

            else:
                if state is None:
                    return None

        # Get the handler list for current state, if we didn't find one yet and we're still here
        if state is not None and not handler:
            handlers = self.states.get(state)

            for candidate in (handlers or []):
                check = candidate.check_update(update)
                if check is not None and check is not False:
                    handler = candidate
                    break

            # Find a fallback handler if all other handlers fail
            else:
                for fallback in self.fallbacks:
                    check = fallback.check_update(update)
                    if check is not None and check is not False:
                        handler = fallback
                        break

                else:
                    return None

        return key, handler, check  # type: ignore[return-value]

    def handle_update(self,  # type: ignore[override]
                      update: HandlerArg,
                      dispatcher: 'Dispatcher',
                      check_result: CheckUpdateType,
                      context: CallbackContext = None) -> Optional[object]:
        """Send the update to the callback for the current state and Handler

        Args:
            check_result: The result from check_update. For this handler it's a tuple of key,
                handler, and the handler's check result.
            update (:class:`telegram.Update`): Incoming telegram update.
            dispatcher (:class:`telegram.ext.Dispatcher`): Dispatcher that originated the Update.
            context (:class:`telegram.ext.CallbackContext`, optional): The context as provided by
                the dispatcher.

        """
        update = cast(Update, update)  # for mypy
        conversation_key, handler, check_result = check_result  # type: ignore[assignment,misc]
        raise_dp_handler_stop = False

        with self._timeout_jobs_lock:
            # Remove the old timeout job (if present)
            timeout_job = self.timeout_jobs.pop(conversation_key, None)

            if timeout_job is not None:
                timeout_job.schedule_removal()
        try:
            new_state = handler.handle_update(update, dispatcher, check_result, context)
        except DispatcherHandlerStop as e:
            new_state = e.state
            raise_dp_handler_stop = True
        with self._timeout_jobs_lock:
            if self.conversation_timeout and new_state != self.END and dispatcher.job_queue:
                # Add the new timeout job
                self.timeout_jobs[conversation_key] = dispatcher.job_queue.run_once(
                    self._trigger_timeout, self.conversation_timeout,  # type: ignore[arg-type]
                    context=_ConversationTimeoutContext(conversation_key, update,
                                                        dispatcher, context))

        if isinstance(self.map_to_parent, dict) and new_state in self.map_to_parent:
            self.update_state(self.END, conversation_key)
            if raise_dp_handler_stop:
                raise DispatcherHandlerStop(self.map_to_parent.get(new_state))
            else:
                return self.map_to_parent.get(new_state)
        else:
            self.update_state(new_state, conversation_key)
            if raise_dp_handler_stop:
                # Don't pass the new state here. If we're in a nested conversation, the parent is
                # expecting None as return value.
                raise DispatcherHandlerStop()
        return None

    def update_state(self,
                     new_state: object,
                     key: Tuple[int, ...]) -> None:
        if new_state == self.END:
            with self._conversations_lock:
                if key in self.conversations:
                    # If there is no key in conversations, nothing is done.
                    del self.conversations[key]
                    if self.persistent and self.persistence and self.name:
                        self.persistence.update_conversation(self.name, key, None)

        elif isinstance(new_state, Promise):
            with self._conversations_lock:
                self.conversations[key] = (self.conversations.get(key), new_state)
                if self.persistent and self.persistence and self.name:
                    self.persistence.update_conversation(self.name, key,
                                                         (self.conversations.get(key), new_state))

        elif new_state is not None:
            with self._conversations_lock:
                self.conversations[key] = new_state
                if self.persistent and self.persistence and self.name:
                    self.persistence.update_conversation(self.name, key, new_state)

    def _trigger_timeout(self,
                         context: _ConversationTimeoutContext,
                         job: 'Job' = None) -> None:
        self.logger.debug('conversation timeout was triggered!')

        # Backward compatibility with bots that do not use CallbackContext
        callback_context = None
        if isinstance(context, CallbackContext):
            job = context.job

        context = job.context  # type:ignore[union-attr,assignment]
        callback_context = context.callback_context

        with self._timeout_jobs_lock:
            found_job = self.timeout_jobs[context.conversation_key]
            if found_job is not job:
                # The timeout has been canceled in handle_update
                return
            del self.timeout_jobs[context.conversation_key]

        handlers = self.states.get(self.TIMEOUT, [])
        for handler in handlers:
            check = handler.check_update(context.update)
            if check is not None and check is not False:
                try:
                    handler.handle_update(context.update, context.dispatcher, check,
                                          callback_context)
                except DispatcherHandlerStop:
                    self.logger.warning('DispatcherHandlerStop in TIMEOUT state of '
                                        'ConversationHandler has no effect. Ignoring.')
        self.update_state(self.END, context.conversation_key)
