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

import pytest

from telegram import Message, User, Chat, MessageEntity, Document, Update, Dice
from telegram.ext import Filters, BaseFilter, MessageFilter, UpdateFilter
from sys import version_info as py_ver
import inspect
import re

from telegram.utils.deprecate import TelegramDeprecationWarning


@pytest.fixture(scope='function')
def update():
    return Update(
        0,
        Message(
            0,
            datetime.datetime.utcnow(),
            Chat(0, 'private'),
            from_user=User(0, 'Testuser', False),
            via_bot=User(0, "Testbot", True),
            sender_chat=Chat(0, 'Channel'),
            forward_from=User(0, "HAL9000", False),
            forward_from_chat=Chat(0, "Channel"),
        ),
    )


@pytest.fixture(scope='function', params=MessageEntity.ALL_TYPES)
def message_entity(request):
    return MessageEntity(request.param, 0, 0, url='', user=User(1, 'first_name', False))


@pytest.fixture(
    scope='class',
    params=[{'class': MessageFilter}, {'class': UpdateFilter}],
    ids=['MessageFilter', 'UpdateFilter'],
)
def base_class(request):
    return request.param['class']


class TestFilters:
    def test_all_filters_slot_behaviour(self, recwarn, mro_slots):
        """
        Use depth first search to get all nested filters, and instantiate them (which need it) with
        the correct number of arguments, then test each filter separately. Also tests setting
        custom attributes on custom filters.
        """
        # The total no. of filters excluding filters defined in __all__ is about 70 as of 16/2/21.
        # Gather all the filters to test using DFS-
        visited = []
        classes = inspect.getmembers(Filters, predicate=inspect.isclass)  # List[Tuple[str, type]]
        stack = classes.copy()
        while stack:
            cls = stack[-1][-1]  # get last element and its class
            for inner_cls in inspect.getmembers(
                cls,  # Get inner filters
                lambda a: inspect.isclass(a) and not issubclass(a, cls.__class__),
            ):
                if inner_cls[1] not in visited:
                    stack.append(inner_cls)
                    visited.append(inner_cls[1])
                    classes.append(inner_cls)
                    break
            else:
                stack.pop()

        # Now start the actual testing
        for name, cls in classes:
            # Can't instantiate abstract classes without overriding methods, so skip them for now
            if inspect.isabstract(cls) or name in {'__class__', '__base__'}:
                continue

            assert '__slots__' in cls.__dict__, f"Filter {name!r} doesn't have __slots__"
            # get no. of args minus the 'self' argument
            args = len(inspect.signature(cls.__init__).parameters) - 1
            if cls.__base__.__name__ == '_ChatUserBaseFilter':  # Special case, only 1 arg needed
                inst = cls('1')
            else:
                inst = cls() if args < 1 else cls(*['blah'] * args)  # unpack variable no. of args

            for attr in cls.__slots__:
                assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}' for {name}"
                assert not inst.__dict__, f"got missing slot(s): {inst.__dict__} for {name}"
                assert len(mro_slots(inst)) == len(set(mro_slots(inst))), f"same slot in {name}"

            with pytest.warns(TelegramDeprecationWarning, match='custom attributes') as warn:
                inst.custom = 'should give warning'
                if not warn:
                    pytest.fail(f"Filter {name!r} didn't warn when setting custom attr")

        assert '__dict__' not in BaseFilter.__slots__ if py_ver < (3, 7) else True, 'dict in abc'

        class CustomFilter(MessageFilter):
            def filter(self, message: Message):
                pass

        with pytest.warns(None):
            CustomFilter().custom = 'allowed'  # Test setting custom attr to custom filters

        with pytest.warns(TelegramDeprecationWarning, match='custom attributes'):
            Filters().custom = 'raise warning'

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
        assert all(type(res) is SRE_TYPE for res in matches)
        result = (Filters.regex('deep') | Filters.regex(r'linked param'))(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        result = (Filters.regex('not int') | Filters.regex(r'linked param'))(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
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
        assert all(type(res) is SRE_TYPE for res in matches)
        result = (Filters.regex(r'linked param') & Filters.command)(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        result = (Filters.regex(r'linked param') | Filters.command)(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        # Should not give a match since it's a or filter and it short circuits
        result = (Filters.command | Filters.regex(r'linked param'))(update)
        assert result is True

    def test_regex_complex_merges(self, update):
        SRE_TYPE = type(re.match("", ""))
        update.message.text = 'test it out'
        test_filter = Filters.regex('test') & (
            (Filters.status_update | Filters.forwarded) | Filters.regex('out')
        )
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert len(matches) == 2
        assert all(type(res) is SRE_TYPE for res in matches)
        update.message.forward_date = datetime.datetime.utcnow()
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        update.message.text = 'test it'
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        update.message.forward_date = None
        result = test_filter(update)
        assert not result
        update.message.text = 'test it out'
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        update.message.pinned_message = True
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        update.message.text = 'it out'
        result = test_filter(update)
        assert not result

        update.message.text = 'test it out'
        update.message.forward_date = None
        update.message.pinned_message = None
        test_filter = (Filters.regex('test') | Filters.command) & (
            Filters.regex('it') | Filters.status_update
        )
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert len(matches) == 2
        assert all(type(res) is SRE_TYPE for res in matches)
        update.message.text = 'test'
        result = test_filter(update)
        assert not result
        update.message.pinned_message = True
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert len(matches) == 1
        assert all(type(res) is SRE_TYPE for res in matches)
        update.message.text = 'nothing'
        result = test_filter(update)
        assert not result
        update.message.text = '/start'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = test_filter(update)
        assert result
        assert isinstance(result, bool)
        update.message.text = '/start it'
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert len(matches) == 1
        assert all(type(res) is SRE_TYPE for res in matches)

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

        filter = ~Filters.regex('linked') & Filters.command
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

        filter = ~Filters.regex('linked') | Filters.command
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

    def test_filters_caption_regex(self, update):
        SRE_TYPE = type(re.match("", ""))
        update.message.caption = '/start deep-linked param'
        result = Filters.caption_regex(r'deep-linked param')(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert type(matches[0]) is SRE_TYPE
        update.message.caption = '/help'
        assert Filters.caption_regex(r'help')(update)

        update.message.caption = 'test'
        assert not Filters.caption_regex(r'fail')(update)
        assert Filters.caption_regex(r'test')(update)
        assert Filters.caption_regex(re.compile(r'test'))(update)
        assert Filters.caption_regex(re.compile(r'TEST', re.IGNORECASE))(update)

        update.message.caption = 'i love python'
        assert Filters.caption_regex(r'.\b[lo]{2}ve python')(update)

        update.message.caption = None
        assert not Filters.caption_regex(r'fail')(update)

    def test_filters_caption_regex_multiple(self, update):
        SRE_TYPE = type(re.match("", ""))
        update.message.caption = '/start deep-linked param'
        result = (Filters.caption_regex('deep') & Filters.caption_regex(r'linked param'))(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        result = (Filters.caption_regex('deep') | Filters.caption_regex(r'linked param'))(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        result = (Filters.caption_regex('not int') | Filters.caption_regex(r'linked param'))(
            update
        )
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        result = (Filters.caption_regex('not int') & Filters.caption_regex(r'linked param'))(
            update
        )
        assert not result

    def test_filters_merged_with_caption_regex(self, update):
        SRE_TYPE = type(re.match("", ""))
        update.message.caption = '/start deep-linked param'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = (Filters.command & Filters.caption_regex(r'linked param'))(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        result = (Filters.caption_regex(r'linked param') & Filters.command)(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        result = (Filters.caption_regex(r'linked param') | Filters.command)(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        # Should not give a match since it's a or filter and it short circuits
        result = (Filters.command | Filters.caption_regex(r'linked param'))(update)
        assert result is True

    def test_caption_regex_complex_merges(self, update):
        SRE_TYPE = type(re.match("", ""))
        update.message.caption = 'test it out'
        test_filter = Filters.caption_regex('test') & (
            (Filters.status_update | Filters.forwarded) | Filters.caption_regex('out')
        )
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert len(matches) == 2
        assert all(type(res) is SRE_TYPE for res in matches)
        update.message.forward_date = datetime.datetime.utcnow()
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        update.message.caption = 'test it'
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        update.message.forward_date = None
        result = test_filter(update)
        assert not result
        update.message.caption = 'test it out'
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        update.message.pinned_message = True
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert all(type(res) is SRE_TYPE for res in matches)
        update.message.caption = 'it out'
        result = test_filter(update)
        assert not result

        update.message.caption = 'test it out'
        update.message.forward_date = None
        update.message.pinned_message = None
        test_filter = (Filters.caption_regex('test') | Filters.command) & (
            Filters.caption_regex('it') | Filters.status_update
        )
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert len(matches) == 2
        assert all(type(res) is SRE_TYPE for res in matches)
        update.message.caption = 'test'
        result = test_filter(update)
        assert not result
        update.message.pinned_message = True
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert len(matches) == 1
        assert all(type(res) is SRE_TYPE for res in matches)
        update.message.caption = 'nothing'
        result = test_filter(update)
        assert not result
        update.message.caption = '/start'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = test_filter(update)
        assert result
        assert isinstance(result, bool)
        update.message.caption = '/start it'
        result = test_filter(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert len(matches) == 1
        assert all(type(res) is SRE_TYPE for res in matches)

    def test_caption_regex_inverted(self, update):
        update.message.caption = '/start deep-linked param'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]
        test_filter = ~Filters.caption_regex(r'deep-linked param')
        result = test_filter(update)
        assert not result
        update.message.caption = 'not it'
        result = test_filter(update)
        assert result
        assert isinstance(result, bool)

        test_filter = ~Filters.caption_regex('linked') & Filters.command
        update.message.caption = "it's linked"
        result = test_filter(update)
        assert not result
        update.message.caption = '/start'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = test_filter(update)
        assert result
        update.message.caption = '/linked'
        result = test_filter(update)
        assert not result

        test_filter = ~Filters.caption_regex('linked') | Filters.command
        update.message.caption = "it's linked"
        update.message.entities = []
        result = test_filter(update)
        assert not result
        update.message.caption = '/start linked'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = test_filter(update)
        assert result
        update.message.caption = '/start'
        result = test_filter(update)
        assert result
        update.message.caption = 'nothig'
        update.message.entities = []
        result = test_filter(update)
        assert result

    def test_filters_reply(self, update):
        another_message = Message(
            1,
            datetime.datetime.utcnow(),
            Chat(0, 'private'),
            from_user=User(1, 'TestOther', False),
        )
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
        update.message.document = Document(
            "file_id", 'unique_id', mime_type="application/vnd.android.package-archive"
        )
        assert Filters.document.apk(update)
        assert Filters.document.application(update)
        assert not Filters.document.doc(update)
        assert not Filters.document.audio(update)

        update.message.document.mime_type = "application/msword"
        assert Filters.document.doc(update)
        assert Filters.document.application(update)
        assert not Filters.document.docx(update)
        assert not Filters.document.audio(update)

        update.message.document.mime_type = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
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

    def test_filters_file_extension_basic(self, update):
        update.message.document = Document(
            "file_id",
            "unique_id",
            file_name="file.jpg",
            mime_type="image/jpeg",
        )
        assert Filters.document.file_extension("jpg")(update)
        assert not Filters.document.file_extension("jpeg")(update)
        assert not Filters.document.file_extension("file.jpg")(update)

        update.message.document.file_name = "file.tar.gz"
        assert Filters.document.file_extension("tar.gz")(update)
        assert Filters.document.file_extension("gz")(update)
        assert not Filters.document.file_extension("tgz")(update)
        assert not Filters.document.file_extension("jpg")(update)

        update.message.document = None
        assert not Filters.document.file_extension("jpg")(update)

    def test_filters_file_extension_minds_dots(self, update):
        update.message.document = Document(
            "file_id",
            "unique_id",
            file_name="file.jpg",
            mime_type="image/jpeg",
        )
        assert not Filters.document.file_extension(".jpg")(update)
        assert not Filters.document.file_extension("e.jpg")(update)
        assert not Filters.document.file_extension("file.jpg")(update)
        assert not Filters.document.file_extension("")(update)

        update.message.document.file_name = "file..jpg"
        assert Filters.document.file_extension("jpg")(update)
        assert Filters.document.file_extension(".jpg")(update)
        assert not Filters.document.file_extension("..jpg")(update)

        update.message.document.file_name = "file.docx"
        assert Filters.document.file_extension("docx")(update)
        assert not Filters.document.file_extension("doc")(update)
        assert not Filters.document.file_extension("ocx")(update)

        update.message.document.file_name = "file"
        assert not Filters.document.file_extension("")(update)
        assert not Filters.document.file_extension("file")(update)

        update.message.document.file_name = "file."
        assert Filters.document.file_extension("")(update)

    def test_filters_file_extension_none_arg(self, update):
        update.message.document = Document(
            "file_id",
            "unique_id",
            file_name="file.jpg",
            mime_type="image/jpeg",
        )
        assert not Filters.document.file_extension(None)(update)

        update.message.document.file_name = "file"
        assert Filters.document.file_extension(None)(update)
        assert not Filters.document.file_extension("None")(update)

        update.message.document.file_name = "file."
        assert not Filters.document.file_extension(None)(update)

        update.message.document = None
        assert not Filters.document.file_extension(None)(update)

    def test_filters_file_extension_case_sensitivity(self, update):
        update.message.document = Document(
            "file_id",
            "unique_id",
            file_name="file.jpg",
            mime_type="image/jpeg",
        )
        assert Filters.document.file_extension("JPG")(update)
        assert Filters.document.file_extension("jpG")(update)

        update.message.document.file_name = "file.JPG"
        assert Filters.document.file_extension("jpg")(update)
        assert not Filters.document.file_extension("jpg", case_sensitive=True)(update)

        update.message.document.file_name = "file.Dockerfile"
        assert Filters.document.file_extension("Dockerfile", case_sensitive=True)(update)
        assert not Filters.document.file_extension("DOCKERFILE", case_sensitive=True)(update)

    def test_filters_file_extension_name(self):
        assert Filters.document.file_extension("jpg").name == (
            "Filters.document.file_extension('jpg')"
        )
        assert Filters.document.file_extension("JPG").name == (
            "Filters.document.file_extension('jpg')"
        )
        assert Filters.document.file_extension("jpg", case_sensitive=True).name == (
            "Filters.document.file_extension('jpg', case_sensitive=True)"
        )
        assert Filters.document.file_extension("JPG", case_sensitive=True).name == (
            "Filters.document.file_extension('JPG', case_sensitive=True)"
        )
        assert Filters.document.file_extension(".jpg").name == (
            "Filters.document.file_extension('.jpg')"
        )
        assert Filters.document.file_extension("").name == "Filters.document.file_extension('')"
        assert (
            Filters.document.file_extension(None).name == "Filters.document.file_extension(None)"
        )

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

        update.message.message_auto_delete_timer_changed = True
        assert Filters.status_update(update)
        assert Filters.status_update.message_auto_delete_timer_changed(update)
        update.message.message_auto_delete_timer_changed = False

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

        update.message.proximity_alert_triggered = 'alert'
        assert Filters.status_update(update)
        assert Filters.status_update.proximity_alert_triggered(update)
        update.message.proximity_alert_triggered = None

        update.message.voice_chat_scheduled = 'scheduled'
        assert Filters.status_update(update)
        assert Filters.status_update.voice_chat_scheduled(update)
        update.message.voice_chat_scheduled = None

        update.message.voice_chat_started = 'hello'
        assert Filters.status_update(update)
        assert Filters.status_update.voice_chat_started(update)
        update.message.voice_chat_started = None

        update.message.voice_chat_ended = 'bye'
        assert Filters.status_update(update)
        assert Filters.status_update.voice_chat_ended(update)
        update.message.voice_chat_ended = None

        update.message.voice_chat_participants_invited = 'invited'
        assert Filters.status_update(update)
        assert Filters.status_update.voice_chat_participants_invited(update)
        update.message.voice_chat_participants_invited = None

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

    def test_private_filter_deprecation(self, update):
        with pytest.warns(TelegramDeprecationWarning):
            Filters.private(update)

    def test_group_filter(self, update):
        assert not Filters.group(update)
        update.message.chat.type = 'group'
        assert Filters.group(update)
        update.message.chat.type = 'supergroup'
        assert Filters.group(update)

    def test_group_filter_deprecation(self, update):
        with pytest.warns(TelegramDeprecationWarning):
            Filters.group(update)

    @pytest.mark.parametrize(
        ('chat_type, results'),
        [
            (None, (False, False, False, False, False, False)),
            (Chat.PRIVATE, (True, True, False, False, False, False)),
            (Chat.GROUP, (True, False, True, False, True, False)),
            (Chat.SUPERGROUP, (True, False, False, True, True, False)),
            (Chat.CHANNEL, (True, False, False, False, False, True)),
        ],
    )
    def test_filters_chat_types(self, update, chat_type, results):
        update.message.chat.type = chat_type
        assert Filters.chat_type(update) is results[0]
        assert Filters.chat_type.private(update) is results[1]
        assert Filters.chat_type.group(update) is results[2]
        assert Filters.chat_type.supergroup(update) is results[3]
        assert Filters.chat_type.groups(update) is results[4]
        assert Filters.chat_type.channel(update) is results[5]

    def test_filters_user_init(self):
        with pytest.raises(RuntimeError, match='in conjunction with'):
            Filters.user(user_id=1, username='user')

    def test_filters_user_allow_empty(self, update):
        assert not Filters.user()(update)
        assert Filters.user(allow_empty=True)(update)

    def test_filters_user_id(self, update):
        assert not Filters.user(user_id=1)(update)
        update.message.from_user.id = 1
        assert Filters.user(user_id=1)(update)
        update.message.from_user.id = 2
        assert Filters.user(user_id=[1, 2])(update)
        assert not Filters.user(user_id=[3, 4])(update)
        update.message.from_user = None
        assert not Filters.user(user_id=[3, 4])(update)

    def test_filters_username(self, update):
        assert not Filters.user(username='user')(update)
        assert not Filters.user(username='Testuser')(update)
        update.message.from_user.username = 'user@'
        assert Filters.user(username='@user@')(update)
        assert Filters.user(username='user@')(update)
        assert Filters.user(username=['user1', 'user@', 'user2'])(update)
        assert not Filters.user(username=['@username', '@user_2'])(update)
        update.message.from_user = None
        assert not Filters.user(username=['@username', '@user_2'])(update)

    def test_filters_user_change_id(self, update):
        f = Filters.user(user_id=1)
        assert f.user_ids == {1}
        update.message.from_user.id = 1
        assert f(update)
        update.message.from_user.id = 2
        assert not f(update)
        f.user_ids = 2
        assert f.user_ids == {2}
        assert f(update)

        with pytest.raises(RuntimeError, match='username in conjunction'):
            f.usernames = 'user'

    def test_filters_user_change_username(self, update):
        f = Filters.user(username='user')
        update.message.from_user.username = 'user'
        assert f(update)
        update.message.from_user.username = 'User'
        assert not f(update)
        f.usernames = 'User'
        assert f(update)

        with pytest.raises(RuntimeError, match='user_id in conjunction'):
            f.user_ids = 1

    def test_filters_user_add_user_by_name(self, update):
        users = ['user_a', 'user_b', 'user_c']
        f = Filters.user()

        for user in users:
            update.message.from_user.username = user
            assert not f(update)

        f.add_usernames('user_a')
        f.add_usernames(['user_b', 'user_c'])

        for user in users:
            update.message.from_user.username = user
            assert f(update)

        with pytest.raises(RuntimeError, match='user_id in conjunction'):
            f.add_user_ids(1)

    def test_filters_user_add_user_by_id(self, update):
        users = [1, 2, 3]
        f = Filters.user()

        for user in users:
            update.message.from_user.id = user
            assert not f(update)

        f.add_user_ids(1)
        f.add_user_ids([2, 3])

        for user in users:
            update.message.from_user.username = user
            assert f(update)

        with pytest.raises(RuntimeError, match='username in conjunction'):
            f.add_usernames('user')

    def test_filters_user_remove_user_by_name(self, update):
        users = ['user_a', 'user_b', 'user_c']
        f = Filters.user(username=users)

        with pytest.raises(RuntimeError, match='user_id in conjunction'):
            f.remove_user_ids(1)

        for user in users:
            update.message.from_user.username = user
            assert f(update)

        f.remove_usernames('user_a')
        f.remove_usernames(['user_b', 'user_c'])

        for user in users:
            update.message.from_user.username = user
            assert not f(update)

    def test_filters_user_remove_user_by_id(self, update):
        users = [1, 2, 3]
        f = Filters.user(user_id=users)

        with pytest.raises(RuntimeError, match='username in conjunction'):
            f.remove_usernames('user')

        for user in users:
            update.message.from_user.id = user
            assert f(update)

        f.remove_user_ids(1)
        f.remove_user_ids([2, 3])

        for user in users:
            update.message.from_user.username = user
            assert not f(update)

    def test_filters_user_repr(self):
        f = Filters.user([1, 2])
        assert str(f) == 'Filters.user(1, 2)'
        f.remove_user_ids(1)
        f.remove_user_ids(2)
        assert str(f) == 'Filters.user()'
        f.add_usernames('@foobar')
        assert str(f) == 'Filters.user(foobar)'
        f.add_usernames('@barfoo')
        assert str(f).startswith('Filters.user(')
        # we don't know th exact order
        assert 'barfoo' in str(f) and 'foobar' in str(f)

        with pytest.raises(RuntimeError, match='Cannot set name'):
            f.name = 'foo'

    def test_filters_chat_init(self):
        with pytest.raises(RuntimeError, match='in conjunction with'):
            Filters.chat(chat_id=1, username='chat')

    def test_filters_chat_allow_empty(self, update):
        assert not Filters.chat()(update)
        assert Filters.chat(allow_empty=True)(update)

    def test_filters_chat_id(self, update):
        assert not Filters.chat(chat_id=1)(update)
        update.message.chat.id = 1
        assert Filters.chat(chat_id=1)(update)
        update.message.chat.id = 2
        assert Filters.chat(chat_id=[1, 2])(update)
        assert not Filters.chat(chat_id=[3, 4])(update)
        update.message.chat = None
        assert not Filters.chat(chat_id=[3, 4])(update)

    def test_filters_chat_username(self, update):
        assert not Filters.chat(username='chat')(update)
        assert not Filters.chat(username='Testchat')(update)
        update.message.chat.username = 'chat@'
        assert Filters.chat(username='@chat@')(update)
        assert Filters.chat(username='chat@')(update)
        assert Filters.chat(username=['chat1', 'chat@', 'chat2'])(update)
        assert not Filters.chat(username=['@username', '@chat_2'])(update)
        update.message.chat = None
        assert not Filters.chat(username=['@username', '@chat_2'])(update)

    def test_filters_chat_change_id(self, update):
        f = Filters.chat(chat_id=1)
        assert f.chat_ids == {1}
        update.message.chat.id = 1
        assert f(update)
        update.message.chat.id = 2
        assert not f(update)
        f.chat_ids = 2
        assert f.chat_ids == {2}
        assert f(update)

        with pytest.raises(RuntimeError, match='username in conjunction'):
            f.usernames = 'chat'

    def test_filters_chat_change_username(self, update):
        f = Filters.chat(username='chat')
        update.message.chat.username = 'chat'
        assert f(update)
        update.message.chat.username = 'User'
        assert not f(update)
        f.usernames = 'User'
        assert f(update)

        with pytest.raises(RuntimeError, match='chat_id in conjunction'):
            f.chat_ids = 1

    def test_filters_chat_add_chat_by_name(self, update):
        chats = ['chat_a', 'chat_b', 'chat_c']
        f = Filters.chat()

        for chat in chats:
            update.message.chat.username = chat
            assert not f(update)

        f.add_usernames('chat_a')
        f.add_usernames(['chat_b', 'chat_c'])

        for chat in chats:
            update.message.chat.username = chat
            assert f(update)

        with pytest.raises(RuntimeError, match='chat_id in conjunction'):
            f.add_chat_ids(1)

    def test_filters_chat_add_chat_by_id(self, update):
        chats = [1, 2, 3]
        f = Filters.chat()

        for chat in chats:
            update.message.chat.id = chat
            assert not f(update)

        f.add_chat_ids(1)
        f.add_chat_ids([2, 3])

        for chat in chats:
            update.message.chat.username = chat
            assert f(update)

        with pytest.raises(RuntimeError, match='username in conjunction'):
            f.add_usernames('chat')

    def test_filters_chat_remove_chat_by_name(self, update):
        chats = ['chat_a', 'chat_b', 'chat_c']
        f = Filters.chat(username=chats)

        with pytest.raises(RuntimeError, match='chat_id in conjunction'):
            f.remove_chat_ids(1)

        for chat in chats:
            update.message.chat.username = chat
            assert f(update)

        f.remove_usernames('chat_a')
        f.remove_usernames(['chat_b', 'chat_c'])

        for chat in chats:
            update.message.chat.username = chat
            assert not f(update)

    def test_filters_chat_remove_chat_by_id(self, update):
        chats = [1, 2, 3]
        f = Filters.chat(chat_id=chats)

        with pytest.raises(RuntimeError, match='username in conjunction'):
            f.remove_usernames('chat')

        for chat in chats:
            update.message.chat.id = chat
            assert f(update)

        f.remove_chat_ids(1)
        f.remove_chat_ids([2, 3])

        for chat in chats:
            update.message.chat.username = chat
            assert not f(update)

    def test_filters_chat_repr(self):
        f = Filters.chat([1, 2])
        assert str(f) == 'Filters.chat(1, 2)'
        f.remove_chat_ids(1)
        f.remove_chat_ids(2)
        assert str(f) == 'Filters.chat()'
        f.add_usernames('@foobar')
        assert str(f) == 'Filters.chat(foobar)'
        f.add_usernames('@barfoo')
        assert str(f).startswith('Filters.chat(')
        # we don't know th exact order
        assert 'barfoo' in str(f) and 'foobar' in str(f)

        with pytest.raises(RuntimeError, match='Cannot set name'):
            f.name = 'foo'

    def test_filters_forwarded_from_init(self):
        with pytest.raises(RuntimeError, match='in conjunction with'):
            Filters.forwarded_from(chat_id=1, username='chat')

    def test_filters_forwarded_from_allow_empty(self, update):
        assert not Filters.forwarded_from()(update)
        assert Filters.forwarded_from(allow_empty=True)(update)

    def test_filters_forwarded_from_id(self, update):
        # Test with User id-
        assert not Filters.forwarded_from(chat_id=1)(update)
        update.message.forward_from.id = 1
        assert Filters.forwarded_from(chat_id=1)(update)
        update.message.forward_from.id = 2
        assert Filters.forwarded_from(chat_id=[1, 2])(update)
        assert not Filters.forwarded_from(chat_id=[3, 4])(update)
        update.message.forward_from = None
        assert not Filters.forwarded_from(chat_id=[3, 4])(update)

        # Test with Chat id-
        update.message.forward_from_chat.id = 4
        assert Filters.forwarded_from(chat_id=[4])(update)
        assert Filters.forwarded_from(chat_id=[3, 4])(update)

        update.message.forward_from_chat.id = 2
        assert not Filters.forwarded_from(chat_id=[3, 4])(update)
        assert Filters.forwarded_from(chat_id=2)(update)

    def test_filters_forwarded_from_username(self, update):
        # For User username
        assert not Filters.forwarded_from(username='chat')(update)
        assert not Filters.forwarded_from(username='Testchat')(update)
        update.message.forward_from.username = 'chat@'
        assert Filters.forwarded_from(username='@chat@')(update)
        assert Filters.forwarded_from(username='chat@')(update)
        assert Filters.forwarded_from(username=['chat1', 'chat@', 'chat2'])(update)
        assert not Filters.forwarded_from(username=['@username', '@chat_2'])(update)
        update.message.forward_from = None
        assert not Filters.forwarded_from(username=['@username', '@chat_2'])(update)

        # For Chat username
        assert not Filters.forwarded_from(username='chat')(update)
        assert not Filters.forwarded_from(username='Testchat')(update)
        update.message.forward_from_chat.username = 'chat@'
        assert Filters.forwarded_from(username='@chat@')(update)
        assert Filters.forwarded_from(username='chat@')(update)
        assert Filters.forwarded_from(username=['chat1', 'chat@', 'chat2'])(update)
        assert not Filters.forwarded_from(username=['@username', '@chat_2'])(update)
        update.message.forward_from_chat = None
        assert not Filters.forwarded_from(username=['@username', '@chat_2'])(update)

    def test_filters_forwarded_from_change_id(self, update):
        f = Filters.forwarded_from(chat_id=1)
        # For User ids-
        assert f.chat_ids == {1}
        update.message.forward_from.id = 1
        assert f(update)
        update.message.forward_from.id = 2
        assert not f(update)
        f.chat_ids = 2
        assert f.chat_ids == {2}
        assert f(update)

        # For Chat ids-
        f = Filters.forwarded_from(chat_id=1)  # reset this
        update.message.forward_from = None  # and change this to None, only one of them can be True
        assert f.chat_ids == {1}
        update.message.forward_from_chat.id = 1
        assert f(update)
        update.message.forward_from_chat.id = 2
        assert not f(update)
        f.chat_ids = 2
        assert f.chat_ids == {2}
        assert f(update)

        with pytest.raises(RuntimeError, match='username in conjunction'):
            f.usernames = 'chat'

    def test_filters_forwarded_from_change_username(self, update):
        # For User usernames
        f = Filters.forwarded_from(username='chat')
        update.message.forward_from.username = 'chat'
        assert f(update)
        update.message.forward_from.username = 'User'
        assert not f(update)
        f.usernames = 'User'
        assert f(update)

        # For Chat usernames
        update.message.forward_from = None
        f = Filters.forwarded_from(username='chat')
        update.message.forward_from_chat.username = 'chat'
        assert f(update)
        update.message.forward_from_chat.username = 'User'
        assert not f(update)
        f.usernames = 'User'
        assert f(update)

        with pytest.raises(RuntimeError, match='chat_id in conjunction'):
            f.chat_ids = 1

    def test_filters_forwarded_from_add_chat_by_name(self, update):
        chats = ['chat_a', 'chat_b', 'chat_c']
        f = Filters.forwarded_from()

        # For User usernames
        for chat in chats:
            update.message.forward_from.username = chat
            assert not f(update)

        f.add_usernames('chat_a')
        f.add_usernames(['chat_b', 'chat_c'])

        for chat in chats:
            update.message.forward_from.username = chat
            assert f(update)

        # For Chat usernames
        update.message.forward_from = None
        f = Filters.forwarded_from()
        for chat in chats:
            update.message.forward_from_chat.username = chat
            assert not f(update)

        f.add_usernames('chat_a')
        f.add_usernames(['chat_b', 'chat_c'])

        for chat in chats:
            update.message.forward_from_chat.username = chat
            assert f(update)

        with pytest.raises(RuntimeError, match='chat_id in conjunction'):
            f.add_chat_ids(1)

    def test_filters_forwarded_from_add_chat_by_id(self, update):
        chats = [1, 2, 3]
        f = Filters.forwarded_from()

        # For User ids
        for chat in chats:
            update.message.forward_from.id = chat
            assert not f(update)

        f.add_chat_ids(1)
        f.add_chat_ids([2, 3])

        for chat in chats:
            update.message.forward_from.username = chat
            assert f(update)

        # For Chat ids-
        update.message.forward_from = None
        f = Filters.forwarded_from()
        for chat in chats:
            update.message.forward_from_chat.id = chat
            assert not f(update)

        f.add_chat_ids(1)
        f.add_chat_ids([2, 3])

        for chat in chats:
            update.message.forward_from_chat.username = chat
            assert f(update)

        with pytest.raises(RuntimeError, match='username in conjunction'):
            f.add_usernames('chat')

    def test_filters_forwarded_from_remove_chat_by_name(self, update):
        chats = ['chat_a', 'chat_b', 'chat_c']
        f = Filters.forwarded_from(username=chats)

        with pytest.raises(RuntimeError, match='chat_id in conjunction'):
            f.remove_chat_ids(1)

        # For User usernames
        for chat in chats:
            update.message.forward_from.username = chat
            assert f(update)

        f.remove_usernames('chat_a')
        f.remove_usernames(['chat_b', 'chat_c'])

        for chat in chats:
            update.message.forward_from.username = chat
            assert not f(update)

        # For Chat usernames
        update.message.forward_from = None
        f = Filters.forwarded_from(username=chats)
        for chat in chats:
            update.message.forward_from_chat.username = chat
            assert f(update)

        f.remove_usernames('chat_a')
        f.remove_usernames(['chat_b', 'chat_c'])

        for chat in chats:
            update.message.forward_from_chat.username = chat
            assert not f(update)

    def test_filters_forwarded_from_remove_chat_by_id(self, update):
        chats = [1, 2, 3]
        f = Filters.forwarded_from(chat_id=chats)

        with pytest.raises(RuntimeError, match='username in conjunction'):
            f.remove_usernames('chat')

        # For User ids
        for chat in chats:
            update.message.forward_from.id = chat
            assert f(update)

        f.remove_chat_ids(1)
        f.remove_chat_ids([2, 3])

        for chat in chats:
            update.message.forward_from.username = chat
            assert not f(update)

        # For Chat ids
        update.message.forward_from = None
        f = Filters.forwarded_from(chat_id=chats)
        for chat in chats:
            update.message.forward_from_chat.id = chat
            assert f(update)

        f.remove_chat_ids(1)
        f.remove_chat_ids([2, 3])

        for chat in chats:
            update.message.forward_from_chat.username = chat
            assert not f(update)

    def test_filters_forwarded_from_repr(self):
        f = Filters.forwarded_from([1, 2])
        assert str(f) == 'Filters.forwarded_from(1, 2)'
        f.remove_chat_ids(1)
        f.remove_chat_ids(2)
        assert str(f) == 'Filters.forwarded_from()'
        f.add_usernames('@foobar')
        assert str(f) == 'Filters.forwarded_from(foobar)'
        f.add_usernames('@barfoo')
        assert str(f).startswith('Filters.forwarded_from(')
        # we don't know the exact order
        assert 'barfoo' in str(f) and 'foobar' in str(f)

        with pytest.raises(RuntimeError, match='Cannot set name'):
            f.name = 'foo'

    def test_filters_sender_chat_init(self):
        with pytest.raises(RuntimeError, match='in conjunction with'):
            Filters.sender_chat(chat_id=1, username='chat')

    def test_filters_sender_chat_allow_empty(self, update):
        assert not Filters.sender_chat()(update)
        assert Filters.sender_chat(allow_empty=True)(update)

    def test_filters_sender_chat_id(self, update):
        assert not Filters.sender_chat(chat_id=1)(update)
        update.message.sender_chat.id = 1
        assert Filters.sender_chat(chat_id=1)(update)
        update.message.sender_chat.id = 2
        assert Filters.sender_chat(chat_id=[1, 2])(update)
        assert not Filters.sender_chat(chat_id=[3, 4])(update)
        update.message.sender_chat = None
        assert not Filters.sender_chat(chat_id=[3, 4])(update)

    def test_filters_sender_chat_username(self, update):
        assert not Filters.sender_chat(username='chat')(update)
        assert not Filters.sender_chat(username='Testchat')(update)
        update.message.sender_chat.username = 'chat@'
        assert Filters.sender_chat(username='@chat@')(update)
        assert Filters.sender_chat(username='chat@')(update)
        assert Filters.sender_chat(username=['chat1', 'chat@', 'chat2'])(update)
        assert not Filters.sender_chat(username=['@username', '@chat_2'])(update)
        update.message.sender_chat = None
        assert not Filters.sender_chat(username=['@username', '@chat_2'])(update)

    def test_filters_sender_chat_change_id(self, update):
        f = Filters.sender_chat(chat_id=1)
        assert f.chat_ids == {1}
        update.message.sender_chat.id = 1
        assert f(update)
        update.message.sender_chat.id = 2
        assert not f(update)
        f.chat_ids = 2
        assert f.chat_ids == {2}
        assert f(update)

        with pytest.raises(RuntimeError, match='username in conjunction'):
            f.usernames = 'chat'

    def test_filters_sender_chat_change_username(self, update):
        f = Filters.sender_chat(username='chat')
        update.message.sender_chat.username = 'chat'
        assert f(update)
        update.message.sender_chat.username = 'User'
        assert not f(update)
        f.usernames = 'User'
        assert f(update)

        with pytest.raises(RuntimeError, match='chat_id in conjunction'):
            f.chat_ids = 1

    def test_filters_sender_chat_add_sender_chat_by_name(self, update):
        chats = ['chat_a', 'chat_b', 'chat_c']
        f = Filters.sender_chat()

        for chat in chats:
            update.message.sender_chat.username = chat
            assert not f(update)

        f.add_usernames('chat_a')
        f.add_usernames(['chat_b', 'chat_c'])

        for chat in chats:
            update.message.sender_chat.username = chat
            assert f(update)

        with pytest.raises(RuntimeError, match='chat_id in conjunction'):
            f.add_chat_ids(1)

    def test_filters_sender_chat_add_sender_chat_by_id(self, update):
        chats = [1, 2, 3]
        f = Filters.sender_chat()

        for chat in chats:
            update.message.sender_chat.id = chat
            assert not f(update)

        f.add_chat_ids(1)
        f.add_chat_ids([2, 3])

        for chat in chats:
            update.message.sender_chat.username = chat
            assert f(update)

        with pytest.raises(RuntimeError, match='username in conjunction'):
            f.add_usernames('chat')

    def test_filters_sender_chat_remove_sender_chat_by_name(self, update):
        chats = ['chat_a', 'chat_b', 'chat_c']
        f = Filters.sender_chat(username=chats)

        with pytest.raises(RuntimeError, match='chat_id in conjunction'):
            f.remove_chat_ids(1)

        for chat in chats:
            update.message.sender_chat.username = chat
            assert f(update)

        f.remove_usernames('chat_a')
        f.remove_usernames(['chat_b', 'chat_c'])

        for chat in chats:
            update.message.sender_chat.username = chat
            assert not f(update)

    def test_filters_sender_chat_remove_sender_chat_by_id(self, update):
        chats = [1, 2, 3]
        f = Filters.sender_chat(chat_id=chats)

        with pytest.raises(RuntimeError, match='username in conjunction'):
            f.remove_usernames('chat')

        for chat in chats:
            update.message.sender_chat.id = chat
            assert f(update)

        f.remove_chat_ids(1)
        f.remove_chat_ids([2, 3])

        for chat in chats:
            update.message.sender_chat.username = chat
            assert not f(update)

    def test_filters_sender_chat_repr(self):
        f = Filters.sender_chat([1, 2])
        assert str(f) == 'Filters.sender_chat(1, 2)'
        f.remove_chat_ids(1)
        f.remove_chat_ids(2)
        assert str(f) == 'Filters.sender_chat()'
        f.add_usernames('@foobar')
        assert str(f) == 'Filters.sender_chat(foobar)'
        f.add_usernames('@barfoo')
        assert str(f).startswith('Filters.sender_chat(')
        # we don't know th exact order
        assert 'barfoo' in str(f) and 'foobar' in str(f)

        with pytest.raises(RuntimeError, match='Cannot set name'):
            f.name = 'foo'

    def test_filters_sender_chat_super_group(self, update):
        update.message.sender_chat.type = Chat.PRIVATE
        assert not Filters.sender_chat.super_group(update)
        update.message.sender_chat.type = Chat.CHANNEL
        assert not Filters.sender_chat.super_group(update)
        update.message.sender_chat.type = Chat.SUPERGROUP
        assert Filters.sender_chat.super_group(update)
        update.message.sender_chat = None
        assert not Filters.sender_chat.super_group(update)

    def test_filters_sender_chat_channel(self, update):
        update.message.sender_chat.type = Chat.PRIVATE
        assert not Filters.sender_chat.channel(update)
        update.message.sender_chat.type = Chat.SUPERGROUP
        assert not Filters.sender_chat.channel(update)
        update.message.sender_chat.type = Chat.CHANNEL
        assert Filters.sender_chat.channel(update)
        update.message.sender_chat = None
        assert not Filters.sender_chat.channel(update)

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

    @pytest.mark.parametrize('emoji', Dice.ALL_EMOJI)
    def test_filters_dice(self, update, emoji):
        update.message.dice = Dice(4, emoji)
        assert Filters.dice(update)
        update.message.dice = None
        assert not Filters.dice(update)

    @pytest.mark.parametrize('emoji', Dice.ALL_EMOJI)
    def test_filters_dice_list(self, update, emoji):
        update.message.dice = None
        assert not Filters.dice(5)(update)

        update.message.dice = Dice(5, emoji)
        assert Filters.dice(5)(update)
        assert Filters.dice({5, 6})(update)
        assert not Filters.dice(1)(update)
        assert not Filters.dice([2, 3])(update)

    def test_filters_dice_type(self, update):
        update.message.dice = Dice(5, '🎲')
        assert Filters.dice.dice(update)
        assert Filters.dice.dice([4, 5])(update)
        assert not Filters.dice.darts(update)
        assert not Filters.dice.basketball(update)
        assert not Filters.dice.dice([6])(update)

        update.message.dice = Dice(5, '🎯')
        assert Filters.dice.darts(update)
        assert Filters.dice.darts([4, 5])(update)
        assert not Filters.dice.dice(update)
        assert not Filters.dice.basketball(update)
        assert not Filters.dice.darts([6])(update)

        update.message.dice = Dice(5, '🏀')
        assert Filters.dice.basketball(update)
        assert Filters.dice.basketball([4, 5])(update)
        assert not Filters.dice.dice(update)
        assert not Filters.dice.darts(update)
        assert not Filters.dice.basketball([4])(update)

        update.message.dice = Dice(5, '⚽')
        assert Filters.dice.football(update)
        assert Filters.dice.football([4, 5])(update)
        assert not Filters.dice.dice(update)
        assert not Filters.dice.darts(update)
        assert not Filters.dice.football([4])(update)

        update.message.dice = Dice(5, '🎰')
        assert Filters.dice.slot_machine(update)
        assert Filters.dice.slot_machine([4, 5])(update)
        assert not Filters.dice.dice(update)
        assert not Filters.dice.darts(update)
        assert not Filters.dice.slot_machine([4])(update)

        update.message.dice = Dice(5, '🎳')
        assert Filters.dice.bowling(update)
        assert Filters.dice.bowling([4, 5])(update)
        assert not Filters.dice.dice(update)
        assert not Filters.dice.darts(update)
        assert not Filters.dice.bowling([4])(update)

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
        update.message.forward_date = None
        assert not (Filters.text & (Filters.forwarded | Filters.status_update))(update)
        update.message.pinned_message = True
        assert Filters.text & (Filters.forwarded | Filters.status_update)(update)

        assert (
            str(Filters.text & (Filters.forwarded | Filters.entity(MessageEntity.MENTION)))
            == '<Filters.text and <Filters.forwarded or '
            'Filters.entity(mention)>>'
        )

    def test_xor_filters(self, update):
        update.message.text = 'test'
        update.effective_user.id = 123
        assert not (Filters.text ^ Filters.user(123))(update)
        update.message.text = None
        update.effective_user.id = 1234
        assert not (Filters.text ^ Filters.user(123))(update)
        update.message.text = 'test'
        assert (Filters.text ^ Filters.user(123))(update)
        update.message.text = None
        update.effective_user.id = 123
        assert (Filters.text ^ Filters.user(123))(update)

    def test_xor_filters_repr(self, update):
        assert str(Filters.text ^ Filters.user(123)) == '<Filters.text xor Filters.user(123)>'
        with pytest.raises(RuntimeError, match='Cannot set name'):
            (Filters.text ^ Filters.user(123)).name = 'foo'

    def test_and_xor_filters(self, update):
        update.message.text = 'test'
        update.message.forward_date = datetime.datetime.utcnow()
        assert (Filters.forwarded & (Filters.text ^ Filters.user(123)))(update)
        update.message.text = None
        update.effective_user.id = 123
        assert (Filters.forwarded & (Filters.text ^ Filters.user(123)))(update)
        update.message.text = 'test'
        assert not (Filters.forwarded & (Filters.text ^ Filters.user(123)))(update)
        update.message.forward_date = None
        update.message.text = None
        update.effective_user.id = 123
        assert not (Filters.forwarded & (Filters.text ^ Filters.user(123)))(update)
        update.message.text = 'test'
        update.effective_user.id = 456
        assert not (Filters.forwarded & (Filters.text ^ Filters.user(123)))(update)

        assert (
            str(Filters.forwarded & (Filters.text ^ Filters.user(123)))
            == '<Filters.forwarded and <Filters.text xor '
            'Filters.user(123)>>'
        )

    def test_xor_regex_filters(self, update):
        SRE_TYPE = type(re.match("", ""))
        update.message.text = 'test'
        update.message.forward_date = datetime.datetime.utcnow()
        assert not (Filters.forwarded ^ Filters.regex('^test$'))(update)
        update.message.forward_date = None
        result = (Filters.forwarded ^ Filters.regex('^test$'))(update)
        assert result
        assert isinstance(result, dict)
        matches = result['matches']
        assert isinstance(matches, list)
        assert type(matches[0]) is SRE_TYPE
        update.message.forward_date = datetime.datetime.utcnow()
        update.message.text = None
        assert (Filters.forwarded ^ Filters.regex('^test$'))(update) is True

    def test_inverted_filters(self, update):
        update.message.text = '/test'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]
        assert Filters.command(update)
        assert not (~Filters.command)(update)
        update.message.text = 'test'
        update.message.entities = []
        assert not Filters.command(update)
        assert (~Filters.command)(update)

    def test_inverted_filters_repr(self, update):
        assert str(~Filters.text) == '<inverted Filters.text>'
        with pytest.raises(RuntimeError, match='Cannot set name'):
            (~Filters.text).name = 'foo'

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

        with pytest.raises(TypeError, match='Can\'t instantiate abstract class _CustomFilter'):
            _CustomFilter()

    def test_custom_unnamed_filter(self, update, base_class):
        class Unnamed(base_class):
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

    def test_merged_short_circuit_and(self, update, base_class):
        update.message.text = '/test'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]

        class TestException(Exception):
            pass

        class RaisingFilter(base_class):
            def filter(self, _):
                raise TestException

        raising_filter = RaisingFilter()

        with pytest.raises(TestException):
            (Filters.command & raising_filter)(update)

        update.message.text = 'test'
        update.message.entities = []
        (Filters.command & raising_filter)(update)

    def test_merged_filters_repr(self, update):
        with pytest.raises(RuntimeError, match='Cannot set name'):
            (Filters.text & Filters.photo).name = 'foo'

    def test_merged_short_circuit_or(self, update, base_class):
        update.message.text = 'test'

        class TestException(Exception):
            pass

        class RaisingFilter(base_class):
            def filter(self, _):
                raise TestException

        raising_filter = RaisingFilter()

        with pytest.raises(TestException):
            (Filters.command | raising_filter)(update)

        update.message.text = '/test'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]
        (Filters.command | raising_filter)(update)

    def test_merged_data_merging_and(self, update, base_class):
        update.message.text = '/test'
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]

        class DataFilter(base_class):
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

    def test_merged_data_merging_or(self, update, base_class):
        update.message.text = '/test'

        class DataFilter(base_class):
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

    def test_filters_via_bot_init(self):
        with pytest.raises(RuntimeError, match='in conjunction with'):
            Filters.via_bot(bot_id=1, username='bot')

    def test_filters_via_bot_allow_empty(self, update):
        assert not Filters.via_bot()(update)
        assert Filters.via_bot(allow_empty=True)(update)

    def test_filters_via_bot_id(self, update):
        assert not Filters.via_bot(bot_id=1)(update)
        update.message.via_bot.id = 1
        assert Filters.via_bot(bot_id=1)(update)
        update.message.via_bot.id = 2
        assert Filters.via_bot(bot_id=[1, 2])(update)
        assert not Filters.via_bot(bot_id=[3, 4])(update)
        update.message.via_bot = None
        assert not Filters.via_bot(bot_id=[3, 4])(update)

    def test_filters_via_bot_username(self, update):
        assert not Filters.via_bot(username='bot')(update)
        assert not Filters.via_bot(username='Testbot')(update)
        update.message.via_bot.username = 'bot@'
        assert Filters.via_bot(username='@bot@')(update)
        assert Filters.via_bot(username='bot@')(update)
        assert Filters.via_bot(username=['bot1', 'bot@', 'bot2'])(update)
        assert not Filters.via_bot(username=['@username', '@bot_2'])(update)
        update.message.via_bot = None
        assert not Filters.user(username=['@username', '@bot_2'])(update)

    def test_filters_via_bot_change_id(self, update):
        f = Filters.via_bot(bot_id=3)
        assert f.bot_ids == {3}
        update.message.via_bot.id = 3
        assert f(update)
        update.message.via_bot.id = 2
        assert not f(update)
        f.bot_ids = 2
        assert f.bot_ids == {2}
        assert f(update)

        with pytest.raises(RuntimeError, match='username in conjunction'):
            f.usernames = 'user'

    def test_filters_via_bot_change_username(self, update):
        f = Filters.via_bot(username='bot')
        update.message.via_bot.username = 'bot'
        assert f(update)
        update.message.via_bot.username = 'Bot'
        assert not f(update)
        f.usernames = 'Bot'
        assert f(update)

        with pytest.raises(RuntimeError, match='bot_id in conjunction'):
            f.bot_ids = 1

    def test_filters_via_bot_add_user_by_name(self, update):
        users = ['bot_a', 'bot_b', 'bot_c']
        f = Filters.via_bot()

        for user in users:
            update.message.via_bot.username = user
            assert not f(update)

        f.add_usernames('bot_a')
        f.add_usernames(['bot_b', 'bot_c'])

        for user in users:
            update.message.via_bot.username = user
            assert f(update)

        with pytest.raises(RuntimeError, match='bot_id in conjunction'):
            f.add_bot_ids(1)

    def test_filters_via_bot_add_user_by_id(self, update):
        users = [1, 2, 3]
        f = Filters.via_bot()

        for user in users:
            update.message.via_bot.id = user
            assert not f(update)

        f.add_bot_ids(1)
        f.add_bot_ids([2, 3])

        for user in users:
            update.message.via_bot.username = user
            assert f(update)

        with pytest.raises(RuntimeError, match='username in conjunction'):
            f.add_usernames('bot')

    def test_filters_via_bot_remove_user_by_name(self, update):
        users = ['bot_a', 'bot_b', 'bot_c']
        f = Filters.via_bot(username=users)

        with pytest.raises(RuntimeError, match='bot_id in conjunction'):
            f.remove_bot_ids(1)

        for user in users:
            update.message.via_bot.username = user
            assert f(update)

        f.remove_usernames('bot_a')
        f.remove_usernames(['bot_b', 'bot_c'])

        for user in users:
            update.message.via_bot.username = user
            assert not f(update)

    def test_filters_via_bot_remove_user_by_id(self, update):
        users = [1, 2, 3]
        f = Filters.via_bot(bot_id=users)

        with pytest.raises(RuntimeError, match='username in conjunction'):
            f.remove_usernames('bot')

        for user in users:
            update.message.via_bot.id = user
            assert f(update)

        f.remove_bot_ids(1)
        f.remove_bot_ids([2, 3])

        for user in users:
            update.message.via_bot.username = user
            assert not f(update)

    def test_filters_via_bot_repr(self):
        f = Filters.via_bot([1, 2])
        assert str(f) == 'Filters.via_bot(1, 2)'
        f.remove_bot_ids(1)
        f.remove_bot_ids(2)
        assert str(f) == 'Filters.via_bot()'
        f.add_usernames('@foobar')
        assert str(f) == 'Filters.via_bot(foobar)'
        f.add_usernames('@barfoo')
        assert str(f).startswith('Filters.via_bot(')
        # we don't know th exact order
        assert 'barfoo' in str(f) and 'foobar' in str(f)

        with pytest.raises(RuntimeError, match='Cannot set name'):
            f.name = 'foo'

    def test_filters_attachment(self, update):
        assert not Filters.attachment(update)
        # we need to define a new Update (or rather, message class) here because
        # effective_attachment is only evaluated once per instance, and the filter relies on that
        up = Update(
            0,
            Message(
                0,
                datetime.datetime.utcnow(),
                Chat(0, 'private'),
                document=Document("str", "other_str"),
            ),
        )
        assert Filters.attachment(up)
