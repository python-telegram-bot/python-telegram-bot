#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
# pylint: disable=C0112, C0103, W0221
"""This module contains the Filters for use with the MessageHandler class."""

import re
import warnings

from abc import ABC, abstractmethod
from threading import Lock
from typing import (
    Dict,
    FrozenSet,
    List,
    Match,
    Optional,
    Pattern,
    Set,
    Tuple,
    Union,
    cast,
    NoReturn,
)

from telegram import Chat, Message, MessageEntity, Update, User

__all__ = [
    'Filters',
    'BaseFilter',
    'MessageFilter',
    'UpdateFilter',
    'InvertedFilter',
    'MergedFilter',
    'XORFilter',
]

from telegram.utils.deprecate import TelegramDeprecationWarning
from telegram.utils.types import SLT

DataDict = Dict[str, list]


class BaseFilter(ABC):
    """Base class for all Filters.

    Filters subclassing from this class can combined using bitwise operators:

    And:

        >>> (Filters.text & Filters.entity(MENTION))

    Or:

        >>> (Filters.audio | Filters.video)

    Exclusive Or:

        >>> (Filters.regex('To Be') ^ Filters.regex('Not 2B'))

    Not:

        >>> ~ Filters.command

    Also works with more than two filters:

        >>> (Filters.text & (Filters.entity(URL) | Filters.entity(TEXT_LINK)))
        >>> Filters.text & (~ Filters.forwarded)

    Note:
        Filters use the same short circuiting logic as python's `and`, `or` and `not`.
        This means that for example:

            >>> Filters.regex(r'(a?x)') | Filters.regex(r'(b?x)')

        With ``message.text == x``, will only ever return the matches for the first filter,
        since the second one is never evaluated.


    If you want to create your own filters create a class inheriting from either
    :class:`MessageFilter` or :class:`UpdateFilter` and implement a :meth:`filter` method that
    returns a boolean: :obj:`True` if the message should be
    handled, :obj:`False` otherwise.
    Note that the filters work only as class instances, not
    actual class objects (so remember to
    initialize your filter classes).

    By default the filters name (what will get printed when converted to a string for display)
    will be the class name. If you want to overwrite this assign a better name to the :attr:`name`
    class variable.

    Attributes:
        name (:obj:`str`): Name for this filter. Defaults to the type of filter.
        data_filter (:obj:`bool`): Whether this filter is a data filter. A data filter should
            return a dict with lists. The dict will be merged with
            :class:`telegram.ext.CallbackContext`'s internal dict in most cases
            (depends on the handler).
    """

    _name = None
    data_filter = False

    @abstractmethod
    def __call__(self, update: Update) -> Optional[Union[bool, DataDict]]:
        pass

    def __and__(self, other: 'BaseFilter') -> 'BaseFilter':
        return MergedFilter(self, and_filter=other)

    def __or__(self, other: 'BaseFilter') -> 'BaseFilter':
        return MergedFilter(self, or_filter=other)

    def __xor__(self, other: 'BaseFilter') -> 'BaseFilter':
        return XORFilter(self, other)

    def __invert__(self) -> 'BaseFilter':
        return InvertedFilter(self)

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, name: Optional[str]) -> None:
        self._name = name

    def __repr__(self) -> str:
        # We do this here instead of in a __init__ so filter don't have to call __init__ or super()
        if self.name is None:
            self.name = self.__class__.__name__
        return self.name


class MessageFilter(BaseFilter, ABC):
    """Base class for all Message Filters. In contrast to :class:`UpdateFilter`, the object passed
    to :meth:`filter` is ``update.effective_message``.

    Please see :class:`telegram.ext.filters.BaseFilter` for details on how to create custom
    filters.

    Attributes:
        name (:obj:`str`): Name for this filter. Defaults to the type of filter.
        data_filter (:obj:`bool`): Whether this filter is a data filter. A data filter should
            return a dict with lists. The dict will be merged with
            :class:`telegram.ext.CallbackContext`'s internal dict in most cases
            (depends on the handler).

    """

    def __call__(self, update: Update) -> Optional[Union[bool, DataDict]]:
        return self.filter(update.effective_message)

    @abstractmethod
    def filter(self, message: Message) -> Optional[Union[bool, DataDict]]:
        """This method must be overwritten.

        Args:
            message (:class:`telegram.Message`): The message that is tested.

        Returns:
            :obj:`dict` or :obj:`bool`

        """


class UpdateFilter(BaseFilter, ABC):
    """Base class for all Update Filters. In contrast to :class:`MessageFilter`, the object
    passed to :meth:`filter` is ``update``, which allows to create filters like
    :attr:`Filters.update.edited_message`.

    Please see :class:`telegram.ext.filters.BaseFilter` for details on how to create custom
    filters.

    Attributes:
        name (:obj:`str`): Name for this filter. Defaults to the type of filter.
        data_filter (:obj:`bool`): Whether this filter is a data filter. A data filter should
            return a dict with lists. The dict will be merged with
            :class:`telegram.ext.CallbackContext`'s internal dict in most cases
            (depends on the handler).

    """

    def __call__(self, update: Update) -> Optional[Union[bool, DataDict]]:
        return self.filter(update)

    @abstractmethod
    def filter(self, update: Update) -> Optional[Union[bool, DataDict]]:
        """This method must be overwritten.

        Args:
            update (:class:`telegram.Update`): The update that is tested.

        Returns:
            :obj:`dict` or :obj:`bool`.

        """


class InvertedFilter(UpdateFilter):
    """Represents a filter that has been inverted.

    Args:
        f: The filter to invert.

    """

    def __init__(self, f: BaseFilter):
        self.f = f

    def filter(self, update: Update) -> bool:
        return not bool(self.f(update))

    @property
    def name(self) -> str:
        return f"<inverted {self.f}>"

    @name.setter
    def name(self, name: str) -> NoReturn:
        raise RuntimeError('Cannot set name for InvertedFilter')


class MergedFilter(UpdateFilter):
    """Represents a filter consisting of two other filters.

    Args:
        base_filter: Filter 1 of the merged filter.
        and_filter: Optional filter to "and" with base_filter. Mutually exclusive with or_filter.
        or_filter: Optional filter to "or" with base_filter. Mutually exclusive with and_filter.

    """

    def __init__(
        self, base_filter: BaseFilter, and_filter: BaseFilter = None, or_filter: BaseFilter = None
    ):
        self.base_filter = base_filter
        if self.base_filter.data_filter:
            self.data_filter = True
        self.and_filter = and_filter
        if (
            self.and_filter
            and not isinstance(self.and_filter, bool)
            and self.and_filter.data_filter
        ):
            self.data_filter = True
        self.or_filter = or_filter
        if self.or_filter and not isinstance(self.and_filter, bool) and self.or_filter.data_filter:
            self.data_filter = True

    @staticmethod
    def _merge(base_output: Union[bool, Dict], comp_output: Union[bool, Dict]) -> DataDict:
        base = base_output if isinstance(base_output, dict) else {}
        comp = comp_output if isinstance(comp_output, dict) else {}
        for k in comp.keys():
            # Make sure comp values are lists
            comp_value = comp[k] if isinstance(comp[k], list) else []
            try:
                # If base is a list then merge
                if isinstance(base[k], list):
                    base[k] += comp_value
                else:
                    base[k] = [base[k]] + comp_value
            except KeyError:
                base[k] = comp_value
        return base

    def filter(self, update: Update) -> Union[bool, DataDict]:  # pylint: disable=R0911
        base_output = self.base_filter(update)
        # We need to check if the filters are data filters and if so return the merged data.
        # If it's not a data filter or an or_filter but no matches return bool
        if self.and_filter:
            # And filter needs to short circuit if base is falsey
            if base_output:
                comp_output = self.and_filter(update)
                if comp_output:
                    if self.data_filter:
                        merged = self._merge(base_output, comp_output)
                        if merged:
                            return merged
                    return True
        elif self.or_filter:
            # Or filter needs to short circuit if base is truthey
            if base_output:
                if self.data_filter:
                    return base_output
                return True

            comp_output = self.or_filter(update)
            if comp_output:
                if self.data_filter:
                    return comp_output
                return True
        return False

    @property
    def name(self) -> str:
        return (
            f"<{self.base_filter} {'and' if self.and_filter else 'or'} "
            f"{self.and_filter or self.or_filter}>"
        )

    @name.setter
    def name(self, name: str) -> NoReturn:
        raise RuntimeError('Cannot set name for MergedFilter')


