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

import dataclasses
import datetime as dtm
import inspect
from collections.abc import Sequence
from dataclasses import FrozenInstanceError
from types import MappingProxyType

import pytest

from telegram import constants
from telegram._dice import Dice
from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import (
    float_to_timedelta,
    int_to_timedelta,
    parse_sequence_arg,
)
from telegram._utils.dataclass import (
    ALIAS_KEY,
    CONVERTER_KEY,
    ENUM_KEY,
    process_init,
    tg_dataclass,
    tg_field,
)


class TestTGDataclass:
    @pytest.mark.parametrize("eq", [True, False])
    def test_frozen_slots_repr_defaults(self, eq):

        @tg_dataclass(eq=eq)
        class A:
            field: str

        a = A("field")

        with pytest.raises(FrozenInstanceError):
            a.field = "not_field"
        assert a.__slots__ == ("field",)
        assert A.__repr__ is object.__repr__

    def test_eq(self):

        @tg_dataclass(eq=True)
        class A:
            field: str

        assert hasattr(A, "__eq__")
        assert A.__eq__ is not object.__eq__

        @tg_dataclass(eq=False)
        class B:
            field: str

        assert B.__eq__ is object.__eq__

        @tg_dataclass()
        class C:
            field: str

        assert hasattr(C, "__eq__")
        assert C.__eq__ is not object.__eq__

    def test_hash_includes_class_name(self):
        @tg_dataclass(eq=True)
        class A:
            id: str = tg_field(compare=True)

        a1 = A("123")
        a2 = A("123")
        assert hash(a1) == hash(a2)

        @tg_dataclass(eq=True)
        class B:
            field: str

        b1 = B("123")
        assert hash(a1) != hash(b1)

    def test_pickle_protocol_methods_on_tg_object_only(self):
        assert hasattr(TelegramObject, "__getstate__")
        assert TelegramObject.__getstate__ is not object.__getstate__

        assert hasattr(TelegramObject, "__setstate__")
        # python has not builtin `object.__setstate__`

        @tg_dataclass(eq=True)
        class A(TelegramObject):
            pass

        assert A.__getstate__ is TelegramObject.__getstate__
        assert A.__setstate__ is TelegramObject.__setstate__


class TestTGField:
    def test_field_metadata_population(self):

        @tg_dataclass()
        class A:
            converter: tuple[str] = tg_field(converter=parse_sequence_arg)
            _alias: int = tg_field(alias="alias")
            type: str = tg_field(enum=constants.StoryAreaTypeType)

            converter_alias: tuple[str] = tg_field(converter=parse_sequence_arg, alias="c_a")
            type_alias: tuple[str] = tg_field(enum=constants.StoryAreaTypeType, alias="t_a")

            bare: str = tg_field()

        fields = {
            dataclass_field.name: dataclass_field for dataclass_field in dataclasses.fields(A)
        }

        assert fields["converter"].metadata.get(CONVERTER_KEY) == parse_sequence_arg
        assert fields["converter"].metadata.get(ALIAS_KEY) is None
        assert fields["converter"].metadata.get(ENUM_KEY) is None

        assert fields["_alias"].metadata.get(CONVERTER_KEY) is None
        assert fields["_alias"].metadata.get(ALIAS_KEY) == "alias"
        assert fields["_alias"].metadata.get(ENUM_KEY) is None

        # We only test that its callable here, actuall enum conversion is tested under each class
        assert callable(fields["type"].metadata.get(CONVERTER_KEY))
        assert fields["type"].metadata.get(ALIAS_KEY) is None
        assert fields["type"].metadata.get(ENUM_KEY) is True

        assert fields["converter_alias"].metadata.get(CONVERTER_KEY) == parse_sequence_arg
        assert fields["converter_alias"].metadata.get(ALIAS_KEY) == "c_a"
        assert fields["converter_alias"].metadata.get(ENUM_KEY) is None

        assert callable(fields["type_alias"].metadata.get(CONVERTER_KEY))
        assert fields["type_alias"].metadata.get(ALIAS_KEY) == "t_a"
        assert fields["type_alias"].metadata.get(ENUM_KEY) is True

        assert fields["bare"].metadata == MappingProxyType({})

    def test_enum_mutually_exclusive_converter(self):
        with pytest.raises(ValueError, match="`enum` and `converter` are mutually exclusive!"):

            @tg_dataclass()
            class A:
                field: str = tg_field(
                    enum=constants.StoryAreaTypeType, converter=parse_sequence_arg
                )


