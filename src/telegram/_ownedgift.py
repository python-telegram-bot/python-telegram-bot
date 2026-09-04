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
"""This module contains objects that represent owned gifts."""

import datetime as dtm
from typing import ClassVar

from telegram import constants
from telegram._gifts import Gift
from telegram._messageentity import MessageEntity
from telegram._telegramobject import TelegramObject
from telegram._uniquegift import UniqueGift
from telegram._user import User
from telegram._utils import enum
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram._utils.entities import parse_message_entities, parse_message_entity


@tg_dataclass()
class OwnedGift(TelegramObject):
    """This object describes a gift received and owned by a user or a chat. Currently, it
    can be one of:

    * :class:`telegram.OwnedGiftRegular`
    * :class:`telegram.OwnedGiftUnique`

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` is equal.

    .. versionadded:: 22.1

    Args:
        type (:obj:`str`): Type of the owned gift.

    Attributes:
        type (:obj:`str`): Type of the owned gift.
    """

    REGULAR: ClassVar[str] = constants.OwnedGiftType.REGULAR
    """:const:`telegram.constants.OwnedGiftType.REGULAR`"""
    UNIQUE: ClassVar[str] = constants.OwnedGiftType.UNIQUE
    """:const:`telegram.constants.OwnedGiftType.UNIQUE`"""

    __DE_JSON_DISPATCH__: ClassVar[tuple[str, dict[str, str]] | None] = (
        "type",
        {
            "regular": "OwnedGiftRegular",
            "unique": "OwnedGiftUnique",
        },
    )

    @staticmethod
    def _type_converter(value: str) -> str:
        return enum.get_member(constants.OwnedGiftType, value, value)

    type: str = tg_field(compare=True, converter=_type_converter)


@tg_dataclass()
class OwnedGifts(TelegramObject):
    """Contains the list of gifts received and owned by a user or a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`total_count` and :attr:`gifts` are equal.

    .. versionadded:: 22.1

    Args:
        total_count (:obj:`int`): The total number of gifts owned by the user or the chat.
        gifts (Sequence[:class:`telegram.OwnedGift`]): The list of gifts.
        next_offset (:obj:`str`, optional): Offset for the next request. If empty,
            then there are no more results.

    Attributes:
        total_count (:obj:`int`): The total number of gifts owned by the user or the chat.
        gifts (Sequence[:class:`telegram.OwnedGift`]): The list of gifts.
        next_offset (:obj:`str`): Optional. Offset for the next request. If empty,
            then there are no more results.
    """

    total_count: int = tg_field(compare=True)
    gifts: tuple[OwnedGift, ...] = tg_field(compare=True, converter=parse_sequence_arg)
    next_offset: str | None = tg_field(default=None)


