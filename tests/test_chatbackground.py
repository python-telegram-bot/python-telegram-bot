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

import pytest

from telegram import (
    BackgroundFill,
    BackgroundFillFreeformGradient,
    BackgroundFillGradient,
    BackgroundFillSolid,
    BackgroundType,
    BackgroundTypeChatTheme,
    BackgroundTypeFill,
    BackgroundTypePattern,
    BackgroundTypeWallpaper,
    ChatBackground,
    Dice,
    Document,
)
from telegram.constants import BackgroundFillType, BackgroundTypeType
from tests.auxil.deserialization import DeserializationTestBase
from tests.auxil.slots import mro_slots


@pytest.fixture
def background_fill():
    return BackgroundFill(BackgroundFillTestBase.type)


class BackgroundFillTestBase:
    type = BackgroundFill.SOLID
    color = 42
    top_color = 43
    bottom_color = 44
    rotation_angle = 45
    colors = [46, 47, 48, 49]


class TestBackgroundFillWithoutRequest(BackgroundFillTestBase, DeserializationTestBase):
    de_json_class = BackgroundFill

    def test_slots(self, background_fill):
        inst = background_fill
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_type_enum_conversion(self, background_fill):
        assert type(BackgroundFill("solid").type) is BackgroundFillType
        assert BackgroundFill("unknown").type == "unknown"

    @pytest.fixture
    def de_json_dict(self):
        # An unknown type, so that BackgroundFill.de_json does not dispatch to a subclass
        return {"type": "unknown"}

    def test_de_json(self, offline_bot, de_json_dict):
        background_fill = BackgroundFill.de_json(de_json_dict, offline_bot)
        assert type(background_fill) is BackgroundFill
        assert background_fill.api_kwargs == {}
        assert background_fill.type == "unknown"

    @pytest.mark.parametrize(
        ("bf_type", "subclass"),
        [
            ("solid", BackgroundFillSolid),
            ("gradient", BackgroundFillGradient),
            ("freeform_gradient", BackgroundFillFreeformGradient),
        ],
    )
    def test_de_json_subclass(self, offline_bot, bf_type, subclass):
        json_dict = {
            "type": bf_type,
            "color": self.color,
            "top_color": self.top_color,
            "bottom_color": self.bottom_color,
            "rotation_angle": self.rotation_angle,
            "colors": self.colors,
        }
        bf = BackgroundFill.de_json(json_dict, offline_bot)

        assert type(bf) is subclass
        assert set(bf.api_kwargs.keys()) == set(json_dict.keys()) - set(subclass.__slots__) - {
            "type"
        }
        assert bf.type == bf_type

    def test_to_dict(self, background_fill):
        assert background_fill.to_dict() == {"type": background_fill.type}

    def test_equality(self, background_fill):
        a = background_fill
        b = BackgroundFill(self.type)
        c = BackgroundFill("unknown")
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def background_fill_gradient():
    return BackgroundFillGradient(
        TestBackgroundFillGradientWithoutRequest.top_color,
        TestBackgroundFillGradientWithoutRequest.bottom_color,
        TestBackgroundFillGradientWithoutRequest.rotation_angle,
    )


class TestBackgroundFillGradientWithoutRequest(BackgroundFillTestBase, DeserializationTestBase):
    de_json_class = BackgroundFillGradient
    type = BackgroundFill.GRADIENT

    def test_slots(self, background_fill_gradient):
        inst = background_fill_gradient
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {
            "top_color": self.top_color,
            "bottom_color": self.bottom_color,
            "rotation_angle": self.rotation_angle,
        }

    def test_de_json(self, offline_bot, de_json_dict):
        background_fill = BackgroundFillGradient.de_json(de_json_dict, offline_bot)
        assert type(background_fill) is BackgroundFillGradient
        assert background_fill.api_kwargs == {}
        assert background_fill.type == "gradient"
        assert background_fill.top_color == self.top_color
        assert background_fill.bottom_color == self.bottom_color
        assert background_fill.rotation_angle == self.rotation_angle

    def test_to_dict(self, background_fill_gradient):
        assert background_fill_gradient.to_dict() == {
            "type": background_fill_gradient.type,
            "top_color": self.top_color,
            "bottom_color": self.bottom_color,
            "rotation_angle": self.rotation_angle,
        }

    def test_equality(self, background_fill_gradient):
        a = background_fill_gradient
        b = BackgroundFillGradient(
            self.top_color,
            self.bottom_color,
            self.rotation_angle,
        )
        c = BackgroundFillGradient(
            self.top_color + 1,
            self.bottom_color + 1,
            self.rotation_angle + 1,
        )
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def background_fill_freeform_gradient():
    return BackgroundFillFreeformGradient(
        TestBackgroundFillFreeformGradientWithoutRequest.colors,
    )


