#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2023
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
import collections.abc
import inspect
import re
import typing
from pathlib import Path

from sphinx.application import Sphinx

import telegram
import telegram.ext
from docs.auxil.admonition_inserter import AdmonitionInserter
from docs.auxil.kwargs_insertion import (
    check_timeout_and_api_kwargs_presence,
    find_insert_pos_for_kwargs,
    is_write_timeout_20,
    keyword_args,
    read_timeout_sub,
    read_timeout_type,
    write_timeout_sub,
)
from docs.auxil.link_code import LINE_NUMBERS

ADMONITION_INSERTER = AdmonitionInserter()

# Some base classes are implementation detail
# We want to instead show *their* base class
PRIVATE_BASE_CLASSES = {
    "_ChatUserBaseFilter": "MessageFilter",
    "_Dice": "MessageFilter",
    "_BaseThumbedMedium": "TelegramObject",
    "_BaseMedium": "TelegramObject",
    "_CredentialsBase": "TelegramObject",
}


FILE_ROOT = Path(inspect.getsourcefile(telegram)).parent.parent.resolve()


def autodoc_skip_member(app, what, name, obj, skip, options):
    """We use this to not document certain members like filter() or check_update() for filters.
    See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#skipping-members"""

    included = {"MessageFilter", "UpdateFilter"}  # filter() and check_update() only for these.
    included_in_obj = any(inc in repr(obj) for inc in included)

    if included_in_obj:  # it's difficult to see if check_update is from an inherited-member or not
        for frame in inspect.stack():  # From https://github.com/sphinx-doc/sphinx/issues/9533
            if frame.function == "filter_members":
                docobj = frame.frame.f_locals["self"].object
                if not any(inc in str(docobj) for inc in included) and name == "check_update":
                    return True
                break

    if name == "filter" and obj.__module__ == "telegram.ext.filters":
        if not included_in_obj:
            return True  # return True to exclude from docs.


def autodoc_process_docstring(
    app: Sphinx, what, name: str, obj: object, options, lines: list[str]
):
    """We do the following things:
    1) Use this method to automatically insert the Keyword Args and "Shortcuts" admonitions
       for the Bot methods.

    2) Use this method to automatically insert "Returned in" admonition into classes
       that are returned from the Bot methods

    3) Use this method to automatically insert "Available in" admonition into classes
       whose instances are available as attributes of other classes

    4) Use this method to automatically insert "Use in" admonition into classes
       whose instances can be used as arguments of the Bot methods

    5) Misuse this autodoc hook to get the file names & line numbers because we have access
       to the actual object here.
    """

    # 1) Insert the Keyword Args and "Shortcuts" admonitions for the Bot methods
    method_name = name.split(".")[-1]
    if (
        name.startswith("telegram.Bot.")
        and what == "method"
        and method_name.islower()
        and check_timeout_and_api_kwargs_presence(obj)
    ):
        insert_index = find_insert_pos_for_kwargs(lines)
        if not insert_index:
            raise ValueError(
                f"Couldn't find the correct position to insert the keyword args for {obj}."
            )

        long_write_timeout = is_write_timeout_20(obj)
        get_updates_sub = 1 if (method_name == "get_updates") else 0
        # The below can be done in 1 line with itertools.chain, but this must be modified in-place
        for i in range(insert_index, insert_index + len(keyword_args)):
            lines.insert(
                i,
                keyword_args[i - insert_index].format(
                    method=method_name,
                    write_timeout=write_timeout_sub[long_write_timeout],
                    read_timeout=read_timeout_sub[get_updates_sub],
                    read_timeout_type=read_timeout_type[get_updates_sub],
                ),
            )

        ADMONITION_INSERTER.insert_admonitions(
            obj=typing.cast(collections.abc.Callable, obj),
            docstring_lines=lines,
        )

    # 2-4) Insert "Returned in", "Available in", "Use in" admonitions into classes
    # (where applicable)
    if what == "class":
        ADMONITION_INSERTER.insert_admonitions(
            obj=typing.cast(type, obj),  # since "what" == class, we know it's not just object
            docstring_lines=lines,
        )

    # 5) Get the file names & line numbers
    # We can't properly handle ordinary attributes.
    # In linkcode_resolve we'll resolve to the `__init__` or module instead
    if what == "attribute":
        return

    # Special casing for properties
    if hasattr(obj, "fget"):
        obj = obj.fget

    # Special casing for filters
    if isinstance(obj, telegram.ext.filters.BaseFilter):
        obj = obj.__class__

    try:
        source_lines, start_line = inspect.getsourcelines(obj)
        end_line = start_line + len(source_lines)
        file = Path(inspect.getsourcefile(obj)).relative_to(FILE_ROOT)
        LINE_NUMBERS[name] = (file, start_line, end_line)
    except Exception:
        pass

    # Since we don't document the `__init__`, we call this manually to have it available for
    # attributes -- see the note above
    if what == "class":
        autodoc_process_docstring(app, "method", f"{name}.__init__", obj.__init__, options, lines)


def autodoc_process_bases(app, name, obj, option, bases: list):
    """Here we fine tune how the base class's classes are displayed."""
    for idx, base in enumerate(bases):
        # let's use a string representation of the object
        base = str(base)

        # Special case for abstract context managers which are wrongly resoled for some reason
        if base.startswith("typing.AbstractAsyncContextManager"):
            bases[idx] = ":class:`contextlib.AbstractAsyncContextManager`"
            continue

        # Special case because base classes are in std lib:
        if "StringEnum" in base == "<enum 'StringEnum'>":
            bases[idx] = ":class:`enum.Enum`"
            bases.insert(0, ":class:`str`")
            continue

        if "IntEnum" in base:
            bases[idx] = ":class:`enum.IntEnum`"
            continue

        # Drop generics (at least for now)
        if base.endswith("]"):
            base = base.split("[", maxsplit=1)[0]
            bases[idx] = f":class:`{base}`"

        # Now convert `telegram._message.Message` to `telegram.Message` etc
        match = re.search(pattern=r"(telegram(\.ext|))\.[_\w\.]+", string=base)
        if not match or "_utils" in base:
            continue

        parts = match.group(0).split(".")

        # Remove private paths
        for index, part in enumerate(parts):
            if part.startswith("_"):
                parts = parts[:index] + parts[-1:]
                break

        # Replace private base classes with their respective parent
        parts = [PRIVATE_BASE_CLASSES.get(part, part) for part in parts]

        base = ".".join(parts)

        bases[idx] = f":class:`{base}`"
