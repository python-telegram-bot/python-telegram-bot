#!/usr/bin/env python
#
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
"""This module contains classes related to unique gifs."""

import datetime as dtm
from typing import ClassVar

from telegram import constants
from telegram._chat import Chat
from telegram._files.sticker import Sticker
from telegram._telegramobject import TelegramObject
from telegram._utils import enum
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class UniqueGiftColors(TelegramObject):
    """This object contains information about the color scheme for a user's name, message replies
    and link previews based on a unique gift.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`model_custom_emoji_id`, :attr:`symbol_custom_emoji_id`,
    :attr:`light_theme_main_color`, :attr:`light_theme_other_colors`,
    :attr:`dark_theme_main_color`, and :attr:`dark_theme_other_colors` are equal.

    .. versionadded:: 22.6

    Args:
        model_custom_emoji_id (:obj:`str`): Custom emoji identifier of the unique gift's model.
        symbol_custom_emoji_id (:obj:`str`): Custom emoji identifier of the unique gift's symbol.
        light_theme_main_color (:obj:`int`): Main color used in light themes; RGB format.
        light_theme_other_colors (Sequence[:obj:`int`]): List of 1-3 additional colors used in
            light themes; RGB format. |sequenceclassargs|
        dark_theme_main_color (:obj:`int`): Main color used in dark themes; RGB format.
        dark_theme_other_colors (Sequence[:obj:`int`]): List of 1-3 additional colors used in dark
            themes; RGB format. |sequenceclassargs|

    Attributes:
        model_custom_emoji_id (:obj:`str`): Custom emoji identifier of the unique gift's model.
        symbol_custom_emoji_id (:obj:`str`): Custom emoji identifier of the unique gift's symbol.
        light_theme_main_color (:obj:`int`): Main color used in light themes; RGB format.
        light_theme_other_colors (Tuple[:obj:`int`]): Tuple of 1-3 additional colors used in
            light themes; RGB format.
        dark_theme_main_color (:obj:`int`): Main color used in dark themes; RGB format.
        dark_theme_other_colors (Tuple[:obj:`int`]): Tuple of 1-3 additional colors used in dark
            themes; RGB format.
    """

    model_custom_emoji_id: str = tg_field(compare=True)
    symbol_custom_emoji_id: str = tg_field(compare=True)
    light_theme_main_color: int = tg_field(compare=True)
    light_theme_other_colors: tuple[int, ...] = tg_field(
        compare=True, converter=parse_sequence_arg
    )
    dark_theme_main_color: int = tg_field(compare=True)
    dark_theme_other_colors: tuple[int, ...] = tg_field(compare=True, converter=parse_sequence_arg)


@tg_dataclass()
class UniqueGiftModel(TelegramObject):
    """This object describes the model of a unique gift.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`name`, :attr:`sticker` and :attr:`rarity_per_mille` are equal.

    .. versionadded:: 22.1

    Args:
        name (:obj:`str`): Name of the model.
        sticker (:class:`telegram.Sticker`): The sticker that represents the unique gift.
        rarity_per_mille (:obj:`int`): The number of unique gifts that receive this
            model for every ``1000`` gifts upgraded. Always ``0`` for crafted gifts.
        rarity (:obj:`str`, optional): Rarity of the model if it is a crafted model.
            Currently, can be :tg-const:`telegram.constants.UniqueGiftModelRarity.UNCOMMON`,
            :tg-const:`telegram.constants.UniqueGiftModelRarity.RARE`,
            :tg-const:`telegram.constants.UniqueGiftModelRarity.EPIC`,
            or :tg-const:`telegram.constants.UniqueGiftModelRarity.LEGENDARY`.

            .. versionadded:: 22.7

    Attributes:
        name (:obj:`str`): Name of the model.
        sticker (:class:`telegram.Sticker`): The sticker that represents the unique gift.
        rarity_per_mille (:obj:`int`): The number of unique gifts that receive this
            model for every ``1000`` gifts upgraded. Always ``0`` for crafted gifts.
        rarity (:obj:`str`): Optional. Rarity of the model if it is a crafted model.
            Currently, can be :tg-const:`telegram.constants.UniqueGiftModelRarity.UNCOMMON`,
            :tg-const:`telegram.constants.UniqueGiftModelRarity.RARE`,
            :tg-const:`telegram.constants.UniqueGiftModelRarity.EPIC`,
            or :tg-const:`telegram.constants.UniqueGiftModelRarity.LEGENDARY`.

            .. versionadded:: 22.7
    """

    @staticmethod
    def _rarity_converter(value: str | None) -> str | None:
        return enum.get_member(constants.UniqueGiftModelRarity, value, value)

    # Required
    name: str = tg_field(compare=True)
    sticker: Sticker = tg_field(compare=True)
    rarity_per_mille: int = tg_field(compare=True)
    # Optional
    rarity: str | None = tg_field(default=None, converter=_rarity_converter)