class TestBackgroundFillFreeformGradientWithoutRequest(
    BackgroundFillTestBase, DeserializationTestBase
):
    de_json_class = BackgroundFillFreeformGradient
    type = BackgroundFill.FREEFORM_GRADIENT

    def test_slots(self, background_fill_freeform_gradient):
        inst = background_fill_freeform_gradient
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {"colors": self.colors}

    def test_de_json(self, offline_bot, de_json_dict):
        background_fill = BackgroundFillFreeformGradient.de_json(de_json_dict, offline_bot)
        assert type(background_fill) is BackgroundFillFreeformGradient
        assert background_fill.api_kwargs == {}
        assert background_fill.type == "freeform_gradient"
        assert background_fill.colors == tuple(self.colors)

    def test_to_dict(self, background_fill_freeform_gradient):
        assert background_fill_freeform_gradient.to_dict() == {
            "type": background_fill_freeform_gradient.type,
            "colors": self.colors,
        }

    def test_equality(self, background_fill_freeform_gradient):
        a = background_fill_freeform_gradient
        b = BackgroundFillFreeformGradient(self.colors)
        c = BackgroundFillFreeformGradient([color + 1 for color in self.colors])
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def background_fill_solid():
    return BackgroundFillSolid(TestBackgroundFillSolidWithoutRequest.color)


class TestBackgroundFillSolidWithoutRequest(BackgroundFillTestBase, DeserializationTestBase):
    de_json_class = BackgroundFillSolid
    type = BackgroundFill.SOLID

    def test_slots(self, background_fill_solid):
        inst = background_fill_solid
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {"color": self.color}

    def test_de_json(self, offline_bot, de_json_dict):
        background_fill = BackgroundFillSolid.de_json(de_json_dict, offline_bot)
        assert type(background_fill) is BackgroundFillSolid
        assert background_fill.api_kwargs == {}
        assert background_fill.type == "solid"
        assert background_fill.color == self.color

    def test_to_dict(self, background_fill_solid):
        assert background_fill_solid.to_dict() == {
            "type": background_fill_solid.type,
            "color": self.color,
        }

    def test_equality(self, background_fill_solid):
        a = background_fill_solid
        b = BackgroundFillSolid(self.color)
        c = BackgroundFillSolid(self.color + 1)
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def background_type():
    return BackgroundType(BackgroundTypeTestBase.type)


class BackgroundTypeTestBase:
    type = BackgroundType.WALLPAPER
    fill = BackgroundFillSolid(42)
    dark_theme_dimming = 43
    document = Document("file_id", "file_unique_id", file_name="file_name", file_size=42)
    is_blurred = True
    is_moving = True
    intensity = 45
    is_inverted = True
    theme_name = "test theme name"


class TestBackgroundTypeWithoutRequest(BackgroundTypeTestBase, DeserializationTestBase):
    de_json_class = BackgroundType

    def test_slots(self, background_type):
        inst = background_type
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_type_enum_conversion(self, background_type):
        assert type(BackgroundType("wallpaper").type) is BackgroundTypeType
        assert BackgroundType("unknown").type == "unknown"

    @pytest.fixture
    def de_json_dict(self):
        # An unknown type, so that BackgroundType.de_json does not dispatch to a subclass
        return {"type": "unknown"}

    def test_de_json(self, offline_bot, de_json_dict):
        background_type = BackgroundType.de_json(de_json_dict, offline_bot)
        assert type(background_type) is BackgroundType
        assert background_type.api_kwargs == {}
        assert background_type.type == "unknown"

    @pytest.mark.parametrize(
        ("bt_type", "subclass"),
        [
            ("wallpaper", BackgroundTypeWallpaper),
            ("fill", BackgroundTypeFill),
            ("pattern", BackgroundTypePattern),
            ("chat_theme", BackgroundTypeChatTheme),
        ],
    )
    def test_de_json_subclass(self, offline_bot, bt_type, subclass):
        json_dict = {
            "type": bt_type,
            "fill": self.fill.to_dict(),
            "dark_theme_dimming": self.dark_theme_dimming,
            "document": self.document.to_dict(),
            "is_blurred": self.is_blurred,
            "is_moving": self.is_moving,
            "intensity": self.intensity,
            "is_inverted": self.is_inverted,
            "theme_name": self.theme_name,
        }
        bt = BackgroundType.de_json(json_dict, offline_bot)

        assert type(bt) is subclass
        assert set(bt.api_kwargs.keys()) == set(json_dict.keys()) - set(subclass.__slots__) - {
            "type"
        }
        assert bt.type == bt_type

    def test_to_dict(self, background_type):
        assert background_type.to_dict() == {"type": background_type.type}

    def test_equality(self, background_type):
        a = background_type
        b = BackgroundType(self.type)
        c = BackgroundType("unknown")
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def background_type_fill():
    return BackgroundTypeFill(
        fill=TestBackgroundTypeFillWithoutRequest.fill,
        dark_theme_dimming=TestBackgroundTypeFillWithoutRequest.dark_theme_dimming,
    )


