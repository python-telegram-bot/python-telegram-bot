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
import re
from pathlib import Path

telegram_root = Path(__file__).parent.parent / "telegram"
telegram_ext_root = telegram_root / "ext"
exclude_dirs = {
    # We touch passport stuff only if strictly necessary.
    telegram_root
    / "_passport",
}

exclude_patterns = {re.compile(re.escape("self.type: ReactionType = type"))}


def test_types_are_converted_to_enum():
    """We want to convert all attributes of name "type" to an enum from telegram.constants.
    Since we don't necessarily document this as type hint, we simply check this with a regex.
    """
    pattern = re.compile(r"self\.type: [^=]+ = ([^\n]+)\n", re.MULTILINE)

    for path in telegram_root.rglob("*.py"):
        if telegram_ext_root in path.parents or any(
            exclude_dir in path.parents for exclude_dir in exclude_dirs
        ):
            # We don't check tg.ext.
            continue

        text = path.read_text(encoding="utf-8")
        for match in re.finditer(pattern, text):
            if any(exclude_pattern.match(match.group(0)) for exclude_pattern in exclude_patterns):
                continue

            assert match.group(1).startswith("enum.get_member") or match.group(1).startswith(
                "get_member"
            ), (
                f"`{match.group(1)}` in `{path}` does not seem to convert the type to an enum. "
                f"Please fix this and also make sure to add a separate test to the classes test "
                f"file."
            )
