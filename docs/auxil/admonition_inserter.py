#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2025
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
import contextlib
import inspect
import re
import typing
from collections import defaultdict
from collections.abc import Iterator
from socket import socket
from types import FunctionType
from typing import Union

from apscheduler.job import Job as APSJob

import telegram
import telegram._utils.defaultvalue
import telegram._utils.types
import telegram.ext
import telegram.ext._utils.types
from tests.auxil.slots import mro_slots

# Define the namespace for type resolution. This helps dealing with the internal imports that
# we do in many places
# The .copy() is important to avoid modifying the original namespace
TG_NAMESPACE = vars(telegram).copy()
TG_NAMESPACE.update(vars(telegram._utils.types))
TG_NAMESPACE.update(vars(telegram._utils.defaultvalue))
TG_NAMESPACE.update(vars(telegram.ext))
TG_NAMESPACE.update(vars(telegram.ext._utils.types))
TG_NAMESPACE.update(vars(telegram.ext._applicationbuilder))
TG_NAMESPACE.update({"socket": socket, "APSJob": APSJob})


class PublicMethod(typing.NamedTuple):
    name: str
    method: FunctionType


def _is_inherited_method(cls: type, method_name: str) -> bool:
    """Checks if a method is inherited from a parent class.
    Inheritance is not considered if the parent class is private.
    Recurses through all direcot or indirect parent classes.
    """
    # The [1:] slice is used to exclude the class itself from the MRO.
    for base in cls.__mro__[1:]:
        if method_name in base.__dict__ and not base.__name__.startswith("_"):
            return True
    return False


def _iter_own_public_methods(cls: type) -> Iterator[PublicMethod]:
    """Iterates over methods of a class that are not protected/private,
    not camelCase and not inherited from the parent class.

    Returns pairs of method names and methods.

    This function is defined outside the class because it is used to create class constants.
    """

    # Use .isfunction() instead of .ismethod() because we want to include static methods.
    for m in inspect.getmembers(cls, predicate=inspect.isfunction):
        if (
            not m[0].startswith("_")
            and m[0].islower()  # to avoid camelCase methods
            and not _is_inherited_method(cls, m[0])
        ):
            yield PublicMethod(m[0], m[1])


