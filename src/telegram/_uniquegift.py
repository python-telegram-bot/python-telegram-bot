#!/usr/bin/env python
#
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
"""This module contains classes related to unique gifs."""
import datetime as dtm
from typing import TYPE_CHECKING, Final, Optional

from telegram import constants
from telegram._files.sticker import Sticker
from telegram._telegramobject import TelegramObject
from telegram._utils import enum
from telegram._utils.argumentparsing import de_json_optional
from telegram._utils.datetime import extract_tzinfo_from_defaults, from_timestamp
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class UniqueGiftModel(TelegramObject):
    """This object describes the model of a unique gift.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`name`, :attr:`sticker` and :attr:`rarity_per_mille` are equal.

    .. versionadded:: 22.1

    Args:
        name (:obj:`str`): Name of the model.
        sticker (:class:`telegram.Sticker`): The sticker that represents the unique gift.
        rarity_per_mille (:obj:`int`): The number of unique gifts that receive this
            model for every ``1000`` gifts upgraded.

    Attributes:
        name (:obj:`str`): Name of the model.
        sticker (:class:`telegram.Sticker`): The sticker that represents the unique gift.
        rarity_per_mille (:obj:`int`): The number of unique gifts that receive this
            model for every ``1000`` gifts upgraded.

    """

    __slots__ = (
        "name",
        "rarity_per_mille",
        "sticker",
    )

    def __init__(
        self,
        name: str,
        sticker: Sticker,
        rarity_per_mille: int,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.name: str = name
        self.sticker: Sticker = sticker
        self.rarity_per_mille: int = rarity_per_mille

        self._id_attrs = (self.name, self.sticker, self.rarity_per_mille)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: Optional["Bot"] = None) -> "UniqueGiftModel":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["sticker"] = de_json_optional(data.get("sticker"), Sticker, bot)

        return super().de_json(data=data, bot=bot)


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

    __slots__ = (
        "name",
        "rarity_per_mille",
        "sticker",
    )

    def __init__(
        self,
        name: str,
        sticker: Sticker,
        rarity_per_mille: int,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.name: str = name
        self.sticker: Sticker = sticker
        self.rarity_per_mille: int = rarity_per_mille

        self._id_attrs = (self.name, self.sticker, self.rarity_per_mille)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: Optional["Bot"] = None) -> "UniqueGiftSymbol":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["sticker"] = de_json_optional(data.get("sticker"), Sticker, bot)

        return super().de_json(data=data, bot=bot)


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

    __slots__ = (
        "center_color",
        "edge_color",
        "symbol_color",
        "text_color",
    )

    def __init__(
        self,
        center_color: int,
        edge_color: int,
        symbol_color: int,
        text_color: int,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.center_color: int = center_color
        self.edge_color: int = edge_color
        self.symbol_color: int = symbol_color
        self.text_color: int = text_color

        self._id_attrs = (self.center_color, self.edge_color, self.symbol_color, self.text_color)

        self._freeze()


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

    __slots__ = (
        "colors",
        "name",
        "rarity_per_mille",
    )

    def __init__(
        self,
        name: str,
        colors: UniqueGiftBackdropColors,
        rarity_per_mille: int,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.name: str = name
        self.colors: UniqueGiftBackdropColors = colors
        self.rarity_per_mille: int = rarity_per_mille

        self._id_attrs = (self.name, self.colors, self.rarity_per_mille)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: Optional["Bot"] = None) -> "UniqueGiftBackdrop":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["colors"] = de_json_optional(data.get("colors"), UniqueGiftBackdropColors, bot)

        return super().de_json(data=data, bot=bot)


class UniqueGift(TelegramObject):
    """This object describes a unique gift that was upgraded from a regular gift.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`base_name`, :attr:`name`, :attr:`number`, :class:`model`,
    :attr:`symbol`, and :attr:`backdrop` are equal.

    .. versionadded:: 22.1

    Args:
        base_name (:obj:`str`): Human-readable name of the regular gift from which this unique
            gift was upgraded.
        name (:obj:`str`): Unique name of the gift. This name can be used
            in ``https://t.me/nft/...`` links and story areas.
        number (:obj:`int`): Unique number of the upgraded gift among gifts upgraded from the
            same regular gift.
        model (:class:`UniqueGiftModel`): Model of the gift.
        symbol (:class:`UniqueGiftSymbol`): Symbol of the gift.
        backdrop (:class:`UniqueGiftBackdrop`): Backdrop of the gift.

    Attributes:
        base_name (:obj:`str`): Human-readable name of the regular gift from which this unique
            gift was upgraded.
        name (:obj:`str`): Unique name of the gift. This name can be used
            in ``https://t.me/nft/...`` links and story areas.
        number (:obj:`int`): Unique number of the upgraded gift among gifts upgraded from the
            same regular gift.
        model (:class:`telegram.UniqueGiftModel`): Model of the gift.
        symbol (:class:`telegram.UniqueGiftSymbol`): Symbol of the gift.
        backdrop (:class:`telegram.UniqueGiftBackdrop`): Backdrop of the gift.

    """

    __slots__ = (
        "backdrop",
        "base_name",
        "model",
        "name",
        "number",
        "symbol",
    )

    def __init__(
        self,
        base_name: str,
        name: str,
        number: int,
        model: UniqueGiftModel,
        symbol: UniqueGiftSymbol,
        backdrop: UniqueGiftBackdrop,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.base_name: str = base_name
        self.name: str = name
        self.number: int = number
        self.model: UniqueGiftModel = model
        self.symbol: UniqueGiftSymbol = symbol
        self.backdrop: UniqueGiftBackdrop = backdrop

        self._id_attrs = (
            self.base_name,
            self.name,
            self.number,
            self.model,
            self.symbol,
            self.backdrop,
        )

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: Optional["Bot"] = None) -> "UniqueGift":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["model"] = de_json_optional(data.get("model"), UniqueGiftModel, bot)
        data["symbol"] = de_json_optional(data.get("symbol"), UniqueGiftSymbol, bot)
        data["backdrop"] = de_json_optional(data.get("backdrop"), UniqueGiftBackdrop, bot)

        return super().de_json(data=data, bot=bot)


class UniqueGiftInfo(TelegramObject):
    """Describes a service message about a unique gift that was sent or received.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal if their :attr:`gift`, and :attr:`origin` are equal.

    .. versionadded:: 22.1

    Args:
        gift (:class:`UniqueGift`): Information about the gift.
        origin (:obj:`str`): Origin of the gift. Currently, either :attr:`UPGRADE` for gifts
            upgraded from regular gifts, :attr:`TRANSFER` for gifts transferred from other users
            or channels, or :attr:`RESALE` for gifts bought from other users.

            .. versionchanged:: 22.3
                The :attr:`RESALE` origin was added.
        owned_gift_id (:obj:`str`, optional) Unique identifier of the received gift for the
            bot; only present for gifts received on behalf of business accounts.
        transfer_star_count (:obj:`int`, optional): Number of Telegram Stars that must be paid
            to transfer the gift; omitted if the bot cannot transfer the gift.
        last_resale_star_count (:obj:`int`, optional): For gifts bought from other users, the price
            paid for the gift.

            .. versionadded:: 22.3
        next_transfer_date (:obj:`datetime.datetime`, optional): Date when the gift can be
            transferred. If it's in the past, then the gift can be transferred now.
            |datetime_localization|

            .. versionadded:: 22.3

    Attributes:
        gift (:class:`UniqueGift`): Information about the gift.
        origin (:obj:`str`): Origin of the gift. Currently, either :attr:`UPGRADE` for gifts
            upgraded from regular gifts, :attr:`TRANSFER` for gifts transferred from other users
            or channels, or :attr:`RESALE` for gifts bought from other users.

            .. versionchanged:: 22.3
                The :attr:`RESALE` origin was added.
        owned_gift_id (:obj:`str`) Optional. Unique identifier of the received gift for the
            bot; only present for gifts received on behalf of business accounts.
        transfer_star_count (:obj:`int`): Optional. Number of Telegram Stars that must be paid
            to transfer the gift; omitted if the bot cannot transfer the gift.
        last_resale_star_count (:obj:`int`): Optional. For gifts bought from other users, the price
            paid for the gift.

            .. versionadded:: 22.3
        next_transfer_date (:obj:`datetime.datetime`): Optional. Date when the gift can be
            transferred. If it's in the past, then the gift can be transferred now.
            |datetime_localization|

            .. versionadded:: 22.3
    """

    UPGRADE: Final[str] = constants.UniqueGiftInfoOrigin.UPGRADE
    """:const:`telegram.constants.UniqueGiftInfoOrigin.UPGRADE`"""
    TRANSFER: Final[str] = constants.UniqueGiftInfoOrigin.TRANSFER
    """:const:`telegram.constants.UniqueGiftInfoOrigin.TRANSFER`"""
    RESALE: Final[str] = constants.UniqueGiftInfoOrigin.RESALE
    """:const:`telegram.constants.UniqueGiftInfoOrigin.RESALE`

    .. versionadded:: 22.3
    """

    __slots__ = (
        "gift",
        "last_resale_star_count",
        "next_transfer_date",
        "origin",
        "owned_gift_id",
        "transfer_star_count",
    )

    def __init__(
        self,
        gift: UniqueGift,
        origin: str,
        owned_gift_id: Optional[str] = None,
        transfer_star_count: Optional[int] = None,
        last_resale_star_count: Optional[int] = None,
        next_transfer_date: Optional[dtm.datetime] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        # Required
        self.gift: UniqueGift = gift
        self.origin: str = enum.get_member(constants.UniqueGiftInfoOrigin, origin, origin)
        # Optional
        self.owned_gift_id: Optional[str] = owned_gift_id
        self.transfer_star_count: Optional[int] = transfer_star_count
        self.last_resale_star_count: Optional[int] = last_resale_star_count
        self.next_transfer_date: Optional[dtm.datetime] = next_transfer_date

        self._id_attrs = (self.gift, self.origin)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: Optional["Bot"] = None) -> "UniqueGiftInfo":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        loc_tzinfo = extract_tzinfo_from_defaults(bot)
        data["gift"] = de_json_optional(data.get("gift"), UniqueGift, bot)
        data["next_transfer_date"] = from_timestamp(
            data.get("next_transfer_date"), tzinfo=loc_tzinfo
        )

        return super().de_json(data=data, bot=bot)
