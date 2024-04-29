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
import pytest

from telegram import LinkPreviewOptions
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def link_preview_options():
    return LinkPreviewOptions(
        is_disabled=TestLinkPreviewOptionsBase.is_disabled,
        url=TestLinkPreviewOptionsBase.url,
        prefer_small_media=TestLinkPreviewOptionsBase.prefer_small_media,
        prefer_large_media=TestLinkPreviewOptionsBase.prefer_large_media,
        show_above_text=TestLinkPreviewOptionsBase.show_above_text,
    )


class TestLinkPreviewOptionsBase:
    is_disabled = True
    url = "https://www.example.com"
    prefer_small_media = True
    prefer_large_media = False
    show_above_text = True


class TestLinkPreviewOptionsWithoutRequest(TestLinkPreviewOptionsBase):
    def test_slot_behaviour(self, link_preview_options):
        a = link_preview_options
        for attr in a.__slots__:
            assert getattr(a, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(a)) == len(set(mro_slots(a))), "duplicate slot"

    def test_to_dict(self, link_preview_options):
        link_preview_options_dict = link_preview_options.to_dict()

        assert isinstance(link_preview_options_dict, dict)
        assert link_preview_options_dict["is_disabled"] == self.is_disabled
        assert link_preview_options_dict["url"] == self.url
        assert link_preview_options_dict["prefer_small_media"] == self.prefer_small_media
        assert link_preview_options_dict["prefer_large_media"] == self.prefer_large_media
        assert link_preview_options_dict["show_above_text"] == self.show_above_text

    def test_de_json(self, link_preview_options):
        link_preview_options_dict = {
            "is_disabled": self.is_disabled,
            "url": self.url,
            "prefer_small_media": self.prefer_small_media,
            "prefer_large_media": self.prefer_large_media,
            "show_above_text": self.show_above_text,
        }

        link_preview_options = LinkPreviewOptions.de_json(link_preview_options_dict, bot=None)
        assert link_preview_options.api_kwargs == {}

        assert link_preview_options.is_disabled == self.is_disabled
        assert link_preview_options.url == self.url
        assert link_preview_options.prefer_small_media == self.prefer_small_media
        assert link_preview_options.prefer_large_media == self.prefer_large_media
        assert link_preview_options.show_above_text == self.show_above_text

    def test_equality(self):
        a = LinkPreviewOptions(
            self.is_disabled,
            self.url,
            self.prefer_small_media,
            self.prefer_large_media,
            self.show_above_text,
        )
        b = LinkPreviewOptions(
            self.is_disabled,
            self.url,
            self.prefer_small_media,
            self.prefer_large_media,
            self.show_above_text,
        )
        c = LinkPreviewOptions(self.is_disabled)
        d = LinkPreviewOptions(
            False, self.url, self.prefer_small_media, self.prefer_large_media, self.show_above_text
        )

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