class XORFilter(UpdateFilter):
    """Convenience filter acting as wrapper for :class:`MergedFilter` representing the an XOR gate
    for two filters.

    Args:
        base_filter: Filter 1 of the merged filter.
        xor_filter: Filter 2 of the merged filter.

    """

    def __init__(self, base_filter: BaseFilter, xor_filter: BaseFilter):
        self.base_filter = base_filter
        self.xor_filter = xor_filter
        self.merged_filter = (base_filter & ~xor_filter) | (~base_filter & xor_filter)

    def filter(self, update: Update) -> Optional[Union[bool, DataDict]]:
        return self.merged_filter(update)

    @property
    def name(self) -> str:
        return f'<{self.base_filter} xor {self.xor_filter}>'

    @name.setter
    def name(self, name: str) -> NoReturn:
        raise RuntimeError('Cannot set name for XORFilter')


class _DiceEmoji(MessageFilter):
    def __init__(self, emoji: str = None, name: str = None):
        self.name = f'Filters.dice.{name}' if name else 'Filters.dice'
        self.emoji = emoji

    class _DiceValues(MessageFilter):
        def __init__(
            self,
            values: SLT[int],
            name: str,
            emoji: str = None,
        ):
            self.values = [values] if isinstance(values, int) else values
            self.emoji = emoji
            self.name = f'{name}({values})'

        def filter(self, message: Message) -> bool:
            if message.dice and message.dice.value in self.values:
                if self.emoji:
                    return message.dice.emoji == self.emoji
                return True
            return False

    def __call__(  # type: ignore[override]
        self, update: Union[Update, List[int], Tuple[int]]
    ) -> Union[bool, '_DiceValues']:
        if isinstance(update, Update):
            return self.filter(update.effective_message)
        return self._DiceValues(update, self.name, emoji=self.emoji)

    def filter(self, message: Message) -> bool:
        if bool(message.dice):
            if self.emoji:
                return message.dice.emoji == self.emoji
            return True
        return False


