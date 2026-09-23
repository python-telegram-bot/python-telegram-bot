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
"""This module contains objects that represent story areas."""

from typing import ClassVar

from telegram import constants
from telegram._reaction import ReactionType
from telegram._telegramobject import TelegramObject
from telegram._utils import enum
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class StoryAreaPosition(TelegramObject):
    """Describes the position of a clickable area within a story.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if all of their attributes are equal.

    .. versionadded:: 22.1

    Args:
        x_percentage (:obj:`float`): The abscissa of the area's center, as a percentage of the
            media width.
        y_percentage (:obj:`float`): The ordinate of the area's center, as a percentage of the
            media height.
        width_percentage (:obj:`float`): The width of the area's rectangle, as a percentage of the
            media width.
        height_percentage (:obj:`float`): The height of the area's rectangle, as a percentage of
            the media height.
        rotation_angle (:obj:`float`): The clockwise rotation angle of the rectangle, in degrees;
            0-:tg-const:`~telegram.constants.StoryAreaPositionLimit.MAX_ROTATION_ANGLE`.
        corner_radius_percentage (:obj:`float`): The radius of the rectangle corner rounding, as a
            percentage of the media width.

    Attributes:
        x_percentage (:obj:`float`): The abscissa of the area's center, as a percentage of the
            media width.
        y_percentage (:obj:`float`): The ordinate of the area's center, as a percentage of the
            media height.
        width_percentage (:obj:`float`): The width of the area's rectangle, as a percentage of the
            media width.
        height_percentage (:obj:`float`): The height of the area's rectangle, as a percentage of
            the media height.
        rotation_angle (:obj:`float`): The clockwise rotation angle of the rectangle, in degrees;
            0-:tg-const:`~telegram.constants.StoryAreaPositionLimit.MAX_ROTATION_ANGLE`.
        corner_radius_percentage (:obj:`float`): The radius of the rectangle corner rounding, as a
            percentage of the media width.

    """

    x_percentage: float = tg_field(compare=True)
    y_percentage: float = tg_field(compare=True)
    width_percentage: float = tg_field(compare=True)
    height_percentage: float = tg_field(compare=True)
    rotation_angle: float = tg_field(compare=True)
    corner_radius_percentage: float = tg_field(compare=True)


@tg_dataclass()
class LocationAddress(TelegramObject):
    """Describes the physical address of a location.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`country_code`, :attr:`state`, :attr:`city` and :attr:`street`
    are equal.

    .. versionadded:: 22.1

    Args:
        country_code (:obj:`str`): The two-letter ``ISO 3166-1 alpha-2`` country code of the
            country where the location is located.
        state (:obj:`str`, optional): State of the location.
        city (:obj:`str`, optional): City of the location.
        street (:obj:`str`, optional): Street address of the location.

    Attributes:
        country_code (:obj:`str`): The two-letter ``ISO 3166-1 alpha-2`` country code of the
            country where the location is located.
        state (:obj:`str`): Optional. State of the location.
        city (:obj:`str`): Optional. City of the location.
        street (:obj:`str`): Optional. Street address of the location.

    """

    country_code: str = tg_field(compare=True)
    state: str | None = tg_field(compare=True, default=None)
    city: str | None = tg_field(compare=True, default=None)
    street: str | None = tg_field(compare=True, default=None)


@tg_dataclass()
class StoryAreaType(TelegramObject):
    """Describes the type of a clickable area on a story. Currently, it can be one of:

    * :class:`telegram.StoryAreaTypeLocation`
    * :class:`telegram.StoryAreaTypeSuggestedReaction`
    * :class:`telegram.StoryAreaTypeLink`
    * :class:`telegram.StoryAreaTypeWeather`
    * :class:`telegram.StoryAreaTypeUniqueGift`

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` is equal.

    .. versionadded:: 22.1

    Args:
        type (:obj:`str`): Type of the area.

    Attributes:
        type (:obj:`str`): Type of the area.

    """

    LOCATION: ClassVar[str] = constants.StoryAreaTypeType.LOCATION
    """:const:`telegram.constants.StoryAreaTypeType.LOCATION`"""
    SUGGESTED_REACTION: ClassVar[str] = constants.StoryAreaTypeType.SUGGESTED_REACTION
    """:const:`telegram.constants.StoryAreaTypeType.SUGGESTED_REACTION`"""
    LINK: ClassVar[str] = constants.StoryAreaTypeType.LINK
    """:const:`telegram.constants.StoryAreaTypeType.LINK`"""
    WEATHER: ClassVar[str] = constants.StoryAreaTypeType.WEATHER
    """:const:`telegram.constants.StoryAreaTypeType.WEATHER`"""
    UNIQUE_GIFT: ClassVar[str] = constants.StoryAreaTypeType.UNIQUE_GIFT
    """:const:`telegram.constants.StoryAreaTypeType.UNIQUE_GIFT`"""

    @staticmethod
    def _type_converter(value: str) -> str:
        return enum.get_member(constants.StoryAreaTypeType, value, value)

    type: str = tg_field(compare=True, converter=_type_converter)


