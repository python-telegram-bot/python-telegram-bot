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
import inspect
from copy import deepcopy
from typing import Union

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
    Dice,
    Document,
)
from tests.auxil.slots import mro_slots

ignored = ["self", "api_kwargs"]


class BFDefaults:
    color = 0
    top_color = 1
    bottom_color = 2
    rotation_angle = 45
    colors = [0, 1, 2]


def background_fill_solid():
    return BackgroundFillSolid(BFDefaults.color)


def background_fill_gradient():
    return BackgroundFillGradient(
        BFDefaults.top_color, BFDefaults.bottom_color, BFDefaults.rotation_angle
    )


def background_fill_freeform_gradient():
    return BackgroundFillFreeformGradient(BFDefaults.colors)


class BTDefaults:
    document = Document(1, 2)
    fill = BackgroundFillSolid(color=0)
    dark_theme_dimming = 20
    is_blurred = True
    is_moving = False
    intensity = 90
    is_inverted = False
    theme_name = "ice"


def background_type_fill():
    return BackgroundTypeFill(BTDefaults.fill, BTDefaults.dark_theme_dimming)


def background_type_wallpaper():
    return BackgroundTypeWallpaper(
        BTDefaults.document,
        BTDefaults.dark_theme_dimming,
        BTDefaults.is_blurred,
        BTDefaults.is_moving,
    )


def background_type_pattern():
    return BackgroundTypePattern(
        BTDefaults.document,
        BTDefaults.fill,
        BTDefaults.intensity,
        BTDefaults.is_inverted,
        BTDefaults.is_moving,
    )


def background_type_chat_theme():
    return BackgroundTypeChatTheme(BTDefaults.theme_name)


def make_json_dict(
    instance: Union[BackgroundType, BackgroundFill], include_optional_args: bool = False
) -> dict:
    """Used to make the json dict which we use for testing de_json. Similar to iter_args()"""
    json_dict = {"type": instance.type}
    sig = inspect.signature(instance.__class__.__init__)

    for param in sig.parameters.values():
        if param.name in ignored:  # ignore irrelevant params
            continue

        val = getattr(instance, param.name)
        # Compulsory args-
        if param.default is inspect.Parameter.empty:
            if hasattr(val, "to_dict"):  # convert the user object or any future ones to dict.
                val = val.to_dict()
            json_dict[param.name] = val

        # If we want to test all args (for de_json)-
        elif param.default is not inspect.Parameter.empty and include_optional_args:
            json_dict[param.name] = val
    return json_dict


def iter_args(
    instance: Union[BackgroundType, BackgroundFill],
    de_json_inst: Union[BackgroundType, BackgroundFill],
    include_optional: bool = False,
):
    """
    We accept both the regular instance and de_json created instance and iterate over them for
    easy one line testing later one.
    """
    yield instance.type, de_json_inst.type  # yield this here cause it's not available in sig.

    sig = inspect.signature(instance.__class__.__init__)
    for param in sig.parameters.values():
        if param.name in ignored:
            continue
        inst_at, json_at = getattr(instance, param.name), getattr(de_json_inst, param.name)
        if (
            param.default is not inspect.Parameter.empty and include_optional
        ) or param.default is inspect.Parameter.empty:
            yield inst_at, json_at


@pytest.fixture()
def background_type(request):
    return request.param()


