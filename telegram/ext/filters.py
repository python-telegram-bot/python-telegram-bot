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
# pylint: disable=empty-docstring,  invalid-name,  arguments-differ
"""This module contains the Filters for use with the MessageHandler class."""

import re

from abc import ABC, abstractmethod
from functools import partial
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

from telegram import Chat as TGChat, Message, MessageEntity, Update, User as TGUser

__all__ = [
    'BaseFilter',
    'MessageFilter',
    'UpdateFilter',
    'InvertedFilter',
    'MergedFilter',
    'XORFilter',
]

from telegram._utils.types import SLT
from telegram.constants import DiceEmoji as DE

DataDict = Dict[str, list]


class BaseFilter(ABC):
    """Base class for all Filters.

    Filters subclassing from this class can combined using bitwise operators:

    And:

        >>> (filters.TEXT & filters.Entity(MENTION))

    Or:

        >>> (filters.AUDIO | filters.VIDEO)

    Exclusive Or:

        >>> (filters.Regex('To Be') ^ filters.Regex('Not 2B'))

    Not:

        >>> ~ filters.COMMAND

    Also works with more than two filters:

        >>> (filters.TEXT & (filters.Entity(URL) | filters.Entity(TEXT_LINK)))
        >>> filters.TEXT & (~ filters.FORWARDED)

    Note:
        Filters use the same short circuiting logic as python's `and`, `or` and `not`.
        This means that for example:

            >>> filters.Regex(r'(a?x)') | filters.Regex(r'(b?x)')

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

    __slots__ = ('_name', '_data_filter')

    # pylint: disable=unused-argument
    def __new__(cls, *args: object, **kwargs: object) -> 'BaseFilter':
        # We do this here instead of in a __init__ so filter don't have to call __init__ or super()
        instance = super().__new__(cls)
        instance._name = None
        instance._data_filter = False

        return instance

    @abstractmethod
    def __call__(self, update: Update) -> Optional[Union[bool, DataDict]]:
        ...

    def __and__(self, other: 'BaseFilter') -> 'BaseFilter':
        return MergedFilter(self, and_filter=other)

    def __or__(self, other: 'BaseFilter') -> 'BaseFilter':
        return MergedFilter(self, or_filter=other)

    def __xor__(self, other: 'BaseFilter') -> 'BaseFilter':
        return XORFilter(self, other)

    def __invert__(self) -> 'BaseFilter':
        return InvertedFilter(self)

    @property
    def data_filter(self) -> bool:
        return self._data_filter

    @data_filter.setter
    def data_filter(self, value: bool) -> None:
        self._data_filter = value

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, name: Optional[str]) -> None:
        self._name = name  # pylint: disable=assigning-non-slot

    def __repr__(self) -> str:
        # We do this here instead of in a __init__ so filter don't have to call __init__ or super()
        if self.name is None:
            self.name = self.__class__.__name__
        return self.name


class MessageFilter(BaseFilter):
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

    __slots__ = ()

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


class UpdateFilter(BaseFilter):
    """Base class for all Update Filters. In contrast to :class:`MessageFilter`, the object
    passed to :meth:`filter` is ``update``, which allows to create filters like
    :attr:`filters.UpdateType.EDITED_MESSAGE`.

    Please see :class:`telegram.ext.filters.BaseFilter` for details on how to create custom
    filters.

    Attributes:
        name (:obj:`str`): Name for this filter. Defaults to the type of filter.
        data_filter (:obj:`bool`): Whether this filter is a data filter. A data filter should
            return a dict with lists. The dict will be merged with
            :class:`telegram.ext.CallbackContext`'s internal dict in most cases
            (depends on the handler).

    """

    __slots__ = ()

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

    __slots__ = ('f',)

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

    __slots__ = ('base_filter', 'and_filter', 'or_filter')

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

    # pylint: disable=too-many-return-statements
    def filter(self, update: Update) -> Union[bool, DataDict]:
        base_output = self.base_filter(update)
        # We need to check if the filters are data filters and if so return the merged data.
        # If it's not a data filter or an or_filter but no matches return bool
        if self.and_filter:
            # And filter needs to short circuit if base is falsy
            if base_output:
                comp_output = self.and_filter(update)
                if comp_output:
                    if self.data_filter:
                        merged = self._merge(base_output, comp_output)
                        if merged:
                            return merged
                    return True
        elif self.or_filter:
            # Or filter needs to short circuit if base is truthy
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

    __slots__ = ('base_filter', 'xor_filter', 'merged_filter')

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
    __slots__ = ('emoji',)

    def __init__(self, values: SLT[int] = None, emoji: str = None):
        # self.name = f'Filters.dice.{name}' if name else 'Filters.dice'
        self.emoji = emoji
        self.values = [values] if isinstance(values, int) else values

    def filter(self, message: Message) -> bool:
        if not message.dice:
            return False

        if self.emoji:
            if self.values:
                return True if message.dice.value in self.values else False
            return message.dice.emoji == self.emoji
        return True


class _All(MessageFilter):
    __slots__ = ()
    name = 'Filters.all'

    def filter(self, message: Message) -> bool:
        return True


ALL = _All()
"""All Messages."""


class Text(MessageFilter):
    __slots__ = ('strings',)

    def __init__(self, strings: Union[List[str], Tuple[str]] = None):
        self.strings = strings
        self.name = f'Filters.text({strings})'

    def filter(self, message: Message) -> bool:
        if self.strings is None:
            return bool(message.text)
        return message.text in self.strings if message.text else False


TEXT = Text()
"""Text Messages. If a list of strings is passed, it filters messages to only allow those
whose text is appearing in the given list.

Examples:
    To allow any text message, simply use
    ``MessageHandler(filters.TEXT, callback_method)``.

    A simple use case for passing a list is to allow only messages that were sent by a
    custom :class:`telegram.ReplyKeyboardMarkup`::

        buttons = ['Start', 'Settings', 'Back']
        markup = ReplyKeyboardMarkup.from_column(buttons)
        ...
        MessageHandler(filters.Text(buttons), callback_method)

Note:
    * Dice messages don't have text. If you want to filter either text or dice messages, use
      ``filters.TEXT | filters.DICE``.
    * Messages containing a command are accepted by this filter. Use
      ``filters.TEXT & (~filters.COMMAND)``, if you want to filter only text messages without
      commands.

Args:
    update (List[:obj:`str`] | Tuple[:obj:`str`], optional): Which messages to allow. Only
        exact matches are allowed. If not specified, will allow any text message.
