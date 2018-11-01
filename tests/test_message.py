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
from datetime import datetime

import pytest

from telegram import ParseMode
from telegram import (Update, Message, User, MessageEntity, Chat, Audio, Document, Animation,
                      Game, PhotoSize, Sticker, Video, Voice, VideoNote, Contact, Location, Venue,
                      Invoice, SuccessfulPayment, PassportData)
from tests.test_passport import RAW_PASSPORT_DATA


@pytest.fixture(scope='class')
def message(bot):
    return Message(TestMessage.id, TestMessage.from_user, TestMessage.date, TestMessage.chat,
                   bot=bot)


@pytest.fixture(scope='function',
                params=[
                    {'forward_from': User(99, 'forward_user', False),
                     'forward_date': datetime.now()},
                    {'forward_from_chat': Chat(-23, 'channel'),
                     'forward_from_message_id': 101,
                     'forward_date': datetime.now()},
                    {'reply_to_message': Message(50, None, None, None)},
                    {'edit_date': datetime.now()},
                    {'text': 'a text message',
                     'enitites': [MessageEntity('bold', 10, 4),
                                  MessageEntity('italic', 16, 7)]},
                    {'caption': 'A message caption',
                     'caption_entities': [MessageEntity('bold', 1, 1),
                                          MessageEntity('text_link', 4, 3)]},
                    {'audio': Audio('audio_id', 12),
                     'caption': 'audio_file'},
                    {'document': Document('document_id'),
                     'caption': 'document_file'},
                    {'animation': Animation('animation_id', 30, 30, 1),
                     'caption': 'animation_file'},
                    {'game': Game('my_game', 'just my game',
                                  [PhotoSize('game_photo_id', 30, 30), ])},
                    {'photo': [PhotoSize('photo_id', 50, 50)],
                     'caption': 'photo_file'},
                    {'sticker': Sticker('sticker_id', 50, 50)},
                    {'video': Video('video_id', 12, 12, 12),
                     'caption': 'video_file'},
                    {'voice': Voice('voice_id', 5)},
                    {'video_note': VideoNote('video_note_id', 20, 12)},
                    {'new_chat_members': [User(55, 'new_user', False)]},
                    {'contact': Contact('phone_numner', 'contact_name')},
                    {'location': Location(-23.691288, 46.788279)},
                    {'venue': Venue(Location(-23.691288, 46.788279),
                                    'some place', 'right here')},
                    {'left_chat_member': User(33, 'kicked', False)},
                    {'new_chat_title': 'new title'},
                    {'new_chat_photo': [PhotoSize('photo_id', 50, 50)]},
                    {'delete_chat_photo': True},
                    {'group_chat_created': True},
                    {'supergroup_chat_created': True},
                    {'channel_chat_created': True},
                    {'migrate_to_chat_id': -12345},
                    {'migrate_from_chat_id': -54321},
                    {'pinned_message': Message(7, None, None, None)},
                    {'invoice': Invoice('my invoice', 'invoice', 'start', 'EUR', 243)},
                    {'successful_payment': SuccessfulPayment('EUR', 243, 'payload',
                                                             'charge_id', 'provider_id',
                                                             order_info={})},
                    {'connected_website': 'http://example.com/'},
                    {'forward_signature': 'some_forward_sign'},
                    {'author_signature': 'some_author_sign'},
                    {'photo': [PhotoSize('photo_id', 50, 50)],
                     'caption': 'photo_file',
                     'media_group_id': 1234443322222},
                    {'passport_data': PassportData.de_json(RAW_PASSPORT_DATA, None)}
                ],
                ids=['forwarded_user', 'forwarded_channel', 'reply', 'edited', 'text',
                     'caption_entities', 'audio', 'document', 'animation', 'game', 'photo',
                     'sticker', 'video', 'voice', 'video_note', 'new_members', 'contact',
                     'location', 'venue', 'left_member', 'new_title', 'new_photo', 'delete_photo',
                     'group_created', 'supergroup_created', 'channel_created', 'migrated_to',
                     'migrated_from', 'pinned', 'invoice', 'successful_payment',
                     'connected_website', 'forward_signature', 'author_signature',
                     'photo_from_media_group', 'passport_data'])
def message_params(bot, request):
    return Message(message_id=TestMessage.id,
                   from_user=TestMessage.from_user,
                   date=TestMessage.date,
                   chat=TestMessage.chat, bot=bot, **request.param)


