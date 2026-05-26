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

"""
This module is intentionally named without a "test_" prefix.
These tests are supposed to be run on GitHub when building docs.
The tests require Python 3.12+ (just like AttributeInserter being tested), so they cannot be
included in the main suite while older versions of Python are supported.
"""

import pytest

from docs.auxil.attribute_inserter import (
    ENTRY_PATTERN,
    KNOWN_SECTION_TITLES,
    AttributeInserter,
    DocstringEntry,
    DocstringParser,
    _is_col0_noncontent,
    _is_section_header,
)


@pytest.fixture
def inserter():
    return AttributeInserter()


class TestHelpers:
    def test_entry_pattern_matches_simple(self):
        m = ENTRY_PATTERN.match("    name (:obj:`str`): The name.")
        assert m is not None
        assert m.group(1) == "name"
        assert m.group(2) == ":obj:`str`"
        assert m.group(3) == "The name."

    def test_entry_pattern_matches_optional(self):
        m = ENTRY_PATTERN.match(
            "    invite_link (:class:`telegram.ChatInviteLink`, optional): Chat invite link."
        )
        assert m is not None
        assert m.group(1) == "invite_link"
        assert m.group(2) == ":class:`telegram.ChatInviteLink`, optional"
        assert m.group(3) == "Chat invite link."

    def test_entry_pattern_matches_sequence(self):
        m = ENTRY_PATTERN.match(
            "    stickers (Sequence[:class:`telegram.Sticker`]): List of all set stickers."
        )
        assert m is not None
        assert m.group(1) == "stickers"
        assert m.group(2) == "Sequence[:class:`telegram.Sticker`]"
        assert m.group(3) == "List of all set stickers."

    def test_entry_pattern_rejects_wrong_indent(self):
        # 8-space indent should not match
        assert ENTRY_PATTERN.match("        name (:obj:`str`): desc.") is None

    def test_entry_pattern_rejects_no_type(self):
        # No parenthesised type
        assert ENTRY_PATTERN.match("    name: description") is None

    def test_is_section_header_known_titles(self):
        for title in KNOWN_SECTION_TITLES:
            assert _is_section_header(f"{title}:")

    def test_is_section_header_unknown_title(self):
        assert not _is_section_header("FooBar:")

    def test_is_section_header_indented(self):
        assert not _is_section_header("    Args:")
        assert not _is_section_header("        Note:")

    def test_is_section_header_no_colon(self):
        assert not _is_section_header("Args")


