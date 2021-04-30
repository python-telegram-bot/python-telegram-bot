#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
# pylint: disable=R0201
"""This module contains the ConversationHandler."""

import logging
import warnings
import functools
import datetime
from threading import Lock
from typing import TYPE_CHECKING, Dict, List, NoReturn, Optional, Union, Tuple, cast, ClassVar

from telegram import Update
from telegram.ext import (
    BasePersistence,
    CallbackContext,
    CallbackQueryHandler,
    ChosenInlineResultHandler,
    DispatcherHandlerStop,
    Handler,
    InlineQueryHandler,
)
from telegram.ext.utils.promise import Promise
from telegram.utils.types import ConversationDict

if TYPE_CHECKING:
    from telegram.ext import Dispatcher, Job
CheckUpdateType = Optional[Tuple[Tuple[int, ...], Handler, object]]


class _ConversationTimeoutContext:
    def __init__(
        self,
        conversation_key: Tuple[int, ...],
        update: Update,
        dispatcher: 'Dispatcher',
        callback_context: Optional[CallbackContext],
    ):
        self.conversation_key = conversation_key
        self.update = update
        self.dispatcher = dispatcher
        self.callback_context = callback_context


class ConversationHandler(Handler[Update]):
    """
    A handler to hold a conversation with a single or multiple users through Telegram updates by
    managing four collections of other handlers.

    Note:
        ``ConversationHandler`` will only accept updates that are (subclass-)instances of
        :class:`telegram.Update`. This is, because depending on the :attr:`per_user` and
        :attr:`per_chat` ``ConversationHandler`` relies on
        :attr:`telegram.Update.effective_user` and/or :attr:`telegram.Update.effective_chat` in
        order to determine which conversation an update should belong to. For ``per_message=True``,
        ``ConversationHandler`` uses ``update.callback_query.message.message_id`` when
        ``per_chat=True`` and ``update.callback_query.inline_message_id`` when ``per_chat=False``.
        For a more detailed explanation, please see our `FAQ`_.

        Finally, ``ConversationHandler``, does *not* handle (edited) channel posts.

    .. _`FAQ`: https://git.io/JtcyU

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
    Finally, :class:`telegram.ext.DispatcherHandlerStop` can be used in conversations as described
    in the corresponding documentation.

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

            Note:
                 Using `conversation_timeout` with nested conversations is currently not
                 supported. You can still try to use it, but it will likely behave differently
                 from what you expect.


        name (:obj:`str`, optional): The name for this conversationhandler. Required for
            persistence.
        persistent (:obj:`bool`, optional): If the conversations dict for this handler should be
            saved. Name is required and persistence has to be set in :class:`telegram.ext.Updater`
        map_to_parent (Dict[:obj:`object`, :obj:`object`], optional): A :obj:`dict` that can be
            used to instruct a nested conversationhandler to transition into a mapped state on
            its parent conversationhandler in place of a specified nested state.
        run_async (:obj:`bool`, optional): Pass :obj:`True` to *override* the
            :attr:`Handler.run_async` setting of all handlers (in :attr:`entry_points`,
            :attr:`states` and :attr:`fallbacks`).

            Note:
                If set to :obj:`True`, you should not pass a handler instance, that needs to be
                run synchronously in another context.

            .. versionadded:: 13.2

    Raises:
        ValueError

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
        run_async (:obj:`bool`): If :obj:`True`, will override the
            :attr:`Handler.run_async` setting of all internal handlers on initialization.

            .. versionadded:: 13.2

    """

    END: ClassVar[int] = -1
    """:obj:`int`: Used as a constant to return when a conversation is ended."""
    TIMEOUT: ClassVar[int] = -2
    """:obj:`int`: Used as a constant to handle state when a conversation is timed out."""
    WAITING: ClassVar[int] = -3
    """:obj:`int`: Used as a constant to handle state when a conversation is still waiting on the
    previous ``@run_sync`` decorated running handler to finish."""
    # pylint: disable=W0231
    def __init__(
        self,
        entry_points: List[Handler],
        states: Dict[object, List[Handler]],
        fallbacks: List[Handler],
        allow_reentry: bool = False,
        per_chat: bool = True,
        per_user: bool = True,
        per_message: bool = False,
        conversation_timeout: Union[float, datetime.timedelta] = None,
        name: str = None,
        persistent: bool = False,
        map_to_parent: Dict[object, object] = None,
        run_async: bool = False,
    ):
        self.run_async = run_async

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

        self.timeout_jobs: Dict[Tuple[int, ...], 'Job'] = {}
        self._timeout_jobs_lock = Lock()
        self._conversations: ConversationDict = {}
        self._conversations_lock = Lock()

        self.logger = logging.getLogger(__name__)

        if not any((self.per_user, self.per_chat, self.per_message)):
            raise ValueError("'per_user', 'per_chat' and 'per_message' can't all be 'False'")

        if self.per_message and not self.per_chat:
            warnings.warn(
                "If 'per_message=True' is used, 'per_chat=True' should also be used, "
                "since message IDs are not globally unique."
            )

        all_handlers: List[Handler] = []
        all_handlers.extend(entry_points)
        all_handlers.extend(fallbacks)

        for state_handlers in states.values():
            all_handlers.extend(state_handlers)

        if self.per_message:
            for handler in all_handlers:
                if not isinstance(handler, CallbackQueryHandler):
                    warnings.warn(
                        "If 'per_message=True', all entry points and state handlers"
                        " must be 'CallbackQueryHandler', since no other handlers "
                        "have a message context."
                    )
                    break
        else:
            for handler in all_handlers:
                if isinstance(handler, CallbackQueryHandler):
                    warnings.warn(
                        "If 'per_message=False', 'CallbackQueryHandler' will not be "
                        "tracked for every message."
                    )
                    break

        if self.per_chat:
            for handler in all_handlers:
                if isinstance(handler, (InlineQueryHandler, ChosenInlineResultHandler)):
                    warnings.warn(
                        "If 'per_chat=True', 'InlineQueryHandler' can not be used, "
                        "since inline queries have no chat context."
                    )
                    break

        if self.conversation_timeout:
            for handler in all_handlers:
                if isinstance(handler, self.__class__):
                    warnings.warn(
                        "Using `conversation_timeout` with nested conversations is currently not "
                        "supported. You can still try to use it, but it will likely behave "
                        "differently from what you expect."
                    )
                    break

        if self.run_async:
            for handler in all_handlers:
                handler.run_async = True

    @property
    def entry_points(self) -> List[Handler]:
        return self._entry_points

    @entry_points.setter
    def entry_points(self, value: object) -> NoReturn:
        raise ValueError('You can not assign a new value to entry_points after initialization.')

    @property
    def states(self) -> Dict[object, List[Handler]]:
        return self._states

    @states.setter
    def states(self, value: object) -> NoReturn:
        raise ValueError('You can not assign a new value to states after initialization.')

    @property
    def fallbacks(self) -> List[Handler]:
        return self._fallbacks

    @fallbacks.setter
    def fallbacks(self, value: object) -> NoReturn:
        raise ValueError('You can not assign a new value to fallbacks after initialization.')

    @property
    def allow_reentry(self) -> bool:
        return self._allow_reentry

    @allow_reentry.setter
    def allow_reentry(self, value: object) -> NoReturn:
        raise ValueError('You can not assign a new value to allow_reentry after initialization.')

    @property
    def per_user(self) -> bool:
        return self._per_user

    @per_user.setter
    def per_user(self, value: object) -> NoReturn:
        raise ValueError('You can not assign a new value to per_user after initialization.')

    @property
    def per_chat(self) -> bool:
        return self._per_chat

    @per_chat.setter
    def per_chat(self, value: object) -> NoReturn:
        raise ValueError('You can not assign a new value to per_chat after initialization.')

    @property
    def per_message(self) -> bool:
        return self._per_message

    @per_message.setter
    def per_message(self, value: object) -> NoReturn:
        raise ValueError('You can not assign a new value to per_message after initialization.')

    @property
    def conversation_timeout(
        self,
    ) -> Optional[Union[float, datetime.timedelta]]:
        return self._conversation_timeout

    @conversation_timeout.setter
    def conversation_timeout(self, value: object) -> NoReturn:
        raise ValueError(
            'You can not assign a new value to conversation_timeout after ' 'initialization.'
        )

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: object) -> NoReturn:
        raise ValueError('You can not assign a new value to name after initialization.')

    @property
    def map_to_parent(self) -> Optional[Dict[object, object]]:
        return self._map_to_parent

    @map_to_parent.setter
    def map_to_parent(self, value: object) -> NoReturn:
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

        key = []

        if self.per_chat:
            key.append(chat.id)  # type: ignore[union-attr]

        if self.per_user and user is not None:
            key.append(user.id)

        if self.per_message:
            key.append(
                update.callback_query.inline_message_id  # type: ignore[union-attr]
                or update.callback_query.message.message_id  # type: ignore[union-attr]
            )

        return tuple(key)

    def _resolve_promise(self, state: Tuple) -> object:
        old_state, new_state = state
        try:
            res = new_state.result(0)
            res = res if res is not None else old_state
        except Exception as exc:
            self.logger.exception("Promise function raised exception")
            self.logger.exception("%s", exc)
            res = old_state
        finally:
            if res is None and old_state is None:
                res = self.END
        return res

    def _schedule_job(
        self,
        new_state: object,
        dispatcher: 'Dispatcher',
        update: Update,
        context: Optional[CallbackContext],
        conversation_key: Tuple[int, ...],
    ) -> None:
        if new_state != self.END:
            try:
                # both job_queue & conversation_timeout are checked before calling _schedule_job
                j_queue = dispatcher.job_queue
                self.timeout_jobs[conversation_key] = j_queue.run_once(  # type: ignore[union-attr]
                    self._trigger_timeout,
                    self.conversation_timeout,  # type: ignore[arg-type]
                    context=_ConversationTimeoutContext(
                        conversation_key, update, dispatcher, context
                    ),
                )
            except Exception as exc:
                self.logger.exception(
                    "Failed to schedule timeout job due to the following exception:"
                )
                self.logger.exception("%s", exc)

    def check_update(self, update: object) -> CheckUpdateType:  # pylint: disable=R0911
        """
        Determines whether an update should be handled by this conversationhandler, and if so in
        which state the conversation currently is.

        Args:
            update (:class:`telegram.Update` | :obj:`object`): Incoming update.

        Returns:
            :obj:`bool`

        """
        if not isinstance(update, Update):
            return None
        # Ignore messages in channels
        if update.channel_post or update.edited_channel_post:
            return None
        if self.per_chat and not update.effective_chat:
            return None
        if self.per_message and not update.callback_query:
            return None
        if update.callback_query and self.per_chat and not update.callback_query.message:
            return None

        key = self._get_key(update)
        with self._conversations_lock:
            state = self.conversations.get(key)

        # Resolve promises
        if isinstance(state, tuple) and len(state) == 2 and isinstance(state[1], Promise):
            self.logger.debug('waiting for promise...')

            # check if promise is finished or not
            if state[1].done.wait(0):
                res = self._resolve_promise(state)
                self.update_state(res, key)
                with self._conversations_lock:
                    state = self.conversations.get(key)

            # if not then handle WAITING state instead
            else:
                hdlrs = self.states.get(self.WAITING, [])
                for hdlr in hdlrs:
                    check = hdlr.check_update(update)
                    if check is not None and check is not False:
                        return key, hdlr, check
                return None

        self.logger.debug('selecting conversation %s with state %s', str(key), str(state))

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

            for candidate in handlers or []:
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

    def handle_update(  # type: ignore[override]
        self,
        update: Update,
        dispatcher: 'Dispatcher',
        check_result: CheckUpdateType,
        context: CallbackContext = None,
    ) -> Optional[object]:
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
        except DispatcherHandlerStop as exception:
            new_state = exception.state
            raise_dp_handler_stop = True
        with self._timeout_jobs_lock:
            if self.conversation_timeout:
                if dispatcher.job_queue is not None:
                    # Add the new timeout job
                    if isinstance(new_state, Promise):
                        new_state.add_done_callback(
                            functools.partial(
                                self._schedule_job,
                                dispatcher=dispatcher,
                                update=update,
                                context=context,
                                conversation_key=conversation_key,
                            )
                        )
                    elif new_state != self.END:
                        self._schedule_job(
                            new_state, dispatcher, update, context, conversation_key
                        )
                else:
                    self.logger.warning(
                        "Ignoring `conversation_timeout` because the Dispatcher has no JobQueue."
                    )

        if isinstance(self.map_to_parent, dict) and new_state in self.map_to_parent:
            self.update_state(self.END, conversation_key)
            if raise_dp_handler_stop:
                raise DispatcherHandlerStop(self.map_to_parent.get(new_state))
            return self.map_to_parent.get(new_state)

        self.update_state(new_state, conversation_key)
        if raise_dp_handler_stop:
            # Don't pass the new state here. If we're in a nested conversation, the parent is
            # expecting None as return value.
            raise DispatcherHandlerStop()
        return None

    def update_state(self, new_state: object, key: Tuple[int, ...]) -> None:
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
                    self.persistence.update_conversation(
                        self.name, key, (self.conversations.get(key), new_state)
                    )

        elif new_state is not None:
            if new_state not in self.states:
                warnings.warn(
                    f"Handler returned state {new_state} which is unknown to the "
                    f"ConversationHandler{' ' + self.name if self.name is not None else ''}."
                )
            with self._conversations_lock:
                self.conversations[key] = new_state
                if self.persistent and self.persistence and self.name:
                    self.persistence.update_conversation(self.name, key, new_state)

    def _trigger_timeout(self, context: CallbackContext, job: 'Job' = None) -> None:
        self.logger.debug('conversation timeout was triggered!')

        # Backward compatibility with bots that do not use CallbackContext
        if isinstance(context, CallbackContext):
            job = context.job
            ctxt = cast(_ConversationTimeoutContext, job.context)  # type: ignore[union-attr]
        else:
            ctxt = cast(_ConversationTimeoutContext, job.context)

        callback_context = ctxt.callback_context

        with self._timeout_jobs_lock:
            found_job = self.timeout_jobs[ctxt.conversation_key]
            if found_job is not job:
                # The timeout has been cancelled in handle_update
                return
            del self.timeout_jobs[ctxt.conversation_key]

        handlers = self.states.get(self.TIMEOUT, [])
        for handler in handlers:
            check = handler.check_update(ctxt.update)
            if check is not None and check is not False:
                try:
                    handler.handle_update(ctxt.update, ctxt.dispatcher, check, callback_context)
                except DispatcherHandlerStop:
                    self.logger.warning(
                        'DispatcherHandlerStop in TIMEOUT state of '
                        'ConversationHandler has no effect. Ignoring.'
                    )

        self.update_state(self.END, ctxt.conversation_key)