class TestBackgroundTypeFillWithoutRequest(BackgroundTypeTestBase, DeserializationTestBase):
    de_json_class = BackgroundTypeFill
    type = BackgroundType.FILL

    def test_slots(self, background_type_fill):
        inst = background_type_fill
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {"fill": self.fill.to_dict(), "dark_theme_dimming": self.dark_theme_dimming}

    def test_de_json(self, offline_bot, de_json_dict):
        background_type = BackgroundTypeFill.de_json(de_json_dict, offline_bot)
        assert type(background_type) is BackgroundTypeFill
        assert background_type.api_kwargs == {}
        assert background_type.type == "fill"
        assert background_type.fill == self.fill
        assert background_type.dark_theme_dimming == self.dark_theme_dimming

    def test_to_dict(self, background_type_fill):
        assert background_type_fill.to_dict() == {
            "type": background_type_fill.type,
            "fill": self.fill.to_dict(),
            "dark_theme_dimming": self.dark_theme_dimming,
        }

    def test_equality(self, background_type_fill):
        a = background_type_fill
        b = BackgroundTypeFill(self.fill, self.dark_theme_dimming)
        c = BackgroundTypeFill(BackgroundFillSolid(43), 44)
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def background_type_pattern():
    return BackgroundTypePattern(
        TestBackgroundTypePatternWithoutRequest.document,
        TestBackgroundTypePatternWithoutRequest.fill,
        TestBackgroundTypePatternWithoutRequest.intensity,
        TestBackgroundTypePatternWithoutRequest.is_inverted,
        TestBackgroundTypePatternWithoutRequest.is_moving,
    )


class TestBackgroundTypePatternWithoutRequest(BackgroundTypeTestBase, DeserializationTestBase):
    de_json_class = BackgroundTypePattern
    type = BackgroundType.PATTERN

    def test_slots(self, background_type_pattern):
        inst = background_type_pattern
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {
            "document": self.document.to_dict(),
            "fill": self.fill.to_dict(),
            "intensity": self.intensity,
            "is_inverted": self.is_inverted,
            "is_moving": self.is_moving,
        }

    def test_de_json(self, offline_bot, de_json_dict):
        background_type = BackgroundTypePattern.de_json(de_json_dict, offline_bot)
        assert type(background_type) is BackgroundTypePattern
        assert background_type.api_kwargs == {}
        assert background_type.type == "pattern"
        assert background_type.document == self.document
        assert background_type.fill == self.fill
        assert background_type.intensity == self.intensity
        assert background_type.is_inverted == self.is_inverted
        assert background_type.is_moving == self.is_moving

    def test_to_dict(self, background_type_pattern):
        assert background_type_pattern.to_dict() == {
            "type": background_type_pattern.type,
            "document": self.document.to_dict(),
            "fill": self.fill.to_dict(),
            "intensity": self.intensity,
            "is_inverted": self.is_inverted,
            "is_moving": self.is_moving,
        }

    def test_equality(self, background_type_pattern):
        a = background_type_pattern
        b = BackgroundTypePattern(
            self.document,
            self.fill,
            self.intensity,
        )
        c = BackgroundTypePattern(
            Document("other", "other", "file_name", 43),
            False,
            False,
            44,
        )
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def background_type_chat_theme():
    return BackgroundTypeChatTheme(
        TestBackgroundTypeChatThemeWithoutRequest.theme_name,
    )