class TestDocstringEntry:
    def test_to_attribute_lines_simple(self):
        """Non-optional arg with a plain type produces attribute line unchanged."""
        entry = DocstringEntry(
            name="title",
            type_str=":obj:`str`",
            is_optional=False,
            all_lines=("    title (:obj:`str`): Sticker set title.",),
        )
        assert entry.to_attribute_lines() == ["    title (:obj:`str`): Sticker set title."]

    def test_to_attribute_lines_optional(self):
        """Optional arg: 'Optional. ' prepended to description, type has no ', optional'."""
        entry = DocstringEntry(
            name="invite_link",
            type_str=":class:`telegram.ChatInviteLink`",
            is_optional=True,
            all_lines=(
                "    invite_link (:class:`telegram.ChatInviteLink`, optional): Chat invite link.",
            ),
        )
        result = entry.to_attribute_lines()
        assert result == [
            "    invite_link (:class:`telegram.ChatInviteLink`): Optional. Chat invite link."
        ]

    def test_to_attribute_lines_sequence_not_optional(self):
        """Sequence[ in type is replaced; body lines pass through unchanged."""
        entry = DocstringEntry(
            name="stickers",
            type_str="Sequence[:class:`telegram.Sticker`]",
            is_optional=False,
            all_lines=(
                "    stickers (Sequence[:class:`telegram.Sticker`]): List of all set stickers.",
                "",
                "        .. versionchanged:: 20.0",
                "            |sequenceclassargs|",
            ),
        )
        result = entry.to_attribute_lines()
        assert (
            result[0]
            == "    stickers (tuple[:class:`telegram.Sticker`]): List of all set stickers."
        )
        # Body lines are unchanged - no substitution replacement
        assert "            |sequenceclassargs|" in result
        assert "|tupleclassattrs|" not in "\n".join(result)

    def test_to_attribute_lines_sequence_optional(self):
        """Optional Sequence: type replaced, Optional. prefix, body passes through."""
        entry = DocstringEntry(
            name="caption_entities",
            type_str="Sequence[:class:`telegram.MessageEntity`]",
            is_optional=True,
            all_lines=(
                "    caption_entities "
                "(Sequence[:class:`telegram.MessageEntity`], optional): |caption_entities|",
                "",
                "        .. versionchanged:: 20.0",
                "                |sequenceclassargs|",
            ),
        )
        result = entry.to_attribute_lines()
        assert result[0].startswith(
            "    caption_entities (tuple[:class:`telegram.MessageEntity`]): Optional."
        )
        # Body lines unchanged
        assert "                |sequenceclassargs|" in result

    def test_to_attribute_lines_no_trailing_blank(self):
        """to_attribute_lines() never appends a trailing blank line."""
        entry = DocstringEntry(
            name="x",
            type_str=":obj:`int`",
            is_optional=False,
            all_lines=("    x (:obj:`int`): Some value.",),
        )
        result = entry.to_attribute_lines()
        assert result[-1] != ""

    def test_to_attribute_lines_empty_all_lines_warns(self):
        entry = DocstringEntry(
            name="x",
            type_str=":obj:`int`",
            is_optional=False,
            all_lines=(),
        )
        with pytest.warns(UserWarning, match="no lines"):
            result = entry.to_attribute_lines()
        assert result == []

    def test_to_attribute_lines_sequence_replaced_in_type(self):
        """'Sequence[' is replaced with 'tuple[' in the header type string."""
        entry = DocstringEntry(
            name="items",
            type_str="Sequence[:obj:`str`]",
            is_optional=False,
            all_lines=("    items (Sequence[:obj:`str`]): Some items.",),
        )
        result = entry.to_attribute_lines()
        assert "tuple[:obj:`str`]" in result[0]
        assert "Sequence" not in result[0]

    def test_to_attribute_lines_optional_empty_description(self):
        """When the description is empty, 'Optional.' is still produced cleanly."""
        entry = DocstringEntry(
            name="flag",
            type_str=":obj:`bool`",
            is_optional=True,
            all_lines=("    flag (:obj:`bool`, optional): ",),
        )
        result = entry.to_attribute_lines()
        # The description part starts with "Optional. " (trailing space if original desc is empty)
        assert result[0].startswith("    flag (:obj:`bool`): Optional.")


