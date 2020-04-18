#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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

import pytest

from telegram import Message, User, Chat, MessageEntity, Document, Update, Dice
from telegram.ext import Filters, BaseFilter
import re


@pytest.fixture(scope='function')
def update():
    return Update(0, Message(0, User(0, 'Testuser', False), datetime.datetime.utcnow(),
                             Chat(0, 'private')))


@pytest.fixture(scope='function',
                params=MessageEntity.ALL_TYPES)
def message_entity(request):
    return MessageEntity(request.param, 0, 0, url='', user='')


class TestFilters(object):
    def test_filters_all(self, update):
        assert Filters.all(update)

    def test_filters_text(self, update):
        update.message.text = 'test'
        assert (Filters.text)(update)
        update.message.text = '/test'
        assert (Filters.text)(update)

    def test_filters_text_strings(self, update):
        update.message.text = '/test'
        assert Filters.text({'/test', 'test1'})(update)
        assert not Filters.text(['test1', 'test2'])(update)

    def test_filters_caption(self, update):
        update.message.caption = 'test'
        assert (Filters.caption)(update)
        update.message.caption = None
        assert not (Filters.caption)(update)

    def test_filters_caption_strings(self, update):
        update.message.caption = 'test'
        assert Filters.caption({'test', 'test1'})(update)
        assert not Filters.caption(['test1', 'test2'])(update)

    def test_filters_command_default(self, update):
        update.message.text = 'test'
        assert not Filters.command(update)
        update.message.text = '/test'
        assert not Filters.command(update)
        # Only accept commands at the beginning
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 3, 5)]
        assert not Filters.command(update)
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]
        assert Filters.command(update)

    def test_filters_command_anywhere(self, update):
        update.message.text = 'test /cmd'
        assert not (Filters.command(False))(update)
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 5, 4)]
        assert (Filters.command(False))(update)

    def test_filters_regex(self, update):
        SRE_TYPE = type(re.match("", ""))
        update.message.text = '/start deep-linked param'
        result = Filters.regex(r'deep-linked param')(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert type(matches[0]) is SRE_TYPE
        update.message.text = '/help'
        assert Filters.regex(r'help')(update)

        update.message.text = 'test'
        assert not Filters.regex(r'fail')(update)
        assert Filters.regex(r'test')(update)
        assert Filters.regex(re.compile(r'test'))(update)
        assert Filters.regex(re.compile(r'TEST', re.IGNORECASE))(update)

        update.message.text = 'i love python'
        assert Filters.regex(r'.\b[lo]{2}ve python')(update)

        update.message.text = None
        assert not Filters.regex(r'fail')(update)

    def test_filters_regex_multiple(self, update):
        SRE_TYPE = type(re.match("", ""))
        update.message.text = '/start deep-linked param'
        result = (Filters.regex('deep') & Filters.regex(r'linked param'))(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all([type(res) == SRE_TYPE for res in matches])
        result = (Filters.regex('deep') | Filters.regex(r'linked param'))(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all([type(res) == SRE_TYPE for res in matches])
        result = (Filters.regex('not int') | Filters.regex(r'linked param'))(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all([type(res) == SRE_TYPE for res in matches])
        result = (Filters.regex('not int') & Filters.regex(r'linked param'))(update)
        assert not result

    def test_filters_merged_with_regex(self, update):
        SRE_TYPE = type(re.match("", ""))
        update.message.text = '/start deep-linked param'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = (Filters.command & Filters.regex(r'linked param'))(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all([type(res) == SRE_TYPE for res in matches])
        result = (Filters.regex(r'linked param') & Filters.command)(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all([type(res) == SRE_TYPE for res in matches])
        result = (Filters.regex(r'linked param') | Filters.command)(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all([type(res) == SRE_TYPE for res in matches])
        # Should not give a match since it's a or filter and it short circuits
        result = (Filters.command | Filters.regex(r'linked param'))(update)
        assert result is True

    def test_regex_complex_merges(self, update):
        SRE_TYPE = type(re.match("", ""))
        update.message.text = 'test it out'
        filter = (Filters.regex('test')
                  & ((Filters.status_update | Filters.forwarded) | Filters.regex('out')))
        result = filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert len(matches) == 2
        assert all([type(res) == SRE_TYPE for res in matches])
        update.message.forward_date = datetime.datetime.utcnow()
        result = filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all([type(res) == SRE_TYPE for res in matches])
        update.message.text = 'test it'
        result = filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all([type(res) == SRE_TYPE for res in matches])
        update.message.forward_date = False
        result = filter(update)
        assert not result
        update.message.text = 'test it out'
        result = filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all([type(res) == SRE_TYPE for res in matches])
        update.message.pinned_message = True
        result = filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all([type(res) == SRE_TYPE for res in matches])
        update.message.text = 'it out'
        result = filter(update)
        assert not result

        update.message.text = 'test it out'
        update.message.forward_date = None
        update.message.pinned_message = None
        filter = ((Filters.regex('test') | Filters.command)
                  & (Filters.regex('it') | Filters.status_update))
        result = filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert len(matches) == 2
        assert all([type(res) == SRE_TYPE for res in matches])
        update.message.text = 'test'
        result = filter(update)
        assert not result
        update.message.pinned_message = True
        result = filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert len(matches) == 1
        assert all([type(res) == SRE_TYPE for res in matches])
        update.message.text = 'nothing'
        result = filter(update)
        assert not result
        update.message.text = '/start'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = filter(update)
        assert result
        assert isinstance(result, bool)
        update.message.text = '/start it'
        result = filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert len(matches) == 1
        assert all([type(res) == SRE_TYPE for res in matches])

    def test_regex_inverted(self, update):
        update.message.text = '/start deep-linked param'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]
        filter = ~Filters.regex(r'deep-linked param')
        result = filter(update)
        assert not result
        update.message.text = 'not it'
        result = filter(update)
        assert result
        assert isinstance(result, bool)

        filter = (~Filters.regex('linked') & Filters.command)
        update.message.text = "it's linked"
        result = filter(update)
        assert not result
        update.message.text = '/start'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = filter(update)
        assert result
        update.message.text = '/linked'
        result = filter(update)
        assert not result

        filter = (~Filters.regex('linked') | Filters.command)
        update.message.text = "it's linked"
        update.message.entities = []
        result = filter(update)
        assert not result
        update.message.text = '/start linked'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = filter(update)
        assert result
        update.message.text = '/start'
        result = filter(update)
        assert result
        update.message.text = 'nothig'
        update.message.entities = []
        result = filter(update)
        assert result

    def test_filters_reply(self, update):
        another_message = Message(1, User(1, 'TestOther', False), datetime.datetime.utcnow(),
                                  Chat(0, 'private'))
        update.message.text = 'test'
        assert not Filters.reply(update)
        update.message.reply_to_message = another_message
        assert Filters.reply(update)

    def test_filters_audio(self, update):
        assert not Filters.audio(update)
        update.message.audio = 'test'
        assert Filters.audio(update)

    def test_filters_document(self, update):
        assert not Filters.document(update)
        update.message.document = 'test'
        assert Filters.document(update)

    def test_filters_document_type(self, update):
        update.message.document = Document("file_id", 'unique_id',
                                           mime_type="application/vnd.android.package-archive")
        assert Filters.document.apk(update)
        assert Filters.document.application(update)
        assert not Filters.document.doc(update)
        assert not Filters.document.audio(update)

        update.message.document.mime_type = "application/msword"
        assert Filters.document.doc(update)
        assert Filters.document.application(update)
        assert not Filters.document.docx(update)
        assert not Filters.document.audio(update)

        update.message.document.mime_type = "application/vnd.openxmlformats-officedocument." \
                                            "wordprocessingml.document"
        assert Filters.document.docx(update)
        assert Filters.document.application(update)
        assert not Filters.document.exe(update)
        assert not Filters.document.audio(update)

        update.message.document.mime_type = "application/x-ms-dos-executable"
        assert Filters.document.exe(update)
        assert Filters.document.application(update)
        assert not Filters.document.docx(update)
        assert not Filters.document.audio(update)

        update.message.document.mime_type = "video/mp4"
        assert Filters.document.gif(update)
        assert Filters.document.video(update)
        assert not Filters.document.jpg(update)
        assert not Filters.document.text(update)

        update.message.document.mime_type = "image/jpeg"
        assert Filters.document.jpg(update)
        assert Filters.document.image(update)
        assert not Filters.document.mp3(update)
        assert not Filters.document.video(update)

        update.message.document.mime_type = "audio/mpeg"
        assert Filters.document.mp3(update)
        assert Filters.document.audio(update)
        assert not Filters.document.pdf(update)
        assert not Filters.document.image(update)

        update.message.document.mime_type = "application/pdf"
        assert Filters.document.pdf(update)
        assert Filters.document.application(update)
        assert not Filters.document.py(update)
        assert not Filters.document.audio(update)

        update.message.document.mime_type = "text/x-python"
        assert Filters.document.py(update)
        assert Filters.document.text(update)
        assert not Filters.document.svg(update)
        assert not Filters.document.application(update)

        update.message.document.mime_type = "image/svg+xml"
        assert Filters.document.svg(update)
        assert Filters.document.image(update)
        assert not Filters.document.txt(update)
        assert not Filters.document.video(update)

        update.message.document.mime_type = "text/plain"
        assert Filters.document.txt(update)
        assert Filters.document.text(update)
        assert not Filters.document.targz(update)
        assert not Filters.document.application(update)

        update.message.document.mime_type = "application/x-compressed-tar"
        assert Filters.document.targz(update)
        assert Filters.document.application(update)
        assert not Filters.document.wav(update)
        assert not Filters.document.audio(update)

        update.message.document.mime_type = "audio/x-wav"
        assert Filters.document.wav(update)
        assert Filters.document.audio(update)
        assert not Filters.document.xml(update)
        assert not Filters.document.image(update)

        update.message.document.mime_type = "application/xml"
        assert Filters.document.xml(update)
        assert Filters.document.application(update)
        assert not Filters.document.zip(update)
        assert not Filters.document.audio(update)

        update.message.document.mime_type = "application/zip"
        assert Filters.document.zip(update)
        assert Filters.document.application(update)
        assert not Filters.document.apk(update)
        assert not Filters.document.audio(update)

        update.message.document.mime_type = "image/x-rgb"
        assert not Filters.document.category("application/")(update)
        assert not Filters.document.mime_type("application/x-sh")(update)
        update.message.document.mime_type = "application/x-sh"
        assert Filters.document.category("application/")(update)
        assert Filters.document.mime_type("application/x-sh")(update)

    def test_filters_animation(self, update):
        assert not Filters.animation(update)
        update.message.animation = 'test'
        assert Filters.animation(update)

    def test_filters_photo(self, update):
        assert not Filters.photo(update)
        update.message.photo = 'test'
        assert Filters.photo(update)

    def test_filters_sticker(self, update):
        assert not Filters.sticker(update)
        update.message.sticker = 'test'
        assert Filters.sticker(update)

    def test_filters_video(self, update):
        assert not Filters.video(update)
        update.message.video = 'test'
        assert Filters.video(update)

    def test_filters_voice(self, update):
        assert not Filters.voice(update)
        update.message.voice = 'test'
        assert Filters.voice(update)

    def test_filters_video_note(self, update):
        assert not Filters.video_note(update)
        update.message.video_note = 'test'
        assert Filters.video_note(update)

    def test_filters_contact(self, update):
        assert not Filters.contact(update)
        update.message.contact = 'test'
        assert Filters.contact(update)

    def test_filters_location(self, update):
        assert not Filters.location(update)
        update.message.location = 'test'
        assert Filters.location(update)

    def test_filters_venue(self, update):
        assert not Filters.venue(update)
        update.message.venue = 'test'
        assert Filters.venue(update)

    def test_filters_status_update(self, update):
        assert not Filters.status_update(update)

        update.message.new_chat_members = ['test']
        assert Filters.status_update(update)
        assert Filters.status_update.new_chat_members(update)
        update.message.new_chat_members = None

        update.message.left_chat_member = 'test'
        assert Filters.status_update(update)
        assert Filters.status_update.left_chat_member(update)
        update.message.left_chat_member = None

        update.message.new_chat_title = 'test'
        assert Filters.status_update(update)
        assert Filters.status_update.new_chat_title(update)
        update.message.new_chat_title = ''

        update.message.new_chat_photo = 'test'
        assert Filters.status_update(update)
        assert Filters.status_update.new_chat_photo(update)
        update.message.new_chat_photo = None

        update.message.delete_chat_photo = True
        assert Filters.status_update(update)
        assert Filters.status_update.delete_chat_photo(update)
        update.message.delete_chat_photo = False

        update.message.group_chat_created = True
        assert Filters.status_update(update)
        assert Filters.status_update.chat_created(update)
        update.message.group_chat_created = False

        update.message.supergroup_chat_created = True
        assert Filters.status_update(update)
        assert Filters.status_update.chat_created(update)
        update.message.supergroup_chat_created = False

        update.message.channel_chat_created = True
        assert Filters.status_update(update)
        assert Filters.status_update.chat_created(update)
        update.message.channel_chat_created = False

        update.message.migrate_to_chat_id = 100
        assert Filters.status_update(update)
        assert Filters.status_update.migrate(update)
        update.message.migrate_to_chat_id = 0

        update.message.migrate_from_chat_id = 100
        assert Filters.status_update(update)
        assert Filters.status_update.migrate(update)
        update.message.migrate_from_chat_id = 0

        update.message.pinned_message = 'test'
        assert Filters.status_update(update)
        assert Filters.status_update.pinned_message(update)
        update.message.pinned_message = None

        update.message.connected_website = 'http://example.com/'
        assert Filters.status_update(update)
        assert Filters.status_update.connected_website(update)
        update.message.connected_website = None

    def test_filters_forwarded(self, update):
        assert not Filters.forwarded(update)
        update.message.forward_date = datetime.datetime.utcnow()
        assert Filters.forwarded(update)

    def test_filters_game(self, update):
        assert not Filters.game(update)
        update.message.game = 'test'
        assert Filters.game(update)

    def test_entities_filter(self, update, message_entity):
        update.message.entities = [message_entity]
        assert Filters.entity(message_entity.type)(update)

        update.message.entities = []
        assert not Filters.entity(MessageEntity.MENTION)(update)

        second = message_entity.to_dict()
        second['type'] = 'bold'
        second = MessageEntity.de_json(second, None)
        update.message.entities = [message_entity, second]
        assert Filters.entity(message_entity.type)(update)
        assert not Filters.caption_entity(message_entity.type)(update)

    def test_caption_entities_filter(self, update, message_entity):
        update.message.caption_entities = [message_entity]
        assert Filters.caption_entity(message_entity.type)(update)

        update.message.caption_entities = []
        assert not Filters.caption_entity(MessageEntity.MENTION)(update)

        second = message_entity.to_dict()
        second['type'] = 'bold'
        second = MessageEntity.de_json(second, None)
        update.message.caption_entities = [message_entity, second]
        assert Filters.caption_entity(message_entity.type)(update)
        assert not Filters.entity(message_entity.type)(update)

    def test_private_filter(self, update):
        assert Filters.private(update)
        update.message.chat.type = 'group'
        assert not Filters.private(update)

    def test_group_filter(self, update):
        assert not Filters.group(update)
        update.message.chat.type = 'group'
        assert Filters.group(update)
        update.message.chat.type = 'supergroup'
        assert Filters.group(update)

    def test_filters_user(self):
        with pytest.raises(ValueError, match='user_id or username'):
            Filters.user(user_id=1, username='user')
        with pytest.raises(ValueError, match='user_id or username'):
            Filters.user()

    def test_filters_user_id(self, update):
        assert not Filters.user(user_id=1)(update)
        update.message.from_user.id = 1
        assert Filters.user(user_id=1)(update)
        update.message.from_user.id = 2
        assert Filters.user(user_id=[1, 2])(update)
        assert not Filters.user(user_id=[3, 4])(update)

    def test_filters_username(self, update):
        assert not Filters.user(username='user')(update)
        assert not Filters.user(username='Testuser')(update)
        update.message.from_user.username = 'user'
        assert Filters.user(username='@user')(update)
        assert Filters.user(username='user')(update)
        assert Filters.user(username=['user1', 'user', 'user2'])(update)
        assert not Filters.user(username=['@username', '@user_2'])(update)

    def test_filters_chat(self):
        with pytest.raises(ValueError, match='chat_id or username'):
            Filters.chat(chat_id=-1, username='chat')
        with pytest.raises(ValueError, match='chat_id or username'):
            Filters.chat()

    def test_filters_chat_id(self, update):
        assert not Filters.chat(chat_id=-1)(update)
        update.message.chat.id = -1
        assert Filters.chat(chat_id=-1)(update)
        update.message.chat.id = -2
        assert Filters.chat(chat_id=[-1, -2])(update)
        assert not Filters.chat(chat_id=[-3, -4])(update)

    def test_filters_chat_username(self, update):
        assert not Filters.chat(username='chat')(update)
        update.message.chat.username = 'chat'
        assert Filters.chat(username='@chat')(update)
        assert Filters.chat(username='chat')(update)
        assert Filters.chat(username=['chat1', 'chat', 'chat2'])(update)
        assert not Filters.chat(username=['@chat1', 'chat_2'])(update)

    def test_filters_invoice(self, update):
        assert not Filters.invoice(update)
        update.message.invoice = 'test'
        assert Filters.invoice(update)

    def test_filters_successful_payment(self, update):
        assert not Filters.successful_payment(update)
        update.message.successful_payment = 'test'
        assert Filters.successful_payment(update)

    def test_filters_passport_data(self, update):
        assert not Filters.passport_data(update)
        update.message.passport_data = 'test'
        assert Filters.passport_data(update)

    def test_filters_poll(self, update):
        assert not Filters.poll(update)
        update.message.poll = 'test'
        assert Filters.poll(update)

    def test_filters_dice(self, update):
        update.message.dice = Dice(4)
        assert Filters.dice(update)
        update.message.dice = None
        assert not Filters.dice(update)

    def test_filters_dice_iterable(self, update):
        update.message.dice = None
        assert not Filters.dice(5)(update)

        update.message.dice = Dice(5)
        assert Filters.dice(5)(update)
        assert Filters.dice({5, 6})(update)
        assert not Filters.dice(1)(update)
        assert not Filters.dice([2, 3])(update)

    def test_language_filter_single(self, update):
        update.message.from_user.language_code = 'en_US'
        assert (Filters.language('en_US'))(update)
        assert (Filters.language('en'))(update)
        assert not (Filters.language('en_GB'))(update)
        assert not (Filters.language('da'))(update)
        update.message.from_user.language_code = 'da'
        assert not (Filters.language('en_US'))(update)
        assert not (Filters.language('en'))(update)
        assert not (Filters.language('en_GB'))(update)
        assert (Filters.language('da'))(update)

    def test_language_filter_multiple(self, update):
        f = Filters.language(['en_US', 'da'])
        update.message.from_user.language_code = 'en_US'
        assert f(update)
        update.message.from_user.language_code = 'en_GB'
        assert not f(update)
        update.message.from_user.language_code = 'da'
        assert f(update)

    def test_and_filters(self, update):
        update.message.text = 'test'
        update.message.forward_date = datetime.datetime.utcnow()
        assert (Filters.text & Filters.forwarded)(update)
        update.message.text = '/test'
        assert (Filters.text & Filters.forwarded)(update)
        update.message.text = 'test'
        update.message.forward_date = None
        assert not (Filters.text & Filters.forwarded)(update)

        update.message.text = 'test'
        update.message.forward_date = datetime.datetime.utcnow()
        assert (Filters.text & Filters.forwarded & Filters.private)(update)

    def test_or_filters(self, update):
        update.message.text = 'test'
        assert (Filters.text | Filters.status_update)(update)
        update.message.group_chat_created = True
        assert (Filters.text | Filters.status_update)(update)
        update.message.text = None
        assert (Filters.text | Filters.status_update)(update)
        update.message.group_chat_created = False
        assert not (Filters.text | Filters.status_update)(update)

    def test_and_or_filters(self, update):
        update.message.text = 'test'
        update.message.forward_date = datetime.datetime.utcnow()
        assert (Filters.text & (Filters.status_update | Filters.forwarded))(update)
        update.message.forward_date = False
        assert not (Filters.text & (Filters.forwarded | Filters.status_update))(update)
        update.message.pinned_message = True
        assert (Filters.text & (Filters.forwarded | Filters.status_update)(update))

        assert str((Filters.text & (Filters.forwarded | Filters.entity(
            MessageEntity.MENTION)))) == '<Filters.text and <Filters.forwarded or ' \
                                         'Filters.entity(mention)>>'

    def test_inverted_filters(self, update):
        update.message.text = '/test'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]
        assert Filters.command(update)
        assert not (~Filters.command)(update)
        update.message.text = 'test'
        update.message.entities = []
        assert not Filters.command(update)
        assert (~Filters.command)(update)

    def test_inverted_and_filters(self, update):
        update.message.text = '/test'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]
        update.message.forward_date = 1
        assert (Filters.forwarded & Filters.command)(update)
        assert not (~Filters.forwarded & Filters.command)(update)
        assert not (Filters.forwarded & ~Filters.command)(update)
        assert not (~(Filters.forwarded & Filters.command))(update)
        update.message.forward_date = None
        assert not (Filters.forwarded & Filters.command)(update)
        assert (~Filters.forwarded & Filters.command)(update)
        assert not (Filters.forwarded & ~Filters.command)(update)
        assert (~(Filters.forwarded & Filters.command))(update)
        update.message.text = 'test'
        update.message.entities = []
        assert not (Filters.forwarded & Filters.command)(update)
        assert not (~Filters.forwarded & Filters.command)(update)
        assert not (Filters.forwarded & ~Filters.command)(update)
        assert (~(Filters.forwarded & Filters.command))(update)

    def test_faulty_custom_filter(self, update):
        class _CustomFilter(BaseFilter):
            pass

        custom = _CustomFilter()

        with pytest.raises(NotImplementedError):
            (custom & Filters.text)(update)

    def test_custom_unnamed_filter(self, update):
        class Unnamed(BaseFilter):
            def filter(self, mes):
                return True

        unnamed = Unnamed()
        assert str(unnamed) == Unnamed.__name__

    def test_update_type_message(self, update):
        assert Filters.update.message(update)
        assert not Filters.update.edited_message(update)
        assert Filters.update.messages(update)
        assert not Filters.update.channel_post(update)
        assert not Filters.update.edited_channel_post(update)
        assert not Filters.update.channel_posts(update)
        assert Filters.update(update)

    def test_update_type_edited_message(self, update):
        update.edited_message, update.message = update.message, update.edited_message
        assert not Filters.update.message(update)
        assert Filters.update.edited_message(update)
        assert Filters.update.messages(update)
        assert not Filters.update.channel_post(update)
        assert not Filters.update.edited_channel_post(update)
        assert not Filters.update.channel_posts(update)
        assert Filters.update(update)

    def test_update_type_channel_post(self, update):
        update.channel_post, update.message = update.message, update.edited_message
        assert not Filters.update.message(update)
        assert not Filters.update.edited_message(update)
        assert not Filters.update.messages(update)
        assert Filters.update.channel_post(update)
        assert not Filters.update.edited_channel_post(update)
        assert Filters.update.channel_posts(update)
        assert Filters.update(update)

    def test_update_type_edited_channel_post(self, update):
        update.edited_channel_post, update.message = update.message, update.edited_message
        assert not Filters.update.message(update)
        assert not Filters.update.edited_message(update)
        assert not Filters.update.messages(update)
        assert not Filters.update.channel_post(update)
        assert Filters.update.edited_channel_post(update)
        assert Filters.update.channel_posts(update)
        assert Filters.update(update)

    def test_merged_short_circuit_and(self, update):
        update.message.text = '/test'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]

        class TestException(Exception):
            pass

        class RaisingFilter(BaseFilter):
            def filter(self, _):
                raise TestException

        raising_filter = RaisingFilter()

        with pytest.raises(TestException):
            (Filters.command & raising_filter)(update)

        update.message.text = 'test'
        update.message.entities = []
        (Filters.command & raising_filter)(update)

    def test_merged_short_circuit_or(self, update):
        update.message.text = 'test'

        class TestException(Exception):
            pass

        class RaisingFilter(BaseFilter):
            def filter(self, _):
                raise TestException

        raising_filter = RaisingFilter()

        with pytest.raises(TestException):
            (Filters.command | raising_filter)(update)

        update.message.text = '/test'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]
        (Filters.command | raising_filter)(update)

    def test_merged_data_merging_and(self, update):
        update.message.text = '/test'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]

        class DataFilter(BaseFilter):
            data_filter = True

            def __init__(self, data):
                self.data = data

            def filter(self, _):
                return {'test': [self.data]}

        result = (Filters.command & DataFilter('blah'))(update)
        assert result['test'] == ['blah']

        result = (DataFilter('blah1') & DataFilter('blah2'))(update)
        assert result['test'] == ['blah1', 'blah2']

        update.message.text = 'test'
        update.message.entities = []
        result = (Filters.command & DataFilter('blah'))(update)
        assert not result

    def test_merged_data_merging_or(self, update):
        update.message.text = '/test'

        class DataFilter(BaseFilter):
            data_filter = True

            def __init__(self, data):
                self.data = data

            def filter(self, _):
                return {'test': [self.data]}

        result = (Filters.command | DataFilter('blah'))(update)
        assert result

        result = (DataFilter('blah1') | DataFilter('blah2'))(update)
        assert result['test'] == ['blah1']

        update.message.text = 'test'
        result = (Filters.command | DataFilter('blah'))(update)
        assert result['test'] == ['blah']
