#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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
import asyncio
import collections
import copy
import enum
import functools
import logging
import sys
import time
from pathlib import Path
from typing import NamedTuple, Optional

import pytest

from telegram import Bot, Chat, InlineKeyboardButton, InlineKeyboardMarkup, Update, User
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ApplicationHandlerStop,
    BaseHandler,
    BasePersistence,
    CallbackContext,
    ConversationHandler,
    ExtBot,
    MessageHandler,
    PersistenceInput,
    filters,
)
from telegram.warnings import PTBUserWarning
from tests.auxil.build_messages import make_message_update
from tests.auxil.pytest_classes import PytestApplication, make_bot
from tests.auxil.slots import mro_slots


class HandlerStates(int, enum.Enum):
    END = ConversationHandler.END
    STATE_1 = 1
    STATE_2 = 2
    STATE_3 = 3
    STATE_4 = 4

    def next(self):
        cls = self.__class__
        members = list(cls)
        index = members.index(self) + 1
        if index >= len(members):
            index = 0
        return members[index]


class TrackingPersistence(BasePersistence):
    """A dummy implementation of BasePersistence that will help us a great deal in keeping
    the individual tests as short as reasonably possible."""

    def __init__(
        self,
        store_data: Optional[PersistenceInput] = None,
        update_interval: float = 60,
        fill_data: bool = False,
    ):
        super().__init__(store_data=store_data, update_interval=update_interval)
        self.updated_chat_ids = collections.Counter()
        self.updated_user_ids = collections.Counter()
        self.refreshed_chat_ids = collections.Counter()
        self.refreshed_user_ids = collections.Counter()
        self.dropped_chat_ids = collections.Counter()
        self.dropped_user_ids = collections.Counter()
        self.updated_conversations = collections.defaultdict(collections.Counter)
        self.updated_bot_data: bool = False
        self.refreshed_bot_data: bool = False
        self.updated_callback_data: bool = False
        self.flushed = False

        self.chat_data = collections.defaultdict(dict)
        self.user_data = collections.defaultdict(dict)
        self.conversations = collections.defaultdict(dict)
        self.bot_data = {}
        self.callback_data = ([], {})

        if fill_data:
            self.fill()

    CALLBACK_DATA = (
        [("uuid", time.time(), {"uuid4": "callback_data"})],
        {"query_id": "keyboard_id"},
    )

    def fill(self):
        self.chat_data[1]["key"] = "value"
        self.chat_data[2]["foo"] = "bar"
        self.user_data[1]["key"] = "value"
        self.user_data[2]["foo"] = "bar"
        self.bot_data["key"] = "value"
        self.conversations["conv_1"][(1, 1)] = HandlerStates.STATE_1
        self.conversations["conv_1"][(2, 2)] = HandlerStates.STATE_2
        self.conversations["conv_2"][(3, 3)] = HandlerStates.STATE_3
        self.conversations["conv_2"][(4, 4)] = HandlerStates.STATE_4
        self.callback_data = self.CALLBACK_DATA

    def reset_tracking(self):
        self.updated_user_ids.clear()
        self.updated_chat_ids.clear()
        self.dropped_user_ids.clear()
        self.dropped_chat_ids.clear()
        self.refreshed_chat_ids = collections.Counter()
        self.refreshed_user_ids = collections.Counter()
        self.updated_conversations.clear()
        self.updated_bot_data = False
        self.refreshed_bot_data = False
        self.updated_callback_data = False
        self.flushed = False

        self.chat_data = {}
        self.user_data = {}
        self.conversations = collections.defaultdict(dict)
        self.bot_data = {}
        self.callback_data = ([], {})

    async def update_bot_data(self, data):
        self.updated_bot_data = True
        self.bot_data = data

    async def update_chat_data(self, chat_id: int, data):
        self.updated_chat_ids[chat_id] += 1
        self.chat_data[chat_id] = data

    async def update_user_data(self, user_id: int, data):
        self.updated_user_ids[user_id] += 1
        self.user_data[user_id] = data

    async def update_conversation(self, name: str, key, new_state):
        self.updated_conversations[name][key] += 1
        self.conversations[name][key] = new_state

    async def update_callback_data(self, data):
        self.updated_callback_data = True
        self.callback_data = data

    async def get_conversations(self, name):
        return self.conversations.get(name, {})

    async def get_bot_data(self):
        return copy.deepcopy(self.bot_data)

    async def get_chat_data(self):
        return copy.deepcopy(self.chat_data)

    async def get_user_data(self):
        return copy.deepcopy(self.user_data)

    async def get_callback_data(self):
        return copy.deepcopy(self.callback_data)

    async def drop_chat_data(self, chat_id):
        self.dropped_chat_ids[chat_id] += 1
        self.chat_data.pop(chat_id, None)

    async def drop_user_data(self, user_id):
        self.dropped_user_ids[user_id] += 1
        self.user_data.pop(user_id, None)

    async def refresh_user_data(self, user_id: int, user_data: dict):
        self.refreshed_user_ids[user_id] += 1
        user_data["refreshed"] = True

    async def refresh_chat_data(self, chat_id: int, chat_data: dict):
        self.refreshed_chat_ids[chat_id] += 1
        chat_data["refreshed"] = True

    async def refresh_bot_data(self, bot_data: dict):
        self.refreshed_bot_data = True
        bot_data["refreshed"] = True

    async def flush(self) -> None:
        self.flushed = True


class TrackingConversationHandler(ConversationHandler):
    def __init__(self, *args, **kwargs):
        fallbacks = []
        states = {state.value: [self.build_handler(state)] for state in HandlerStates}
        entry_points = [self.build_handler(HandlerStates.END)]
        super().__init__(
            *args, **kwargs, fallbacks=fallbacks, states=states, entry_points=entry_points
        )

    @staticmethod
    async def callback(update, context, state):
        return state.next()

    @staticmethod
    def build_update(state: HandlerStates, chat_id: int):
        user = User(id=chat_id, first_name="", is_bot=False)
        chat = Chat(id=chat_id, type="")
        return make_message_update(message=str(state.value), user=user, chat=chat)

    @classmethod
    def build_handler(cls, state: HandlerStates, callback=None):
        return MessageHandler(
            filters.Regex(f"^{state.value}$"),
            callback or functools.partial(cls.callback, state=state),
        )


class PappInput(NamedTuple):
    bot_data: Optional[bool] = None
    chat_data: Optional[bool] = None
    user_data: Optional[bool] = None
    callback_data: Optional[bool] = None
    conversations: bool = True
    update_interval: float = None
    fill_data: bool = False


