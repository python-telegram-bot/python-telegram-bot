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
# along with this program.  If not, see [http://www.gnu.org/licenses/]
"""This module contains classes related to gifs sent by bots."""

from telegram._chat import Chat
from telegram._files.sticker import Sticker
from telegram._messageentity import MessageEntity
from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram._utils.entities import parse_message_entities, parse_message_entity


@tg_dataclass()
class GiftBackground(TelegramObject):
    """This object describes the background of a gift.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`center_color`, :attr:`edge_color` and :attr:`text_color` are
    equal.

    .. versionadded:: 22.6

    Args:
        center_color (:obj:`int`): Center color of the background in RGB format.
        edge_color (:obj:`int`): Edge color of the background in RGB format.
        text_color (:obj:`int`): Text color of the background in RGB format.

    Attributes:
        center_color (:obj:`int`): Center color of the background in RGB format.
        edge_color (:obj:`int`): Edge color of the background in RGB format.
        text_color (:obj:`int`): Text color of the background in RGB format.

    """

    center_color: int = tg_field(compare=True)
    edge_color: int = tg_field(compare=True)
    text_color: int = tg_field(compare=True)


@tg_dataclass()
class Gift(TelegramObject):
    """This object represents a gift that can be sent by the bot.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`id` is equal.

    .. versionadded:: 21.8

    Args:
        id (:obj:`str`): Unique identifier of the gift.
        sticker (:class:`~telegram.Sticker`): The sticker that represents the gift.
        star_count (:obj:`int`): The number of Telegram Stars that must be paid to send the
            sticker.
        total_count (:obj:`int`, optional): The total number of the gifts of this type that can be
            sent by all users; for limited gifts only.
        remaining_count (:obj:`int`, optional): The number of remaining gifts of this type that can
            be sent by all users; for limited gifts only.
        upgrade_star_count (:obj:`int`, optional): The number of Telegram Stars that must be paid
            to upgrade the gift to a unique one.

            .. versionadded:: 21.10
        publisher_chat (:class:`telegram.Chat`, optional): Information about the chat that
            published the gift.

            .. versionadded:: 22.4
        personal_total_count (:obj:`int`, optional): The total number of gifts of this type that
            can be sent by the bot; for limited gifts only.

            .. versionadded:: 22.6
        personal_remaining_count (:obj:`int`, optional): The number of remaining gifts of this type
            that can be sent by the bot; for limited gifts only.

            .. versionadded:: 22.6
        background (:class:`GiftBackground`, optional): Background of the gift.

            .. versionadded:: 22.6
        is_premium (:obj:`bool`, optional): :obj:`True`, if the gift can only be purchased by
            Telegram Premium subscribers.

            .. versionadded:: 22.6
        has_colors (:obj:`bool`, optional): :obj:`True`, if the gift can be used (after being
            upgraded) to customize a user's appearance.

            .. versionadded:: 22.6
        unique_gift_variant_count (:obj:`int`, optional): The total number of different unique
            gifts that can be obtained by upgrading the gift.

            .. versionadded:: 22.6

    Attributes:
        id (:obj:`str`): Unique identifier of the gift.
        sticker (:class:`~telegram.Sticker`): The sticker that represents the gift.
        star_count (:obj:`int`): The number of Telegram Stars that must be paid to send the
            sticker.
        total_count (:obj:`int`): Optional. The total number of the gifts of this type that can be
            sent by all users; for limited gifts only.
        remaining_count (:obj:`int`): Optional. The number of remaining gifts of this type that can
            be sent by all users; for limited gifts only.
        upgrade_star_count (:obj:`int`): Optional. The number of Telegram Stars that must be paid
            to upgrade the gift to a unique one.

            .. versionadded:: 21.10
        publisher_chat (:class:`telegram.Chat`): Optional. Information about the chat that
            published the gift.

            .. versionadded:: 22.4
        personal_total_count (:obj:`int`): Optional. The total number of gifts of this type that
            can be sent by the bot; for limited gifts only.

            .. versionadded:: 22.6
        personal_remaining_count (:obj:`int`): Optional. The number of remaining gifts of this type
            that can be sent by the bot; for limited gifts only.

            .. versionadded:: 22.6
        background (:class:`GiftBackground`): Optional. Background of the gift.

            .. versionadded:: 22.6
        is_premium (:obj:`bool`): Optional. :obj:`True`, if the gift can only be purchased by
            Telegram Premium subscribers.

            .. versionadded:: 22.6
        has_colors (:obj:`bool`): Optional. :obj:`True`, if the gift can be used (after being
            upgraded) to customize a user's appearance.

            .. versionadded:: 22.6
        unique_gift_variant_count (:obj:`int`): Optional. The total number of different unique
            gifts that can be obtained by upgrading the gift.

            .. versionadded:: 22.6

    """

    id: str = tg_field(compare=True)
    sticker: Sticker = tg_field()
    star_count: int = tg_field()
    total_count: int | None = tg_field(default=None)
    remaining_count: int | None = tg_field(default=None)
    upgrade_star_count: int | None = tg_field(default=None)
    publisher_chat: Chat | None = tg_field(default=None)
    personal_total_count: int | None = tg_field(default=None)
    personal_remaining_count: int | None = tg_field(default=None)
    background: GiftBackground | None = tg_field(default=None)
    is_premium: bool | None = tg_field(default=None)
    has_colors: bool | None = tg_field(default=None)
    unique_gift_variant_count: int | None = tg_field(default=None)


