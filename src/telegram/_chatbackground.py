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
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains objects related to chat backgrounds."""

from typing import ClassVar

from telegram import constants
from telegram._files.document import Document
from telegram._telegramobject import TelegramObject
from telegram._utils import enum
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class BackgroundFill(TelegramObject):
    """Base class for Telegram BackgroundFill Objects. It can be one of:

    * :class:`telegram.BackgroundFillSolid`
    * :class:`telegram.BackgroundFillGradient`
    * :class:`telegram.BackgroundFillFreeformGradient`

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` is equal.

    .. versionadded:: 21.2

    Args:
        type (:obj:`str`): Type of the background fill. Can be one of:
            :attr:`~telegram.BackgroundFill.SOLID`, :attr:`~telegram.BackgroundFill.GRADIENT`
            or :attr:`~telegram.BackgroundFill.FREEFORM_GRADIENT`.

    Attributes:
        type (:obj:`str`): Type of the background fill. Can be one of:
            :attr:`~telegram.BackgroundFill.SOLID`, :attr:`~telegram.BackgroundFill.GRADIENT`
            or :attr:`~telegram.BackgroundFill.FREEFORM_GRADIENT`.
    """

    __DE_JSON_DISPATCH__: ClassVar[tuple[str, dict[str, str]] | None] = (
        "type",
        {
            "solid": "BackgroundFillSolid",
            "gradient": "BackgroundFillGradient",
            "freeform_gradient": "BackgroundFillFreeformGradient",
        },
    )

    SOLID: ClassVar[constants.BackgroundFillType] = constants.BackgroundFillType.SOLID
    """:const:`telegram.constants.BackgroundFillType.SOLID`"""
    GRADIENT: ClassVar[constants.BackgroundFillType] = constants.BackgroundFillType.GRADIENT
    """:const:`telegram.constants.BackgroundFillType.GRADIENT`"""
    FREEFORM_GRADIENT: ClassVar[constants.BackgroundFillType] = (
        constants.BackgroundFillType.FREEFORM_GRADIENT
    )
    """:const:`telegram.constants.BackgroundFillType.FREEFORM_GRADIENT`"""

    @staticmethod
    def _type_converter(value: str) -> str:
        return enum.get_member(constants.BackgroundFillType, value, value)

    type: str = tg_field(compare=True, converter=_type_converter)


@tg_dataclass()
class BackgroundFillSolid(BackgroundFill):
    """
    The background is filled using the selected color.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`color` is equal.

    .. versionadded:: 21.2

    Args:
        color (:obj:`int`): The color of the background fill in the `RGB24` format.

    Attributes:
        type (:obj:`str`): Type of the background fill. Always
            :attr:`~telegram.BackgroundFill.SOLID`.
        color (:obj:`int`): The color of the background fill in the `RGB24` format.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=BackgroundFill.SOLID)

    color: int = tg_field(compare=True)


@tg_dataclass()
class BackgroundFillGradient(BackgroundFill):
    """
    The background is a gradient fill.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`top_color`, :attr:`bottom_color`
    and :attr:`rotation_angle` are equal.

    .. versionadded:: 21.2

    Args:
        top_color (:obj:`int`): Top color of the gradient in the `RGB24` format.
        bottom_color (:obj:`int`): Bottom color of the gradient in the `RGB24` format.
        rotation_angle (:obj:`int`): Clockwise rotation angle of the background
            fill in degrees;
            0-:tg-const:`telegram.constants.BackgroundFillLimit.MAX_ROTATION_ANGLE`.


    Attributes:
        type (:obj:`str`): Type of the background fill. Always
            :attr:`~telegram.BackgroundFill.GRADIENT`.
        top_color (:obj:`int`): Top color of the gradient in the `RGB24` format.
        bottom_color (:obj:`int`): Bottom color of the gradient in the `RGB24` format.
        rotation_angle (:obj:`int`): Clockwise rotation angle of the background
            fill in degrees;
            0-:tg-const:`telegram.constants.BackgroundFillLimit.MAX_ROTATION_ANGLE`.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=BackgroundFill.GRADIENT)

    top_color: int = tg_field(compare=True)
    bottom_color: int = tg_field(compare=True)
    rotation_angle: int = tg_field(compare=True)


@tg_dataclass()
class BackgroundFillFreeformGradient(BackgroundFill):
    """
    The background is a freeform gradient that rotates after every message in the chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`colors` is equal.

    .. versionadded:: 21.2

    Args:
        colors (Sequence[:obj:`int`]): A list of the 3 or 4 base colors that are used to
            generate the freeform gradient in the `RGB24` format

    Attributes:
        type (:obj:`str`): Type of the background fill. Always
            :attr:`~telegram.BackgroundFill.FREEFORM_GRADIENT`.
        colors (Sequence[:obj:`int`]): A list of the 3 or 4 base colors that are used to
            generate the freeform gradient in the `RGB24` format
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=BackgroundFill.FREEFORM_GRADIENT)

    colors: tuple[int, ...] = tg_field(compare=True, converter=parse_sequence_arg)


@tg_dataclass()
class BackgroundType(TelegramObject):
    """Base class for Telegram BackgroundType Objects. It can be one of:

    * :class:`telegram.BackgroundTypeFill`
    * :class:`telegram.BackgroundTypeWallpaper`
    * :class:`telegram.BackgroundTypePattern`
    * :class:`telegram.BackgroundTypeChatTheme`.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` is equal.

    .. versionadded:: 21.2

    Args:
        type (:obj:`str`): Type of the background. Can be one of:
            :attr:`~telegram.BackgroundType.FILL`, :attr:`~telegram.BackgroundType.WALLPAPER`
            :attr:`~telegram.BackgroundType.PATTERN` or
            :attr:`~telegram.BackgroundType.CHAT_THEME`.

    Attributes:
        type (:obj:`str`): Type of the background. Can be one of:
            :attr:`~telegram.BackgroundType.FILL`, :attr:`~telegram.BackgroundType.WALLPAPER`
            :attr:`~telegram.BackgroundType.PATTERN` or
            :attr:`~telegram.BackgroundType.CHAT_THEME`.

    """

    __DE_JSON_DISPATCH__: ClassVar[tuple[str, dict[str, str]] | None] = (
        "type",
        {
            "fill": "BackgroundTypeFill",
            "wallpaper": "BackgroundTypeWallpaper",
            "pattern": "BackgroundTypePattern",
            "chat_theme": "BackgroundTypeChatTheme",
        },
    )

    FILL: ClassVar[constants.BackgroundTypeType] = constants.BackgroundTypeType.FILL
    """:const:`telegram.constants.BackgroundTypeType.FILL`"""
    WALLPAPER: ClassVar[constants.BackgroundTypeType] = constants.BackgroundTypeType.WALLPAPER
    """:const:`telegram.constants.BackgroundTypeType.WALLPAPER`"""
    PATTERN: ClassVar[constants.BackgroundTypeType] = constants.BackgroundTypeType.PATTERN
    """:const:`telegram.constants.BackgroundTypeType.PATTERN`"""
    CHAT_THEME: ClassVar[constants.BackgroundTypeType] = constants.BackgroundTypeType.CHAT_THEME
    """:const:`telegram.constants.BackgroundTypeType.CHAT_THEME`"""

    @staticmethod
    def _type_converter(value: str) -> str:
        return enum.get_member(constants.BackgroundTypeType, value, value)

    type: str = tg_field(compare=True, converter=_type_converter)


@tg_dataclass()
class BackgroundTypeFill(BackgroundType):
    """
    The background is automatically filled based on the selected colors.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`fill` and :attr:`dark_theme_dimming` are equal.

    .. versionadded:: 21.2

    Args:
        fill (:class:`telegram.BackgroundFill`): The background fill.
        dark_theme_dimming (:obj:`int`): Dimming of the background in dark themes, as a
            percentage;
            0-:tg-const:`telegram.constants.BackgroundTypeLimit.MAX_DIMMING`.

    Attributes:
        type (:obj:`str`): Type of the background. Always
            :attr:`~telegram.BackgroundType.FILL`.
        fill (:class:`telegram.BackgroundFill`): The background fill.
        dark_theme_dimming (:obj:`int`): Dimming of the background in dark themes, as a
            percentage;
            0-:tg-const:`telegram.constants.BackgroundTypeLimit.MAX_DIMMING`.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=BackgroundType.FILL)

    fill: BackgroundFill = tg_field(compare=True)
    dark_theme_dimming: int = tg_field(compare=True)