class Filters:
    """Predefined filters for use as the ``filter`` argument of
    :class:`telegram.ext.MessageHandler`.

    Examples:
        Use ``MessageHandler(Filters.video, callback_method)`` to filter all video
        messages. Use ``MessageHandler(Filters.contact, callback_method)`` for all contacts. etc.

    """

    class _All(MessageFilter):
        name = 'Filters.all'

        def filter(self, message: Message) -> bool:
            return True

    all = _All()
    """All Messages."""

    class _Text(MessageFilter):
        name = 'Filters.text'

        class _TextStrings(MessageFilter):
            def __init__(self, strings: Union[List[str], Tuple[str]]):
                self.strings = strings
                self.name = f'Filters.text({strings})'

            def filter(self, message: Message) -> bool:
                if message.text:
                    return message.text in self.strings
                return False

        def __call__(  # type: ignore[override]
            self, update: Union[Update, List[str], Tuple[str]]
        ) -> Union[bool, '_TextStrings']:
            if isinstance(update, Update):
                return self.filter(update.effective_message)
            return self._TextStrings(update)

        def filter(self, message: Message) -> bool:
            return bool(message.text)

    text = _Text()
    """Text Messages. If a list of strings is passed, it filters messages to only allow those
    whose text is appearing in the given list.

    Examples:
        To allow any text message, simply use
        ``MessageHandler(Filters.text, callback_method)``.

        A simple use case for passing a list is to allow only messages that were sent by a
        custom :class:`telegram.ReplyKeyboardMarkup`::

            buttons = ['Start', 'Settings', 'Back']
            markup = ReplyKeyboardMarkup.from_column(buttons)
            ...
            MessageHandler(Filters.text(buttons), callback_method)

    Note:
        * Dice messages don't have text. If you want to filter either text or dice messages, use
          ``Filters.text | Filters.dice``.
        * Messages containing a command are accepted by this filter. Use
          ``Filters.text & (~Filters.command)``, if you want to filter only text messages without
          commands.

    Args:
        update (List[:obj:`str`] | Tuple[:obj:`str`], optional): Which messages to allow. Only
            exact matches are allowed. If not specified, will allow any text message.
    """

    class _Caption(MessageFilter):
        name = 'Filters.caption'

        class _CaptionStrings(MessageFilter):
            def __init__(self, strings: Union[List[str], Tuple[str]]):
                self.strings = strings
                self.name = f'Filters.caption({strings})'

            def filter(self, message: Message) -> bool:
                if message.caption:
                    return message.caption in self.strings
                return False

        def __call__(  # type: ignore[override]
            self, update: Union[Update, List[str], Tuple[str]]
        ) -> Union[bool, '_CaptionStrings']:
            if isinstance(update, Update):
                return self.filter(update.effective_message)
            return self._CaptionStrings(update)

        def filter(self, message: Message) -> bool:
            return bool(message.caption)

    caption = _Caption()
    """Messages with a caption. If a list of strings is passed, it filters messages to only
    allow those whose caption is appearing in the given list.

    Examples:
        ``MessageHandler(Filters.caption, callback_method)``

    Args:
        update (List[:obj:`str`] | Tuple[:obj:`str`], optional): Which captions to allow. Only
            exact matches are allowed. If not specified, will allow any message with a caption.
    """

    class _Command(MessageFilter):
        name = 'Filters.command'

        class _CommandOnlyStart(MessageFilter):
            def __init__(self, only_start: bool):
                self.only_start = only_start
                self.name = f'Filters.command({only_start})'

            def filter(self, message: Message) -> bool:
                return bool(
                    message.entities
                    and any(e.type == MessageEntity.BOT_COMMAND for e in message.entities)
                )

        def __call__(  # type: ignore[override]
            self, update: Union[bool, Update]
        ) -> Union[bool, '_CommandOnlyStart']:
            if isinstance(update, Update):
                return self.filter(update.effective_message)
            return self._CommandOnlyStart(update)

        def filter(self, message: Message) -> bool:
            return bool(
                message.entities
                and message.entities[0].type == MessageEntity.BOT_COMMAND
                and message.entities[0].offset == 0
            )

    command = _Command()
    """
    Messages with a :attr:`telegram.MessageEntity.BOT_COMMAND`. By default only allows
    messages `starting` with a bot command. Pass :obj:`False` to also allow messages that contain a
    bot command `anywhere` in the text.

    Examples::

        MessageHandler(Filters.command, command_at_start_callback)
        MessageHandler(Filters.command(False), command_anywhere_callback)

    Note:
        ``Filters.text`` also accepts messages containing a command.

    Args:
        update (:obj:`bool`, optional): Whether to only allow messages that `start` with a bot
            command. Defaults to :obj:`True`.
    """

    class regex(MessageFilter):
        """
        Filters updates by searching for an occurrence of ``pattern`` in the message text.
        The ``re.search()`` function is used to determine whether an update should be filtered.

        Refer to the documentation of the ``re`` module for more information.

        To get the groups and groupdict matched, see :attr:`telegram.ext.CallbackContext.matches`.

        Examples:
            Use ``MessageHandler(Filters.regex(r'help'), callback)`` to capture all messages that
            contain the word 'help'. You can also use
            ``MessageHandler(Filters.regex(re.compile(r'help', re.IGNORECASE)), callback)`` if
            you want your pattern to be case insensitive. This approach is recommended
            if you need to specify flags on your pattern.

        Note:
            Filters use the same short circuiting logic as python's `and`, `or` and `not`.
            This means that for example:

                >>> Filters.regex(r'(a?x)') | Filters.regex(r'(b?x)')

            With a message.text of `x`, will only ever return the matches for the first filter,
            since the second one is never evaluated.

        Args:
            pattern (:obj:`str` | :obj:`Pattern`): The regex pattern.
        """

        data_filter = True

        def __init__(self, pattern: Union[str, Pattern]):
            if isinstance(pattern, str):
                pattern = re.compile(pattern)
            pattern = cast(Pattern, pattern)
            self.pattern: Pattern = pattern
            self.name = f'Filters.regex({self.pattern})'

        def filter(self, message: Message) -> Optional[Dict[str, List[Match]]]:
            """"""  # remove method from docs
            if message.text:
                match = self.pattern.search(message.text)
                if match:
                    return {'matches': [match]}
            return {}

    class caption_regex(MessageFilter):
        """
        Filters updates by searching for an occurrence of ``pattern`` in the message caption.

        This filter works similarly to :class:`Filters.regex`, with the only exception being that
        it applies to the message caption instead of the text.

        Examples:
            Use ``MessageHandler(Filters.photo & Filters.caption_regex(r'help'), callback)``
            to capture all photos with caption containing the word 'help'.

        Note:
            This filter will not work on simple text messages, but only on media with caption.

        Args:
            pattern (:obj:`str` | :obj:`Pattern`): The regex pattern.
        """

        data_filter = True

        def __init__(self, pattern: Union[str, Pattern]):
            if isinstance(pattern, str):
                pattern = re.compile(pattern)
            pattern = cast(Pattern, pattern)
            self.pattern: Pattern = pattern
            self.name = f'Filters.caption_regex({self.pattern})'

        def filter(self, message: Message) -> Optional[Dict[str, List[Match]]]:
            """"""  # remove method from docs
            if message.caption:
                match = self.pattern.search(message.caption)
                if match:
                    return {'matches': [match]}
            return {}

    class _Reply(MessageFilter):
        name = 'Filters.reply'

        def filter(self, message: Message) -> bool:
            return bool(message.reply_to_message)

    reply = _Reply()
    """Messages that are a reply to another message."""

    class _Audio(MessageFilter):
        name = 'Filters.audio'

        def filter(self, message: Message) -> bool:
            return bool(message.audio)

    audio = _Audio()
    """Messages that contain :class:`telegram.Audio`."""

    class _Document(MessageFilter):
        name = 'Filters.document'

        class category(MessageFilter):
            """Filters documents by their category in the mime-type attribute.

            Note:
                This Filter only filters by the mime_type of the document,
                    it doesn't check the validity of the document.
                The user can manipulate the mime-type of a message and
                    send media with wrong types that don't fit to this handler.

            Example:
                Filters.document.category('audio/') returns :obj:`True` for all types
                of audio sent as file, for example 'audio/mpeg' or 'audio/x-wav'.
            """

            def __init__(self, category: Optional[str]):
                """Initialize the category you want to filter

                Args:
                    category (str, optional): category of the media you want to filter"""
                self.category = category
                self.name = f"Filters.document.category('{self.category}')"

            def filter(self, message: Message) -> bool:
                """"""  # remove method from docs
                if message.document:
                    return message.document.mime_type.startswith(self.category)
                return False

        application = category('application/')
        audio = category('audio/')
        image = category('image/')
        video = category('video/')
        text = category('text/')

        class mime_type(MessageFilter):
            """This Filter filters documents by their mime-type attribute

            Note:
                This Filter only filters by the mime_type of the document,
                    it doesn't check the validity of document.
                The user can manipulate the mime-type of a message and
                    send media with wrong types that don't fit to this handler.

            Example:
                ``Filters.document.mime_type('audio/mpeg')`` filters all audio in mp3 format.
            """

            def __init__(self, mimetype: Optional[str]):
                """Initialize the category you want to filter

                Args:
                    mimetype (str, optional): mime_type of the media you want to filter"""
                self.mimetype = mimetype
                self.name = f"Filters.document.mime_type('{self.mimetype}')"

            def filter(self, message: Message) -> bool:
                """"""  # remove method from docs
                if message.document:
                    return message.document.mime_type == self.mimetype
                return False

        apk = mime_type('application/vnd.android.package-archive')
        doc = mime_type('application/msword')
        docx = mime_type('application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        exe = mime_type('application/x-ms-dos-executable')
        gif = mime_type('video/mp4')
        jpg = mime_type('image/jpeg')
        mp3 = mime_type('audio/mpeg')
        pdf = mime_type('application/pdf')
        py = mime_type('text/x-python')
        svg = mime_type('image/svg+xml')
        txt = mime_type('text/plain')
        targz = mime_type('application/x-compressed-tar')
        wav = mime_type('audio/x-wav')
        xml = mime_type('application/xml')
        zip = mime_type('application/zip')

        class file_extension(MessageFilter):
            """This filter filters documents by their file ending/extension.

            Note:
                * This Filter only filters by the file ending/extension of the document,
                  it doesn't check the validity of document.
                * The user can manipulate the file extension of a document and
                  send media with wrong types that don't fit to this handler.
                * Case insensitive by default,
                  you may change this with the flag ``case_sensitive=True``.
                * Extension should be passed without leading dot
                  unless it's a part of the extension.
                * Pass :obj:`None` to filter files with no extension,
                  i.e. without a dot in the filename.

            Example:
                * ``Filters.document.file_extension("jpg")``
                  filters files with extension ``".jpg"``.
                * ``Filters.document.file_extension(".jpg")``
                  filters files with extension ``"..jpg"``.
                * ``Filters.document.file_extension("Dockerfile", case_sensitive=True)``
                  filters files with extension ``".Dockerfile"`` minding the case.
                * ``Filters.document.file_extension(None)``
                  filters files without a dot in the filename.
            """

            def __init__(self, file_extension: Optional[str], case_sensitive: bool = False):
                """Initialize the extension you want to filter.

                Args:
                    file_extension (:obj:`str` | :obj:`None`):
                        media file extension you want to filter.
                    case_sensitive (:obj:bool, optional):
                        pass :obj:`True` to make the filter case sensitive.
                        Default: :obj:`False`.
                """
                self.is_case_sensitive = case_sensitive
                if file_extension is None:
                    self.file_extension = None
                    self.name = "Filters.document.file_extension(None)"
                elif case_sensitive:
                    self.file_extension = f".{file_extension}"
                    self.name = (
                        f"Filters.document.file_extension({file_extension!r},"
                        " case_sensitive=True)"
                    )
                else:
                    self.file_extension = f".{file_extension}".lower()
                    self.name = f"Filters.document.file_extension({file_extension.lower()!r})"

            def filter(self, message: Message) -> bool:
                """"""  # remove method from docs
                if message.document is None:
                    return False
                if self.file_extension is None:
                    return "." not in message.document.file_name
                if self.is_case_sensitive:
                    filename = message.document.file_name
                else:
                    filename = message.document.file_name.lower()
                return filename.endswith(self.file_extension)

        def filter(self, message: Message) -> bool:
            return bool(message.document)

    document = _Document()
    """
    Subset for messages containing a document/file.

    Examples:
        Use these filters like: ``Filters.document.mp3``,
        ``Filters.document.mime_type("text/plain")`` etc. Or use just
        ``Filters.document`` for all document messages.

    Attributes:
        category: Filters documents by their category in the mime-type attribute

            Note:
                This Filter only filters by the mime_type of the document,
                it doesn't check the validity of the document.
                The user can manipulate the mime-type of a message and
                send media with wrong types that don't fit to this handler.

            Example:
                ``Filters.document.category('audio/')`` filters all types
                of audio sent as file, for example 'audio/mpeg' or 'audio/x-wav'.
        application: Same as ``Filters.document.category("application")``.
        audio: Same as ``Filters.document.category("audio")``.
        image: Same as ``Filters.document.category("image")``.
        video: Same as ``Filters.document.category("video")``.
        text: Same as ``Filters.document.category("text")``.
        mime_type: Filters documents by their mime-type attribute

            Note:
                This Filter only filters by the mime_type of the document,
                it doesn't check the validity of document.

                The user can manipulate the mime-type of a message and
                send media with wrong types that don't fit to this handler.

            Example:
                ``Filters.document.mime_type('audio/mpeg')`` filters all audio in mp3 format.
        apk: Same as ``Filters.document.mime_type("application/vnd.android.package-archive")``.
        doc: Same as ``Filters.document.mime_type("application/msword")``.
        docx: Same as ``Filters.document.mime_type("application/vnd.openxmlformats-\
officedocument.wordprocessingml.document")``.
        exe: Same as ``Filters.document.mime_type("application/x-ms-dos-executable")``.
        gif: Same as ``Filters.document.mime_type("video/mp4")``.
        jpg: Same as ``Filters.document.mime_type("image/jpeg")``.
        mp3: Same as ``Filters.document.mime_type("audio/mpeg")``.
        pdf: Same as ``Filters.document.mime_type("application/pdf")``.
        py: Same as ``Filters.document.mime_type("text/x-python")``.
        svg: Same as ``Filters.document.mime_type("image/svg+xml")``.
        txt: Same as ``Filters.document.mime_type("text/plain")``.
        targz: Same as ``Filters.document.mime_type("application/x-compressed-tar")``.
        wav: Same as ``Filters.document.mime_type("audio/x-wav")``.
        xml: Same as ``Filters.document.mime_type("application/xml")``.
        zip: Same as ``Filters.document.mime_type("application/zip")``.
        file_extension: This filter filters documents by their file ending/extension.

            Note:
                * This Filter only filters by the file ending/extension of the document,
                  it doesn't check the validity of document.
                * The user can manipulate the file extension of a document and
                  send media with wrong types that don't fit to this handler.
                * Case insensitive by default,
                  you may change this with the flag ``case_sensitive=True``.
                * Extension should be passed without leading dot
                  unless it's a part of the extension.
                * Pass :obj:`None` to filter files with no extension,
                  i.e. without a dot in the filename.

            Example:
                * ``Filters.document.file_extension("jpg")``
                  filters files with extension ``".jpg"``.
                * ``Filters.document.file_extension(".jpg")``
                  filters files with extension ``"..jpg"``.
                * ``Filters.document.file_extension("Dockerfile", case_sensitive=True)``
                  filters files with extension ``".Dockerfile"`` minding the case.
                * ``Filters.document.file_extension(None)``
                  filters files without a dot in the filename.
    """

    class _Animation(MessageFilter):
        name = 'Filters.animation'

        def filter(self, message: Message) -> bool:
            return bool(message.animation)

    animation = _Animation()
    """Messages that contain :class:`telegram.Animation`."""

    class _Photo(MessageFilter):
        name = 'Filters.photo'

        def filter(self, message: Message) -> bool:
            return bool(message.photo)

    photo = _Photo()
    """Messages that contain :class:`telegram.PhotoSize`."""

    class _Sticker(MessageFilter):
        name = 'Filters.sticker'

        def filter(self, message: Message) -> bool:
            return bool(message.sticker)

    sticker = _Sticker()
    """Messages that contain :class:`telegram.Sticker`."""

    class _Video(MessageFilter):
        name = 'Filters.video'

        def filter(self, message: Message) -> bool:
            return bool(message.video)

    video = _Video()
    """Messages that contain :class:`telegram.Video`."""

    class _Voice(MessageFilter):
        name = 'Filters.voice'

        def filter(self, message: Message) -> bool:
            return bool(message.voice)

    voice = _Voice()
    """Messages that contain :class:`telegram.Voice`."""

    class _VideoNote(MessageFilter):
        name = 'Filters.video_note'

        def filter(self, message: Message) -> bool:
            return bool(message.video_note)

    video_note = _VideoNote()
    """Messages that contain :class:`telegram.VideoNote`."""

    class _Contact(MessageFilter):
        name = 'Filters.contact'

        def filter(self, message: Message) -> bool:
            return bool(message.contact)

    contact = _Contact()
    """Messages that contain :class:`telegram.Contact`."""

    class _Location(MessageFilter):
        name = 'Filters.location'

        def filter(self, message: Message) -> bool:
            return bool(message.location)

    location = _Location()
    """Messages that contain :class:`telegram.Location`."""

    class _Venue(MessageFilter):
        name = 'Filters.venue'

        def filter(self, message: Message) -> bool:
            return bool(message.venue)

    venue = _Venue()
    """Messages that contain :class:`telegram.Venue`."""

    class _StatusUpdate(UpdateFilter):
        """Subset for messages containing a status update.

        Examples:
            Use these filters like: ``Filters.status_update.new_chat_members`` etc. Or use just
            ``Filters.status_update`` for all status update messages.

        """

        class _NewChatMembers(MessageFilter):
            name = 'Filters.status_update.new_chat_members'

            def filter(self, message: Message) -> bool:
                return bool(message.new_chat_members)

        new_chat_members = _NewChatMembers()
        """Messages that contain :attr:`telegram.Message.new_chat_members`."""

        class _LeftChatMember(MessageFilter):
            name = 'Filters.status_update.left_chat_member'

            def filter(self, message: Message) -> bool:
                return bool(message.left_chat_member)

        left_chat_member = _LeftChatMember()
        """Messages that contain :attr:`telegram.Message.left_chat_member`."""

        class _NewChatTitle(MessageFilter):
            name = 'Filters.status_update.new_chat_title'

            def filter(self, message: Message) -> bool:
                return bool(message.new_chat_title)

        new_chat_title = _NewChatTitle()
        """Messages that contain :attr:`telegram.Message.new_chat_title`."""

        class _NewChatPhoto(MessageFilter):
            name = 'Filters.status_update.new_chat_photo'

            def filter(self, message: Message) -> bool:
                return bool(message.new_chat_photo)

        new_chat_photo = _NewChatPhoto()
        """Messages that contain :attr:`telegram.Message.new_chat_photo`."""

        class _DeleteChatPhoto(MessageFilter):
            name = 'Filters.status_update.delete_chat_photo'

            def filter(self, message: Message) -> bool:
                return bool(message.delete_chat_photo)

        delete_chat_photo = _DeleteChatPhoto()
        """Messages that contain :attr:`telegram.Message.delete_chat_photo`."""

        class _ChatCreated(MessageFilter):
            name = 'Filters.status_update.chat_created'

            def filter(self, message: Message) -> bool:
                return bool(
                    message.group_chat_created
                    or message.supergroup_chat_created
                    or message.channel_chat_created
                )

        chat_created = _ChatCreated()
        """Messages that contain :attr:`telegram.Message.group_chat_created`,
            :attr: `telegram.Message.supergroup_chat_created` or
            :attr: `telegram.Message.channel_chat_created`."""

        class _MessageAutoDeleteTimerChanged(MessageFilter):
            name = 'MessageAutoDeleteTimerChanged'

            def filter(self, message: Message) -> bool:
                return bool(message.message_auto_delete_timer_changed)

        message_auto_delete_timer_changed = _MessageAutoDeleteTimerChanged()
        """Messages that contain :attr:`message_auto_delete_timer_changed`"""

        class _Migrate(MessageFilter):
            name = 'Filters.status_update.migrate'

            def filter(self, message: Message) -> bool:
                return bool(message.migrate_from_chat_id or message.migrate_to_chat_id)

        migrate = _Migrate()
        """Messages that contain :attr:`telegram.Message.migrate_from_chat_id` or
            :attr:`telegram.Message.migrate_to_chat_id`."""

        class _PinnedMessage(MessageFilter):
            name = 'Filters.status_update.pinned_message'

            def filter(self, message: Message) -> bool:
                return bool(message.pinned_message)

        pinned_message = _PinnedMessage()
        """Messages that contain :attr:`telegram.Message.pinned_message`."""

        class _ConnectedWebsite(MessageFilter):
            name = 'Filters.status_update.connected_website'

            def filter(self, message: Message) -> bool:
                return bool(message.connected_website)

        connected_website = _ConnectedWebsite()
        """Messages that contain :attr:`telegram.Message.connected_website`."""

        class _ProximityAlertTriggered(MessageFilter):
            name = 'Filters.status_update.proximity_alert_triggered'

            def filter(self, message: Message) -> bool:
                return bool(message.proximity_alert_triggered)

        proximity_alert_triggered = _ProximityAlertTriggered()
        """Messages that contain :attr:`telegram.Message.proximity_alert_triggered`."""

        class _VoiceChatScheduled(MessageFilter):
            name = 'Filters.status_update.voice_chat_scheduled'

            def filter(self, message: Message) -> bool:
                return bool(message.voice_chat_scheduled)

        voice_chat_scheduled = _VoiceChatScheduled()
        """Messages that contain :attr:`telegram.Message.voice_chat_scheduled`."""

        class _VoiceChatStarted(MessageFilter):
            name = 'Filters.status_update.voice_chat_started'

            def filter(self, message: Message) -> bool:
                return bool(message.voice_chat_started)

        voice_chat_started = _VoiceChatStarted()
        """Messages that contain :attr:`telegram.Message.voice_chat_started`."""

        class _VoiceChatEnded(MessageFilter):
            name = 'Filters.status_update.voice_chat_ended'

            def filter(self, message: Message) -> bool:
                return bool(message.voice_chat_ended)

        voice_chat_ended = _VoiceChatEnded()
        """Messages that contain :attr:`telegram.Message.voice_chat_ended`."""

        class _VoiceChatParticipantsInvited(MessageFilter):
            name = 'Filters.status_update.voice_chat_participants_invited'

            def filter(self, message: Message) -> bool:
                return bool(message.voice_chat_participants_invited)

        voice_chat_participants_invited = _VoiceChatParticipantsInvited()
        """Messages that contain :attr:`telegram.Message.voice_chat_participants_invited`."""

        name = 'Filters.status_update'

        def filter(self, message: Update) -> bool:
            return bool(
                self.new_chat_members(message)
                or self.left_chat_member(message)
                or self.new_chat_title(message)
                or self.new_chat_photo(message)
                or self.delete_chat_photo(message)
                or self.chat_created(message)
                or self.message_auto_delete_timer_changed(message)
                or self.migrate(message)
                or self.pinned_message(message)
                or self.connected_website(message)
                or self.proximity_alert_triggered(message)
                or self.voice_chat_scheduled(message)
                or self.voice_chat_started(message)
                or self.voice_chat_ended(message)
                or self.voice_chat_participants_invited(message)
            )

    status_update = _StatusUpdate()
    """Subset for messages containing a status update.

    Examples:
        Use these filters like: ``Filters.status_update.new_chat_members`` etc. Or use just
        ``Filters.status_update`` for all status update messages.

    Attributes:
        chat_created: Messages that contain
            :attr:`telegram.Message.group_chat_created`,
            :attr:`telegram.Message.supergroup_chat_created` or
            :attr:`telegram.Message.channel_chat_created`.
        connected_website: Messages that contain
            :attr:`telegram.Message.connected_website`.
        delete_chat_photo: Messages that contain
            :attr:`telegram.Message.delete_chat_photo`.
        left_chat_member: Messages that contain
            :attr:`telegram.Message.left_chat_member`.
        migrate: Messages that contain
            :attr:`telegram.Message.migrate_to_chat_id` or
            :attr:`telegram.Message.migrate_from_chat_id`.
        new_chat_members: Messages that contain
            :attr:`telegram.Message.new_chat_members`.
        new_chat_photo: Messages that contain
            :attr:`telegram.Message.new_chat_photo`.
        new_chat_title: Messages that contain
            :attr:`telegram.Message.new_chat_title`.
        message_auto_delete_timer_changed: Messages that contain
            :attr:`message_auto_delete_timer_changed`.

            .. versionadded:: 13.4
        pinned_message: Messages that contain
            :attr:`telegram.Message.pinned_message`.
        proximity_alert_triggered: Messages that contain
            :attr:`telegram.Message.proximity_alert_triggered`.
        voice_chat_scheduled: Messages that contain
            :attr:`telegram.Message.voice_chat_scheduled`.

            .. versionadded:: 13.5
        voice_chat_started: Messages that contain
            :attr:`telegram.Message.voice_chat_started`.

            .. versionadded:: 13.4
        voice_chat_ended: Messages that contain
            :attr:`telegram.Message.voice_chat_ended`.

            .. versionadded:: 13.4
        voice_chat_participants_invited: Messages that contain
            :attr:`telegram.Message.voice_chat_participants_invited`.

            .. versionadded:: 13.4

    """

    class _Forwarded(MessageFilter):
        name = 'Filters.forwarded'

        def filter(self, message: Message) -> bool:
            return bool(message.forward_date)

    forwarded = _Forwarded()
    """Messages that are forwarded."""

    class _Game(MessageFilter):
        name = 'Filters.game'

        def filter(self, message: Message) -> bool:
            return bool(message.game)

    game = _Game()
    """Messages that contain :class:`telegram.Game`."""

    class entity(MessageFilter):
        """
        Filters messages to only allow those which have a :class:`telegram.MessageEntity`
        where their `type` matches `entity_type`.

        Examples:
            Example ``MessageHandler(Filters.entity("hashtag"), callback_method)``

        Args:
            entity_type: Entity type to check for. All types can be found as constants
                in :class:`telegram.MessageEntity`.

        """

        def __init__(self, entity_type: str):
            self.entity_type = entity_type
            self.name = f'Filters.entity({self.entity_type})'

        def filter(self, message: Message) -> bool:
            """"""  # remove method from docs
            return any(entity.type == self.entity_type for entity in message.entities)

    class caption_entity(MessageFilter):
        """
        Filters media messages to only allow those which have a :class:`telegram.MessageEntity`
        where their `type` matches `entity_type`.

        Examples:
            Example ``MessageHandler(Filters.caption_entity("hashtag"), callback_method)``

        Args:
            entity_type: Caption Entity type to check for. All types can be found as constants
                in :class:`telegram.MessageEntity`.

        """

        def __init__(self, entity_type: str):
            self.entity_type = entity_type
            self.name = f'Filters.caption_entity({self.entity_type})'

        def filter(self, message: Message) -> bool:
            """"""  # remove method from docs
            return any(entity.type == self.entity_type for entity in message.caption_entities)

    class _Private(MessageFilter):
        name = 'Filters.private'

        def filter(self, message: Message) -> bool:
            warnings.warn(
                'Filters.private is deprecated. Use Filters.chat_type.private instead.',
                TelegramDeprecationWarning,
                stacklevel=2,
            )
            return message.chat.type == Chat.PRIVATE

    private = _Private()
    """
    Messages sent in a private chat.

    Note:
        DEPRECATED. Use
        :attr:`telegram.ext.Filters.chat_type.private` instead.
    """

    class _Group(MessageFilter):
        name = 'Filters.group'

        def filter(self, message: Message) -> bool:
            warnings.warn(
                'Filters.group is deprecated. Use Filters.chat_type.groups instead.',
                TelegramDeprecationWarning,
                stacklevel=2,
            )
            return message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]

    group = _Group()
    """
    Messages sent in a group or a supergroup chat.

    Note:
        DEPRECATED. Use
        :attr:`telegram.ext.Filters.chat_type.groups` instead.
    """

    class _ChatType(MessageFilter):
        name = 'Filters.chat_type'

        class _Channel(MessageFilter):
            name = 'Filters.chat_type.channel'

            def filter(self, message: Message) -> bool:
                return message.chat.type == Chat.CHANNEL

        channel = _Channel()

        class _Group(MessageFilter):
            name = 'Filters.chat_type.group'

            def filter(self, message: Message) -> bool:
                return message.chat.type == Chat.GROUP

        group = _Group()

        class _SuperGroup(MessageFilter):
            name = 'Filters.chat_type.supergroup'

            def filter(self, message: Message) -> bool:
                return message.chat.type == Chat.SUPERGROUP

        supergroup = _SuperGroup()

        class _Groups(MessageFilter):
            name = 'Filters.chat_type.groups'

            def filter(self, message: Message) -> bool:
                return message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]

        groups = _Groups()

        class _Private(MessageFilter):
            name = 'Filters.chat_type.private'

            def filter(self, message: Message) -> bool:
                return message.chat.type == Chat.PRIVATE

        private = _Private()

        def filter(self, message: Message) -> bool:
            return bool(message.chat.type)

    chat_type = _ChatType()
    """Subset for filtering the type of chat.

    Examples:
        Use these filters like: ``Filters.chat_type.channel`` or
        ``Filters.chat_type.supergroup`` etc. Or use just ``Filters.chat_type`` for all
        chat types.

    Attributes:
        channel: Updates from channel
        group: Updates from group
        supergroup: Updates from supergroup
        groups: Updates from group *or* supergroup
        private: Updates sent in private chat
    """

    class _ChatUserBaseFilter(MessageFilter):
        def __init__(
            self,
            chat_id: SLT[int] = None,
            username: SLT[str] = None,
            allow_empty: bool = False,
        ):
            self.chat_id_name = 'chat_id'
            self.username_name = 'username'
            self.allow_empty = allow_empty
            self.__lock = Lock()

            self._chat_ids: Set[int] = set()
            self._usernames: Set[str] = set()

            self._set_chat_ids(chat_id)
            self._set_usernames(username)

        @abstractmethod
        def get_chat_or_user(self, message: Message) -> Union[Chat, User, None]:
            pass

        @staticmethod
        def _parse_chat_id(chat_id: SLT[int]) -> Set[int]:
            if chat_id is None:
                return set()
            if isinstance(chat_id, int):
                return {chat_id}
            return set(chat_id)

        @staticmethod
        def _parse_username(username: SLT[str]) -> Set[str]:
            if username is None:
                return set()
            if isinstance(username, str):
                return {username[1:] if username.startswith('@') else username}
            return {chat[1:] if chat.startswith('@') else chat for chat in username}

        def _set_chat_ids(self, chat_id: SLT[int]) -> None:
            with self.__lock:
                if chat_id and self._usernames:
                    raise RuntimeError(
                        f"Can't set {self.chat_id_name} in conjunction with (already set) "
                        f"{self.username_name}s."
                    )
                self._chat_ids = self._parse_chat_id(chat_id)

        def _set_usernames(self, username: SLT[str]) -> None:
            with self.__lock:
                if username and self._chat_ids:
                    raise RuntimeError(
                        f"Can't set {self.username_name} in conjunction with (already set) "
                        f"{self.chat_id_name}s."
                    )
                self._usernames = self._parse_username(username)

        @property
        def chat_ids(self) -> FrozenSet[int]:
            with self.__lock:
                return frozenset(self._chat_ids)

        @chat_ids.setter
        def chat_ids(self, chat_id: SLT[int]) -> None:
            self._set_chat_ids(chat_id)

        @property
        def usernames(self) -> FrozenSet[str]:
            with self.__lock:
                return frozenset(self._usernames)

        @usernames.setter
        def usernames(self, username: SLT[str]) -> None:
            self._set_usernames(username)

        def add_usernames(self, username: SLT[str]) -> None:
            with self.__lock:
                if self._chat_ids:
                    raise RuntimeError(
                        f"Can't set {self.username_name} in conjunction with (already set) "
                        f"{self.chat_id_name}s."
                    )

                parsed_username = self._parse_username(username)
                self._usernames |= parsed_username

        def add_chat_ids(self, chat_id: SLT[int]) -> None:
            with self.__lock:
                if self._usernames:
                    raise RuntimeError(
                        f"Can't set {self.chat_id_name} in conjunction with (already set) "
                        f"{self.username_name}s."
                    )

                parsed_chat_id = self._parse_chat_id(chat_id)

                self._chat_ids |= parsed_chat_id

        def remove_usernames(self, username: SLT[str]) -> None:
            with self.__lock:
                if self._chat_ids:
                    raise RuntimeError(
                        f"Can't set {self.username_name} in conjunction with (already set) "
                        f"{self.chat_id_name}s."
                    )

                parsed_username = self._parse_username(username)
                self._usernames -= parsed_username

        def remove_chat_ids(self, chat_id: SLT[int]) -> None:
            with self.__lock:
                if self._usernames:
                    raise RuntimeError(
                        f"Can't set {self.chat_id_name} in conjunction with (already set) "
                        f"{self.username_name}s."
                    )
                parsed_chat_id = self._parse_chat_id(chat_id)
                self._chat_ids -= parsed_chat_id

        def filter(self, message: Message) -> bool:
            """"""  # remove method from docs
            chat_or_user = self.get_chat_or_user(message)
            if chat_or_user:
                if self.chat_ids:
                    return chat_or_user.id in self.chat_ids
                if self.usernames:
                    return bool(chat_or_user.username and chat_or_user.username in self.usernames)
                return self.allow_empty
            return False

        @property
        def name(self) -> str:
            return (
                f'Filters.{self.__class__.__name__}('
                f'{", ".join(str(s) for s in (self.usernames or self.chat_ids))})'
            )

        @name.setter
        def name(self, name: str) -> NoReturn:
            raise RuntimeError(f'Cannot set name for Filters.{self.__class__.__name__}')

    class user(_ChatUserBaseFilter):
        # pylint: disable=W0235
        """Filters messages to allow only those which are from specified user ID(s) or
        username(s).

        Examples:
            ``MessageHandler(Filters.user(1234), callback_method)``

        Warning:
            :attr:`user_ids` will give a *copy* of the saved user ids as :class:`frozenset`. This
            is to ensure thread safety. To add/remove a user, you should use :meth:`add_usernames`,
            :meth:`add_user_ids`, :meth:`remove_usernames` and :meth:`remove_user_ids`. Only update
            the entire set by ``filter.user_ids/usernames = new_set``, if you are entirely sure
            that it is not causing race conditions, as this will complete replace the current set
            of allowed users.

        Args:
            user_id(:class:`telegram.utils.types.SLT[int]`, optional):
                Which user ID(s) to allow through.
            username(:class:`telegram.utils.types.SLT[str]`, optional):
                Which username(s) to allow through. Leading ``'@'`` s in usernames will be
                discarded.
            allow_empty(:obj:`bool`, optional): Whether updates should be processed, if no user
                is specified in :attr:`user_ids` and :attr:`usernames`. Defaults to :obj:`False`

        Raises:
            RuntimeError: If user_id and username are both present.

        Attributes:
            user_ids(set(:obj:`int`), optional): Which user ID(s) to allow through.
            usernames(set(:obj:`str`), optional): Which username(s) (without leading ``'@'``) to
                allow through.
            allow_empty(:obj:`bool`, optional): Whether updates should be processed, if no user
                is specified in :attr:`user_ids` and :attr:`usernames`.

        """

        def __init__(
            self,
            user_id: SLT[int] = None,
            username: SLT[str] = None,
            allow_empty: bool = False,
        ):
            super().__init__(chat_id=user_id, username=username, allow_empty=allow_empty)
            self.chat_id_name = 'user_id'

        def get_chat_or_user(self, message: Message) -> Optional[User]:
            return message.from_user

        @property
        def user_ids(self) -> FrozenSet[int]:
            return self.chat_ids

        @user_ids.setter
        def user_ids(self, user_id: SLT[int]) -> None:
            self.chat_ids = user_id  # type: ignore[assignment]

        def add_usernames(self, username: SLT[str]) -> None:
            """
            Add one or more users to the allowed usernames.

            Args:
                username(:class:`telegram.utils.types.SLT[str]`, optional):
                    Which username(s) to allow through.
                    Leading ``'@'`` s in usernames will be discarded.
            """
            return super().add_usernames(username)

        def add_user_ids(self, user_id: SLT[int]) -> None:
            """
            Add one or more users to the allowed user ids.

            Args:
                user_id(:class:`telegram.utils.types.SLT[int]`, optional):
                    Which user ID(s) to allow through.
            """
            return super().add_chat_ids(user_id)

        def remove_usernames(self, username: SLT[str]) -> None:
            """
            Remove one or more users from allowed usernames.

            Args:
                username(:class:`telegram.utils.types.SLT[str]`, optional):
                    Which username(s) to disallow through.
                    Leading ``'@'`` s in usernames will be discarded.
            """
            return super().remove_usernames(username)

        def remove_user_ids(self, user_id: SLT[int]) -> None:
            """
            Remove one or more users from allowed user ids.

            Args:
                user_id(:class:`telegram.utils.types.SLT[int]`, optional):
                    Which user ID(s) to disallow through.
            """
            return super().remove_chat_ids(user_id)

    class via_bot(_ChatUserBaseFilter):
        # pylint: disable=W0235
        """Filters messages to allow only those which are from specified via_bot ID(s) or
        username(s).

        Examples:
            ``MessageHandler(Filters.via_bot(1234), callback_method)``

        Warning:
            :attr:`bot_ids` will give a *copy* of the saved bot ids as :class:`frozenset`. This
            is to ensure thread safety. To add/remove a bot, you should use :meth:`add_usernames`,
            :meth:`add_bot_ids`, :meth:`remove_usernames` and :meth:`remove_bot_ids`. Only update
            the entire set by ``filter.bot_ids/usernames = new_set``, if you are entirely sure
            that it is not causing race conditions, as this will complete replace the current set
            of allowed bots.

        Args:
            bot_id(:class:`telegram.utils.types.SLT[int]`, optional):
                Which bot ID(s) to allow through.
            username(:class:`telegram.utils.types.SLT[str]`, optional):
                Which username(s) to allow through. Leading ``'@'`` s in usernames will be
                discarded.
            allow_empty(:obj:`bool`, optional): Whether updates should be processed, if no user
                is specified in :attr:`bot_ids` and :attr:`usernames`. Defaults to :obj:`False`

        Raises:
            RuntimeError: If bot_id and username are both present.

        Attributes:
            bot_ids(set(:obj:`int`), optional): Which bot ID(s) to allow through.
            usernames(set(:obj:`str`), optional): Which username(s) (without leading ``'@'``) to
                allow through.
            allow_empty(:obj:`bool`, optional): Whether updates should be processed, if no bot
                is specified in :attr:`bot_ids` and :attr:`usernames`.

        """

        def __init__(
            self,
            bot_id: SLT[int] = None,
            username: SLT[str] = None,
            allow_empty: bool = False,
        ):
            super().__init__(chat_id=bot_id, username=username, allow_empty=allow_empty)
            self.chat_id_name = 'bot_id'

        def get_chat_or_user(self, message: Message) -> Optional[User]:
            return message.via_bot

        @property
        def bot_ids(self) -> FrozenSet[int]:
            return self.chat_ids

        @bot_ids.setter
        def bot_ids(self, bot_id: SLT[int]) -> None:
            self.chat_ids = bot_id  # type: ignore[assignment]

        def add_usernames(self, username: SLT[str]) -> None:
            """
            Add one or more users to the allowed usernames.

            Args:
                username(:class:`telegram.utils.types.SLT[str]`, optional):
                    Which username(s) to allow through.
                    Leading ``'@'`` s in usernames will be discarded.
            """
            return super().add_usernames(username)

        def add_bot_ids(self, bot_id: SLT[int]) -> None:
            """

            Add one or more users to the allowed user ids.

            Args:
                bot_id(:class:`telegram.utils.types.SLT[int]`, optional):
                    Which bot ID(s) to allow through.
            """
            return super().add_chat_ids(bot_id)

        def remove_usernames(self, username: SLT[str]) -> None:
            """
            Remove one or more users from allowed usernames.

            Args:
                username(:class:`telegram.utils.types.SLT[str]`, optional):
                    Which username(s) to disallow through.
                    Leading ``'@'`` s in usernames will be discarded.
            """
            return super().remove_usernames(username)

        def remove_bot_ids(self, bot_id: SLT[int]) -> None:
            """
            Remove one or more users from allowed user ids.

            Args:
                bot_id(:class:`telegram.utils.types.SLT[int]`, optional):
                    Which bot ID(s) to disallow through.
            """
            return super().remove_chat_ids(bot_id)

    class chat(_ChatUserBaseFilter):
        # pylint: disable=W0235
        """Filters messages to allow only those which are from a specified chat ID or username.

        Examples:
            ``MessageHandler(Filters.chat(-1234), callback_method)``

        Warning:
            :attr:`chat_ids` will give a *copy* of the saved chat ids as :class:`frozenset`. This
            is to ensure thread safety. To add/remove a chat, you should use :meth:`add_usernames`,
            :meth:`add_chat_ids`, :meth:`remove_usernames` and :meth:`remove_chat_ids`. Only update
            the entire set by ``filter.chat_ids/usernames = new_set``, if you are entirely sure
            that it is not causing race conditions, as this will complete replace the current set
            of allowed chats.

        Args:
            chat_id(:class:`telegram.utils.types.SLT[int]`, optional):
                Which chat ID(s) to allow through.
            username(:class:`telegram.utils.types.SLT[str]`, optional):
                Which username(s) to allow through.
                Leading ``'@'`` s in usernames will be discarded.
            allow_empty(:obj:`bool`, optional): Whether updates should be processed, if no chat
                is specified in :attr:`chat_ids` and :attr:`usernames`. Defaults to :obj:`False`

        Raises:
            RuntimeError: If chat_id and username are both present.

        Attributes:
            chat_ids(set(:obj:`int`), optional): Which chat ID(s) to allow through.
            usernames(set(:obj:`str`), optional): Which username(s) (without leading ``'@'``) to
                allow through.
            allow_empty(:obj:`bool`, optional): Whether updates should be processed, if no chat
                is specified in :attr:`chat_ids` and :attr:`usernames`.

        """

        def get_chat_or_user(self, message: Message) -> Optional[Chat]:
            return message.chat

        def add_usernames(self, username: SLT[str]) -> None:
            """
            Add one or more chats to the allowed usernames.

            Args:
                username(:class:`telegram.utils.types.SLT[str]`, optional):
                    Which username(s) to allow through.
                    Leading ``'@'`` s in usernames will be discarded.
            """
            return super().add_usernames(username)

        def add_chat_ids(self, chat_id: SLT[int]) -> None:
            """
            Add one or more chats to the allowed chat ids.

            Args:
                chat_id(:class:`telegram.utils.types.SLT[int]`, optional):
                    Which chat ID(s) to allow through.
            """
            return super().add_chat_ids(chat_id)

        def remove_usernames(self, username: SLT[str]) -> None:
            """
            Remove one or more chats from allowed usernames.

            Args:
                username(:class:`telegram.utils.types.SLT[str]`, optional):
                    Which username(s) to disallow through.
                    Leading ``'@'`` s in usernames will be discarded.
            """
            return super().remove_usernames(username)

        def remove_chat_ids(self, chat_id: SLT[int]) -> None:
            """
            Remove one or more chats from allowed chat ids.

            Args:
                chat_id(:class:`telegram.utils.types.SLT[int]`, optional):
                    Which chat ID(s) to disallow through.
            """
            return super().remove_chat_ids(chat_id)

    class forwarded_from(_ChatUserBaseFilter):
        # pylint: disable=W0235
        """Filters messages to allow only those which are forwarded from the specified chat ID(s)
        or username(s) based on :attr:`telegram.Message.forward_from` and
        :attr:`telegram.Message.forward_from_chat`.

        .. versionadded:: 13.5

        Examples:
            ``MessageHandler(Filters.forwarded_from(chat_id=1234), callback_method)``

        Note:
            When a user has disallowed adding a link to their account while forwarding their
            messages, this filter will *not* work since both
            :attr:`telegram.Message.forwarded_from` and
            :attr:`telegram.Message.forwarded_from_chat` are :obj:`None`. However, this behaviour
            is undocumented and might be changed by Telegram.

        Warning:
            :attr:`chat_ids` will give a *copy* of the saved chat ids as :class:`frozenset`. This
            is to ensure thread safety. To add/remove a chat, you should use :meth:`add_usernames`,
            :meth:`add_chat_ids`, :meth:`remove_usernames` and :meth:`remove_chat_ids`. Only update
            the entire set by ``filter.chat_ids/usernames = new_set``, if you are entirely sure
            that it is not causing race conditions, as this will complete replace the current set
            of allowed chats.

        Args:
            chat_id(:class:`telegram.utils.types.SLT[int]`, optional):
                Which chat/user ID(s) to allow through.
            username(:class:`telegram.utils.types.SLT[str]`, optional):
                Which username(s) to allow through. Leading ``'@'`` s in usernames will be
                discarded.
            allow_empty(:obj:`bool`, optional): Whether updates should be processed, if no chat
                is specified in :attr:`chat_ids` and :attr:`usernames`. Defaults to :obj:`False`.

        Raises:
            RuntimeError: If both chat_id and username are present.

        Attributes:
            chat_ids(set(:obj:`int`), optional): Which chat/user ID(s) to allow through.
            usernames(set(:obj:`str`), optional): Which username(s) (without leading ``'@'``) to
                allow through.
            allow_empty(:obj:`bool`, optional): Whether updates should be processed, if no chat
                is specified in :attr:`chat_ids` and :attr:`usernames`.
        """

        def get_chat_or_user(self, message: Message) -> Union[User, Chat, None]:
            return message.forward_from or message.forward_from_chat

        def add_usernames(self, username: SLT[str]) -> None:
            """
            Add one or more chats to the allowed usernames.

            Args:
                username(:class:`telegram.utils.types.SLT[str]`, optional):
                    Which username(s) to allow through.
                    Leading ``'@'`` s in usernames will be discarded.
            """
            return super().add_usernames(username)

        def add_chat_ids(self, chat_id: SLT[int]) -> None:
            """
            Add one or more chats to the allowed chat ids.

            Args:
                chat_id(:class:`telegram.utils.types.SLT[int]`, optional):
                    Which chat/user ID(s) to allow through.
            """
            return super().add_chat_ids(chat_id)

        def remove_usernames(self, username: SLT[str]) -> None:
            """
            Remove one or more chats from allowed usernames.

            Args:
                username(:class:`telegram.utils.types.SLT[str]`, optional):
                    Which username(s) to disallow through.
                    Leading ``'@'`` s in usernames will be discarded.
            """
            return super().remove_usernames(username)

        def remove_chat_ids(self, chat_id: SLT[int]) -> None:
            """
            Remove one or more chats from allowed chat ids.

            Args:
                chat_id(:class:`telegram.utils.types.SLT[int]`, optional):
                    Which chat/user ID(s) to disallow through.
            """
            return super().remove_chat_ids(chat_id)

    class sender_chat(_ChatUserBaseFilter):
        # pylint: disable=W0235
        """Filters messages to allow only those which are from a specified sender chats chat ID or
        username.

        Examples:
            * To filter for messages forwarded to a discussion group from a channel with ID
              ``-1234``, use ``MessageHandler(Filters.sender_chat(-1234), callback_method)``.
            * To filter for messages of anonymous admins in a super group with username
              ``@anonymous``, use
              ``MessageHandler(Filters.sender_chat(username='anonymous'), callback_method)``.
            * To filter for messages forwarded to a discussion group from *any* channel, use
              ``MessageHandler(Filters.sender_chat.channel, callback_method)``.
            * To filter for messages of anonymous admins in *any* super group, use
              ``MessageHandler(Filters.sender_chat.super_group, callback_method)``.

        Note:
            Remember, ``sender_chat`` is also set for messages in a channel as the channel itself,
            so when your bot is an admin in a channel and the linked discussion group, you would
            receive the message twice (once from inside the channel, once inside the discussion
            group).

        Warning:
            :attr:`chat_ids` will return a *copy* of the saved chat ids as :class:`frozenset`. This
            is to ensure thread safety. To add/remove a chat, you should use :meth:`add_usernames`,
            :meth:`add_chat_ids`, :meth:`remove_usernames` and :meth:`remove_chat_ids`. Only update
            the entire set by ``filter.chat_ids/usernames = new_set``, if you are entirely sure
            that it is not causing race conditions, as this will complete replace the current set
            of allowed chats.

        Args:
            chat_id(:class:`telegram.utils.types.SLT[int]`, optional):
                Which sender chat chat ID(s) to allow through.
            username(:class:`telegram.utils.types.SLT[str]`, optional):
                Which sender chat username(s) to allow through.
                Leading ``'@'`` s in usernames will be discarded.
            allow_empty(:obj:`bool`, optional): Whether updates should be processed, if no sender
                chat is specified in :attr:`chat_ids` and :attr:`usernames`. Defaults to
                :obj:`False`

        Raises:
            RuntimeError: If both chat_id and username are present.

        Attributes:
            chat_ids(set(:obj:`int`), optional): Which sender chat chat ID(s) to allow through.
            usernames(set(:obj:`str`), optional): Which sender chat username(s) (without leading
                ``'@'``) to allow through.
            allow_empty(:obj:`bool`, optional): Whether updates should be processed, if no sender
                chat is specified in :attr:`chat_ids` and :attr:`usernames`.
            super_group: Messages whose sender chat is a super group.

                Examples:
                    ``Filters.sender_chat.supergroup``
            channel: Messages whose sender chat is a channel.

                Examples:
                    ``Filters.sender_chat.channel``

        """

        def get_chat_or_user(self, message: Message) -> Optional[Chat]:
            return message.sender_chat

        def add_usernames(self, username: SLT[str]) -> None:
            """
            Add one or more sender chats to the allowed usernames.

            Args:
                username(:class:`telegram.utils.types.SLT[str]`, optional):
                    Which sender chat username(s) to allow through.
                    Leading ``'@'`` s in usernames will be discarded.
            """
            return super().add_usernames(username)

        def add_chat_ids(self, chat_id: SLT[int]) -> None:
            """
            Add one or more sender chats to the allowed chat ids.

            Args:
                chat_id(:class:`telegram.utils.types.SLT[int]`, optional):
                    Which sender chat ID(s) to allow through.
            """
            return super().add_chat_ids(chat_id)

        def remove_usernames(self, username: SLT[str]) -> None:
            """
            Remove one or more sender chats from allowed usernames.

            Args:
                username(:class:`telegram.utils.types.SLT[str]`, optional):
                    Which sender chat username(s) to disallow through.
                    Leading ``'@'`` s in usernames will be discarded.
            """
            return super().remove_usernames(username)

        def remove_chat_ids(self, chat_id: SLT[int]) -> None:
            """
            Remove one or more sender chats from allowed chat ids.

            Args:
                chat_id(:class:`telegram.utils.types.SLT[int]`, optional):
                    Which sender chat ID(s) to disallow through.
            """
            return super().remove_chat_ids(chat_id)

        class _SuperGroup(MessageFilter):
            def filter(self, message: Message) -> bool:
                if message.sender_chat:
                    return message.sender_chat.type == Chat.SUPERGROUP
                return False

        class _Channel(MessageFilter):
            def filter(self, message: Message) -> bool:
                if message.sender_chat:
                    return message.sender_chat.type == Chat.CHANNEL
                return False

        super_group = _SuperGroup()
        channel = _Channel()

    class _Invoice(MessageFilter):
        name = 'Filters.invoice'

        def filter(self, message: Message) -> bool:
            return bool(message.invoice)

    invoice = _Invoice()
    """Messages that contain :class:`telegram.Invoice`."""

    class _SuccessfulPayment(MessageFilter):
        name = 'Filters.successful_payment'

        def filter(self, message: Message) -> bool:
            return bool(message.successful_payment)

    successful_payment = _SuccessfulPayment()
    """Messages that confirm a :class:`telegram.SuccessfulPayment`."""

    class _PassportData(MessageFilter):
        name = 'Filters.passport_data'

        def filter(self, message: Message) -> bool:
            return bool(message.passport_data)

    passport_data = _PassportData()
    """Messages that contain a :class:`telegram.PassportData`"""

    class _Poll(MessageFilter):
        name = 'Filters.poll'

        def filter(self, message: Message) -> bool:
            return bool(message.poll)

    poll = _Poll()
    """Messages that contain a :class:`telegram.Poll`."""

    class _Dice(_DiceEmoji):
        dice = _DiceEmoji('🎲', 'dice')
        darts = _DiceEmoji('🎯', 'darts')
        basketball = _DiceEmoji('🏀', 'basketball')
        football = _DiceEmoji('⚽')
        slot_machine = _DiceEmoji('🎰')
        bowling = _DiceEmoji('🎳', 'bowling')

    dice = _Dice()
    """Dice Messages. If an integer or a list of integers is passed, it filters messages to only
    allow those whose dice value is appearing in the given list.

    Examples:
        To allow any dice message, simply use
        ``MessageHandler(Filters.dice, callback_method)``.
        To allow only dice with value 6, use
        ``MessageHandler(Filters.dice(6), callback_method)``.
        To allow only dice with value 5 `or` 6, use
        ``MessageHandler(Filters.dice([5, 6]), callback_method)``.

    Note:
        Dice messages don't have text. If you want to filter either text or dice messages, use
        ``Filters.text | Filters.dice``.

    Args:
        update (:class:`telegram.utils.types.SLT[int]`, optional):
            Which values to allow. If not specified, will allow any dice message.

    Attributes:
        dice: Dice messages with the emoji 🎲. Passing a list of integers is supported just as for
            :attr:`Filters.dice`.
        darts: Dice messages with the emoji 🎯. Passing a list of integers is supported just as for
            :attr:`Filters.dice`.
        basketball: Dice messages with the emoji 🏀. Passing a list of integers is supported just
            as for :attr:`Filters.dice`.
        football: Dice messages with the emoji ⚽. Passing a list of integers is supported just
            as for :attr:`Filters.dice`.
        slot_machine: Dice messages with the emoji 🎰. Passing a list of integers is supported just
            as for :attr:`Filters.dice`.
        bowling: Dice messages with the emoji 🎳. Passing a list of integers is supported just
            as for :attr:`Filters.dice`.

            .. versionadded:: 13.4

    """

    class language(MessageFilter):
        """Filters messages to only allow those which are from users with a certain language code.

        Note:
            According to official Telegram API documentation, not every single user has the
            `language_code` attribute. Do not count on this filter working on all users.

        Examples:
            ``MessageHandler(Filters.language("en"), callback_method)``

        Args:
            lang (:class:`telegram.utils.types.SLT[str]`):
                Which language code(s) to allow through.
                This will be matched using ``.startswith`` meaning that
                'en' will match both 'en_US' and 'en_GB'.

        """

        def __init__(self, lang: SLT[str]):
            if isinstance(lang, str):
                lang = cast(str, lang)
                self.lang = [lang]
            else:
                lang = cast(List[str], lang)
                self.lang = lang
            self.name = f'Filters.language({self.lang})'

        def filter(self, message: Message) -> bool:
            """"""  # remove method from docs
            return bool(
                message.from_user.language_code
                and any(message.from_user.language_code.startswith(x) for x in self.lang)
            )

    class _UpdateType(UpdateFilter):
        name = 'Filters.update'

        class _Message(UpdateFilter):
            name = 'Filters.update.message'

            def filter(self, update: Update) -> bool:
                return update.message is not None

        message = _Message()

        class _EditedMessage(UpdateFilter):
            name = 'Filters.update.edited_message'

            def filter(self, update: Update) -> bool:
                return update.edited_message is not None

        edited_message = _EditedMessage()

        class _Messages(UpdateFilter):
            name = 'Filters.update.messages'

            def filter(self, update: Update) -> bool:
                return update.message is not None or update.edited_message is not None

        messages = _Messages()

        class _ChannelPost(UpdateFilter):
            name = 'Filters.update.channel_post'

            def filter(self, update: Update) -> bool:
                return update.channel_post is not None

        channel_post = _ChannelPost()

        class _EditedChannelPost(UpdateFilter):
            name = 'Filters.update.edited_channel_post'

            def filter(self, update: Update) -> bool:
                return update.edited_channel_post is not None

        edited_channel_post = _EditedChannelPost()

        class _ChannelPosts(UpdateFilter):
            name = 'Filters.update.channel_posts'

            def filter(self, update: Update) -> bool:
                return update.channel_post is not None or update.edited_channel_post is not None

        channel_posts = _ChannelPosts()

        def filter(self, update: Update) -> bool:
            return bool(self.messages(update) or self.channel_posts(update))

    update = _UpdateType()
    """Subset for filtering the type of update.

    Examples:
        Use these filters like: ``Filters.update.message`` or
        ``Filters.update.channel_posts`` etc. Or use just ``Filters.update`` for all
        types.

    Attributes:
        message: Updates with :attr:`telegram.Update.message`
        edited_message: Updates with :attr:`telegram.Update.edited_message`
        messages: Updates with either :attr:`telegram.Update.message` or
            :attr:`telegram.Update.edited_message`
        channel_post: Updates with :attr:`telegram.Update.channel_post`
        edited_channel_post: Updates with
            :attr:`telegram.Update.edited_channel_post`
        channel_posts: Updates with either :attr:`telegram.Update.channel_post` or
            :attr:`telegram.Update.edited_channel_post`
    """
