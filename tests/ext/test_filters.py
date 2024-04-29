#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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
import inspect
import re

import pytest

from telegram import (
    CallbackQuery,
    Chat,
    Dice,
    Document,
    File,
    Message,
    MessageEntity,
    MessageOriginChannel,
    MessageOriginChat,
    MessageOriginHiddenUser,
    MessageOriginUser,
    Sticker,
    SuccessfulPayment,
    Update,
    User,
)
from telegram.ext import filters
from tests.auxil.slots import mro_slots


@pytest.fixture()
def update():
    update = Update(
        0,
        Message(
            0,
            datetime.datetime.utcnow(),
            Chat(0, "private"),
            from_user=User(0, "Testuser", False),
            via_bot=User(0, "Testbot", True),
            sender_chat=Chat(0, "Channel"),
            forward_origin=MessageOriginUser(
                datetime.datetime.utcnow(), User(0, "Testuser", False)
            ),
        ),
    )
    update._unfreeze()
    update.message._unfreeze()
    update.message.chat._unfreeze()
    update.message.from_user._unfreeze()
    update.message.via_bot._unfreeze()
    update.message.sender_chat._unfreeze()
    update.message.forward_origin._unfreeze()
    update.message.forward_origin.sender_user._unfreeze()
    return update


@pytest.fixture(params=MessageEntity.ALL_TYPES)
def message_entity(request):
    return MessageEntity(request.param, 0, 0, url="", user=User(1, "first_name", False))


@pytest.fixture(
    scope="class",
    params=[{"class": filters.MessageFilter}, {"class": filters.UpdateFilter}],
    ids=["MessageFilter", "UpdateFilter"],
)
def base_class(request):
    return request.param["class"]


@pytest.fixture(scope="class")
def message_origin_user():
    return MessageOriginUser(datetime.datetime.utcnow(), User(1, "TestOther", False))


