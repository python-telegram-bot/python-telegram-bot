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
from queue import Queue

import pytest

from telegram import (
    Update,
    CallbackQuery,
    Bot,
    Message,
    User,
    Chat,
    InlineQuery,
    ChosenInlineResult,
    ShippingQuery,
    PreCheckoutQuery,
    Location,
)
from telegram.ext import InlineQueryHandler, CallbackContext, JobQueue

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


@pytest.fixture(scope='function')
def inline_query(bot):
    return Update(
        0,
        inline_query=InlineQuery(
            'id',
            User(2, 'test user', False),
            'test query',
            offset='22',
            location=Location(latitude=-23.691288, longitude=-46.788279),
        ),
    )


class TestInlineQueryHandler:
    test_flag = False

    def test_slot_behaviour(self, recwarn, mro_slots):
        handler = InlineQueryHandler(self.callback_context)
        for attr in handler.__slots__:
            assert getattr(handler, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not handler.__dict__, f"got missing slot(s): {handler.__dict__}"
        assert len(mro_slots(handler)) == len(set(mro_slots(handler))), "duplicate slot"
        handler.custom, handler.callback = 'should give warning', self.callback_basic
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

    def callback_group(self, bot, update, groups=None, groupdict=None):
        if groups is not None:
            self.test_flag = groups == ('t', ' query')
        if groupdict is not None:
            self.test_flag = groupdict == {'begin': 't', 'end': ' query'}

    def callback_context(self, update, context):
        self.test_flag = (
            isinstance(context, CallbackContext)
            and isinstance(context.bot, Bot)
            and isinstance(update, Update)
            and isinstance(context.update_queue, Queue)
            and isinstance(context.job_queue, JobQueue)
            and isinstance(context.user_data, dict)
            and context.chat_data is None
            and isinstance(context.bot_data, dict)
            and isinstance(update.inline_query, InlineQuery)
        )

    def callback_context_pattern(self, update, context):
        if context.matches[0].groups():
            self.test_flag = context.matches[0].groups() == ('t', ' query')
        if context.matches[0].groupdict():
            self.test_flag = context.matches[0].groupdict() == {'begin': 't', 'end': ' query'}

    def test_basic(self, dp, inline_query):
        handler = InlineQueryHandler(self.callback_basic)
        dp.add_handler(handler)

        assert handler.check_update(inline_query)

        dp.process_update(inline_query)
        assert self.test_flag

    def test_with_pattern(self, inline_query):
        handler = InlineQueryHandler(self.callback_basic, pattern='(?P<begin>.*)est(?P<end>.*)')

        assert handler.check_update(inline_query)

        inline_query.inline_query.query = 'nothing here'
        assert not handler.check_update(inline_query)

    def test_with_passing_group_dict(self, dp, inline_query):
        handler = InlineQueryHandler(
            self.callback_group, pattern='(?P<begin>.*)est(?P<end>.*)', pass_groups=True
        )
        dp.add_handler(handler)

        dp.process_update(inline_query)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = InlineQueryHandler(
            self.callback_group, pattern='(?P<begin>.*)est(?P<end>.*)', pass_groupdict=True
        )
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(inline_query)
        assert self.test_flag

    def test_pass_user_or_chat_data(self, dp, inline_query):
        handler = InlineQueryHandler(self.callback_data_1, pass_user_data=True)
        dp.add_handler(handler)

        dp.process_update(inline_query)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = InlineQueryHandler(self.callback_data_1, pass_chat_data=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(inline_query)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = InlineQueryHandler(
            self.callback_data_2, pass_chat_data=True, pass_user_data=True
        )
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(inline_query)
        assert self.test_flag

    def test_pass_job_or_update_queue(self, dp, inline_query):
        handler = InlineQueryHandler(self.callback_queue_1, pass_job_queue=True)
        dp.add_handler(handler)

        dp.process_update(inline_query)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = InlineQueryHandler(self.callback_queue_1, pass_update_queue=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(inline_query)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = InlineQueryHandler(
            self.callback_queue_2, pass_job_queue=True, pass_update_queue=True
        )
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(inline_query)
        assert self.test_flag

    def test_other_update_types(self, false_update):
        handler = InlineQueryHandler(self.callback_basic)
        assert not handler.check_update(false_update)

    def test_context(self, cdp, inline_query):
        handler = InlineQueryHandler(self.callback_context)
        cdp.add_handler(handler)

        cdp.process_update(inline_query)
        assert self.test_flag

    def test_context_pattern(self, cdp, inline_query):
        handler = InlineQueryHandler(
            self.callback_context_pattern, pattern=r'(?P<begin>.*)est(?P<end>.*)'
        )
        cdp.add_handler(handler)

        cdp.process_update(inline_query)
        assert self.test_flag

        cdp.remove_handler(handler)
        handler = InlineQueryHandler(self.callback_context_pattern, pattern=r'(t)est(.*)')
        cdp.add_handler(handler)

        cdp.process_update(inline_query)
        assert self.test_flag

    @pytest.mark.parametrize('chat_types', [[Chat.SENDER], [Chat.SENDER, Chat.SUPERGROUP], []])
    @pytest.mark.parametrize(
        'chat_type,result', [(Chat.SENDER, True), (Chat.CHANNEL, False), (None, False)]
    )
    def test_chat_types(self, cdp, inline_query, chat_types, chat_type, result):
        try:
            inline_query.inline_query.chat_type = chat_type

            handler = InlineQueryHandler(self.callback_context, chat_types=chat_types)
            cdp.add_handler(handler)
            cdp.process_update(inline_query)

            if not chat_types:
                assert self.test_flag is False
            else:
                assert self.test_flag == result

        finally:
            inline_query.chat_type = None
