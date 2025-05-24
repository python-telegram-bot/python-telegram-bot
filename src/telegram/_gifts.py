#!/usr/bin/env python
# pylint: disable=redefined-builtin
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
# along with this program.  If not, see [http://www.gnu.org/licenses/]
"""This module contains classes related to gifs sent by bots."""
from collections.abc import Sequence
from typing import TYPE_CHECKING, Optional

from telegram._files.sticker import Sticker
from telegram._messageentity import MessageEntity
from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import de_json_optional, de_list_optional, parse_sequence_arg
from telegram._utils.entities import parse_message_entities, parse_message_entity
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class Gift(TelegramObject):
    """This object represents a gift that can be sent by the bot.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`id` is equal.

    .. versionadded:: 21.8

    Args:
        id (:obj:`str`): Unique identifier of the gift
        sticker (:class:`~telegram.Sticker`): The sticker that represents the gift
        star_count (:obj:`int`): The number of Telegram Stars that must be paid to send the sticker
        total_count (:obj:`int`, optional): The total number of the gifts of this type that can be
            sent; for limited gifts only
        remaining_count (:obj:`int`, optional): The number of remaining gifts of this type that can
            be sent; for limited gifts only
        upgrade_star_count (:obj:`int`, optional): The number of Telegram Stars that must be paid
            to upgrade the gift to a unique one

            .. versionadded:: 21.10

    Attributes:
        id (:obj:`str`): Unique identifier of the gift
        sticker (:class:`~telegram.Sticker`): The sticker that represents the gift
        star_count (:obj:`int`): The number of Telegram Stars that must be paid to send the sticker
        total_count (:obj:`int`): Optional. The total number of the gifts of this type that can be
            sent; for limited gifts only
        remaining_count (:obj:`int`): Optional. The number of remaining gifts of this type that can
            be sent; for limited gifts only
        upgrade_star_count (:obj:`int`): Optional. The number of Telegram Stars that must be paid
            to upgrade the gift to a unique one

            .. versionadded:: 21.10

    """

    __slots__ = (
        "id",
        "remaining_count",
        "star_count",
        "sticker",
        "total_count",
        "upgrade_star_count",
    )

    def __init__(
        self,
        id: str,
        sticker: Sticker,
        star_count: int,
        total_count: Optional[int] = None,
        remaining_count: Optional[int] = None,
        upgrade_star_count: Optional[int] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.id: str = id
        self.sticker: Sticker = sticker
        self.star_count: int = star_count
        self.total_count: Optional[int] = total_count
        self.remaining_count: Optional[int] = remaining_count
        self.upgrade_star_count: Optional[int] = upgrade_star_count

        self._id_attrs = (self.id,)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: Optional["Bot"] = None) -> "Gift":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["sticker"] = de_json_optional(data.get("sticker"), Sticker, bot)
        return super().de_json(data=data, bot=bot)


class Gifts(TelegramObject):
    """This object represent a list of gifts.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`gifts` are equal.

    .. versionadded:: 21.8

    Args:
        gifts (Sequence[:class:`Gift`]): The sequence of gifts

    Attributes:
        gifts (tuple[:class:`Gift`]): The sequence of gifts

    """

    __slots__ = ("gifts",)

    def __init__(
        self,
        gifts: Sequence[Gift],
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.gifts: tuple[Gift, ...] = parse_sequence_arg(gifts)

        self._id_attrs = (self.gifts,)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: Optional["Bot"] = None) -> "Gifts":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["gifts"] = de_list_optional(data.get("gifts"), Gift, bot)
        return super().de_json(data=data, bot=bot)