@tg_dataclass()
class UniqueGiftSymbol(TelegramObject):
    """This object describes the symbol shown on the pattern of a unique gift.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`name`, :attr:`sticker` and :attr:`rarity_per_mille` are equal.

    .. versionadded:: 22.1

    Args:
        name (:obj:`str`): Name of the symbol.
        sticker (:class:`telegram.Sticker`): The sticker that represents the unique gift.
        rarity_per_mille (:obj:`int`): The number of unique gifts that receive this
            model for every ``1000`` gifts upgraded.

    Attributes:
        name (:obj:`str`): Name of the symbol.
        sticker (:class:`telegram.Sticker`): The sticker that represents the unique gift.
        rarity_per_mille (:obj:`int`): The number of unique gifts that receive this
            model for every ``1000`` gifts upgraded.

    """

    name: str = tg_field(compare=True)
    sticker: Sticker = tg_field(compare=True)
    rarity_per_mille: int = tg_field(compare=True)


@tg_dataclass()
class UniqueGiftBackdropColors(TelegramObject):
    """This object describes the colors of the backdrop of a unique gift.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`center_color`, :attr:`edge_color`, :attr:`symbol_color`,
    and :attr:`text_color` are equal.

    .. versionadded:: 22.1

    Args:
        center_color (:obj:`int`): The color in the center of the backdrop in RGB format.
        edge_color (:obj:`int`): The color on the edges of the backdrop in RGB format.
        symbol_color (:obj:`int`): The color to be applied to the symbol in RGB format.
        text_color (:obj:`int`): The color for the text on the backdrop in RGB format.

    Attributes:
        center_color (:obj:`int`): The color in the center of the backdrop in RGB format.
        edge_color (:obj:`int`): The color on the edges of the backdrop in RGB format.
        symbol_color (:obj:`int`): The color to be applied to the symbol in RGB format.
        text_color (:obj:`int`): The color for the text on the backdrop in RGB format.

    """

    center_color: int = tg_field(compare=True)
    edge_color: int = tg_field(compare=True)
    symbol_color: int = tg_field(compare=True)
    text_color: int = tg_field(compare=True)


@tg_dataclass()
class UniqueGiftBackdrop(TelegramObject):
    """This object describes the backdrop of a unique gift.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`name`, :attr:`colors`, and :attr:`rarity_per_mille` are equal.

    .. versionadded:: 22.1

    Args:
        name (:obj:`str`): Name of the backdrop.
        colors (:class:`telegram.UniqueGiftBackdropColors`): Colors of the backdrop.
        rarity_per_mille (:obj:`int`): The number of unique gifts that receive this backdrop
            for every ``1000`` gifts upgraded.

    Attributes:
        name (:obj:`str`): Name of the backdrop.
        colors (:class:`telegram.UniqueGiftBackdropColors`): Colors of the backdrop.
        rarity_per_mille (:obj:`int`): The number of unique gifts that receive this backdrop
            for every ``1000`` gifts upgraded.

    """

    name: str = tg_field(compare=True)
    colors: UniqueGiftBackdropColors = tg_field(compare=True)
    rarity_per_mille: int = tg_field(compare=True)