@tg_dataclass()
class StoryAreaTypeLocation(StoryAreaType):
    """Describes a story area pointing to a location. Currently, a story can have up to
    :tg-const:`~telegram.constants.StoryAreaTypeLimit.MAX_LOCATION_AREAS` location areas.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`latitude` and :attr:`longitude` are equal.

    .. versionadded:: 22.1

    Args:
        latitude (:obj:`float`): Location latitude in degrees.
        longitude (:obj:`float`): Location longitude in degrees.
        address (:class:`telegram.LocationAddress`, optional): Address of the location.

    Attributes:
        type (:obj:`str`): Type of the area, always :attr:`~telegram.StoryAreaType.LOCATION`.
        latitude (:obj:`float`): Location latitude in degrees.
        longitude (:obj:`float`): Location longitude in degrees.
        address (:class:`telegram.LocationAddress`): Optional. Address of the location.

    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=StoryAreaType.LOCATION)
    # Required
    latitude: float = tg_field(compare=True)
    longitude: float = tg_field(compare=True)
    # Optional
    address: LocationAddress | None = tg_field(default=None)


@tg_dataclass()
class StoryAreaTypeSuggestedReaction(StoryAreaType):
    """
    Describes a story area pointing to a suggested reaction. Currently, a story can have up to
    :tg-const:`~telegram.constants.StoryAreaTypeLimit.MAX_SUGGESTED_REACTION_AREAS`
    suggested reaction areas.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`reaction_type`, :attr:`is_dark` and :attr:`is_flipped`
    are equal.

    .. versionadded:: 22.1

    Args:
        reaction_type (:class:`ReactionType`): Type of the reaction.
        is_dark (:obj:`bool`, optional): Pass :obj:`True` if the reaction area has a dark
            background.
        is_flipped (:obj:`bool`, optional): Pass :obj:`True` if reaction area corner is flipped.

    Attributes:
        type (:obj:`str`): Type of the area, always
            :tg-const:`~telegram.StoryAreaType.SUGGESTED_REACTION`.
        reaction_type (:class:`ReactionType`): Type of the reaction.
        is_dark (:obj:`bool`): Optional. Pass :obj:`True` if the reaction area has a dark
            background.
        is_flipped (:obj:`bool`): Optional. Pass :obj:`True` if reaction area corner is flipped.

    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=StoryAreaType.SUGGESTED_REACTION)
    # Required
    reaction_type: ReactionType = tg_field(compare=True)
    # Optional
    is_dark: bool | None = tg_field(compare=True, default=None)
    is_flipped: bool | None = tg_field(compare=True, default=None)


@tg_dataclass()
class StoryAreaTypeLink(StoryAreaType):
    """Describes a story area pointing to an ``HTTP`` or ``tg://`` link. Currently, a story can
    have up to :tg-const:`~telegram.constants.StoryAreaTypeLimit.MAX_LINK_AREAS` link areas.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`url` is equal.

    .. versionadded:: 22.1

    Args:
        url (:obj:`str`): ``HTTP`` or ``tg://`` URL to be opened when the area is clicked.

    Attributes:
        type (:obj:`str`): Type of the area, always :attr:`~telegram.StoryAreaType.LINK`.
        url (:obj:`str`): ``HTTP`` or ``tg://`` URL to be opened when the area is clicked.

    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=StoryAreaType.LINK)
    # Required
    url: str = tg_field(compare=True)


@tg_dataclass()
class StoryAreaTypeWeather(StoryAreaType):
    """
    Describes a story area containing weather information. Currently, a story can have up to
    :tg-const:`~telegram.constants.StoryAreaTypeLimit.MAX_WEATHER_AREAS` weather areas.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`temperature`, :attr:`emoji` and
    :attr:`background_color` are equal.

    .. versionadded:: 22.1

    Args:
        temperature (:obj:`float`): Temperature, in degree Celsius.
        emoji (:obj:`str`): Emoji representing the weather.
        background_color (:obj:`int`): A color of the area background in the ``ARGB`` format.

    Attributes:
        type (:obj:`str`): Type of the area, always
            :tg-const:`~telegram.StoryAreaType.WEATHER`.
        temperature (:obj:`float`): Temperature, in degree Celsius.
        emoji (:obj:`str`): Emoji representing the weather.
        background_color (:obj:`int`): A color of the area background in the ``ARGB`` format.

    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=StoryAreaType.WEATHER)
    # Required
    temperature: float = tg_field(compare=True)
    emoji: str = tg_field(compare=True)
    background_color: int = tg_field(compare=True)


@tg_dataclass()
class StoryAreaTypeUniqueGift(StoryAreaType):
    """
    Describes a story area pointing to a unique gift. Currently, a story can have at most
    :tg-const:`~telegram.constants.StoryAreaTypeLimit.MAX_UNIQUE_GIFT_AREAS` unique gift area.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`name` is equal.

    .. versionadded:: 22.1

    Args:
        name (:obj:`str`): Unique name of the gift.

    Attributes:
        type (:obj:`str`): Type of the area, always
            :tg-const:`~telegram.StoryAreaType.UNIQUE_GIFT`.
        name (:obj:`str`): Unique name of the gift.

    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=StoryAreaType.UNIQUE_GIFT)
    # Required
    name: str = tg_field(compare=True)


@tg_dataclass()
class StoryArea(TelegramObject):
    """Describes a clickable area on a story media.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`position` and :attr:`type` are equal.

    .. versionadded:: 22.1

    Args:
        position (:class:`telegram.StoryAreaPosition`): Position of the area.
        type (:class:`telegram.StoryAreaType`): Type of the area.

    Attributes:
        position (:class:`telegram.StoryAreaPosition`): Position of the area.
        type (:class:`telegram.StoryAreaType`): Type of the area.

    """

    position: StoryAreaPosition = tg_field(compare=True)
    type: StoryAreaType = tg_field(compare=True)