@tg_dataclass()
class OwnedGiftRegular(OwnedGift):
    """Describes a regular gift owned by a user or a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`gift` and :attr:`send_date` are equal.

    .. versionadded:: 22.1

    Args:
        gift (:class:`telegram.Gift`): Information about the regular gift.
        owned_gift_id (:obj:`str`, optional): Unique identifier of the gift for the bot; for
            gifts received on behalf of business accounts only.
        sender_user (:class:`telegram.User`, optional): Sender of the gift if it is a known user.
        send_date (:obj:`datetime.datetime`): Date the gift was sent as :class:`datetime.datetime`.
            |datetime_localization|.
        text (:obj:`str`, optional): Text of the message that was added to the gift.
        entities (Sequence[:class:`telegram.MessageEntity`], optional): Special entities that
            appear in the text.
        is_private (:obj:`bool`, optional): :obj:`True`, if the sender and gift text are shown
            only to the gift receiver; otherwise, everyone will be able to see them.
        is_saved (:obj:`bool`, optional): :obj:`True`, if the gift is displayed on the account's
            profile page; for gifts received on behalf of business accounts only.
        can_be_upgraded (:obj:`bool`, optional): :obj:`True`, if the gift can be upgraded to a
            unique gift; for gifts received on behalf of business accounts only.
        was_refunded (:obj:`bool`, optional): :obj:`True`, if the gift was refunded and isn't
            available anymore.
        convert_star_count (:obj:`int`, optional): Number of Telegram Stars that can be
            claimed by the receiver instead of the gift; omitted if the gift cannot be converted
            to Telegram Stars; for gifts received on behalf of business accounts only.
        prepaid_upgrade_star_count (:obj:`int`, optional): Number of Telegram Stars that were
            paid for the ability to upgrade the gift.
        is_upgrade_separate (:obj:`bool`, optional): :obj:`True`, if the gift's upgrade was
            purchased after the gift was sent; for gifts received on behalf of business accounts

            .. versionadded:: 22.6
        unique_gift_number (:obj:`int`, optional): Unique number reserved for this gift when
            upgraded. See the number field in :class:`~telegram.UniqueGift`

            ... versionadded:: 22.6

    Attributes:
        type (:obj:`str`): Type of the gift, always :attr:`~telegram.OwnedGift.REGULAR`.
        gift (:class:`telegram.Gift`): Information about the regular gift.
        owned_gift_id (:obj:`str`): Optional. Unique identifier of the gift for the bot; for
            gifts received on behalf of business accounts only.
        sender_user (:class:`telegram.User`): Optional. Sender of the gift if it is a known user.
        send_date (:obj:`datetime.datetime`): Date the gift was sent as :class:`datetime.datetime`.
            |datetime_localization|.
        text (:obj:`str`): Optional. Text of the message that was added to the gift.
        entities (Sequence[:class:`telegram.MessageEntity`]): Optional. Special entities that
            appear in the text.
        is_private (:obj:`bool`): Optional. :obj:`True`, if the sender and gift text are shown
            only to the gift receiver; otherwise, everyone will be able to see them.
        is_saved (:obj:`bool`): Optional. :obj:`True`, if the gift is displayed on the account's
            profile page; for gifts received on behalf of business accounts only.
        can_be_upgraded (:obj:`bool`): Optional. :obj:`True`, if the gift can be upgraded to a
            unique gift; for gifts received on behalf of business accounts only.
        was_refunded (:obj:`bool`): Optional. :obj:`True`, if the gift was refunded and isn't
            available anymore.
        convert_star_count (:obj:`int`): Optional. Number of Telegram Stars that can be
            claimed by the receiver instead of the gift; omitted if the gift cannot be converted
            to Telegram Stars; for gifts received on behalf of business accounts only.
        prepaid_upgrade_star_count (:obj:`int`): Optional. Number of Telegram Stars that were
            paid for the ability to upgrade the gift.
        is_upgrade_separate (:obj:`bool`): Optional. :obj:`True`, if the gift's upgrade was
            purchased after the gift was sent; for gifts received on behalf of business accounts

            .. versionadded:: 22.6
        unique_gift_number (:obj:`int`): Optional. Unique number reserved for this gift when
            upgraded. See the number field in :class:`~telegram.UniqueGift`

            ... versionadded:: 22.6

    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=OwnedGift.REGULAR)

    # Required
    gift: Gift = tg_field(compare=True)
    send_date: dtm.datetime = tg_field(compare=True)

    # Optional
    owned_gift_id: str | None = tg_field(default=None)
    sender_user: User | None = tg_field(default=None)
    text: str | None = tg_field(default=None)
    entities: tuple[MessageEntity, ...] = tg_field(default=None, converter=parse_sequence_arg)
    is_private: bool | None = tg_field(default=None)
    is_saved: bool | None = tg_field(default=None)
    can_be_upgraded: bool | None = tg_field(default=None)
    was_refunded: bool | None = tg_field(default=None)
    convert_star_count: int | None = tg_field(default=None)
    prepaid_upgrade_star_count: int | None = tg_field(default=None)
    is_upgrade_separate: bool | None = tg_field(default=None)
    unique_gift_number: int | None = tg_field(default=None)

    def parse_entity(self, entity: MessageEntity) -> str:
        """Returns the text in :attr:`text`
        from a given :class:`telegram.MessageEntity` of :attr:`entities`.

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice ``OwnedGiftRegular.text`` with the offset and length.)

        Args:
            entity (:class:`telegram.MessageEntity`): The entity to extract the text from. It must
                be an entity that belongs to :attr:`entities`.

        Returns:
            :obj:`str`: The text of the given entity.

        Raises:
            RuntimeError: If the owned gift has no text.

        """
        if not self.text:
            raise RuntimeError("This OwnedGiftRegular has no 'text'.")

        return parse_message_entity(self.text, entity)

    def parse_entities(self, types: list[str] | None = None) -> dict[MessageEntity, str]:
        """
        Returns a :obj:`dict` that maps :class:`telegram.MessageEntity` to :obj:`str`.
        It contains entities from this owned gift's text filtered by their ``type`` attribute as
        the key, and the text that each entity belongs to as the value of the :obj:`dict`.

        Note:
            This method should always be used instead of the :attr:`entities`
            attribute, since it calculates the correct substring from the message text based on
            UTF-16 codepoints. See :attr:`parse_entity` for more info.

        Args:
            types (list[:obj:`str`], optional): List of ``MessageEntity`` types as strings. If the
                    ``type`` attribute of an entity is contained in this list, it will be returned.
                    Defaults to :attr:`telegram.MessageEntity.ALL_TYPES`.

        Returns:
            dict[:class:`telegram.MessageEntity`, :obj:`str`]: A dictionary of entities mapped to
            the text that belongs to them, calculated based on UTF-16 codepoints.

        Raises:
            RuntimeError: If the owned gift has no text.

        """
        if not self.text:
            raise RuntimeError("This OwnedGiftRegular has no 'text'.")

        return parse_message_entities(self.text, self.entities, types)


@tg_dataclass()
class OwnedGiftUnique(OwnedGift):
    """
    Describes a unique gift received and owned by a user or a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`gift` and :attr:`send_date` are equal.

    .. versionadded:: 22.1

    Args:
        gift (:class:`telegram.UniqueGift`): Information about the unique gift.
        owned_gift_id (:obj:`str`, optional): Unique identifier of the received gift for the
            bot; for gifts received on behalf of business accounts only.
        sender_user (:class:`telegram.User`, optional): Sender of the gift if it is a known user.
        send_date (:obj:`datetime.datetime`): Date the gift was sent as :class:`datetime.datetime`.
            |datetime_localization|
        is_saved (:obj:`bool`, optional): :obj:`True`, if the gift is displayed on the account's
            profile page; for gifts received on behalf of business accounts only.
        can_be_transferred (:obj:`bool`, optional): :obj:`True`, if the gift can be transferred to
            another owner; for gifts received on behalf of business accounts only.
        transfer_star_count (:obj:`int`, optional): Number of Telegram Stars that must be paid
            to transfer the gift; omitted if the bot cannot transfer the gift.
        next_transfer_date (:obj:`datetime.datetime`, optional): Date when the gift can be
            transferred. If it's in the past, then the gift can be transferred now.
            |datetime_localization|
            .. versionadded:: 22.3

    Attributes:
        type (:obj:`str`): Type of the owned gift, always :tg-const:`~telegram.OwnedGift.UNIQUE`.
        gift (:class:`telegram.UniqueGift`): Information about the unique gift.
        owned_gift_id (:obj:`str`): Optional. Unique identifier of the received gift for the
            bot; for gifts received on behalf of business accounts only.
        sender_user (:class:`telegram.User`): Optional. Sender of the gift if it is a known user.
        send_date (:obj:`datetime.datetime`): Date the gift was sent as :class:`datetime.datetime`.
            |datetime_localization|
        is_saved (:obj:`bool`): Optional. :obj:`True`, if the gift is displayed on the account's
            profile page; for gifts received on behalf of business accounts only.
        can_be_transferred (:obj:`bool`): Optional. :obj:`True`, if the gift can be transferred to
            another owner; for gifts received on behalf of business accounts only.
        transfer_star_count (:obj:`int`): Optional. Number of Telegram Stars that must be paid
            to transfer the gift; omitted if the bot cannot transfer the gift.
        next_transfer_date (:obj:`datetime.datetime`): Optional. Date when the gift can be
            transferred. If it's in the past, then the gift can be transferred now.
            |datetime_localization|
            .. versionadded:: 22.3
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=OwnedGift.UNIQUE)

    # Required
    gift: UniqueGift = tg_field(compare=True)
    send_date: dtm.datetime = tg_field(compare=True)

    # Optional
    owned_gift_id: str | None = tg_field(default=None)
    sender_user: User | None = tg_field(default=None)
    is_saved: bool | None = tg_field(default=None)
    can_be_transferred: bool | None = tg_field(default=None)
    transfer_star_count: int | None = tg_field(default=None)
    next_transfer_date: dtm.datetime | None = tg_field(default=None)