@tg_dataclass()
class Gifts(TelegramObject):
    """This object represent a list of gifts.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`gifts` are equal.

    .. versionadded:: 21.8

    Args:
        gifts (Sequence[:class:`Gift`]): The sequence of gifts.

    Attributes:
        gifts (tuple[:class:`Gift`]): The sequence of gifts.

    """

    gifts: tuple[Gift, ...] = tg_field(compare=True, converter=parse_sequence_arg)


@tg_dataclass()
class GiftInfo(TelegramObject):
    """Describes a service message about a regular gift that was sent or received.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`gift` is equal.

    .. versionadded:: 22.1

    Args:
        gift (:class:`Gift`): Information about the gift.
        owned_gift_id (:obj:`str`, optional): Unique identifier of the received gift for the bot;
            only present for gifts received on behalf of business accounts.
        convert_star_count (:obj:`int`, optional) Number of Telegram Stars that can be claimed by
            the receiver by converting the gift; omitted if conversion to Telegram Stars
            is impossible.
        prepaid_upgrade_star_count (:obj:`int`, optional): Number of Telegram Stars that were
            prepaid for the ability to upgrade the gift.
        can_be_upgraded (:obj:`bool`, optional): :obj:`True`, if the gift can be upgraded
            to a unique gift.
        text (:obj:`str`, optional): Text of the message that was added to the gift.
        entities (Sequence[:class:`telegram.MessageEntity`], optional): Special entities that
            appear in the text.
        is_private (:obj:`bool`, optional): :obj:`True`, if the sender and gift text are
            shown only to the gift receiver; otherwise, everyone will be able to see them.
        is_upgrade_separate (:obj:`bool`, optional): :obj:`True`, if the gift's upgrade was
            purchased after the gift was sent.

            .. versionadded:: 22.6
        unique_gift_number (:obj:`int`, optional): Unique number reserved for this gift when
            upgraded. See the number field in :class:`~telegram.UniqueGift`.

            .. versionadded:: 22.6

    Attributes:
        gift (:class:`Gift`): Information about the gift.
        owned_gift_id (:obj:`str`): Optional. Unique identifier of the received gift for the bot;
            only present for gifts received on behalf of business accounts.
        convert_star_count (:obj:`int`): Optional. Number of Telegram Stars that can be claimed by
            the receiver by converting the gift; omitted if conversion to Telegram Stars
            is impossible.
        prepaid_upgrade_star_count (:obj:`int`): Optional. Number of Telegram Stars that were
            prepaid for the ability to upgrade the gift.
        can_be_upgraded (:obj:`bool`): Optional. :obj:`True`, if the gift can be upgraded
            to a unique gift.
        text (:obj:`str`): Optional. Text of the message that was added to the gift.
        entities (Sequence[:class:`telegram.MessageEntity`]): Optional. Special entities that
            appear in the text.
        is_private (:obj:`bool`): Optional. :obj:`True`, if the sender and gift text are
            shown only to the gift receiver; otherwise, everyone will be able to see them.
        is_upgrade_separate (:obj:`bool`): Optional. :obj:`True`, if the gift's upgrade was
            purchased after the gift was sent.

            .. versionadded:: 22.6
        unique_gift_number (:obj:`int`): Optional. Unique number reserved for this gift when
            upgraded. See the number field in :class:`~telegram.UniqueGift`.

            .. versionadded:: 22.6

    """

    gift: Gift = tg_field(compare=True)
    owned_gift_id: str | None = tg_field(default=None)
    convert_star_count: int | None = tg_field(default=None)
    prepaid_upgrade_star_count: int | None = tg_field(default=None)
    can_be_upgraded: bool | None = tg_field(default=None)
    text: str | None = tg_field(default=None)
    entities: tuple[MessageEntity, ...] = tg_field(default=None, converter=parse_sequence_arg)
    is_private: bool | None = tg_field(default=None)
    unique_gift_number: int | None = tg_field(default=None)
    is_upgrade_separate: bool | None = tg_field(default=None)

    def parse_entity(self, entity: MessageEntity) -> str:
        """Returns the text in :attr:`text`
        from a given :class:`telegram.MessageEntity` of :attr:`entities`.

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice ``Message.text`` with the offset and length.)

        Args:
            entity (:class:`telegram.MessageEntity`): The entity to extract the text from. It must
                be an entity that belongs to :attr:`entities`.

        Returns:
            :obj:`str`: The text of the given entity.

        Raises:
            RuntimeError: If the gift info has no text.

        """
        if not self.text:
            raise RuntimeError("This GiftInfo has no 'text'.")

        return parse_message_entity(self.text, entity)

    def parse_entities(self, types: list[str] | None = None) -> dict[MessageEntity, str]:
        """
        Returns a :obj:`dict` that maps :class:`telegram.MessageEntity` to :obj:`str`.
        It contains entities from this gift info's text filtered by their ``type`` attribute as
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
            RuntimeError: If the gift info has no text.

        """
        if not self.text:
            raise RuntimeError("This GiftInfo has no 'text'.")

        return parse_message_entities(self.text, self.entities, types)


