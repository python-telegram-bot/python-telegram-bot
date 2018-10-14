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
import time
from datetime import datetime
from platform import python_implementation

import pytest
from flaky import flaky
from future.utils import string_types

from telegram import (Bot, Update, ChatAction, TelegramError, User, InlineKeyboardMarkup,
                      InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent,
                      ShippingOption, LabeledPrice)
from telegram.error import BadRequest, InvalidToken, NetworkError, RetryAfter
from telegram.utils.helpers import from_timestamp

BASE_TIME = time.time()
HIGHSCORE_DELTA = 1450000000


@pytest.fixture(scope='class')
def message(bot, chat_id):
    return bot.send_message(chat_id, 'Text', reply_to_message_id=1,
                            disable_web_page_preview=True, disable_notification=True)


@pytest.fixture(scope='class')
def media_message(bot, chat_id):
    with open('tests/data/telegram.ogg', 'rb') as f:
        return bot.send_voice(chat_id, voice=f, caption='my caption', timeout=10)


class TestBot(object):
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
        with pytest.raises(InvalidToken, match='Invalid token'):
            Bot(token)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_invalid_token_server_response(self, monkeypatch):
        monkeypatch.setattr('telegram.Bot._validate_token', lambda x, y: True)
        bot = Bot('12')
        with pytest.raises(InvalidToken):
            bot.get_me()

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_me_and_properties(self, bot):
        get_me_bot = bot.get_me()

        assert isinstance(get_me_bot, User)
        assert get_me_bot.id == bot.id
        assert get_me_bot.username == bot.username
        assert get_me_bot.first_name == bot.first_name
        assert get_me_bot.last_name == bot.last_name
        assert get_me_bot.name == bot.name

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_forward_message(self, bot, chat_id, message):
        message = bot.forward_message(chat_id, from_chat_id=chat_id, message_id=message.message_id)

        assert message.text == message.text
        assert message.forward_from.username == message.from_user.username
        assert isinstance(message.forward_date, datetime)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_delete_message(self, bot, chat_id):
        message = bot.send_message(chat_id, text='will be deleted')

        assert bot.delete_message(chat_id=chat_id, message_id=message.message_id) is True

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_delete_message_old_message(self, bot, chat_id):
        with pytest.raises(TelegramError, match='can\'t be deleted'):
            # Considering that the first message is old enough
            bot.delete_message(chat_id=chat_id, message_id=1)

    # send_photo, send_audio, send_document, send_sticker, send_video, send_voice, send_video_note,
    # send_media_group and send_animation are tested in their respective test modules. No need to
    # duplicate here.

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_venue(self, bot, chat_id):
        longitude = -46.788279
        latitude = -23.691288
        title = 'title'
        address = 'address'
        foursquare_id = 'foursquare id'
        foursquare_type = 'foursquare type'
        message = bot.send_venue(chat_id=chat_id, title=title, address=address, latitude=latitude,
                                 longitude=longitude, foursquare_id=foursquare_id,
                                 foursquare_type=foursquare_type)

        assert message.venue
        assert message.venue.title == title
        assert message.venue.address == address
        assert message.venue.location.latitude == latitude
        assert message.venue.location.longitude == longitude
        assert message.venue.foursquare_id == foursquare_id
        assert message.venue.foursquare_type == foursquare_type

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    @pytest.mark.xfail(raises=RetryAfter)
    @pytest.mark.skipif(python_implementation() == 'PyPy',
                        reason='Unstable on pypy for some reason')
    def test_send_contact(self, bot, chat_id):
        phone_number = '+11234567890'
        first_name = 'Leandro'
        last_name = 'Toledo'
        message = bot.send_contact(chat_id=chat_id, phone_number=phone_number,
                                   first_name=first_name, last_name=last_name)

        assert message.contact
        assert message.contact.phone_number == phone_number
        assert message.contact.first_name == first_name
        assert message.contact.last_name == last_name

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_game(self, bot, chat_id):
        game_short_name = 'test_game'
        message = bot.send_game(chat_id, game_short_name)

        assert message.game
        assert message.game.description == ('A no-op test game, for python-telegram-bot '
                                            'bot framework testing.')
        assert message.game.animation.file_id != ''
        assert message.game.photo[0].file_size == 851

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_chat_action(self, bot, chat_id):
        assert bot.send_chat_action(chat_id, ChatAction.TYPING)

    # TODO: Needs improvement. We need incoming inline query to test answer.
    def test_answer_inline_query(self, monkeypatch, bot):
        # For now just test that our internals pass the correct data
        def test(_, url, data, *args, **kwargs):
            return data == {'cache_time': 300,
                            'results': [{'title': 'first', 'id': '11', 'type': 'article',
                                         'input_message_content': {'message_text': 'first'}},
                                        {'title': 'second', 'id': '12', 'type': 'article',
                                         'input_message_content': {'message_text': 'second'}}],
                            'next_offset': '42', 'switch_pm_parameter': 'start_pm',
                            'inline_query_id': 1234, 'is_personal': True,
                            'switch_pm_text': 'switch pm'}

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        results = [InlineQueryResultArticle('11', 'first', InputTextMessageContent('first')),
                   InlineQueryResultArticle('12', 'second', InputTextMessageContent('second'))]

        assert bot.answer_inline_query(1234,
                                       results=results,
                                       cache_time=300,
                                       is_personal=True,
                                       next_offset='42',
                                       switch_pm_text='switch pm',
                                       switch_pm_parameter='start_pm')

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_user_profile_photos(self, bot, chat_id):
        user_profile_photos = bot.get_user_profile_photos(chat_id)

        assert user_profile_photos.photos[0][0].file_size == 5403

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_one_user_profile_photo(self, bot, chat_id):
        user_profile_photos = bot.get_user_profile_photos(chat_id, offset=0, limit=1)
        assert user_profile_photos.photos[0][0].file_size == 5403

    # get_file is tested multiple times in the test_*media* modules.

    # TODO: Needs improvement. No feasable way to test until bots can add members.
    def test_kick_chat_member(self, monkeypatch, bot):
        def test(_, url, data, *args, **kwargs):
            chat_id = data['chat_id'] == 2
            user_id = data['user_id'] == 32
            until_date = data.get('until_date', 1577887200) == 1577887200
            return chat_id and user_id and until_date

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        until = from_timestamp(1577887200)

        assert bot.kick_chat_member(2, 32)
        assert bot.kick_chat_member(2, 32, until_date=until)
        assert bot.kick_chat_member(2, 32, until_date=1577887200)

    # TODO: Needs improvement.
    def test_unban_chat_member(self, monkeypatch, bot):
        def test(_, url, data, *args, **kwargs):
            chat_id = data['chat_id'] == 2
            user_id = data['user_id'] == 32
            return chat_id and user_id

        monkeypatch.setattr('telegram.utils.request.Request.post', test)

        assert bot.unban_chat_member(2, 32)

    # TODO: Needs improvement. Need an incoming callbackquery to test
    def test_answer_callback_query(self, monkeypatch, bot):
        # For now just test that our internals pass the correct data
        def test(_, url, data, *args, **kwargs):
            return data == {'callback_query_id': 23, 'show_alert': True, 'url': 'no_url',
                            'cache_time': 1, 'text': 'answer'}

        monkeypatch.setattr('telegram.utils.request.Request.post', test)

        assert bot.answer_callback_query(23, text='answer', show_alert=True, url='no_url',
                                         cache_time=1)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_edit_message_text(self, bot, message):
        message = bot.edit_message_text(text='new_text', chat_id=message.chat_id,
                                        message_id=message.message_id, parse_mode='HTML',
                                        disable_web_page_preview=True)

        assert message.text == 'new_text'

    @pytest.mark.skip(reason='need reference to an inline message')
    def test_edit_message_text_inline(self):
        pass

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_edit_message_caption(self, bot, media_message):
        message = bot.edit_message_caption(caption='new_caption', chat_id=media_message.chat_id,
                                           message_id=media_message.message_id)

        assert message.caption == 'new_caption'

    # edit_message_media is tested in test_inputmedia

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_edit_message_caption_with_parse_mode(self, bot, media_message):
        message = bot.edit_message_caption(caption='new *caption*', parse_mode='Markdown',
                                           chat_id=media_message.chat_id,
                                           message_id=media_message.message_id)

        assert message.caption == 'new caption'

    def test_edit_message_caption_without_required(self, bot):
        with pytest.raises(ValueError, match='Both chat_id and message_id are required when'):
            bot.edit_message_caption(caption='new_caption')

    @pytest.mark.skip(reason='need reference to an inline message')
    def test_edit_message_caption_inline(self):
        pass

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_edit_reply_markup(self, bot, message):
        new_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text='test', callback_data='1')]])
        message = bot.edit_message_reply_markup(chat_id=message.chat_id,
                                                message_id=message.message_id,
                                                reply_markup=new_markup)

        assert message is not True

    def test_edit_message_reply_markup_without_required(self, bot):
        new_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text='test', callback_data='1')]])
        with pytest.raises(ValueError, match='Both chat_id and message_id are required when'):
            bot.edit_message_reply_markup(reply_markup=new_markup)

    @pytest.mark.skip(reason='need reference to an inline message')
    def test_edit_reply_markup_inline(self):
        pass

    # TODO: Actually send updates to the test bot so this can be tested properly
    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_updates(self, bot):
        bot.delete_webhook()  # make sure there is no webhook set if webhook tests failed
        updates = bot.get_updates(timeout=1)

        assert isinstance(updates, list)
        if updates:
            assert isinstance(updates[0], Update)

    @flaky(3, 1)
    @pytest.mark.timeout(15)
    @pytest.mark.xfail
    def test_set_webhook_get_webhook_info_and_delete_webhook(self, bot):
        url = 'https://python-telegram-bot.org/test/webhook'
        max_connections = 7
        allowed_updates = ['message']
        bot.set_webhook(url, max_connections=max_connections, allowed_updates=allowed_updates)
        time.sleep(2)
        live_info = bot.get_webhook_info()
        time.sleep(6)
        bot.delete_webhook()
        time.sleep(2)
        info = bot.get_webhook_info()
        assert info.url == ''
        assert live_info.url == url
        assert live_info.max_connections == max_connections
        assert live_info.allowed_updates == allowed_updates

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_leave_chat(self, bot):
        with pytest.raises(BadRequest, match='Chat not found'):
            bot.leave_chat(-123456)

        with pytest.raises(NetworkError, match='Chat not found'):
            bot.leave_chat(-123456)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_chat(self, bot, group_id):
        chat = bot.get_chat(group_id)

        assert chat.type == 'group'
        assert chat.title == '>>> telegram.Bot(test)'
        assert chat.id == int(group_id)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_chat_administrators(self, bot, channel_id):
        admins = bot.get_chat_administrators(channel_id)
        assert isinstance(admins, list)

        for a in admins:
            assert a.status in ('administrator', 'creator')

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_chat_members_count(self, bot, channel_id):
        count = bot.get_chat_members_count(channel_id)
        assert isinstance(count, int)
        assert count > 3

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_chat_member(self, bot, channel_id, chat_id):
        chat_member = bot.get_chat_member(channel_id, chat_id)

        assert chat_member.status == 'administrator'
        assert chat_member.user.first_name == 'PTB'
        assert chat_member.user.last_name == 'Test user'

    @pytest.mark.skip(reason="Not implemented yet.")
    def test_set_chat_sticker_set(self):
        pass

    @pytest.mark.skip(reason="Not implemented yet.")
    def test_delete_chat_sticker_set(self):
        pass

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_set_game_score_1(self, bot, chat_id):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        game_short_name = 'test_game'
        game = bot.send_game(chat_id, game_short_name)

        message = bot.set_game_score(
            user_id=chat_id,
            score=int(BASE_TIME) - HIGHSCORE_DELTA,
            chat_id=game.chat_id,
            message_id=game.message_id)

        assert message.game.description == game.game.description
        assert message.game.animation.file_id == game.game.animation.file_id
        assert message.game.photo[0].file_size == game.game.photo[0].file_size
        assert message.game.text != game.game.text

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_set_game_score_2(self, bot, chat_id):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        game_short_name = 'test_game'
        game = bot.send_game(chat_id, game_short_name)

        score = int(BASE_TIME) - HIGHSCORE_DELTA + 1

        message = bot.set_game_score(
            user_id=chat_id,
            score=score,
            chat_id=game.chat_id,
            message_id=game.message_id,
            disable_edit_message=True)

        assert message.game.description == game.game.description
        assert message.game.animation.file_id == game.game.animation.file_id
        assert message.game.photo[0].file_size == game.game.photo[0].file_size
        assert message.game.text == game.game.text

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_set_game_score_3(self, bot, chat_id):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        game_short_name = 'test_game'
        game = bot.send_game(chat_id, game_short_name)

        score = int(BASE_TIME) - HIGHSCORE_DELTA - 1

        with pytest.raises(BadRequest, match='Bot_score_not_modified'):
            bot.set_game_score(
                user_id=chat_id,
                score=score,
                chat_id=game.chat_id,
                message_id=game.message_id)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_set_game_score_4(self, bot, chat_id):
        # NOTE: numbering of methods assures proper order between test_set_game_scoreX methods
        game_short_name = 'test_game'
        game = bot.send_game(chat_id, game_short_name)

        score = int(BASE_TIME) - HIGHSCORE_DELTA - 2

        message = bot.set_game_score(
            user_id=chat_id,
            score=score,
            chat_id=game.chat_id,
            message_id=game.message_id,
            force=True)

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
        game_short_name = 'test_game'
        game = bot.send_game(chat_id, game_short_name)

        with pytest.raises(BadRequest):
            bot.set_game_score(user_id=chat_id, score=100,
                               chat_id=game.chat_id, message_id=game.message_id)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_game_high_scores(self, bot, chat_id):
        # We need a game to get the scores for
        game_short_name = 'test_game'
        game = bot.send_game(chat_id, game_short_name)
        high_scores = bot.get_game_high_scores(chat_id, game.chat_id, game.message_id)
        # We assume that the other game score tests ran within 20 sec
        assert pytest.approx(high_scores[0].score, abs=20) == int(BASE_TIME) - HIGHSCORE_DELTA

    # send_invoice is tested in test_invoice

    # TODO: Needs improvement. Need incoming shippping queries to test
    def test_answer_shipping_query_ok(self, monkeypatch, bot):
        # For now just test that our internals pass the correct data
        def test(_, url, data, *args, **kwargs):
            return data == {'shipping_query_id': 1, 'ok': True,
                            'shipping_options': [{'title': 'option1',
                                                  'prices': [{'label': 'price', 'amount': 100}],
                                                  'id': 1}]}

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        shipping_options = ShippingOption(1, 'option1', [LabeledPrice('price', 100)])
        assert bot.answer_shipping_query(1, True, shipping_options=[shipping_options])

    def test_answer_shipping_query_error_message(self, monkeypatch, bot):
        # For now just test that our internals pass the correct data
        def test(_, url, data, *args, **kwargs):
            return data == {'shipping_query_id': 1, 'error_message': 'Not enough fish',
                            'ok': False}

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        assert bot.answer_shipping_query(1, False, error_message='Not enough fish')

    def test_answer_shipping_query_errors(self, monkeypatch, bot):
        shipping_options = ShippingOption(1, 'option1', [LabeledPrice('price', 100)])

        with pytest.raises(TelegramError, match='should not be empty and there should not be'):
            bot.answer_shipping_query(1, True, error_message='Not enough fish')

        with pytest.raises(TelegramError, match='should not be empty and there should not be'):
            bot.answer_shipping_query(1, False)

        with pytest.raises(TelegramError, match='should not be empty and there should not be'):
            bot.answer_shipping_query(1, False, shipping_options=shipping_options)

        with pytest.raises(TelegramError, match='should not be empty and there should not be'):
            bot.answer_shipping_query(1, True)

    # TODO: Needs improvement. Need incoming pre checkout queries to test
    def test_answer_pre_checkout_query_ok(self, monkeypatch, bot):
        # For now just test that our internals pass the correct data
        def test(_, url, data, *args, **kwargs):
            return data == {'pre_checkout_query_id': 1, 'ok': True}

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        assert bot.answer_pre_checkout_query(1, True)

    def test_answer_pre_checkout_query_error_message(self, monkeypatch, bot):
        # For now just test that our internals pass the correct data
        def test(_, url, data, *args, **kwargs):
            return data == {'pre_checkout_query_id': 1, 'error_message': 'Not enough fish',
                            'ok': False}

        monkeypatch.setattr('telegram.utils.request.Request.post', test)
        assert bot.answer_pre_checkout_query(1, False, error_message='Not enough fish')

    def test_answer_pre_checkout_query_errors(self, monkeypatch, bot):
        with pytest.raises(TelegramError, match='should not be'):
            bot.answer_pre_checkout_query(1, True, error_message='Not enough fish')

        with pytest.raises(TelegramError, match='should not be empty'):
            bot.answer_pre_checkout_query(1, False)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_restrict_chat_member(self, bot, channel_id):
        # TODO: Add bot to supergroup so this can be tested properly
        with pytest.raises(BadRequest, match='Method is available only for supergroups'):
            assert bot.restrict_chat_member(channel_id,
                                            95205500,
                                            until_date=datetime.now(),
                                            can_send_messages=False,
                                            can_send_media_messages=False,
                                            can_send_other_messages=False,
                                            can_add_web_page_previews=False)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_promote_chat_member(self, bot, channel_id):
        # TODO: Add bot to supergroup so this can be tested properly / give bot perms
        with pytest.raises(BadRequest, match='Not enough rights'):
            assert bot.promote_chat_member(channel_id,
                                           95205500,
                                           can_change_info=True,
                                           can_post_messages=True,
                                           can_edit_messages=True,
                                           can_delete_messages=True,
                                           can_invite_users=True,
                                           can_restrict_members=True,
                                           can_pin_messages=True,
                                           can_promote_members=True)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_export_chat_invite_link(self, bot, channel_id):
        # Each link is unique apparently
        invite_link = bot.export_chat_invite_link(channel_id)
        assert isinstance(invite_link, string_types)
        assert invite_link != ''

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_delete_chat_photo(self, bot, channel_id):
        assert bot.delete_chat_photo(channel_id)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_set_chat_photo(self, bot, channel_id):
        with open('tests/data/telegram_test_channel.jpg', 'rb') as f:
            assert bot.set_chat_photo(channel_id, f)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_set_chat_title(self, bot, channel_id):
        assert bot.set_chat_title(channel_id, '>>> telegram.Bot() - Tests')

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_set_chat_description(self, bot, channel_id):
        assert bot.set_chat_description(channel_id, 'Time: ' + str(time.time()))

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_pin_unpin_message(self, bot, message):
        # TODO: Add bot to supergroup so this can be tested properly
        with pytest.raises(BadRequest, match='Method is available only for supergroups'):
            bot.pin_chat_message(message.chat_id, message.message_id, disable_notification=True)

        with pytest.raises(BadRequest, match='Method is available only for supergroups'):
            bot.unpin_chat_message(message.chat_id)

    # get_sticker_set, upload_sticker_file, create_new_sticker_set, add_sticker_to_set,
    # set_sticker_position_in_set and delete_sticker_from_set are tested in the
    # test_sticker module.

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