class TestMessage(object):
    id = 1
    from_user = User(2, 'testuser', False)
    date = datetime.now()
    chat = Chat(3, 'private')
    test_entities = [{'length': 4, 'offset': 10, 'type': 'bold'},
                     {'length': 7, 'offset': 16, 'type': 'italic'},
                     {'length': 4, 'offset': 25, 'type': 'code'},
                     {'length': 5, 'offset': 31, 'type': 'text_link', 'url': 'http://github.com/'},
                     {'length': 12, 'offset': 38, 'type': 'text_mention',
                      'user': User(123456789, 'mentioned user', False)},
                     {'length': 3, 'offset': 55, 'type': 'pre'},
                     {'length': 17, 'offset': 60, 'type': 'url'}]
    test_text = 'Test for <bold, ita_lic, code, links, text-mention and pre. http://google.com'
    test_message = Message(message_id=1,
                           from_user=None,
                           date=None,
                           chat=None,
                           text=test_text,
                           entities=[MessageEntity(**e) for e in test_entities],
                           caption=test_text,
                           caption_entities=[MessageEntity(**e) for e in test_entities])

    def test_all_posibilities_de_json_and_to_dict(self, bot, message_params):
        new = Message.de_json(message_params.to_dict(), bot)

        assert new.to_dict() == message_params.to_dict()

    def test_dict_approach(self, message):
        assert message['date'] == message.date
        assert message['chat_id'] == message.chat_id
        assert message['no_key'] is None

    def test_parse_entity(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
                b'\\u200d\\U0001f467\\U0001f431http://google.com').decode('unicode-escape')
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        message = Message(1, self.from_user, self.date, self.chat, text=text, entities=[entity])
        assert message.parse_entity(entity) == 'http://google.com'

    def test_parse_caption_entity(self):
        caption = (b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
                   b'\\u200d\\U0001f467\\U0001f431http://google.com').decode('unicode-escape')
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        message = Message(1, self.from_user, self.date, self.chat, caption=caption,
                          caption_entities=[entity])
        assert message.parse_caption_entity(entity) == 'http://google.com'

    def test_parse_entities(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
                b'\\u200d\\U0001f467\\U0001f431http://google.com').decode('unicode-escape')
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        entity_2 = MessageEntity(type=MessageEntity.BOLD, offset=13, length=1)
        message = Message(1, self.from_user, self.date, self.chat,
                          text=text, entities=[entity_2, entity])
        assert message.parse_entities(MessageEntity.URL) == {entity: 'http://google.com'}
        assert message.parse_entities() == {entity: 'http://google.com', entity_2: 'h'}

    def test_parse_caption_entities(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
                b'\\u200d\\U0001f467\\U0001f431http://google.com').decode('unicode-escape')
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        entity_2 = MessageEntity(type=MessageEntity.BOLD, offset=13, length=1)
        message = Message(1, self.from_user, self.date, self.chat,
                          caption=text, caption_entities=[entity_2, entity])
        assert message.parse_caption_entities(MessageEntity.URL) == {entity: 'http://google.com'}
        assert message.parse_caption_entities() == {entity: 'http://google.com', entity_2: 'h'}

    def test_text_html_simple(self):
        test_html_string = ('Test for &lt;<b>bold</b>, <i>ita_lic</i>, <code>code</code>, '
                            '<a href="http://github.com/">links</a>, '
                            '<a href="tg://user?id=123456789">text-mention</a> and '
                            '<pre>pre</pre>. http://google.com')
        text_html = self.test_message.text_html
        assert text_html == test_html_string

    def test_text_html_empty(self, message):
        message.text = None
        message.caption = "test"
        assert message.text_html is None

    def test_text_html_urled(self):
        test_html_string = ('Test for &lt;<b>bold</b>, <i>ita_lic</i>, <code>code</code>, '
                            '<a href="http://github.com/">links</a>, '
                            '<a href="tg://user?id=123456789">text-mention</a> and '
                            '<pre>pre</pre>. <a href="http://google.com">http://google.com</a>')
        text_html = self.test_message.text_html_urled
        assert text_html == test_html_string

    def test_text_markdown_simple(self):
        test_md_string = (r'Test for <*bold*, _ita\_lic_, `code`, [links](http://github.com/), '
                          '[text-mention](tg://user?id=123456789) and ```pre```. '
                          'http://google.com')
        text_markdown = self.test_message.text_markdown
        assert text_markdown == test_md_string

    def test_text_markdown_empty(self, message):
        message.text = None
        message.caption = "test"
        assert message.text_markdown is None

    def test_text_markdown_urled(self):
        test_md_string = (r'Test for <*bold*, _ita\_lic_, `code`, [links](http://github.com/), '
                          '[text-mention](tg://user?id=123456789) and ```pre```. '
                          '[http://google.com](http://google.com)')
        text_markdown = self.test_message.text_markdown_urled
        assert text_markdown == test_md_string

    def test_text_html_emoji(self):
        text = b'\\U0001f469\\u200d\\U0001f469\\u200d ABC'.decode('unicode-escape')
        expected = b'\\U0001f469\\u200d\\U0001f469\\u200d <b>ABC</b>'.decode('unicode-escape')
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(1, self.from_user, self.date, self.chat,
                          text=text, entities=[bold_entity])
        assert expected == message.text_html

    def test_text_markdown_emoji(self):
        text = b'\\U0001f469\\u200d\\U0001f469\\u200d ABC'.decode('unicode-escape')
        expected = b'\\U0001f469\\u200d\\U0001f469\\u200d *ABC*'.decode('unicode-escape')
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(1, self.from_user, self.date, self.chat,
                          text=text, entities=[bold_entity])
        assert expected == message.text_markdown

    def test_caption_html_simple(self):
        test_html_string = ('Test for &lt;<b>bold</b>, <i>ita_lic</i>, <code>code</code>, '
                            '<a href="http://github.com/">links</a>, '
                            '<a href="tg://user?id=123456789">text-mention</a> and '
                            '<pre>pre</pre>. http://google.com')
        caption_html = self.test_message.caption_html
        assert caption_html == test_html_string

    def test_caption_html_empty(self, message):
        message.text = "test"
        message.caption = None
        assert message.caption_html is None

    def test_caption_html_urled(self):
        test_html_string = ('Test for &lt;<b>bold</b>, <i>ita_lic</i>, <code>code</code>, '
                            '<a href="http://github.com/">links</a>, '
                            '<a href="tg://user?id=123456789">text-mention</a> and '
                            '<pre>pre</pre>. <a href="http://google.com">http://google.com</a>')
        caption_html = self.test_message.caption_html_urled
        assert caption_html == test_html_string

    def test_caption_markdown_simple(self):
        test_md_string = (r'Test for <*bold*, _ita\_lic_, `code`, [links](http://github.com/), '
                          '[text-mention](tg://user?id=123456789) and ```pre```. '
                          'http://google.com')
        caption_markdown = self.test_message.caption_markdown
        assert caption_markdown == test_md_string

    def test_caption_markdown_empty(self, message):
        message.text = "test"
        message.caption = None
        assert message.caption_markdown is None

    def test_caption_markdown_urled(self):
        test_md_string = (r'Test for <*bold*, _ita\_lic_, `code`, [links](http://github.com/), '
                          '[text-mention](tg://user?id=123456789) and ```pre```. '
                          '[http://google.com](http://google.com)')
        caption_markdown = self.test_message.caption_markdown_urled
        assert caption_markdown == test_md_string

    def test_caption_html_emoji(self):
        caption = b'\\U0001f469\\u200d\\U0001f469\\u200d ABC'.decode('unicode-escape')
        expected = b'\\U0001f469\\u200d\\U0001f469\\u200d <b>ABC</b>'.decode('unicode-escape')
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(1, self.from_user, self.date, self.chat,
                          caption=caption, caption_entities=[bold_entity])
        assert expected == message.caption_html

    def test_caption_markdown_emoji(self):
        caption = b'\\U0001f469\\u200d\\U0001f469\\u200d ABC'.decode('unicode-escape')
        expected = b'\\U0001f469\\u200d\\U0001f469\\u200d *ABC*'.decode('unicode-escape')
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(1, self.from_user, self.date, self.chat,
                          caption=caption, caption_entities=[bold_entity])
        assert expected == message.caption_markdown

    def test_parse_entities_url_emoji(self):
        url = b'http://github.com/?unicode=\\u2713\\U0001f469'.decode('unicode-escape')
        text = 'some url'
        link_entity = MessageEntity(type=MessageEntity.URL, offset=0, length=8, url=url)
        message = Message(1, self.from_user, self.date, self.chat,
                          text=text, entities=[link_entity])
        assert message.parse_entities() == {link_entity: text}
        assert next(iter(message.parse_entities())).url == url

    def test_chat_id(self, message):
        assert message.chat_id == message.chat.id

    def test_link(self, message):
        assert message.link is None
        message.chat.username = 'username'
        message.chat.type = 'supergroup'
        assert message.link == 'https://t.me/{}/{}'.format(message.chat.username,
                                                           message.message_id)
        message.chat.type = 'channel'
        assert message.link == 'https://t.me/{}/{}'.format(message.chat.username,
                                                           message.message_id)
        message.chat.type = 'private'
        assert message.link is None

    def test_effective_attachment(self, message_params):
        for i in ('audio', 'game', 'document', 'animation', 'photo', 'sticker', 'video', 'voice',
                  'video_note', 'contact', 'location', 'venue', 'invoice', 'invoice',
                  'successful_payment'):
            item = getattr(message_params, i, None)
            if item:
                break
        else:
            item = None
        assert message_params.effective_attachment == item

    def test_reply_text(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            text = args[2] == 'test'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and text and reply

        monkeypatch.setattr('telegram.Bot.send_message', test)
        assert message.reply_text('test')
        assert message.reply_text('test', quote=True)
        assert message.reply_text('test', reply_to_message_id=message.message_id, quote=True)

    def test_reply_markdown(self, monkeypatch, message):
        test_md_string = (r'Test for <*bold*, _ita\_lic_, `code`, [links](http://github.com/), '
                          '[text-mention](tg://user?id=123456789) and ```pre```. '
                          'http://google.com')

        def test(*args, **kwargs):
            cid = args[1] == message.chat_id
            markdown_text = args[2] == test_md_string
            markdown_enabled = kwargs['parse_mode'] == ParseMode.MARKDOWN
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return all([cid, markdown_text, reply, markdown_enabled])

        text_markdown = self.test_message.text_markdown
        assert text_markdown == test_md_string

        monkeypatch.setattr('telegram.Bot.send_message', test)
        assert message.reply_markdown(self.test_message.text_markdown)
        assert message.reply_markdown(self.test_message.text_markdown, quote=True)
        assert message.reply_markdown(self.test_message.text_markdown,
                                      reply_to_message_id=message.message_id,
                                      quote=True)

    def test_reply_html(self, monkeypatch, message):
        test_html_string = ('Test for &lt;<b>bold</b>, <i>ita_lic</i>, <code>code</code>, '
                            '<a href="http://github.com/">links</a>, '
                            '<a href="tg://user?id=123456789">text-mention</a> and '
                            '<pre>pre</pre>. http://google.com')

        def test(*args, **kwargs):
            cid = args[1] == message.chat_id
            html_text = args[2] == test_html_string
            html_enabled = kwargs['parse_mode'] == ParseMode.HTML
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return all([cid, html_text, reply, html_enabled])

        text_html = self.test_message.text_html
        assert text_html == test_html_string

        monkeypatch.setattr('telegram.Bot.send_message', test)
        assert message.reply_html(self.test_message.text_html)
        assert message.reply_html(self.test_message.text_html, quote=True)
        assert message.reply_html(self.test_message.text_html,
                                  reply_to_message_id=message.message_id,
                                  quote=True)

    def test_reply_media_group(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            media = kwargs['media'] == 'reply_media_group'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and media and reply

        monkeypatch.setattr('telegram.Bot.send_media_group', test)
        assert message.reply_media_group(media='reply_media_group')
        assert message.reply_media_group(media='reply_media_group', quote=True)

    def test_reply_photo(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            photo = kwargs['photo'] == 'test_photo'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and photo and reply

        monkeypatch.setattr('telegram.Bot.send_photo', test)
        assert message.reply_photo(photo='test_photo')
        assert message.reply_photo(photo='test_photo', quote=True)

    def test_reply_audio(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            audio = kwargs['audio'] == 'test_audio'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and audio and reply

        monkeypatch.setattr('telegram.Bot.send_audio', test)
        assert message.reply_audio(audio='test_audio')
        assert message.reply_audio(audio='test_audio', quote=True)

    def test_reply_document(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            document = kwargs['document'] == 'test_document'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and document and reply

        monkeypatch.setattr('telegram.Bot.send_document', test)
        assert message.reply_document(document='test_document')
        assert message.reply_document(document='test_document', quote=True)

    def test_reply_animation(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            animation = kwargs['animation'] == 'test_animation'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and animation and reply

        monkeypatch.setattr('telegram.Bot.send_animation', test)
        assert message.reply_animation(animation='test_animation')
        assert message.reply_animation(animation='test_animation', quote=True)

    def test_reply_sticker(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            sticker = kwargs['sticker'] == 'test_sticker'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and sticker and reply

        monkeypatch.setattr('telegram.Bot.send_sticker', test)
        assert message.reply_sticker(sticker='test_sticker')
        assert message.reply_sticker(sticker='test_sticker', quote=True)

    def test_reply_video(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            video = kwargs['video'] == 'test_video'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and video and reply

        monkeypatch.setattr('telegram.Bot.send_video', test)
        assert message.reply_video(video='test_video')
        assert message.reply_video(video='test_video', quote=True)

    def test_reply_video_note(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            video_note = kwargs['video_note'] == 'test_video_note'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and video_note and reply

        monkeypatch.setattr('telegram.Bot.send_video_note', test)
        assert message.reply_video_note(video_note='test_video_note')
        assert message.reply_video_note(video_note='test_video_note', quote=True)

    def test_reply_voice(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            voice = kwargs['voice'] == 'test_voice'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and voice and reply

        monkeypatch.setattr('telegram.Bot.send_voice', test)
        assert message.reply_voice(voice='test_voice')
        assert message.reply_voice(voice='test_voice', quote=True)

    def test_reply_location(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            location = kwargs['location'] == 'test_location'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and location and reply

        monkeypatch.setattr('telegram.Bot.send_location', test)
        assert message.reply_location(location='test_location')
        assert message.reply_location(location='test_location', quote=True)

    def test_reply_venue(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            venue = kwargs['venue'] == 'test_venue'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and venue and reply

        monkeypatch.setattr('telegram.Bot.send_venue', test)
        assert message.reply_venue(venue='test_venue')
        assert message.reply_venue(venue='test_venue', quote=True)

    def test_reply_contact(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            contact = kwargs['contact'] == 'test_contact'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and contact and reply

        monkeypatch.setattr('telegram.Bot.send_contact', test)
        assert message.reply_contact(contact='test_contact')
        assert message.reply_contact(contact='test_contact', quote=True)

    def test_forward(self, monkeypatch, message):
        def test(*args, **kwargs):
            chat_id = kwargs['chat_id'] == 123456
            from_chat = kwargs['from_chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            if kwargs.get('disable_notification'):
                notification = kwargs['disable_notification'] is True
            else:
                notification = True
            return chat_id and from_chat and message_id and notification

        monkeypatch.setattr('telegram.Bot.forward_message', test)
        assert message.forward(123456)
        assert message.forward(123456, disable_notification=True)
        assert not message.forward(635241)

    def test_edit_text(self, monkeypatch, message):
        def test(*args, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            text = kwargs['text'] == 'test'
            return chat_id and message_id and text

        monkeypatch.setattr('telegram.Bot.edit_message_text', test)
        assert message.edit_text(text='test')

    def test_edit_caption(self, monkeypatch, message):
        def test(*args, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            caption = kwargs['caption'] == 'new caption'
            return chat_id and message_id and caption

        monkeypatch.setattr('telegram.Bot.edit_message_caption', test)
        assert message.edit_caption(caption='new caption')

    def test_edit_media(self, monkeypatch, message):
        def test(*args, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            media = kwargs['media'] == 'my_media'
            return chat_id and message_id and media

        monkeypatch.setattr('telegram.Bot.edit_message_media', test)
        assert message.edit_media('my_media')

    def test_edit_reply_markup(self, monkeypatch, message):
        def test(*args, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            reply_markup = kwargs['reply_markup'] == [['1', '2']]
            return chat_id and message_id and reply_markup

        monkeypatch.setattr('telegram.Bot.edit_message_reply_markup', test)
        assert message.edit_reply_markup(reply_markup=[['1', '2']])

    def test_delete(self, monkeypatch, message):
        def test(*args, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            return chat_id and message_id

        monkeypatch.setattr('telegram.Bot.delete_message', test)
        assert message.delete()

    def test_equality(self):
        id = 1
        a = Message(id, self.from_user, self.date, self.chat)
        b = Message(id, self.from_user, self.date, self.chat)
        c = Message(id, User(0, '', False), self.date, self.chat)
        d = Message(0, self.from_user, self.date, self.chat)
        e = Update(id)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