class TestDocstringParser:
    def test_sections_empty_docstring(self):
        parser = DocstringParser([])
        assert parser.sections == {}

    def test_sections_no_sections(self):
        parser = DocstringParser(["Just a description.", "No sections here."])
        assert parser.sections == {}

    def test_parse_single_args_section(self):
        lines = [
            "Description.",
            "",
            "Args:",
            "    name (:obj:`str`): The name.",
            "    value (:obj:`int`, optional): The value.",
        ]
        parser = DocstringParser(lines)
        assert "Args" in parser.sections

        args = parser.sections["Args"]
        assert args.start_idx == 2
        assert args.end_idx == 5
        assert set(args.entries.keys()) == {"name", "value"}

        assert args.entries["name"].is_optional is False
        assert args.entries["name"].type_str == ":obj:`str`"

        assert args.entries["value"].is_optional is True
        assert args.entries["value"].type_str == ":obj:`int`"

    def test_parse_preserves_continuation_lines(self):
        lines = [
            "Args:",
            "    stickers (Sequence[:class:`telegram.Sticker`]): List of stickers.",
            "",
            "        .. versionchanged:: 20.0",
            "            |sequenceclassargs|",
        ]
        parser = DocstringParser(lines)
        entry = parser.sections["Args"].entries["stickers"]
        # Trailing blank line should be stripped from all_lines.
        assert entry.all_lines == (
            "    stickers (Sequence[:class:`telegram.Sticker`]): List of stickers.",
            "",
            "        .. versionchanged:: 20.0",
            "            |sequenceclassargs|",
        )

    def test_parse_multiple_sections(self):
        lines = [
            "Args:",
            "    name (:obj:`str`): The name.",
            "",
            "Attributes:",
            "    name (:obj:`str`): The name.",
            "",
        ]
        parser = DocstringParser(lines)
        assert "Args" in parser.sections
        assert "Attributes" in parser.sections

        args = parser.sections["Args"]
        attrs = parser.sections["Attributes"]

        assert args.start_idx == 0
        assert args.end_idx == 3  # stops at "Attributes:" line
        assert attrs.start_idx == 3
        assert attrs.end_idx == 6

    def test_parse_end_idx_at_eof(self):
        lines = [
            "Args:",
            "    name (:obj:`str`): The name.",
        ]
        parser = DocstringParser(lines)
        assert parser.sections["Args"].end_idx == 2  # == len(lines)

    def test_get_section_args_present(self):
        """'Args:' header is found when requesting 'Args'."""
        lines = [
            "Args:",
            "    x (:obj:`str`): X.",
        ]
        parser = DocstringParser(lines)
        section = parser.get_section("Args")
        assert section is not None
        assert section.title == "Args"

    def test_col0_rst_directive_terminates_section(self):
        """An RST substitution definition at column 0 stops section parsing."""
        lines = [
            "Attributes:",
            "    name (:obj:`str`): The name.",
            "",
            ".. |user_chat_id_note| replace:: This shortcut builds on the assumption.",
            "    continued text here.",
        ]
        parser = DocstringParser(lines)
        attrs = parser.sections["Attributes"]
        # The section ends before the substitution definition.
        assert attrs.end_idx == 3  # points to the blank line before the directive
        assert "name" in attrs.entries

    def test_is_col0_noncontent_cases(self):
        assert _is_col0_noncontent(".. |foo| replace:: bar")
        assert not _is_col0_noncontent("    some text")
        assert not _is_col0_noncontent("")
        assert not _is_col0_noncontent("Args:")

    def test_get_section_absent_returns_none(self):
        parser = DocstringParser(["Description."])
        assert parser.get_section("Args") is None
        assert parser.get_section("Attributes") is None

    def test_sections_lazily_parsed(self):
        parser = DocstringParser(["Args:", "    x (:obj:`str`): X."])
        assert parser._sections is None  # not yet parsed
        _ = parser.sections
        assert parser._sections is not None  # now parsed

    def test_parse_strips_trailing_blank_lines_from_entry(self):
        lines = [
            "Args:",
            "    name (:obj:`str`): The name.",
            "",
            "",
        ]
        parser = DocstringParser(lines)
        entry = parser.sections["Args"].entries["name"]
        # Trailing blank lines must not be part of all_lines.
        assert entry.all_lines == ("    name (:obj:`str`): The name.",)

    def test_parse_indented_section_like_line_is_not_a_header(self):
        """A line like '    Note:' inside an entry is continuation, not a new section."""
        lines = [
            "Args:",
            "    name (:obj:`str`): The name.",
            "        Note: some note.",
        ]
        parser = DocstringParser(lines)
        # "    Note:" must NOT have ended the Args section.
        assert parser.sections["Args"].end_idx == 3
        entry = parser.sections["Args"].entries["name"]
        assert len(entry.all_lines) == 2