class TestProcessInit:
    def test_processes_dataclass_only(self):
        class A:
            pass

        with pytest.raises(TypeError, match="is not a dataclass"):
            process_init(A)

    def test_alias_runtime_support(self):
        @tg_dataclass()
        class A:
            _deprecated: str = tg_field(alias="deprecated")

        a = A(deprecated="test")
        assert a._deprecated == "test"

        with pytest.raises(TypeError, match="got an unexpected keyword argument '_deprecated'"):
            A(_deprecated="test")

    def test_alias_signature_param_name_swap(self):
        @tg_dataclass()
        class A:
            _deprecated: str = tg_field(alias="deprecated")

        init_sig = inspect.signature(A.__init__)
        param = list(init_sig.parameters.values())[1]  # `0` is `self`
        assert param.name == "deprecated"

    def test_processed_type_annotations(self):
        @tg_dataclass()
        class A:
            @staticmethod
            def bytes_to_str(value: bytes | None) -> str:
                if value is None:
                    return ""
                return value.decode()

            @staticmethod
            def tuple_xy_points(
                points: Sequence[Sequence[int]],
            ) -> tuple[tuple[int, ...], ...]:
                return tuple(tuple(val for val in point) for point in points)

            # Required
            bare: str = tg_field()
            seq: tuple[str, ...] = tg_field(converter=parse_sequence_arg)
            nested_seq: tuple[tuple[int, ...], ...] = tg_field(converter=tuple_xy_points)
            type: str = tg_field(enum=constants.StoryAreaTypeType)
            name: str = tg_field(converter=bytes_to_str)
            tg_obj: Dice = tg_field()
            int_duration: dtm.timedelta = tg_field(converter=int_to_timedelta)
            float_duration: dtm.timedelta = tg_field(converter=float_to_timedelta)

            # Optional
            bare_opt: str | None = tg_field(default=None)
            seq_opt: tuple[str, ...] = tg_field(converter=parse_sequence_arg, default=None)
            nested_seq_opt: tuple[tuple[int, ...], ...] = tg_field(
                converter=tuple_xy_points, default=None
            )
            type_opt: str | None = tg_field(enum=constants.StoryAreaTypeType, default=None)
            name_opt: str = tg_field(converter=bytes_to_str, default=None)
            tg_obj_opt: Dice | None = tg_field(default=None)
            int_duration_opt: dtm.timedelta | None = tg_field(
                converter=int_to_timedelta, default=None
            )
            float_duration_opt: dtm.timedelta | None = tg_field(
                converter=float_to_timedelta, default=None
            )

        @tg_dataclass()
        class B:
            # A  few optional fields *with* aliases
            _tg_obj_opt: Dice | None = tg_field(default=None, alias="tg_obj_opt_alias")
            _int_duration_opt: dtm.timedelta | None = tg_field(
                converter=int_to_timedelta, default=None, alias="int_duration_opt_alias"
            )
            _type_opt: str | None = tg_field(
                enum=constants.StoryAreaTypeType, default=None, alias="type_opt_alias"
            )

        init_sig = inspect.signature(A.__init__)
        params = {param.name: param for param in init_sig.parameters.values()}

        assert params["bare"].annotation is str
        assert params["bare_opt"].annotation == str | None
        assert params["seq"].annotation == Sequence[str]
        assert params["seq_opt"].annotation == Sequence[str] | None
        assert params["nested_seq"].annotation == Sequence[Sequence[int]]
        assert params["nested_seq_opt"].annotation == Sequence[Sequence[int]] | None
        assert params["type"].annotation is str
        assert params["type_opt"].annotation == str | None
        assert params["name"].annotation is bytes
        assert params["name_opt"].annotation == bytes | None
        assert params["tg_obj"].annotation is Dice
        assert params["tg_obj_opt"].annotation == Dice | None
        assert params["int_duration"].annotation == int | dtm.timedelta
        assert params["int_duration_opt"].annotation == int | dtm.timedelta | None
        assert params["float_duration"].annotation == float | dtm.timedelta
        assert params["float_duration_opt"].annotation == float | dtm.timedelta | None

        # With no aliases, the dataclass generated __init__ should not be overwritten
        assert not hasattr(A.__init__, "__wrapped__")

        init_sig = inspect.signature(B.__init__)
        params = {param.name: param for param in init_sig.parameters.values()}

        assert params["tg_obj_opt_alias"].annotation == Dice | None
        assert params["int_duration_opt_alias"].annotation == int | dtm.timedelta | None
        assert params["type_opt_alias"].annotation == str | None

        assert hasattr(B.__init__, "__wrapped__")