def build_papp(
    bot_info: Optional[dict] = None,
    token: Optional[str] = None,
    store_data: Optional[dict] = None,
    update_interval: Optional[float] = None,
    fill_data: bool = False,
) -> Application:
    store_data = PersistenceInput(**(store_data or {}))
    if update_interval is not None:
        persistence = TrackingPersistence(
            store_data=store_data, update_interval=update_interval, fill_data=fill_data
        )
    else:
        persistence = TrackingPersistence(store_data=store_data, fill_data=fill_data)

    if bot_info is not None:
        bot = make_bot(bot_info, arbitrary_callback_data=True)
    else:
        bot = make_bot(token=token, arbitrary_callback_data=True)
    return (
        ApplicationBuilder()
        .bot(bot)
        .persistence(persistence)
        .application_class(PytestApplication)
        .build()
    )


def build_conversation_handler(name: str, persistent: bool = True) -> BaseHandler:
    return TrackingConversationHandler(name=name, persistent=persistent)


@pytest.fixture()
def papp(request, bot_info) -> Application:
    papp_input = request.param
    store_data = {}
    if papp_input.bot_data is not None:
        store_data["bot_data"] = papp_input.bot_data
    if papp_input.chat_data is not None:
        store_data["chat_data"] = papp_input.chat_data
    if papp_input.user_data is not None:
        store_data["user_data"] = papp_input.user_data
    if papp_input.callback_data is not None:
        store_data["callback_data"] = papp_input.callback_data

    app = build_papp(
        bot_info=bot_info,
        store_data=store_data,
        update_interval=papp_input.update_interval,
        fill_data=papp_input.fill_data,
    )

    app.add_handlers(
        [
            build_conversation_handler(name="conv_1", persistent=papp_input.conversations),
            build_conversation_handler(name="conv_2", persistent=papp_input.conversations),
        ]
    )

    return app


# Decorator shortcuts
default_papp = pytest.mark.parametrize("papp", [PappInput()], indirect=True)
filled_papp = pytest.mark.parametrize("papp", [PappInput(fill_data=True)], indirect=True)
papp_store_all_or_none = pytest.mark.parametrize(
    "papp",
    [
        PappInput(),
        PappInput(False, False, False, False),
    ],
    ids=(
        "all_data",
        "no_data",
    ),
    indirect=True,
)