class TestAttributeInserter:
    def test_no_args_section_noop(self, inserter):
        """If there is no Args section, lines must not be modified."""
        lines = ["Just a description."]
        original = list(lines)
        inserter.insert_attributes(object, lines)
        assert lines == original

    def test_creates_attributes_section(self, inserter):
        """When no Attributes section exists one is created."""
        lines = [
            "Description.",
            "",
            "Args:",
            "    name (:obj:`str`): The name.",
        ]
        inserter.insert_attributes(object, lines)

        assert "Attributes:" in lines
        attr_idx = lines.index("Attributes:")
        assert "    name (:obj:`str`): The name." in lines[attr_idx:]

    def test_creates_attributes_section_with_separator(self, inserter):
        """A blank line is added between existing content and the new Attributes header."""
        lines = [
            "Args:",
            "    name (:obj:`str`): The name.",
        ]
        inserter.insert_attributes(object, lines)
        attr_idx = lines.index("Attributes:")
        # The line before "Attributes:" must be blank.
        assert lines[attr_idx - 1] == ""

    def test_no_separator_if_already_blank(self, inserter):
        """No extra blank line is inserted before Attributes: if the last line is already blank."""
        lines = [
            "Args:",
            "    name (:obj:`str`): The name.",
            "",
        ]
        inserter.insert_attributes(object, lines)
        attr_idx = lines.index("Attributes:")
        assert lines[attr_idx - 1] == ""
        # There must not be two consecutive blank lines before the header.
        if attr_idx >= 2:
            assert not (lines[attr_idx - 1] == "" and lines[attr_idx - 2] == "")

    def test_skips_already_documented_attributes(self, inserter):
        """Attributes already present in the Attributes section are not duplicated."""
        lines = [
            "Args:",
            "    name (:obj:`str`): The name.",
            "",
            "Attributes:",
            "    name (:obj:`str`): The name.",
        ]
        original_len = len(lines)
        inserter.insert_attributes(object, lines)
        # Nothing new should have been added.
        assert len(lines) == original_len

    def test_inserts_missing_into_existing_section(self, inserter):
        """When some args are missing from Attributes, they are appended to the section."""
        lines = [
            "Args:",
            "    name (:obj:`str`): The name.",
            "    title (:obj:`str`): The title.",
            "",
            "Attributes:",
            "    name (:obj:`str`): The name.",
        ]
        inserter.insert_attributes(object, lines)

        attr_idx = lines.index("Attributes:")
        attrs_block = lines[attr_idx:]
        assert "    title (:obj:`str`): The title." in attrs_block

    def test_inserts_before_trailing_blanks(self, inserter):
        """New entries are inserted before any trailing blank lines in the Attributes section."""
        lines = [
            "Args:",
            "    title (:obj:`str`): The title.",
            "",
            "Attributes:",
            "    name (:obj:`str`): The name.",
            "",
        ]
        inserter.insert_attributes(object, lines)

        attr_idx = lines.index("Attributes:")
        attrs_block = lines[attr_idx:]
        title_idx = attrs_block.index("    title (:obj:`str`): The title.")
        # The trailing blank from the original section should still be present.
        assert "" in attrs_block[title_idx + 1 :]

    def test_optional_gets_optional_prefix(self, inserter):
        """Optional args produce 'Optional. ' prefix in the generated attribute entry."""
        lines = [
            "Args:",
            "    thumb (:class:`telegram.PhotoSize`, optional): The thumbnail.",
        ]
        inserter.insert_attributes(object, lines)
        assert "    thumb (:class:`telegram.PhotoSize`): Optional. The thumbnail." in lines

    def test_sequence_type_replaced(self, inserter):
        """'Sequence[' is replaced with 'tuple[' in generated attribute entries."""
        lines = [
            "Args:",
            "    items (Sequence[:obj:`str`]): The items.",
        ]
        inserter.insert_attributes(object, lines)
        attr_idx = lines.index("Attributes:")
        attrs_block = "\n".join(lines[attr_idx:])
        assert "tuple[:obj:`str`]" in attrs_block
        assert "Sequence" not in attrs_block

    def test_property_not_duplicated(self, inserter):
        """Args entries that correspond to a property on the class are not generated."""

        class _MyClass:
            __slots__ = ("_value",)

            @property
            def value(self) -> int:
                return self._value  # type: ignore[return-value]

        lines = [
            "Args:",
            "    value (:obj:`int`): The value.",
        ]
        inserter.insert_attributes(_MyClass, lines)
        # No Attributes section should be created because 'value' is a property.
        assert "Attributes:" not in lines

    def test_undocumented_public_slot_warns(self, inserter):
        """A public own slot with no Args entry and no Attributes entry raises a warning."""

        class _MyClass:
            __slots__ = ("computed",)

        lines = [
            "Args:",
            "    name (:obj:`str`): The name.",
        ]
        with pytest.warns(UserWarning, match="public slot 'computed'"):
            inserter.insert_attributes(_MyClass, lines)

    def test_rst_substitution_after_attributes_not_swallowed(self, inserter):
        """RST substitution definitions after Attributes section are preserved intact."""
        lines = [
            "Args:",
            "    name (:obj:`str`): The name.",
            "",
            "Attributes:",
            "    name (:obj:`str`): The name.",
            "",
            ".. |my_note| replace:: Some note text.",
            "    continued.",
        ]
        original_directive_line = lines[6]
        inserter.insert_attributes(object, lines)
        # The substitution definition must still be present and in the right place.
        assert original_directive_line in lines
        assert lines.index(original_directive_line) == 6

    def test_sequence_classargs_substitution_non_optional(self, inserter):
        """Full round-trip: Sequence->tuple in type; body lines pass through unchanged."""
        lines = [
            "Args:",
            "    stickers (Sequence[:class:`telegram.Sticker`]): List of stickers.",
            "",
            "        .. versionchanged:: 20.0",
            "            |sequenceclassargs|",
        ]
        inserter.insert_attributes(object, lines)

        attr_idx = lines.index("Attributes:")
        attrs_block = lines[attr_idx:]
        assert "    stickers (tuple[:class:`telegram.Sticker`]): List of stickers." in attrs_block
        # Body lines pass through unchanged
        assert "            |sequenceclassargs|" in attrs_block
        assert "|tupleclassattrs|" not in "\n".join(attrs_block)

    def test_sequence_classargs_substitution_optional(self, inserter):
        """Full round-trip: optional Sequence; body lines pass through unchanged."""
        lines = [
            "Args:",
            "    items (Sequence[:obj:`str`], optional): The items.",
            "",
            "        .. versionchanged:: 20.0",
            "                |sequenceclassargs|",
        ]
        inserter.insert_attributes(object, lines)

        attr_idx = lines.index("Attributes:")
        attrs_block = lines[attr_idx:]
        assert "    items (tuple[:obj:`str`]): Optional. The items." in attrs_block
        assert "                |sequenceclassargs|" in attrs_block
        assert "|tupleclassattrs|" not in "\n".join(attrs_block)
        assert "|alwaystuple|" not in "\n".join(attrs_block)

    def test_no_args_section_slot_warns(self, inserter):
        """No Args section but class has undocumented public slot -> warning."""

        class _MyClass:
            __slots__ = ("computed",)

        lines = ["Just a description."]
        with pytest.warns(UserWarning, match="public slot 'computed'"):
            inserter.insert_attributes(_MyClass, lines)
        # Lines unchanged (no args to generate from)
        assert "Attributes:" not in lines

    def test_modifies_lines_in_place(self, inserter):
        """insert_attributes must modify the *same* list object, not replace it."""
        lines = ["Args:", "    x (:obj:`str`): X."]
        original_id = id(lines)
        inserter.insert_attributes(object, lines)
        assert id(lines) == original_id

    def test_no_args_entries_is_noop(self, inserter):
        """An Args section with no parsable entries leaves lines unchanged."""
        lines = [
            "Args:",
            "        Some non-entry text.",
        ]
        original = list(lines)
        inserter.insert_attributes(object, lines)
        assert lines == original
