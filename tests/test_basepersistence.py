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
import asyncio
import collections
import copy
import enum
import functools
import logging
import time
from pathlib import Path
from typing import NamedTuple

import pytest
from flaky import flaky

from telegram import User, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    PersistenceInput,
    BasePersistence,
    Application,
    ConversationHandler,
    MessageHandler,
    filters,
    Handler,
    ApplicationHandlerStop,
)
from telegram.warnings import PTBUserWarning
from tests.conftest import make_message_update, PROJECT_ROOT_PATH, DictApplication


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
        store_data: PersistenceInput = None,
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
        [('uuid', time.time(), {'uuid4': 'callback_data'})],
        {'query_id': 'keyboard_id'},
    )

    def fill(self):
        self.chat_data[1]['key'] = 'value'
        self.chat_data[2]['foo'] = 'bar'
        self.user_data[1]['key'] = 'value'
        self.user_data[2]['foo'] = 'bar'
        self.bot_data['key'] = 'value'
        self.conversations['conv_1'][(1, 1)] = HandlerStates.STATE_1
        self.conversations['conv_1'][(2, 2)] = HandlerStates.STATE_2
        self.conversations['conv_2'][(3, 3)] = HandlerStates.STATE_3
        self.conversations['conv_2'][(4, 4)] = HandlerStates.STATE_4
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
        user_data['refreshed'] = True

    async def refresh_chat_data(self, chat_id: int, chat_data: dict):
        self.refreshed_chat_ids[chat_id] += 1
        chat_data['refreshed'] = True

    async def refresh_bot_data(self, bot_data: dict):
        self.refreshed_bot_data = True
        bot_data['refreshed'] = True

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
        user = User(id=chat_id, first_name='', is_bot=False)
        chat = Chat(id=chat_id, type='')
        return make_message_update(message=str(state.value), user=user, chat=chat)

    @classmethod
    def build_handler(cls, state: HandlerStates):
        return MessageHandler(
            filters.Regex(f'^{state.value}$'),
            functools.partial(cls.callback, state=state),
        )


class PappInput(NamedTuple):
    bot_data: bool = None
    chat_data: bool = None
    user_data: bool = None
    callback_data: bool = None
    conversations: bool = True
    update_interval: float = None
    fill_data: bool = False


def build_papp(
    token: str, store_data: dict = None, update_interval: float = None, fill_data: bool = False
) -> Application:
    store_data = PersistenceInput(**store_data)
    if update_interval is not None:
        persistence = TrackingPersistence(
            store_data=store_data, update_interval=update_interval, fill_data=fill_data
        )
    else:
        persistence = TrackingPersistence(store_data=store_data, fill_data=fill_data)

    return (
        ApplicationBuilder()
        .token(token)
        .persistence(persistence)
        .application_class(DictApplication)
        .arbitrary_callback_data(True)
        .build()
    )


def build_conversation_handler(name: str, persistent: bool = True) -> Handler:
    return TrackingConversationHandler(name=name, persistent=persistent)


@pytest.fixture(scope='function')
def papp(request, bot) -> Application:
    papp_input = request.param
    store_data = {}
    if papp_input.bot_data is not None:
        store_data['bot_data'] = papp_input.bot_data
    if papp_input.chat_data is not None:
        store_data['chat_data'] = papp_input.chat_data
    if papp_input.user_data is not None:
        store_data['user_data'] = papp_input.user_data
    if papp_input.callback_data is not None:
        store_data['callback_data'] = papp_input.callback_data

    app = build_papp(
        bot.token,
        store_data=store_data,
        update_interval=papp_input.update_interval,
        fill_data=papp_input.fill_data,
    )

    app.add_handlers(
        [
            build_conversation_handler(name='conv_1', persistent=papp_input.conversations),
            build_conversation_handler(name='conv_2', persistent=papp_input.conversations),
        ]
    )

    return app