class GiftInfo(TelegramObject):
    """Describes a service message about a regular gift that was sent or received.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`gift` is equal.

    .. versionadded:: 22.1

    Args:
        gift (:class:`Gift`): Information about the gift.
        owned_gift_id (:obj:`str`, optional): Unique identifier of the received gift for the bot;
            only present for gifts received on behalf of business accounts
        convert_star_count (:obj:`int`, optional) Number of Telegram Stars that can be claimed by
            the receiver by converting the gift; omitted if conversion to Telegram Stars
            is impossible
        prepaid_upgrade_star_count (:obj:`int`, optional): Number of Telegram Stars that were
            prepaid by the sender for the ability to upgrade the gift
        can_be_upgraded (:obj:`bool`, optional): :obj:`True`, if the gift can be upgraded
            to a unique gift.
        text (:obj:`str`, optional): Text of the message that was added to the gift.
        entities (Sequence[:class:`telegram.MessageEntity`], optional): Special entities that
            appear in the text.
        is_private (:obj:`bool`, optional): :obj:`True`, if the sender and gift text are
            shown only to the gift receiver; otherwise, everyone will be able to see them.

    Attributes:
        gift (:class:`Gift`): Information about the gift.
        owned_gift_id (:obj:`str`): Optional. Unique identifier of the received gift for the bot;
            only present for gifts received on behalf of business accounts
        convert_star_count (:obj:`int`): Optional. Number of Telegram Stars that can be claimed by
            the receiver by converting the gift; omitted if conversion to Telegram Stars
            is impossible
        prepaid_upgrade_star_count (:obj:`int`): Optional. Number of Telegram Stars that were
            prepaid by the sender for the ability to upgrade the gift
        can_be_upgraded (:obj:`bool`): Optional. :obj:`True`, if the gift can be upgraded
            to a unique gift.
        text (:obj:`str`): Optional. Text of the message that was added to the gift.
        entities (Sequence[:class:`telegram.MessageEntity`]): Optional. Special entities that
            appear in the text.
        is_private (:obj:`bool`): Optional. :obj:`True`, if the sender and gift text are
            shown only to the gift receiver; otherwise, everyone will be able to see them.

    """

    __slots__ = (
        "can_be_upgraded",
        "convert_star_count",
        "entities",
        "gift",
        "is_private",
        "owned_gift_id",
        "prepaid_upgrade_star_count",
        "text",
    )

    def __init__(
        self,
        gift: Gift,
        owned_gift_id: Optional[str] = None,
        convert_star_count: Optional[int] = None,
        prepaid_upgrade_star_count: Optional[int] = None,
        can_be_upgraded: Optional[bool] = None,
        text: Optional[str] = None,
        entities: Optional[Sequence[MessageEntity]] = None,
        is_private: Optional[bool] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        # Required
        self.gift: Gift = gift
        # Optional
        self.owned_gift_id: Optional[str] = owned_gift_id
        self.convert_star_count: Optional[int] = convert_star_count
        self.prepaid_upgrade_star_count: Optional[int] = prepaid_upgrade_star_count
        self.can_be_upgraded: Optional[bool] = can_be_upgraded
        self.text: Optional[str] = text
        self.entities: tuple[MessageEntity, ...] = parse_sequence_arg(entities)
        self.is_private: Optional[bool] = is_private

        self._id_attrs = (self.gift,)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: Optional["Bot"] = None) -> "GiftInfo":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["gift"] = de_json_optional(data.get("gift"), Gift, bot)
        data["entities"] = de_list_optional(data.get("entities"), MessageEntity, bot)

        return super().de_json(data=data, bot=bot)

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

    def parse_entities(self, types: Optional[list[str]] = None) -> dict[MessageEntity, str]:
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


class AcceptedGiftTypes(TelegramObject):
    """This object describes the types of gifts that can be gifted to a user or a chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`unlimited_gifts`, :attr:`limited_gifts`,
    :attr:`unique_gifts` and :attr:`premium_subscription` are equal.

    .. versionadded:: 22.1

    Args:
        unlimited_gifts (:class:`bool`): :obj:`True`, if unlimited regular gifts are accepted.
        limited_gifts (:class:`bool`): :obj:`True`, if limited regular gifts are accepted.
        unique_gifts (:class:`bool`): :obj:`True`, if unique gifts or gifts that can be upgraded
            to unique for free are accepted.
        premium_subscription (:class:`bool`): :obj:`True`, if a Telegram Premium subscription
            is accepted.

    Attributes:
        unlimited_gifts (:class:`bool`): :obj:`True`, if unlimited regular gifts are accepted.
        limited_gifts (:class:`bool`): :obj:`True`, if limited regular gifts are accepted.
        unique_gifts (:class:`bool`): :obj:`True`, if unique gifts or gifts that can be upgraded
            to unique for free are accepted.
        premium_subscription (:class:`bool`): :obj:`True`, if a Telegram Premium subscription
            is accepted.

    """

    __slots__ = (
        "limited_gifts",
        "premium_subscription",
        "unique_gifts",
        "unlimited_gifts",
    )

    def __init__(
        self,
        unlimited_gifts: bool,
        limited_gifts: bool,
        unique_gifts: bool,
        premium_subscription: bool,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.unlimited_gifts: bool = unlimited_gifts
        self.limited_gifts: bool = limited_gifts
        self.unique_gifts: bool = unique_gifts
        self.premium_subscription: bool = premium_subscription

        self._id_attrs = (
            self.unlimited_gifts,
            self.limited_gifts,
            self.unique_gifts,
            self.premium_subscription,
        )

        self._freeze()
