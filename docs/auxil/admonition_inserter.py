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
from collections import defaultdict
from typing import Any, Iterator, Union

import telegram
import telegram.ext


def _iter_own_public_methods(cls: type) -> Iterator[tuple[str, type]]:
    """Iterates over methods of a class that are not protected/private,
    not camelCase and not inherited from the parent class.

    Returns pairs of method names and methods.

    This function is defined outside the class because it is used to create class constants.
    """
    return (
        m
        for m in inspect.getmembers(cls, predicate=inspect.isfunction)  # not .ismethod
        if not m[0].startswith("_")
        and m[0].islower()  # to avoid camelCase methods
        and m[0] in cls.__dict__  # method is not inherited from parent class
    )


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

    FORWARD_REF_SKIP_PATTERN = re.compile(r"^ForwardRef\('DefaultValue\[\w+]'\)$")
    """A pattern that will be used to skip known ForwardRef's that need not be resolved
    to a Telegram class, e.g.:
    ForwardRef('DefaultValue[None]')
    ForwardRef('DefaultValue[DVValueType]')
    """

    METHOD_NAMES_FOR_BOT_AND_APPBUILDER: dict[type, str] = {
        cls: tuple(m[0] for m in _iter_own_public_methods(cls))  # m[0] means we take only names
        for cls in (telegram.Bot, telegram.ext.ApplicationBuilder)
    }
    """A dictionary mapping Bot and ApplicationBuilder classes to their relevant methods that will
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
        "use_in": {<class 'telegram._chatinvitelink.ChatInviteLink'>:
        <"Use in" admonition for ChatInviteLink>, ...},
        "available_in": {<class 'telegram._chatinvitelink.ChatInviteLink'>:
        <"Available in" admonition">, ...},
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

        # The following regex is supposed to capture a class name in a line like this:
        # media (:obj:`str` | :class:`telegram.InputFile`): Audio file to send.
        #
        # Note that even if such typing description spans over multiple lines but each line ends
        # with a backslash (otherwise Sphinx will throw an error)
        # (e.g. EncryptedPassportElement.data), then Sphinx will combine these lines into a single
        # line automatically, and it will contain no backslash (only some extra many whitespaces
        # from the indentation).

        attr_docstr_pattern = re.compile(
            r"^\s*(?P<attr_name>[a-z_]+)"  # Any number of spaces, named group for attribute
            r"\s?\("  # Optional whitespace, opening parenthesis
            r".*"  # Any number of characters (that could denote a built-in type)
            r":class:`.+`"  # Marker of a classref, class name in backticks
            r".*\):"  # Any number of characters, closing parenthesis, colon.
            # The ^ colon above along with parenthesis is important because it makes sure that
            # the class is mentioned in the attribute description, not in free text.
            r".*$",  # Any number of characters, end of string (end of line)
            re.VERBOSE,
        )

        # for properties: there is no attr name in docstring.  Just check if there's a class name.
        prop_docstring_pattern = re.compile(r":class:`.+`.*:")

        # pattern for iterating over potentially many class names in docstring for one attribute.
        # Tilde is optional (sometimes it is in the docstring, sometimes not).
        single_class_name_pattern = re.compile(r":class:`~?(?P<class_name>[\w.]*)`")

        classes_to_inspect = inspect.getmembers(telegram, inspect.isclass) + inspect.getmembers(
            telegram.ext, inspect.isclass
        )

        for class_name, inspected_class in classes_to_inspect:
            # We need to make "<class 'telegram._files.sticker.StickerSet'>" into
            # "telegram.StickerSet" because that's the way the classes are mentioned in
            # docstrings.
            name_of_inspected_class_in_docstr = self._generate_class_name_for_link(inspected_class)

            # Parsing part of the docstring with attributes (parsing of properties follows later)
            docstring_lines = inspect.getdoc(inspected_class).splitlines()
            lines_with_attrs = []
            for idx, line in enumerate(docstring_lines):
                if line.strip() == "Attributes:":
                    lines_with_attrs = docstring_lines[idx + 1 :]
                    break

            for line in lines_with_attrs:
                line_match = attr_docstr_pattern.match(line)
                if not line_match:
                    continue

                target_attr = line_match.group("attr_name")
                # a typing description of one attribute can contain multiple classes
                for match in single_class_name_pattern.finditer(line):
                    name_of_class_in_attr = match.group("class_name")

                    # Writing to dictionary: matching the class found in the docstring
                    # and its subclasses to the attribute of the class being inspected.
                    # The class in the attribute docstring (or its subclass) is the key,
                    # ReST link to attribute of the class currently being inspected is the value.
                    try:
                        self._resolve_arg_and_add_link(
                            arg=name_of_class_in_attr,
                            dict_of_methods_for_class=attrs_for_class,
                            link=f":attr:`{name_of_inspected_class_in_docstr}.{target_attr}`",
                        )
                    except NotImplementedError as e:
                        raise NotImplementedError(
                            f"Error generating Sphinx 'Available in' admonition "
                            f"(admonition_inserter.py). Class {name_of_class_in_attr} present in "
                            f"attribute {target_attr} of class {name_of_inspected_class_in_docstr}"
                            f" could not be resolved. {str(e)}"
                        )

            # Properties need to be parsed separately because they act like attributes but not
            # listed as attributes.
            properties = inspect.getmembers(inspected_class, lambda o: isinstance(o, property))
            for prop_name, _ in properties:
                # Make sure this property is really defined in the class being inspected.
                # A property can be inherited from a parent class, then a link to it will not work.
                if prop_name not in inspected_class.__dict__:
                    continue

                # 1. Can't use typing.get_type_hints because double-quoted type hints
                #    (like "Application") will throw a NameError
                # 2. Can't use inspect.signature because return annotations of properties can be
                #    hard to parse (like "(self) -> BD").
                # 3. fget is used to access the actual function under the property wrapper
                docstring = inspect.getdoc(getattr(inspected_class, prop_name).fget)
                if docstring is None:
                    continue

                first_line = docstring.splitlines()[0]
                if not prop_docstring_pattern.match(first_line):
                    continue

                for match in single_class_name_pattern.finditer(first_line):
                    name_of_class_in_prop = match.group("class_name")

                    # Writing to dictionary: matching the class found in the docstring and its
                    # subclasses to the property of the class being inspected.
                    # The class in the property docstring (or its subclass) is the key,
                    # ReST link to property of the class currently being inspected is the value.
                    try:
                        self._resolve_arg_and_add_link(
                            arg=name_of_class_in_prop,
                            dict_of_methods_for_class=attrs_for_class,
                            link=f":attr:`{name_of_inspected_class_in_docstr}.{prop_name}`",
                        )
                    except NotImplementedError as e:
                        raise NotImplementedError(
                            f"Error generating Sphinx 'Available in' admonition "
                            f"(admonition_inserter.py). Class {name_of_class_in_prop} present in "
                            f"property {prop_name} of class {name_of_inspected_class_in_docstr}"
                            f" could not be resolved. {str(e)}"
                        )

        return self._generate_admonitions(attrs_for_class, admonition_type="available_in")

    def _create_returned_in(self) -> dict[type, str]:
        """Creates a dictionary with 'Returned in' admonitions for classes that are returned
        in Bot's and ApplicationBuilder's methods.
        """

        # Generate a mapping of classes to ReST links to Bot methods which return it,
        # i.e. {<class 'telegram._message.Message'>: {:meth:`telegram.Bot.send_message`, ...}}
        methods_for_class = defaultdict(set)

        for cls, method_names in self.METHOD_NAMES_FOR_BOT_AND_APPBUILDER.items():
            for method_name in method_names:
                sig = inspect.signature(getattr(cls, method_name))
                ret_annot = sig.return_annotation

                method_link = self._generate_link_to_method(method_name, cls)

                try:
                    self._resolve_arg_and_add_link(
                        arg=ret_annot,
                        dict_of_methods_for_class=methods_for_class,
                        link=method_link,
                    )
                except NotImplementedError as e:
                    raise NotImplementedError(
                        f"Error generating Sphinx 'Returned in' admonition "
                        f"(admonition_inserter.py). {cls}, method {method_name}. "
                        f"Couldn't resolve type hint in return annotation {ret_annot}. {str(e)}"
                    )

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
        for class_name, cls in inspect.getmembers(telegram, predicate=inspect.isclass):
            # no need to inspect Bot's own methods, as Bot can't have shortcuts in Bot
            if cls is telegram.Bot:
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

        for cls, method_names in self.METHOD_NAMES_FOR_BOT_AND_APPBUILDER.items():
            for method_name in method_names:
                method_link = self._generate_link_to_method(method_name, cls)

                sig = inspect.signature(getattr(cls, method_name))
                parameters = sig.parameters

                for param in parameters.values():
                    try:
                        self._resolve_arg_and_add_link(
                            arg=param.annotation,
                            dict_of_methods_for_class=methods_for_class,
                            link=method_link,
                        )
                    except NotImplementedError as e:
                        raise NotImplementedError(
                            f"Error generating Sphinx 'Use in' admonition "
                            f"(admonition_inserter.py). {cls}, method {method_name}, parameter "
                            f"{param}: Couldn't resolve type hint {param.annotation}. {str(e)}"
                        )

        return self._generate_admonitions(methods_for_class, admonition_type="use_in")

    @staticmethod
    def _find_insert_pos_for_admonition(lines: list[str]) -> int:
        """Finds the correct position to insert the class admonition and returns the index.

        The admonition will be insert above "See also", "Examples:", version added/changed notes
        and args, whatever comes first.

        If no key phrases are found, the admonition will be inserted at the very end.
        """
        for idx, value in list(enumerate(lines)):
            if (
                value.startswith(".. seealso:")
                # The docstring contains heading "Examples:", but Sphinx will have it converted
                # to ".. admonition: Examples":
                or value.startswith(".. admonition:: Examples")
                or value.startswith(".. version")
                # The space after ":param" is important because docstring can contain ":paramref:"
                # in its plain text in the beginning of a line (e.g. ExtBot):
                or value.startswith(":param ")
                # some classes (like "Credentials") have no params, so insert before attrs:
                or value.startswith(".. attribute::")
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

            attrs = sorted(attrs)

            # e.g. for admonition type "use_in" the title will be "Use in" and CSS class "use-in".
            admonition = f"""