@tg_dataclass()
class AcceptedGiftTypes(TelegramObject):
    """This object describes the types of gifts that can be gifted to a user or a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`unlimited_gifts`, :attr:`limited_gifts`,
    :attr:`unique_gifts`, :attr:`premium_subscription` and :attr:`gifts_from_channels` are equal.

    .. versionadded:: 22.1
    .. versionchanged:: 22.6
        :attr:`gifts_from_channels` is now considered for equality checks.

    Args:
        unlimited_gifts (:class:`bool`): :obj:`True`, if unlimited regular gifts are accepted.
        limited_gifts (:class:`bool`): :obj:`True`, if limited regular gifts are accepted.
        unique_gifts (:class:`bool`): :obj:`True`, if unique gifts or gifts that can be upgraded
            to unique for free are accepted.
        premium_subscription (:class:`bool`): :obj:`True`, if a Telegram Premium subscription
            is accepted.
        gifts_from_channels (:obj:`bool`): :obj:`True`, if transfers of unique gifts from channels
            are accepted

            .. versionadded:: 22.6

    Attributes:
        unlimited_gifts (:class:`bool`): :obj:`True`, if unlimited regular gifts are accepted.
        limited_gifts (:class:`bool`): :obj:`True`, if limited regular gifts are accepted.
        unique_gifts (:class:`bool`): :obj:`True`, if unique gifts or gifts that can be upgraded
            to unique for free are accepted.
        premium_subscription (:class:`bool`): :obj:`True`, if a Telegram Premium subscription
            is accepted.
        gifts_from_channels (:obj:`bool`): :obj:`True`, if transfers of unique gifts from channels
            are accepted

            .. versionadded:: 22.6

    """

    unlimited_gifts: bool = tg_field(compare=True)
    limited_gifts: bool = tg_field(compare=True)
    unique_gifts: bool = tg_field(compare=True)
    premium_subscription: bool = tg_field(compare=True)
    gifts_from_channels: bool = tg_field(compare=True)
