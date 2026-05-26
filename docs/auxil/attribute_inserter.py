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
"""Automatic generation of ``Attributes:`` section entries from ``Args:`` in class docstrings."""

import inspect
import re
import warnings
from dataclasses import dataclass

from telegram import TelegramObject

ENTRY_PATTERN: re.Pattern[str] = re.compile(r"^    (\w+) \((.+)\):\s*(.*)")

KNOWN_SECTION_TITLES: frozenset[str] = frozenset(
    {
        "Args",
        "Attributes",
        "Returns",
        "Raises",
        "Note",
        "Notes",
        "Example",
        "Examples",
        "Keyword Args",
        "Keyword Arguments",
    }
)


def _is_section_header(line: str) -> bool:
    return line.endswith(":") and line[:-1] in KNOWN_SECTION_TITLES


def _is_col0_noncontent(line: str) -> bool:
    """Non-blank col-0 line that is not a section header (e.g. RST substitution definitions)."""
    return bool(line) and not line[0].isspace() and not _is_section_header(line)


def _save_entry(
    entries: dict[str, "DocstringEntry"],
    name: str,
    raw_type: str,
    raw_lines: list[str],
) -> None:
    lines = list(raw_lines)
    while lines and lines[-1] == "":
        lines.pop()

    is_optional = raw_type.endswith(", optional")
    type_str = raw_type.removesuffix(", optional") if is_optional else raw_type

    entries[name] = DocstringEntry(
        name=name,
        type_str=type_str,
        is_optional=is_optional,
        all_lines=tuple(lines),
    )


@dataclass(frozen=True, slots=True)
class DocstringEntry:
    name: str
    type_str: str
    is_optional: bool
    all_lines: tuple[str, ...]

    def to_attribute_lines(self) -> list[str]:
        if not self.all_lines:
            warnings.warn(
                f"DocstringEntry {self.name!r} has no lines; skipping attribute generation.",
                stacklevel=2,
            )
            return []

        m = ENTRY_PATTERN.match(self.all_lines[0])
        if m is None:
            warnings.warn(
                f"DocstringEntry {self.name!r}: first line does not match the entry pattern "
                f"({self.all_lines[0]!r}); returning raw lines unchanged.",
                stacklevel=2,
            )
            return list(self.all_lines)

        desc: str = m.group(3)
        new_type = self.type_str.replace("Sequence[", "tuple[")
        new_desc = f"Optional. {desc}" if self.is_optional else desc
        return [f"    {self.name} ({new_type}): {new_desc}", *self.all_lines[1:]]


@dataclass(slots=True)
class DocstringSection:
    title: str
    entries: dict[str, DocstringEntry]
    start_idx: int
    end_idx: int


class DocstringParser:
    """Parse a Google-style docstring (list of lines) into sections and entries."""

    __slots__ = ("_lines", "_sections")

    def __init__(self, lines: list[str]) -> None:
        self._lines = lines
        self._sections: dict[str, DocstringSection] | None = None

    @property
    def sections(self) -> dict[str, DocstringSection]:
        if self._sections is None:
            self._sections = self._parse()
        return self._sections

    def get_section(self, title: str) -> DocstringSection | None:
        return self.sections.get(title)

    def _parse(self) -> dict[str, DocstringSection]:
        sections: dict[str, DocstringSection] = {}
        lines = self._lines
        n = len(lines)
        i = 0

        while i < n:
            line = lines[i]
            if _is_section_header(line):
                title = line[:-1]
                start_idx = i
                i += 1
                entries, end_idx = self._parse_section_entries(i, n)
                i = end_idx
                sections[title] = DocstringSection(
                    title=title,
                    entries=entries,
                    start_idx=start_idx,
                    end_idx=end_idx,
                )
            else:
                i += 1

        return sections

    def _parse_section_entries(
        self,
        start: int,
        end: int,
    ) -> tuple[dict[str, DocstringEntry], int]:
        entries: dict[str, DocstringEntry] = {}
        current_name: str | None = None
        current_raw_type: str = ""
        current_lines: list[str] = []

        lines = self._lines
        i = start

        while i < end:
            line = lines[i]

            # RST substitution definitions and other on-section content end the section.
            if _is_section_header(line) or _is_col0_noncontent(line):
                break

            m = ENTRY_PATTERN.match(line)
            if m:
                if current_name is not None:
                    _save_entry(entries, current_name, current_raw_type, current_lines)
                current_name = m.group(1)
                current_raw_type = m.group(2)
                current_lines = [line]
            elif current_name is not None:
                current_lines.append(line)

            i += 1

        if current_name is not None:
            _save_entry(entries, current_name, current_raw_type, current_lines)

        return entries, i


class AttributeInserter:
    """Inserts auto-generated ``Attributes:`` entries into class docstrings."""

    def insert_attributes(self, obj: type, lines: list[str]) -> None:
        """Insert missing attribute entries derived from the ``Args:`` section in-place."""
        parser = DocstringParser(lines)

        args_section = parser.get_section("Args")
        attrs_section = parser.get_section("Attributes")

        already_documented: set[str] = (
            set(attrs_section.entries.keys()) if attrs_section is not None else set()
        )
        args_entries: dict[str, DocstringEntry] = (
            args_section.entries if args_section is not None else {}
        )
        args_names: set[str] = set(args_entries.keys())

        properties_on_class: set[str] = {
            name for name, _ in inspect.getmembers(obj, lambda o: isinstance(o, property))
        }

        # Warn about own public slots that have no documentation source.
        # Get slots from TGObject if it's a TGObj subclass:
        if issubclass(obj, TelegramObject):
            all_slots = {
                s
                for c in obj.__mro__[:-1]
                if issubclass(c, TelegramObject)
                for s in c.__slots__
                if not s.startswith("_")
            }
            all_slots.remove("api_kwargs")
        else:
            all_slots = (s for s in getattr(obj, "__slots__", ()) if not s.startswith("_"))
        for slot in all_slots:
            if (
                slot not in already_documented
                and slot not in args_names
                and slot not in properties_on_class
            ):
                warnings.warn(
                    f"Class {obj.__qualname__!r}: public slot {slot!r} has no documentation "
                    f"source. Please add it to the 'Attributes:' section manually.",
                    stacklevel=2,
                )

        new_attr_lines: list[str] = []
        for name, entry in args_entries.items():
            if name in already_documented or name in properties_on_class:
                continue
            new_attr_lines.extend(entry.to_attribute_lines())
            new_attr_lines.append("")

        if not new_attr_lines:
            return

        if attrs_section is not None:
            insert_idx = attrs_section.end_idx
            while insert_idx > attrs_section.start_idx + 1 and lines[insert_idx - 1] == "":
                insert_idx -= 1
            lines[insert_idx:insert_idx] = new_attr_lines
        else:
            if lines and lines[-1].strip():
                lines.append("")
            lines.append("Attributes:")
            lines.extend(new_attr_lines)
