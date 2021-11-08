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
import datetime
from queue import Queue

import pytest
import pytz

from telegram import (
    Update,
    Bot,
    Message,
    User,
    Chat,
    CallbackQuery,
    ChosenInlineResult,
    ShippingQuery,
    PreCheckoutQuery,
    ChatJoinRequest,
    ChatInviteLink,
)
from telegram.ext import CallbackContext, JobQueue, ChatJoinRequestHandler


message = Message(1, None, Chat(1, ''), from_user=User(1, '', False), text='Text')

params = [
    {'message': message},
    {'edited_message': message},
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat', message=message)},
    {'channel_post': message},
    {'edited_channel_post': message},
    {'chosen_inline_result': ChosenInlineResult('id', User(1, '', False), '')},
    {'shipping_query': ShippingQuery('id', User(1, '', False), '', None)},
    {'pre_checkout_query': PreCheckoutQuery('id', User(1, '', False), '', 0, '')},
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat')},
]

ids = (
    'message',
    'edited_message',
    'callback_query',
    'channel_post',
    'edited_channel_post',
    'chosen_inline_result',
    'shipping_query',
    'pre_checkout_query',
    'callback_query_without_message',
)


@pytest.fixture(scope='class', params=params, ids=ids)
def false_update(request):
    return Update(update_id=2, **request.param)


@pytest.fixture(scope='class')
def time():
    return datetime.datetime.now(tz=pytz.utc)


@pytest.fixture(scope='class')
def chat_join_request(time, bot):
    return ChatJoinRequest(
        chat=Chat(1, Chat.SUPERGROUP),
        from_user=User(2, 'first_name', False),
        date=time,
        bio='bio',
        invite_link=ChatInviteLink(
            'https://invite.link',
            User(42, 'creator', False),
            name='InviteLink',
            is_revoked=False,
            is_primary=False,
        ),
        bot=bot,
    )


@pytest.fixture(scope='function')
def chat_join_request_update(bot, chat_join_request):
    return Update(0, chat_join_request=chat_join_request)


class TestChatJoinRequestHandler:
    test_flag = False

    def test_slot_behaviour(self, recwarn, mro_slots):
        action = ChatJoinRequestHandler(self.callback_basic)
        for attr in action.__slots__:
            assert getattr(action, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not action.__dict__, f"got missing slot(s): {action.__dict__}"
        assert len(mro_slots(action)) == len(set(mro_slots(action))), "duplicate slot"
        action.custom = 'should give warning'
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = False

    def callback_basic(self, bot, update):
        test_bot = isinstance(bot, Bot)
        test_update = isinstance(update, Update)
        self.test_flag = test_bot and test_update

    def callback_data_1(self, bot, update, user_data=None, chat_data=None):
        self.test_flag = (user_data is not None) or (chat_data is not None)

    def callback_data_2(self, bot, update, user_data=None, chat_data=None):
        self.test_flag = (user_data is not None) and (chat_data is not None)

    def callback_queue_1(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) or (update_queue is not None)

    def callback_queue_2(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) and (update_queue is not None)

    def callback_context(self, update, context):
        self.test_flag = (
            isinstance(context, CallbackContext)
            and isinstance(context.bot, Bot)
            and isinstance(update, Update)
            and isinstance(context.update_queue, Queue)
            and isinstance(context.job_queue, JobQueue)
            and isinstance(context.user_data, dict)
            and isinstance(context.chat_data, dict)
            and isinstance(context.bot_data, dict)
            and isinstance(
                update.chat_join_request,
                ChatJoinRequest,
            )
        )

    def test_basic(self, dp, chat_join_request_update):
        handler = ChatJoinRequestHandler(self.callback_basic)
        dp.add_handler(handler)

        assert handler.check_update(chat_join_request_update)

        dp.process_update(chat_join_request_update)
        assert self.test_flag

    def test_pass_user_or_chat_data(self, dp, chat_join_request_update):
        handler = ChatJoinRequestHandler(self.callback_data_1, pass_user_data=True)
        dp.add_handler(handler)

        dp.process_update(chat_join_request_update)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = ChatJoinRequestHandler(self.callback_data_1, pass_chat_data=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(chat_join_request_update)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = ChatJoinRequestHandler(
            self.callback_data_2, pass_chat_data=True, pass_user_data=True
        )
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(chat_join_request_update)
        assert self.test_flag

    def test_pass_job_or_update_queue(self, dp, chat_join_request_update):
        handler = ChatJoinRequestHandler(self.callback_queue_1, pass_job_queue=True)
        dp.add_handler(handler)

        dp.process_update(chat_join_request_update)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = ChatJoinRequestHandler(self.callback_queue_1, pass_update_queue=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(chat_join_request_update)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = ChatJoinRequestHandler(
            self.callback_queue_2, pass_job_queue=True, pass_update_queue=True
        )
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(chat_join_request_update)
        assert self.test_flag

    def test_other_update_types(self, false_update):
        handler = ChatJoinRequestHandler(self.callback_basic)
        assert not handler.check_update(false_update)
        assert not handler.check_update(True)

    def test_context(self, cdp, chat_join_request_update):
        handler = ChatJoinRequestHandler(callback=self.callback_context)
        cdp.add_handler(handler)

        cdp.process_update(chat_join_request_update)
        assert self.test_flag
