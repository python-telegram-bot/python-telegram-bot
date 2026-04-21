#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
# along with this program. If not, see [http://www.gnu.org/licenses/].

import datetime as dtm

from telegram import Chat, Message, MessageEntity, PollOptionAdded, PollOptionDeleted, User
from tests.auxil.slots import mro_slots


class _Base:
    poll_message = Message(1, dtm.datetime.utcnow(), Chat(1, Chat.PRIVATE), User(1, "user", False))
    option_persistent_id = "persistent-option-id"
    option_text = "Option A"
    option_text_entities = [MessageEntity(MessageEntity.BOLD, 0, 6)]


class TestPollOptionAddedWithoutRequest(_Base):
    def test_slot_behaviour(self):
        inst = PollOptionAdded(
            poll_message=self.poll_message,
            option_persistent_id=self.option_persistent_id,
            option_text=self.option_text,
            option_text_entities=self.option_text_entities,
        )
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst)))

    def test_de_json(self, offline_bot):
        inst = PollOptionAdded.de_json(
            {
                "poll_message": self.poll_message.to_dict(),
                "option_persistent_id": self.option_persistent_id,
                "option_text": self.option_text,
                "option_text_entities": [e.to_dict() for e in self.option_text_entities],
            },
            offline_bot,
        )
        assert inst.option_persistent_id == self.option_persistent_id
        assert inst.option_text == self.option_text
        assert inst.option_text_entities == tuple(self.option_text_entities)


class TestPollOptionDeletedWithoutRequest(_Base):
    def test_slot_behaviour(self):
        inst = PollOptionDeleted(
            poll_message=self.poll_message,
            option_persistent_id=self.option_persistent_id,
            option_text=self.option_text,
            option_text_entities=self.option_text_entities,
        )
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst)))

    def test_de_json(self, offline_bot):
        inst = PollOptionDeleted.de_json(
            {
                "poll_message": self.poll_message.to_dict(),
                "option_persistent_id": self.option_persistent_id,
                "option_text": self.option_text,
                "option_text_entities": [e.to_dict() for e in self.option_text_entities],
            },
            offline_bot,
        )
        assert inst.option_persistent_id == self.option_persistent_id
        assert inst.option_text == self.option_text
        assert inst.option_text_entities == tuple(self.option_text_entities)