@tg_dataclass()
class BackgroundTypeWallpaper(BackgroundType):
    """
    The background is a wallpaper in the `JPEG` format.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`document` and :attr:`dark_theme_dimming` are equal.

    .. versionadded:: 21.2

    Args:
        document (:class:`telegram.Document`): Document with the wallpaper
        dark_theme_dimming (:obj:`int`): Dimming of the background in dark themes, as a
            percentage;
            0-:tg-const:`telegram.constants.BackgroundTypeLimit.MAX_DIMMING`.
        is_blurred (:obj:`bool`, optional): :obj:`True`, if the wallpaper is downscaled to fit
            in a 450x450 square and then box-blurred with radius 12
        is_moving (:obj:`bool`, optional): :obj:`True`, if the background moves slightly
            when the device is tilted

    Attributes:
        type (:obj:`str`): Type of the background. Always
            :attr:`~telegram.BackgroundType.WALLPAPER`.
        document (:class:`telegram.Document`): Document with the wallpaper
        dark_theme_dimming (:obj:`int`): Dimming of the background in dark themes, as a
            percentage;
            0-:tg-const:`telegram.constants.BackgroundTypeLimit.MAX_DIMMING`.
        is_blurred (:obj:`bool`): Optional. :obj:`True`, if the wallpaper is downscaled to fit
            in a 450x450 square and then box-blurred with radius 12
        is_moving (:obj:`bool`): Optional. :obj:`True`, if the background moves slightly
            when the device is tilted
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=BackgroundType.WALLPAPER)

    # Required
    document: Document = tg_field(compare=True)
    dark_theme_dimming: int = tg_field(compare=True)
    # Optionals
    is_blurred: bool | None = tg_field(default=None)
    is_moving: bool | None = tg_field(default=None)


@tg_dataclass()
class BackgroundTypePattern(BackgroundType):
    """
    The background is a ``.PNG`` or ``.TGV`` (gzipped subset of ``SVG`` with ``MIME`` type
    ``"application/x-tgwallpattern"``) pattern to be combined with the background fill
    chosen by the user.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`document` and :attr:`fill` and :attr:`intensity` are equal.

    .. versionadded:: 21.2

    Args:
        document (:class:`telegram.Document`): Document with the pattern.
        fill (:class:`telegram.BackgroundFill`): The background fill that is combined with
            the pattern.
        intensity (:obj:`int`): Intensity of the pattern when it is shown above the filled
            background;
            0-:tg-const:`telegram.constants.BackgroundTypeLimit.MAX_INTENSITY`.
        is_inverted (:obj:`int`, optional): :obj:`True`, if the background fill must be applied
            only to the pattern itself. All other pixels are black in this case. For dark
            themes only.
        is_moving (:obj:`bool`, optional): :obj:`True`, if the background moves slightly
            when the device is tilted.

    Attributes:
        type (:obj:`str`): Type of the background. Always
            :attr:`~telegram.BackgroundType.PATTERN`.
        document (:class:`telegram.Document`): Document with the pattern.
        fill (:class:`telegram.BackgroundFill`): The background fill that is combined with
            the pattern.
        intensity (:obj:`int`): Intensity of the pattern when it is shown above the filled
            background;
            0-:tg-const:`telegram.constants.BackgroundTypeLimit.MAX_INTENSITY`.
        is_inverted (:obj:`int`): Optional. :obj:`True`, if the background fill must be applied
            only to the pattern itself. All other pixels are black in this case. For dark
            themes only.
        is_moving (:obj:`bool`): Optional. :obj:`True`, if the background moves slightly
            when the device is tilted.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=BackgroundType.PATTERN)

    # Required
    document: Document = tg_field(compare=True)
    fill: BackgroundFill = tg_field(compare=True)
    intensity: int = tg_field(compare=True)
    # Optionals
    is_inverted: bool | None = tg_field(default=None)
    is_moving: bool | None = tg_field(default=None)


@tg_dataclass()
class BackgroundTypeChatTheme(BackgroundType):
    """
    The background is taken directly from a built-in chat theme.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`theme_name` is equal.

    .. versionadded:: 21.2

    Args:
        theme_name (:obj:`str`): Name of the chat theme, which is usually an emoji.

    Attributes:
        type (:obj:`str`): Type of the background. Always
            :attr:`~telegram.BackgroundType.CHAT_THEME`.
        theme_name (:obj:`str`): Name of the chat theme, which is usually an emoji.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=BackgroundType.CHAT_THEME)
    theme_name: str = tg_field(compare=True)


@tg_dataclass()
class ChatBackground(TelegramObject):
    """
    This object represents a chat background.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` is  equal.

    .. versionadded:: 21.2

    Args:
        type (:class:`telegram.BackgroundType`): Type of the background.

    Attributes:
        type (:class:`telegram.BackgroundType`): Type of the background.
    """

    type: BackgroundType = tg_field(compare=True)