@tg_dataclass()
class UniqueGift(TelegramObject):
    """This object describes a unique gift that was upgraded from a regular gift.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`base_name`, :attr:`name`, :attr:`number`, :class:`model`,
    :attr:`symbol`, and :attr:`backdrop` are equal.

    .. versionadded:: 22.1

    .. versionchanged:: 22.7
        :attr:`gift_id` is now a positional argument.

    Args:
        gift_id (:obj:`str`): Identifier of the regular gift from which the gift was upgraded.

            .. versionadded:: 22.6
        base_name (:obj:`str`): Human-readable name of the regular gift from which this unique
            gift was upgraded.
        name (:obj:`str`): Unique name of the gift. This name can be used
            in ``https://t.me/nft/...`` links and story areas.
        number (:obj:`int`): Unique number of the upgraded gift among gifts upgraded from the
            same regular gift.
        model (:class:`UniqueGiftModel`): Model of the gift.
        symbol (:class:`UniqueGiftSymbol`): Symbol of the gift.
        backdrop (:class:`UniqueGiftBackdrop`): Backdrop of the gift.
        publisher_chat (:class:`telegram.Chat`, optional): Information about the chat that
            published the gift.

            .. versionadded:: 22.4
        is_premium (:obj:`bool`, optional): :obj:`True`, if the original regular gift was
            exclusively purchaseable by Telegram Premium subscribers.

            .. versionadded:: 22.6
        is_from_blockchain (:obj:`bool`, optional): :obj:`True`, if the gift is assigned from the
            TON blockchain and can't be resold or transferred in Telegram.

            .. versionadded:: 22.6
        colors (:class:`telegram.UniqueGiftColors`, optional): The color scheme that can be used
            by the gift's owner for the chat's name, replies to messages and link previews; for
            business account gifts and gifts that are currently on sale only.

            .. versionadded:: 22.6
        is_burned (:obj:`bool`, optional): :obj:`True`, if the gift was used to craft another
            gift and isn't available anymore.

            .. versionadded:: 22.7

    Attributes:
        gift_id (:obj:`str`): Identifier of the regular gift from which the gift was upgraded.

            .. versionadded:: 22.6
        base_name (:obj:`str`): Human-readable name of the regular gift from which this unique
            gift was upgraded.
        name (:obj:`str`): Unique name of the gift. This name can be used
            in ``https://t.me/nft/...`` links and story areas.
        number (:obj:`int`): Unique number of the upgraded gift among gifts upgraded from the
            same regular gift.
        model (:class:`telegram.UniqueGiftModel`): Model of the gift.
        symbol (:class:`telegram.UniqueGiftSymbol`): Symbol of the gift.
        backdrop (:class:`telegram.UniqueGiftBackdrop`): Backdrop of the gift.
        publisher_chat (:class:`telegram.Chat`): Optional. Information about the chat that
            published the gift.

            .. versionadded:: 22.4
        is_premium (:obj:`bool`): Optional. :obj:`True`, if the original regular gift was
            exclusively purchaseable by Telegram Premium subscribers.

            .. versionadded:: 22.6
        is_from_blockchain (:obj:`bool`): Optional. :obj:`True`, if the gift is assigned from the
            TON blockchain and can't be resold or transferred in Telegram.

            .. versionadded:: 22.6
        colors (:class:`telegram.UniqueGiftColors`): Optional. The color scheme that can be used
            by the gift's owner for the chat's name, replies to messages and link previews; for
            business account gifts and gifts that are currently on sale only.

            .. versionadded:: 22.6
        is_burned (:obj:`bool`): Optional. :obj:`True`, if the gift was used to craft another
            gift and isn't available anymore.

            .. versionadded:: 22.7
    """

    # Required
    gift_id: str = tg_field()
    base_name: str = tg_field(compare=True)
    name: str = tg_field(compare=True)
    number: int = tg_field(compare=True)
    model: UniqueGiftModel = tg_field(compare=True)
    symbol: UniqueGiftSymbol = tg_field(compare=True)
    backdrop: UniqueGiftBackdrop = tg_field(compare=True)
    # Optional
    publisher_chat: Chat | None = tg_field(default=None)
    is_from_blockchain: bool | None = tg_field(default=None)
    is_premium: bool | None = tg_field(default=None)
    colors: UniqueGiftColors | None = tg_field(default=None)
    is_burned: bool | None = tg_field(default=None)