@pytest.mark.parametrize(
    "background_type",
    [
        background_type_fill,
        background_type_wallpaper,
        background_type_pattern,
        background_type_chat_theme,
    ],
    indirect=True,
)
class TestBackgroundTypeWithoutRequest:
    def test_slot_behaviour(self, background_type):
        inst = background_type
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json_required_args(self, bot, background_type):
        cls = background_type.__class__
        assert cls.de_json({}, bot) is None

        json_dict = make_json_dict(background_type)
        const_background_type = BackgroundType.de_json(json_dict, bot)
        assert const_background_type.api_kwargs == {}

        assert isinstance(const_background_type, BackgroundType)
        assert isinstance(const_background_type, cls)
        for bg_type_at, const_bg_type_at in iter_args(background_type, const_background_type):
            assert bg_type_at == const_bg_type_at

    def test_de_json_all_args(self, bot, background_type):
        json_dict = make_json_dict(background_type, include_optional_args=True)
        const_background_type = BackgroundType.de_json(json_dict, bot)

        assert const_background_type.api_kwargs == {}

        assert isinstance(const_background_type, BackgroundType)
        assert isinstance(const_background_type, background_type.__class__)
        for bg_type_at, const_bg_type_at in iter_args(
            background_type, const_background_type, True
        ):
            assert bg_type_at == const_bg_type_at

    def test_de_json_invalid_type(self, background_type, bot):
        json_dict = {"type": "invalid", "theme_name": BTDefaults.theme_name}
        background_type = BackgroundType.de_json(json_dict, bot)

        assert type(background_type) is BackgroundType
        assert background_type.type == "invalid"

    def test_de_json_subclass(self, background_type, bot, chat_id):
        """This makes sure that e.g. BackgroundTypeFill(data, bot) never returns a
        BackgroundTypeWallpaper instance."""
        cls = background_type.__class__
        json_dict = make_json_dict(background_type, True)
        assert type(cls.de_json(json_dict, bot)) is cls

    def test_to_dict(self, background_type):
        bg_type_dict = background_type.to_dict()

        assert isinstance(bg_type_dict, dict)
        assert bg_type_dict["type"] == background_type.type

        for slot in background_type.__slots__:  # additional verification for the optional args
            if slot in ("fill", "document"):
                assert (getattr(background_type, slot)).to_dict() == bg_type_dict[slot]
                continue
            assert getattr(background_type, slot) == bg_type_dict[slot]

    def test_equality(self, background_type):
        a = BackgroundType(type="type")
        b = BackgroundType(type="type")
        c = background_type
        d = deepcopy(background_type)
        e = Dice(4, "emoji")
        sig = inspect.signature(background_type.__class__.__init__)
        params = [
            "random" for param in sig.parameters.values() if param.name not in [*ignored, "type"]
        ]
        f = background_type.__class__(*params)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert c == d
        assert hash(c) == hash(d)

        assert c != e
        assert hash(c) != hash(e)

        assert f != c
        assert hash(f) != hash(c)


@pytest.fixture()
def background_fill(request):
    return request.param()


@pytest.mark.parametrize(
    "background_fill",
    [
        background_fill_solid,
        background_fill_gradient,
        background_fill_freeform_gradient,
    ],
    indirect=True,
)
class TestBackgroundFillWithoutRequest:
    def test_slot_behaviour(self, background_fill):
        inst = background_fill
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_de_json_required_args(self, bot, background_fill):
        cls = background_fill.__class__
        assert cls.de_json({}, bot) is None

        json_dict = make_json_dict(background_fill)
        const_background_fill = BackgroundFill.de_json(json_dict, bot)
        assert const_background_fill.api_kwargs == {}

        assert isinstance(const_background_fill, BackgroundFill)
        assert isinstance(const_background_fill, cls)
        for bg_fill_at, const_bg_fill_at in iter_args(background_fill, const_background_fill):
            assert bg_fill_at == const_bg_fill_at

    def test_de_json_all_args(self, bot, background_fill):
        json_dict = make_json_dict(background_fill, include_optional_args=True)
        const_background_fill = BackgroundFill.de_json(json_dict, bot)

        assert const_background_fill.api_kwargs == {}

        assert isinstance(const_background_fill, BackgroundFill)
        assert isinstance(const_background_fill, background_fill.__class__)
        for bg_fill_at, const_bg_fill_at in iter_args(
            background_fill, const_background_fill, True
        ):
            assert bg_fill_at == const_bg_fill_at

    def test_de_json_invalid_type(self, background_fill, bot):
        json_dict = {"type": "invalid", "theme_name": BTDefaults.theme_name}
        background_fill = BackgroundFill.de_json(json_dict, bot)

        assert type(background_fill) is BackgroundFill
        assert background_fill.type == "invalid"

    def test_de_json_subclass(self, background_fill, bot):
        """This makes sure that e.g. BackgroundFillSolid(data, bot) never returns a
        BackgroundFillGradient instance."""
        cls = background_fill.__class__
        json_dict = make_json_dict(background_fill, True)
        assert type(cls.de_json(json_dict, bot)) is cls

    def test_to_dict(self, background_fill):
        bg_fill_dict = background_fill.to_dict()

        assert isinstance(bg_fill_dict, dict)
        assert bg_fill_dict["type"] == background_fill.type

        for slot in background_fill.__slots__:  # additional verification for the optional args
            if slot == "colors":
                assert getattr(background_fill, slot) == tuple(bg_fill_dict[slot])
                continue
            assert getattr(background_fill, slot) == bg_fill_dict[slot]

    def test_equality(self, background_fill):
        a = BackgroundFill(type="type")
        b = BackgroundFill(type="type")
        c = background_fill
        d = deepcopy(background_fill)
        e = Dice(4, "emoji")
        sig = inspect.signature(background_fill.__class__.__init__)
        params = [
            "random" for param in sig.parameters.values() if param.name not in [*ignored, "type"]
        ]
        f = background_fill.__class__(*params)

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

        assert c == d
        assert hash(c) == hash(d)

        assert c != e
        assert hash(c) != hash(e)

        assert f != c
        assert hash(f) != hash(c)
