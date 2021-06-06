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
from datetime import datetime

import pytest

from telegram import (
    Update,
    Message,
    User,
    MessageEntity,
    Chat,
    Audio,
    Document,
    Animation,
    Game,
    PhotoSize,
    Sticker,
    Video,
    Voice,
    VideoNote,
    Contact,
    Location,
    Venue,
    Invoice,
    SuccessfulPayment,
    PassportData,
    ParseMode,
    Poll,
    PollOption,
    ProximityAlertTriggered,
    Dice,
    Bot,
    ChatAction,
    VoiceChatStarted,
    VoiceChatEnded,
    VoiceChatParticipantsInvited,
    MessageAutoDeleteTimerChanged,
    VoiceChatScheduled,
)
from telegram.ext import Defaults
from tests.conftest import check_shortcut_signature, check_shortcut_call, check_defaults_handling
from tests.test_passport import RAW_PASSPORT_DATA


@pytest.fixture(scope='class')
def message(bot):
    return Message(
        TestMessage.id_,
        TestMessage.date,
        TestMessage.chat,
        from_user=TestMessage.from_user,
        bot=bot,
    )


@pytest.fixture(
    scope='function',
    params=[
        {'forward_from': User(99, 'forward_user', False), 'forward_date': datetime.utcnow()},
        {
            'forward_from_chat': Chat(-23, 'channel'),
            'forward_from_message_id': 101,
            'forward_date': datetime.utcnow(),
        },
        {'reply_to_message': Message(50, None, None, None)},
        {'edit_date': datetime.utcnow()},
        {
            'text': 'a text message',
            'enitites': [MessageEntity('bold', 10, 4), MessageEntity('italic', 16, 7)],
        },
        {
            'caption': 'A message caption',
            'caption_entities': [MessageEntity('bold', 1, 1), MessageEntity('text_link', 4, 3)],
        },
        {'audio': Audio('audio_id', 'unique_id', 12), 'caption': 'audio_file'},
        {'document': Document('document_id', 'unique_id'), 'caption': 'document_file'},
        {
            'animation': Animation('animation_id', 'unique_id', 30, 30, 1),
            'caption': 'animation_file',
        },
        {
            'game': Game(
                'my_game',
                'just my game',
                [
                    PhotoSize('game_photo_id', 'unique_id', 30, 30),
                ],
            )
        },
        {'photo': [PhotoSize('photo_id', 'unique_id', 50, 50)], 'caption': 'photo_file'},
        {'sticker': Sticker('sticker_id', 'unique_id', 50, 50, True)},
        {'video': Video('video_id', 'unique_id', 12, 12, 12), 'caption': 'video_file'},
        {'voice': Voice('voice_id', 'unique_id', 5)},
        {'video_note': VideoNote('video_note_id', 'unique_id', 20, 12)},
        {'new_chat_members': [User(55, 'new_user', False)]},
        {'contact': Contact('phone_numner', 'contact_name')},
        {'location': Location(-23.691288, 46.788279)},
        {'venue': Venue(Location(-23.691288, 46.788279), 'some place', 'right here')},
        {'left_chat_member': User(33, 'kicked', False)},
        {'new_chat_title': 'new title'},
        {'new_chat_photo': [PhotoSize('photo_id', 'unique_id', 50, 50)]},
        {'delete_chat_photo': True},
        {'group_chat_created': True},
        {'supergroup_chat_created': True},
        {'channel_chat_created': True},
        {'message_auto_delete_timer_changed': MessageAutoDeleteTimerChanged(42)},
        {'migrate_to_chat_id': -12345},
        {'migrate_from_chat_id': -54321},
        {'pinned_message': Message(7, None, None, None)},
        {'invoice': Invoice('my invoice', 'invoice', 'start', 'EUR', 243)},
        {
            'successful_payment': SuccessfulPayment(
                'EUR', 243, 'payload', 'charge_id', 'provider_id', order_info={}
            )
        },
        {'connected_website': 'http://example.com/'},
        {'forward_signature': 'some_forward_sign'},
        {'author_signature': 'some_author_sign'},
        {
            'photo': [PhotoSize('photo_id', 'unique_id', 50, 50)],
            'caption': 'photo_file',
            'media_group_id': 1234443322222,
        },
        {'passport_data': PassportData.de_json(RAW_PASSPORT_DATA, None)},
        {
            'poll': Poll(
                id='abc',
                question='What is this?',
                options=[PollOption(text='a', voter_count=1), PollOption(text='b', voter_count=2)],
                is_closed=False,
                total_voter_count=0,
                is_anonymous=False,
                type=Poll.REGULAR,
                allows_multiple_answers=True,
                explanation_entities=[],
            )
        },
        {
            'text': 'a text message',
            'reply_markup': {
                'inline_keyboard': [
                    [
                        {'text': 'start', 'url': 'http://google.com'},
                        {'text': 'next', 'callback_data': 'abcd'},
                    ],
                    [{'text': 'Cancel', 'callback_data': 'Cancel'}],
                ]
            },
        },
        {'dice': Dice(4, '🎲')},
        {'via_bot': User(9, 'A_Bot', True)},
        {
            'proximity_alert_triggered': ProximityAlertTriggered(
                User(1, 'John', False), User(2, 'Doe', False), 42
            )
        },
        {'voice_chat_scheduled': VoiceChatScheduled(datetime.utcnow())},
        {'voice_chat_started': VoiceChatStarted()},
        {'voice_chat_ended': VoiceChatEnded(100)},
        {
            'voice_chat_participants_invited': VoiceChatParticipantsInvited(
                [User(1, 'Rem', False), User(2, 'Emilia', False)]
            )
        },
        {'sender_chat': Chat(-123, 'discussion_channel')},
    ],
    ids=[
        'forwarded_user',
        'forwarded_channel',
        'reply',
        'edited',
        'text',
        'caption_entities',
        'audio',
        'document',
        'animation',
        'game',
        'photo',
        'sticker',
        'video',
        'voice',
        'video_note',
        'new_members',
        'contact',
        'location',
        'venue',
        'left_member',
        'new_title',
        'new_photo',
        'delete_photo',
        'group_created',
        'supergroup_created',
        'channel_created',
        'message_auto_delete_timer_changed',
        'migrated_to',
        'migrated_from',
        'pinned',
        'invoice',
        'successful_payment',
        'connected_website',
        'forward_signature',
        'author_signature',
        'photo_from_media_group',
        'passport_data',
        'poll',
        'reply_markup',
        'dice',
        'via_bot',
        'proximity_alert_triggered',
        'voice_chat_scheduled',
        'voice_chat_started',
        'voice_chat_ended',
        'voice_chat_participants_invited',
        'sender_chat',
    ],
)
def message_params(bot, request):
    return Message(
        message_id=TestMessage.id_,
        from_user=TestMessage.from_user,
        date=TestMessage.date,
        chat=TestMessage.chat,
        bot=bot,
        **request.param,
    )


