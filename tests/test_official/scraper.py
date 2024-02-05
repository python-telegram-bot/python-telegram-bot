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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains functions which are used to scrape the official Bot API documentation."""

import asyncio
from dataclasses import dataclass
from typing import Literal, overload

import httpx
from bs4 import BeautifulSoup, Tag

from tests.test_official.exceptions import IGNORED_OBJECTS
from tests.test_official.helpers import (
    find_next_sibling_until,
    is_parameter_required_by_tg,
    is_pascal_case,
)


@dataclass(slots=True, frozen=True)
class TelegramParameter:
    """Represents the scraped Telegram parameter. Contains all relevant attributes needed for
    comparison. Relevant for both TelegramMethod and TelegramClass."""

    param_name: str
    param_type: str
    param_required: bool
    param_description: str


@dataclass(slots=True, frozen=True)
class TelegramClass:
    """Represents the scraped Telegram class. Contains all relevant attributes needed for
    comparison."""

    class_name: str
    class_parameters: list[TelegramParameter]
    # class_description: str


@dataclass(slots=True, frozen=True)
class TelegramMethod:
    """Represents the scraped Telegram method. Contains all relevant attributes needed for
    comparison."""

    method_name: str
    method_parameters: list[TelegramParameter]
    # method_description: str


@dataclass(slots=True, frozen=False)
class Scraper:
    request: httpx.Response | None = None
    soup: BeautifulSoup | None = None

    async def make_request(self) -> None:
        async with httpx.AsyncClient() as client:
            self.request = await client.get("https://core.telegram.org/bots/api", timeout=10)
        self.soup = BeautifulSoup(self.request.text, "html.parser")

    @overload
    def parse_docs(
        self, doc_type: Literal["method"]
    ) -> tuple[list[TelegramMethod], list[str]]: ...

    @overload
    def parse_docs(self, doc_type: Literal["class"]) -> tuple[list[TelegramClass], list[str]]: ...

    def parse_docs(self, doc_type):
        argvalues = []
        names: list[str] = []
        if self.request is None:
            asyncio.run(self.make_request())

        for unparsed in self.soup.select("h4 > a.anchor"):
            if "-" not in unparsed["name"]:
                h4: Tag | None = unparsed.parent
                name = h4.text
                if h4 is None:
                    raise AssertionError("h4 is None")
                if doc_type == "method" and name[0].lower() == name[0]:
                    params = parse_table_for_params(h4)
                    obj = TelegramMethod(method_name=name, method_parameters=params)
                    argvalues.append(obj)
                    names.append(name)
                elif doc_type == "class" and is_pascal_case(name) and name not in IGNORED_OBJECTS:
                    params = parse_table_for_params(h4)
                    obj = TelegramClass(class_name=name, class_parameters=params)
                    argvalues.append(obj)
                    names.append(name)

        return argvalues, names

    def collect_methods(self) -> tuple[list[TelegramMethod], list[str]]:
        return self.parse_docs("method")

    def collect_classes(self) -> tuple[list[TelegramClass], list[str]]:
        return self.parse_docs("class")


def parse_table_for_params(h4: Tag) -> list[TelegramParameter]:
    """Parses the Telegram doc table and outputs a list of TelegramParameter objects."""
    table = find_next_sibling_until(h4, "table", h4.find_next_sibling("h4"))
    if not table:
        return []

    params = []
    for tr in table.find_all("tr")[1:]:
        fields = []
        for td in tr.find_all("td"):
            param = td.text
            fields.append(param)

        param_name = fields[0]
        param_type = fields[1]
        param_required = is_parameter_required_by_tg(fields[2])
        param_desc = fields[-1]  # since length can be 2 or 3, but desc is always the last
        params.append(TelegramParameter(param_name, param_type, param_required, param_desc))

    return params