@tg_dataclass()
class UniqueGiftInfo(TelegramObject):
    """Describes a service message about a unique gift that was sent or received.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`gift`, and :attr:`origin` are equal.

    .. versionadded:: 22.1

    .. versionremoved:: 22.7
        Removed argument and attribute ``last_resale_star_count`` deprecated since Bot API 9.3.

    Args:
        gift (:class:`UniqueGift`): Information about the gift.
        origin (:obj:`str`): Origin of the gift. Currently, either :attr:`UPGRADE` for gifts
            upgraded from regular gifts, :attr:`TRANSFER` for gifts transferred from other users
            or channels, :attr:`RESALE` for gifts bought from other users,
            :attr:`GIFTED_UPGRADE` for upgrades purchased after the gift was sent, or :attr:`OFFER`
            for gifts bought or sold through gift purchase offers

            .. versionchanged:: 22.3
                The :attr:`RESALE` origin was added.
            .. versionchanged:: 22.6
                Bot API 9.3 added the :attr:`GIFTED_UPGRADE` and :attr:`OFFER` origins.
        owned_gift_id (:obj:`str`, optional) Unique identifier of the received gift for the
            bot; only present for gifts received on behalf of business accounts.
        transfer_star_count (:obj:`int`, optional): Number of Telegram Stars that must be paid
            to transfer the gift; omitted if the bot cannot transfer the gift.
        last_resale_currency (:obj:`str`, optional): For gifts bought from other users, the
            currency in which the payment for the gift was done. Currently, one of ``XTR`` for
            Telegram Stars or ``TON`` for toncoins.

            .. versionadded:: 22.6
        last_resale_amount (:obj:`int`, optional): For gifts bought from other users, the price
            paid for the gift in either Telegram Stars or nanotoncoins.

            .. versionadded:: 22.6
        next_transfer_date (:obj:`datetime.datetime`, optional): Date when the gift can be
            transferred. If it's in the past, then the gift can be transferred now.
            |datetime_localization|

            .. versionadded:: 22.3

    Attributes:
        gift (:class:`UniqueGift`): Information about the gift.
        origin (:obj:`str`): Origin of the gift. Currently, either :attr:`UPGRADE` for gifts
            upgraded from regular gifts, :attr:`TRANSFER` for gifts transferred from other users
            or channels, :attr:`RESALE` for gifts bought from other users,
            :attr:`GIFTED_UPGRADE` for upgrades purchased after the gift was sent, or :attr:`OFFER`
            for gifts bought or sold through gift purchase offers

            .. versionchanged:: 22.3
                The :attr:`RESALE` origin was added.
            .. versionchanged:: 22.6
                Bot API 9.3 added the :attr:`GIFTED_UPGRADE` and :attr:`OFFER` origins.
        owned_gift_id (:obj:`str`) Optional. Unique identifier of the received gift for the
            bot; only present for gifts received on behalf of business accounts.
        transfer_star_count (:obj:`int`): Optional. Number of Telegram Stars that must be paid
            to transfer the gift; omitted if the bot cannot transfer the gift.
        last_resale_currency (:obj:`str`): Optional. For gifts bought from other users, the
            currency in which the payment for the gift was done. Currently, one of ``XTR`` for
            Telegram Stars or ``TON`` for toncoins.

            .. versionadded:: 22.6
        last_resale_amount (:obj:`int`): Optional. For gifts bought from other users, the price
            paid for the gift in either Telegram Stars or nanotoncoins.

            .. versionadded:: 22.6
        next_transfer_date (:obj:`datetime.datetime`): Optional. Date when the gift can be
            transferred. If it's in the past, then the gift can be transferred now.
            |datetime_localization|

            .. versionadded:: 22.3
    """

    GIFTED_UPGRADE: ClassVar[str] = constants.UniqueGiftInfoOrigin.GIFTED_UPGRADE
    """:const:`telegram.constants.UniqueGiftInfoOrigin.GIFTED_UPGRADE`

    .. versionadded:: 22.6
    """
    OFFER: ClassVar[str] = constants.UniqueGiftInfoOrigin.OFFER
    """:const:`telegram.constants.UniqueGiftInfoOrigin.OFFER`

    .. versionadded:: 22.6
    """
    RESALE: ClassVar[str] = constants.UniqueGiftInfoOrigin.RESALE
    """:const:`telegram.constants.UniqueGiftInfoOrigin.RESALE`

    .. versionadded:: 22.3
    """
    TRANSFER: ClassVar[str] = constants.UniqueGiftInfoOrigin.TRANSFER
    """:const:`telegram.constants.UniqueGiftInfoOrigin.TRANSFER`"""
    UPGRADE: ClassVar[str] = constants.UniqueGiftInfoOrigin.UPGRADE
    """:const:`telegram.constants.UniqueGiftInfoOrigin.UPGRADE`"""

    @staticmethod
    def _origin_converter(value: str) -> str:
        return enum.get_member(constants.UniqueGiftInfoOrigin, value, value)

    # Required
    gift: UniqueGift = tg_field(compare=True)
    origin: str = tg_field(compare=True, converter=_origin_converter)
    # Optional
    owned_gift_id: str | None = tg_field(default=None)
    transfer_star_count: int | None = tg_field(default=None)
    next_transfer_date: dtm.datetime | None = tg_field(default=None)
    last_resale_currency: str | None = tg_field(default=None)
    last_resale_amount: int | None = tg_field(default=None)