class AdmonitionInserter:
    """Class for inserting admonitions into docs of Telegram classes."""

    CLASS_ADMONITION_TYPES = ("use_in", "available_in", "returned_in")
    METHOD_ADMONITION_TYPES = ("shortcuts",)
    ALL_ADMONITION_TYPES = CLASS_ADMONITION_TYPES + METHOD_ADMONITION_TYPES

    FORWARD_REF_PATTERN = re.compile(r"^ForwardRef\('(?P<class_name>\w+)'\)$")
    """ A pattern to find a class name in a ForwardRef typing annotation.
    Class name (in a named group) is surrounded by parentheses and single quotes.
    Note that since we're analyzing argument by argument, the pattern can be strict, with
    start and end markers.
    """

    METHOD_NAMES_FOR_BOT_APP_APPBUILDER: typing.ClassVar[dict[type, str]] = {
        cls: tuple(m.name for m in _iter_own_public_methods(cls))
        for cls in (telegram.Bot, telegram.ext.ApplicationBuilder, telegram.ext.Application)
    }
    """A dictionary mapping Bot, Application & ApplicationBuilder classes to their relevant methods
    that will
    be mentioned in 'Returned in' and 'Use in' admonitions in other classes' docstrings.
    Methods must be public, not aliases, not inherited from TelegramObject.
    """

    def __init__(self):
        self.admonitions: dict[str, dict[Union[type, collections.abc.Callable], str]] = {
            # dynamically determine which method to use to create a sub-dictionary
            admonition_type: getattr(self, f"_create_{admonition_type}")()
            for admonition_type in self.ALL_ADMONITION_TYPES
        }
        """Dictionary with admonitions. Contains sub-dictionaries, one per admonition type.
        Each sub-dictionary matches bot methods (for "Shortcuts") or telegram classes (for other
        admonition types) to texts of admonitions, e.g.:

        ```
        {
            "use_in": {
                <class 'telegram._chatinvitelink.ChatInviteLink'>:
                    <"Use in" admonition for ChatInviteLink>,
                ...
            },
            "available_in": {
                <class 'telegram._chatinvitelink.ChatInviteLink'>:
                    <"Available in" admonition">,
                ...
            },
            "returned_in": {...}
        }
        ```
        """

    def insert_admonitions(
        self,
        obj: Union[type, collections.abc.Callable],
        docstring_lines: list[str],
    ):
        """Inserts admonitions into docstring lines for a given class or method.

        **Modifies lines in place**.
        """
        # A better way would be to copy the lines and return them, but that will not work with
        # docs.auxil.sphinx_hooks.autodoc_process_docstring()

        for admonition_type in self.ALL_ADMONITION_TYPES:
            # If there is no admonition of the given type for the given class or method,
            # continue to the next admonition type, maybe the class/method is listed there.
            if obj not in self.admonitions[admonition_type]:
                continue

            insert_idx = self._find_insert_pos_for_admonition(docstring_lines)
            admonition_lines = self.admonitions[admonition_type][obj].splitlines()

            for idx in range(insert_idx, insert_idx + len(admonition_lines)):
                docstring_lines.insert(idx, admonition_lines[idx - insert_idx])

    def _create_available_in(self) -> dict[type, str]:
        """Creates a dictionary with 'Available in' admonitions for classes that are available
        in attributes of other classes.
        """

        # Generate a mapping of classes to ReST links to attributes in other classes that
        # correspond to instances of a given class
        # i.e. {telegram._files.sticker.Sticker: {":attr:`telegram.Message.sticker`", ...}}
        attrs_for_class = defaultdict(set)

        classes_to_inspect = inspect.getmembers(telegram, inspect.isclass) + inspect.getmembers(
            telegram.ext, inspect.isclass
        )

        for _class_name, inspected_class in classes_to_inspect:
            # We need to make "<class 'telegram._files.sticker.StickerSet'>" into
            # "telegram.StickerSet" because that's the way the classes are mentioned in
            # docstrings.
            name_of_inspected_class_in_docstr = self._generate_class_name_for_link(inspected_class)

            # Writing to dictionary: matching the class found in the type hint
            # and its subclasses to the attribute of the class being inspected.
            # The class in the attribute typehint (or its subclass) is the key,
            # ReST link to attribute of the class currently being inspected is the value.

            # best effort - args of __init__ means not all attributes are covered, but there is no
            # other way to get type hints of all attributes, other than doing ast parsing maybe.
            # (Docstring parsing was discontinued with the closing of #4414)
            type_hints = typing.get_type_hints(inspected_class.__init__, localns=TG_NAMESPACE)
            class_attrs = [slot for slot in mro_slots(inspected_class) if not slot.startswith("_")]
            for target_attr in class_attrs:
                try:
                    self._resolve_arg_and_add_link(
                        dict_of_methods_for_class=attrs_for_class,
                        link=f":attr:`{name_of_inspected_class_in_docstr}.{target_attr}`",
                        type_hints={target_attr: type_hints.get(target_attr)},
                        resolve_nested_type_vars=False,
                    )
                except NotImplementedError as e:
                    raise NotImplementedError(
                        "Error generating Sphinx 'Available in' admonition "
                        f"(admonition_inserter.py). Class {inspected_class} present in "
                        f"attribute {target_attr} of class {name_of_inspected_class_in_docstr}"
                        f" could not be resolved. {e!s}"
                    ) from e

            # Properties need to be parsed separately because they act like attributes but not
            # listed as attributes.
            properties = inspect.getmembers(inspected_class, lambda o: isinstance(o, property))
            for prop_name, _ in properties:
                # Make sure this property is really defined in the class being inspected.
                # A property can be inherited from a parent class, then a link to it will not work.
                if prop_name not in inspected_class.__dict__:
                    continue

                # fget is used to access the actual function under the property wrapper
                type_hints = typing.get_type_hints(
                    getattr(inspected_class, prop_name).fget, localns=TG_NAMESPACE
                )

                # Writing to dictionary: matching the class found in the docstring and its
                # subclasses to the property of the class being inspected.
                # The class in the property docstring (or its subclass) is the key,
                # ReST link to property of the class currently being inspected is the value.
                try:
                    self._resolve_arg_and_add_link(
                        dict_of_methods_for_class=attrs_for_class,
                        link=f":attr:`{name_of_inspected_class_in_docstr}.{prop_name}`",
                        type_hints={prop_name: type_hints.get("return")},
                        resolve_nested_type_vars=False,
                    )
                except NotImplementedError as e:
                    raise NotImplementedError(
                        "Error generating Sphinx 'Available in' admonition "
                        f"(admonition_inserter.py). Class {inspected_class} present in "
                        f"property {prop_name} of class {name_of_inspected_class_in_docstr}"
                        f" could not be resolved. {e!s}"
                    ) from e

        return self._generate_admonitions(attrs_for_class, admonition_type="available_in")

    def _create_returned_in(self) -> dict[type, str]:
        """Creates a dictionary with 'Returned in' admonitions for classes that are returned
        in Bot's and ApplicationBuilder's methods.
        """
        # Generate a mapping of classes to ReST links to Bot methods which return it,
        # i.e. {<class 'telegram._message.Message'>: {:meth:`telegram.Bot.send_message`, ...}}
        methods_for_class = defaultdict(set)

        for cls, method_names in self.METHOD_NAMES_FOR_BOT_APP_APPBUILDER.items():
            for method_name in method_names:
                method_link = self._generate_link_to_method(method_name, cls)
                arg = getattr(cls, method_name)
                ret_type_hint = typing.get_type_hints(arg, localns=TG_NAMESPACE)

                try:
                    self._resolve_arg_and_add_link(
                        dict_of_methods_for_class=methods_for_class,
                        link=method_link,
                        type_hints={"return": ret_type_hint.get("return")},
                        resolve_nested_type_vars=False,
                    )
                except NotImplementedError as e:
                    raise NotImplementedError(
                        "Error generating Sphinx 'Returned in' admonition "
                        f"(admonition_inserter.py). {cls}, method {method_name}. "
                        f"Couldn't resolve type hint in return annotation {ret_type_hint}. {e!s}"
                    ) from e

        return self._generate_admonitions(methods_for_class, admonition_type="returned_in")

    def _create_shortcuts(self) -> dict[collections.abc.Callable, str]:
        """Creates a dictionary with 'Shortcuts' admonitions for Bot methods that
        have shortcuts in other classes.
        """

        # pattern for looking for calls to Bot methods only
        bot_method_pattern = re.compile(
            r"""\s*  # any number of whitespaces
            (?<=return\sawait\sself\.get_bot\(\)\.)  # lookbehind
            \w+  # the method name we are looking for, letters/underscores
            (?=\() # lookahead: opening bracket before the args of the method start
            """,
            re.VERBOSE,
        )

        # Generate a mapping of methods of classes to links to Bot methods which they are shortcuts
        # for, i.e. {<function Bot.send_voice at ...>: {:meth:`telegram.User.send_voice`, ...}
        shortcuts_for_bot_method = defaultdict(set)

        # inspect methods of all telegram classes for return statements that indicate
        # that this given method is a shortcut for a Bot method
        for _class_name, cls in inspect.getmembers(telegram, predicate=inspect.isclass):
            if not cls.__module__.startswith("telegram"):
                # For some reason inspect.getmembers() also yields some classes that are
                # imported in the namespace but not part of the telegram module.
                continue

            if cls is telegram.Bot:
                # no need to inspect Bot's own methods, as Bot can't have shortcuts in Bot
                continue

            for method_name, method in _iter_own_public_methods(cls):
                # .getsourcelines() returns a tuple. Item [1] is an int
                for line in inspect.getsourcelines(method)[0]:
                    if not (bot_method_match := bot_method_pattern.search(line)):
                        continue

                    bot_method = getattr(telegram.Bot, bot_method_match.group())
                    link_to_shortcut_method = self._generate_link_to_method(method_name, cls)
                    shortcuts_for_bot_method[bot_method].add(link_to_shortcut_method)

        return self._generate_admonitions(shortcuts_for_bot_method, admonition_type="shortcuts")

    def _create_use_in(self) -> dict[type, str]:
        """Creates a dictionary with 'Use in' admonitions for classes whose instances are
        accepted as arguments for Bot's and ApplicationBuilder's methods.
        """

        # Generate a mapping of classes to links to Bot methods which accept them as arguments,
        # i.e. {<class 'telegram._inline.inlinequeryresult.InlineQueryResult'>:
        # {:meth:`telegram.Bot.answer_inline_query`, ...}}
        methods_for_class = defaultdict(set)

        for cls, method_names in self.METHOD_NAMES_FOR_BOT_APP_APPBUILDER.items():
            for method_name in method_names:
                method_link = self._generate_link_to_method(method_name, cls)

                arg = getattr(cls, method_name)
                param_type_hints = typing.get_type_hints(arg, localns=TG_NAMESPACE)
                param_type_hints.pop("return", None)
                try:
                    self._resolve_arg_and_add_link(
                        dict_of_methods_for_class=methods_for_class,
                        link=method_link,
                        type_hints=param_type_hints,
                    )
                except NotImplementedError as e:
                    raise NotImplementedError(
                        "Error generating Sphinx 'Use in' admonition "
                        f"(admonition_inserter.py). {cls}, method {method_name}, parameter "
                    ) from e

        return self._generate_admonitions(methods_for_class, admonition_type="use_in")

    @staticmethod
    def _find_insert_pos_for_admonition(lines: list[str]) -> int:
        """Finds the correct position to insert the class admonition and returns the index.

        The admonition will be insert above "See also", "Examples:", version added/changed notes
        and args, whatever comes first.

        If no key phrases are found, the admonition will be inserted at the very end.
        """
        for idx, value in list(enumerate(lines)):
            if value.startswith(
                (
                    # ".. seealso:",
                    # The docstring contains heading "Examples:", but Sphinx will have it converted
                    # to ".. admonition: Examples":
                    ".. admonition:: Examples",
                    ".. version",
                    "Args:",
                    # The space after ":param" is important because docstring can contain
                    # ":paramref:" in its plain text in the beginning of a line (e.g. ExtBot):
                    ":param ",
                    # some classes (like "Credentials") have no params, so insert before attrs:
                    ".. attribute::",
                )
            ):
                return idx
        return len(lines) - 1

    def _generate_admonitions(
        self,
        attrs_or_methods_for_class: dict[type, set[str]],
        admonition_type: str,
    ) -> dict[type, str]:
        """Generates admonitions of a given type.
        Takes a dictionary of classes matched to ReST links to methods or attributes, e.g.:

        ```
        {<class 'telegram._files.sticker.StickerSet'>:
        [":meth: `telegram.Bot.get_sticker_set`", ...]}.
        ```

        Returns a dictionary of classes matched to full admonitions, e.g.
        for `admonition_type` "returned_in" (note that title and CSS class are generated
        automatically):

        ```
        {<class 'telegram._files.sticker.StickerSet'>:
        ".. admonition:: Returned in:
            :class: returned-in

            :meth: `telegram.Bot.get_sticker_set`"}.
        ```
        """

        if admonition_type not in self.ALL_ADMONITION_TYPES:
            raise TypeError(f"Admonition type {admonition_type} not supported.")

        admonition_for_class = {}

        for cls, attrs in attrs_or_methods_for_class.items():
            if cls is telegram.ext.ApplicationBuilder:
                # ApplicationBuilder is only used in and returned from its own methods,
                # so its page needs no admonitions.
                continue

            sorted_attrs = sorted(attrs)

            # e.g. for admonition type "use_in" the title will be "Use in" and CSS class "use-in".
            admonition = f"""

.. admonition:: {admonition_type.title().replace("_", " ")}
    :class: {admonition_type.replace("_", "-")}
    """
            if len(sorted_attrs) > 1:
                for target_attr in sorted_attrs:
                    admonition += "\n    * " + target_attr
            else:
                admonition += f"\n    {sorted_attrs[0]}"

            admonition += "\n    "  # otherwise an unexpected unindent warning will be issued
            admonition_for_class[cls] = admonition

        return admonition_for_class

    @staticmethod
    def _generate_class_name_for_link(cls_: type) -> str:
        """Generates class name that can be used in a ReST link."""

        # Check for potential presence of ".ext.", we will need to keep it.
        ext = ".ext" if ".ext." in str(cls_) else ""
        return f"telegram{ext}.{cls_.__name__}"

    def _generate_link_to_method(self, method_name: str, cls: type) -> str:
        """Generates a ReST link to a method of a telegram class."""

        return f":meth:`{self._generate_class_name_for_link(cls)}.{method_name}`"

    @staticmethod
    def _iter_subclasses(cls_: type) -> Iterator:
        if not hasattr(cls_, "__subclasses__") or cls_ is telegram.TelegramObject:
            return iter([])
        return (
            # exclude private classes
            c
            for c in cls_.__subclasses__()
            if not str(c).split(".")[-1].startswith("_")
        )

    def _resolve_arg_and_add_link(
        self,
        dict_of_methods_for_class: defaultdict,
        link: str,
        type_hints: dict[str, type],
        resolve_nested_type_vars: bool = True,
    ) -> None:
        """A helper method. Tries to resolve the arg into a valid class. In case of success,
        adds the link (to a method, attribute, or property) for that class' and its subclasses'
        sets of links in the dictionary of admonitions.

        **Modifies dictionary in place.**
        """
        type_hints.pop("self", None)

        for cls in self._resolve_arg(type_hints, resolve_nested_type_vars):
            # When trying to resolve an argument from args or return annotation,
            # the method _resolve_arg returns None if nothing could be resolved.
            # Also, if class was resolved correctly, "telegram" will definitely be in its str().
            if cls is None or "telegram" not in str(cls):
                continue

            dict_of_methods_for_class[cls].add(link)

            for subclass in self._iter_subclasses(cls):
                dict_of_methods_for_class[subclass].add(link)

    def _resolve_arg(
        self,
        type_hints: dict[str, type],
        resolve_nested_type_vars: bool,
    ) -> list[type]:
        """Analyzes an argument of a method and recursively yields classes that the argument
        or its sub-arguments (in cases like Union[...]) belong to, if they can be resolved to
        telegram or telegram.ext classes.

        Args:
            type_hints: A dictionary of argument names and their types.
            resolve_nested_type_vars: If True, nested type variables (like Application[BT, …])
                will be resolved to their actual classes. If False, only the outermost type
                variable will be resolved. *Only* affects ptb classes, not built-in types.
                Useful for checking the return type of methods, where nested type variables
                are not really useful.

        Raises `NotImplementedError`.
        """

        def _is_ptb_class(cls: type) -> bool:
            if not hasattr(cls, "__module__"):
                return False
            return cls.__module__.startswith("telegram")

        # will be edited in place
        telegram_classes = set()

        def recurse_type(type_, is_recursed_from_ptb_class: bool):
            next_is_recursed_from_ptb_class = is_recursed_from_ptb_class or _is_ptb_class(type_)

            if hasattr(type_, "__origin__"):  # For generic types like Union, List, etc.
                # Make sure it's not a telegram.ext generic type (e.g. ContextTypes[...])
                org = typing.get_origin(type_)
                if "telegram.ext" in str(org):
                    telegram_classes.add(org)

                args = typing.get_args(type_)
                for arg in args:
                    recurse_type(arg, next_is_recursed_from_ptb_class)
            elif isinstance(type_, typing.TypeVar) and (
                resolve_nested_type_vars or not is_recursed_from_ptb_class
            ):
                # gets access to the "bound=..." parameter
                recurse_type(type_.__bound__, next_is_recursed_from_ptb_class)
            elif inspect.isclass(type_) and "telegram" in inspect.getmodule(type_).__name__:
                telegram_classes.add(type_)
            elif isinstance(type_, typing.ForwardRef):
                # Resolving ForwardRef is not easy. https://peps.python.org/pep-0749/ will
                # hopefully make it better by introducing typing.resolve_forward_ref() in py3.14
                # but that's not there yet
                # So for now we fall back to a best effort approach of guessing if the class is
                # available in tg or tg.ext
                with contextlib.suppress(AttributeError):
                    telegram_classes.add(self._resolve_class(type_.__forward_arg__))

        for type_hint in type_hints.values():
            if type_hint is not None:
                recurse_type(type_hint, False)

        return list(telegram_classes)

    @staticmethod
    def _resolve_class(name: str) -> Union[type, None]:
        """The keys in the admonitions dictionary are not strings like "telegram.StickerSet"
        but classes like <class 'telegram._files.sticker.StickerSet'>.

        This method attempts to resolve a PTB class from a name that does or does not
        contain the word 'telegram', e.g.
        <class 'telegram._files.sticker.StickerSet'> from "telegram.StickerSet" or "StickerSet".

        Returns a class on success, :obj:`None` if nothing could be resolved.
        """

        for option in (
            name,
            f"telegram.{name}",
            f"telegram.ext.{name}",
            f"telegram.ext.filters.{name}",
        ):
            # NameError will be raised if trying to eval just name and it doesn't work, e.g.
            # "Name 'ApplicationBuilder' is not defined".
            # AttributeError will be raised if trying to e.g. eval f"telegram.{name}" when the
            # class denoted by `name` actually belongs to `telegram.ext`:
            # "module 'telegram' has no attribute 'ApplicationBuilder'".
            # If neither option works, this is not a PTB class.
            with contextlib.suppress(NameError, AttributeError):
                return eval(option)
        return None


if __name__ == "__main__":
    # just try instantiating for debugging purposes
    AdmonitionInserter()