class TestBackgroundTypeChatThemeWithoutRequest(BackgroundTypeTestBase, DeserializationTestBase):
    de_json_class = BackgroundTypeChatTheme
    type = BackgroundType.CHAT_THEME

    def test_slots(self, background_type_chat_theme):
        inst = background_type_chat_theme
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {"theme_name": self.theme_name}

    def test_de_json(self, offline_bot, de_json_dict):
        background_type = BackgroundTypeChatTheme.de_json(de_json_dict, offline_bot)
        assert type(background_type) is BackgroundTypeChatTheme
        assert background_type.api_kwargs == {}
        assert background_type.type == "chat_theme"
        assert background_type.theme_name == self.theme_name

    def test_to_dict(self, background_type_chat_theme):
        assert background_type_chat_theme.to_dict() == {
            "type": background_type_chat_theme.type,
            "theme_name": self.theme_name,
        }

    def test_equality(self, background_type_chat_theme):
        a = background_type_chat_theme
        b = BackgroundTypeChatTheme(self.theme_name)
        c = BackgroundTypeChatTheme("other")
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def background_type_wallpaper():
    return BackgroundTypeWallpaper(
        TestBackgroundTypeWallpaperWithoutRequest.document,
        TestBackgroundTypeWallpaperWithoutRequest.dark_theme_dimming,
        TestBackgroundTypeWallpaperWithoutRequest.is_blurred,
        TestBackgroundTypeWallpaperWithoutRequest.is_moving,
    )


class TestBackgroundTypeWallpaperWithoutRequest(BackgroundTypeTestBase, DeserializationTestBase):
    de_json_class = BackgroundTypeWallpaper
    type = BackgroundType.WALLPAPER

    def test_slots(self, background_type_wallpaper):
        inst = background_type_wallpaper
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {
            "document": self.document.to_dict(),
            "dark_theme_dimming": self.dark_theme_dimming,
            "is_blurred": self.is_blurred,
            "is_moving": self.is_moving,
        }

    def test_de_json(self, offline_bot, de_json_dict):
        background_type = BackgroundTypeWallpaper.de_json(de_json_dict, offline_bot)
        assert type(background_type) is BackgroundTypeWallpaper
        assert background_type.api_kwargs == {}
        assert background_type.type == "wallpaper"
        assert background_type.document == self.document
        assert background_type.dark_theme_dimming == self.dark_theme_dimming
        assert background_type.is_blurred == self.is_blurred
        assert background_type.is_moving == self.is_moving

    def test_to_dict(self, background_type_wallpaper):
        assert background_type_wallpaper.to_dict() == {
            "type": background_type_wallpaper.type,
            "document": self.document.to_dict(),
            "dark_theme_dimming": self.dark_theme_dimming,
            "is_blurred": self.is_blurred,
            "is_moving": self.is_moving,
        }

    def test_equality(self, background_type_wallpaper):
        a = background_type_wallpaper
        b = BackgroundTypeWallpaper(
            self.document,
            self.dark_theme_dimming,
            self.is_blurred,
            self.is_moving,
        )
        c = BackgroundTypeWallpaper(
            Document("other", "other", "file_name", 43),
            44,
            False,
            False,
        )
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)


@pytest.fixture
def chat_background():
    return ChatBackground(ChatBackgroundTestBase.type)


class ChatBackgroundTestBase:
    type = BackgroundTypeFill(BackgroundFillSolid(42), 43)


class TestChatBackgroundWithoutRequest(ChatBackgroundTestBase, DeserializationTestBase):
    de_json_class = ChatBackground

    def test_slots(self, chat_background):
        inst = chat_background
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture
    def de_json_dict(self):
        return {"type": self.type.to_dict()}

    def test_de_json(self, offline_bot, de_json_dict):
        chat_background = ChatBackground.de_json(de_json_dict, offline_bot)
        assert type(chat_background) is ChatBackground
        assert chat_background.api_kwargs == {}
        assert chat_background.type == self.type
        assert type(chat_background.type) is BackgroundTypeFill

    def test_to_dict(self, chat_background):
        assert chat_background.to_dict() == {"type": chat_background.type.to_dict()}

    def test_equality(self, chat_background):
        a = chat_background
        b = ChatBackground(self.type)
        c = ChatBackground(BackgroundTypeFill(BackgroundFillSolid(43), 44))
        d = Dice(5, "test")

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)
