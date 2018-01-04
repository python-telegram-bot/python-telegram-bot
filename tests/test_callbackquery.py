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

from telegram import CallbackQuery, User, Message, Chat, Audio


@pytest.fixture(scope='class', params=['message', 'inline'])
def callback_query(bot, request):
    cbq = CallbackQuery(TestCallbackQuery.id,
                        TestCallbackQuery.from_user,
                        TestCallbackQuery.chat_instance,
                        data=TestCallbackQuery.data,
                        game_short_name=TestCallbackQuery.game_short_name,
                        bot=bot)
    if request.param == 'message':
        cbq.message = TestCallbackQuery.message
    else:
        cbq.inline_message_id = TestCallbackQuery.inline_message_id
    return cbq


class TestCallbackQuery(object):
    id = 'id'
    from_user = User(1, 'test_user', False)
    chat_instance = 'chat_instance'
    message = Message(3, User(5, 'bot', False), None, Chat(4, 'private'))
    data = 'data'
    inline_message_id = 'inline_message_id'
    game_short_name = 'the_game'

    def test_de_json(self, bot):
        json_dict = {'id': self.id,
                     'from': self.from_user.to_dict(),
                     'chat_instance': self.chat_instance,
                     'message': self.message.to_dict(),
                     'data': self.data,
                     'inline_message_id': self.inline_message_id,
                     'game_short_name': self.game_short_name}
        callback_query = CallbackQuery.de_json(json_dict, bot)

        assert callback_query.id == self.id
        assert callback_query.from_user == self.from_user
        assert callback_query.chat_instance == self.chat_instance
        assert callback_query.message == self.message
        assert callback_query.data == self.data
        assert callback_query.inline_message_id == self.inline_message_id
        assert callback_query.game_short_name == self.game_short_name

    def test_to_dict(self, callback_query):
        callback_query_dict = callback_query.to_dict()

        assert isinstance(callback_query_dict, dict)
        assert callback_query_dict['id'] == callback_query.id
        assert callback_query_dict['from'] == callback_query.from_user.to_dict()
        assert callback_query_dict['chat_instance'] == callback_query.chat_instance
        if callback_query.message:
            assert callback_query_dict['message'] == callback_query.message.to_dict()
        else:
            assert callback_query_dict['inline_message_id'] == callback_query.inline_message_id
        assert callback_query_dict['data'] == callback_query.data
        assert callback_query_dict['game_short_name'] == callback_query.game_short_name

    def test_answer(self, monkeypatch, callback_query):
        def test(*args, **kwargs):
            return args[1] == callback_query.id

        monkeypatch.setattr('telegram.Bot.answerCallbackQuery', test)
        # TODO: PEP8
        assert callback_query.answer()

    def test_edit_message_text(self, monkeypatch, callback_query):
        def test(*args, **kwargs):
            try:
                id = kwargs['inline_message_id'] == callback_query.inline_message_id
                text = kwargs['text'] == 'test'
                return id and text
            except KeyError:
                chat_id = kwargs['chat_id'] == callback_query.message.chat_id
                message_id = kwargs['message_id'] == callback_query.message.message_id
                text = kwargs['text'] == 'test'
                return chat_id and message_id and text

        monkeypatch.setattr('telegram.Bot.edit_message_text', test)
        assert callback_query.edit_message_text(text='test')

    def test_edit_message_caption(self, monkeypatch, callback_query):
        def test(*args, **kwargs):
            try:
                id = kwargs['inline_message_id'] == callback_query.inline_message_id
                caption = kwargs['caption'] == 'new caption'
                return id and caption
            except KeyError:
                id = kwargs['chat_id'] == callback_query.message.chat_id
                message = kwargs['message_id'] == callback_query.message.message_id
                caption = kwargs['caption'] == 'new caption'
                return id and message and caption

        monkeypatch.setattr('telegram.Bot.edit_message_caption', test)
        assert callback_query.edit_message_caption(caption='new caption')

    def test_edit_message_reply_markup(self, monkeypatch, callback_query):
        def test(*args, **kwargs):
            try:
                id = kwargs['inline_message_id'] == callback_query.inline_message_id
                reply_markup = kwargs['reply_markup'] == [['1', '2']]
                return id and reply_markup
            except KeyError:
                id = kwargs['chat_id'] == callback_query.message.chat_id
                message = kwargs['message_id'] == callback_query.message.message_id
                reply_markup = kwargs['reply_markup'] == [['1', '2']]
                return id and message and reply_markup

        monkeypatch.setattr('telegram.Bot.edit_message_reply_markup', test)
        assert callback_query.edit_message_reply_markup(reply_markup=[['1', '2']])

    def test_equality(self):
        a = CallbackQuery(self.id, self.from_user, 'chat')
        b = CallbackQuery(self.id, self.from_user, 'chat')
        c = CallbackQuery(self.id, None, '')
        d = CallbackQuery('', None, 'chat')
        e = Audio(self.id, 1)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