.. admonition:: {admonition_type.title().replace("_", " ")}
    :class: {admonition_type.replace("_", "-")}
    """
            if len(attrs) > 1:
                for target_attr in attrs:
                    admonition += "\n    * " + target_attr
            else:
                admonition += f"\n    {attrs[0]}"

            admonition += "\n    "  # otherwise an unexpected unindent warning will be issued
            admonition_for_class[cls] = admonition

        return admonition_for_class

    @staticmethod
    def _generate_class_name_for_link(cls: type) -> str:
        """Generates class name that can be used in a ReST link."""

        # Check for potential presence of ".ext.", we will need to keep it.
        ext = ".ext" if ".ext." in str(cls) else ""
        return f"telegram{ext}.{cls.__name__}"

    def _generate_link_to_method(self, method_name: str, cls: type) -> str:
        """Generates a ReST link to a method of a telegram class."""

        return f":meth:`{self._generate_class_name_for_link(cls)}.{method_name}`"

    @staticmethod
    def _iter_subclasses(cls: type) -> Iterator:
        return (
            # exclude private classes
            c
            for c in cls.__subclasses__()
            if not str(c).split(".")[-1].startswith("_")
        )

    def _resolve_arg_and_add_link(
        self,
        arg: Any,
        dict_of_methods_for_class: defaultdict,
        link: str,
    ) -> None:
        """A helper method. Tries to resolve the arg into a valid class. In case of success,
        adds the link (to a method, attribute, or property) for that class' and its subclasses'
        sets of links in the dictionary of admonitions.

        **Modifies dictionary in place.**
        """
        for cls in self._resolve_arg(arg):
            # When trying to resolve an argument from args or return annotation,
            # the method _resolve_arg returns None if nothing could be resolved.
            # Also, if class was resolved correctly, "telegram" will definitely be in its str().
            if cls is None or "telegram" not in str(cls):
                continue

            dict_of_methods_for_class[cls].add(link)

            for subclass in self._iter_subclasses(cls):
                dict_of_methods_for_class[subclass].add(link)

    def _resolve_arg(self, arg: Any) -> Iterator[Union[type, None]]:
        """Analyzes an argument of a method and recursively yields classes that the argument
        or its sub-arguments (in cases like Union[...]) belong to, if they can be resolved to
        telegram or telegram.ext classes.

        Raises `NotImplementedError`.
        """

        origin = typing.get_origin(arg)

        if (
            origin in (collections.abc.Callable, typing.IO)
            or arg is None
            # no other check available (by type or origin) for these:
            or str(type(arg)) in ("<class 'typing._SpecialForm'>", "<class 'ellipsis'>")
        ):
            pass

        # RECURSIVE CALLS
        # for cases like Union[Sequence....
        elif origin in (
            Union,
            collections.abc.Coroutine,
            collections.abc.Sequence,
        ):
            for sub_arg in typing.get_args(arg):
                yield from self._resolve_arg(sub_arg)

        elif isinstance(arg, typing.TypeVar):
            # gets access to the "bound=..." parameter
            yield from self._resolve_arg(arg.__bound__)
        # END RECURSIVE CALLS

        elif isinstance(arg, typing.ForwardRef):
            m = self.FORWARD_REF_PATTERN.match(str(arg))
            # We're sure it's a ForwardRef, so, unless it belongs to known exceptions,
            # the class must be resolved.
            # If it isn't resolved, we'll have the program throw an exception to be sure.
            try:
                cls = self._resolve_class(m.group("class_name"))
            except AttributeError:
                # skip known ForwardRef's that need not be resolved to a Telegram class
                if self.FORWARD_REF_SKIP_PATTERN.match(str(arg)):
                    pass
                else:
                    raise NotImplementedError(f"Could not process ForwardRef: {arg}")
            else:
                yield cls

        # For custom generics like telegram.ext._application.Application[~BT, ~CCT, ~UD...].
        # This must come before the check for isinstance(type) because GenericAlias can also be
        # recognized as type if it belongs to <class 'types.GenericAlias'>.
        elif str(type(arg)) in ("<class 'typing._GenericAlias'>", "<class 'types.GenericAlias'>"):
            if "telegram" in str(arg):
                # get_origin() of telegram.ext._application.Application[~BT, ~CCT, ~UD...]
                # will produce <class 'telegram.ext._application.Application'>
                yield origin

        elif isinstance(arg, type):
            if "telegram" in str(arg):
                yield arg

        # For some reason "InlineQueryResult", "InputMedia" & some others are currently not
        # recognized as ForwardRefs and are identified as plain strings.
        elif isinstance(arg, str):
            # args like "ApplicationBuilder[BT, CCT, UD, CD, BD, JQ]" can be recognized as strings.
            # Remove whatever is in the square brackets because it doesn't need to be parsed.
            arg = re.sub(r"\[.+]", "", arg)

            cls = self._resolve_class(arg)
            # Here we don't want an exception to be thrown since we're not sure it's ForwardRef
            if cls is not None:
                yield cls

        else:
            raise NotImplementedError(
                f"Cannot process argument {arg} of type {type(arg)} (origin {origin})"
            )

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
            try:
                return eval(option)
            # NameError will be raised if trying to eval just name and it doesn't work, e.g.
            # "Name 'ApplicationBuilder' is not defined".
            # AttributeError will be raised if trying to e.g. eval f"telegram.{name}" when the
            # class denoted by `name` actually belongs to `telegram.ext`:
            # "module 'telegram' has no attribute 'ApplicationBuilder'".
            # If neither option works, this is not a PTB class.
            except (NameError, AttributeError):
                continue


if __name__ == "__main__":
    # just try instantiating for debugging purposes
    AdmonitionInserter()