class TestBasePersistence:
    """Tests basic bahvior of BasePersistence and (most importantly) the integration of persistence
    into the Application."""

    # TODO:
    #  * Test add_handler with persistent conversationhandler
    #  * Test migrate_chat_data
    #  * Test drop_chat/user_data
    #  * Test update_persistence & flush getting called on shutdown
    #  * Test the update parameter of create_task
    #  * conversations: pending states, ending conversations, unresolved pending states

    async def job_callback(self, context):
        pass

    def handler_callback(self, chat_id: int = None, sleep: float = None):
        async def callback(update, context):
            if sleep:
                await asyncio.sleep(sleep)

            context.user_data['key'] = 'value'
            context.chat_data['key'] = 'value'
            context.bot_data['key'] = 'value'

            if chat_id:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text='text',
                    reply_markup=InlineKeyboardMarkup.from_button(
                        InlineKeyboardButton(text='text', callback_data='callback_data')
                    ),
                )
            raise ApplicationHandlerStop

        return callback

    def test_slot_behaviour(self, mro_slots):
        inst = TrackingPersistence()
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        # We're interested in BasePersistence, not in the implementation
        slots = mro_slots(inst, only_parents=True)
        print(slots)
        assert len(slots) == len(set(slots)), "duplicate slot"

    @pytest.mark.parametrize('bot_data', (True, False))
    @pytest.mark.parametrize('chat_data', (True, False))
    @pytest.mark.parametrize('user_data', (True, False))
    @pytest.mark.parametrize('callback_data', (True, False))
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
        with pytest.raises(
            TypeError,
            match=(
                'drop_chat_data, drop_user_data, flush, get_bot_data, get_callback_data, '
                'get_chat_data, get_conversations, '
                'get_user_data, refresh_bot_data, refresh_chat_data, '
                'refresh_user_data, update_bot_data, update_callback_data, '
                'update_chat_data, update_conversation, update_user_data'
            ),
        ):
            BasePersistence()

    def test_construction_with_bad_persistence(self, caplog, bot):
        class MyPersistence:
            def __init__(self):
                self.store_data = PersistenceInput(False, False, False, False)

        with pytest.raises(
            TypeError, match='persistence must be based on telegram.ext.BasePersistence'
        ):
            ApplicationBuilder().bot(bot).persistence(MyPersistence()).build()

    @pytest.mark.parametrize(
        'papp',
        [PappInput(fill_data=True), PappInput(False, False, False, False, False, fill_data=True)],
        indirect=True,
    )
    @pytest.mark.asyncio
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
                assert papp.chat_data[1]['key'] == 'value'
                assert papp.chat_data[2]['foo'] == 'bar'
                assert papp.user_data[1]['key'] == 'value'
                assert papp.user_data[2]['foo'] == 'bar'
                assert papp.bot_data == {'key': 'value'}
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
        'papp',
        [PappInput(fill_data=True)],
        indirect=True,
    )
    @pytest.mark.asyncio
    async def test_initialization_invalid_bot_data(self, papp: Application, monkeypatch):
        async def get_bot_data(*args, **kwargs):
            return 'invalid'

        monkeypatch.setattr(papp.persistence, 'get_bot_data', get_bot_data)

        with pytest.raises(ValueError, match='bot_data must be'):
            await papp.initialize()

    @pytest.mark.parametrize(
        'papp',
        [PappInput(fill_data=True)],
        indirect=True,
    )
    @pytest.mark.parametrize('callback_data', ('invalid', (1, 2, 3)))
    @pytest.mark.asyncio
    async def test_initialization_invalid_callback_data(
        self, papp: Application, callback_data, monkeypatch
    ):
        async def get_callback_data(*args, **kwargs):
            return callback_data

        monkeypatch.setattr(papp.persistence, 'get_callback_data', get_callback_data)

        with pytest.raises(ValueError, match='callback_data must be'):
            await papp.initialize()

    @pytest.mark.parametrize(
        'papp',
        [PappInput()],
        indirect=True,
    )
    @pytest.mark.asyncio
    async def test_add_conversation_handler_after_init(self, papp: Application, recwarn):
        async with papp:
            papp.add_handler(build_conversation_handler('name', persistent=True))

            # For debugging if this test fails in CI
            print([rec.message for rec in recwarn])
            assert len(recwarn) == 1
            assert recwarn[0].category is PTBUserWarning
            assert 'after `Application.initialize` was called' in str(recwarn[-1].message)
            assert (
                Path(recwarn[-1].filename)
                == PROJECT_ROOT_PATH / 'telegram' / 'ext' / '_application.py'
            ), "incorrect stacklevel!"

    def test_add_conversation_without_persistence(self, app):
        with pytest.raises(ValueError, match='if application has no persistence'):
            app.add_handler(build_conversation_handler('name', persistent=True))

    @pytest.mark.parametrize(
        'papp',
        [PappInput()],
        indirect=True,
    )
    @pytest.mark.asyncio
    async def test_add_conversation_handler_without_name(self, papp: Application):
        with pytest.raises(ValueError, match="when handler is unnamed"):
            papp.add_handler(build_conversation_handler(name=None, persistent=True))

    @flaky(3, 1)
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'papp',
        [
            PappInput(update_interval=1),
        ],
        indirect=True,
    )
    async def test_update_interval(self, papp: Application, monkeypatch):
        """If we don't want this test to take much longer to run, the accuracy will be a bit low.
        A few tenths of seconds are easy to go astray ... That's why it's flaky."""
        call_times = []

        async def update_persistence(*args, **kwargs):
            call_times.append(time.time())

        monkeypatch.setattr(papp, 'update_persistence', update_persistence)
        async with papp:
            await papp.start()
            await asyncio.sleep(3)
            await papp.stop()

            diffs = [j - i for i, j in zip(call_times[:-1], call_times[1:])]
            for diff in diffs:
                assert diff == pytest.approx(papp.persistence.update_interval, rel=1e-1)

    @pytest.mark.parametrize(
        'papp',
        [
            PappInput(),
            PappInput(bot_data=False),
            PappInput(chat_data=False),
            PappInput(user_data=False),
            PappInput(callback_data=False),
            PappInput(False, False, False, False),
        ],
        ids=(
            'all_data',
            'no_bot_data',
            'no_chat_data',
            'not_user_data',
            'no_callback_data',
            'no_data',
        ),
        indirect=True,
    )
    @pytest.mark.asyncio
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
                'conv_1': {(1, 1): 1},
                'conv_2': {(1, 1): 1},
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
            await papp.process_update('string_update')
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

    @pytest.mark.parametrize(
        'papp',
        [
            PappInput(),
            PappInput(bot_data=False),
            PappInput(chat_data=False),
            PappInput(user_data=False),
            PappInput(callback_data=False),
            PappInput(False, False, False, False),
        ],
        ids=(
            'all_data',
            'no_bot_data',
            'no_chat_data',
            'not_user_data',
            'no_callback_data',
            'no_data',
        ),
        indirect=True,
    )
    @pytest.mark.asyncio
    async def test_update_persistence_loop_call_count_job(self, papp: Application, caplog):
        async with papp:
            papp.job_queue.start()
            papp.job_queue.run_once(self.job_callback, when=0.1, chat_id=1, user_id=1)
            await asyncio.sleep(0.2)
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
            papp.job_queue.run_once(self.job_callback, when=0.1)
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

    @pytest.mark.parametrize('papp', [PappInput()], indirect=True)
    @pytest.mark.asyncio
    async def test_calls_on_shutdown(self, papp, chat_id):
        papp.add_handler(
            MessageHandler(filters.ALL, callback=self.handler_callback(chat_id=chat_id)), group=-1
        )

        async with papp:
            await papp.process_update(
                TrackingConversationHandler.build_update(HandlerStates.STATE_1, chat_id=1)
            )

        # Make sure this this outside the context manager, which is where shutdown is called!
        assert papp.persistence.bot_data == {'key': 'value', 'refreshed': True}
        assert papp.persistence.callback_data[1] == {}
        assert len(papp.persistence.callback_data[0]) == 1
        assert papp.persistence.user_data == {1: {'key': 'value', 'refreshed': True}}
        assert papp.persistence.chat_data == {1: {'key': 'value', 'refreshed': True}}
        assert not papp.persistence.conversations
        assert papp.persistence.flushed

    @pytest.mark.parametrize(
        'papp',
        [
            PappInput(),
            PappInput(bot_data=False),
            PappInput(chat_data=False),
            PappInput(user_data=False),
            PappInput(callback_data=False),
            PappInput(False, False, False, False),
        ],
        ids=(
            'all_data',
            'no_bot_data',
            'no_chat_data',
            'not_user_data',
            'no_callback_data',
            'no_data',
        ),
        indirect=True,
    )
    @pytest.mark.asyncio
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
                assert papp.persistence.bot_data == {'key': 'value', 'refreshed': True}
            else:
                assert not papp.persistence.bot_data

            assert papp.persistence.chat_data is not papp.chat_data
            if papp.persistence.store_data.chat_data:
                assert papp.persistence.chat_data == {1: {'key': 'value', 'refreshed': True}}
                assert papp.persistence.chat_data[1] is not papp.chat_data[1]
            else:
                assert not papp.persistence.chat_data

            assert papp.persistence.user_data is not papp.user_data
            if papp.persistence.store_data.user_data:
                assert papp.persistence.user_data == {1: {'key': 'value', 'refreshed': True}}
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

    @pytest.mark.parametrize('papp', [PappInput()], indirect=True)
    @pytest.mark.parametrize('delay_type', ('job', 'handler', 'task'))
    @pytest.mark.asyncio
    async def test_update_persistence_loop_async_logic(
        self, papp: Application, delay_type: str, chat_id
    ):
        sleep = 0.1
        update = TrackingConversationHandler.build_update(HandlerStates.STATE_1, chat_id=1)

        async with papp:
            if delay_type == 'job':
                papp.job_queue.start()
                papp.job_queue.run_once(self.job_callback, when=sleep, chat_id=1, user_id=1)
            elif delay_type == 'handler':
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

            await asyncio.sleep(sleep + 0.1)
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

    # def test_error_while_saving_chat_data(self, bot):
    #     increment = []
    #
    #     class OwnPersistence(BasePersistence):
    #         def get_callback_data(self):
    #             return None
    #
    #         def update_callback_data(self, data):
    #             raise Exception
    #
    #         def get_bot_data(self):
    #             return {}
    #
    #         def update_bot_data(self, data):
    #             raise Exception
    #
    #         def drop_chat_data(self, chat_id):
    #             pass
    #
    #         def drop_user_data(self, user_id):
    #             pass
    #
    #         def get_chat_data(self):
    #             return defaultdict(dict)
    #
    #         def update_chat_data(self, chat_id, data):
    #             raise Exception
    #
    #         def get_user_data(self):
    #             return defaultdict(dict)
    #
    #         def update_user_data(self, user_id, data):
    #             raise Exception
    #
    #         def get_conversations(self, name):
    #             pass
    #
    #         def update_conversation(self, name, key, new_state):
    #             pass
    #
    #         def refresh_user_data(self, user_id, user_data):
    #             pass
    #
    #         def refresh_chat_data(self, chat_id, chat_data):
    #             pass
    #
    #         def refresh_bot_data(self, bot_data):
    #             pass
    #
    #         def flush(self):
    #             pass
    #
    #     def start1(u, c):
    #         pass
    #
    #     def error(u, c):
    #         increment.append("error")
    #
    #     # If updating a user_data or chat_data from a persistence object throws an error,
    #     # the error handler should catch it
    #
    #     update = Update(
    #         1,
    #         message=Message(
    #             1,
    #             None,
    #             Chat(1, "lala"),
    #             from_user=User(1, "Test", False),
    #             text='/start',
    #             entities=[
    #                 MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len('/start'))
    #             ],
    #             bot=bot,
    #         ),
    #     )
    #     my_persistence = OwnPersistence()
    #     app = ApplicationBuilder().bot(bot).persistence(my_persistence).build()
    #     app.add_handler(CommandHandler('start', start1))
    #     app.add_error_handler(error)
    #     app.process_update(update)
    #     assert increment == ["error", "error", "error", "error"]
    #
    # def test_error_while_persisting(self, app, caplog):
    #     class OwnPersistence(BasePersistence):
    #         def update(self, data):
    #             raise Exception('PersistenceError')
    #
    #         def update_callback_data(self, data):
    #             self.update(data)
    #
    #         def update_bot_data(self, data):
    #             self.update(data)
    #
    #         def update_chat_data(self, chat_id, data):
    #             self.update(data)
    #
    #         def update_user_data(self, user_id, data):
    #             self.update(data)
    #
    #         def drop_user_data(self, user_id):
    #             pass
    #
    #         def drop_chat_data(self, chat_id):
    #             pass
    #
    #         def get_chat_data(self):
    #             pass
    #
    #         def get_bot_data(self):
    #             pass
    #
    #         def get_user_data(self):
    #             pass
    #
    #         def get_callback_data(self):
    #             pass
    #
    #         def get_conversations(self, name):
    #             pass
    #
    #         def update_conversation(self, name, key, new_state):
    #             pass
    #
    #         def refresh_bot_data(self, bot_data):
    #             pass
    #
    #         def refresh_user_data(self, user_id, user_data):
    #             pass
    #
    #         def refresh_chat_data(self, chat_id, chat_data):
    #             pass
    #
    #         def flush(self):
    #             pass
    #
    #     def callback(update, context):
    #         pass
    #
    #     test_flag = []
    #
    #     def error(update, context):
    #         nonlocal test_flag
    #         test_flag.append(str(context.error) == 'PersistenceError')
    #         raise Exception('ErrorHandlingError')
    #
    #     update = Update(
    #         1, message=Message(1, None, Chat(1, ''), from_user=User(1, '', False), text='Text')
    #     )
    #     handler = MessageHandler(filters.ALL, callback)
    #     app.add_handler(handler)
    #     app.add_error_handler(error)
    #
    #     app.persistence = OwnPersistence()
    #
    #     with caplog.at_level(logging.ERROR):
    #         app.process_update(update)
    #
    #     assert test_flag == [True, True, True, True]
    #     assert len(caplog.records) == 4
    #     for record in caplog.records:
    #         message = record.getMessage()
    #         assert message.startswith('An error was raised and an uncaught')
    #
    # def test_persisting_no_user_no_chat(self, app):
    #     class OwnPersistence(BasePersistence):
    #         def __init__(self):
    #             super().__init__()
    #             self.test_flag_bot_data = False
    #             self.test_flag_chat_data = False
    #             self.test_flag_user_data = False
    #
    #         def update_bot_data(self, data):
    #             self.test_flag_bot_data = True
    #
    #         def update_chat_data(self, chat_id, data):
    #             self.test_flag_chat_data = True
    #
    #         def update_user_data(self, user_id, data):
    #             self.test_flag_user_data = True
    #
    #         def update_conversation(self, name, key, new_state):
    #             pass
    #
    #         def drop_chat_data(self, chat_id):
    #             pass
    #
    #         def drop_user_data(self, user_id):
    #             pass
    #
    #         def get_conversations(self, name):
    #             pass
    #
    #         def get_user_data(self):
    #             pass
    #
    #         def get_bot_data(self):
    #             pass
    #
    #         def get_chat_data(self):
    #             pass
    #
    #         def refresh_bot_data(self, bot_data):
    #             pass
    #
    #         def refresh_user_data(self, user_id, user_data):
    #             pass
    #
    #         def refresh_chat_data(self, chat_id, chat_data):
    #             pass
    #
    #         def get_callback_data(self):
    #             pass
    #
    #         def update_callback_data(self, data):
    #             pass
    #
    #         def flush(self):
    #             pass
    #
    #     def callback(update, context):
    #         pass
    #
    #     handler = MessageHandler(filters.ALL, callback)
    #     app.add_handler(handler)
    #     app.persistence = OwnPersistence()
    #
    #     update = Update(
    #         1, message=Message(1, None, None, from_user=User(1, '', False), text='Text')
    #     )
    #     app.process_update(update)
    #     assert app.persistence.test_flag_bot_data
    #     assert app.persistence.test_flag_user_data
    #     assert not app.persistence.test_flag_chat_data
    #
    #     app.persistence.test_flag_bot_data = False
    #     app.persistence.test_flag_user_data = False
    #     app.persistence.test_flag_chat_data = False
    #     update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='Text'))
    #     app.process_update(update)
    #     assert app.persistence.test_flag_bot_data
    #     assert not app.persistence.test_flag_user_data
    #     assert app.persistence.test_flag_chat_data
    #
    # def test_update_persistence_all_async(self, monkeypatch, app):
    #     def update_persistence(*args, **kwargs):
    #         self.count += 1
    #
    #     def dummy_callback(*args, **kwargs):
    #         pass
    #
    #     monkeypatch.setattr(app, 'update_persistence', update_persistence)
    #     monkeypatch.setattr(app, 'block', dummy_callback)
    #
    #     for group in range(5):
    #         app.add_handler(
    #             MessageHandler(filters.TEXT, dummy_callback, block=True), group=group
    #         )
    #
    #     update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='Text'))
    #     app.process_update(update)
    #     assert self.count == 0
    #
    #     app.bot._defaults = Defaults(block=True)
    #     try:
    #         for group in range(5):
    #             app.add_handler(MessageHandler(filters.TEXT, dummy_callback), group=group)
    #
    #         update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None,
    #         text='Text'))
    #         app.process_update(update)
    #         assert self.count == 0
    #     finally:
    #         app.bot._defaults = None
    #
    # @pytest.mark.parametrize('block', [DEFAULT_FALSE, False])
    # def test_update_persistence_one_sync(self, monkeypatch, app, block):
    #     def update_persistence(*args, **kwargs):
    #         self.count += 1
    #
    #     def dummy_callback(*args, **kwargs):
    #         pass
    #
    #     monkeypatch.setattr(app, 'update_persistence', update_persistence)
    #     monkeypatch.setattr(app, 'block', dummy_callback)
    #
    #     for group in range(5):
    #         app.add_handler(
    #             MessageHandler(filters.TEXT, dummy_callback, block=True), group=group
    #         )
    #     app.add_handler(MessageHandler(filters.TEXT, dummy_callback, block=block),group=5)
    #
    #     update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None, text='Text'))
    #     app.process_update(update)
    #     assert self.count == 1
    #
    # @pytest.mark.parametrize('block,expected', [(DEFAULT_FALSE, 1), (False, 1), (True, 0)])
    # def test_update_persistence_defaults_async(self, monkeypatch, app, block, expected):
    #     def update_persistence(*args, **kwargs):
    #         self.count += 1
    #
    #     def dummy_callback(*args, **kwargs):
    #         pass
    #
    #     monkeypatch.setattr(app, 'update_persistence', update_persistence)
    #     monkeypatch.setattr(app, 'block', dummy_callback)
    #     app.bot._defaults = Defaults(block=block)
    #
    #     try:
    #         for group in range(5):
    #             app.add_handler(MessageHandler(filters.TEXT, dummy_callback), group=group)
    #
    #         update = Update(1, message=Message(1, None, Chat(1, ''), from_user=None,
    #         text='Text'))
    #         app.process_update(update)
    #         assert self.count == expected
    #     finally:
    #         app.bot._defaults = None
