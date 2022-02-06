#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
# pylint: disable=no-self-use
"""This module contains the ConversationHandler."""
import asyncio
import logging
import functools
import datetime
from typing import (  # pylint: disable=unused-import  # for the "Any" import
    TYPE_CHECKING,
    Dict,
    List,
    NoReturn,
    Optional,
    Union,
    Tuple,
    cast,
    ClassVar,
    Any,
    Set,
)

from telegram import Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    ChosenInlineResultHandler,
    ApplicationHandlerStop,
    Handler,
    InlineQueryHandler,
    StringCommandHandler,
    StringRegexHandler,
    TypeHandler,
)
from telegram._utils.warnings import warn
from telegram.ext._utils.trackingdefaultdict import TrackingDefaultDict
from telegram.ext._utils.types import ConversationDict
from telegram.ext._utils.types import CCT

if TYPE_CHECKING:
    from telegram.ext import Application, Job, JobQueue
CheckUpdateType = Tuple[object, Tuple[int, ...], Handler, object]


class _ConversationTimeoutContext:
    __slots__ = ('conversation_key', 'update', 'application', 'callback_context')

    def __init__(
        self,
        conversation_key: Tuple[int, ...],
        update: Update,
        application: 'Application[Any, CCT, Any, Any, Any, JobQueue]',
        callback_context: CallbackContext,
    ):
        self.conversation_key = conversation_key
        self.update = update
        self.application = application
        self.callback_context = callback_context