class TestFilters:
    def test_all_filters_slot_behaviour(self):
        """
        Use depth first search to get all nested filters, and instantiate them (which need it) with
        the correct number of arguments, then test each filter separately. Also tests setting
        custom attributes on custom filters.
        """

        def filter_class(obj):
            return bool(inspect.isclass(obj) and "filters" in repr(obj))

        # The total no. of filters is about 72 as of 31/10/21.
        # Gather all the filters to test using DFS-
        visited = []
        classes = inspect.getmembers(filters, predicate=filter_class)  # List[Tuple[str, type]]
        stack = classes.copy()
        while stack:
            cls = stack[-1][-1]  # get last element and its class
            for inner_cls in inspect.getmembers(
                cls,  # Get inner filters
                lambda a: inspect.isclass(a) and not issubclass(a, cls.__class__),  # noqa: B023
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
            exclude = {"_MergedFilter", "_XORFilter"}
            if inspect.isabstract(cls) or name in {"__class__", "__base__"} | exclude:
                continue

            assert "__slots__" in cls.__dict__, f"Filter {name!r} doesn't have __slots__"
            # get no. of args minus the 'self', 'args' and 'kwargs' argument
            init_sig = inspect.signature(cls.__init__).parameters
            extra = 0
            for param in init_sig:
                if param in {"self", "args", "kwargs"}:
                    extra += 1
            args = len(init_sig) - extra

            if not args:
                inst = cls()
            elif args == 1:
                inst = cls("1")
            else:
                inst = cls(*["blah"])

            assert len(mro_slots(inst)) == len(set(mro_slots(inst))), f"same slot in {name}"

            for attr in cls.__slots__:
                assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}' for {name}"

    def test__all__(self):
        expected = {
            key
            for key, member in filters.__dict__.items()
            if (
                not key.startswith("_")
                # exclude imported stuff
                and getattr(member, "__module__", "unknown module") == "telegram.ext.filters"
                and key != "sys"
            )
        }
        actual = set(filters.__all__)
        assert (
            actual == expected
        ), f"Members {expected - actual} were not listed in constants.__all__"

    def test_filters_all(self, update):
        assert filters.ALL.check_update(update)

    def test_filters_text(self, update):
        update.message.text = "test"
        assert filters.TEXT.check_update(update)
        update.message.text = "/test"
        assert filters.Text().check_update(update)

    def test_filters_text_strings(self, update):
        update.message.text = "/test"
        assert filters.Text(("/test", "test1")).check_update(update)
        assert not filters.Text(["test1", "test2"]).check_update(update)

    def test_filters_caption(self, update):
        update.message.caption = "test"
        assert filters.CAPTION.check_update(update)
        update.message.caption = None
        assert not filters.CAPTION.check_update(update)

    def test_filters_caption_strings(self, update):
        update.message.caption = "test"
        assert filters.Caption(("test", "test1")).check_update(update)
        assert not filters.Caption(["test1", "test2"]).check_update(update)

    def test_filters_command_default(self, update):
        update.message.text = "test"
        assert not filters.COMMAND.check_update(update)
        update.message.text = "/test"
        assert not filters.COMMAND.check_update(update)
        # Only accept commands at the beginning
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 3, 5)]
        assert not filters.COMMAND.check_update(update)
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]
        assert filters.COMMAND.check_update(update)

    def test_filters_command_anywhere(self, update):
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 5, 4)]
        assert filters.Command(False).check_update(update)

    def test_filters_regex(self, update):
        sre_type = type(re.match("", ""))
        update.message.text = "/start deep-linked param"
        result = filters.Regex(r"deep-linked param").check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert type(matches[0]) is sre_type
        update.message.text = "/help"
        assert filters.Regex(r"help").check_update(update)

        update.message.text = "test"
        assert not filters.Regex(r"fail").check_update(update)
        assert filters.Regex(r"test").check_update(update)
        assert filters.Regex(re.compile(r"test")).check_update(update)
        assert filters.Regex(re.compile(r"TEST", re.IGNORECASE)).check_update(update)

        update.message.text = "i love python"
        assert filters.Regex(r".\b[lo]{2}ve python").check_update(update)

        update.message.text = None
        assert not filters.Regex(r"fail").check_update(update)

    def test_filters_regex_multiple(self, update):
        sre_type = type(re.match("", ""))
        update.message.text = "/start deep-linked param"
        result = (filters.Regex("deep") & filters.Regex(r"linked param")).check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        result = (filters.Regex("deep") | filters.Regex(r"linked param")).check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        result = (filters.Regex("not int") | filters.Regex(r"linked param")).check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        result = (filters.Regex("not int") & filters.Regex(r"linked param")).check_update(update)
        assert not result

    def test_filters_merged_with_regex(self, update):
        sre_type = type(re.match("", ""))
        update.message.text = "/start deep-linked param"
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = (filters.COMMAND & filters.Regex(r"linked param")).check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        result = (filters.Regex(r"linked param") & filters.COMMAND).check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        result = (filters.Regex(r"linked param") | filters.COMMAND).check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        # Should not give a match since it's a or filter and it short circuits
        result = (filters.COMMAND | filters.Regex(r"linked param")).check_update(update)
        assert result is True

    def test_regex_complex_merges(self, update, message_origin_user):
        sre_type = type(re.match("", ""))
        update.message.text = "test it out"
        test_filter = filters.Regex("test") & (
            (filters.StatusUpdate.ALL | filters.AUDIO) | filters.Regex("out")
        )
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert len(matches) == 2
        assert all(type(res) is sre_type for res in matches)
        update.message.audio = "test"
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        update.message.text = "test it"
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        update.message.audio = None
        result = test_filter.check_update(update)
        assert not result
        update.message.text = "test it out"
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        update.message.pinned_message = True
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        update.message.text = "it out"
        result = test_filter.check_update(update)
        assert not result

        update.message.text = "test it out"
        update.message.forward_origin = None
        update.message.pinned_message = None
        test_filter = (filters.Regex("test") | filters.COMMAND) & (
            filters.Regex("it") | filters.StatusUpdate.ALL
        )
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert len(matches) == 2
        assert all(type(res) is sre_type for res in matches)
        update.message.text = "test"
        result = test_filter.check_update(update)
        assert not result
        update.message.pinned_message = True
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert len(matches) == 1
        assert all(type(res) is sre_type for res in matches)
        update.message.text = "nothing"
        result = test_filter.check_update(update)
        assert not result
        update.message.text = "/start"
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, bool)
        update.message.text = "/start it"
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert len(matches) == 1
        assert all(type(res) is sre_type for res in matches)

    def test_regex_inverted(self, update):
        update.message.text = "/start deep-linked param"
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]
        inv = ~filters.Regex(r"deep-linked param")
        result = inv.check_update(update)
        assert not result
        update.message.text = "not it"
        result = inv.check_update(update)
        assert result
        assert isinstance(result, bool)

        inv = ~filters.Regex("linked") & filters.COMMAND
        update.message.text = "it's linked"
        result = inv.check_update(update)
        assert not result
        update.message.text = "/start"
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = inv.check_update(update)
        assert result
        update.message.text = "/linked"
        result = inv.check_update(update)
        assert not result

        inv = ~filters.Regex("linked") | filters.COMMAND
        update.message.text = "it's linked"
        update.message.entities = []
        result = inv.check_update(update)
        assert not result
        update.message.text = "/start linked"
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = inv.check_update(update)
        assert result
        update.message.text = "/start"
        result = inv.check_update(update)
        assert result
        update.message.text = "nothig"
        update.message.entities = []
        result = inv.check_update(update)
        assert result

    def test_filters_caption_regex(self, update):
        sre_type = type(re.match("", ""))
        update.message.caption = "/start deep-linked param"
        result = filters.CaptionRegex(r"deep-linked param").check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert type(matches[0]) is sre_type
        update.message.caption = "/help"
        assert filters.CaptionRegex(r"help").check_update(update)

        update.message.caption = "test"
        assert not filters.CaptionRegex(r"fail").check_update(update)
        assert filters.CaptionRegex(r"test").check_update(update)
        assert filters.CaptionRegex(re.compile(r"test")).check_update(update)
        assert filters.CaptionRegex(re.compile(r"TEST", re.IGNORECASE)).check_update(update)

        update.message.caption = "i love python"
        assert filters.CaptionRegex(r".\b[lo]{2}ve python").check_update(update)

        update.message.caption = None
        assert not filters.CaptionRegex(r"fail").check_update(update)

    def test_filters_caption_regex_multiple(self, update):
        sre_type = type(re.match("", ""))
        update.message.caption = "/start deep-linked param"
        _and = filters.CaptionRegex("deep") & filters.CaptionRegex(r"linked param")
        result = _and.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        _or = filters.CaptionRegex("deep") | filters.CaptionRegex(r"linked param")
        result = _or.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        _or = filters.CaptionRegex("not int") | filters.CaptionRegex(r"linked param")
        result = _or.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        _and = filters.CaptionRegex("not int") & filters.CaptionRegex(r"linked param")
        result = _and.check_update(update)
        assert not result

    def test_filters_merged_with_caption_regex(self, update):
        sre_type = type(re.match("", ""))
        update.message.caption = "/start deep-linked param"
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = (filters.COMMAND & filters.CaptionRegex(r"linked param")).check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        result = (filters.CaptionRegex(r"linked param") & filters.COMMAND).check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        result = (filters.CaptionRegex(r"linked param") | filters.COMMAND).check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        # Should not give a match since it's a or filter and it short circuits
        result = (filters.COMMAND | filters.CaptionRegex(r"linked param")).check_update(update)
        assert result is True

    def test_caption_regex_complex_merges(self, update, message_origin_user):
        sre_type = type(re.match("", ""))
        update.message.caption = "test it out"
        test_filter = filters.CaptionRegex("test") & (
            (filters.StatusUpdate.ALL | filters.AUDIO) | filters.CaptionRegex("out")
        )
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert len(matches) == 2
        assert all(type(res) is sre_type for res in matches)
        update.message.audio = "test"
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        update.message.caption = "test it"
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        update.message.audio = None
        result = test_filter.check_update(update)
        assert not result
        update.message.caption = "test it out"
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        update.message.pinned_message = True
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert all(type(res) is sre_type for res in matches)
        update.message.caption = "it out"
        result = test_filter.check_update(update)
        assert not result

        update.message.caption = "test it out"
        update.message.forward_origin = None
        update.message.pinned_message = None
        test_filter = (filters.CaptionRegex("test") | filters.COMMAND) & (
            filters.CaptionRegex("it") | filters.StatusUpdate.ALL
        )
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert len(matches) == 2
        assert all(type(res) is sre_type for res in matches)
        update.message.caption = "test"
        result = test_filter.check_update(update)
        assert not result
        update.message.pinned_message = True
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert len(matches) == 1
        assert all(type(res) is sre_type for res in matches)
        update.message.caption = "nothing"
        result = test_filter.check_update(update)
        assert not result
        update.message.caption = "/start"
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, bool)
        update.message.caption = "/start it"
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert len(matches) == 1
        assert all(type(res) is sre_type for res in matches)

    def test_caption_regex_inverted(self, update):
        update.message.caption = "/start deep-linked param"
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]
        test_filter = ~filters.CaptionRegex(r"deep-linked param")
        result = test_filter.check_update(update)
        assert not result
        update.message.caption = "not it"
        result = test_filter.check_update(update)
        assert result
        assert isinstance(result, bool)

        test_filter = ~filters.CaptionRegex("linked") & filters.COMMAND
        update.message.caption = "it's linked"
        result = test_filter.check_update(update)
        assert not result
        update.message.caption = "/start"
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = test_filter.check_update(update)
        assert result
        update.message.caption = "/linked"
        result = test_filter.check_update(update)
        assert not result

        test_filter = ~filters.CaptionRegex("linked") | filters.COMMAND
        update.message.caption = "it's linked"
        update.message.entities = []
        result = test_filter.check_update(update)
        assert not result
        update.message.caption = "/start linked"
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)]
        result = test_filter.check_update(update)
        assert result
        update.message.caption = "/start"
        result = test_filter.check_update(update)
        assert result
        update.message.caption = "nothig"
        update.message.entities = []
        result = test_filter.check_update(update)
        assert result

    def test_filters_reply(self, update):
        another_message = Message(
            1,
            datetime.datetime.utcnow(),
            Chat(0, "private"),
            from_user=User(1, "TestOther", False),
        )
        update.message.text = "test"
        assert not filters.REPLY.check_update(update)
        update.message.reply_to_message = another_message
        assert filters.REPLY.check_update(update)

    def test_filters_audio(self, update):
        assert not filters.AUDIO.check_update(update)
        update.message.audio = "test"
        assert filters.AUDIO.check_update(update)

    def test_filters_document(self, update):
        assert not filters.Document.ALL.check_update(update)
        update.message.document = "test"
        assert filters.Document.ALL.check_update(update)

    def test_filters_document_type(self, update):
        update.message.document = Document(
            "file_id", "unique_id", mime_type="application/vnd.android.package-archive"
        )
        update.message.document._unfreeze()
        assert filters.Document.APK.check_update(update)
        assert filters.Document.APPLICATION.check_update(update)
        assert not filters.Document.DOC.check_update(update)
        assert not filters.Document.AUDIO.check_update(update)

        update.message.document.mime_type = "application/msword"
        assert filters.Document.DOC.check_update(update)
        assert filters.Document.APPLICATION.check_update(update)
        assert not filters.Document.DOCX.check_update(update)
        assert not filters.Document.AUDIO.check_update(update)

        update.message.document.mime_type = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        assert filters.Document.DOCX.check_update(update)
        assert filters.Document.APPLICATION.check_update(update)
        assert not filters.Document.EXE.check_update(update)
        assert not filters.Document.AUDIO.check_update(update)

        update.message.document.mime_type = "application/octet-stream"
        assert filters.Document.EXE.check_update(update)
        assert filters.Document.APPLICATION.check_update(update)
        assert not filters.Document.DOCX.check_update(update)
        assert not filters.Document.AUDIO.check_update(update)

        update.message.document.mime_type = "image/gif"
        assert filters.Document.GIF.check_update(update)
        assert filters.Document.IMAGE.check_update(update)
        assert not filters.Document.JPG.check_update(update)
        assert not filters.Document.TEXT.check_update(update)

        update.message.document.mime_type = "image/jpeg"
        assert filters.Document.JPG.check_update(update)
        assert filters.Document.IMAGE.check_update(update)
        assert not filters.Document.MP3.check_update(update)
        assert not filters.Document.VIDEO.check_update(update)

        update.message.document.mime_type = "audio/mpeg"
        assert filters.Document.MP3.check_update(update)
        assert filters.Document.AUDIO.check_update(update)
        assert not filters.Document.PDF.check_update(update)
        assert not filters.Document.IMAGE.check_update(update)

        update.message.document.mime_type = "application/pdf"
        assert filters.Document.PDF.check_update(update)
        assert filters.Document.APPLICATION.check_update(update)
        assert not filters.Document.PY.check_update(update)
        assert not filters.Document.AUDIO.check_update(update)

        update.message.document.mime_type = "text/x-python"
        assert filters.Document.PY.check_update(update)
        assert filters.Document.TEXT.check_update(update)
        assert not filters.Document.SVG.check_update(update)
        assert not filters.Document.APPLICATION.check_update(update)

        update.message.document.mime_type = "image/svg+xml"
        assert filters.Document.SVG.check_update(update)
        assert filters.Document.IMAGE.check_update(update)
        assert not filters.Document.TXT.check_update(update)
        assert not filters.Document.VIDEO.check_update(update)

        update.message.document.mime_type = "text/plain"
        assert filters.Document.TXT.check_update(update)
        assert filters.Document.TEXT.check_update(update)
        assert not filters.Document.TARGZ.check_update(update)
        assert not filters.Document.APPLICATION.check_update(update)

        update.message.document.mime_type = "application/x-compressed-tar"
        assert filters.Document.TARGZ.check_update(update)
        assert filters.Document.APPLICATION.check_update(update)
        assert not filters.Document.WAV.check_update(update)
        assert not filters.Document.AUDIO.check_update(update)

        update.message.document.mime_type = "audio/x-wav"
        assert filters.Document.WAV.check_update(update)
        assert filters.Document.AUDIO.check_update(update)
        assert not filters.Document.XML.check_update(update)
        assert not filters.Document.IMAGE.check_update(update)

        update.message.document.mime_type = "text/xml"
        assert filters.Document.XML.check_update(update)
        assert filters.Document.TEXT.check_update(update)
        assert not filters.Document.ZIP.check_update(update)
        assert not filters.Document.AUDIO.check_update(update)

        update.message.document.mime_type = "application/zip"
        assert filters.Document.ZIP.check_update(update)
        assert filters.Document.APPLICATION.check_update(update)
        assert not filters.Document.APK.check_update(update)
        assert not filters.Document.AUDIO.check_update(update)

        update.message.document.mime_type = "image/x-rgb"
        assert not filters.Document.Category("application/").check_update(update)
        assert not filters.Document.MimeType("application/x-sh").check_update(update)
        update.message.document.mime_type = "application/x-sh"
        assert filters.Document.Category("application/").check_update(update)
        assert filters.Document.MimeType("application/x-sh").check_update(update)

        update.message.document.mime_type = None
        assert not filters.Document.Category("application/").check_update(update)
        assert not filters.Document.MimeType("application/x-sh").check_update(update)

    def test_filters_file_extension_basic(self, update):
        update.message.document = Document(
            "file_id",
            "unique_id",
            file_name="file.jpg",
            mime_type="image/jpeg",
        )
        update.message.document._unfreeze()
        assert filters.Document.FileExtension("jpg").check_update(update)
        assert not filters.Document.FileExtension("jpeg").check_update(update)
        assert not filters.Document.FileExtension("file.jpg").check_update(update)

        update.message.document.file_name = "file.tar.gz"
        assert filters.Document.FileExtension("tar.gz").check_update(update)
        assert filters.Document.FileExtension("gz").check_update(update)
        assert not filters.Document.FileExtension("tgz").check_update(update)
        assert not filters.Document.FileExtension("jpg").check_update(update)

        update.message.document.file_name = None
        assert not filters.Document.FileExtension("jpg").check_update(update)

        update.message.document = None
        assert not filters.Document.FileExtension("jpg").check_update(update)

    def test_filters_file_extension_minds_dots(self, update):
        update.message.document = Document(
            "file_id",
            "unique_id",
            file_name="file.jpg",
            mime_type="image/jpeg",
        )
        update.message.document._unfreeze()
        assert not filters.Document.FileExtension(".jpg").check_update(update)
        assert not filters.Document.FileExtension("e.jpg").check_update(update)
        assert not filters.Document.FileExtension("file.jpg").check_update(update)
        assert not filters.Document.FileExtension("").check_update(update)

        update.message.document.file_name = "file..jpg"
        assert filters.Document.FileExtension("jpg").check_update(update)
        assert filters.Document.FileExtension(".jpg").check_update(update)
        assert not filters.Document.FileExtension("..jpg").check_update(update)

        update.message.document.file_name = "file.docx"
        assert filters.Document.FileExtension("docx").check_update(update)
        assert not filters.Document.FileExtension("doc").check_update(update)
        assert not filters.Document.FileExtension("ocx").check_update(update)

        update.message.document.file_name = "file"
        assert not filters.Document.FileExtension("").check_update(update)
        assert not filters.Document.FileExtension("file").check_update(update)

        update.message.document.file_name = "file."
        assert filters.Document.FileExtension("").check_update(update)

    def test_filters_file_extension_none_arg(self, update):
        update.message.document = Document(
            "file_id",
            "unique_id",
            file_name="file.jpg",
            mime_type="image/jpeg",
        )
        update.message.document._unfreeze()
        assert not filters.Document.FileExtension(None).check_update(update)

        update.message.document.file_name = "file"
        assert filters.Document.FileExtension(None).check_update(update)
        assert not filters.Document.FileExtension("None").check_update(update)

        update.message.document.file_name = "file."
        assert not filters.Document.FileExtension(None).check_update(update)

        update.message.document = None
        assert not filters.Document.FileExtension(None).check_update(update)

    def test_filters_file_extension_case_sensitivity(self, update):
        update.message.document = Document(
            "file_id",
            "unique_id",
            file_name="file.jpg",
            mime_type="image/jpeg",
        )
        update.message.document._unfreeze()
        assert filters.Document.FileExtension("JPG").check_update(update)
        assert filters.Document.FileExtension("jpG").check_update(update)

        update.message.document.file_name = "file.JPG"
        assert filters.Document.FileExtension("jpg").check_update(update)
        assert not filters.Document.FileExtension("jpg", case_sensitive=True).check_update(update)

        update.message.document.file_name = "file.Dockerfile"
        assert filters.Document.FileExtension("Dockerfile", case_sensitive=True).check_update(
            update
        )
        assert not filters.Document.FileExtension("DOCKERFILE", case_sensitive=True).check_update(
            update
        )

    def test_filters_file_extension_name(self):
        assert (
            filters.Document.FileExtension("jpg").name == "filters.Document.FileExtension('jpg')"
        )
        assert (
            filters.Document.FileExtension("JPG").name == "filters.Document.FileExtension('jpg')"
        )
        assert (
            filters.Document.FileExtension("jpg", case_sensitive=True).name
            == "filters.Document.FileExtension('jpg', case_sensitive=True)"
        )
        assert (
            filters.Document.FileExtension("JPG", case_sensitive=True).name
            == "filters.Document.FileExtension('JPG', case_sensitive=True)"
        )
        assert (
            filters.Document.FileExtension(".jpg").name == "filters.Document.FileExtension('.jpg')"
        )
        assert filters.Document.FileExtension("").name == "filters.Document.FileExtension('')"
        assert filters.Document.FileExtension(None).name == "filters.Document.FileExtension(None)"

    def test_filters_animation(self, update):
        assert not filters.ANIMATION.check_update(update)
        update.message.animation = "test"
        assert filters.ANIMATION.check_update(update)

    def test_filters_photo(self, update):
        assert not filters.PHOTO.check_update(update)
        update.message.photo = "test"
        assert filters.PHOTO.check_update(update)

    def test_filters_sticker(self, update):
        assert not filters.Sticker.ALL.check_update(update)
        update.message.sticker = Sticker("1", "uniq", 1, 2, False, False, Sticker.REGULAR)
        update.message.sticker._unfreeze()
        assert filters.Sticker.ALL.check_update(update)
        assert filters.Sticker.STATIC.check_update(update)
        assert not filters.Sticker.VIDEO.check_update(update)
        assert not filters.Sticker.PREMIUM.check_update(update)
        update.message.sticker.is_animated = True
        assert filters.Sticker.ANIMATED.check_update(update)
        assert not filters.Sticker.VIDEO.check_update(update)
        assert not filters.Sticker.STATIC.check_update(update)
        assert not filters.Sticker.PREMIUM.check_update(update)
        update.message.sticker.is_animated = False
        update.message.sticker.is_video = True
        assert not filters.Sticker.ANIMATED.check_update(update)
        assert not filters.Sticker.STATIC.check_update(update)
        assert filters.Sticker.VIDEO.check_update(update)
        assert not filters.Sticker.PREMIUM.check_update(update)
        update.message.sticker.premium_animation = File("string", "uniqueString")
        assert not filters.Sticker.ANIMATED.check_update(update)
        # premium stickers can be animated, video, or probably also static,
        # it doesn't really matter for the test
        assert not filters.Sticker.STATIC.check_update(update)
        assert filters.Sticker.VIDEO.check_update(update)
        assert filters.Sticker.PREMIUM.check_update(update)

    def test_filters_story(self, update):
        assert not filters.STORY.check_update(update)
        update.message.story = "test"
        assert filters.STORY.check_update(update)

    def test_filters_video(self, update):
        assert not filters.VIDEO.check_update(update)
        update.message.video = "test"
        assert filters.VIDEO.check_update(update)

    def test_filters_voice(self, update):
        assert not filters.VOICE.check_update(update)
        update.message.voice = "test"
        assert filters.VOICE.check_update(update)

    def test_filters_video_note(self, update):
        assert not filters.VIDEO_NOTE.check_update(update)
        update.message.video_note = "test"
        assert filters.VIDEO_NOTE.check_update(update)

    def test_filters_contact(self, update):
        assert not filters.CONTACT.check_update(update)
        update.message.contact = "test"
        assert filters.CONTACT.check_update(update)

    def test_filters_location(self, update):
        assert not filters.LOCATION.check_update(update)
        update.message.location = "test"
        assert filters.LOCATION.check_update(update)

    def test_filters_venue(self, update):
        assert not filters.VENUE.check_update(update)
        update.message.venue = "test"
        assert filters.VENUE.check_update(update)

    def test_filters_status_update(self, update):
        assert not filters.StatusUpdate.ALL.check_update(update)

        update.message.new_chat_members = ["test"]
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.NEW_CHAT_MEMBERS.check_update(update)
        update.message.new_chat_members = None

        update.message.left_chat_member = "test"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.LEFT_CHAT_MEMBER.check_update(update)
        update.message.left_chat_member = None

        update.message.new_chat_title = "test"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.NEW_CHAT_TITLE.check_update(update)
        update.message.new_chat_title = ""

        update.message.new_chat_photo = "test"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.NEW_CHAT_PHOTO.check_update(update)
        update.message.new_chat_photo = None

        update.message.delete_chat_photo = True
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.DELETE_CHAT_PHOTO.check_update(update)
        update.message.delete_chat_photo = False

        update.message.group_chat_created = True
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.CHAT_CREATED.check_update(update)
        update.message.group_chat_created = False

        update.message.supergroup_chat_created = True
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.CHAT_CREATED.check_update(update)
        update.message.supergroup_chat_created = False

        update.message.channel_chat_created = True
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.CHAT_CREATED.check_update(update)
        update.message.channel_chat_created = False

        update.message.message_auto_delete_timer_changed = True
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.MESSAGE_AUTO_DELETE_TIMER_CHANGED.check_update(update)
        update.message.message_auto_delete_timer_changed = False

        update.message.migrate_to_chat_id = 100
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.MIGRATE.check_update(update)
        update.message.migrate_to_chat_id = 0

        update.message.migrate_from_chat_id = 100
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.MIGRATE.check_update(update)
        update.message.migrate_from_chat_id = 0

        update.message.pinned_message = "test"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.PINNED_MESSAGE.check_update(update)
        update.message.pinned_message = None

        update.message.connected_website = "https://example.com/"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.CONNECTED_WEBSITE.check_update(update)
        update.message.connected_website = None

        update.message.proximity_alert_triggered = "alert"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.PROXIMITY_ALERT_TRIGGERED.check_update(update)
        update.message.proximity_alert_triggered = None

        update.message.video_chat_scheduled = "scheduled"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.VIDEO_CHAT_SCHEDULED.check_update(update)
        update.message.video_chat_scheduled = None

        update.message.video_chat_started = "hello"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.VIDEO_CHAT_STARTED.check_update(update)
        update.message.video_chat_started = None

        update.message.video_chat_ended = "bye"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.VIDEO_CHAT_ENDED.check_update(update)
        update.message.video_chat_ended = None

        update.message.video_chat_participants_invited = "invited"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.VIDEO_CHAT_PARTICIPANTS_INVITED.check_update(update)
        update.message.video_chat_participants_invited = None

        update.message.web_app_data = "data"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.WEB_APP_DATA.check_update(update)
        update.message.web_app_data = None

        update.message.forum_topic_created = "topic"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.FORUM_TOPIC_CREATED.check_update(update)
        update.message.forum_topic_created = None

        update.message.forum_topic_closed = "topic"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.FORUM_TOPIC_CLOSED.check_update(update)
        update.message.forum_topic_closed = None

        update.message.forum_topic_reopened = "topic"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.FORUM_TOPIC_REOPENED.check_update(update)
        update.message.forum_topic_reopened = None

        update.message.forum_topic_edited = "topic_edited"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.FORUM_TOPIC_EDITED.check_update(update)
        update.message.forum_topic_edited = None

        update.message.general_forum_topic_hidden = "topic_hidden"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.GENERAL_FORUM_TOPIC_HIDDEN.check_update(update)
        update.message.general_forum_topic_hidden = None

        update.message.general_forum_topic_unhidden = "topic_unhidden"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.GENERAL_FORUM_TOPIC_UNHIDDEN.check_update(update)
        update.message.general_forum_topic_unhidden = None

        update.message.write_access_allowed = "allowed"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.WRITE_ACCESS_ALLOWED.check_update(update)
        update.message.write_access_allowed = None

        update.message.api_kwargs = {"user_shared": "user_shared"}
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.USER_SHARED.check_update(update)
        update.message.api_kwargs = {}

        update.message.users_shared = "users_shared"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.USERS_SHARED.check_update(update)
        update.message.users_shared = None

        update.message.chat_shared = "user_shared"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.CHAT_SHARED.check_update(update)
        update.message.chat_shared = None

        update.message.giveaway_created = "giveaway_created"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.GIVEAWAY_CREATED.check_update(update)
        update.message.giveaway_created = None

        update.message.giveaway_completed = "giveaway_completed"
        assert filters.StatusUpdate.ALL.check_update(update)
        assert filters.StatusUpdate.GIVEAWAY_COMPLETED.check_update(update)
        update.message.giveaway_completed = None

    def test_filters_forwarded(self, update, message_origin_user):
        assert filters.FORWARDED.check_update(update)
        update.message.forward_origin = MessageOriginHiddenUser(datetime.datetime.utcnow(), 1)
        assert filters.FORWARDED.check_update(update)
        update.message.forward_origin = None
        assert not filters.FORWARDED.check_update(update)

    def test_filters_game(self, update):
        assert not filters.GAME.check_update(update)
        update.message.game = "test"
        assert filters.GAME.check_update(update)

    def test_entities_filter(self, update, message_entity):
        update.message.entities = [message_entity]
        assert filters.Entity(message_entity.type).check_update(update)

        update.message.entities = []
        assert not filters.Entity(MessageEntity.MENTION).check_update(update)

        second = message_entity.to_dict()
        second["type"] = "bold"
        second = MessageEntity.de_json(second, None)
        update.message.entities = [message_entity, second]
        assert filters.Entity(message_entity.type).check_update(update)
        assert not filters.CaptionEntity(message_entity.type).check_update(update)

    def test_caption_entities_filter(self, update, message_entity):
        update.message.caption_entities = [message_entity]
        assert filters.CaptionEntity(message_entity.type).check_update(update)

        update.message.caption_entities = []
        assert not filters.CaptionEntity(MessageEntity.MENTION).check_update(update)

        second = message_entity.to_dict()
        second["type"] = "bold"
        second = MessageEntity.de_json(second, None)
        update.message.caption_entities = [message_entity, second]
        assert filters.CaptionEntity(message_entity.type).check_update(update)
        assert not filters.Entity(message_entity.type).check_update(update)

    @pytest.mark.parametrize(
        ("chat_type", "results"),
        [
            (Chat.PRIVATE, (True, False, False, False, False)),
            (Chat.GROUP, (False, True, False, True, False)),
            (Chat.SUPERGROUP, (False, False, True, True, False)),
            (Chat.CHANNEL, (False, False, False, False, True)),
        ],
    )
    def test_filters_chat_types(self, update, chat_type, results):
        update.message.chat.type = chat_type
        assert filters.ChatType.PRIVATE.check_update(update) is results[0]
        assert filters.ChatType.GROUP.check_update(update) is results[1]
        assert filters.ChatType.SUPERGROUP.check_update(update) is results[2]
        assert filters.ChatType.GROUPS.check_update(update) is results[3]
        assert filters.ChatType.CHANNEL.check_update(update) is results[4]

    def test_filters_user_init(self):
        with pytest.raises(RuntimeError, match="in conjunction with"):
            filters.User(user_id=1, username="user")

    def test_filters_user_allow_empty(self, update):
        assert not filters.User().check_update(update)
        assert filters.User(allow_empty=True).check_update(update)

    def test_filters_user_id(self, update):
        assert not filters.User(user_id=1).check_update(update)
        update.message.from_user.id = 1
        assert filters.User(user_id=1).check_update(update)
        assert filters.USER.check_update(update)
        update.message.from_user.id = 2
        assert filters.User(user_id=[1, 2]).check_update(update)
        assert not filters.User(user_id=[3, 4]).check_update(update)
        update.message.from_user = None
        assert not filters.USER.check_update(update)
        assert not filters.User(user_id=[3, 4]).check_update(update)

    def test_filters_username(self, update):
        assert not filters.User(username="user").check_update(update)
        assert not filters.User(username="Testuser").check_update(update)
        update.message.from_user.username = "user@"
        assert filters.User(username="@user@").check_update(update)
        assert filters.User(username="user@").check_update(update)
        assert filters.User(username=["user1", "user@", "user2"]).check_update(update)
        assert not filters.User(username=["@username", "@user_2"]).check_update(update)
        update.message.from_user = None
        assert not filters.User(username=["@username", "@user_2"]).check_update(update)

    def test_filters_user_change_id(self, update):
        f = filters.User(user_id=1)
        assert f.user_ids == {1}
        update.message.from_user.id = 1
        assert f.check_update(update)
        update.message.from_user.id = 2
        assert not f.check_update(update)
        f.user_ids = 2
        assert f.user_ids == {2}
        assert f.check_update(update)

        with pytest.raises(RuntimeError, match="username in conjunction"):
            f.usernames = "user"

    def test_filters_user_change_username(self, update):
        f = filters.User(username="user")
        update.message.from_user.username = "user"
        assert f.check_update(update)
        update.message.from_user.username = "User"
        assert not f.check_update(update)
        f.usernames = "User"
        assert f.check_update(update)

        with pytest.raises(RuntimeError, match="user_id in conjunction"):
            f.user_ids = 1

    def test_filters_user_add_user_by_name(self, update):
        users = ["user_a", "user_b", "user_c"]
        f = filters.User()

        for user in users:
            update.message.from_user.username = user
            assert not f.check_update(update)

        f.add_usernames("user_a")
        f.add_usernames(["user_b", "user_c"])

        for user in users:
            update.message.from_user.username = user
            assert f.check_update(update)

        with pytest.raises(RuntimeError, match="user_id in conjunction"):
            f.add_user_ids(1)

    def test_filters_user_add_user_by_id(self, update):
        users = [1, 2, 3]
        f = filters.User()

        for user in users:
            update.message.from_user.id = user
            assert not f.check_update(update)

        f.add_user_ids(1)
        f.add_user_ids([2, 3])

        for user in users:
            update.message.from_user.username = user
            assert f.check_update(update)

        with pytest.raises(RuntimeError, match="username in conjunction"):
            f.add_usernames("user")

    def test_filters_user_remove_user_by_name(self, update):
        users = ["user_a", "user_b", "user_c"]
        f = filters.User(username=users)

        with pytest.raises(RuntimeError, match="user_id in conjunction"):
            f.remove_user_ids(1)

        for user in users:
            update.message.from_user.username = user
            assert f.check_update(update)

        f.remove_usernames("user_a")
        f.remove_usernames(["user_b", "user_c"])

        for user in users:
            update.message.from_user.username = user
            assert not f.check_update(update)

    def test_filters_user_remove_user_by_id(self, update):
        users = [1, 2, 3]
        f = filters.User(user_id=users)

        with pytest.raises(RuntimeError, match="username in conjunction"):
            f.remove_usernames("user")

        for user in users:
            update.message.from_user.id = user
            assert f.check_update(update)

        f.remove_user_ids(1)
        f.remove_user_ids([2, 3])

        for user in users:
            update.message.from_user.username = user
            assert not f.check_update(update)

    def test_filters_user_repr(self):
        f = filters.User([1, 2])
        assert str(f) == "filters.User(1, 2)"
        f.remove_user_ids(1)
        f.remove_user_ids(2)
        assert str(f) == "filters.User()"
        f.add_usernames("@foobar")
        assert str(f) == "filters.User(foobar)"
        f.add_usernames("@barfoo")
        assert str(f).startswith("filters.User(")
        # we don't know th exact order
        assert "barfoo" in str(f)
        assert "foobar" in str(f)

        with pytest.raises(RuntimeError, match="Cannot set name"):
            f.name = "foo"

    def test_filters_user_attributes(self, update):
        assert not filters.USER_ATTACHMENT.check_update(update)
        assert not filters.PREMIUM_USER.check_update(update)
        update.message.from_user.added_to_attachment_menu = True
        assert filters.USER_ATTACHMENT.check_update(update)
        assert not filters.PREMIUM_USER.check_update(update)
        update.message.from_user.is_premium = True
        assert filters.USER_ATTACHMENT.check_update(update)
        assert filters.PREMIUM_USER.check_update(update)
        update.message.from_user.added_to_attachment_menu = False
        assert not filters.USER_ATTACHMENT.check_update(update)
        assert filters.PREMIUM_USER.check_update(update)

    def test_filters_chat_init(self):
        with pytest.raises(RuntimeError, match="in conjunction with"):
            filters.Chat(chat_id=1, username="chat")

    def test_filters_chat_allow_empty(self, update):
        assert not filters.Chat().check_update(update)
        assert filters.Chat(allow_empty=True).check_update(update)

    def test_filters_chat_id(self, update):
        assert not filters.Chat(chat_id=1).check_update(update)
        assert filters.CHAT.check_update(update)
        update.message.chat.id = 1
        assert filters.Chat(chat_id=1).check_update(update)
        assert filters.CHAT.check_update(update)
        update.message.chat.id = 2
        assert filters.Chat(chat_id=[1, 2]).check_update(update)
        assert not filters.Chat(chat_id=[3, 4]).check_update(update)
        update.message.chat = None
        assert not filters.CHAT.check_update(update)
        assert not filters.Chat(chat_id=[3, 4]).check_update(update)

    def test_filters_chat_username(self, update):
        assert not filters.Chat(username="chat").check_update(update)
        assert not filters.Chat(username="Testchat").check_update(update)
        update.message.chat.username = "chat@"
        assert filters.Chat(username="@chat@").check_update(update)
        assert filters.Chat(username="chat@").check_update(update)
        assert filters.Chat(username=["chat1", "chat@", "chat2"]).check_update(update)
        assert not filters.Chat(username=["@username", "@chat_2"]).check_update(update)
        update.message.chat = None
        assert not filters.Chat(username=["@username", "@chat_2"]).check_update(update)

    def test_filters_chat_change_id(self, update):
        f = filters.Chat(chat_id=1)
        assert f.chat_ids == {1}
        update.message.chat.id = 1
        assert f.check_update(update)
        update.message.chat.id = 2
        assert not f.check_update(update)
        f.chat_ids = 2
        assert f.chat_ids == {2}
        assert f.check_update(update)

        with pytest.raises(RuntimeError, match="username in conjunction"):
            f.usernames = "chat"

    def test_filters_chat_change_username(self, update):
        f = filters.Chat(username="chat")
        update.message.chat.username = "chat"
        assert f.check_update(update)
        update.message.chat.username = "User"
        assert not f.check_update(update)
        f.usernames = "User"
        assert f.check_update(update)

        with pytest.raises(RuntimeError, match="chat_id in conjunction"):
            f.chat_ids = 1

    def test_filters_chat_add_chat_by_name(self, update):
        chats = ["chat_a", "chat_b", "chat_c"]
        f = filters.Chat()

        for chat in chats:
            update.message.chat.username = chat
            assert not f.check_update(update)

        f.add_usernames("chat_a")
        f.add_usernames(["chat_b", "chat_c"])

        for chat in chats:
            update.message.chat.username = chat
            assert f.check_update(update)

        with pytest.raises(RuntimeError, match="chat_id in conjunction"):
            f.add_chat_ids(1)

    def test_filters_chat_add_chat_by_id(self, update):
        chats = [1, 2, 3]
        f = filters.Chat()

        for chat in chats:
            update.message.chat.id = chat
            assert not f.check_update(update)

        f.add_chat_ids(1)
        f.add_chat_ids([2, 3])

        for chat in chats:
            update.message.chat.username = chat
            assert f.check_update(update)

        with pytest.raises(RuntimeError, match="username in conjunction"):
            f.add_usernames("chat")

    def test_filters_chat_remove_chat_by_name(self, update):
        chats = ["chat_a", "chat_b", "chat_c"]
        f = filters.Chat(username=chats)

        with pytest.raises(RuntimeError, match="chat_id in conjunction"):
            f.remove_chat_ids(1)

        for chat in chats:
            update.message.chat.username = chat
            assert f.check_update(update)

        f.remove_usernames("chat_a")
        f.remove_usernames(["chat_b", "chat_c"])

        for chat in chats:
            update.message.chat.username = chat
            assert not f.check_update(update)

    def test_filters_chat_remove_chat_by_id(self, update):
        chats = [1, 2, 3]
        f = filters.Chat(chat_id=chats)

        with pytest.raises(RuntimeError, match="username in conjunction"):
            f.remove_usernames("chat")

        for chat in chats:
            update.message.chat.id = chat
            assert f.check_update(update)

        f.remove_chat_ids(1)
        f.remove_chat_ids([2, 3])

        for chat in chats:
            update.message.chat.username = chat
            assert not f.check_update(update)

    def test_filters_chat_repr(self):
        f = filters.Chat([1, 2])
        assert str(f) == "filters.Chat(1, 2)"
        f.remove_chat_ids(1)
        f.remove_chat_ids(2)
        assert str(f) == "filters.Chat()"
        f.add_usernames("@foobar")
        assert str(f) == "filters.Chat(foobar)"
        f.add_usernames("@barfoo")
        assert str(f).startswith("filters.Chat(")
        # we don't know th exact order
        assert "barfoo" in str(f)
        assert "foobar" in str(f)

        with pytest.raises(RuntimeError, match="Cannot set name"):
            f.name = "foo"

    def test_filters_forwarded_from_init(self):
        with pytest.raises(RuntimeError, match="in conjunction with"):
            filters.ForwardedFrom(chat_id=1, username="chat")

    def test_filters_forwarded_from_allow_empty(self, update):
        assert not filters.ForwardedFrom().check_update(update)
        assert filters.ForwardedFrom(allow_empty=True).check_update(update)

        update.message.forward_origin = MessageOriginHiddenUser(date=1, sender_user_name="test")
        assert not filters.ForwardedFrom(allow_empty=True).check_update(update)

    def test_filters_forwarded_from_id(self, update):
        # Test with User id-
        assert not filters.ForwardedFrom(chat_id=1).check_update(update)
        update.message.forward_origin.sender_user.id = 1
        assert filters.ForwardedFrom(chat_id=1).check_update(update)
        update.message.forward_origin.sender_user.id = 2
        assert filters.ForwardedFrom(chat_id=[1, 2]).check_update(update)
        assert not filters.ForwardedFrom(chat_id=[3, 4]).check_update(update)
        update.message.forward_origin = None
        assert not filters.ForwardedFrom(chat_id=[3, 4]).check_update(update)

        # Test with Chat id-
        update.message.forward_origin = MessageOriginChat(date=1, sender_chat=Chat(4, "test"))
        assert filters.ForwardedFrom(chat_id=[4]).check_update(update)
        assert filters.ForwardedFrom(chat_id=[3, 4]).check_update(update)

        update.message.forward_origin = MessageOriginChat(date=1, sender_chat=Chat(2, "test"))
        assert not filters.ForwardedFrom(chat_id=[3, 4]).check_update(update)
        assert filters.ForwardedFrom(chat_id=2).check_update(update)

        # Test with Channel id-
        update.message.forward_origin = MessageOriginChannel(
            date=1, chat=Chat(4, "test"), message_id=1
        )
        assert filters.ForwardedFrom(chat_id=[4]).check_update(update)
        assert filters.ForwardedFrom(chat_id=[3, 4]).check_update(update)

        update.message.forward_origin = MessageOriginChannel(
            date=1, chat=Chat(2, "test"), message_id=1
        )
        assert not filters.ForwardedFrom(chat_id=[3, 4]).check_update(update)
        assert filters.ForwardedFrom(chat_id=2).check_update(update)
        update.message.forward_origin = None

    def test_filters_forwarded_from_username(self, update):
        # For User username
        assert not filters.ForwardedFrom(username="chat").check_update(update)
        assert not filters.ForwardedFrom(username="Testchat").check_update(update)
        update.message.forward_origin.sender_user.username = "chat@"
        assert filters.ForwardedFrom(username="@chat@").check_update(update)
        assert filters.ForwardedFrom(username="chat@").check_update(update)
        assert filters.ForwardedFrom(username=["chat1", "chat@", "chat2"]).check_update(update)
        assert not filters.ForwardedFrom(username=["@username", "@chat_2"]).check_update(update)
        update.message.forward_origin = None
        assert not filters.ForwardedFrom(username=["@username", "@chat_2"]).check_update(update)

        # For Chat username
        assert not filters.ForwardedFrom(username="chat").check_update(update)
        assert not filters.ForwardedFrom(username="Testchat").check_update(update)
        update.message.forward_origin = MessageOriginChat(
            date=1, sender_chat=Chat(4, username="chat@", type=Chat.SUPERGROUP)
        )
        assert filters.ForwardedFrom(username="@chat@").check_update(update)
        assert filters.ForwardedFrom(username="chat@").check_update(update)
        assert filters.ForwardedFrom(username=["chat1", "chat@", "chat2"]).check_update(update)
        assert not filters.ForwardedFrom(username=["@username", "@chat_2"]).check_update(update)
        update.message.forward_origin = None
        assert not filters.ForwardedFrom(username=["@username", "@chat_2"]).check_update(update)

        # For Channel username
        assert not filters.ForwardedFrom(username="chat").check_update(update)
        assert not filters.ForwardedFrom(username="Testchat").check_update(update)
        update.message.forward_origin = MessageOriginChannel(
            date=1, chat=Chat(4, username="chat@", type=Chat.SUPERGROUP), message_id=1
        )
        assert filters.ForwardedFrom(username="@chat@").check_update(update)
        assert filters.ForwardedFrom(username="chat@").check_update(update)
        assert filters.ForwardedFrom(username=["chat1", "chat@", "chat2"]).check_update(update)
        assert not filters.ForwardedFrom(username=["@username", "@chat_2"]).check_update(update)
        update.message.forward_origin = None
        assert not filters.ForwardedFrom(username=["@username", "@chat_2"]).check_update(update)

    def test_filters_forwarded_from_change_id(self, update):
        f = filters.ForwardedFrom(chat_id=1)
        # For User ids-
        assert f.chat_ids == {1}
        update.message.forward_origin.sender_user.id = 1
        assert f.check_update(update)
        update.message.forward_origin.sender_user.id = 2
        assert not f.check_update(update)
        f.chat_ids = 2
        assert f.chat_ids == {2}
        assert f.check_update(update)

        # For Chat ids-
        f = filters.ForwardedFrom(chat_id=1)  # reset this
        # and change this to None, only one of them can be True
        update.message.forward_origin = None
        assert f.chat_ids == {1}
        update.message.forward_origin = MessageOriginChat(date=1, sender_chat=Chat(1, "test"))
        assert f.check_update(update)
        update.message.forward_origin = MessageOriginChat(date=1, sender_chat=Chat(2, "test"))
        assert not f.check_update(update)
        f.chat_ids = 2
        assert f.chat_ids == {2}
        assert f.check_update(update)

        # For Channel ids-
        f = filters.ForwardedFrom(chat_id=1)  # reset this
        # and change this to None, only one of them can be True
        update.message.forward_origin = None
        assert f.chat_ids == {1}
        update.message.forward_origin = MessageOriginChannel(
            date=1, chat=Chat(1, "test"), message_id=1
        )
        assert f.check_update(update)
        update.message.forward_origin = MessageOriginChannel(
            date=1, chat=Chat(2, "test"), message_id=1
        )
        assert not f.check_update(update)
        f.chat_ids = 2
        assert f.chat_ids == {2}
        assert f.check_update(update)

        with pytest.raises(RuntimeError, match="username in conjunction"):
            f.usernames = "chat"

    def test_filters_forwarded_from_change_username(self, update):
        # For User usernames
        f = filters.ForwardedFrom(username="chat")
        update.message.forward_origin.sender_user.username = "chat"
        assert f.check_update(update)
        update.message.forward_origin.sender_user.username = "User"
        assert not f.check_update(update)
        f.usernames = "User"
        assert f.check_update(update)

        # For Chat usernames
        update.message.forward_origin = None
        f = filters.ForwardedFrom(username="chat")
        update.message.forward_origin = MessageOriginChat(
            date=1, sender_chat=Chat(1, username="chat", type=Chat.SUPERGROUP)
        )
        assert f.check_update(update)
        update.message.forward_origin = MessageOriginChat(
            date=1, sender_chat=Chat(2, username="User", type=Chat.SUPERGROUP)
        )
        assert not f.check_update(update)
        f.usernames = "User"
        assert f.check_update(update)

        # For Channel usernames
        update.message.forward_origin = None
        f = filters.ForwardedFrom(username="chat")
        update.message.forward_origin = MessageOriginChannel(
            date=1, chat=Chat(1, username="chat", type=Chat.SUPERGROUP), message_id=1
        )
        assert f.check_update(update)
        update.message.forward_origin = MessageOriginChannel(
            date=1, chat=Chat(2, username="User", type=Chat.SUPERGROUP), message_id=1
        )
        assert not f.check_update(update)
        f.usernames = "User"
        assert f.check_update(update)

        with pytest.raises(RuntimeError, match="chat_id in conjunction"):
            f.chat_ids = 1

    def test_filters_forwarded_from_add_chat_by_name(self, update):
        chats = ["chat_a", "chat_b", "chat_c"]
        f = filters.ForwardedFrom()

        # For User usernames
        for chat in chats:
            update.message.forward_origin.sender_user.username = chat
            assert not f.check_update(update)

        f.add_usernames("chat_a")
        f.add_usernames(["chat_b", "chat_c"])

        for chat in chats:
            update.message.forward_origin.sender_user.username = chat
            assert f.check_update(update)

        # For Chat usernames
        update.message.forward_origin = None
        f = filters.ForwardedFrom()
        for chat in chats:
            update.message.forward_origin = MessageOriginChat(
                date=1, sender_chat=Chat(1, username=chat, type=Chat.SUPERGROUP)
            )
            assert not f.check_update(update)

        f.add_usernames("chat_a")
        f.add_usernames(["chat_b", "chat_c"])

        for chat in chats:
            update.message.forward_origin = MessageOriginChat(
                date=1, sender_chat=Chat(1, username=chat, type=Chat.SUPERGROUP)
            )
            assert f.check_update(update)

        # For Channel usernames
        update.message.forward_origin = None
        f = filters.ForwardedFrom()
        for chat in chats:
            update.message.forward_origin = MessageOriginChannel(
                date=1, chat=Chat(1, username=chat, type=Chat.SUPERGROUP), message_id=1
            )
            assert not f.check_update(update)

        f.add_usernames("chat_a")
        f.add_usernames(["chat_b", "chat_c"])

        for chat in chats:
            update.message.forward_origin = MessageOriginChannel(
                date=1, chat=Chat(1, username=chat, type=Chat.SUPERGROUP), message_id=1
            )
            assert f.check_update(update)

        with pytest.raises(RuntimeError, match="chat_id in conjunction"):
            f.add_chat_ids(1)

    def test_filters_forwarded_from_add_chat_by_id(self, update):
        chats = [1, 2, 3]
        f = filters.ForwardedFrom()

        # For User ids
        for chat in chats:
            update.message.forward_origin.sender_user.id = chat
            assert not f.check_update(update)

        f.add_chat_ids(1)
        f.add_chat_ids([2, 3])

        for chat in chats:
            update.message.forward_origin.sender_user.username = chat
            assert f.check_update(update)

        # For Chat ids-
        update.message.forward_origin = None
        f = filters.ForwardedFrom()
        for chat in chats:
            update.message.forward_origin = MessageOriginChat(
                date=1, sender_chat=Chat(chat, "test")
            )
            assert not f.check_update(update)

        f.add_chat_ids(1)
        f.add_chat_ids([2, 3])

        for chat in chats:
            update.message.forward_origin = MessageOriginChat(
                date=1, sender_chat=Chat(chat, "test")
            )
            assert f.check_update(update)

        # For Channel ids-
        update.message.forward_origin = None
        f = filters.ForwardedFrom()
        for chat in chats:
            update.message.forward_origin = MessageOriginChannel(
                date=1, chat=Chat(chat, "test"), message_id=1
            )
            assert not f.check_update(update)

        f.add_chat_ids(1)
        f.add_chat_ids([2, 3])

        for chat in chats:
            update.message.forward_origin = MessageOriginChannel(
                date=1, chat=Chat(chat, "test"), message_id=1
            )
            assert f.check_update(update)

        with pytest.raises(RuntimeError, match="username in conjunction"):
            f.add_usernames("chat")

    def test_filters_forwarded_from_remove_chat_by_name(self, update):
        chats = ["chat_a", "chat_b", "chat_c"]
        f = filters.ForwardedFrom(username=chats)

        with pytest.raises(RuntimeError, match="chat_id in conjunction"):
            f.remove_chat_ids(1)

        # For User usernames
        for chat in chats:
            update.message.forward_origin.sender_user.username = chat
            assert f.check_update(update)

        f.remove_usernames("chat_a")
        f.remove_usernames(["chat_b", "chat_c"])

        for chat in chats:
            update.message.forward_origin.sender_user.username = chat
            assert not f.check_update(update)

        # For Chat usernames
        update.message.forward_origin = None
        f = filters.ForwardedFrom(username=chats)
        for chat in chats:
            update.message.forward_origin = MessageOriginChat(
                date=1, sender_chat=Chat(1, username=chat, type=Chat.SUPERGROUP)
            )
            assert f.check_update(update)

        f.remove_usernames("chat_a")
        f.remove_usernames(["chat_b", "chat_c"])

        for chat in chats:
            update.message.forward_origin = MessageOriginChat(
                date=1, sender_chat=Chat(1, username=chat, type=Chat.SUPERGROUP)
            )
            assert not f.check_update(update)

        # For Channel usernames
        update.message.forward_origin = None
        f = filters.ForwardedFrom(username=chats)
        for chat in chats:
            update.message.forward_origin = MessageOriginChannel(
                date=1, chat=Chat(1, username=chat, type=Chat.SUPERGROUP), message_id=1
            )
            assert f.check_update(update)

        f.remove_usernames("chat_a")
        f.remove_usernames(["chat_b", "chat_c"])

        for chat in chats:
            update.message.forward_origin = MessageOriginChannel(
                date=1, chat=Chat(1, username=chat, type=Chat.SUPERGROUP), message_id=1
            )
            assert not f.check_update(update)

    def test_filters_forwarded_from_remove_chat_by_id(self, update):
        chats = [1, 2, 3]
        f = filters.ForwardedFrom(chat_id=chats)

        with pytest.raises(RuntimeError, match="username in conjunction"):
            f.remove_usernames("chat")

        # For User ids
        for chat in chats:
            update.message.forward_origin.sender_user.id = chat
            assert f.check_update(update)

        f.remove_chat_ids(1)
        f.remove_chat_ids([2, 3])

        for chat in chats:
            update.message.forward_origin.sender_user.username = chat
            assert not f.check_update(update)

        # For Chat ids
        update.message.forward_origin = None
        f = filters.ForwardedFrom(chat_id=chats)
        for chat in chats:
            update.message.forward_origin = MessageOriginChat(
                date=1, sender_chat=Chat(chat, "test")
            )
            assert f.check_update(update)

        f.remove_chat_ids(1)
        f.remove_chat_ids([2, 3])

        for chat in chats:
            update.message.forward_origin = MessageOriginChat(
                date=1, sender_chat=Chat(chat, "test")
            )
            assert not f.check_update(update)

        # For Channel ids
        update.message.forward_origin = None
        f = filters.ForwardedFrom(chat_id=chats)
        for chat in chats:
            update.message.forward_origin = MessageOriginChannel(
                date=1, chat=Chat(chat, "test"), message_id=1
            )
            assert f.check_update(update)

        f.remove_chat_ids(1)
        f.remove_chat_ids([2, 3])

        for chat in chats:
            update.message.forward_origin = MessageOriginChannel(
                date=1, chat=Chat(chat, "test"), message_id=1
            )
            assert not f.check_update(update)

    def test_filters_forwarded_from_repr(self):
        f = filters.ForwardedFrom([1, 2])
        assert str(f) == "filters.ForwardedFrom(1, 2)"
        f.remove_chat_ids(1)
        f.remove_chat_ids(2)
        assert str(f) == "filters.ForwardedFrom()"
        f.add_usernames("@foobar")
        assert str(f) == "filters.ForwardedFrom(foobar)"
        f.add_usernames("@barfoo")
        assert str(f).startswith("filters.ForwardedFrom(")
        # we don't know the exact order
        assert "barfoo" in str(f)
        assert "foobar" in str(f)

        with pytest.raises(RuntimeError, match="Cannot set name"):
            f.name = "foo"

    def test_filters_sender_chat_init(self):
        with pytest.raises(RuntimeError, match="in conjunction with"):
            filters.SenderChat(chat_id=1, username="chat")

    def test_filters_sender_chat_allow_empty(self, update):
        assert not filters.SenderChat().check_update(update)
        assert filters.SenderChat(allow_empty=True).check_update(update)

    def test_filters_sender_chat_id(self, update):
        assert not filters.SenderChat(chat_id=1).check_update(update)
        update.message.sender_chat.id = 1
        assert filters.SenderChat(chat_id=1).check_update(update)
        update.message.sender_chat.id = 2
        assert filters.SenderChat(chat_id=[1, 2]).check_update(update)
        assert not filters.SenderChat(chat_id=[3, 4]).check_update(update)
        assert filters.SenderChat.ALL.check_update(update)
        update.message.sender_chat = None
        assert not filters.SenderChat(chat_id=[3, 4]).check_update(update)
        assert not filters.SenderChat.ALL.check_update(update)

    def test_filters_sender_chat_username(self, update):
        assert not filters.SenderChat(username="chat").check_update(update)
        assert not filters.SenderChat(username="Testchat").check_update(update)
        update.message.sender_chat.username = "chat@"
        assert filters.SenderChat(username="@chat@").check_update(update)
        assert filters.SenderChat(username="chat@").check_update(update)
        assert filters.SenderChat(username=["chat1", "chat@", "chat2"]).check_update(update)
        assert not filters.SenderChat(username=["@username", "@chat_2"]).check_update(update)
        assert filters.SenderChat.ALL.check_update(update)
        update.message.sender_chat = None
        assert not filters.SenderChat(username=["@username", "@chat_2"]).check_update(update)
        assert not filters.SenderChat.ALL.check_update(update)

    def test_filters_sender_chat_change_id(self, update):
        f = filters.SenderChat(chat_id=1)
        assert f.chat_ids == {1}
        update.message.sender_chat.id = 1
        assert f.check_update(update)
        update.message.sender_chat.id = 2
        assert not f.check_update(update)
        f.chat_ids = 2
        assert f.chat_ids == {2}
        assert f.check_update(update)

        with pytest.raises(RuntimeError, match="username in conjunction"):
            f.usernames = "chat"

    def test_filters_sender_chat_change_username(self, update):
        f = filters.SenderChat(username="chat")
        update.message.sender_chat.username = "chat"
        assert f.check_update(update)
        update.message.sender_chat.username = "User"
        assert not f.check_update(update)
        f.usernames = "User"
        assert f.check_update(update)

        with pytest.raises(RuntimeError, match="chat_id in conjunction"):
            f.chat_ids = 1

    def test_filters_sender_chat_add_sender_chat_by_name(self, update):
        chats = ["chat_a", "chat_b", "chat_c"]
        f = filters.SenderChat()

        for chat in chats:
            update.message.sender_chat.username = chat
            assert not f.check_update(update)

        f.add_usernames("chat_a")
        f.add_usernames(["chat_b", "chat_c"])

        for chat in chats:
            update.message.sender_chat.username = chat
            assert f.check_update(update)

        with pytest.raises(RuntimeError, match="chat_id in conjunction"):
            f.add_chat_ids(1)

    def test_filters_sender_chat_add_sender_chat_by_id(self, update):
        chats = [1, 2, 3]
        f = filters.SenderChat()

        for chat in chats:
            update.message.sender_chat.id = chat
            assert not f.check_update(update)

        f.add_chat_ids(1)
        f.add_chat_ids([2, 3])

        for chat in chats:
            update.message.sender_chat.username = chat
            assert f.check_update(update)

        with pytest.raises(RuntimeError, match="username in conjunction"):
            f.add_usernames("chat")

    def test_filters_sender_chat_remove_sender_chat_by_name(self, update):
        chats = ["chat_a", "chat_b", "chat_c"]
        f = filters.SenderChat(username=chats)

        with pytest.raises(RuntimeError, match="chat_id in conjunction"):
            f.remove_chat_ids(1)

        for chat in chats:
            update.message.sender_chat.username = chat
            assert f.check_update(update)

        f.remove_usernames("chat_a")
        f.remove_usernames(["chat_b", "chat_c"])

        for chat in chats:
            update.message.sender_chat.username = chat
            assert not f.check_update(update)

    def test_filters_sender_chat_remove_sender_chat_by_id(self, update):
        chats = [1, 2, 3]
        f = filters.SenderChat(chat_id=chats)

        with pytest.raises(RuntimeError, match="username in conjunction"):
            f.remove_usernames("chat")

        for chat in chats:
            update.message.sender_chat.id = chat
            assert f.check_update(update)

        f.remove_chat_ids(1)
        f.remove_chat_ids([2, 3])

        for chat in chats:
            update.message.sender_chat.username = chat
            assert not f.check_update(update)

    def test_filters_sender_chat_repr(self):
        f = filters.SenderChat([1, 2])
        assert str(f) == "filters.SenderChat(1, 2)"
        f.remove_chat_ids(1)
        f.remove_chat_ids(2)
        assert str(f) == "filters.SenderChat()"
        f.add_usernames("@foobar")
        assert str(f) == "filters.SenderChat(foobar)"
        f.add_usernames("@barfoo")
        assert str(f).startswith("filters.SenderChat(")
        # we don't know th exact order
        assert "barfoo" in str(f)
        assert "foobar" in str(f)

        with pytest.raises(RuntimeError, match="Cannot set name"):
            f.name = "foo"

    def test_filters_sender_chat_super_group(self, update):
        update.message.sender_chat.type = Chat.PRIVATE
        assert not filters.SenderChat.SUPER_GROUP.check_update(update)
        assert filters.SenderChat.ALL.check_update(update)
        update.message.sender_chat.type = Chat.CHANNEL
        assert not filters.SenderChat.SUPER_GROUP.check_update(update)
        update.message.sender_chat.type = Chat.SUPERGROUP
        assert filters.SenderChat.SUPER_GROUP.check_update(update)
        assert filters.SenderChat.ALL.check_update(update)
        update.message.sender_chat = None
        assert not filters.SenderChat.SUPER_GROUP.check_update(update)
        assert not filters.SenderChat.ALL.check_update(update)

    def test_filters_sender_chat_channel(self, update):
        update.message.sender_chat.type = Chat.PRIVATE
        assert not filters.SenderChat.CHANNEL.check_update(update)
        update.message.sender_chat.type = Chat.SUPERGROUP
        assert not filters.SenderChat.CHANNEL.check_update(update)
        update.message.sender_chat.type = Chat.CHANNEL
        assert filters.SenderChat.CHANNEL.check_update(update)
        update.message.sender_chat = None
        assert not filters.SenderChat.CHANNEL.check_update(update)

    def test_filters_is_automatic_forward(self, update):
        assert not filters.IS_AUTOMATIC_FORWARD.check_update(update)
        update.message.is_automatic_forward = True
        assert filters.IS_AUTOMATIC_FORWARD.check_update(update)

    def test_filters_is_from_offline(self, update):
        assert not filters.IS_FROM_OFFLINE.check_update(update)
        update.message.is_from_offline = True
        assert filters.IS_FROM_OFFLINE.check_update(update)

    def test_filters_is_topic_message(self, update):
        assert not filters.IS_TOPIC_MESSAGE.check_update(update)
        update.message.is_topic_message = True
        assert filters.IS_TOPIC_MESSAGE.check_update(update)

    def test_filters_has_media_spoiler(self, update):
        assert not filters.HAS_MEDIA_SPOILER.check_update(update)
        update.message.has_media_spoiler = True
        assert filters.HAS_MEDIA_SPOILER.check_update(update)

    def test_filters_has_protected_content(self, update):
        assert not filters.HAS_PROTECTED_CONTENT.check_update(update)
        update.message.has_protected_content = True
        assert filters.HAS_PROTECTED_CONTENT.check_update(update)

    def test_filters_invoice(self, update):
        assert not filters.INVOICE.check_update(update)
        update.message.invoice = "test"
        assert filters.INVOICE.check_update(update)

    def test_filters_successful_payment(self, update):
        assert not filters.SUCCESSFUL_PAYMENT.check_update(update)
        update.message.successful_payment = "test"
        assert filters.SUCCESSFUL_PAYMENT.check_update(update)

    def test_filters_successful_payment_payloads(self, update):
        assert not filters.SuccessfulPayment(("custom-payload",)).check_update(update)
        assert not filters.SuccessfulPayment().check_update(update)

        update.message.successful_payment = SuccessfulPayment(
            "USD", 100, "custom-payload", "123", "123"
        )
        assert filters.SuccessfulPayment(("custom-payload",)).check_update(update)
        assert filters.SuccessfulPayment().check_update(update)
        assert not filters.SuccessfulPayment(["test1"]).check_update(update)

    def test_filters_successful_payment_repr(self):
        f = filters.SuccessfulPayment()
        assert str(f) == "filters.SUCCESSFUL_PAYMENT"

        f = filters.SuccessfulPayment(["payload1", "payload2"])
        assert str(f) == "filters.SuccessfulPayment(['payload1', 'payload2'])"

    def test_filters_passport_data(self, update):
        assert not filters.PASSPORT_DATA.check_update(update)
        update.message.passport_data = "test"
        assert filters.PASSPORT_DATA.check_update(update)

    def test_filters_poll(self, update):
        assert not filters.POLL.check_update(update)
        update.message.poll = "test"
        assert filters.POLL.check_update(update)

    @pytest.mark.parametrize("emoji", Dice.ALL_EMOJI)
    def test_filters_dice(self, update, emoji):
        update.message.dice = Dice(4, emoji)
        assert filters.Dice.ALL.check_update(update)
        assert filters.Dice().check_update(update)

        to_camel = emoji.name.title().replace("_", "")
        assert repr(filters.Dice.ALL) == "filters.Dice.ALL"
        assert repr(getattr(filters.Dice, to_camel)(4)) == f"filters.Dice.{to_camel}([4])"

        update.message.dice = None
        assert not filters.Dice.ALL.check_update(update)

    @pytest.mark.parametrize("emoji", Dice.ALL_EMOJI)
    def test_filters_dice_list(self, update, emoji):
        update.message.dice = None
        assert not filters.Dice(5).check_update(update)

        update.message.dice = Dice(5, emoji)
        assert filters.Dice(5).check_update(update)
        assert repr(filters.Dice(5)) == "filters.Dice([5])"
        assert filters.Dice({5, 6}).check_update(update)
        assert not filters.Dice(1).check_update(update)
        assert not filters.Dice([2, 3]).check_update(update)

    def test_filters_dice_type(self, update):
        update.message.dice = Dice(5, "🎲")
        assert filters.Dice.DICE.check_update(update)
        assert repr(filters.Dice.DICE) == "filters.Dice.DICE"
        assert filters.Dice.Dice([4, 5]).check_update(update)
        assert not filters.Dice.Darts(5).check_update(update)
        assert not filters.Dice.BASKETBALL.check_update(update)
        assert not filters.Dice.Dice([6]).check_update(update)

        update.message.dice = Dice(5, "🎯")
        assert filters.Dice.DARTS.check_update(update)
        assert filters.Dice.Darts([4, 5]).check_update(update)
        assert not filters.Dice.Dice(5).check_update(update)
        assert not filters.Dice.BASKETBALL.check_update(update)
        assert not filters.Dice.Darts([6]).check_update(update)

        update.message.dice = Dice(5, "🏀")
        assert filters.Dice.BASKETBALL.check_update(update)
        assert filters.Dice.Basketball([4, 5]).check_update(update)
        assert not filters.Dice.Dice(5).check_update(update)
        assert not filters.Dice.DARTS.check_update(update)
        assert not filters.Dice.Basketball([4]).check_update(update)

        update.message.dice = Dice(5, "⚽")
        assert filters.Dice.FOOTBALL.check_update(update)
        assert filters.Dice.Football([4, 5]).check_update(update)
        assert not filters.Dice.Dice(5).check_update(update)
        assert not filters.Dice.DARTS.check_update(update)
        assert not filters.Dice.Football([4]).check_update(update)

        update.message.dice = Dice(5, "🎰")
        assert filters.Dice.SLOT_MACHINE.check_update(update)
        assert filters.Dice.SlotMachine([4, 5]).check_update(update)
        assert not filters.Dice.Dice(5).check_update(update)
        assert not filters.Dice.DARTS.check_update(update)
        assert not filters.Dice.SlotMachine([4]).check_update(update)

        update.message.dice = Dice(5, "🎳")
        assert filters.Dice.BOWLING.check_update(update)
        assert filters.Dice.Bowling([4, 5]).check_update(update)
        assert not filters.Dice.Dice(5).check_update(update)
        assert not filters.Dice.DARTS.check_update(update)
        assert not filters.Dice.Bowling([4]).check_update(update)

    def test_language_filter_single(self, update):
        update.message.from_user.language_code = "en_US"
        assert filters.Language("en_US").check_update(update)
        assert filters.Language("en").check_update(update)
        assert not filters.Language("en_GB").check_update(update)
        assert not filters.Language("da").check_update(update)
        update.message.from_user.language_code = "da"
        assert not filters.Language("en_US").check_update(update)
        assert not filters.Language("en").check_update(update)
        assert not filters.Language("en_GB").check_update(update)
        assert filters.Language("da").check_update(update)

        update.message.from_user = None
        assert not filters.Language("da").check_update(update)

    def test_language_filter_multiple(self, update):
        f = filters.Language(["en_US", "da"])
        update.message.from_user.language_code = "en_US"
        assert f.check_update(update)
        update.message.from_user.language_code = "en_GB"
        assert not f.check_update(update)
        update.message.from_user.language_code = "da"
        assert f.check_update(update)

    def test_and_filters(self, update, message_origin_user):
        update.message.text = "test"
        update.message.forward_origin = message_origin_user
        assert (filters.TEXT & filters.FORWARDED).check_update(update)
        update.message.text = "/test"
        assert (filters.TEXT & filters.FORWARDED).check_update(update)
        update.message.text = "test"
        update.message.forward_origin = None
        assert not (filters.TEXT & filters.FORWARDED).check_update(update)

        update.message.text = "test"
        update.message.forward_origin = message_origin_user
        assert (filters.TEXT & filters.FORWARDED & filters.ChatType.PRIVATE).check_update(update)

    def test_or_filters(self, update):
        update.message.text = "test"
        assert (filters.TEXT | filters.StatusUpdate.ALL).check_update(update)
        update.message.group_chat_created = True
        assert (filters.TEXT | filters.StatusUpdate.ALL).check_update(update)
        update.message.text = None
        assert (filters.TEXT | filters.StatusUpdate.ALL).check_update(update)
        update.message.group_chat_created = False
        assert not (filters.TEXT | filters.StatusUpdate.ALL).check_update(update)

    def test_and_or_filters(self, update):
        update.message.text = "test"
        update.message.forward_origin = message_origin_user
        assert (filters.TEXT & (filters.StatusUpdate.ALL | filters.FORWARDED)).check_update(update)
        update.message.forward_origin = None
        assert not (filters.TEXT & (filters.FORWARDED | filters.StatusUpdate.ALL)).check_update(
            update
        )
        update.message.pinned_message = True
        assert filters.TEXT & (filters.FORWARDED | filters.StatusUpdate.ALL).check_update(update)

        assert (
            str(filters.TEXT & (filters.FORWARDED | filters.Entity(MessageEntity.MENTION)))
            == "<filters.TEXT and <filters.FORWARDED or filters.Entity(mention)>>"
        )

    def test_xor_filters(self, update):
        update.message.text = "test"
        update.effective_user.id = 123
        assert not (filters.TEXT ^ filters.User(123)).check_update(update)
        update.message.text = None
        update.effective_user.id = 1234
        assert not (filters.TEXT ^ filters.User(123)).check_update(update)
        update.message.text = "test"
        assert (filters.TEXT ^ filters.User(123)).check_update(update)
        update.message.text = None
        update.effective_user.id = 123
        assert (filters.TEXT ^ filters.User(123)).check_update(update)

    def test_xor_filters_repr(self, update):
        assert str(filters.TEXT ^ filters.User(123)) == "<filters.TEXT xor filters.User(123)>"
        with pytest.raises(RuntimeError, match="Cannot set name"):
            (filters.TEXT ^ filters.User(123)).name = "foo"

    def test_and_xor_filters(self, update, message_origin_user):
        update.message.text = "test"
        update.message.forward_origin = message_origin_user
        assert (filters.FORWARDED & (filters.TEXT ^ filters.User(123))).check_update(update)
        update.message.text = None
        update.effective_user.id = 123
        assert (filters.FORWARDED & (filters.TEXT ^ filters.User(123))).check_update(update)
        update.message.text = "test"
        assert not (filters.FORWARDED & (filters.TEXT ^ filters.User(123))).check_update(update)
        update.message.forward_origin = None
        update.message.text = None
        update.effective_user.id = 123
        assert not (filters.FORWARDED & (filters.TEXT ^ filters.User(123))).check_update(update)
        update.message.text = "test"
        update.effective_user.id = 456
        assert not (filters.FORWARDED & (filters.TEXT ^ filters.User(123))).check_update(update)

        assert (
            str(filters.FORWARDED & (filters.TEXT ^ filters.User(123)))
            == "<filters.FORWARDED and <filters.TEXT xor filters.User(123)>>"
        )

    def test_xor_regex_filters(self, update, message_origin_user):
        sre_type = type(re.match("", ""))
        update.message.text = "test"
        update.message.forward_origin = message_origin_user
        assert not (filters.FORWARDED ^ filters.Regex("^test$")).check_update(update)
        update.message.forward_origin = None
        result = (filters.FORWARDED ^ filters.Regex("^test$")).check_update(update)
        assert result
        assert isinstance(result, dict)
        matches = result["matches"]
        assert isinstance(matches, list)
        assert type(matches[0]) is sre_type
        update.message.forward_origin = message_origin_user
        update.message.text = None
        assert (filters.FORWARDED ^ filters.Regex("^test$")).check_update(update) is True

    def test_inverted_filters(self, update):
        update.message.text = "/test"
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]
        assert filters.COMMAND.check_update(update)
        assert not (~filters.COMMAND).check_update(update)
        update.message.text = "test"
        update.message.entities = []
        assert not filters.COMMAND.check_update(update)
        assert (~filters.COMMAND).check_update(update)

    def test_inverted_filters_repr(self, update):
        assert str(~filters.TEXT) == "<inverted filters.TEXT>"
        with pytest.raises(RuntimeError, match="Cannot set name"):
            (~filters.TEXT).name = "foo"

    def test_inverted_and_filters(self, update, message_origin_user):
        update.message.text = "/test"
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]
        update.message.forward_origin = message_origin_user
        assert (filters.FORWARDED & filters.COMMAND).check_update(update)
        assert not (~filters.FORWARDED & filters.COMMAND).check_update(update)
        assert not (filters.FORWARDED & ~filters.COMMAND).check_update(update)
        assert not (~(filters.FORWARDED & filters.COMMAND)).check_update(update)
        update.message.forward_origin = None
        assert not (filters.FORWARDED & filters.COMMAND).check_update(update)
        assert (~filters.FORWARDED & filters.COMMAND).check_update(update)
        assert not (filters.FORWARDED & ~filters.COMMAND).check_update(update)
        assert (~(filters.FORWARDED & filters.COMMAND)).check_update(update)
        update.message.text = "test"
        update.message.entities = []
        assert not (filters.FORWARDED & filters.COMMAND).check_update(update)
        assert not (~filters.FORWARDED & filters.COMMAND).check_update(update)
        assert not (filters.FORWARDED & ~filters.COMMAND).check_update(update)
        assert (~(filters.FORWARDED & filters.COMMAND)).check_update(update)

    def test_indirect_message(self, update):
        class _CustomFilter(filters.MessageFilter):
            test_flag = False

            def filter(self, message: Message):
                self.test_flag = True
                return self.test_flag

        c = _CustomFilter()
        u = Update(0, callback_query=CallbackQuery("0", update.effective_user, "", update.message))
        assert not c.check_update(u)
        assert not c.test_flag
        assert c.check_update(update)
        assert c.test_flag

    def test_custom_unnamed_filter(self, update, base_class):
        class Unnamed(base_class):
            def filter(self, _):
                return True

        unnamed = Unnamed()
        assert str(unnamed) == Unnamed.__name__

    def test_update_type_message(self, update):
        assert filters.UpdateType.MESSAGE.check_update(update)
        assert not filters.UpdateType.EDITED_MESSAGE.check_update(update)
        assert filters.UpdateType.MESSAGES.check_update(update)
        assert not filters.UpdateType.CHANNEL_POST.check_update(update)
        assert not filters.UpdateType.EDITED_CHANNEL_POST.check_update(update)
        assert not filters.UpdateType.CHANNEL_POSTS.check_update(update)
        assert not filters.UpdateType.EDITED.check_update(update)
        assert not filters.UpdateType.BUSINESS_MESSAGES.check_update(update)
        assert not filters.UpdateType.BUSINESS_MESSAGE.check_update(update)
        assert not filters.UpdateType.EDITED_BUSINESS_MESSAGE.check_update(update)

    def test_update_type_edited_message(self, update):
        update.edited_message, update.message = update.message, update.edited_message
        assert not filters.UpdateType.MESSAGE.check_update(update)
        assert filters.UpdateType.EDITED_MESSAGE.check_update(update)
        assert filters.UpdateType.MESSAGES.check_update(update)
        assert not filters.UpdateType.CHANNEL_POST.check_update(update)
        assert not filters.UpdateType.EDITED_CHANNEL_POST.check_update(update)
        assert not filters.UpdateType.CHANNEL_POSTS.check_update(update)
        assert filters.UpdateType.EDITED.check_update(update)
        assert not filters.UpdateType.BUSINESS_MESSAGES.check_update(update)
        assert not filters.UpdateType.BUSINESS_MESSAGE.check_update(update)
        assert not filters.UpdateType.EDITED_BUSINESS_MESSAGE.check_update(update)

    def test_update_type_channel_post(self, update):
        update.channel_post, update.message = update.message, update.edited_message
        assert not filters.UpdateType.MESSAGE.check_update(update)
        assert not filters.UpdateType.EDITED_MESSAGE.check_update(update)
        assert not filters.UpdateType.MESSAGES.check_update(update)
        assert filters.UpdateType.CHANNEL_POST.check_update(update)
        assert not filters.UpdateType.EDITED_CHANNEL_POST.check_update(update)
        assert filters.UpdateType.CHANNEL_POSTS.check_update(update)
        assert not filters.UpdateType.EDITED.check_update(update)
        assert not filters.UpdateType.BUSINESS_MESSAGES.check_update(update)
        assert not filters.UpdateType.BUSINESS_MESSAGE.check_update(update)
        assert not filters.UpdateType.EDITED_BUSINESS_MESSAGE.check_update(update)

    def test_update_type_edited_channel_post(self, update):
        update.edited_channel_post, update.message = update.message, update.edited_message
        assert not filters.UpdateType.MESSAGE.check_update(update)
        assert not filters.UpdateType.EDITED_MESSAGE.check_update(update)
        assert not filters.UpdateType.MESSAGES.check_update(update)
        assert not filters.UpdateType.CHANNEL_POST.check_update(update)
        assert filters.UpdateType.EDITED_CHANNEL_POST.check_update(update)
        assert filters.UpdateType.CHANNEL_POSTS.check_update(update)
        assert filters.UpdateType.EDITED.check_update(update)
        assert not filters.UpdateType.BUSINESS_MESSAGES.check_update(update)
        assert not filters.UpdateType.BUSINESS_MESSAGE.check_update(update)
        assert not filters.UpdateType.EDITED_BUSINESS_MESSAGE.check_update(update)

    def test_update_type_business_message(self, update):
        update.business_message, update.message = update.message, update.edited_message
        assert not filters.UpdateType.MESSAGE.check_update(update)
        assert not filters.UpdateType.EDITED_MESSAGE.check_update(update)
        assert not filters.UpdateType.MESSAGES.check_update(update)
        assert not filters.UpdateType.CHANNEL_POST.check_update(update)
        assert not filters.UpdateType.EDITED_CHANNEL_POST.check_update(update)
        assert not filters.UpdateType.CHANNEL_POSTS.check_update(update)
        assert not filters.UpdateType.EDITED.check_update(update)
        assert filters.UpdateType.BUSINESS_MESSAGES.check_update(update)
        assert filters.UpdateType.BUSINESS_MESSAGE.check_update(update)
        assert not filters.UpdateType.EDITED_BUSINESS_MESSAGE.check_update(update)

    def test_update_type_edited_business_message(self, update):
        update.edited_business_message, update.message = update.message, update.edited_message
        assert not filters.UpdateType.MESSAGE.check_update(update)
        assert not filters.UpdateType.EDITED_MESSAGE.check_update(update)
        assert not filters.UpdateType.MESSAGES.check_update(update)
        assert not filters.UpdateType.CHANNEL_POST.check_update(update)
        assert not filters.UpdateType.EDITED_CHANNEL_POST.check_update(update)
        assert not filters.UpdateType.CHANNEL_POSTS.check_update(update)
        assert filters.UpdateType.EDITED.check_update(update)
        assert filters.UpdateType.BUSINESS_MESSAGES.check_update(update)
        assert not filters.UpdateType.BUSINESS_MESSAGE.check_update(update)
        assert filters.UpdateType.EDITED_BUSINESS_MESSAGE.check_update(update)

    def test_merged_short_circuit_and(self, update, base_class):
        update.message.text = "/test"
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]

        class TestException(Exception):
            pass

        class RaisingFilter(base_class):
            def filter(self, _):
                raise TestException

        raising_filter = RaisingFilter()

        with pytest.raises(TestException):
            (filters.COMMAND & raising_filter).check_update(update)

        update.message.text = "test"
        update.message.entities = []
        (filters.COMMAND & raising_filter).check_update(update)

    def test_merged_filters_repr(self, update):
        with pytest.raises(RuntimeError, match="Cannot set name"):
            (filters.TEXT & filters.PHOTO).name = "foo"

    def test_merged_short_circuit_or(self, update, base_class):
        update.message.text = "test"

        class TestException(Exception):
            pass

        class RaisingFilter(base_class):
            def filter(self, _):
                raise TestException

        raising_filter = RaisingFilter()

        with pytest.raises(TestException):
            (filters.COMMAND | raising_filter).check_update(update)

        update.message.text = "/test"
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]
        (filters.COMMAND | raising_filter).check_update(update)

    def test_merged_data_merging_and(self, update, base_class):
        update.message.text = "/test"
        update.message.entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, 5)]

        class DataFilter(base_class):
            data_filter = True

            def __init__(self, data):
                self.data = data

            def filter(self, _):
                return {"test": [self.data], "test2": {"test3": [self.data]}}

        result = (filters.COMMAND & DataFilter("blah")).check_update(update)
        assert result["test"] == ["blah"]
        assert not result["test2"]

        result = (DataFilter("blah1") & DataFilter("blah2")).check_update(update)
        assert result["test"] == ["blah1", "blah2"]
        assert isinstance(result["test2"], list)
        assert result["test2"][0]["test3"] == ["blah1"]

        update.message.text = "test"
        update.message.entities = []
        result = (filters.COMMAND & DataFilter("blah")).check_update(update)
        assert not result

    def test_merged_data_merging_or(self, update, base_class):
        update.message.text = "/test"

        class DataFilter(base_class):
            data_filter = True

            def __init__(self, data):
                self.data = data

            def filter(self, _):
                return {"test": [self.data]}

        result = (filters.COMMAND | DataFilter("blah")).check_update(update)
        assert result

        result = (DataFilter("blah1") | DataFilter("blah2")).check_update(update)
        assert result["test"] == ["blah1"]

        update.message.text = "test"
        result = (filters.COMMAND | DataFilter("blah")).check_update(update)
        assert result["test"] == ["blah"]

    def test_filters_via_bot_init(self):
        with pytest.raises(RuntimeError, match="in conjunction with"):
            filters.ViaBot(bot_id=1, username="bot")

    def test_filters_via_bot_allow_empty(self, update):
        assert not filters.ViaBot().check_update(update)
        assert filters.ViaBot(allow_empty=True).check_update(update)

    def test_filters_via_bot_id(self, update):
        assert not filters.ViaBot(bot_id=1).check_update(update)
        update.message.via_bot.id = 1
        assert filters.ViaBot(bot_id=1).check_update(update)
        update.message.via_bot.id = 2
        assert filters.ViaBot(bot_id=[1, 2]).check_update(update)
        assert not filters.ViaBot(bot_id=[3, 4]).check_update(update)
        update.message.via_bot = None
        assert not filters.ViaBot(bot_id=[3, 4]).check_update(update)

    def test_filters_via_bot_username(self, update):
        assert not filters.ViaBot(username="bot").check_update(update)
        assert not filters.ViaBot(username="Testbot").check_update(update)
        update.message.via_bot.username = "bot@"
        assert filters.ViaBot(username="@bot@").check_update(update)
        assert filters.ViaBot(username="bot@").check_update(update)
        assert filters.ViaBot(username=["bot1", "bot@", "bot2"]).check_update(update)
        assert not filters.ViaBot(username=["@username", "@bot_2"]).check_update(update)
        update.message.via_bot = None
        assert not filters.User(username=["@username", "@bot_2"]).check_update(update)

    def test_filters_via_bot_change_id(self, update):
        f = filters.ViaBot(bot_id=3)
        assert f.bot_ids == {3}
        update.message.via_bot.id = 3
        assert f.check_update(update)
        update.message.via_bot.id = 2
        assert not f.check_update(update)
        f.bot_ids = 2
        assert f.bot_ids == {2}
        assert f.check_update(update)

        with pytest.raises(RuntimeError, match="username in conjunction"):
            f.usernames = "user"

    def test_filters_via_bot_change_username(self, update):
        f = filters.ViaBot(username="bot")
        update.message.via_bot.username = "bot"
        assert f.check_update(update)
        update.message.via_bot.username = "Bot"
        assert not f.check_update(update)
        f.usernames = "Bot"
        assert f.check_update(update)

        with pytest.raises(RuntimeError, match="bot_id in conjunction"):
            f.bot_ids = 1

    def test_filters_via_bot_add_user_by_name(self, update):
        users = ["bot_a", "bot_b", "bot_c"]
        f = filters.ViaBot()

        for user in users:
            update.message.via_bot.username = user
            assert not f.check_update(update)

        f.add_usernames("bot_a")
        f.add_usernames(["bot_b", "bot_c"])

        for user in users:
            update.message.via_bot.username = user
            assert f.check_update(update)

        with pytest.raises(RuntimeError, match="bot_id in conjunction"):
            f.add_bot_ids(1)

    def test_filters_via_bot_add_user_by_id(self, update):
        users = [1, 2, 3]
        f = filters.ViaBot()

        for user in users:
            update.message.via_bot.id = user
            assert not f.check_update(update)

        f.add_bot_ids(1)
        f.add_bot_ids([2, 3])

        for user in users:
            update.message.via_bot.username = user
            assert f.check_update(update)

        with pytest.raises(RuntimeError, match="username in conjunction"):
            f.add_usernames("bot")

    def test_filters_via_bot_remove_user_by_name(self, update):
        users = ["bot_a", "bot_b", "bot_c"]
        f = filters.ViaBot(username=users)

        with pytest.raises(RuntimeError, match="bot_id in conjunction"):
            f.remove_bot_ids(1)

        for user in users:
            update.message.via_bot.username = user
            assert f.check_update(update)

        f.remove_usernames("bot_a")
        f.remove_usernames(["bot_b", "bot_c"])

        for user in users:
            update.message.via_bot.username = user
            assert not f.check_update(update)

    def test_filters_via_bot_remove_user_by_id(self, update):
        users = [1, 2, 3]
        f = filters.ViaBot(bot_id=users)

        with pytest.raises(RuntimeError, match="username in conjunction"):
            f.remove_usernames("bot")

        for user in users:
            update.message.via_bot.id = user
            assert f.check_update(update)

        f.remove_bot_ids(1)
        f.remove_bot_ids([2, 3])

        for user in users:
            update.message.via_bot.username = user
            assert not f.check_update(update)

    def test_filters_via_bot_repr(self):
        f = filters.ViaBot([1, 2])
        assert str(f) == "filters.ViaBot(1, 2)"
        f.remove_bot_ids(1)
        f.remove_bot_ids(2)
        assert str(f) == "filters.ViaBot()"
        f.add_usernames("@foobar")
        assert str(f) == "filters.ViaBot(foobar)"
        f.add_usernames("@barfoo")
        assert str(f).startswith("filters.ViaBot(")
        # we don't know th exact order
        assert "barfoo" in str(f)
        assert "foobar" in str(f)

        with pytest.raises(RuntimeError, match="Cannot set name"):
            f.name = "foo"

    def test_filters_attachment(self, update):
        assert not filters.ATTACHMENT.check_update(update)
        # we need to define a new Update (or rather, message class) here because
        # effective_attachment is only evaluated once per instance, and the filter relies on that
        up = Update(
            0,
            Message(
                0,
                datetime.datetime.utcnow(),
                Chat(0, "private"),
                document=Document("str", "other_str"),
            ),
        )
        assert filters.ATTACHMENT.check_update(up)

    def test_filters_mention_no_entities(self, update):
        update.message.text = "test"
        assert not filters.Mention("@test").check_update(update)
        assert not filters.Mention(123456).check_update(update)
        assert not filters.Mention("123456").check_update(update)
        assert not filters.Mention(User(1, "first_name", False)).check_update(update)
        assert not filters.Mention(
            ["@test", 123456, "123456", User(1, "first_name", False)]
        ).check_update(update)

    def test_filters_mention_type_mention(self, update):
        update.message.text = "@test1 @test2 user"
        update.message.entities = [
            MessageEntity(MessageEntity.MENTION, 0, 6),
            MessageEntity(MessageEntity.MENTION, 7, 6),
        ]

        user_no_username = User(123456, "first_name", False)
        user_wrong_username = User(123456, "first_name", False, username="wrong")
        user_1 = User(111, "first_name", False, username="test1")
        user_2 = User(222, "first_name", False, username="test2")

        for username in ("@test1", "@test2"):
            assert filters.Mention(username).check_update(update)
            assert filters.Mention({username}).check_update(update)

        for user in (user_1, user_2):
            assert filters.Mention(user).check_update(update)
            assert filters.Mention({user}).check_update(update)

        assert not filters.Mention(
            ["@test3", 123, user_no_username, user_wrong_username]
        ).check_update(update)

    def test_filters_mention_type_text_mention(self, update):
        user_1 = User(111, "first_name", False, username="test1")
        user_2 = User(222, "first_name", False, username="test2")
        user_no_username = User(123456, "first_name", False)
        user_wrong_username = User(123456, "first_name", False, username="wrong")

        update.message.text = "test1 test2 user"
        update.message.entities = [
            MessageEntity(MessageEntity.TEXT_MENTION, 0, 5, user=user_1),
            MessageEntity(MessageEntity.TEXT_MENTION, 6, 5, user=user_2),
        ]

        for username in ("@test1", "@test2"):
            assert filters.Mention(username).check_update(update)
            assert filters.Mention({username}).check_update(update)

        for user in (user_1, user_2):
            assert filters.Mention(user).check_update(update)
            assert filters.Mention({user}).check_update(update)

        for user_id in (111, 222):
            assert filters.Mention(user_id).check_update(update)
            assert filters.Mention({user_id}).check_update(update)

        assert not filters.Mention(
            ["@test3", 123, user_no_username, user_wrong_username]
        ).check_update(update)

    def test_filters_giveaway(self, update):
        assert not filters.GIVEAWAY.check_update(update)

        update.message.giveaway = "test"
        assert filters.GIVEAWAY.check_update(update)
        assert str(filters.GIVEAWAY) == "filters.GIVEAWAY"

    def test_filters_giveaway_winners(self, update):
        assert not filters.GIVEAWAY_WINNERS.check_update(update)

        update.message.giveaway_winners = "test"
        assert filters.GIVEAWAY_WINNERS.check_update(update)
        assert str(filters.GIVEAWAY_WINNERS) == "filters.GIVEAWAY_WINNERS"

    def test_filters_reply_to_story(self, update):
        assert not filters.REPLY_TO_STORY.check_update(update)

        update.message.reply_to_story = "test"
        assert filters.REPLY_TO_STORY.check_update(update)
        assert str(filters.REPLY_TO_STORY) == "filters.REPLY_TO_STORY"

    def test_filters_boost_added(self, update):
        assert not filters.BOOST_ADDED.check_update(update)

        update.message.boost_added = "test"
        assert filters.BOOST_ADDED.check_update(update)
        assert str(filters.BOOST_ADDED) == "filters.BOOST_ADDED"

    def test_filters_sender_boost_count(self, update):
        assert not filters.SENDER_BOOST_COUNT.check_update(update)

        update.message.sender_boost_count = "test"
        assert filters.SENDER_BOOST_COUNT.check_update(update)
        assert str(filters.SENDER_BOOST_COUNT) == "filters.SENDER_BOOST_COUNT"