"""


class Caption(MessageFilter):
    __slots__ = ('strings',)

    def __init__(self, strings: Union[List[str], Tuple[str]] = None):
        self.strings = strings
        self.name = f'Filters.caption({strings})'

    def filter(self, message: Message) -> bool:
        if self.strings is None:
            return bool(message.caption)
        return message.caption in self.strings if message.caption else False


CAPTION = Caption()
"""Messages with a caption. If a list of strings is passed, it filters messages to only
allow those whose caption is appearing in the given list.

Examples:
    ``MessageHandler(filters.CAPTION, callback_method)``
    ``MessageHandler(filters.Caption(['PTB rocks!', 'PTB'], callback_method_2)``

Args:
    update (List[:obj:`str`] | Tuple[:obj:`str`], optional): Which captions to allow. Only
        exact matches are allowed. If not specified, will allow any message with a caption.
"""


class Command(MessageFilter):
    __slots__ = ('only_start',)

    def __init__(self, only_start: bool = None):
        self.only_start = only_start
        self.name = f'Filters.command({only_start})'

    def filter(self, message: Message) -> bool:
        if not message.entities:
            return False

        first = message.entities[0]

        if self.only_start:
            return bool(first.type == MessageEntity.BOT_COMMAND and first.offset == 0)
        return bool(any(e.type == MessageEntity.BOT_COMMAND for e in message.entities))


COMMAND = Command()
"""
Messages with a :attr:`telegram.MessageEntity.BOT_COMMAND`. By default only allows
messages `starting` with a bot command. Pass :obj:`False` to also allow messages that contain a
bot command `anywhere` in the text.

Examples::

    MessageHandler(filters.COMMAND, command_at_start_callback)
    MessageHandler(filters.Command(False), command_anywhere_callback)

Note:
    ``filters.TEXT`` also accepts messages containing a command.

Args:
    update (:obj:`bool`, optional): Whether to only allow messages that `start` with a bot
        command. Defaults to :obj:`True`.
"""


class Regex(MessageFilter):
    """
    Filters updates by searching for an occurrence of ``pattern`` in the message text.
    The :obj:`re.search()` function is used to determine whether an update should be filtered.

    Refer to the documentation of the :obj:`re` module for more information.

    To get the groups and groupdict matched, see :attr:`telegram.ext.CallbackContext.matches`.

    Examples:
        Use ``MessageHandler(filters.Regex(r'help'), callback)`` to capture all messages that
        contain the word 'help'. You can also use
        ``MessageHandler(filters.Regex(re.compile(r'help', re.IGNORECASE)), callback)`` if
        you want your pattern to be case insensitive. This approach is recommended
        if you need to specify flags on your pattern.

    Note:
        Filters use the same short circuiting logic as python's `and`, `or` and `not`.
        This means that for example:

            >>> filters.Regex(r'(a?x)') | filters.Regex(r'(b?x)')

        With a message.text of `x`, will only ever return the matches for the first filter,
        since the second one is never evaluated.

    Args:
        pattern (:obj:`str` | :obj:`re.Pattern`): The regex pattern.
    """

    __slots__ = ('pattern',)
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


class CaptionRegex(MessageFilter):
    """
    Filters updates by searching for an occurrence of ``pattern`` in the message caption.

    This filter works similarly to :class:`filters.Regex`, with the only exception being that
    it applies to the message caption instead of the text.

    Examples:
        Use ``MessageHandler(filters.PHOTO & filters.CaptionRegex(r'help'), callback)``
        to capture all photos with caption containing the word 'help'.

    Note:
        This filter will not work on simple text messages, but only on media with caption.

    Args:
        pattern (:obj:`str` | :obj:`re.Pattern`): The regex pattern.
    """

    __slots__ = ('pattern',)
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
    __slots__ = ()
    name = 'Filters.reply'

    def filter(self, message: Message) -> bool:
        return bool(message.reply_to_message)


REPLY = _Reply()
"""Messages that are a reply to another message."""


class _Audio(MessageFilter):
    __slots__ = ()
    name = 'Filters.audio'

    def filter(self, message: Message) -> bool:
        return bool(message.audio)


AUDIO = _Audio()
"""Messages that contain :class:`telegram.Audio`."""


class Document(MessageFilter):
    __slots__ = ()
    name = 'Filters.document'

    class Category(MessageFilter):
        """Filters documents by their category in the mime-type attribute.

        Note:
            This Filter only filters by the mime_type of the document,
                it doesn't check the validity of the document.
            The user can manipulate the mime-type of a message and
                send media with wrong types that don't fit to this handler.

        Example:
            ``filters.Document.Category('audio/')`` returns :obj:`True` for all types
            of audio sent as a file, for example ``'audio/mpeg'`` or ``'audio/x-wav'``.
        """

        __slots__ = ('_category',)

        def __init__(self, category: Optional[str]):
            """Initialize the category you want to filter

            Args:
                category (str, optional): category of the media you want to filter
            """
            self._category = category
            self.name = f"Filters.document.category('{self._category}')"

        def filter(self, message: Message) -> bool:
            """"""  # remove method from docs
            if message.document:
                return message.document.mime_type.startswith(self._category)
            return False

    APPLICATION = Category('application/')
    AUDIO = Category('audio/')
    IMAGE = Category('image/')
    VIDEO = Category('video/')
    TEXT = Category('text/')

    class MimeType(MessageFilter):
        """This Filter filters documents by their mime-type attribute

        Note:
            This Filter only filters by the mime_type of the document,
                it doesn't check the validity of document.
            The user can manipulate the mime-type of a message and
                send media with wrong types that don't fit to this handler.

        Example:
            ``filters.Document.MimeType('audio/mpeg')`` filters all audio in mp3 format.
        """

        __slots__ = ('mimetype',)

        def __init__(self, mimetype: Optional[str]):
            self.mimetype = mimetype
            self.name = f"Filters.document.mime_type('{self.mimetype}')"

        def filter(self, message: Message) -> bool:
            """"""  # remove method from docs
            if message.document:
                return message.document.mime_type == self.mimetype
            return False

    # TODO: Change this to mimetypes.types_map
    APK = MimeType('application/vnd.android.package-archive')
    DOC = MimeType('application/msword')
    DOCX = MimeType('application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    EXE = MimeType('application/x-ms-dos-executable')
    MP4 = MimeType('video/mp4')
    GIF = MimeType('image/gif')
    JPG = MimeType('image/jpeg')
    MP3 = MimeType('audio/mpeg')
    PDF = MimeType('application/pdf')
    PY = MimeType('text/x-python')
    SVG = MimeType('image/svg+xml')
    TXT = MimeType('text/plain')
    TARGZ = MimeType('application/x-compressed-tar')
    WAV = MimeType('audio/x-wav')
    XML = MimeType('application/xml')
    ZIP = MimeType('application/zip')

    class FileExtension(MessageFilter):
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
            * ``filters.Document.FileExtension("jpg")``
              filters files with extension ``".jpg"``.
            * ``filters.Document.FileExtension(".jpg")``
              filters files with extension ``"..jpg"``.
            * ``filters.Document.FileExtension("Dockerfile", case_sensitive=True)``
              filters files with extension ``".Dockerfile"`` minding the case.
            * ``filters.Document.FileExtension(None)``
              filters files without a dot in the filename.
        """

        __slots__ = ('_file_extension', 'is_case_sensitive')

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
                self._file_extension = None
                self.name = "Filters.document.file_extension(None)"
            elif self.is_case_sensitive:
                self._file_extension = f".{file_extension}"
                self.name = (
                    f"Filters.document.file_extension({file_extension!r}," " case_sensitive=True)"
                )
            else:
                self._file_extension = f".{file_extension}".lower()
                self.name = f"Filters.document.file_extension({file_extension.lower()!r})"

        def filter(self, message: Message) -> bool:
            """"""  # remove method from docs
            if message.document is None:
                return False
            if self._file_extension is None:
                return "." not in message.document.file_name
            if self.is_case_sensitive:
                filename = message.document.file_name
            else:
                filename = message.document.file_name.lower()
            return filename.endswith(self._file_extension)

    def filter(self, message: Message) -> bool:
        return bool(message.document)


DOCUMENT = Document
"""
    Subset for messages containing a document/file.

    Examples:
        Use these filters like: ``filters.Document.MP3``,
        ``filters.Document.MimeType("text/plain")`` etc. Or use just
        ``filters.DOCUMENT`` for all document messages.

    Attributes:
        Category: Filters documents by their category in the mime-type attribute

            Note:
                This Filter only filters by the mime_type of the document,
                it doesn't check the validity of the document.
                The user can manipulate the mime-type of a message and
                send media with wrong types that don't fit to this handler.

            Example:
                ``filters.Document.Category('audio/')`` filters all types
                of audio sent as file, for example 'audio/mpeg' or 'audio/x-wav'.
        APPLICATION: Same as ``filters.Document.Category("application")``.
        AUDIO: Same as ``filters.Document.Category("audio")``.
        IMAGE: Same as ``filters.Document.Category("image")``.
        VIDEO: Same as ``filters.Document.Category("video")``.
        TEXT: Same as ``filters.Document.Category("text")``.
        MimeType: Filters documents by their mime-type attribute

            Note:
                This Filter only filters by the mime_type of the document,
                it doesn't check the validity of document.

                The user can manipulate the mime-type of a message and
                send media with wrong types that don't fit to this handler.

            Example:
                ``filters.Document.MimeType('audio/mpeg')`` filters all audio in mp3 format.
        APK: Same as ``filters.Document.MimeType("application/vnd.android.package-archive")``.
        DOC: Same as ``filters.Document.MimeType("application/msword")``.
        DOCX: Same as ``filters.Document.MimeType("application/vnd.openxmlformats-\
    officedocument.wordprocessingml.document")``.
        EXE: Same as ``filters.Document.MimeType("application/x-ms-dos-executable")``.
        GIF: Same as ``filters.Document.MimeType("image/gif")``.
        MP4: Same as ``filters.Document.MimeType("video/mp4")``.
        JPG: Same as ``filters.Document.MimeType("image/jpeg")``.
        MP3: Same as ``filters.Document.MimeType("audio/mpeg")``.
        PDF: Same as ``filters.Document.MimeType("application/pdf")``.
        PY: Same as ``filters.Document.MimeType("text/x-python")``.
        SVG: Same as ``filters.Document.MimeType("image/svg+xml")``.
        TXT: Same as ``filters.Document.MimeType("text/plain")``.
        TARGZ: Same as ``filters.Document.MimeType("application/x-compressed-tar")``.
        WAV: Same as ``filters.Document.MimeType("audio/x-wav")``.
        XML: Same as ``filters.Document.MimeType("application/xml")``.
        ZIP: Same as ``filters.Document.MimeType("application/zip")``.
        FileExtension: This filter filters documents by their file ending/extension.

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
                * ``filters.Document.FileExtension("jpg")``
                  filters files with extension ``".jpg"``.
                * ``filters.Document.FileExtension(".jpg")``
                  filters files with extension ``"..jpg"``.
                * ``filters.Document.FileExtension("Dockerfile", case_sensitive=True)``
                  filters files with extension ``".Dockerfile"`` minding the case.
                * ``filters.Document.FileExtension(None)``
                  filters files without a dot in the filename.
"""


class _Animation(MessageFilter):
    __slots__ = ()
    name = 'Filters.animation'

    def filter(self, message: Message) -> bool:
        return bool(message.animation)


ANIMATION = _Animation()
"""Messages that contain :class:`telegram.Animation`."""


class _Photo(MessageFilter):
    __slots__ = ()
    name = 'Filters.photo'

    def filter(self, message: Message) -> bool:
        return bool(message.photo)


PHOTO = _Photo()
"""Messages that contain :class:`telegram.PhotoSize`."""


class _Sticker(MessageFilter):
    __slots__ = ()
    name = 'Filters.sticker'

    def filter(self, message: Message) -> bool:
        return bool(message.sticker)


STICKER = _Sticker()
"""Messages that contain :class:`telegram.Sticker`."""


class _Video(MessageFilter):
    __slots__ = ()
    name = 'Filters.video'

    def filter(self, message: Message) -> bool:
        return bool(message.video)


VIDEO = _Video()
"""Messages that contain :class:`telegram.Video`."""


class _Voice(MessageFilter):
    __slots__ = ()
    name = 'Filters.voice'

    def filter(self, message: Message) -> bool:
        return bool(message.voice)


VOICE = _Voice()
"""Messages that contain :class:`telegram.Voice`."""


class _VideoNote(MessageFilter):
    __slots__ = ()
    name = 'Filters.video_note'

    def filter(self, message: Message) -> bool:
        return bool(message.video_note)


VIDEO_NOTE = _VideoNote()
"""Messages that contain :class:`telegram.VideoNote`."""


class _Contact(MessageFilter):
    __slots__ = ()
    name = 'Filters.contact'

    def filter(self, message: Message) -> bool:
        return bool(message.contact)


CONTACT = _Contact()
"""Messages that contain :class:`telegram.Contact`."""


class _Location(MessageFilter):
    __slots__ = ()
    name = 'Filters.location'

    def filter(self, message: Message) -> bool:
        return bool(message.location)


LOCATION = _Location()
"""Messages that contain :class:`telegram.Location`."""


class _Venue(MessageFilter):
    __slots__ = ()
    name = 'Filters.venue'

    def filter(self, message: Message) -> bool:
        return bool(message.venue)


VENUE = _Venue()
"""Messages that contain :class:`telegram.Venue`."""


# TODO: Test if filters.STATUS_UPDATE.CHAT_CREATED == filters.StatusUpdate.CHAT_CREATED
class StatusUpdate(UpdateFilter):
    """Subset for messages containing a status update.

    Examples:
        Use these filters like: ``filters.StatusUpdate.NEW_CHAT_MEMBERS`` etc. Or use just
        ``filters.STATUS_UPDATE`` for all status update messages.

    """

    __slots__ = ()

    class _NewChatMembers(MessageFilter):
        __slots__ = ()
        name = 'Filters.status_update.new_chat_members'

        def filter(self, message: Message) -> bool:
            return bool(message.new_chat_members)

    NEW_CHAT_MEMBERS = _NewChatMembers()
    """Messages that contain :attr:`telegram.Message.new_chat_members`."""

    class _LeftChatMember(MessageFilter):
        __slots__ = ()
        name = 'Filters.status_update.left_chat_member'

        def filter(self, message: Message) -> bool:
            return bool(message.left_chat_member)

    LEFT_CHAT_MEMBER = _LeftChatMember()
    """Messages that contain :attr:`telegram.Message.left_chat_member`."""

    class _NewChatTitle(MessageFilter):
        __slots__ = ()
        name = 'Filters.status_update.new_chat_title'

        def filter(self, message: Message) -> bool:
            return bool(message.new_chat_title)

    NEW_CHAT_TITLE = _NewChatTitle()
    """Messages that contain :attr:`telegram.Message.new_chat_title`."""

    class _NewChatPhoto(MessageFilter):
        __slots__ = ()
        name = 'Filters.status_update.new_chat_photo'

        def filter(self, message: Message) -> bool:
            return bool(message.new_chat_photo)

    NEW_CHAT_PHOTO = _NewChatPhoto()
    """Messages that contain :attr:`telegram.Message.new_chat_photo`."""

    class _DeleteChatPhoto(MessageFilter):
        __slots__ = ()
        name = 'Filters.status_update.delete_chat_photo'

        def filter(self, message: Message) -> bool:
            return bool(message.delete_chat_photo)

    DELETE_CHAT_PHOTO = _DeleteChatPhoto()
    """Messages that contain :attr:`telegram.Message.delete_chat_photo`."""

    class _ChatCreated(MessageFilter):
        __slots__ = ()
        name = 'Filters.status_update.chat_created'

        def filter(self, message: Message) -> bool:
            return bool(
                message.group_chat_created
                or message.supergroup_chat_created
                or message.channel_chat_created
            )

    CHAT_CREATED = _ChatCreated()
    """Messages that contain :attr:`telegram.Message.group_chat_created`,
        :attr: `telegram.Message.supergroup_chat_created` or
        :attr: `telegram.Message.channel_chat_created`."""

    class _MessageAutoDeleteTimerChanged(MessageFilter):
        __slots__ = ()
        # TODO: fix the below and its doc
        name = 'MessageAutoDeleteTimerChanged'

        def filter(self, message: Message) -> bool:
            return bool(message.message_auto_delete_timer_changed)

    MESSAGE_AUTO_DELETE_TIMER_CHANGED = _MessageAutoDeleteTimerChanged()
    """Messages that contain :attr:`message_auto_delete_timer_changed`"""

    class _Migrate(MessageFilter):
        __slots__ = ()
        name = 'Filters.status_update.migrate'

        def filter(self, message: Message) -> bool:
            return bool(message.migrate_from_chat_id or message.migrate_to_chat_id)

    MIGRATE = _Migrate()
    """Messages that contain :attr:`telegram.Message.migrate_from_chat_id` or
        :attr:`telegram.Message.migrate_to_chat_id`."""

    class _PinnedMessage(MessageFilter):
        __slots__ = ()
        name = 'Filters.status_update.pinned_message'

        def filter(self, message: Message) -> bool:
            return bool(message.pinned_message)

    PINNED_MESSAGE = _PinnedMessage()
    """Messages that contain :attr:`telegram.Message.pinned_message`."""

    class _ConnectedWebsite(MessageFilter):
        __slots__ = ()
        name = 'Filters.status_update.connected_website'

        def filter(self, message: Message) -> bool:
            return bool(message.connected_website)

    CONNECTED_WEBSITE = _ConnectedWebsite()
    """Messages that contain :attr:`telegram.Message.connected_website`."""

    class _ProximityAlertTriggered(MessageFilter):
        __slots__ = ()
        name = 'Filters.status_update.proximity_alert_triggered'

        def filter(self, message: Message) -> bool:
            return bool(message.proximity_alert_triggered)

    PROXIMITY_ALERT_TRIGGERED = _ProximityAlertTriggered()
    """Messages that contain :attr:`telegram.Message.proximity_alert_triggered`."""

    class _VoiceChatScheduled(MessageFilter):
        __slots__ = ()
        name = 'Filters.status_update.voice_chat_scheduled'

        def filter(self, message: Message) -> bool:
            return bool(message.voice_chat_scheduled)

    VOICE_CHAT_SCHEDULED = _VoiceChatScheduled()
    """Messages that contain :attr:`telegram.Message.voice_chat_scheduled`."""

    class _VoiceChatStarted(MessageFilter):
        __slots__ = ()
        name = 'Filters.status_update.voice_chat_started'

        def filter(self, message: Message) -> bool:
            return bool(message.voice_chat_started)

    VOICE_CHAT_STARTED = _VoiceChatStarted()
    """Messages that contain :attr:`telegram.Message.voice_chat_started`."""

    class _VoiceChatEnded(MessageFilter):
        __slots__ = ()
        name = 'Filters.status_update.voice_chat_ended'

        def filter(self, message: Message) -> bool:
            return bool(message.voice_chat_ended)

    VOICE_CHAT_ENDED = _VoiceChatEnded()
    """Messages that contain :attr:`telegram.Message.voice_chat_ended`."""

    class _VoiceChatParticipantsInvited(MessageFilter):
        __slots__ = ()
        name = 'Filters.status_update.voice_chat_participants_invited'

        def filter(self, message: Message) -> bool:
            return bool(message.voice_chat_participants_invited)

    VOICE_CHAT_PARTICIPANTS_INVITED = _VoiceChatParticipantsInvited()
    """Messages that contain :attr:`telegram.Message.voice_chat_participants_invited`."""

    name = 'Filters.status_update'

    def filter(self, update: Update) -> bool:
        return bool(
            self.NEW_CHAT_MEMBERS(update)
            or self.LEFT_CHAT_MEMBER(update)
            or self.NEW_CHAT_TITLE(update)
            or self.NEW_CHAT_PHOTO(update)
            or self.DELETE_CHAT_PHOTO(update)
            or self.CHAT_CREATED(update)
            or self.MESSAGE_AUTO_DELETE_TIMER_CHANGED(update)
            or self.MIGRATE(update)
            or self.PINNED_MESSAGE(update)
            or self.CONNECTED_WEBSITE(update)
            or self.PROXIMITY_ALERT_TRIGGERED(update)
            or self.VOICE_CHAT_SCHEDULED(update)
            or self.VOICE_CHAT_STARTED(update)
            or self.VOICE_CHAT_ENDED(update)
            or self.VOICE_CHAT_PARTICIPANTS_INVITED(update)
        )


STATUS_UPDATE = StatusUpdate()
"""Subset for messages containing a status update.

Examples:
    Use these filters like: ``filters.StatusUpdate.NEW_CHAT_MEMBERS`` etc. Or use just
    ``filters.STATUS_UPDATE`` for all status update messages.

Attributes:
    CHAT_CREATED: Messages that contain
        :attr:`telegram.Message.group_chat_created`,
        :attr:`telegram.Message.supergroup_chat_created` or
        :attr:`telegram.Message.channel_chat_created`.
    CONNECTED_WEBSITE: Messages that contain
        :attr:`telegram.Message.connected_website`.
    DELETE_CHAT_PHOTO: Messages that contain
        :attr:`telegram.Message.delete_chat_photo`.
    LEFT_CHAT_MEMBER: Messages that contain
        :attr:`telegram.Message.left_chat_member`.
    MIGRATE: Messages that contain
        :attr:`telegram.Message.migrate_to_chat_id` or
        :attr:`telegram.Message.migrate_from_chat_id`.
    NEW_CHAT_MEMBERS: Messages that contain
        :attr:`telegram.Message.new_chat_members`.
    NEW_CHAT_PHOTO: Messages that contain
        :attr:`telegram.Message.new_chat_photo`.
    NEW_CHAT_TITLE: Messages that contain
        :attr:`telegram.Message.new_chat_title`.
    MESSAGE_AUTO_DELETE_TIMER_CHANGED: Messages that contain
        :attr:`message_auto_delete_timer_changed`.

        .. versionadded:: 13.4
    PINNED_MESSAGE: Messages that contain
        :attr:`telegram.Message.pinned_message`.
    PROXIMITY_ALERT_TRIGGERED: Messages that contain
        :attr:`telegram.Message.proximity_alert_triggered`.
    VOICE_CHAT_SCHEDULED: Messages that contain
        :attr:`telegram.Message.voice_chat_scheduled`.

        .. versionadded:: 13.5
    VOICE_CHAT_STARTED: Messages that contain
        :attr:`telegram.Message.voice_chat_started`.

        .. versionadded:: 13.4
    VOICE_CHAT_ENDED: Messages that contain
        :attr:`telegram.Message.voice_chat_ended`.

        .. versionadded:: 13.4
    VOICE_CHAT_PARTICIPANTS_INVITED: Messages that contain
        :attr:`telegram.Message.voice_chat_participants_invited`.

        .. versionadded:: 13.4

"""


class _Forwarded(MessageFilter):
    __slots__ = ()
    name = 'Filters.forwarded'

    def filter(self, message: Message) -> bool:
        return bool(message.forward_date)


FORWARDED = _Forwarded()
"""Messages that are forwarded."""


class _Game(MessageFilter):
    __slots__ = ()
    name = 'Filters.game'

    def filter(self, message: Message) -> bool:
        return bool(message.game)


GAME = _Game()
"""Messages that contain :class:`telegram.Game`."""


class Entity(MessageFilter):
    """
    Filters messages to only allow those which have a :class:`telegram.MessageEntity`
    where their :class:`~telegram.MessageEntity.type` matches `entity_type`.

    Examples:
        Example ``MessageHandler(filters.Entity("hashtag"), callback_method)``

    Args:
        entity_type (:obj:`str`): Entity type to check for. All types can be found as constants
            in :class:`telegram.MessageEntity`.

    """

    __slots__ = ('entity_type',)

    def __init__(self, entity_type: str):
        self.entity_type = entity_type
        self.name = f'Filters.entity({self.entity_type})'

    def filter(self, message: Message) -> bool:
        """"""  # remove method from docs
        return any(entity.type == self.entity_type for entity in message.entities)


class CaptionEntity(MessageFilter):
    """
    Filters media messages to only allow those which have a :class:`telegram.MessageEntity`
    where their :class:`~telegram.MessageEntity.type` matches `entity_type`.

    Examples:
        Example ``MessageHandler(filters.CaptionEntity("hashtag"), callback_method)``

    Args:
        entity_type (:obj:`str`): Caption Entity type to check for. All types can be found as constants
            in :class:`telegram.MessageEntity`.

    """

    __slots__ = ('entity_type',)

    def __init__(self, entity_type: str):
        self.entity_type = entity_type
        self.name = f'Filters.caption_entity({self.entity_type})'

    def filter(self, message: Message) -> bool:
        """"""  # remove method from docs
        return any(entity.type == self.entity_type for entity in message.caption_entities)


class CHAT_TYPE:  # A convenience namespace for Chat types.
    """Subset for filtering the type of chat.

    Examples:
        Use these filters like: ``filters.CHAT_TYPE.CHANNEL`` or
        ``filters.CHAT_TYPE.SUPERGROUP`` etc.

    Attributes:
        CHANNEL: Updates from channel.
        GROUP: Updates from group.
        SUPERGROUP: Updates from supergroup.
        GROUPS: Updates from group *or* supergroup.
        PRIVATE: Updates sent in private chat.
    """

    __slots__ = ()
    name = 'Filters.chat_type'

    class _Channel(MessageFilter):
        __slots__ = ()
        name = 'Filters.chat_type.channel'

        def filter(self, message: Message) -> bool:
            return message.chat.type == TGChat.CHANNEL

    CHANNEL = _Channel()

    class _Group(MessageFilter):
        __slots__ = ()
        name = 'Filters.chat_type.group'

        def filter(self, message: Message) -> bool:
            return message.chat.type == TGChat.GROUP

    GROUP = _Group()

    class _SuperGroup(MessageFilter):
        __slots__ = ()
        name = 'Filters.chat_type.supergroup'

        def filter(self, message: Message) -> bool:
            return message.chat.type == TGChat.SUPERGROUP

    SUPERGROUP = _SuperGroup()

    class _Groups(MessageFilter):
        __slots__ = ()
        name = 'Filters.chat_type.groups'

        def filter(self, message: Message) -> bool:
            return message.chat.type in [TGChat.GROUP, TGChat.SUPERGROUP]

    GROUPS = _Groups()

    class _Private(MessageFilter):
        __slots__ = ()
        name = 'Filters.chat_type.private'

        def filter(self, message: Message) -> bool:
            return message.chat.type == TGChat.PRIVATE

    PRIVATE = _Private()


class _ChatUserBaseFilter(MessageFilter, ABC):
    __slots__ = (
        'chat_id_name',
        'username_name',
        'allow_empty',
        '__lock',
        '_chat_ids',
        '_usernames',
    )

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
    def get_chat_or_user(self, message: Message) -> Union[TGChat, TGUser, None]:
        ...

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


class User(_ChatUserBaseFilter):
    # pylint: disable=useless-super-delegation
    """Filters messages to allow only those which are from specified user ID(s) or
    username(s).

    Examples:
        ``MessageHandler(filters.User(1234), callback_method)``

    Warning:
        :attr:`user_ids` will give a *copy* of the saved user ids as :class:`frozenset`. This
        is to ensure thread safety. To add/remove a user, you should use :meth:`add_usernames`,
        :meth:`add_user_ids`, :meth:`remove_usernames` and :meth:`remove_user_ids`. Only update
        the entire set by ``filter.user_ids/usernames = new_set``, if you are entirely sure
        that it is not causing race conditions, as this will complete replace the current set
        of allowed users.

    Args:
        user_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
            Which user ID(s) to allow through.
        username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
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

    __slots__ = ()

    def __init__(
        self,
        user_id: SLT[int] = None,
        username: SLT[str] = None,
        allow_empty: bool = False,
    ):
        super().__init__(chat_id=user_id, username=username, allow_empty=allow_empty)
        self.chat_id_name = 'user_id'

    def get_chat_or_user(self, message: Message) -> Optional[TGUser]:
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
            username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
                Which username(s) to allow through.
                Leading ``'@'`` s in usernames will be discarded.
        """
        return super().add_usernames(username)

    def add_user_ids(self, user_id: SLT[int]) -> None:
        """
        Add one or more users to the allowed user ids.

        Args:
            user_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which user ID(s) to allow through.
        """
        return super().add_chat_ids(user_id)

    def remove_usernames(self, username: SLT[str]) -> None:
        """
        Remove one or more users from allowed usernames.

        Args:
            username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
                Which username(s) to disallow through.
                Leading ``'@'`` s in usernames will be discarded.
        """
        return super().remove_usernames(username)

    def remove_user_ids(self, user_id: SLT[int]) -> None:
        """
        Remove one or more users from allowed user ids.

        Args:
            user_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which user ID(s) to disallow through.
        """
        return super().remove_chat_ids(user_id)


class ViaBot(_ChatUserBaseFilter):
    # pylint: disable=useless-super-delegation
    """Filters messages to allow only those which are from specified via_bot ID(s) or
    username(s).

    Examples:
        ``MessageHandler(filters.ViaBot(1234), callback_method)``

    Warning:
        :attr:`bot_ids` will give a *copy* of the saved bot ids as :class:`frozenset`. This
        is to ensure thread safety. To add/remove a bot, you should use :meth:`add_usernames`,
        :meth:`add_bot_ids`, :meth:`remove_usernames` and :meth:`remove_bot_ids`. Only update
        the entire set by ``filter.bot_ids/usernames = new_set``, if you are entirely sure
        that it is not causing race conditions, as this will complete replace the current set
        of allowed bots.

    Args:
        bot_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
            Which bot ID(s) to allow through.
        username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
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

    __slots__ = ()

    def __init__(
        self,
        bot_id: SLT[int] = None,
        username: SLT[str] = None,
        allow_empty: bool = False,
    ):
        super().__init__(chat_id=bot_id, username=username, allow_empty=allow_empty)
        self.chat_id_name = 'bot_id'

    def get_chat_or_user(self, message: Message) -> Optional[TGUser]:
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
            username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
                Which username(s) to allow through.
                Leading ``'@'`` s in usernames will be discarded.
        """
        return super().add_usernames(username)

    def add_bot_ids(self, bot_id: SLT[int]) -> None:
        """
        Add one or more users to the allowed user ids.

        Args:
            bot_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which bot ID(s) to allow through.
        """
        return super().add_chat_ids(bot_id)

    def remove_usernames(self, username: SLT[str]) -> None:
        """
        Remove one or more users from allowed usernames.

        Args:
            username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
                Which username(s) to disallow through.
                Leading ``'@'`` s in usernames will be discarded.
        """
        return super().remove_usernames(username)

    def remove_bot_ids(self, bot_id: SLT[int]) -> None:
        """
        Remove one or more users from allowed user ids.

        Args:
            bot_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which bot ID(s) to disallow through.
        """
        return super().remove_chat_ids(bot_id)


class Chat(_ChatUserBaseFilter):
    # pylint: disable=useless-super-delegation
    """Filters messages to allow only those which are from a specified chat ID or username.

    Examples:
        ``MessageHandler(filters.Chat(-1234), callback_method)``

    Warning:
        :attr:`chat_ids` will give a *copy* of the saved chat ids as :class:`frozenset`. This
        is to ensure thread safety. To add/remove a chat, you should use :meth:`add_usernames`,
        :meth:`add_chat_ids`, :meth:`remove_usernames` and :meth:`remove_chat_ids`. Only update
        the entire set by ``filter.chat_ids/usernames = new_set``, if you are entirely sure
        that it is not causing race conditions, as this will complete replace the current set
        of allowed chats.

    Args:
        chat_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
            Which chat ID(s) to allow through.
        username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
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

    __slots__ = ()

    def get_chat_or_user(self, message: Message) -> Optional[TGChat]:
        return message.chat

    def add_usernames(self, username: SLT[str]) -> None:
        """
        Add one or more chats to the allowed usernames.

        Args:
            username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
                Which username(s) to allow through.
                Leading ``'@'`` s in usernames will be discarded.
        """
        return super().add_usernames(username)

    def add_chat_ids(self, chat_id: SLT[int]) -> None:
        """
        Add one or more chats to the allowed chat ids.

        Args:
            chat_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which chat ID(s) to allow through.
        """
        return super().add_chat_ids(chat_id)

    def remove_usernames(self, username: SLT[str]) -> None:
        """
        Remove one or more chats from allowed usernames.

        Args:
            username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
                Which username(s) to disallow through.
                Leading ``'@'`` s in usernames will be discarded.
        """
        return super().remove_usernames(username)

    def remove_chat_ids(self, chat_id: SLT[int]) -> None:
        """
        Remove one or more chats from allowed chat ids.

        Args:
            chat_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which chat ID(s) to disallow through.
        """
        return super().remove_chat_ids(chat_id)


class ForwardedFrom(_ChatUserBaseFilter):
    # pylint: disable=useless-super-delegation
    """Filters messages to allow only those which are forwarded from the specified chat ID(s)
    or username(s) based on :attr:`telegram.Message.forward_from` and
    :attr:`telegram.Message.forward_from_chat`.

    .. versionadded:: 13.5

    Examples:
        ``MessageHandler(filters.ForwardedFrom(chat_id=1234), callback_method)``

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
        chat_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
            Which chat/user ID(s) to allow through.
        username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
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

    __slots__ = ()

    def get_chat_or_user(self, message: Message) -> Union[TGUser, TGChat, None]:
        return message.forward_from or message.forward_from_chat

    def add_usernames(self, username: SLT[str]) -> None:
        """
        Add one or more chats to the allowed usernames.

        Args:
            username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
                Which username(s) to allow through.
                Leading ``'@'`` s in usernames will be discarded.
        """
        return super().add_usernames(username)

    def add_chat_ids(self, chat_id: SLT[int]) -> None:
        """
        Add one or more chats to the allowed chat ids.

        Args:
            chat_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which chat/user ID(s) to allow through.
        """
        return super().add_chat_ids(chat_id)

    def remove_usernames(self, username: SLT[str]) -> None:
        """
        Remove one or more chats from allowed usernames.

        Args:
            username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
                Which username(s) to disallow through.
                Leading ``'@'`` s in usernames will be discarded.
        """
        return super().remove_usernames(username)

    def remove_chat_ids(self, chat_id: SLT[int]) -> None:
        """
        Remove one or more chats from allowed chat ids.

        Args:
            chat_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which chat/user ID(s) to disallow through.
        """
        return super().remove_chat_ids(chat_id)


# TODO: Add SENDER_CHAT as shortcut for SenderChat(allow_empty=True)
class SenderChat(_ChatUserBaseFilter):
    # pylint: disable=useless-super-delegation
    """Filters messages to allow only those which are from a specified sender chats chat ID or
    username.

    Examples:
        * To filter for messages forwarded to a discussion group from a channel with ID
          ``-1234``, use ``MessageHandler(filters.SenderChat(-1234), callback_method)``.
        * To filter for messages of anonymous admins in a super group with username
          ``@anonymous``, use
          ``MessageHandler(filters.SenderChat(username='anonymous'), callback_method)``.
        * To filter for messages forwarded to a discussion group from *any* channel, use
          ``MessageHandler(filters.SenderChat.CHANNEL, callback_method)``.
        * To filter for messages of anonymous admins in *any* super group, use
          ``MessageHandler(filters.SenderChat.SUPERGROUP, callback_method)``.

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
        chat_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
            Which sender chat chat ID(s) to allow through.
        username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
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
        SUPERGROUP: Messages whose sender chat is a super group.

            Examples:
                ``filters.SenderChat.SUPERGROUP``
        CHANNEL: Messages whose sender chat is a channel.

            Examples:
                ``filters.SenderChat.CHANNEL``

    """

    __slots__ = ()

    def get_chat_or_user(self, message: Message) -> Optional[TGChat]:
        return message.sender_chat

    def add_usernames(self, username: SLT[str]) -> None:
        """
        Add one or more sender chats to the allowed usernames.

        Args:
            username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
                Which sender chat username(s) to allow through.
                Leading ``'@'`` s in usernames will be discarded.
        """
        return super().add_usernames(username)

    def add_chat_ids(self, chat_id: SLT[int]) -> None:
        """
        Add one or more sender chats to the allowed chat ids.

        Args:
            chat_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which sender chat ID(s) to allow through.
        """
        return super().add_chat_ids(chat_id)

    def remove_usernames(self, username: SLT[str]) -> None:
        """
        Remove one or more sender chats from allowed usernames.

        Args:
            username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
                Which sender chat username(s) to disallow through.
                Leading ``'@'`` s in usernames will be discarded.
        """
        return super().remove_usernames(username)

    def remove_chat_ids(self, chat_id: SLT[int]) -> None:
        """
        Remove one or more sender chats from allowed chat ids.

        Args:
            chat_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which sender chat ID(s) to disallow through.
        """
        return super().remove_chat_ids(chat_id)

    class _SUPERGROUP(MessageFilter):
        __slots__ = ()

        def filter(self, message: Message) -> bool:
            if message.sender_chat:
                return message.sender_chat.type == TGChat.SUPERGROUP
            return False

    class _CHANNEL(MessageFilter):
        __slots__ = ()

        def filter(self, message: Message) -> bool:
            if message.sender_chat:
                return message.sender_chat.type == TGChat.CHANNEL
            return False

    SUPERGROUP = _SUPERGROUP()
    CHANNEL = _CHANNEL()


class _Invoice(MessageFilter):
    __slots__ = ()
    name = 'Filters.invoice'

    def filter(self, message: Message) -> bool:
        return bool(message.invoice)


INVOICE = _Invoice()
"""Messages that contain :class:`telegram.Invoice`."""


class _SuccessfulPayment(MessageFilter):
    __slots__ = ()
    name = 'Filters.successful_payment'

    def filter(self, message: Message) -> bool:
        return bool(message.successful_payment)


SUCCESSFUL_PAYMENT = _SuccessfulPayment()
"""Messages that confirm a :class:`telegram.SuccessfulPayment`."""


class _PassportData(MessageFilter):
    __slots__ = ()
    name = 'Filters.passport_data'

    def filter(self, message: Message) -> bool:
        return bool(message.passport_data)


PASSPORT_DATA = _PassportData()
"""Messages that contain a :class:`telegram.PassportData`"""


class _Poll(MessageFilter):
    __slots__ = ()
    name = 'Filters.poll'

    def filter(self, message: Message) -> bool:
        return bool(message.poll)


POLL = _Poll()
"""Messages that contain a :class:`telegram.Poll`."""


class _Dice(_DiceEmoji):
    __slots__ = ()
    # Partials so its easier for users to pass dice values without worrying about anything else.
    DICE = _DiceEmoji(DE.DICE)
    Dice = partial(_DiceEmoji, emoji=DE.DICE)

    DARTS = _DiceEmoji(DE.DARTS)
    Darts = partial(_DiceEmoji, emoji=DE.DARTS)

    BASKETBALL = _DiceEmoji(DE.BASKETBALL)
    Basketball = partial(_DiceEmoji, emoji=DE.BASKETBALL)

    FOOTBALL = _DiceEmoji(DE.FOOTBALL)
    Football = partial(_DiceEmoji, emoji=DE.FOOTBALL)

    SLOT_MACHINE = _DiceEmoji(DE.SLOT_MACHINE)
    SlotMachine = partial(_DiceEmoji, emoji=DE.SLOT_MACHINE)

    BOWLING = _DiceEmoji(DE.BOWLING)
    Bowling = partial(_DiceEmoji, emoji=DE.BOWLING)


DICE = _Dice()
"""Dice Messages. If an integer or a list of integers is passed, it filters messages to only
allow those whose dice value is appearing in the given list.

Examples:
    To allow any dice message, simply use
    ``MessageHandler(filters.DICE, callback_method)``.

    To allow only dice messages with the emoji 🎲, but any value, use
    ``MessageHandler(filters.DICE.DICE, callback_method)``.

    To allow only dice messages with the emoji 🎯 and with value 6, use
    ``MessageHandler(filters.DICE.Darts(6), callback_method)``.

    To allow only dice messages with the emoji ⚽ and with value 5 `or` 6, use
    ``MessageHandler(filters.DICE.Football([5, 6]), callback_method)``.

Note:
    Dice messages don't have text. If you want to filter either text or dice messages, use
    ``filters.TEXT | filters.DICE``.

Args:
    values (:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
        Which values to allow. If not specified, will allow the specified dice message.

Attributes:
    DICE: Dice messages with the emoji 🎲. Matches any dice value.
    Dice: Dice messages with the emoji 🎲. Supports passing a list of integers.
    DARTS: Dice messages with the emoji 🎯. Matches any dice value.
    Darts: Dice messages with the emoji 🎯. Supports passing a list of integers.
    BASKETBALL: Dice messages with the emoji 🏀. Matches any dice value.
    Basketball: Dice messages with the emoji 🏀. Supports passing a list of integers.
    FOOTBALL: Dice messages with the emoji ⚽. Matches any dice value.
    Football: Dice messages with the emoji ⚽. Supports passing a list of integers.
    SLOT_MACHINE: Dice messages with the emoji 🎰. Matches any dice value.
    SlotMachine: Dice messages with the emoji 🎰. Supports passing a list of integers.
    BOWLING: Dice messages with the emoji 🎳. Matches any dice value.
    Bowling: Dice messages with the emoji 🎳. Supports passing a list of integers.

    .. versionadded:: 13.4
"""


class Language(MessageFilter):
    """Filters messages to only allow those which are from users with a certain language code.

    Note:
        According to official Telegram Bot API documentation, not every single user has the
        `language_code` attribute. Do not count on this filter working on all users.

    Examples:
        ``MessageHandler(filters.Language("en"), callback_method)``

    Args:
        lang (:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`]):
            Which language code(s) to allow through.
            This will be matched using :obj:`str.startswith` meaning that
            'en' will match both 'en_US' and 'en_GB'.

    """

    __slots__ = ('lang',)

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


class _Attachment(MessageFilter):
    __slots__ = ()

    name = 'Filters.attachment'

    def filter(self, message: Message) -> bool:
        return bool(message.effective_attachment)


ATTACHMENT = _Attachment()
"""Messages that contain :meth:`telegram.Message.effective_attachment`.

.. versionadded:: 13.6"""


class UpdateType(UpdateFilter):
    __slots__ = ()
    name = 'Filters.update'

    class _Message(UpdateFilter):
        __slots__ = ()
        name = 'Filters.update.message'

        def filter(self, update: Update) -> bool:
            return update.message is not None

    MESSAGE = _Message()

    class _EditedMessage(UpdateFilter):
        __slots__ = ()
        name = 'Filters.update.edited_message'

        def filter(self, update: Update) -> bool:
            return update.edited_message is not None

    EDITED_MESSAGE = _EditedMessage()

    class _Messages(UpdateFilter):
        __slots__ = ()
        name = 'Filters.update.messages'

        def filter(self, update: Update) -> bool:
            return update.message is not None or update.edited_message is not None

    MESSAGES = _Messages()

    class _ChannelPost(UpdateFilter):
        __slots__ = ()
        name = 'Filters.update.channel_post'

        def filter(self, update: Update) -> bool:
            return update.channel_post is not None

    CHANNEL_POST = _ChannelPost()

    class _EditedChannelPost(UpdateFilter):
        __slots__ = ()
        name = 'Filters.update.edited_channel_post'

        def filter(self, update: Update) -> bool:
            return update.edited_channel_post is not None

    EDITED_CHANNEL_POST = _EditedChannelPost()

    class _Edited(UpdateFilter):
        __slots__ = ()
        name = 'Filters.update.edited'

        def filter(self, update: Update) -> bool:
            return update.edited_message is not None or update.edited_channel_post is not None

    EDITED = _Edited()

    class _ChannelPosts(UpdateFilter):
        __slots__ = ()
        name = 'Filters.update.channel_posts'

        def filter(self, update: Update) -> bool:
            return update.channel_post is not None or update.edited_channel_post is not None

    CHANNEL_POSTS = _ChannelPosts()

    def filter(self, update: Update) -> bool:
        return bool(self.MESSAGES(update) or self.CHANNEL_POSTS(update))


UPDATE = UpdateType()
"""Subset for filtering the type of update.

Examples:
    Use these filters like: ``filters.UpdateType.MESSAGE`` or
    ``filters.UpdateType.CHANNEL_POSTS`` etc. Or use just ``filters.UPDATE`` for all
    types.

Attributes:
    MESSAGE: Updates with :attr:`telegram.Update.message`
    EDITED_MESSAGE: Updates with :attr:`telegram.Update.edited_message`
    MESSAGES: Updates with either :attr:`telegram.Update.message` or
        :attr:`telegram.Update.edited_message`
    CHANNEL_POST: Updates with :attr:`telegram.Update.channel_post`
    EDITED_CHANNEL_POST: Updates with
        :attr:`telegram.Update.edited_channel_post`
    CHANNEL_POSTS: Updates with either :attr:`telegram.Update.channel_post` or
        :attr:`telegram.Update.edited_channel_post`
    EDITED: Updates with either :attr:`telegram.Update.edited_message` or
        :attr:`telegram.Update.edited_channel_post`
"""
