#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
import random

import pytest

from telegram import MessageEntity, User
from telegram.constants import MessageEntityType
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module", params=MessageEntity.ALL_TYPES)
def message_entity(request):
    type_ = request.param
    url = None
    if type_ == MessageEntity.TEXT_LINK:
        url = "t.me"
    user = None
    if type_ == MessageEntity.TEXT_MENTION:
        user = User(1, "test_user", False)
    language = None
    if type_ == MessageEntity.PRE:
        language = "python"
    return MessageEntity(type_, 1, 3, url=url, user=user, language=language)


class MessageEntityTestBase:
    type_ = "url"
    offset = 1
    length = 2
    url = "url"


class TestMessageEntityWithoutRequest(MessageEntityTestBase):
    def test_slot_behaviour(self, message_entity):
        inst = message_entity
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json(self, offline_bot):
        json_dict = {"type": self.type_, "offset": self.offset, "length": self.length}
        entity = MessageEntity.de_json(json_dict, offline_bot)
        assert entity.api_kwargs == {}

        assert entity.type == self.type_
        assert entity.offset == self.offset
        assert entity.length == self.length

    def test_to_dict(self, message_entity):
        entity_dict = message_entity.to_dict()

        assert isinstance(entity_dict, dict)
        assert entity_dict["type"] == message_entity.type
        assert entity_dict["offset"] == message_entity.offset
        assert entity_dict["length"] == message_entity.length
        if message_entity.url:
            assert entity_dict["url"] == message_entity.url
        if message_entity.user:
            assert entity_dict["user"] == message_entity.user.to_dict()
        if message_entity.language:
            assert entity_dict["language"] == message_entity.language

    def test_enum_init(self):
        entity = MessageEntity(type="foo", offset=0, length=1)
        assert entity.type == "foo"
        entity = MessageEntity(type="url", offset=0, length=1)
        assert entity.type is MessageEntityType.URL

    def test_fix_utf16(self):
        text = "𠌕 bold 𝄢 italic underlined: 𝛙𝌢𑁍"
        inputs_outputs: list[tuple[tuple[int, int, str], tuple[int, int]]] = [
            ((2, 4, MessageEntity.BOLD), (3, 4)),
            ((9, 6, MessageEntity.ITALIC), (11, 6)),
            ((28, 3, MessageEntity.UNDERLINE), (30, 6)),
        ]
        random.shuffle(inputs_outputs)
        unicode_entities = [
            MessageEntity(offset=_input[0], length=_input[1], type=_input[2])
            for _input, _ in inputs_outputs
        ]
        utf_16_entities = MessageEntity.adjust_message_entities_to_utf_16(text, unicode_entities)
        for out_entity, input_output in zip(utf_16_entities, inputs_outputs):
            _, output = input_output
            offset, length = output
            assert out_entity.offset == offset
            assert out_entity.length == length

    @pytest.mark.parametrize("by", [6, "prefix", "𝛙𝌢𑁍"])
    def test_shift_entities(self, by):
        kwargs = {
            "url": "url",
            "user": 42,
            "language": "python",
            "custom_emoji_id": "custom_emoji_id",
        }
        entities = [
            MessageEntity(MessageEntity.BOLD, 2, 3, **kwargs),
            MessageEntity(MessageEntity.BOLD, 5, 6, **kwargs),
        ]
        shifted = MessageEntity.shift_entities(by, entities)
        assert shifted[0].offset == 8
        assert shifted[1].offset == 11

        assert shifted[0] is not entities[0]
        assert shifted[1] is not entities[1]

        for entity in shifted:
            for key, value in kwargs.items():
                assert getattr(entity, key) == value

    def test_concatenate(self):
        kwargs = {
            "url": "url",
            "user": 42,
            "language": "python",
            "custom_emoji_id": "custom_emoji_id",
        }
        first_entity = MessageEntity(MessageEntity.BOLD, 0, 6, **kwargs)
        second_entity = MessageEntity(MessageEntity.ITALIC, 0, 4, **kwargs)
        third_entity = MessageEntity(MessageEntity.UNDERLINE, 3, 6, **kwargs)

        first = ("prefix 𝛙𝌢𑁍 | ", [first_entity], True)
        second = ("text 𝛙𝌢𑁍", [second_entity], False)
        third = (" | suffix 𝛙𝌢𑁍", [third_entity])

        new_text, new_entities = MessageEntity.concatenate(first, second, third)

        assert new_text == "prefix 𝛙𝌢𑁍 | text 𝛙𝌢𑁍 | suffix 𝛙𝌢𑁍"
        assert [entity.offset for entity in new_entities] == [0, 16, 30]
        for old, new in zip([first_entity, second_entity, third_entity], new_entities):
            assert new is not old
            assert new.type == old.type
            for key, value in kwargs.items():
                assert getattr(new, key) == value

    def test_equality(self):
        a = MessageEntity(MessageEntity.BOLD, 2, 3)
        b = MessageEntity(MessageEntity.BOLD, 2, 3)
        c = MessageEntity(MessageEntity.CODE, 2, 3)
        d = MessageEntity(MessageEntity.CODE, 5, 6)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