class TestBasePersistence:
    """Tests basic behavior of BasePersistence and (most importantly) the integration of
    persistence into the Application."""

    def job_callback(self, chat_id: Optional[int] = None):
        async def callback(context):
            if context.user_data:
                context.user_data["key"] = "value"
            if context.chat_data:
                context.chat_data["key"] = "value"
            context.bot_data["key"] = "value"

            if chat_id:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="text",
                    reply_markup=InlineKeyboardMarkup.from_button(
                        InlineKeyboardButton(text="text", callback_data="callback_data")
                    ),
                )

        return callback

    def handler_callback(self, chat_id: Optional[int] = None, sleep: Optional[float] = None):
        async def callback(update, context):
            if sleep:
                await asyncio.sleep(sleep)

            context.user_data["key"] = "value"
            context.chat_data["key"] = "value"
            context.bot_data["key"] = "value"

            if chat_id:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="text",
                    reply_markup=InlineKeyboardMarkup.from_button(
                        InlineKeyboardButton(text="text", callback_data="callback_data")
                    ),
                )
            raise ApplicationHandlerStop

        return callback

    def test_slot_behaviour(self):
        inst = TrackingPersistence()
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        # We're interested in BasePersistence, not in the implementation
        slots = mro_slots(inst, only_parents=True)
        assert len(slots) == len(set(slots)), "duplicate slot"

    @pytest.mark.parametrize("bot_data", [True, False])
    @pytest.mark.parametrize("chat_data", [True, False])
    @pytest.mark.parametrize("user_data", [True, False])
    @pytest.mark.parametrize("callback_data", [True, False])
    def test_init_store_data_update_interval(self, bot_data, chat_data, user_data, callback_data):
        store_data = PersistenceInput(
            bot_data=bot_data,
            chat_data=chat_data,
            user_data=user_data,
            callback_data=callback_data,
        )
        persistence = TrackingPersistence(store_data=store_data, update_interval=3.14)
        assert persistence.store_data.bot_data == bot_data
        assert persistence.store_data.chat_data == chat_data
        assert persistence.store_data.user_data == user_data
        assert persistence.store_data.callback_data == callback_data

    def test_abstract_methods(self):
        methods = list(BasePersistence.__abstractmethods__)
        methods.sort()
        with pytest.raises(
            TypeError,
            match=(
                ", ".join(methods)
                if sys.version_info < (3, 12)
                else ", ".join(f"'{i}'" for i in methods)
            ),
        ):
            BasePersistence()

    @default_papp
    def test_update_interval_immutable(self, papp):
        with pytest.raises(AttributeError, match="can not assign a new value to update_interval"):
            papp.persistence.update_interval = 7

    @default_papp
    def test_set_bot_error(self, papp):
        with pytest.raises(TypeError, match="when using telegram.ext.ExtBot"):
            papp.persistence.set_bot(Bot(papp.bot.token))

        # just making sure that setting an ExtBoxt without callback_data_cache doesn't raise an
        # error even though store_callback_data is True
        bot = ExtBot(papp.bot.token)
        assert bot.callback_data_cache is None
        assert papp.persistence.set_bot(bot) is None

    def test_construction_with_bad_persistence(self, bot):
        class MyPersistence:
            def __init__(self):
                self.store_data = PersistenceInput(False, False, False, False)

        with pytest.raises(
            TypeError, match="persistence must be based on telegram.ext.BasePersistence"
        ):
            ApplicationBuilder().bot(bot).persistence(MyPersistence()).build()

    @pytest.mark.parametrize(
        "papp",
        [PappInput(fill_data=True), PappInput(False, False, False, False, False, fill_data=True)],
        indirect=True,
    )
    async def test_initialization_basic(self, papp: Application):
        # Check that no data is there before init
        assert not papp.chat_data
        assert not papp.user_data
        assert not papp.bot_data
        assert papp.bot.callback_data_cache.persistence_data == ([], {})
        assert not papp.handlers[0][0].check_update(
            TrackingConversationHandler.build_update(HandlerStates.STATE_1, chat_id=1)
        )
        assert not papp.handlers[0][0].check_update(
            TrackingConversationHandler.build_update(HandlerStates.STATE_2, chat_id=2)
        )
        assert not papp.handlers[0][1].check_update(
            TrackingConversationHandler.build_update(HandlerStates.STATE_3, chat_id=3)
        )
        assert not papp.handlers[0][1].check_update(
            TrackingConversationHandler.build_update(HandlerStates.STATE_4, chat_id=4)
        )

        async with papp:
            # Check that data is loaded on init

            # We check just bot_data because we set all to the same value
            if papp.persistence.store_data.bot_data:
                assert papp.chat_data[1]["key"] == "value"
                assert papp.chat_data[2]["foo"] == "bar"
                assert papp.user_data[1]["key"] == "value"
                assert papp.user_data[2]["foo"] == "bar"
                assert papp.bot_data == {"key": "value"}
                assert (
                    papp.bot.callback_data_cache.persistence_data
                    == TrackingPersistence.CALLBACK_DATA
                )

                assert papp.handlers[0][0].check_update(
                    TrackingConversationHandler.build_update(HandlerStates.STATE_1, chat_id=1)
                )
                assert papp.handlers[0][0].check_update(
                    TrackingConversationHandler.build_update(HandlerStates.STATE_2, chat_id=2)
                )
                assert papp.handlers[0][1].check_update(
                    TrackingConversationHandler.build_update(HandlerStates.STATE_3, chat_id=3)
                )
                assert papp.handlers[0][1].check_update(
                    TrackingConversationHandler.build_update(HandlerStates.STATE_4, chat_id=4)
                )
            else:
                assert not papp.chat_data
                assert not papp.user_data
                assert not papp.bot_data
                assert papp.bot.callback_data_cache.persistence_data == ([], {})
                assert not papp.handlers[0][0].check_update(
                    TrackingConversationHandler.build_update(HandlerStates.STATE_1, chat_id=1)
                )
                assert not papp.handlers[0][0].check_update(
                    TrackingConversationHandler.build_update(HandlerStates.STATE_2, chat_id=2)
                )
                assert not papp.handlers[0][1].check_update(
                    TrackingConversationHandler.build_update(HandlerStates.STATE_3, chat_id=3)
                )
                assert not papp.handlers[0][1].check_update(
                    TrackingConversationHandler.build_update(HandlerStates.STATE_4, chat_id=4)
                )

    @pytest.mark.parametrize(
        "papp",
        [PappInput(fill_data=True)],
        indirect=True,
    )
    async def test_initialization_invalid_bot_data(self, papp: Application, monkeypatch):
        async def get_bot_data(*args, **kwargs):
            return "invalid"

        monkeypatch.setattr(papp.persistence, "get_bot_data", get_bot_data)

        with pytest.raises(ValueError, match="bot_data must be"):
            await papp.initialize()

    @pytest.mark.parametrize(
        "papp",
        [PappInput(fill_data=True)],
        indirect=True,
    )
    @pytest.mark.parametrize("callback_data", ["invalid", (1, 2, 3)])
    async def test_initialization_invalid_callback_data(
        self, papp: Application, callback_data, monkeypatch
    ):
        async def get_callback_data(*args, **kwargs):
            return callback_data

        monkeypatch.setattr(papp.persistence, "get_callback_data", get_callback_data)

        with pytest.raises(ValueError, match="callback_data must be"):
            await papp.initialize()

    @filled_papp
    async def test_add_conversation_handler_after_init(self, papp: Application, recwarn):
        context = CallbackContext(application=papp)

        # Set it up such that the handler has a conversation in progress that's not persisted
        papp.persistence.conversations["conv_1"].pop((2, 2))
        conversation = build_conversation_handler("conv_1", persistent=True)
        update = TrackingConversationHandler.build_update(state=HandlerStates.END, chat_id=2)
        check = conversation.check_update(update=update)
        await conversation.handle_update(
            update=update, check_result=check, application=papp, context=context
        )

        assert conversation.check_update(
            TrackingConversationHandler.build_update(state=HandlerStates.STATE_1, chat_id=2)
        )

        # and another one that will be overridden
        update = TrackingConversationHandler.build_update(state=HandlerStates.END, chat_id=1)
        check = conversation.check_update(update=update)
        await conversation.handle_update(
            update=update, check_result=check, application=papp, context=context
        )
        update = TrackingConversationHandler.build_update(state=HandlerStates.STATE_1, chat_id=1)
        check = conversation.check_update(update=update)
        await conversation.handle_update(
            update=update, check_result=check, application=papp, context=context
        )

        assert conversation.check_update(
            TrackingConversationHandler.build_update(state=HandlerStates.STATE_2, chat_id=1)
        )

        async with papp:
            papp.add_handler(conversation)

            assert len(recwarn) >= 1
            tasks = asyncio.all_tasks()
            assert any("conversation_handler_after_init" in t.get_name() for t in tasks)
            found = False
            for warning in recwarn:
                if "after `Application.initialize` was called" in str(warning.message):
                    found = True
                    assert warning.category is PTBUserWarning
                    assert Path(warning.filename) == Path(__file__), "incorrect stacklevel!"

            assert found

            await asyncio.sleep(0.05)
            # conversation with chat_id 2 must not have been overridden
            assert conversation.check_update(
                TrackingConversationHandler.build_update(HandlerStates.STATE_1, chat_id=2)
            )

            # conversation with chat_id 1 must have been overridden
            assert not conversation.check_update(
                TrackingConversationHandler.build_update(state=HandlerStates.STATE_2, chat_id=1)
            )
            assert conversation.check_update(
                TrackingConversationHandler.build_update(state=HandlerStates.STATE_1, chat_id=1)
            )

    def test_add_conversation_without_persistence(self, app):
        with pytest.raises(ValueError, match="if application has no persistence"):
            app.add_handler(build_conversation_handler("name", persistent=True))

    @default_papp
    async def test_add_conversation_handler_without_name(self, papp: Application):
        with pytest.raises(ValueError, match="when handler is unnamed"):
            papp.add_handler(build_conversation_handler(name=None, persistent=True))

    @pytest.mark.parametrize(
        "papp",
        [
            PappInput(update_interval=0.0),
        ],
        indirect=True,
    )
    async def test_update_persistence_called(self, papp: Application, monkeypatch):
        """Tests if Application.update_persistence is called from app.start()"""
        called = asyncio.Event()

        async def update_persistence(*args, **kwargs):
            called.set()

        monkeypatch.setattr(papp, "update_persistence", update_persistence)
        async with papp:
            await papp.start()
            tasks = asyncio.all_tasks()
            assert any(":persistence_updater" in task.get_name() for task in tasks)
            assert await called.wait()
            await papp.stop()

    @pytest.mark.flaky(3, 1)
    @pytest.mark.parametrize(
        "papp",
        [
            PappInput(update_interval=1.5),
        ],
        indirect=True,
    )
    async def test_update_interval(self, papp: Application, monkeypatch):
        """If we don't want this test to take much longer to run, the accuracy will be a bit low.
        A few tenths of seconds are easy to go astray ... That's why it's flaky."""
        call_times = []

        async def update_persistence(*args, **kwargs):
            call_times.append(time.time())

        monkeypatch.setattr(papp, "update_persistence", update_persistence)
        async with papp:
            await papp.start()
            await asyncio.sleep(5)
            await papp.stop()

            # Make assertions before calling shutdown, as that calls update_persistence again!
            diffs = [j - i for i, j in zip(call_times[:-1], call_times[1:])]
            assert sum(diffs) / len(diffs) == pytest.approx(
                papp.persistence.update_interval, rel=1e-1
            )

    @papp_store_all_or_none
    async def test_update_persistence_loop_call_count_update_handling(
        self, papp: Application, caplog
    ):
        async with papp:
            for _ in range(5):
                # second pass processes update in conv_2
                await papp.process_update(
                    TrackingConversationHandler.build_update(HandlerStates.END, chat_id=1)
                )
            assert not papp.persistence.updated_bot_data
            assert not papp.persistence.updated_chat_ids
            assert not papp.persistence.updated_user_ids
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.dropped_user_ids
            assert not papp.persistence.updated_callback_data
            assert not papp.persistence.updated_conversations

            await papp.update_persistence()
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.dropped_user_ids
            assert papp.persistence.updated_bot_data == papp.persistence.store_data.bot_data
            assert (
                papp.persistence.updated_callback_data == papp.persistence.store_data.callback_data
            )
            if papp.persistence.store_data.user_data:
                assert papp.persistence.updated_user_ids == {1: 1}
            else:
                assert not papp.persistence.updated_user_ids
            if papp.persistence.store_data.chat_data:
                assert papp.persistence.updated_chat_ids == {1: 1}
            else:
                assert not papp.persistence.updated_chat_ids
            assert papp.persistence.updated_conversations == {
                "conv_1": {(1, 1): 1},
                "conv_2": {(1, 1): 1},
            }

            # Nothing should have been updated after handling nothing
            papp.persistence.reset_tracking()
            with caplog.at_level(logging.ERROR):
                await papp.update_persistence()
            # Make sure that "nothing updated" is not just due to an error
            assert not caplog.text

            assert papp.persistence.updated_bot_data == papp.persistence.store_data.bot_data
            assert (
                papp.persistence.updated_callback_data == papp.persistence.store_data.callback_data
            )
            assert not papp.persistence.updated_chat_ids
            assert not papp.persistence.updated_user_ids
            assert not papp.persistence.updated_conversations
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.dropped_user_ids

            # Nothing should have been updated after handling an update without associated
            # user/chat_data
            papp.persistence.reset_tracking()
            await papp.process_update("string_update")
            with caplog.at_level(logging.ERROR):
                await papp.update_persistence()
            # Make sure that "nothing updated" is not just due to an error
            assert not caplog.text
            assert papp.persistence.updated_bot_data == papp.persistence.store_data.bot_data
            assert (
                papp.persistence.updated_callback_data == papp.persistence.store_data.callback_data
            )
            assert not papp.persistence.updated_chat_ids
            assert not papp.persistence.updated_user_ids
            assert not papp.persistence.updated_conversations
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.dropped_user_ids

    @papp_store_all_or_none
    async def test_update_persistence_loop_call_count_job(self, papp: Application, caplog):
        async with papp:
            await papp.job_queue.start()
            papp.job_queue.run_once(self.job_callback(), when=1.5, chat_id=1, user_id=1)
            await asyncio.sleep(2.5)
            assert not papp.persistence.updated_bot_data
            assert not papp.persistence.updated_chat_ids
            assert not papp.persistence.updated_user_ids
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.dropped_user_ids
            assert not papp.persistence.updated_callback_data
            assert not papp.persistence.updated_conversations

            await papp.update_persistence()
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.dropped_user_ids
            assert papp.persistence.updated_bot_data == papp.persistence.store_data.bot_data
            assert (
                papp.persistence.updated_callback_data == papp.persistence.store_data.callback_data
            )
            if papp.persistence.store_data.user_data:
                assert papp.persistence.updated_user_ids == {1: 1}
            else:
                assert not papp.persistence.updated_user_ids
            if papp.persistence.store_data.chat_data:
                assert papp.persistence.updated_chat_ids == {1: 1}
            else:
                assert not papp.persistence.updated_chat_ids
            assert not papp.persistence.updated_conversations

            # Nothing should have been updated after no job ran
            papp.persistence.reset_tracking()
            with caplog.at_level(logging.ERROR):
                await papp.update_persistence()
            # Make sure that "nothing updated" is not just due to an error
            assert not caplog.text
            assert papp.persistence.updated_bot_data == papp.persistence.store_data.bot_data
            assert (
                papp.persistence.updated_callback_data == papp.persistence.store_data.callback_data
            )
            assert not papp.persistence.updated_chat_ids
            assert not papp.persistence.updated_user_ids
            assert not papp.persistence.updated_conversations
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.dropped_user_ids

            # Nothing should have been updated after running job without associated user/chat_data
            papp.persistence.reset_tracking()
            papp.job_queue.run_once(self.job_callback(), when=0.1)
            await asyncio.sleep(0.2)
            with caplog.at_level(logging.ERROR):
                await papp.update_persistence()
            # Make sure that "nothing updated" is not just due to an error
            assert not caplog.text
            assert papp.persistence.updated_bot_data == papp.persistence.store_data.bot_data
            assert (
                papp.persistence.updated_callback_data == papp.persistence.store_data.callback_data
            )
            assert not papp.persistence.updated_chat_ids
            assert not papp.persistence.updated_user_ids
            assert not papp.persistence.updated_conversations
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.dropped_user_ids

    @default_papp
    async def test_calls_on_shutdown(self, papp, chat_id):
        papp.add_handler(
            MessageHandler(filters.ALL, callback=self.handler_callback(chat_id=chat_id)), group=-1
        )

        async with papp:
            await papp.process_update(
                TrackingConversationHandler.build_update(HandlerStates.STATE_1, chat_id=1)
            )
            assert not papp.persistence.updated_bot_data
            assert not papp.persistence.updated_callback_data
            assert not papp.persistence.updated_user_ids
            assert not papp.persistence.updated_chat_ids
            assert not papp.persistence.updated_conversations
            assert not papp.persistence.flushed

        # Make sure this this outside the context manager, which is where shutdown is called!
        assert papp.persistence.updated_bot_data
        assert papp.persistence.bot_data == {"key": "value", "refreshed": True}
        assert papp.persistence.updated_callback_data
        assert papp.persistence.callback_data[1] == {}
        assert len(papp.persistence.callback_data[0]) == 1
        assert papp.persistence.updated_user_ids == {1: 1}
        assert papp.persistence.user_data == {1: {"key": "value", "refreshed": True}}
        assert papp.persistence.updated_chat_ids == {1: 1}
        assert papp.persistence.chat_data == {1: {"key": "value", "refreshed": True}}
        assert not papp.persistence.updated_conversations
        assert not papp.persistence.conversations
        assert papp.persistence.flushed

    @papp_store_all_or_none
    async def test_update_persistence_loop_saved_data_update_handling(
        self, papp: Application, chat_id
    ):
        papp.add_handler(
            MessageHandler(filters.ALL, callback=self.handler_callback(chat_id=chat_id)), group=-1
        )

        async with papp:
            await papp.process_update(
                TrackingConversationHandler.build_update(HandlerStates.STATE_1, chat_id=1)
            )
            assert not papp.persistence.bot_data
            assert papp.persistence.bot_data is not papp.bot_data
            assert not papp.persistence.chat_data
            assert papp.persistence.chat_data is not papp.chat_data
            assert not papp.persistence.user_data
            assert papp.persistence.user_data is not papp.user_data
            assert papp.persistence.callback_data == ([], {})
            assert (
                papp.persistence.callback_data is not papp.bot.callback_data_cache.persistence_data
            )
            assert not papp.persistence.conversations

            await papp.update_persistence()

            assert papp.persistence.bot_data is not papp.bot_data
            if papp.persistence.store_data.bot_data:
                assert papp.persistence.bot_data == {"key": "value", "refreshed": True}
            else:
                assert not papp.persistence.bot_data

            assert papp.persistence.chat_data is not papp.chat_data
            if papp.persistence.store_data.chat_data:
                assert papp.persistence.chat_data == {1: {"key": "value", "refreshed": True}}
                assert papp.persistence.chat_data[1] is not papp.chat_data[1]
            else:
                assert not papp.persistence.chat_data

            assert papp.persistence.user_data is not papp.user_data
            if papp.persistence.store_data.user_data:
                assert papp.persistence.user_data == {1: {"key": "value", "refreshed": True}}
                assert papp.persistence.user_data[1] is not papp.chat_data[1]
            else:
                assert not papp.persistence.user_data

            assert (
                papp.persistence.callback_data is not papp.bot.callback_data_cache.persistence_data
            )
            if papp.persistence.store_data.callback_data:
                assert papp.persistence.callback_data[1] == {}
                assert len(papp.persistence.callback_data[0]) == 1
            else:
                assert papp.persistence.callback_data == ([], {})

            assert not papp.persistence.conversations

    @papp_store_all_or_none
    async def test_update_persistence_loop_saved_data_job(self, papp: Application, chat_id):
        papp.add_handler(
            MessageHandler(filters.ALL, callback=self.handler_callback(chat_id=chat_id)), group=-1
        )

        async with papp:
            await papp.job_queue.start()
            papp.job_queue.run_once(
                self.job_callback(chat_id=chat_id), when=1.5, chat_id=1, user_id=1
            )
            await asyncio.sleep(2.5)

            assert not papp.persistence.bot_data
            assert papp.persistence.bot_data is not papp.bot_data
            assert not papp.persistence.chat_data
            assert papp.persistence.chat_data is not papp.chat_data
            assert not papp.persistence.user_data
            assert papp.persistence.user_data is not papp.user_data
            assert papp.persistence.callback_data == ([], {})
            assert (
                papp.persistence.callback_data is not papp.bot.callback_data_cache.persistence_data
            )
            assert not papp.persistence.conversations

            await papp.update_persistence()

            assert papp.persistence.bot_data is not papp.bot_data
            if papp.persistence.store_data.bot_data:
                assert papp.persistence.bot_data == {"key": "value", "refreshed": True}
            else:
                assert not papp.persistence.bot_data

            assert papp.persistence.chat_data is not papp.chat_data
            if papp.persistence.store_data.chat_data:
                assert papp.persistence.chat_data == {1: {"key": "value", "refreshed": True}}
                assert papp.persistence.chat_data[1] is not papp.chat_data[1]
            else:
                assert not papp.persistence.chat_data

            assert papp.persistence.user_data is not papp.user_data
            if papp.persistence.store_data.user_data:
                assert papp.persistence.user_data == {1: {"key": "value", "refreshed": True}}
                assert papp.persistence.user_data[1] is not papp.chat_data[1]
            else:
                assert not papp.persistence.user_data

            assert (
                papp.persistence.callback_data is not papp.bot.callback_data_cache.persistence_data
            )
            if papp.persistence.store_data.callback_data:
                assert papp.persistence.callback_data[1] == {}
                assert len(papp.persistence.callback_data[0]) == 1
            else:
                assert papp.persistence.callback_data == ([], {})

            assert not papp.persistence.conversations

    @default_papp
    @pytest.mark.parametrize("delay_type", ["job", "handler", "task"])
    async def test_update_persistence_loop_async_logic(
        self, papp: Application, delay_type: str, chat_id
    ):
        """All three kinds of 'asyncio background processes' should mark things for update once
        they're done."""
        sleep = 1.5
        update = TrackingConversationHandler.build_update(HandlerStates.STATE_1, chat_id=1)

        async with papp:
            if delay_type == "job":
                await papp.job_queue.start()
                papp.job_queue.run_once(self.job_callback(), when=sleep, chat_id=1, user_id=1)
            elif delay_type == "handler":
                papp.add_handler(
                    MessageHandler(
                        filters.ALL,
                        self.handler_callback(sleep=sleep),
                        block=False,
                    )
                )
                await papp.process_update(update)
            else:
                papp.create_task(asyncio.sleep(sleep), update=update)

            await papp.update_persistence()
            assert papp.persistence.updated_bot_data
            assert not papp.persistence.updated_chat_ids
            assert not papp.persistence.updated_user_ids
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.dropped_user_ids
            assert papp.persistence.updated_callback_data
            assert not papp.persistence.updated_conversations

            # Wait for the asyncio process to be done
            await asyncio.sleep(sleep + 1)
            await papp.update_persistence()
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.dropped_user_ids
            assert papp.persistence.updated_bot_data == papp.persistence.store_data.bot_data
            assert (
                papp.persistence.updated_callback_data == papp.persistence.store_data.callback_data
            )
            if papp.persistence.store_data.user_data:
                assert papp.persistence.updated_user_ids == {1: 1}
            else:
                assert not papp.persistence.updated_user_ids
            if papp.persistence.store_data.chat_data:
                assert papp.persistence.updated_chat_ids == {1: 1}
            else:
                assert not papp.persistence.updated_chat_ids
            assert not papp.persistence.updated_conversations

    @papp_store_all_or_none
    async def test_update_persistence_loop_manual_mark_for_update_persistence(
        self, papp: Application, chat_id
    ):
        async with papp:
            papp.chat_data[1].update({"key": "value", "refreshed": True})
            papp.user_data[1].update({"key": "value", "refreshed": True})
            await papp.update_persistence()

            # Since no update has been processed, nothing should be marked for update
            # So we expect the persisted data to differ from the current data
            assert not papp.persistence.chat_data
            assert papp.persistence.chat_data is not papp.chat_data
            assert not papp.persistence.user_data
            assert papp.persistence.user_data is not papp.user_data

            # Double checking that not marking data doesn't change anything
            papp.mark_data_for_update_persistence()
            await papp.update_persistence()
            assert not papp.persistence.chat_data
            assert papp.persistence.chat_data is not papp.chat_data
            assert not papp.persistence.user_data
            assert papp.persistence.user_data is not papp.user_data

            # marking data should lead to the data being updated
            papp.mark_data_for_update_persistence(chat_ids=1, user_ids=1)
            await papp.update_persistence()

            assert papp.persistence.chat_data is not papp.chat_data
            if papp.persistence.store_data.chat_data:
                assert papp.persistence.chat_data == {1: {"key": "value", "refreshed": True}}
                assert papp.persistence.chat_data[1] is not papp.chat_data[1]
            else:
                assert not papp.persistence.chat_data

            assert papp.persistence.user_data is not papp.user_data
            if papp.persistence.store_data.user_data:
                assert papp.persistence.user_data == {1: {"key": "value", "refreshed": True}}
                assert papp.persistence.user_data[1] is not papp.chat_data[1]
            else:
                assert not papp.persistence.user_data

            # Also testing passing collections
            papp.chat_data[1].update({"key": "value", "refreshed": False})
            papp.user_data[1].update({"key": "value", "refreshed": False})
            papp.mark_data_for_update_persistence(chat_ids={1}, user_ids={1})
            await papp.update_persistence()

            # marking data should lead to the data being updated

            assert papp.persistence.chat_data is not papp.chat_data
            if papp.persistence.store_data.chat_data:
                assert papp.persistence.chat_data == {1: {"key": "value", "refreshed": False}}
                assert papp.persistence.chat_data[1] is not papp.chat_data[1]
            else:
                assert not papp.persistence.chat_data

            assert papp.persistence.user_data is not papp.user_data
            if papp.persistence.store_data.user_data:
                assert papp.persistence.user_data == {1: {"key": "value", "refreshed": False}}
                assert papp.persistence.user_data[1] is not papp.chat_data[1]
            else:
                assert not papp.persistence.user_data

    @filled_papp
    async def test_drop_chat_data(self, papp: Application):
        async with papp:
            assert papp.persistence.chat_data == {1: {"key": "value"}, 2: {"foo": "bar"}}
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.updated_chat_ids

            papp.drop_chat_data(1)

            assert papp.persistence.chat_data == {1: {"key": "value"}, 2: {"foo": "bar"}}
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.updated_chat_ids

            await papp.update_persistence()

            assert papp.persistence.chat_data == {2: {"foo": "bar"}}
            assert papp.persistence.dropped_chat_ids == {1: 1}
            assert not papp.persistence.updated_chat_ids

    @filled_papp
    async def test_drop_user_data(self, papp: Application):
        async with papp:
            assert papp.persistence.user_data == {1: {"key": "value"}, 2: {"foo": "bar"}}
            assert not papp.persistence.dropped_user_ids
            assert not papp.persistence.updated_user_ids

            papp.drop_user_data(1)

            assert papp.persistence.user_data == {1: {"key": "value"}, 2: {"foo": "bar"}}
            assert not papp.persistence.dropped_user_ids
            assert not papp.persistence.updated_user_ids

            await papp.update_persistence()

            assert papp.persistence.user_data == {2: {"foo": "bar"}}
            assert papp.persistence.dropped_user_ids == {1: 1}
            assert not papp.persistence.updated_user_ids

    @filled_papp
    async def test_migrate_chat_data(self, papp: Application):
        async with papp:
            assert papp.persistence.chat_data == {1: {"key": "value"}, 2: {"foo": "bar"}}
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.updated_chat_ids

            papp.migrate_chat_data(old_chat_id=1, new_chat_id=2)

            assert papp.persistence.chat_data == {1: {"key": "value"}, 2: {"foo": "bar"}}
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.updated_chat_ids

            await papp.update_persistence()

            assert papp.persistence.chat_data == {2: {"key": "value"}}
            assert papp.persistence.dropped_chat_ids == {1: 1}
            assert papp.persistence.updated_chat_ids == {2: 1}

    async def test_errors_while_persisting(self, bot_info, caplog):
        class ErrorPersistence(TrackingPersistence):
            def raise_error(self):
                raise Exception("PersistenceError")

            async def update_callback_data(self, data):
                self.raise_error()

            async def update_bot_data(self, data):
                self.raise_error()

            async def update_chat_data(self, chat_id, data):
                self.raise_error()

            async def update_user_data(self, user_id, data):
                self.raise_error()

            async def drop_user_data(self, user_id):
                self.raise_error()

            async def drop_chat_data(self, chat_id):
                self.raise_error()

            async def update_conversation(self, name, key, new_state):
                self.raise_error()

        test_flag = []

        async def error(update, context):
            test_flag.append(str(context.error) == "PersistenceError")
            raise Exception("ErrorHandlingError")

        app = (
            ApplicationBuilder()
            .bot(make_bot(bot_info, arbitrary_callback_data=True))
            .persistence(ErrorPersistence())
            .build()
        )

        async with app:
            app.add_error_handler(error)
            for _ in range(5):
                # second pass processes update in conv_2
                await app.process_update(
                    TrackingConversationHandler.build_update(HandlerStates.END, chat_id=1)
                )
                app.drop_chat_data(7)
                app.drop_user_data(42)

            assert not caplog.records

            with caplog.at_level(logging.ERROR):
                await app.update_persistence()

        assert len(caplog.records) == 6
        assert test_flag == [True, True, True, True, True, True]
        for record in caplog.records:
            assert record.name == "telegram.ext.Application"
            message = record.getMessage()
            assert message.startswith("An error was raised and an uncaught")

    @default_papp
    @pytest.mark.parametrize(
        "delay_type", ["job", "blocking_handler", "nonblocking_handler", "task"]
    )
    async def test_update_persistence_after_exception(
        self, papp: Application, delay_type: str, chat_id
    ):
        """Makes sure that persistence is updated even if an exception happened in a callback."""
        sleep = 1.5
        update = TrackingConversationHandler.build_update(HandlerStates.STATE_1, chat_id=1)
        errors = 0

        async def error(_, __):
            nonlocal errors
            errors += 1

        async def raise_error(*args, **kwargs):
            raise Exception

        async with papp:
            papp.add_error_handler(error)

            await papp.update_persistence()
            assert papp.persistence.updated_bot_data
            assert not papp.persistence.updated_chat_ids
            assert not papp.persistence.updated_user_ids
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.dropped_user_ids
            assert papp.persistence.updated_callback_data
            assert not papp.persistence.updated_conversations
            assert errors == 0

            if delay_type == "job":
                await papp.job_queue.start()
                papp.job_queue.run_once(raise_error, when=sleep, chat_id=1, user_id=1)
            elif delay_type.endswith("_handler"):
                papp.add_handler(
                    MessageHandler(
                        filters.ALL,
                        raise_error,
                        block=delay_type.startswith("blocking"),
                    )
                )
                await papp.process_update(update)
            else:
                papp.create_task(raise_error(), update=update)

            # Wait for the asyncio process to be done
            await asyncio.sleep(sleep + 1)

            assert errors == 1
            await papp.update_persistence()
            assert not papp.persistence.dropped_chat_ids
            assert not papp.persistence.dropped_user_ids
            assert papp.persistence.updated_bot_data == papp.persistence.store_data.bot_data
            assert (
                papp.persistence.updated_callback_data == papp.persistence.store_data.callback_data
            )
            if papp.persistence.store_data.user_data:
                assert papp.persistence.updated_user_ids == {1: 1}
            else:
                assert not papp.persistence.updated_user_ids
            if papp.persistence.store_data.chat_data:
                assert papp.persistence.updated_chat_ids == {1: 1}
            else:
                assert not papp.persistence.updated_chat_ids
            assert not papp.persistence.updated_conversations

    async def test_non_blocking_conversations(self, bot, caplog):
        papp = build_papp(token=bot.token, update_interval=100)
        event = asyncio.Event()

        async def callback(_, __):
            await event.wait()
            return HandlerStates.STATE_1

        conversation = ConversationHandler(
            entry_points=[
                TrackingConversationHandler.build_handler(HandlerStates.END, callback=callback)
            ],
            states={},
            fallbacks=[],
            persistent=True,
            name="conv",
            block=False,
        )
        papp.add_handler(conversation)

        async with papp:
            await papp.start()
            assert papp.persistence.updated_conversations == {}

            await papp.process_update(
                TrackingConversationHandler.build_update(HandlerStates.END, 1)
            )
            assert papp.persistence.updated_conversations == {}

            with caplog.at_level(logging.DEBUG):
                await papp.update_persistence()
                await asyncio.sleep(0.01)
                # Conversation should have been updated with the current state, i.e. None
                assert papp.persistence.updated_conversations == {"conv": {(1, 1): 1}}
                assert papp.persistence.conversations == {"conv": {(1, 1): None}}

            # Ensure that we warn the user about this!
            found_record = None
            for record in caplog.records:
                message = record.getMessage()
                if message.startswith("A ConversationHandlers state was not yet resolved"):
                    assert "Will check again on next run" in record.getMessage()
                    assert record.name == "telegram.ext.Application"
                    found_record = record
                    break
            assert found_record is not None

            caplog.clear()

            papp.persistence.reset_tracking()
            event.set()
            await asyncio.sleep(0.01)
            with caplog.at_level(logging.DEBUG):
                await papp.update_persistence()

            # Conversation should have been updated with the resolved state now and hence
            # there should be no warning
            assert not any(
                record.getMessage().startswith("A ConversationHandlers state was not yet")
                for record in caplog.records
            )
            assert papp.persistence.updated_conversations == {"conv": {(1, 1): 1}}
            assert papp.persistence.conversations == {"conv": {(1, 1): HandlerStates.STATE_1}}

            await papp.stop()

    async def test_non_blocking_conversations_raises_Exception(self, bot):
        papp = build_papp(token=bot.token)

        async def callback_1(_, __):
            return HandlerStates.STATE_1

        async def callback_2(_, __):
            raise Exception("Test Exception")

        conversation = ConversationHandler(
            entry_points=[
                TrackingConversationHandler.build_handler(HandlerStates.END, callback=callback_1)
            ],
            states={
                HandlerStates.STATE_1: [
                    TrackingConversationHandler.build_handler(
                        HandlerStates.STATE_1, callback=callback_2
                    )
                ]
            },
            fallbacks=[],
            persistent=True,
            name="conv",
            block=False,
        )
        papp.add_handler(conversation)

        async with papp:
            assert papp.persistence.updated_conversations == {}

            await papp.process_update(
                TrackingConversationHandler.build_update(HandlerStates.END, 1)
            )
            assert papp.persistence.updated_conversations == {}

            await papp.update_persistence()
            await asyncio.sleep(0.05)
            assert papp.persistence.updated_conversations == {"conv": {(1, 1): 1}}
            # The result of the pending state wasn't retrieved by the CH yet, so we must be in
            # state `None`
            assert papp.persistence.conversations == {"conv": {(1, 1): None}}

            await papp.process_update(
                TrackingConversationHandler.build_update(HandlerStates.STATE_1, 1)
            )

            papp.persistence.reset_tracking()
            await asyncio.sleep(0.01)
            await papp.update_persistence()
            assert papp.persistence.updated_conversations == {"conv": {(1, 1): 1}}
            # since the second callback raised an exception, the state must be the previous one!
            assert papp.persistence.conversations == {"conv": {(1, 1): HandlerStates.STATE_1}}

    async def test_non_blocking_conversations_on_stop(self, bot):
        papp = build_papp(token=bot.token, update_interval=100)
        event = asyncio.Event()

        async def callback(_, __):
            await event.wait()
            return HandlerStates.STATE_1

        conversation = ConversationHandler(
            entry_points=[
                TrackingConversationHandler.build_handler(HandlerStates.END, callback=callback)
            ],
            states={},
            fallbacks=[],
            persistent=True,
            name="conv",
            block=False,
        )
        papp.add_handler(conversation)

        await papp.initialize()
        assert papp.persistence.updated_conversations == {}
        await papp.start()

        await papp.process_update(TrackingConversationHandler.build_update(HandlerStates.END, 1))
        assert papp.persistence.updated_conversations == {}

        stop_task = asyncio.create_task(papp.stop())
        assert not stop_task.done()
        event.set()
        await asyncio.sleep(0.5)
        assert stop_task.done()
        assert papp.persistence.updated_conversations == {}

        await papp.shutdown()
        await asyncio.sleep(0.01)
        # The pending state must have been resolved on shutdown!
        assert papp.persistence.updated_conversations == {"conv": {(1, 1): 1}}
        assert papp.persistence.conversations == {"conv": {(1, 1): HandlerStates.STATE_1}}

    async def test_non_blocking_conversations_on_improper_stop(self, bot, caplog):
        papp = build_papp(token=bot.token, update_interval=100)
        event = asyncio.Event()

        async def callback(_, __):
            await event.wait()
            return HandlerStates.STATE_1

        conversation = ConversationHandler(
            entry_points=[
                TrackingConversationHandler.build_handler(HandlerStates.END, callback=callback)
            ],
            states={},
            fallbacks=[],
            persistent=True,
            name="conv",
            block=False,
        )
        papp.add_handler(conversation)

        await papp.initialize()
        assert papp.persistence.updated_conversations == {}

        await papp.process_update(TrackingConversationHandler.build_update(HandlerStates.END, 1))
        assert papp.persistence.updated_conversations == {}

        with caplog.at_level(logging.WARNING):
            await papp.shutdown()
            await asyncio.sleep(0.01)
            # Because the app wasn't running, the pending state isn't ensured to be done on
            # shutdown - hence we expect the persistence to be updated with state `None`
            assert papp.persistence.updated_conversations == {"conv": {(1, 1): 1}}
            assert papp.persistence.conversations == {"conv": {(1, 1): None}}

        # Ensure that we warn the user about this!
        found_record = None
        for record in caplog.records:
            if record.getMessage().startswith("A ConversationHandlers state was not yet resolved"):
                assert "will check again" not in record.getMessage()
                assert record.name == "telegram.ext.Application"
                found_record = record
                break
        assert found_record is not None

    @default_papp
    async def test_conversation_ends(self, papp):
        async with papp:
            assert papp.persistence.updated_conversations == {}

            for state in HandlerStates:
                await papp.process_update(TrackingConversationHandler.build_update(state, 1))
            assert papp.persistence.updated_conversations == {}

            await papp.update_persistence()
            assert papp.persistence.updated_conversations == {"conv_1": {(1, 1): 1}}
            # This is the important part: the persistence is updated with `None` when the conv ends
            assert papp.persistence.conversations == {"conv_1": {(1, 1): None}}

    async def test_non_blocking_conversation_ends(self, bot):
        papp = build_papp(token=bot.token, update_interval=100)
        event = asyncio.Event()

        async def callback(_, __):
            await event.wait()
            return HandlerStates.END

        conversation = ConversationHandler(
            entry_points=[
                TrackingConversationHandler.build_handler(HandlerStates.END, callback=callback)
            ],
            states={},
            fallbacks=[],
            persistent=True,
            name="conv",
            block=False,
        )
        papp.add_handler(conversation)

        async with papp:
            await papp.start()
            assert papp.persistence.updated_conversations == {}

            await papp.process_update(
                TrackingConversationHandler.build_update(HandlerStates.END, 1)
            )
            assert papp.persistence.updated_conversations == {}

            papp.persistence.reset_tracking()
            event.set()
            await asyncio.sleep(0.01)
            await papp.update_persistence()

            # On shutdown, persisted data should include the END state b/c that's what the
            # pending state is being resolved to
            assert papp.persistence.updated_conversations == {"conv": {(1, 1): 1}}
            assert papp.persistence.conversations == {"conv": {(1, 1): HandlerStates.END}}

            await papp.stop()

        async with papp:
            # On the next restart/persistence loading the ConversationHandler should resolve
            # the stored END state to None …
            assert papp.persistence.conversations == {"conv": {(1, 1): HandlerStates.END}}
            # … and the update should be accepted by the entry point again
            assert conversation.check_update(
                TrackingConversationHandler.build_update(HandlerStates.END, 1)
            )

            await papp.update_persistence()
            assert papp.persistence.conversations == {"conv": {(1, 1): None}}

    async def test_conversation_timeout(self, bot):
        # high update_interval so that we can instead manually call it
        papp = build_papp(token=bot.token, update_interval=150)

        async def callback(_, __):
            return HandlerStates.STATE_1

        conversation = ConversationHandler(
            entry_points=[
                TrackingConversationHandler.build_handler(HandlerStates.END, callback=callback)
            ],
            states={HandlerStates.STATE_1: []},
            fallbacks=[],
            persistent=True,
            name="conv",
            conversation_timeout=3,
        )
        papp.add_handler(conversation)

        async with papp:
            await papp.start()
            assert papp.persistence.updated_conversations == {}

            await papp.process_update(
                TrackingConversationHandler.build_update(HandlerStates.END, 1)
            )
            assert papp.persistence.updated_conversations == {}
            await papp.update_persistence()
            assert papp.persistence.updated_conversations == {"conv": {(1, 1): 1}}
            assert papp.persistence.conversations == {"conv": {(1, 1): HandlerStates.STATE_1}}

            papp.persistence.reset_tracking()
            await asyncio.sleep(4)
            # After the timeout the conversation should run the entry point again …
            assert conversation.check_update(
                TrackingConversationHandler.build_update(HandlerStates.END, 1)
            )
            await papp.update_persistence()
            # … and persistence should be updated with `None`
            assert papp.persistence.updated_conversations == {"conv": {(1, 1): 1}}
            assert papp.persistence.conversations == {"conv": {(1, 1): None}}

            await papp.stop()

    async def test_persistent_nested_conversations(self, bot):
        papp = build_papp(token=bot.token, update_interval=150)

        def build_callback(
            state: HandlerStates,
        ):
            async def callback(_: Update, __: CallbackContext) -> HandlerStates:
                return state

            return callback

        grand_child = ConversationHandler(
            entry_points=[TrackingConversationHandler.build_handler(HandlerStates.END)],
            states={
                HandlerStates.STATE_1: [
                    TrackingConversationHandler.build_handler(
                        HandlerStates.STATE_1, callback=build_callback(HandlerStates.END)
                    )
                ]
            },
            fallbacks=[],
            persistent=True,
            name="grand_child",
            map_to_parent={HandlerStates.END: HandlerStates.STATE_2},
        )

        child = ConversationHandler(
            entry_points=[TrackingConversationHandler.build_handler(HandlerStates.END)],
            states={
                HandlerStates.STATE_1: [grand_child],
                HandlerStates.STATE_2: [
                    TrackingConversationHandler.build_handler(HandlerStates.STATE_2)
                ],
            },
            fallbacks=[],
            persistent=True,
            name="child",
            map_to_parent={HandlerStates.STATE_3: HandlerStates.STATE_2},
        )

        parent = ConversationHandler(
            entry_points=[TrackingConversationHandler.build_handler(HandlerStates.END)],
            states={
                HandlerStates.STATE_1: [child],
                HandlerStates.STATE_2: [
                    TrackingConversationHandler.build_handler(
                        HandlerStates.STATE_2, callback=build_callback(HandlerStates.END)
                    )
                ],
            },
            fallbacks=[],
            persistent=True,
            name="parent",
        )

        papp.add_handler(parent)
        papp.persistence.conversations["grand_child"][(1, 1)] = HandlerStates.STATE_1
        papp.persistence.conversations["child"][(1, 1)] = HandlerStates.STATE_1
        papp.persistence.conversations["parent"][(1, 1)] = HandlerStates.STATE_1

        # Should load the stored data into the persistence so that the updates below are handled
        # accordingly
        await papp.initialize()
        assert papp.persistence.updated_conversations == {}

        assert not parent.check_update(
            TrackingConversationHandler.build_update(HandlerStates.STATE_2, 1)
        )
        assert not parent.check_update(
            TrackingConversationHandler.build_update(HandlerStates.END, 1)
        )
        assert parent.check_update(
            TrackingConversationHandler.build_update(HandlerStates.STATE_1, 1)
        )

        await papp.process_update(
            TrackingConversationHandler.build_update(HandlerStates.STATE_1, 1)
        )
        assert papp.persistence.updated_conversations == {}
        await papp.update_persistence()
        assert papp.persistence.updated_conversations == {
            "grand_child": {(1, 1): 1},
            "child": {(1, 1): 1},
        }
        assert papp.persistence.conversations == {
            "grand_child": {(1, 1): None},
            "child": {(1, 1): HandlerStates.STATE_2},
            "parent": {(1, 1): HandlerStates.STATE_1},
        }

        papp.persistence.reset_tracking()
        await papp.process_update(
            TrackingConversationHandler.build_update(HandlerStates.STATE_2, 1)
        )
        await papp.update_persistence()
        assert papp.persistence.updated_conversations == {
            "parent": {(1, 1): 1},
            "child": {(1, 1): 1},
        }
        assert papp.persistence.conversations == {
            "child": {(1, 1): None},
            "parent": {(1, 1): HandlerStates.STATE_2},
        }

        papp.persistence.reset_tracking()
        await papp.process_update(
            TrackingConversationHandler.build_update(HandlerStates.STATE_2, 1)
        )
        await papp.update_persistence()
        assert papp.persistence.updated_conversations == {
            "parent": {(1, 1): 1},
        }
        assert papp.persistence.conversations == {
            "parent": {(1, 1): None},
        }

        await papp.shutdown()
