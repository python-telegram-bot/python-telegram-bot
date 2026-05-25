#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2026
#  Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser Public License for more details.
#
#  You should have received a copy of the GNU Lesser Public License
#  along with this program.  If not, see [http://www.gnu.org/licenses/].
from dataclasses import dataclass
from typing import ClassVar, Self
from enum import Enum
import inspect

keyword_args = [
    "Keyword Arguments:",
    (
        "    read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to "
        "        :paramref:`telegram.request.BaseRequest.post.read_timeout`. Defaults to "
        "        :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`. "
    ),
    (
        "    write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to "
        "        :paramref:`telegram.request.BaseRequest.post.write_timeout`. Defaults to "
        "        :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`."
    ),
    (
        "    connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to "
        "        :paramref:`telegram.request.BaseRequest.post.connect_timeout`. Defaults to "
        "        :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`."
    ),
    (
        "    pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to "
        "        :paramref:`telegram.request.BaseRequest.post.pool_timeout`. Defaults to "
        "        :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`."
    ),
    (
        "    api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments"
        "        to be passed to the Telegram API. See :meth:`~telegram.Bot.do_api_request` for"
        "        limitations."
    ),
    "",
]

media_write_timeout_change_methods = [
    "add_sticker_to_set",
    "create_new_sticker_set",
    "send_animation",
    "send_audio",
    "send_document",
    "send_media_group",
    "send_photo",
    "send_sticker",
    "send_video",
    "send_video_note",
    "send_voice",
    "set_chat_photo",
    "upload_sticker_file",
]
media_write_timeout_change = [
    "    write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to "
    "        :paramref:`telegram.request.BaseRequest.post.write_timeout`. By default, ``20`` "
    "        seconds are used as write timeout."
    "",
    "",
    "       .. versionchanged:: 22.0",
    "           The default value changed to "
    "           :attr:`~telegram.request.BaseRequest.DEFAULT_NONE`.",
    "",
    "",
]
get_updates_read_timeout_addition = [
    "        :paramref:`timeout` will be added to this value.",
    "",
    "",
    "        .. versionchanged:: 20.7",
    "           Defaults to :attr:`~telegram.request.BaseRequest.DEFAULT_NONE` instead of ",
    "           ``2``.",
]

RAISES_BLOCK = [
    "Raises:",
    "",
    "    :class:`telegram.error.TelegramError`",
    "",
]


def find_insert_pos_for_kwargs(lines: list[str]) -> int:
    """Finds the correct position to insert the keyword arguments and returns the index."""
    for idx, value in reversed(list(enumerate(lines))):  # reversed since :returns: is at the end
        if value.startswith("Returns"):
            return idx
    return False


def find_insert_pos_for_raises(lines: list[str]) -> int:
    """Finds the correct position to insert the Raises block and returns the index."""
    if "Raises:" in lines:
        return -1  # Don't insert if there's already a Raises block
    return len(lines)  # Insert at the end if there's no Raises block


def check_timeout_and_api_kwargs_presence(obj: object) -> int:
    """Checks if the method has timeout and api_kwargs keyword only parameters."""
    sig = inspect.signature(obj)
    params_to_check = (
        "read_timeout",
        "write_timeout",
        "connect_timeout",
        "pool_timeout",
        "api_kwargs",
    )
    return all(
        param in sig.parameters and sig.parameters[param].kind == inspect.Parameter.KEYWORD_ONLY
        for param in params_to_check
    )


class SectionTitle(str, Enum):
    __slots__ = ()

    RAISES = "Raises:"
    RETURNS = "Returns:"
    ARGUMENTS = "Args:"
    ATTRIBUTES = "Attributes:"
    KWARGS = "Keyword Args:"


@dataclass(frozen=True, slots=True)
class ParsedEntry:
    name: str | None  # name of param/attr
    type: str | None  # the type, e.g. :obj:`str`
    required: bool | None  # whether this is a required param or not
    description: list[str]  # actual documentation, including admonitions like versionchanged

    def to_list(self, is_param: bool) -> list[str]:
        """
        Converts the ParsedEntry into a list of strings that can be inserted into the docstring.
        This includes formatting the name, type, and description appropriately.

        Args:
            is_param (bool): Whether this entry represents a parameter (True) or an attribute.
        """
        lines = []
        if self.name and self.type:
            if self.required:
                param_line = f"{self.name} ({self.type}): "
            else:
                if is_param:
                    param_line = f"{self.name} ({self.type}, optional): "
                else:
                    param_line = f"{self.name} ({self.type}): Optional. "
            lines.append(param_line)

        lines.extend(self.description)
        return lines


@dataclass(slots=True)
class Section:
    """
    Dataclass to represent a section in the documentation, such as "Keyword Arguments",
    "Raises", or "Attributes". It contains the title of the section and the content.
    """

    title: ClassVar[SectionTitle]
    content: list[ParsedEntry]

    def parse_section(self, lines: list[str], title: SectionTitle) -> Self:
        """
        Parses a section from the given lines based on the title and returns a Section object.
        """


@dataclass(slots=True)
class Docstring:
    """
    Dataclass to represent the entire docstring, which may contain multiple sections like
    "Arguments", "Raises", "Attributes", etc.
    """

    name: str  # name of the method/class
    description: list[str]  # the initial description, including admonitions, and wiki links
    sections: list[Section]  # the various sections of the docstring


@dataclass(slots=True)
class DocstringGenerator:
    """
    Class to handle the generation and insertion of various sections of the documentation
    such as "Keyword Arguments", "Raises", and "Attributes".
    """

    CURRENT_DOCSTRING: ClassVar[Docstring | None] = None

    @staticmethod
    def parse_docstring(lines: list[str], name: str) -> Docstring:
        """
        Parses the raw docstring and constructs a Docstring object with structured sections.
        """
        # Preserve everything before the first section title as the description:
        description_lines = []
        for line in lines:
            if any(line.startswith(title.value) for title in SectionTitle):
                break
            description_lines.append(line)
        else:
            # If we never break, it means there are no sections:
            return Docstring(name=name, description=description_lines, sections=[])
        # Handoff the entire lines to the Section.parse_section::

    @staticmethod
    def insert_kwargs_in_bot_method(lines: list[str], obj_signature: inspect.Signature) -> None:
        """
        Inserts the "Keyword Arguments" section into the docstring of a Bot method.
        The insertion point is determined by the position of the "Returns" section.
        """

        # Check if we have a Docstring object to parse on:
        if not DocstringGenerator.CURRENT_DOCSTRING:
            DocstringGenerator.CURRENT_DOCSTRING = DocstringGenerator.parse_docstring(lines)

        insert_index = find_insert_pos_for_kwargs(lines)
        if not insert_index:
            raise ValueError(
                f"Couldn't find the correct position to insert the keyword args for {obj_signature}."
            )

        # Logic for inserting keyword args into docstrings:
        # -------------------------------------------------
        insert_idx = insert_index
        for i in range(insert_index, insert_index + len(keyword_args)):
            to_insert = keyword_args[i - insert_index]

            if (
                "post.write_timeout`. Defaults to" in to_insert
                and obj_signature.parameters.get("write_timeout", None) is not None
            ):
                effective_insert: list[str] = media_write_timeout_change
            elif obj_signature.parameters.get(
                "read_timeout", None
            ) is not None and to_insert.lstrip().startswith("read_timeout"):
                effective_insert = [to_insert, *get_updates_read_timeout_addition]
            else:
                effective_insert = [to_insert]

            lines[insert_idx:insert_idx] = effective_insert
            insert_idx += len(effective_insert)
