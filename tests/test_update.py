#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

import pytest

from telegram import (Message, User, Update, Chat, CallbackQuery, InlineQuery,
                      ChosenInlineResult, ShippingQuery, PreCheckoutQuery)

message = Message(1, User(1, '', False), None, Chat(1, ''), text='Text')

params = [
    {'message': message},
    {'edited_message': message},
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat', message=message)},
    {'channel_post': message},
    {'edited_channel_post': message},
    {'inline_query': InlineQuery(1, User(1, '', False), '', '')},
    {'chosen_inline_result': ChosenInlineResult('id', User(1, '', False), '')},
    {'shipping_query': ShippingQuery('id', User(1, '', False), '', None)},
    {'pre_checkout_query': PreCheckoutQuery('id', User(1, '', False), '', 0, '')},
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat')}
]

all_types = ('message', 'edited_message', 'callback_query', 'channel_post',
             'edited_channel_post', 'inline_query', 'chosen_inline_result',
             'shipping_query', 'pre_checkout_query')

ids = all_types + ('callback_query_without_message',)


@pytest.fixture(params=params, ids=ids)
def update(request):
    return Update(update_id=TestUpdate.update_id, **request.param)


class TestUpdate(object):
    update_id = 868573637

    @pytest.mark.parametrize('paramdict', argvalues=params, ids=ids)
    def test_de_json(self, bot, paramdict):
        json_dict = {'update_id': TestUpdate.update_id}
        # Convert the single update 'item' to a dict of that item and apply it to the json_dict
        json_dict.update({k: v.to_dict() for k, v in paramdict.items()})
        update = Update.de_json(json_dict, bot)

        assert update.update_id == self.update_id

        # Make sure only one thing in the update (other than update_id) is not None
        i = 0
        for type in all_types:
            if getattr(update, type) is not None:
                i += 1
                assert getattr(update, type) == paramdict[type]
        assert i == 1

    def test_update_de_json_empty(self, bot):
        update = Update.de_json(None, bot)

        assert update is None

    def test_to_dict(self, update):
        update_dict = update.to_dict()

        assert isinstance(update_dict, dict)
        assert update_dict['update_id'] == update.update_id
        for type in all_types:
            if getattr(update, type) is not None:
                assert update_dict[type] == getattr(update, type).to_dict()

    def test_effective_chat(self, update):
        # Test that it's sometimes None per docstring
        chat = update.effective_chat
        if not (update.inline_query is not None
                or update.chosen_inline_result is not None
                or (update.callback_query is not None
                    and update.callback_query.message is None)
                or update.shipping_query is not None
                or update.pre_checkout_query is not None):
            assert chat.id == 1
        else:
            assert chat is None

    def test_effective_user(self, update):
        # Test that it's sometimes None per docstring
        user = update.effective_user
        if not (update.channel_post is not None or update.edited_channel_post is not None):
            assert user.id == 1
        else:
            assert user is None

    def test_effective_message(self, update):
        # Test that it's sometimes None per docstring
        eff_message = update.effective_message
        if not (update.inline_query is not None
                or update.chosen_inline_result is not None
                or (update.callback_query is not None
                    and update.callback_query.message is None)
                or update.shipping_query is not None
                or update.pre_checkout_query is not None):
            assert eff_message.message_id == message.message_id
        else:
            assert eff_message is None

    def test_equality(self):
        a = Update(self.update_id, message=message)
        b = Update(self.update_id, message=message)
        c = Update(self.update_id)
        d = Update(0, message=message)
        e = User(self.update_id, '', False)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
