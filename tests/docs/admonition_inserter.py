#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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

# This module is intentionally named without "test_" prefix.
# These tests are supposed to be run on GitHub when building docs.
# The tests require Python 3.9+ (just like AdmonitionInserter being tested),
# so they cannot be included in the main suite while older versions of Python are supported.

import collections.abc

import pytest

import telegram.ext
from docs.auxil.admonition_inserter import AdmonitionInserter


@pytest.fixture(scope="session")
def admonition_inserter():
    return AdmonitionInserter()


class TestAdmonitionInserter:
    """This is a minimal-effort test to ensure that the `AdmonitionInserter`
    used for automatically inserting references in the docs works as expected.

    It does not aim to cover all links in the documentation, but rather checks that several special
    cases (which where discovered during the implementation of `AdmonitionInserter`) are handled
    correctly.
    """

    def test_admonitions_dict(self, admonition_inserter):
        # there are keys for every type of admonition
        assert len(admonition_inserter.admonitions) == len(
            admonition_inserter.ALL_ADMONITION_TYPES
        )

        # for each type of admonitions, there is at least one entry
        # ({class/method: admonition text})
        for admonition_type in admonition_inserter.ALL_ADMONITION_TYPES:
            assert admonition_type in admonition_inserter.admonitions
            assert len(admonition_inserter.admonitions[admonition_type].keys()) > 0

        # checking class admonitions
        for admonition_type in admonition_inserter.CLASS_ADMONITION_TYPES:
            # keys are telegram classes
            for cls in admonition_inserter.admonitions[admonition_type]:
                # Test classes crop up in AppBuilder, they can't come from code being tested.
                if "tests." in str(cls):
                    continue

                assert isinstance(cls, type)
                assert str(cls).startswith("<class 'telegram."), (
                    rf"Class {cls} does not belong to Telegram classes. Admonition:\n"
                    rf"{admonition_inserter.admonitions[admonition_type][cls]}"
                )

        # checking Bot method admonitions
        for admonition_type in admonition_inserter.METHOD_ADMONITION_TYPES:
            for method in admonition_inserter.admonitions[admonition_type]:
                assert isinstance(method, collections.abc.Callable)
                assert str(method).startswith("<function Bot."), (
                    f"Method {method} does not belong to methods that should get admonitions."
                    "Admonition:\n"
                    f"{admonition_inserter.admonitions[admonition_type][method]}"
                )

    @pytest.mark.parametrize(
        ("admonition_type", "cls", "link"),
        [
            (
                "available_in",
                telegram.ChatMember,
                ":attr:`telegram.ChatMemberUpdated.new_chat_member`",
            ),
            (
                "available_in",
                telegram.ChatMemberAdministrator,
                ":attr:`telegram.ChatMemberUpdated.new_chat_member`",
            ),
            (
                "available_in",
                telegram.Sticker,
                ":attr:`telegram.StickerSet.stickers`",  # Tuple[telegram.Sticker]
            ),
            (
                "available_in",
                telegram.ResidentialAddress,  # mentioned on the second line of docstring of .data
                ":attr:`telegram.EncryptedPassportElement.data`",
            ),
            (
                "returned_in",
                telegram.StickerSet,
                ":meth:`telegram.Bot.get_sticker_set`",
            ),
            (
                "returned_in",
                telegram.ChatMember,
                ":meth:`telegram.Bot.get_chat_member`",
            ),
            (
                "returned_in",
                telegram.ChatMemberOwner,
                ":meth:`telegram.Bot.get_chat_member`",  # subclass
            ),
            (
                "returned_in",
                telegram.Message,
                ":meth:`telegram.Bot.edit_message_live_location`",  # Union[Message, bool]
            ),
            (
                "returned_in",
                telegram.ext.Application,
                ":meth:`telegram.ext.ApplicationBuilder.build`",  # <class 'types.GenericAlias'>
            ),
            (
                "shortcuts",
                telegram.Bot.edit_message_caption,
                # this method in CallbackQuery contains two return statements,
                # one of which is with Bot
                ":meth:`telegram.CallbackQuery.edit_message_caption`",
            ),
            (
                "use_in",
                telegram.InlineQueryResult,
                ":meth:`telegram.Bot.answer_web_app_query`",  # ForwardRef
            ),
            (
                "use_in",
                telegram.InputMediaPhoto,
                ":meth:`telegram.Bot.send_media_group`",  # Sequence[Union[...]]
            ),
            (
                "use_in",
                telegram.MaskPosition,
                ":meth:`telegram.Bot.add_sticker_to_set`",  # optional
            ),
            (
                "use_in",
                telegram.Sticker,
                ":meth:`telegram.Bot.get_file`",  # .file_id with lots of piped types
            ),
            (
                "use_in",
                telegram.ext.BasePersistence,
                ":meth:`telegram.ext.ApplicationBuilder.persistence`",
            ),
            ("use_in", telegram.ext.Defaults, ":meth:`telegram.ext.ApplicationBuilder.defaults`"),
            (
                "use_in",
                telegram.ext.JobQueue,
                ":meth:`telegram.ext.ApplicationBuilder.job_queue`",  # TypeVar
            ),
            (
                "use_in",
                telegram.ext.PicklePersistence,  # subclass
                ":meth:`telegram.ext.ApplicationBuilder.persistence`",
            ),
        ],
    )
    def test_check_presence(self, admonition_inserter, admonition_type, cls, link):
        """Checks if a given link is present in the admonition of a given type for a given
        class.
        """
        admonitions = admonition_inserter.admonitions

        assert cls in admonitions[admonition_type]

        # exactly one of the lines in the admonition for this class must consist of the link
        # (this is a stricter check than just checking if the entire admonition contains the link)
        lines_with_link = [
            line
            for line in admonitions[admonition_type][cls].splitlines()
            # remove whitespaces and occasional bullet list marker
            if line.strip().removeprefix("* ") == link
        ]
        assert lines_with_link, (
            f"Class {cls}, does not have link {link} in a {admonition_type} admonition:\n"
            f"{admonitions[admonition_type][cls]}"
        )
        assert len(lines_with_link) == 1, (
            f"Class {cls}, must contain only one link {link} in a {admonition_type} admonition:\n"
            f"{admonitions[admonition_type][cls]}"
        )

    @pytest.mark.parametrize(
        ("admonition_type", "cls", "link"),
        [
            (
                "returned_in",
                telegram.ext.CallbackContext,
                # -> Application[BT, CCT, UD, CD, BD, JQ].
                # In this case classes inside square brackets must not be parsed
                ":meth:`telegram.ext.ApplicationBuilder.build`",
            ),
        ],
    )
    def test_check_absence(self, admonition_inserter, admonition_type, cls, link):
        """Checks if a given link is **absent** in the admonition of a given type for a given
        class.

        If a given class has no admonition of this type at all, the test will also pass.
        """
        admonitions = admonition_inserter.admonitions

        assert not (
            cls in admonitions[admonition_type]
            and [
                line
                for line in admonitions[admonition_type][cls].splitlines()
                # remove whitespaces and occasional bullet list marker
                if line.strip().removeprefix("* ") == link
            ]
        ), (
            f"Class {cls} is not supposed to have link {link} in a {admonition_type} admonition:\n"
            f"{admonitions[admonition_type][cls]}"
        )