class ConversationHandler(Handler[Update, CCT]):
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

    .. _`FAQ`: https://github.com/python-telegram-bot/python-telegram-bot/wiki\
        /Frequently-Asked-Questions#what-do-the-per_-settings-in-conversation handler-do

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
    Finally, :class:`telegram.ext.ApplicationHandlerStop` can be used in conversations as described
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


        name (:obj:`str`, optional): The name for this conversation handler. Required for
            persistence.
        persistent (:obj:`bool`, optional): If the conversations dict for this handler should be
            saved. Name is required and persistence has to be set in :class:`telegram.ext.Updater`
        map_to_parent (Dict[:obj:`object`, :obj:`object`], optional): A :obj:`dict` that can be
            used to instruct a nested conversation handler to transition into a mapped state on
            its parent conversation handler in place of a specified nested state.
        block (:obj:`bool`, optional): Pass :obj:`False` to *overrule* the
            :attr:`Handler.block` setting of all handlers (in :attr:`entry_points`,
            :attr:`states` and :attr:`fallbacks`).
            Defaults to :obj:`True`.

            .. versionadded:: 13.2
            .. versionchanged:: 14.0
                No longer overrides the handlers settings

    Raises:
        ValueError

    Attributes:
        persistent (:obj:`bool`): Optional. If the conversations dict for this handler should be
            saved. Name is required and persistence has to be set in :class:`telegram.ext.Updater`
        block (:obj:`bool`): Determines whether the callback will run asynchronously.

            .. versionadded:: 13.2

    """

    __slots__ = (
        '__aplication',
        '_allow_reentry',
        '_child_conversations',
        '_conversation_timeout',
        '_conversations',
        '_conversations_lock',
        '_entry_points',
        '_fallbacks',
        '_logger',
        '_map_to_parent',
        '_name',
        '_per_chat',
        '_per_message',
        '_per_user',
        '_persistence',
        '_states',
        '_timeout_jobs_lock',
        'persistent',
        'timeout_jobs',
    )

    END: ClassVar[int] = -1
    """:obj:`int`: Used as a constant to return when a conversation is ended."""
    TIMEOUT: ClassVar[int] = -2
    """:obj:`int`: Used as a constant to handle state when a conversation is timed out."""
    WAITING: ClassVar[int] = -3
    """:obj:`int`: Used as a constant to handle state when a conversation is still waiting on the
    previous ``@run_sync`` decorated running handler to finish."""
    # pylint: disable=super-init-not-called
    def __init__(
        self,
        entry_points: List[Handler[Update, CCT]],
        states: Dict[object, List[Handler[Update, CCT]]],
        fallbacks: List[Handler[Update, CCT]],
        allow_reentry: bool = False,
        per_chat: bool = True,
        per_user: bool = True,
        per_message: bool = False,
        conversation_timeout: Union[float, datetime.timedelta] = None,
        name: str = None,
        persistent: bool = False,
        map_to_parent: Dict[object, object] = None,
        block: bool = False,
    ):
        # these imports need to be here because of circular import error otherwise
        from telegram.ext import (  # pylint: disable=import-outside-toplevel
            ShippingQueryHandler,
            PreCheckoutQueryHandler,
            PollHandler,
            PollAnswerHandler,
        )

        self.block = block

        self._entry_points = entry_points
        self._states = states
        self._fallbacks = fallbacks

        self._allow_reentry = allow_reentry
        self._per_user = per_user
        self._per_chat = per_chat
        self._per_message = per_message
        self._conversation_timeout = conversation_timeout
        self._name = name
        self._map_to_parent = map_to_parent

        self.timeout_jobs: Dict[Tuple[int, ...], 'Job'] = {}
        self._timeout_jobs_lock = asyncio.Lock()
        self._conversations: ConversationDict = {}
        self._conversations_lock = asyncio.Lock()
        self._child_conversations: Set['ConversationHandler'] = set()

        if persistent and not self.name:
            raise ValueError("Conversations can't be persistent when handler is unnamed.")
        self.persistent: bool = persistent

        self._logger = logging.getLogger(__name__)

        if not any((self.per_user, self.per_chat, self.per_message)):
            raise ValueError("'per_user', 'per_chat' and 'per_message' can't all be 'False'")

        if self.per_message and not self.per_chat:
            warn(
                "If 'per_message=True' is used, 'per_chat=True' should also be used, "
                "since message IDs are not globally unique.",
                stacklevel=2,
            )

        all_handlers: List[Handler] = []
        all_handlers.extend(entry_points)
        all_handlers.extend(fallbacks)

        for state_handlers in states.values():
            all_handlers.extend(state_handlers)

        self._child_conversations.update(
            handler for handler in all_handlers if isinstance(handler, ConversationHandler)
        )

        # this loop is going to warn the user about handlers which can work unexpected
        # in conversations

        # this link will be added to all warnings tied to per_* setting
        per_faq_link = (
            " Read this FAQ entry to learn more about the per_* settings: "
            "https://github.com/python-telegram-bot/python-telegram-bot/wiki"
            "/Frequently-Asked-Questions#what-do-the-per_-settings-in-conversation handler-do."
        )

        for handler in all_handlers:
            if self.block:
                handler.block = True

            if isinstance(handler, (StringCommandHandler, StringRegexHandler)):
                warn(
                    "The `ConversationHandler` only handles updates of type `telegram.Update`. "
                    f"{handler.__class__.__name__} handles updates of type `str`.",
                    stacklevel=2,
                )
            elif isinstance(handler, TypeHandler) and not issubclass(handler.type, Update):
                warn(
                    "The `ConversationHandler` only handles updates of type `telegram.Update`."
                    f" The TypeHandler is set to handle {handler.type.__name__}.",
                    stacklevel=2,
                )
            elif isinstance(handler, PollHandler):
                warn(
                    "PollHandler will never trigger in a conversation since it has no information "
                    "about the chat or the user who voted in it. Do you mean the "
                    "`PollAnswerHandler`?",
                    stacklevel=2,
                )

            elif self.per_chat and (
                isinstance(
                    handler,
                    (
                        ShippingQueryHandler,
                        InlineQueryHandler,
                        ChosenInlineResultHandler,
                        PreCheckoutQueryHandler,
                        PollAnswerHandler,
                    ),
                )
            ):
                warn(
                    f"Updates handled by {handler.__class__.__name__} only have information about "
                    f"the user, so this handler won't ever be triggered if `per_chat=True`."
                    f"{per_faq_link}",
                    stacklevel=2,
                )

            elif self.per_message and not isinstance(handler, CallbackQueryHandler):
                warn(
                    "If 'per_message=True', all entry points, state handlers, and fallbacks"
                    " must be 'CallbackQueryHandler', since no other handlers "
                    f"have a message context.{per_faq_link}",
                    stacklevel=2,
                )
            elif not self.per_message and isinstance(handler, CallbackQueryHandler):
                warn(
                    "If 'per_message=False', 'CallbackQueryHandler' will not be "
                    f"tracked for every message.{per_faq_link}",
                    stacklevel=2,
                )

            if self.conversation_timeout and isinstance(handler, self.__class__):
                warn(
                    "Using `conversation_timeout` with nested conversations is currently not "
                    "supported. You can still try to use it, but it will likely behave "
                    "differently from what you expect.",
                    stacklevel=2,
                )

    @property
    def entry_points(self) -> List[Handler]:
        """List[:class:`telegram.ext.Handler`]: A list of ``Handler`` objects that can trigger the
        start of the conversation.
        """
        return self._entry_points

    @entry_points.setter
    def entry_points(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to entry_points after initialization."
        )

    @property
    def states(self) -> Dict[object, List[Handler]]:
        """Dict[:obj:`object`, List[:class:`telegram.ext.Handler`]]: A :obj:`dict` that
        defines the different states of conversation a user can be in and one or more
        associated ``Handler`` objects that should be used in that state.
        """
        return self._states

    @states.setter
    def states(self, value: object) -> NoReturn:
        raise AttributeError("You can not assign a new value to states after initialization.")

    @property
    def fallbacks(self) -> List[Handler]:
        """List[:class:`telegram.ext.Handler`]: A list of handlers that might be used if
        the user is in a conversation, but every handler for their current state returned
        :obj:`False` on :attr:`check_update`.
        """
        return self._fallbacks

    @fallbacks.setter
    def fallbacks(self, value: object) -> NoReturn:
        raise AttributeError("You can not assign a new value to fallbacks after initialization.")

    @property
    def allow_reentry(self) -> bool:
        """:obj:`bool`: Determines if a user can restart a conversation with an entry point."""
        return self._allow_reentry

    @allow_reentry.setter
    def allow_reentry(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to allow_reentry after initialization."
        )

    @property
    def per_user(self) -> bool:
        """:obj:`bool`: If the conversation key should contain the User's ID."""
        return self._per_user

    @per_user.setter
    def per_user(self, value: object) -> NoReturn:
        raise AttributeError("You can not assign a new value to per_user after initialization.")

    @property
    def per_chat(self) -> bool:
        """:obj:`bool`: If the conversation key should contain the Chat's ID."""
        return self._per_chat

    @per_chat.setter
    def per_chat(self, value: object) -> NoReturn:
        raise AttributeError("You can not assign a new value to per_chat after initialization.")

    @property
    def per_message(self) -> bool:
        """:obj:`bool`: If the conversation key should contain the message's ID."""
        return self._per_message

    @per_message.setter
    def per_message(self, value: object) -> NoReturn:
        raise AttributeError("You can not assign a new value to per_message after initialization.")

    @property
    def conversation_timeout(
        self,
    ) -> Optional[Union[float, datetime.timedelta]]:
        """:obj:`float` | :obj:`datetime.timedelta`: Optional. When this
        handler is inactive more than this timeout (in seconds), it will be automatically
        ended.
        """
        return self._conversation_timeout

    @conversation_timeout.setter
    def conversation_timeout(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to conversation_timeout after initialization."
        )

    @property
    def name(self) -> Optional[str]:
        """:obj:`str`: Optional. The name for this :class:`ConversationHandler`."""
        return self._name

    @name.setter
    def name(self, value: object) -> NoReturn:
        raise AttributeError("You can not assign a new value to name after initialization.")

    @property
    def map_to_parent(self) -> Optional[Dict[object, object]]:
        """Dict[:obj:`object`, :obj:`object`]: Optional. A :obj:`dict` that can be
        used to instruct a nested :class:`ConversationHandler` to transition into a mapped state on
        its parent :class:`ConversationHandler` in place of a specified nested state.
        """
        return self._map_to_parent

    @map_to_parent.setter
    def map_to_parent(self, value: object) -> NoReturn:
        raise AttributeError(
            "You can not assign a new value to map_to_parent after initialization."
        )

    async def _initialize_persistence(
        self, application: 'Application'
    ) -> TrackingDefaultDict[Tuple[int, ...], object]:
        """Initializes the persistence for this handler. While this method is marked as protected,
        we expect it to be called by the Application/parent conversations. It's just protected to
        hide it from users.

        Args:
            application (:class:`telegram.ext.Application`): The application.

        """
        if not (self.persistent and self.name and application.persistence):
            raise RuntimeError(
                'This handler is not persistent, has no name or the application has no '
                'persistence!'
            )

        def default_factory() -> NoReturn:
            raise KeyError

        self._conversations = cast(
            TrackingDefaultDict[Tuple[int, ...], object],
            TrackingDefaultDict(
                default_factory=default_factory, track_read=False, track_write=True
            ),
        )
        self._conversations.update(await application.persistence.get_conversations(self.name))

        for handler in self._child_conversations:
            await handler._initialize_persistence(  # pylint: disable=protected-access
                application=application
            )

        return self._conversations

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

    def _resolve_task(self, state: Tuple[object, asyncio.Task]) -> object:
        old_state, new_state = state
        res = new_state.result()
        res = res if res is not None else old_state

        exc = new_state.exception()
        if exc:
            self._logger.exception("Task function raised exception")
            self._logger.exception("%s", exc)
            res = old_state

        if res is None and old_state is None:
            res = self.END

        return res

    def _schedule_job(
        self,
        new_state: Union[object, asyncio.Task],
        application: 'Application[Any, CCT, Any, Any, Any, JobQueue]',
        update: Update,
        context: CallbackContext,
        conversation_key: Tuple[int, ...],
    ) -> None:
        if isinstance(new_state, asyncio.Task):
            new_state = new_state.result()

        if new_state != self.END:
            try:
                # both job_queue & conversation_timeout are checked before calling _schedule_job
                j_queue = application.job_queue
                self.timeout_jobs[conversation_key] = j_queue.run_once(
                    self._trigger_timeout,
                    self.conversation_timeout,  # type: ignore[arg-type]
                    context=_ConversationTimeoutContext(
                        conversation_key, update, application, context
                    ),
                )
            except Exception as exc:
                self._logger.exception(
                    "Failed to schedule timeout job due to the following exception:"
                )
                self._logger.exception("%s", exc)

    # pylint: disable=too-many-return-statements
    def check_update(self, update: object) -> Optional[CheckUpdateType]:
        """
        Determines whether an update should be handled by this conversation handler, and if so in
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
            state = self._conversations.get(key)

        # Resolve promises
        if isinstance(state, tuple) and len(state) == 2 and isinstance(state[1], asyncio.Task):
            self._logger.warning('Waiting for asyncio Task to finish ...')

            # check if promise is finished or not
            if state[1].done():
                res = self._resolve_task(state)  # type: ignore[arg-type]
                self._update_state(res, key)
                with self._conversations_lock:
                    state = self._conversations.get(key)

            # if not then handle WAITING state instead
            else:
                handlers = self.states.get(self.WAITING, [])
                for handler_ in handlers:
                    check = handler_.check_update(update)
                    if check is not None and check is not False:
                        return self.WAITING, key, handler_, check
                return None

        self._logger.debug('Selecting conversation %s with state %s', str(key), str(state))

        handler: Optional[Handler] = None

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
            for candidate in self.states.get(state, []):
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

        return state, key, handler, check  # type: ignore[return-value]

    async def handle_update(  # type: ignore[override]
        self,
        update: Update,
        application: 'Application',
        check_result: CheckUpdateType,
        context: CallbackContext,
    ) -> Optional[object]:
        """Send the update to the callback for the current state and Handler

        Args:
            check_result: The result from check_update. For this handler it's a tuple of the
                conversation state, key, handler, and the handler's check result.
            update (:class:`telegram.Update`): Incoming telegram update.
            application (:class:`telegram.ext.Application`): Application that originated the
                update.
            context (:class:`telegram.ext.CallbackContext`): The context as provided by
                the application.

        """
        current_state, conversation_key, handler, handler_check_result = check_result
        raise_dp_handler_stop = False

        with self._timeout_jobs_lock:
            # Remove the old timeout job (if present)
            timeout_job = self.timeout_jobs.pop(conversation_key, None)

            if timeout_job is not None:
                timeout_job.schedule_removal()
        try:
            # TODO handle non-blocking handlers correctly
            new_state: object = await handler.handle_update(
                update, application, handler_check_result, context
            )
        except ApplicationHandlerStop as exception:
            new_state = exception.state
            raise_dp_handler_stop = True
        with self._timeout_jobs_lock:
            if self.conversation_timeout:
                if application.job_queue is not None:
                    # Add the new timeout job
                    if isinstance(new_state, asyncio.Task):
                        new_state.add_done_callback(
                            functools.partial(
                                self._schedule_job,
                                application=application,
                                update=update,
                                context=context,
                                conversation_key=conversation_key,
                            )
                        )
                    elif new_state != self.END:
                        self._schedule_job(
                            new_state, application, update, context, conversation_key
                        )
                else:
                    warn(
                        "Ignoring `conversation_timeout` because the Application has no JobQueue.",
                    )

        if isinstance(self.map_to_parent, dict) and new_state in self.map_to_parent:
            self._update_state(self.END, conversation_key)
            if raise_dp_handler_stop:
                raise ApplicationHandlerStop(self.map_to_parent.get(new_state))
            return self.map_to_parent.get(new_state)

        if current_state != self.WAITING:
            self._update_state(new_state, conversation_key)

        if raise_dp_handler_stop:
            # Don't pass the new state here. If we're in a nested conversation, the parent is
            # expecting None as return value.
            raise ApplicationHandlerStop()
        return None

    def _update_state(self, new_state: object, key: Tuple[int, ...]) -> None:
        if new_state == self.END:
            with self._conversations_lock:
                if key in self._conversations:
                    # If there is no key in conversations, nothing is done.
                    del self._conversations[key]

        elif isinstance(new_state, asyncio.Task):
            with self._conversations_lock:
                self._conversations[key] = (self._conversations.get(key), new_state)

        elif new_state is not None:
            if new_state not in self.states:
                warn(
                    f"Handler returned state {new_state} which is unknown to the "
                    f"ConversationHandler{' ' + self.name if self.name is not None else ''}.",
                )
            with self._conversations_lock:
                self._conversations[key] = new_state

    async def _trigger_timeout(self, context: CallbackContext) -> None:
        job = cast('Job', context.job)
        ctxt = cast(_ConversationTimeoutContext, job.context)

        self._logger.debug(
            'Conversation timeout was triggered for conversation %s!', ctxt.conversation_key
        )

        callback_context = ctxt.callback_context

        with self._timeout_jobs_lock:
            found_job = self.timeout_jobs.get(ctxt.conversation_key)
            if found_job is not job:
                # The timeout has been cancelled in handle_update
                return
            del self.timeout_jobs[ctxt.conversation_key]

        handlers = self.states.get(self.TIMEOUT, [])
        for handler in handlers:
            check = handler.check_update(ctxt.update)
            if check is not None and check is not False:
                try:
                    await handler.handle_update(
                        ctxt.update, ctxt.application, check, callback_context
                    )
                except ApplicationHandlerStop:
                    warn(
                        'ApplicationHandlerStop in TIMEOUT state of '
                        'ConversationHandler has no effect. Ignoring.',
                    )

        self._update_state(self.END, ctxt.conversation_key)
