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
import time
from datetime import datetime

import pytest
from flaky import flaky

from telegram import (Bot, Update, ChatAction, TelegramError, error)

BASE_TIME = time.time()
HIGHSCORE_DELTA = 1450000000


class TestBot:
    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_me(self, bot):
        bot = bot.get_me()

        json.loads(bot.to_json())
        self._test_user_equals_bot(bot)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_message_other_args(self, bot, chat_id):
        # parse_mode, reply_markup is tested plenty elsewhere
        message = bot.send_message(chat_id, 'Text', reply_to_message_id=1,
                                   disable_web_page_preview=True, disable_notification=True)

        json.loads(message.to_json())
        assert message.text == u'Text'

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_delete_message(self, bot, chat_id):
        message = bot.send_message(chat_id=chat_id, text='This message will be deleted')

        assert bot.delete_message(chat_id=chat_id, message_id=message.message_id) is True

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_delete_message_old_message(self, bot, chat_id):
        with pytest.raises(TelegramError, match='can\'t be deleted'):
            # Considering that the first message is old enough
            bot.delete_message(chat_id=chat_id, message_id=1)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_updates(self, bot):
        bot.delete_webhook()  # make sure there is no webhook set if webhook tests failed
        updates = bot.getUpdates(timeout=1)

        if updates:  # TODO: Actually send updates to the test bot so this can be tested properly
            json.loads(updates[0].to_json())
            assert isinstance(updates[0], Update)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_forward_message(self, bot, chat_id):
        message = bot.forwardMessage(chat_id, from_chat_id=chat_id, message_id=2398)

        json.loads(message.to_json())
        assert message.text == 'teste'
        assert message.forward_from.username == 'leandrotoledo'
        assert isinstance(message.forward_date, datetime)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_game(self, bot, chat_id):
        game_short_name = 'python_telegram_bot_test_game'
        message = bot.send_game(chat_id, game_short_name)

        json.loads(message.to_json())
        assert message.game.description == 'This is a test game for python-telegram-bot.'
        assert message.game.animation.file_id == 'CgADAQADKwIAAvjAuQABozciVqhFDO0C'
        assert message.game.photo[0].file_size == 851

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_chat_action(self, bot, chat_id):
        bot.sendChatAction(chat_id, ChatAction.TYPING)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_user_profile_photos(self, bot, chat_id):
        user_profile_photos = bot.get_user_profile_photos(chat_id)

        json.loads(user_profile_photos.to_json())
        assert user_profile_photos.photos[0][0].file_size == 12421

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_one_user_profile_photo(self, bot, chat_id):
        user_profile_photos = bot.get_user_profile_photos(chat_id, offset=0)
        json.loads(user_profile_photos.to_json())
        assert user_profile_photos.photos[0][0].file_size == 12421

    @pytest.mark.parametrize('token', argvalues=[
        '123',
        '12a:abcd1234',
        '12:abcd1234',
        '1234:abcd1234\n',
        ' 1234:abcd1234',
        ' 1234:abcd1234\r',
        '1234:abcd 1234'
    ])
    def test_invalid_token(self, token):
        with pytest.raises(error.InvalidToken, match='Invalid token'):
            Bot(token)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_unauthorized_token(self):
        with pytest.raises(error.Unauthorized):
            bot = Bot('1234:abcd1234')
            bot.get_me()

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_invalid_token_server_response(self, monkeypatch):
        monkeypatch.setattr('telegram.Bot._validate_token', lambda x, y: True)
        bot = Bot('12')
        with pytest.raises(error.InvalidToken):
            bot.get_me()

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_leave_chat(self, bot):
        with pytest.raises(error.BadRequest, match='Chat not found'):
            chat = bot.leave_chat(-123456)

        with pytest.raises(error.NetworkError, match='Chat not found'):
            chat = bot.leave_chat(-123456)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_chat(self, bot, group_id):
        chat = bot.get_chat(group_id)

        json.loads(chat.to_json())
        assert chat.type == "group"
        assert chat.title == ">>> telegram.Bot() - Developers"
        assert chat.id == int(group_id)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_chat_administrators(self, bot, channel_id):
        admins = bot.get_chat_administrators(channel_id)
        assert isinstance(admins, list)
        json.loads(admins[0].to_json())

        for a in admins:
            assert a.status in ("administrator", "creator")

        bot = [a.user for a in admins if a.user.id == 133505823][0]
        self._test_user_equals_bot(bot)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_chat_members_count(self, bot, channel_id):
        count = bot.get_chat_members_count(channel_id)
        assert isinstance(count, int)
        assert count > 3

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_chat_member(self, bot, channel_id):
        chat_member = bot.get_chat_member(channel_id, 133505823)
        bot = chat_member.user

        json.loads(chat_member.to_json())
        assert chat_member.status == "administrator"
        self._test_user_equals_bot(chat_member.user)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    @pytest.mark.xfail
    def test_set_webhook_get_webhook_info(self, bot):
        url = 'https://python-telegram-bot.org/test/webhook'
        max_connections = 7
        allowed_updates = ['message']
        bot.set_webhook(url, max_connections=7, allowed_updates=['message'])
        time.sleep(1)
        info = bot.get_webhook_info()
        time.sleep(1)
        bot.delete_webhook()
        time.sleep(1)
        assert url == info.url
        assert max_connections == info.max_connections
        assert allowed_updates == info.allowed_updates

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    @pytest.mark.xfail
    def test_delete_webhook(self, bot):
        url = 'https://python-telegram-bot.org/test/webhook'
        time.sleep(2)
        bot.set_webhook(url)
        time.sleep(1)
        bot.delete_webhook()
        time.sleep(2)
        info = bot.get_webhook_info()
        assert info.url == ''

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_set_game_score_1(self, bot, chat_id):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        game_short_name = 'python_telegram_bot_test_game'
        game = bot.send_game(chat_id, game_short_name)

        message = bot.set_game_score(
            user_id=chat_id,
            score=int(BASE_TIME) - HIGHSCORE_DELTA,
            chat_id=game.chat_id,
            message_id=game.message_id)

        json.loads(game.to_json())
        assert message.game.description == game.game.description
        assert message.game.animation.file_id == game.game.animation.file_id
        assert message.game.photo[0].file_size == game.game.photo[0].file_size
        assert message.game.text != game.game.text

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_set_game_score_2(self, bot, chat_id):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        game_short_name = 'python_telegram_bot_test_game'
        game = bot.send_game(chat_id, game_short_name)

        score = int(BASE_TIME) - HIGHSCORE_DELTA + 1

        message = bot.set_game_score(
            user_id=chat_id,
            score=score,
            chat_id=game.chat_id,
            message_id=game.message_id,
            disable_edit_message=True)

        json.loads(game.to_json())
        assert message.game.description == game.game.description
        assert message.game.animation.file_id == game.game.animation.file_id
        assert message.game.photo[0].file_size == game.game.photo[0].file_size
        assert message.game.text == game.game.text

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_set_game_score_3(self, bot, chat_id):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        game_short_name = 'python_telegram_bot_test_game'
        game = bot.send_game(chat_id, game_short_name)

        score = int(BASE_TIME) - HIGHSCORE_DELTA - 1

        with pytest.raises(error.BadRequest, match='Bot_score_not_modified'):
            bot.set_game_score(
                user_id=chat_id,
                score=score,
                chat_id=game.chat_id,
                message_id=game.message_id)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_set_game_score_4(self, bot, chat_id):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        game_short_name = 'python_telegram_bot_test_game'
        game = bot.send_game(chat_id, game_short_name)

        score = int(BASE_TIME) - HIGHSCORE_DELTA - 2

        message = bot.set_game_score(
            user_id=chat_id,
            score=score,
            chat_id=game.chat_id,
            message_id=game.message_id,
            force=True)

        json.loads(game.to_json())
        assert message.game.description == game.game.description
        assert message.game.animation.file_id == game.game.animation.file_id
        assert message.game.photo[0].file_size == game.game.photo[0].file_size

        # For some reason the returned message does not contain the updated score. need to fetch
        # the game again...
        game2 = bot.send_game(chat_id, game_short_name)
        assert str(score) in game2.game.text

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_set_game_score_too_low_score(self, bot, chat_id):
        # We need a game to set the score for
        game_short_name = 'python_telegram_bot_test_game'
        game = bot.send_game(chat_id, game_short_name)

        with pytest.raises(error.BadRequest):
            bot.set_game_score(user_id=chat_id, score=100,
                               chat_id=game.chat_id, message_id=game.message_id)

    def _test_user_equals_bot(self, user):
        """Tests if user is our trusty @PythonTelegramBot."""
        assert user.id == 133505823
        assert user.first_name == 'PythonTelegramBot'
        assert user.last_name is None
        assert user.username == 'PythonTelegramBot'
        assert user.name == '@PythonTelegramBot'

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_info(self, bot):
        # tests the Bot.info decorator and associated funcs
        assert bot.id == 133505823
        assert bot.first_name == 'PythonTelegramBot'
        assert bot.last_name is None
        assert bot.username == 'PythonTelegramBot'
        assert bot.name == '@PythonTelegramBot'

    def test_timeout_propagation(self, monkeypatch, bot, chat_id):
        class OkException(Exception):
            pass
        timeout = 500

        def post(*args, **kwargs):
            if kwargs.get('timeout') == 500:
                raise OkException

        monkeypatch.setattr('telegram.utils.request.Request.post', post)

        with pytest.raises(OkException):
            bot.send_photo(chat_id, open('tests/data/telegram.jpg', 'rb'), timeout=timeout)