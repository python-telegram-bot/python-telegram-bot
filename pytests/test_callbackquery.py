#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import json

import pytest

from telegram import CallbackQuery, User, Message, Chat


@pytest.fixture(scope='class', params=['message', 'inline'])
def callback_query(bot, request):
    cb = CallbackQuery(id=TestCallbackQuery.id,
                       from_user=TestCallbackQuery.from_user,
                       chat_instance=TestCallbackQuery.chat_instance,
                       data=TestCallbackQuery.data,
                       game_short_name=TestCallbackQuery.game_short_name,
                       bot=bot)
    if request.param == 'message':
        cb.message = TestCallbackQuery.message
    else:
        cb.inline_message_id = TestCallbackQuery.inline_message_id
    return cb


class TestCallbackQuery:
    id = 'id'
    from_user = User(1, 'test_user')
    chat_instance = 'chat_instance'
    message = Message(3, User(5, 'bot'), None, Chat(4, 'private'))
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
        callbackquery = CallbackQuery.de_json(json_dict, bot)

        assert callbackquery.id == self.id
        assert callbackquery.from_user == self.from_user
        assert callbackquery.chat_instance == self.chat_instance
        assert callbackquery.message == self.message
        assert callbackquery.data == self.data
        assert callbackquery.inline_message_id == self.inline_message_id
        assert callbackquery.game_short_name == self.game_short_name

    def test_to_json(self, callback_query):
        json.loads(callback_query.to_json())

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
        assert callback_query.edit_message_text(text="test")

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
                reply_markup = kwargs['reply_markup'] == [["1", "2"]]
                return id and reply_markup
            except KeyError:
                id = kwargs['chat_id'] == callback_query.message.chat_id
                message = kwargs['message_id'] == callback_query.message.message_id
                reply_markup = kwargs['reply_markup'] == [["1", "2"]]
                return id and message and reply_markup

        monkeypatch.setattr('telegram.Bot.edit_message_reply_markup', test)
        assert callback_query.edit_message_reply_markup(reply_markup=[["1", "2"]])