class TestMessage:
    id_ = 1
    from_user = User(2, 'testuser', False)
    date = datetime.utcnow()
    chat = Chat(3, 'private')
    test_entities = [
        {'length': 4, 'offset': 10, 'type': 'bold'},
        {'length': 3, 'offset': 16, 'type': 'italic'},
        {'length': 3, 'offset': 20, 'type': 'italic'},
        {'length': 4, 'offset': 25, 'type': 'code'},
        {'length': 5, 'offset': 31, 'type': 'text_link', 'url': 'http://github.com/ab_'},
        {
            'length': 12,
            'offset': 38,
            'type': 'text_mention',
            'user': User(123456789, 'mentioned user', False),
        },
        {'length': 3, 'offset': 55, 'type': 'pre', 'language': 'python'},
        {'length': 21, 'offset': 60, 'type': 'url'},
    ]
    test_text = 'Test for <bold, ita_lic, code, links, text-mention and pre. http://google.com/ab_'
    test_entities_v2 = [
        {'length': 4, 'offset': 0, 'type': 'underline'},
        {'length': 4, 'offset': 10, 'type': 'bold'},
        {'length': 7, 'offset': 16, 'type': 'italic'},
        {'length': 6, 'offset': 25, 'type': 'code'},
        {'length': 5, 'offset': 33, 'type': 'text_link', 'url': r'http://github.com/abc\)def'},
        {
            'length': 12,
            'offset': 40,
            'type': 'text_mention',
            'user': User(123456789, 'mentioned user', False),
        },
        {'length': 5, 'offset': 57, 'type': 'pre'},
        {'length': 17, 'offset': 64, 'type': 'url'},
        {'length': 41, 'offset': 86, 'type': 'italic'},
        {'length': 29, 'offset': 91, 'type': 'bold'},
        {'length': 9, 'offset': 101, 'type': 'strikethrough'},
        {'length': 10, 'offset': 129, 'type': 'pre', 'language': 'python'},
    ]
    test_text_v2 = (
        r'Test for <bold, ita_lic, \`code, links, text-mention and `\pre. '
        'http://google.com and bold nested in strk>trgh nested in italic. Python pre.'
    )
    test_message = Message(
        message_id=1,
        from_user=None,
        date=None,
        chat=None,
        text=test_text,
        entities=[MessageEntity(**e) for e in test_entities],
        caption=test_text,
        caption_entities=[MessageEntity(**e) for e in test_entities],
    )
    test_message_v2 = Message(
        message_id=1,
        from_user=None,
        date=None,
        chat=None,
        text=test_text_v2,
        entities=[MessageEntity(**e) for e in test_entities_v2],
        caption=test_text_v2,
        caption_entities=[MessageEntity(**e) for e in test_entities_v2],
    )

    def test_slot_behaviour(self, message, recwarn, mro_slots):
        for attr in message.__slots__:
            assert getattr(message, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert not message.__dict__, f"got missing slot(s): {message.__dict__}"
        assert len(mro_slots(message)) == len(set(mro_slots(message))), "duplicate slot"
        message.custom, message.message_id = 'should give warning', self.id_
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

    def test_all_possibilities_de_json_and_to_dict(self, bot, message_params):
        new = Message.de_json(message_params.to_dict(), bot)

        assert new.to_dict() == message_params.to_dict()

    def test_dict_approach(self, message):
        assert message['text'] == message.text
        assert message['chat_id'] == message.chat_id
        assert message['no_key'] is None

    def test_parse_entity(self):
        text = (
            b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
            b'\\u200d\\U0001f467\\U0001f431http://google.com'
        ).decode('unicode-escape')
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        message = Message(1, self.from_user, self.date, self.chat, text=text, entities=[entity])
        assert message.parse_entity(entity) == 'http://google.com'

    def test_parse_caption_entity(self):
        caption = (
            b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
            b'\\u200d\\U0001f467\\U0001f431http://google.com'
        ).decode('unicode-escape')
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        message = Message(
            1, self.from_user, self.date, self.chat, caption=caption, caption_entities=[entity]
        )
        assert message.parse_caption_entity(entity) == 'http://google.com'

    def test_parse_entities(self):
        text = (
            b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
            b'\\u200d\\U0001f467\\U0001f431http://google.com'
        ).decode('unicode-escape')
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        entity_2 = MessageEntity(type=MessageEntity.BOLD, offset=13, length=1)
        message = Message(
            1, self.from_user, self.date, self.chat, text=text, entities=[entity_2, entity]
        )
        assert message.parse_entities(MessageEntity.URL) == {entity: 'http://google.com'}
        assert message.parse_entities() == {entity: 'http://google.com', entity_2: 'h'}

    def test_parse_caption_entities(self):
        text = (
            b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
            b'\\u200d\\U0001f467\\U0001f431http://google.com'
        ).decode('unicode-escape')
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        entity_2 = MessageEntity(type=MessageEntity.BOLD, offset=13, length=1)
        message = Message(
            1,
            self.from_user,
            self.date,
            self.chat,
            caption=text,
            caption_entities=[entity_2, entity],
        )
        assert message.parse_caption_entities(MessageEntity.URL) == {entity: 'http://google.com'}
        assert message.parse_caption_entities() == {entity: 'http://google.com', entity_2: 'h'}

    def test_text_html_simple(self):
        test_html_string = (
            '<u>Test</u> for &lt;<b>bold</b>, <i>ita_lic</i>, '
            r'<code>\`code</code>, '
            r'<a href="http://github.com/abc\)def">links</a>, '
            '<a href="tg://user?id=123456789">text-mention</a> and '
            r'<pre>`\pre</pre>. http://google.com '
            'and <i>bold <b>nested in <s>strk&gt;trgh</s> nested in</b> italic</i>. '
            '<pre><code class="python">Python pre</code></pre>.'
        )
        text_html = self.test_message_v2.text_html
        assert text_html == test_html_string

    def test_text_html_empty(self, message):
        message.text = None
        message.caption = "test"
        assert message.text_html is None

    def test_text_html_urled(self):
        test_html_string = (
            '<u>Test</u> for &lt;<b>bold</b>, <i>ita_lic</i>, '
            r'<code>\`code</code>, '
            r'<a href="http://github.com/abc\)def">links</a>, '
            '<a href="tg://user?id=123456789">text-mention</a> and '
            r'<pre>`\pre</pre>. <a href="http://google.com">http://google.com</a> '
            'and <i>bold <b>nested in <s>strk&gt;trgh</s> nested in</b> italic</i>. '
            '<pre><code class="python">Python pre</code></pre>.'
        )
        text_html = self.test_message_v2.text_html_urled
        assert text_html == test_html_string

    def test_text_markdown_simple(self):
        test_md_string = (
            r'Test for <*bold*, _ita_\__lic_, `code`, '
            '[links](http://github.com/ab_), '
            '[text-mention](tg://user?id=123456789) and ```python\npre```. '
            r'http://google.com/ab\_'
        )
        text_markdown = self.test_message.text_markdown
        assert text_markdown == test_md_string

    def test_text_markdown_v2_simple(self):
        test_md_string = (
            r'__Test__ for <*bold*, _ita\_lic_, `\\\`code`, '
            '[links](http://github.com/abc\\\\\\)def), '
            '[text\\-mention](tg://user?id=123456789) and ```\\`\\\\pre```\\. '
            r'http://google\.com and _bold *nested in ~strk\>trgh~ nested in* italic_\. '
            '```python\nPython pre```\\.'
        )
        text_markdown = self.test_message_v2.text_markdown_v2
        assert text_markdown == test_md_string

    def test_text_markdown_new_in_v2(self, message):
        message.text = 'test'
        message.entities = [
            MessageEntity(MessageEntity.BOLD, offset=0, length=4),
            MessageEntity(MessageEntity.ITALIC, offset=0, length=4),
        ]
        with pytest.raises(ValueError):
            assert message.text_markdown

        message.entities = [MessageEntity(MessageEntity.UNDERLINE, offset=0, length=4)]
        with pytest.raises(ValueError):
            message.text_markdown

        message.entities = [MessageEntity(MessageEntity.STRIKETHROUGH, offset=0, length=4)]
        with pytest.raises(ValueError):
            message.text_markdown

        message.entities = []

    def test_text_markdown_empty(self, message):
        message.text = None
        message.caption = "test"
        assert message.text_markdown is None
        assert message.text_markdown_v2 is None

    def test_text_markdown_urled(self):
        test_md_string = (
            r'Test for <*bold*, _ita_\__lic_, `code`, '
            '[links](http://github.com/ab_), '
            '[text-mention](tg://user?id=123456789) and ```python\npre```. '
            '[http://google.com/ab_](http://google.com/ab_)'
        )
        text_markdown = self.test_message.text_markdown_urled
        assert text_markdown == test_md_string

    def test_text_markdown_v2_urled(self):
        test_md_string = (
            r'__Test__ for <*bold*, _ita\_lic_, `\\\`code`, '
            '[links](http://github.com/abc\\\\\\)def), '
            '[text\\-mention](tg://user?id=123456789) and ```\\`\\\\pre```\\. '
            r'[http://google\.com](http://google.com) and _bold *nested in ~strk\>trgh~ '
            'nested in* italic_\\. ```python\nPython pre```\\.'
        )
        text_markdown = self.test_message_v2.text_markdown_v2_urled
        assert text_markdown == test_md_string

    def test_text_html_emoji(self):
        text = b'\\U0001f469\\u200d\\U0001f469\\u200d ABC'.decode('unicode-escape')
        expected = b'\\U0001f469\\u200d\\U0001f469\\u200d <b>ABC</b>'.decode('unicode-escape')
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(
            1, self.from_user, self.date, self.chat, text=text, entities=[bold_entity]
        )
        assert expected == message.text_html

    def test_text_markdown_emoji(self):
        text = b'\\U0001f469\\u200d\\U0001f469\\u200d ABC'.decode('unicode-escape')
        expected = b'\\U0001f469\\u200d\\U0001f469\\u200d *ABC*'.decode('unicode-escape')
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(
            1, self.from_user, self.date, self.chat, text=text, entities=[bold_entity]
        )
        assert expected == message.text_markdown

    def test_caption_html_simple(self):
        test_html_string = (
            '<u>Test</u> for &lt;<b>bold</b>, <i>ita_lic</i>, '
            r'<code>\`code</code>, '
            r'<a href="http://github.com/abc\)def">links</a>, '
            '<a href="tg://user?id=123456789">text-mention</a> and '
            r'<pre>`\pre</pre>. http://google.com '
            'and <i>bold <b>nested in <s>strk&gt;trgh</s> nested in</b> italic</i>. '
            '<pre><code class="python">Python pre</code></pre>.'
        )
        caption_html = self.test_message_v2.caption_html
        assert caption_html == test_html_string

    def test_caption_html_empty(self, message):
        message.text = "test"
        message.caption = None
        assert message.caption_html is None

    def test_caption_html_urled(self):
        test_html_string = (
            '<u>Test</u> for &lt;<b>bold</b>, <i>ita_lic</i>, '
            r'<code>\`code</code>, '
            r'<a href="http://github.com/abc\)def">links</a>, '
            '<a href="tg://user?id=123456789">text-mention</a> and '
            r'<pre>`\pre</pre>. <a href="http://google.com">http://google.com</a> '
            'and <i>bold <b>nested in <s>strk&gt;trgh</s> nested in</b> italic</i>. '
            '<pre><code class="python">Python pre</code></pre>.'
        )
        caption_html = self.test_message_v2.caption_html_urled
        assert caption_html == test_html_string

    def test_caption_markdown_simple(self):
        test_md_string = (
            r'Test for <*bold*, _ita_\__lic_, `code`, '
            '[links](http://github.com/ab_), '
            '[text-mention](tg://user?id=123456789) and ```python\npre```. '
            r'http://google.com/ab\_'
        )
        caption_markdown = self.test_message.caption_markdown
        assert caption_markdown == test_md_string

    def test_caption_markdown_v2_simple(self):
        test_md_string = (
            r'__Test__ for <*bold*, _ita\_lic_, `\\\`code`, '
            '[links](http://github.com/abc\\\\\\)def), '
            '[text\\-mention](tg://user?id=123456789) and ```\\`\\\\pre```\\. '
            r'http://google\.com and _bold *nested in ~strk\>trgh~ nested in* italic_\. '
            '```python\nPython pre```\\.'
        )
        caption_markdown = self.test_message_v2.caption_markdown_v2
        assert caption_markdown == test_md_string

    def test_caption_markdown_empty(self, message):
        message.text = "test"
        message.caption = None
        assert message.caption_markdown is None
        assert message.caption_markdown_v2 is None

    def test_caption_markdown_urled(self):
        test_md_string = (
            r'Test for <*bold*, _ita_\__lic_, `code`, '
            '[links](http://github.com/ab_), '
            '[text-mention](tg://user?id=123456789) and ```python\npre```. '
            '[http://google.com/ab_](http://google.com/ab_)'
        )
        caption_markdown = self.test_message.caption_markdown_urled
        assert caption_markdown == test_md_string

    def test_caption_markdown_v2_urled(self):
        test_md_string = (
            r'__Test__ for <*bold*, _ita\_lic_, `\\\`code`, '
            '[links](http://github.com/abc\\\\\\)def), '
            '[text\\-mention](tg://user?id=123456789) and ```\\`\\\\pre```\\. '
            r'[http://google\.com](http://google.com) and _bold *nested in ~strk\>trgh~ '
            'nested in* italic_\\. ```python\nPython pre```\\.'
        )
        caption_markdown = self.test_message_v2.caption_markdown_v2_urled
        assert caption_markdown == test_md_string

    def test_caption_html_emoji(self):
        caption = b'\\U0001f469\\u200d\\U0001f469\\u200d ABC'.decode('unicode-escape')
        expected = b'\\U0001f469\\u200d\\U0001f469\\u200d <b>ABC</b>'.decode('unicode-escape')
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(
            1,
            self.from_user,
            self.date,
            self.chat,
            caption=caption,
            caption_entities=[bold_entity],
        )
        assert expected == message.caption_html

    def test_caption_markdown_emoji(self):
        caption = b'\\U0001f469\\u200d\\U0001f469\\u200d ABC'.decode('unicode-escape')
        expected = b'\\U0001f469\\u200d\\U0001f469\\u200d *ABC*'.decode('unicode-escape')
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(
            1,
            self.from_user,
            self.date,
            self.chat,
            caption=caption,
            caption_entities=[bold_entity],
        )
        assert expected == message.caption_markdown

    def test_parse_entities_url_emoji(self):
        url = b'http://github.com/?unicode=\\u2713\\U0001f469'.decode('unicode-escape')
        text = 'some url'
        link_entity = MessageEntity(type=MessageEntity.URL, offset=0, length=8, url=url)
        message = Message(
            1, self.from_user, self.date, self.chat, text=text, entities=[link_entity]
        )
        assert message.parse_entities() == {link_entity: text}
        assert next(iter(message.parse_entities())).url == url

    def test_chat_id(self, message):
        assert message.chat_id == message.chat.id

    @pytest.mark.parametrize('_type', argvalues=[Chat.SUPERGROUP, Chat.CHANNEL])
    def test_link_with_username(self, message, _type):
        message.chat.username = 'username'
        message.chat.type = _type
        assert message.link == f'https://t.me/{message.chat.username}/{message.message_id}'

    @pytest.mark.parametrize(
        '_type, _id', argvalues=[(Chat.CHANNEL, -1003), (Chat.SUPERGROUP, -1003)]
    )
    def test_link_with_id(self, message, _type, _id):
        message.chat.username = None
        message.chat.id = _id
        message.chat.type = _type
        # The leading - for group ids/ -100 for supergroup ids isn't supposed to be in the link
        assert message.link == f'https://t.me/c/{3}/{message.message_id}'

    @pytest.mark.parametrize('_id, username', argvalues=[(None, 'username'), (-3, None)])
    def test_link_private_chats(self, message, _id, username):
        message.chat.type = Chat.PRIVATE
        message.chat.id = _id
        message.chat.username = username
        assert message.link is None
        message.chat.type = Chat.GROUP
        assert message.link is None

    def test_effective_attachment(self, message_params):
        for i in (
            'audio',
            'game',
            'document',
            'animation',
            'photo',
            'sticker',
            'video',
            'voice',
            'video_note',
            'contact',
            'location',
            'venue',
            'invoice',
            'successful_payment',
        ):
            item = getattr(message_params, i, None)
            if item:
                break
        else:
            item = None
        assert message_params.effective_attachment == item

    def test_reply_text(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            text = kwargs['text'] == 'test'
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id_ and text and reply

        assert check_shortcut_signature(
            Message.reply_text, Bot.send_message, ['chat_id'], ['quote']
        )
        assert check_shortcut_call(message.reply_text, message.bot, 'send_message')
        assert check_defaults_handling(message.reply_text, message.bot)

        monkeypatch.setattr(message.bot, 'send_message', make_assertion)
        assert message.reply_text('test')
        assert message.reply_text('test', quote=True)
        assert message.reply_text('test', reply_to_message_id=message.message_id, quote=True)

    def test_reply_markdown(self, monkeypatch, message):
        test_md_string = (
            r'Test for <*bold*, _ita_\__lic_, `code`, '
            '[links](http://github.com/ab_), '
            '[text-mention](tg://user?id=123456789) and ```python\npre```. '
            r'http://google.com/ab\_'
        )

        def make_assertion(*_, **kwargs):
            cid = kwargs['chat_id'] == message.chat_id
            markdown_text = kwargs['text'] == test_md_string
            markdown_enabled = kwargs['parse_mode'] == ParseMode.MARKDOWN
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return all([cid, markdown_text, reply, markdown_enabled])

        assert check_shortcut_signature(
            Message.reply_markdown, Bot.send_message, ['chat_id', 'parse_mode'], ['quote']
        )
        assert check_shortcut_call(message.reply_text, message.bot, 'send_message')
        assert check_defaults_handling(message.reply_text, message.bot)

        text_markdown = self.test_message.text_markdown
        assert text_markdown == test_md_string

        monkeypatch.setattr(message.bot, 'send_message', make_assertion)
        assert message.reply_markdown(self.test_message.text_markdown)
        assert message.reply_markdown(self.test_message.text_markdown, quote=True)
        assert message.reply_markdown(
            self.test_message.text_markdown, reply_to_message_id=message.message_id, quote=True
        )

    def test_reply_markdown_v2(self, monkeypatch, message):
        test_md_string = (
            r'__Test__ for <*bold*, _ita\_lic_, `\\\`code`, '
            '[links](http://github.com/abc\\\\\\)def), '
            '[text\\-mention](tg://user?id=123456789) and ```\\`\\\\pre```\\. '
            r'http://google\.com and _bold *nested in ~strk\>trgh~ nested in* italic_\. '
            '```python\nPython pre```\\.'
        )

        def make_assertion(*_, **kwargs):
            cid = kwargs['chat_id'] == message.chat_id
            markdown_text = kwargs['text'] == test_md_string
            markdown_enabled = kwargs['parse_mode'] == ParseMode.MARKDOWN_V2
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return all([cid, markdown_text, reply, markdown_enabled])

        assert check_shortcut_signature(
            Message.reply_markdown_v2, Bot.send_message, ['chat_id', 'parse_mode'], ['quote']
        )
        assert check_shortcut_call(message.reply_text, message.bot, 'send_message')
        assert check_defaults_handling(message.reply_text, message.bot)

        text_markdown = self.test_message_v2.text_markdown_v2
        assert text_markdown == test_md_string

        monkeypatch.setattr(message.bot, 'send_message', make_assertion)
        assert message.reply_markdown_v2(self.test_message_v2.text_markdown_v2)
        assert message.reply_markdown_v2(self.test_message_v2.text_markdown_v2, quote=True)
        assert message.reply_markdown_v2(
            self.test_message_v2.text_markdown_v2,
            reply_to_message_id=message.message_id,
            quote=True,
        )

    def test_reply_html(self, monkeypatch, message):
        test_html_string = (
            '<u>Test</u> for &lt;<b>bold</b>, <i>ita_lic</i>, '
            r'<code>\`code</code>, '
            r'<a href="http://github.com/abc\)def">links</a>, '
            '<a href="tg://user?id=123456789">text-mention</a> and '
            r'<pre>`\pre</pre>. http://google.com '
            'and <i>bold <b>nested in <s>strk&gt;trgh</s> nested in</b> italic</i>. '
            '<pre><code class="python">Python pre</code></pre>.'
        )

        def make_assertion(*_, **kwargs):
            cid = kwargs['chat_id'] == message.chat_id
            html_text = kwargs['text'] == test_html_string
            html_enabled = kwargs['parse_mode'] == ParseMode.HTML
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return all([cid, html_text, reply, html_enabled])

        assert check_shortcut_signature(
            Message.reply_html, Bot.send_message, ['chat_id', 'parse_mode'], ['quote']
        )
        assert check_shortcut_call(message.reply_text, message.bot, 'send_message')
        assert check_defaults_handling(message.reply_text, message.bot)

        text_html = self.test_message_v2.text_html
        assert text_html == test_html_string

        monkeypatch.setattr(message.bot, 'send_message', make_assertion)
        assert message.reply_html(self.test_message_v2.text_html)
        assert message.reply_html(self.test_message_v2.text_html, quote=True)
        assert message.reply_html(
            self.test_message_v2.text_html, reply_to_message_id=message.message_id, quote=True
        )

    def test_reply_media_group(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            media = kwargs['media'] == 'reply_media_group'
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id_ and media and reply

        assert check_shortcut_signature(
            Message.reply_media_group, Bot.send_media_group, ['chat_id'], ['quote']
        )
        assert check_shortcut_call(message.reply_media_group, message.bot, 'send_media_group')
        assert check_defaults_handling(message.reply_media_group, message.bot)

        monkeypatch.setattr(message.bot, 'send_media_group', make_assertion)
        assert message.reply_media_group(media='reply_media_group')
        assert message.reply_media_group(media='reply_media_group', quote=True)

    def test_reply_photo(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            photo = kwargs['photo'] == 'test_photo'
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id_ and photo and reply

        assert check_shortcut_signature(
            Message.reply_photo, Bot.send_photo, ['chat_id'], ['quote']
        )
        assert check_shortcut_call(message.reply_photo, message.bot, 'send_photo')
        assert check_defaults_handling(message.reply_photo, message.bot)

        monkeypatch.setattr(message.bot, 'send_photo', make_assertion)
        assert message.reply_photo(photo='test_photo')
        assert message.reply_photo(photo='test_photo', quote=True)

    def test_reply_audio(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            audio = kwargs['audio'] == 'test_audio'
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id_ and audio and reply

        assert check_shortcut_signature(
            Message.reply_audio, Bot.send_audio, ['chat_id'], ['quote']
        )
        assert check_shortcut_call(message.reply_audio, message.bot, 'send_audio')
        assert check_defaults_handling(message.reply_audio, message.bot)

        monkeypatch.setattr(message.bot, 'send_audio', make_assertion)
        assert message.reply_audio(audio='test_audio')
        assert message.reply_audio(audio='test_audio', quote=True)

    def test_reply_document(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            document = kwargs['document'] == 'test_document'
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id_ and document and reply

        assert check_shortcut_signature(
            Message.reply_document, Bot.send_document, ['chat_id'], ['quote']
        )
        assert check_shortcut_call(message.reply_document, message.bot, 'send_document')
        assert check_defaults_handling(message.reply_document, message.bot)

        monkeypatch.setattr(message.bot, 'send_document', make_assertion)
        assert message.reply_document(document='test_document')
        assert message.reply_document(document='test_document', quote=True)

    def test_reply_animation(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            animation = kwargs['animation'] == 'test_animation'
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id_ and animation and reply

        assert check_shortcut_signature(
            Message.reply_animation, Bot.send_animation, ['chat_id'], ['quote']
        )
        assert check_shortcut_call(message.reply_animation, message.bot, 'send_animation')
        assert check_defaults_handling(message.reply_animation, message.bot)

        monkeypatch.setattr(message.bot, 'send_animation', make_assertion)
        assert message.reply_animation(animation='test_animation')
        assert message.reply_animation(animation='test_animation', quote=True)

    def test_reply_sticker(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            sticker = kwargs['sticker'] == 'test_sticker'
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id_ and sticker and reply

        assert check_shortcut_signature(
            Message.reply_sticker, Bot.send_sticker, ['chat_id'], ['quote']
        )
        assert check_shortcut_call(message.reply_sticker, message.bot, 'send_sticker')
        assert check_defaults_handling(message.reply_sticker, message.bot)

        monkeypatch.setattr(message.bot, 'send_sticker', make_assertion)
        assert message.reply_sticker(sticker='test_sticker')
        assert message.reply_sticker(sticker='test_sticker', quote=True)

    def test_reply_video(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            video = kwargs['video'] == 'test_video'
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id_ and video and reply

        assert check_shortcut_signature(
            Message.reply_video, Bot.send_video, ['chat_id'], ['quote']
        )
        assert check_shortcut_call(message.reply_video, message.bot, 'send_video')
        assert check_defaults_handling(message.reply_video, message.bot)

        monkeypatch.setattr(message.bot, 'send_video', make_assertion)
        assert message.reply_video(video='test_video')
        assert message.reply_video(video='test_video', quote=True)

    def test_reply_video_note(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            video_note = kwargs['video_note'] == 'test_video_note'
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id_ and video_note and reply

        assert check_shortcut_signature(
            Message.reply_video_note, Bot.send_video_note, ['chat_id'], ['quote']
        )
        assert check_shortcut_call(message.reply_video_note, message.bot, 'send_video_note')
        assert check_defaults_handling(message.reply_video_note, message.bot)

        monkeypatch.setattr(message.bot, 'send_video_note', make_assertion)
        assert message.reply_video_note(video_note='test_video_note')
        assert message.reply_video_note(video_note='test_video_note', quote=True)

    def test_reply_voice(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            voice = kwargs['voice'] == 'test_voice'
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id_ and voice and reply

        assert check_shortcut_signature(
            Message.reply_voice, Bot.send_voice, ['chat_id'], ['quote']
        )
        assert check_shortcut_call(message.reply_voice, message.bot, 'send_voice')
        assert check_defaults_handling(message.reply_voice, message.bot)

        monkeypatch.setattr(message.bot, 'send_voice', make_assertion)
        assert message.reply_voice(voice='test_voice')
        assert message.reply_voice(voice='test_voice', quote=True)

    def test_reply_location(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            location = kwargs['location'] == 'test_location'
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id_ and location and reply

        assert check_shortcut_signature(
            Message.reply_location, Bot.send_location, ['chat_id'], ['quote']
        )
        assert check_shortcut_call(message.reply_location, message.bot, 'send_location')
        assert check_defaults_handling(message.reply_location, message.bot)

        monkeypatch.setattr(message.bot, 'send_location', make_assertion)
        assert message.reply_location(location='test_location')
        assert message.reply_location(location='test_location', quote=True)

    def test_reply_venue(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            venue = kwargs['venue'] == 'test_venue'
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id_ and venue and reply

        assert check_shortcut_signature(
            Message.reply_venue, Bot.send_venue, ['chat_id'], ['quote']
        )
        assert check_shortcut_call(message.reply_venue, message.bot, 'send_venue')
        assert check_defaults_handling(message.reply_venue, message.bot)

        monkeypatch.setattr(message.bot, 'send_venue', make_assertion)
        assert message.reply_venue(venue='test_venue')
        assert message.reply_venue(venue='test_venue', quote=True)

    def test_reply_contact(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            contact = kwargs['contact'] == 'test_contact'
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id_ and contact and reply

        assert check_shortcut_signature(
            Message.reply_contact, Bot.send_contact, ['chat_id'], ['quote']
        )
        assert check_shortcut_call(message.reply_contact, message.bot, 'send_contact')
        assert check_defaults_handling(message.reply_contact, message.bot)

        monkeypatch.setattr(message.bot, 'send_contact', make_assertion)
        assert message.reply_contact(contact='test_contact')
        assert message.reply_contact(contact='test_contact', quote=True)

    def test_reply_poll(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            question = kwargs['question'] == 'test_poll'
            options = kwargs['options'] == ['1', '2', '3']
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id_ and question and options and reply

        assert check_shortcut_signature(Message.reply_poll, Bot.send_poll, ['chat_id'], ['quote'])
        assert check_shortcut_call(message.reply_poll, message.bot, 'send_poll')
        assert check_defaults_handling(message.reply_poll, message.bot)

        monkeypatch.setattr(message.bot, 'send_poll', make_assertion)
        assert message.reply_poll(question='test_poll', options=['1', '2', '3'])
        assert message.reply_poll(question='test_poll', quote=True, options=['1', '2', '3'])

    def test_reply_dice(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            contact = kwargs['disable_notification'] is True
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id_ and contact and reply

        assert check_shortcut_signature(Message.reply_dice, Bot.send_dice, ['chat_id'], ['quote'])
        assert check_shortcut_call(message.reply_dice, message.bot, 'send_dice')
        assert check_defaults_handling(message.reply_dice, message.bot)

        monkeypatch.setattr(message.bot, 'send_dice', make_assertion)
        assert message.reply_dice(disable_notification=True)
        assert message.reply_dice(disable_notification=True, quote=True)

    def test_reply_action(self, monkeypatch, message: Message):
        def make_assertion(*_, **kwargs):
            id_ = kwargs['chat_id'] == message.chat_id
            action = kwargs['action'] == ChatAction.TYPING
            return id_ and action

        assert check_shortcut_signature(
            Message.reply_chat_action, Bot.send_chat_action, ['chat_id'], []
        )
        assert check_shortcut_call(message.reply_chat_action, message.bot, 'send_chat_action')
        assert check_defaults_handling(message.reply_chat_action, message.bot)

        monkeypatch.setattr(message.bot, 'send_chat_action', make_assertion)
        assert message.reply_chat_action(action=ChatAction.TYPING)

    def test_reply_game(self, monkeypatch, message: Message):
        def make_assertion(*_, **kwargs):
            return (
                kwargs['chat_id'] == message.chat_id and kwargs['game_short_name'] == 'test_game'
            )

        assert check_shortcut_signature(Message.reply_game, Bot.send_game, ['chat_id'], ['quote'])
        assert check_shortcut_call(message.reply_game, message.bot, 'send_game')
        assert check_defaults_handling(message.reply_game, message.bot)

        monkeypatch.setattr(message.bot, 'send_game', make_assertion)
        assert message.reply_game(game_short_name='test_game')
        assert message.reply_game(game_short_name='test_game', quote=True)

    def test_reply_invoice(self, monkeypatch, message: Message):
        def make_assertion(*_, **kwargs):
            title = kwargs['title'] == 'title'
            description = kwargs['description'] == 'description'
            payload = kwargs['payload'] == 'payload'
            provider_token = kwargs['provider_token'] == 'provider_token'
            currency = kwargs['currency'] == 'currency'
            prices = kwargs['prices'] == 'prices'
            args = title and description and payload and provider_token and currency and prices
            return kwargs['chat_id'] == message.chat_id and args

        assert check_shortcut_signature(
            Message.reply_invoice, Bot.send_invoice, ['chat_id'], ['quote']
        )
        assert check_shortcut_call(message.reply_invoice, message.bot, 'send_invoice')
        assert check_defaults_handling(message.reply_invoice, message.bot)

        monkeypatch.setattr(message.bot, 'send_invoice', make_assertion)
        assert message.reply_invoice(
            'title',
            'description',
            'payload',
            'provider_token',
            'currency',
            'prices',
        )
        assert message.reply_invoice(
            'title',
            'description',
            'payload',
            'provider_token',
            'currency',
            'prices',
            quote=True,
        )

    @pytest.mark.parametrize('disable_notification', [False, True])
    def test_forward(self, monkeypatch, message, disable_notification):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == 123456
            from_chat = kwargs['from_chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            notification = kwargs['disable_notification'] == disable_notification
            return chat_id and from_chat and message_id and notification

        assert check_shortcut_signature(
            Message.forward, Bot.forward_message, ['from_chat_id', 'message_id'], []
        )
        assert check_shortcut_call(message.forward, message.bot, 'forward_message')
        assert check_defaults_handling(message.forward, message.bot)

        monkeypatch.setattr(message.bot, 'forward_message', make_assertion)
        assert message.forward(123456, disable_notification=disable_notification)
        assert not message.forward(635241)

    @pytest.mark.parametrize('disable_notification', [True, False])
    def test_copy(self, monkeypatch, message, disable_notification):
        keyboard = [[1, 2]]

        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == 123456
            from_chat = kwargs['from_chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            notification = kwargs['disable_notification'] == disable_notification
            if kwargs.get('reply_markup') is not None:
                reply_markup = kwargs['reply_markup'] is keyboard
            else:
                reply_markup = True
            return chat_id and from_chat and message_id and notification and reply_markup

        assert check_shortcut_signature(
            Message.copy, Bot.copy_message, ['from_chat_id', 'message_id'], []
        )
        assert check_shortcut_call(message.copy, message.bot, 'copy_message')
        assert check_defaults_handling(message.copy, message.bot)

        monkeypatch.setattr(message.bot, 'copy_message', make_assertion)
        assert message.copy(123456, disable_notification=disable_notification)
        assert message.copy(
            123456, reply_markup=keyboard, disable_notification=disable_notification
        )
        assert not message.copy(635241)

    @pytest.mark.parametrize('disable_notification', [True, False])
    def test_reply_copy(self, monkeypatch, message, disable_notification):
        keyboard = [[1, 2]]

        def make_assertion(*_, **kwargs):
            chat_id = kwargs['from_chat_id'] == 123456
            from_chat = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == 456789
            notification = kwargs['disable_notification'] == disable_notification
            if kwargs.get('reply_markup') is not None:
                reply_markup = kwargs['reply_markup'] is keyboard
            else:
                reply_markup = True
            if kwargs.get('reply_to_message_id') is not None:
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return chat_id and from_chat and message_id and notification and reply_markup and reply

        assert check_shortcut_signature(
            Message.reply_copy, Bot.copy_message, ['chat_id'], ['quote']
        )
        assert check_shortcut_call(message.copy, message.bot, 'copy_message')
        assert check_defaults_handling(message.copy, message.bot)

        monkeypatch.setattr(message.bot, 'copy_message', make_assertion)
        assert message.reply_copy(123456, 456789, disable_notification=disable_notification)
        assert message.reply_copy(
            123456, 456789, reply_markup=keyboard, disable_notification=disable_notification
        )
        assert message.reply_copy(
            123456, 456789, quote=True, disable_notification=disable_notification
        )
        assert message.reply_copy(
            123456,
            456789,
            quote=True,
            reply_to_message_id=message.message_id,
            disable_notification=disable_notification,
        )

    def test_edit_text(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            text = kwargs['text'] == 'test'
            return chat_id and message_id and text

        assert check_shortcut_signature(
            Message.edit_text,
            Bot.edit_message_text,
            ['chat_id', 'message_id', 'inline_message_id'],
            [],
        )
        assert check_shortcut_call(
            message.edit_text,
            message.bot,
            'edit_message_text',
            skip_params=['inline_message_id'],
            shortcut_kwargs=['message_id', 'chat_id'],
        )
        assert check_defaults_handling(message.edit_text, message.bot)

        monkeypatch.setattr(message.bot, 'edit_message_text', make_assertion)
        assert message.edit_text(text='test')

    def test_edit_caption(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            caption = kwargs['caption'] == 'new caption'
            return chat_id and message_id and caption

        assert check_shortcut_signature(
            Message.edit_caption,
            Bot.edit_message_caption,
            ['chat_id', 'message_id', 'inline_message_id'],
            [],
        )
        assert check_shortcut_call(
            message.edit_caption,
            message.bot,
            'edit_message_caption',
            skip_params=['inline_message_id'],
            shortcut_kwargs=['message_id', 'chat_id'],
        )
        assert check_defaults_handling(message.edit_caption, message.bot)

        monkeypatch.setattr(message.bot, 'edit_message_caption', make_assertion)
        assert message.edit_caption(caption='new caption')

    def test_edit_media(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            media = kwargs['media'] == 'my_media'
            return chat_id and message_id and media

        assert check_shortcut_signature(
            Message.edit_media,
            Bot.edit_message_media,
            ['chat_id', 'message_id', 'inline_message_id'],
            [],
        )
        assert check_shortcut_call(
            message.edit_media,
            message.bot,
            'edit_message_media',
            skip_params=['inline_message_id'],
            shortcut_kwargs=['message_id', 'chat_id'],
        )
        assert check_defaults_handling(message.edit_media, message.bot)

        monkeypatch.setattr(message.bot, 'edit_message_media', make_assertion)
        assert message.edit_media('my_media')

    def test_edit_reply_markup(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            reply_markup = kwargs['reply_markup'] == [['1', '2']]
            return chat_id and message_id and reply_markup

        assert check_shortcut_signature(
            Message.edit_reply_markup,
            Bot.edit_message_reply_markup,
            ['chat_id', 'message_id', 'inline_message_id'],
            [],
        )
        assert check_shortcut_call(
            message.edit_reply_markup,
            message.bot,
            'edit_message_reply_markup',
            skip_params=['inline_message_id'],
            shortcut_kwargs=['message_id', 'chat_id'],
        )
        assert check_defaults_handling(message.edit_reply_markup, message.bot)

        monkeypatch.setattr(message.bot, 'edit_message_reply_markup', make_assertion)
        assert message.edit_reply_markup(reply_markup=[['1', '2']])

    def test_edit_live_location(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            latitude = kwargs['latitude'] == 1
            longitude = kwargs['longitude'] == 2
            return chat_id and message_id and longitude and latitude

        assert check_shortcut_signature(
            Message.edit_live_location,
            Bot.edit_message_live_location,
            ['chat_id', 'message_id', 'inline_message_id'],
            [],
        )
        assert check_shortcut_call(
            message.edit_live_location,
            message.bot,
            'edit_message_live_location',
            skip_params=['inline_message_id'],
            shortcut_kwargs=['message_id', 'chat_id'],
        )
        assert check_defaults_handling(message.edit_live_location, message.bot)

        monkeypatch.setattr(message.bot, 'edit_message_live_location', make_assertion)
        assert message.edit_live_location(latitude=1, longitude=2)

    def test_stop_live_location(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            return chat_id and message_id

        assert check_shortcut_signature(
            Message.stop_live_location,
            Bot.stop_message_live_location,
            ['chat_id', 'message_id', 'inline_message_id'],
            [],
        )
        assert check_shortcut_call(
            message.stop_live_location,
            message.bot,
            'stop_message_live_location',
            skip_params=['inline_message_id'],
            shortcut_kwargs=['message_id', 'chat_id'],
        )
        assert check_defaults_handling(message.stop_live_location, message.bot)

        monkeypatch.setattr(message.bot, 'stop_message_live_location', make_assertion)
        assert message.stop_live_location()

    def test_set_game_score(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            user_id = kwargs['user_id'] == 1
            score = kwargs['score'] == 2
            return chat_id and message_id and user_id and score

        assert check_shortcut_signature(
            Message.set_game_score,
            Bot.set_game_score,
            ['chat_id', 'message_id', 'inline_message_id'],
            [],
        )
        assert check_shortcut_call(
            message.set_game_score,
            message.bot,
            'set_game_score',
            skip_params=['inline_message_id'],
            shortcut_kwargs=['message_id', 'chat_id'],
        )
        assert check_defaults_handling(message.set_game_score, message.bot)

        monkeypatch.setattr(message.bot, 'set_game_score', make_assertion)
        assert message.set_game_score(user_id=1, score=2)

    def test_get_game_high_scores(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            user_id = kwargs['user_id'] == 1
            return chat_id and message_id and user_id

        assert check_shortcut_signature(
            Message.get_game_high_scores,
            Bot.get_game_high_scores,
            ['chat_id', 'message_id', 'inline_message_id'],
            [],
        )
        assert check_shortcut_call(
            message.get_game_high_scores,
            message.bot,
            'get_game_high_scores',
            skip_params=['inline_message_id'],
            shortcut_kwargs=['message_id', 'chat_id'],
        )
        assert check_defaults_handling(message.get_game_high_scores, message.bot)

        monkeypatch.setattr(message.bot, 'get_game_high_scores', make_assertion)
        assert message.get_game_high_scores(user_id=1)

    def test_delete(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            return chat_id and message_id

        assert check_shortcut_signature(
            Message.delete, Bot.delete_message, ['chat_id', 'message_id'], []
        )
        assert check_shortcut_call(message.delete, message.bot, 'delete_message')
        assert check_defaults_handling(message.delete, message.bot)

        monkeypatch.setattr(message.bot, 'delete_message', make_assertion)
        assert message.delete()

    def test_stop_poll(self, monkeypatch, message):
        def make_assertion(*_, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            return chat_id and message_id

        assert check_shortcut_signature(
            Message.stop_poll, Bot.stop_poll, ['chat_id', 'message_id'], []
        )
        assert check_shortcut_call(message.stop_poll, message.bot, 'stop_poll')
        assert check_defaults_handling(message.stop_poll, message.bot)

        monkeypatch.setattr(message.bot, 'stop_poll', make_assertion)
        assert message.stop_poll()

    def test_pin(self, monkeypatch, message):
        def make_assertion(*args, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            return chat_id and message_id

        assert check_shortcut_signature(
            Message.pin, Bot.pin_chat_message, ['chat_id', 'message_id'], []
        )
        assert check_shortcut_call(message.pin, message.bot, 'pin_chat_message')
        assert check_defaults_handling(message.pin, message.bot)

        monkeypatch.setattr(message.bot, 'pin_chat_message', make_assertion)
        assert message.pin()

    def test_unpin(self, monkeypatch, message):
        def make_assertion(*args, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            return chat_id and message_id

        assert check_shortcut_signature(
            Message.unpin, Bot.unpin_chat_message, ['chat_id', 'message_id'], []
        )
        assert check_shortcut_call(
            message.unpin,
            message.bot,
            'unpin_chat_message',
            shortcut_kwargs=['chat_id', 'message_id'],
        )
        assert check_defaults_handling(message.unpin, message.bot)

        monkeypatch.setattr(message.bot, 'unpin_chat_message', make_assertion)
        assert message.unpin()

    def test_default_quote(self, message):
        message.bot.defaults = Defaults()

        try:
            message.bot.defaults._quote = False
            assert message._quote(None, None) is None

            message.bot.defaults._quote = True
            assert message._quote(None, None) == message.message_id

            message.bot.defaults._quote = None
            message.chat.type = Chat.PRIVATE
            assert message._quote(None, None) is None

            message.chat.type = Chat.GROUP
            assert message._quote(None, None)
        finally:
            message.bot.defaults = None

    def test_equality(self):
        id_ = 1
        a = Message(
            id_,
            self.date,
            self.chat,
            from_user=self.from_user,
        )
        b = Message(
            id_,
            self.date,
            self.chat,
            from_user=self.from_user,
        )
        c = Message(id_, self.date, Chat(123, Chat.GROUP), from_user=User(0, '', False))
        d = Message(0, self.date, self.chat, from_user=self.from_user)
        e = Update(id_)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
