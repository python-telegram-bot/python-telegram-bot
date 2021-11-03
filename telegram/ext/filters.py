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
"""
This module contains filters for use with :class:`telegram.ext.MessageHandler` or
:class:`telegram.ext.CommandHandler`.

.. versionchanged:: 14.0

    #. Filters are no longer callable, if you're using a custom filter and are calling an existing
       filter, then switch to the new syntax: ``filters.{filter}.check_update(update)``.
    #. Removed the ``Filters`` class. You should now call filters directly from the module itself.
    #. The names of all filters has been updated:

        * Filters which are ready for use, e.g ``Filters.all`` are now capitalized, e.g
          ``filters.ALL``.
        * Filters which need to be initialized are now in CamelCase. E.g. ``filters.User(...)``.
        * Filters which do both (like ``Filters.text``) are now split as capitalized version
          ``filters.TEXT`` and CamelCase version ``filters.Text(...)``.

"""

import mimetypes
import re

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

from telegram import Chat as TGChat, Message, MessageEntity, Update, User as TGUser

from telegram._utils.types import SLT
from telegram.constants import DiceEmoji as DiceEmojiEnum

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

        With ``message.text == 'x'``, will only ever return the matches for the first filter,
        since the second one is never evaluated.


    If you want to create your own filters create a class inheriting from either
    :class:`MessageFilter` or :class:`UpdateFilter` and implement a ``filter()``
    method that returns a boolean: :obj:`True` if the message should be
    handled, :obj:`False` otherwise.
    Note that the filters work only as class instances, not actual class objects (so remember to
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
    def check_update(self, update: Update) -> Optional[Union[bool, DataDict]]:
        ...

    def __and__(self, other: 'BaseFilter') -> 'BaseFilter':
        return _MergedFilter(self, and_filter=other)

    def __or__(self, other: 'BaseFilter') -> 'BaseFilter':
        return _MergedFilter(self, or_filter=other)

    def __xor__(self, other: 'BaseFilter') -> 'BaseFilter':
        return _XORFilter(self, other)

    def __invert__(self) -> 'BaseFilter':
        return _InvertedFilter(self)

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
    to :meth:`filter` is :obj:`telegram.Update.effective_message`.

    Please see :class:`BaseFilter` for details on how to create custom filters.

    Attributes:
        name (:obj:`str`): Name for this filter. Defaults to the type of filter.
        data_filter (:obj:`bool`): Whether this filter is a data filter. A data filter should
            return a dict with lists. The dict will be merged with
            :class:`telegram.ext.CallbackContext`'s internal dict in most cases
            (depends on the handler).

    """

    __slots__ = ()

    def check_update(self, update: Update) -> Optional[Union[bool, DataDict]]:
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
    passed to :meth:`filter` is an instance of :class:`telegram.Update`, which allows to create
    filters like :attr:`filters.UpdateType.EDITED_MESSAGE`.

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

    def check_update(self, update: Update) -> Optional[Union[bool, DataDict]]:
        return self.filter(update)

    @abstractmethod
    def filter(self, update: Update) -> Optional[Union[bool, DataDict]]:
        """This method must be overwritten.

        Args:
            update (:class:`telegram.Update`): The update that is tested.

        Returns:
            :obj:`dict` or :obj:`bool`.

        """


class _InvertedFilter(UpdateFilter):
    """Represents a filter that has been inverted.

    Args:
        f: The filter to invert.

    """

    __slots__ = ('inv_filter',)

    def __init__(self, f: BaseFilter):
        self.inv_filter = f

    def filter(self, update: Update) -> bool:
        return not bool(self.inv_filter.check_update(update))

    @property
    def name(self) -> str:
        return f"<inverted {self.inv_filter}>"

    @name.setter
    def name(self, name: str) -> NoReturn:
        raise RuntimeError(f'Cannot set name for {self.__class__.__name__!r}')


class _MergedFilter(UpdateFilter):
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
        base_output = self.base_filter.check_update(update)
        # We need to check if the filters are data filters and if so return the merged data.
        # If it's not a data filter or an or_filter but no matches return bool
        if self.and_filter:
            # And filter needs to short circuit if base is falsy
            if base_output:
                comp_output = self.and_filter.check_update(update)
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

            comp_output = self.or_filter.check_update(update)
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
        raise RuntimeError(f'Cannot set name for {self.__class__.__name__!r}')


class _XORFilter(UpdateFilter):
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
        return self.merged_filter.check_update(update)

    @property
    def name(self) -> str:
        return f'<{self.base_filter} xor {self.xor_filter}>'

    @name.setter
    def name(self, name: str) -> NoReturn:
        raise RuntimeError(f'Cannot set name for {self.__class__.__name__!r}')


class _Dice(MessageFilter):
    __slots__ = ('emoji', 'values')

    def __init__(self, values: SLT[int] = None, emoji: DiceEmojiEnum = None):
        self.emoji = emoji
        self.values = [values] if isinstance(values, int) else values
        emoji_name = getattr(emoji, 'name', '')  # Can be e.g. BASKETBALL (see emoji enums)
        if emoji:  # for filters.Dice.BASKETBALL
            self.name = f"filters.Dice.{emoji_name}"
        elif values:  # for filters.Dice(4)
            self.name = f"filters.Dice({self.values})"
        else:
            self.name = "filters.Dice.ALL"
        if self.values and emoji:  # for filters.Dice.Dice(4)  SLOT_MACHINE -> SlotMachine
            self.name = f"filters.Dice.{emoji_name.title().replace('_', '')}({self.values})"

    def filter(self, message: Message) -> bool:
        if not message.dice:  # no dice
            return False

        if self.emoji:
            emoji_match = message.dice.emoji == self.emoji
            if self.values:
                return message.dice.value in self.values and emoji_match  # emoji and value
            return emoji_match  # emoji, no value
        return message.dice.value in self.values if self.values else True  # no emoji, only value


class _All(MessageFilter):
    __slots__ = ()
    name = 'filters.ALL'

    def filter(self, message: Message) -> bool:
        return True


ALL = _All()
"""All Messages."""


class Text(MessageFilter):
    """Text Messages. If a list of strings is passed, it filters messages to only allow those
    whose text is appearing in the given list.

    Examples:
        A simple use case for passing a list is to allow only messages that were sent by a
        custom :class:`telegram.ReplyKeyboardMarkup`::

            buttons = ['Start', 'Settings', 'Back']
            markup = ReplyKeyboardMarkup.from_column(buttons)
            ...
            MessageHandler(filters.Text(buttons), callback_method)

    .. seealso::
        :attr:`telegram.ext.filters.TEXT`


    Note:
        * Dice messages don't have text. If you want to filter either text or dice messages, use
          ``filters.TEXT | filters.Dice.ALL``.
        * Messages containing a command are accepted by this filter. Use
          ``filters.TEXT & (~filters.COMMAND)``, if you want to filter only text messages without
          commands.

    Args:
        strings (List[:obj:`str`] | Tuple[:obj:`str`], optional): Which messages to allow. Only
            exact matches are allowed. If not specified, will allow any text message.
    """

    __slots__ = ('strings',)

    def __init__(self, strings: Union[List[str], Tuple[str, ...]] = None):
        self.strings = strings
        self.name = f'filters.Text({strings})' if strings else 'filters.TEXT'

    def filter(self, message: Message) -> bool:
        if self.strings is None:
            return bool(message.text)
        return message.text in self.strings if message.text else False


TEXT = Text()
"""
Shortcut for :class:`telegram.ext.filters.Text()`.

Examples:
    To allow any text message, simply use ``MessageHandler(filters.TEXT, callback_method)``.
"""


class Caption(MessageFilter):
    """Messages with a caption. If a list of strings is passed, it filters messages to only
    allow those whose caption is appearing in the given list.

    Examples:
        ``MessageHandler(filters.Caption(['PTB rocks!', 'PTB'], callback_method_2)``

    .. seealso::
        :attr:`telegram.ext.filters.CAPTION`

    Args:
        strings (List[:obj:`str`] | Tuple[:obj:`str`], optional): Which captions to allow. Only
            exact matches are allowed. If not specified, will allow any message with a caption.
    """

    __slots__ = ('strings',)

    def __init__(self, strings: Union[List[str], Tuple[str, ...]] = None):
        self.strings = strings
        self.name = f'filters.Caption({strings})' if strings else 'filters.CAPTION'

    def filter(self, message: Message) -> bool:
        if self.strings is None:
            return bool(message.caption)
        return message.caption in self.strings if message.caption else False


CAPTION = Caption()
"""Shortcut for :class:`telegram.ext.filters.Caption()`.

Examples:
    To allow any caption, simply use ``MessageHandler(filters.CAPTION, callback_method)``.
"""


class Command(MessageFilter):
    """
    Messages with a :attr:`telegram.MessageEntity.BOT_COMMAND`. By default only allows
    messages `starting` with a bot command. Pass :obj:`False` to also allow messages that contain a
    bot command `anywhere` in the text.

    Examples:
        ``MessageHandler(filters.Command(False), command_anywhere_callback)``

    .. seealso::
        :attr:`telegram.ext.filters.COMMAND`.

    Note:
        :attr:`telegram.ext.filters.TEXT` also accepts messages containing a command.

    Args:
        only_start (:obj:`bool`, optional): Whether to only allow messages that `start` with a bot
            command. Defaults to :obj:`True`.
    """

    __slots__ = ('only_start',)

    def __init__(self, only_start: bool = True):
        self.only_start = only_start
        self.name = f'filters.Command({only_start})' if not only_start else 'filters.COMMAND'

    def filter(self, message: Message) -> bool:
        if not message.entities:
            return False

        first = message.entities[0]

        if self.only_start:
            return bool(first.type == MessageEntity.BOT_COMMAND and first.offset == 0)
        return bool(any(e.type == MessageEntity.BOT_COMMAND for e in message.entities))


COMMAND = Command()
"""Shortcut for :class:`telegram.ext.filters.Command()`.

Examples:
    To allow messages starting with a command use
    ``MessageHandler(filters.COMMAND, command_at_start_callback)``.
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
        self.pattern: Pattern = pattern
        self.name = f'filters.Regex({self.pattern})'

    def filter(self, message: Message) -> Optional[Dict[str, List[Match]]]:
        if message.text:
            match = self.pattern.search(message.text)
            if match:
                return {'matches': [match]}
        return {}


class CaptionRegex(MessageFilter):
    """
    Filters updates by searching for an occurrence of ``pattern`` in the message caption.

    This filter works similarly to :class:`Regex`, with the only exception being that
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
        self.pattern: Pattern = pattern
        self.name = f'filters.CaptionRegex({self.pattern})'

    def filter(self, message: Message) -> Optional[Dict[str, List[Match]]]:
        if message.caption:
            match = self.pattern.search(message.caption)
            if match:
                return {'matches': [match]}
        return {}


class _Reply(MessageFilter):
    __slots__ = ()
    name = 'filters.REPLY'

    def filter(self, message: Message) -> bool:
        return bool(message.reply_to_message)


REPLY = _Reply()
"""Messages that are a reply to another message."""


class _Audio(MessageFilter):
    __slots__ = ()
    name = 'filters.AUDIO'

    def filter(self, message: Message) -> bool:
        return bool(message.audio)


AUDIO = _Audio()
"""Messages that contain :class:`telegram.Audio`."""


class Document(MessageFilter):
    """
    Subset for messages containing a document/file.

    Examples:
        Use these filters like: ``filters.Document.MP3``,
        ``filters.Document.MimeType("text/plain")`` etc. Or use just ``filters.DOCUMENT`` for all
        document messages.
    """

    __slots__ = ()
    name = 'filters.DOCUMENT'

    class Category(MessageFilter):
        """Filters documents by their category in the mime-type attribute.

        Args:
            category (:obj:`str`): Category of the media you want to filter.

        Example:
            ``filters.Document.Category('audio/')`` returns :obj:`True` for all types
            of audio sent as a file, for example ``'audio/mpeg'`` or ``'audio/x-wav'``.

        Note:
            This Filter only filters by the mime_type of the document, it doesn't check the
            validity of the document. The user can manipulate the mime-type of a message and
            send media with wrong types that don't fit to this handler.
        """

        __slots__ = ('_category',)

        def __init__(self, category: str):
            self._category = category
            self.name = f"filters.Document.Category('{self._category}')"

        def filter(self, message: Message) -> bool:
            if message.document:
                return message.document.mime_type.startswith(self._category)
            return False

    APPLICATION = Category('application/')
    """Use as ``filters.Document.APPLICATION``."""
    AUDIO = Category('audio/')
    """Use as ``filters.Document.AUDIO``."""
    IMAGE = Category('image/')
    """Use as ``filters.Document.IMAGE``."""
    VIDEO = Category('video/')
    """Use as ``filters.Document.VIDEO``."""
    TEXT = Category('text/')
    """Use as ``filters.Document.TEXT``."""

    class MimeType(MessageFilter):
        """This Filter filters documents by their mime-type attribute.

        Args:
            mimetype (:obj:`str`): The mimetype to filter.

        Example:
            ``filters.Document.MimeType('audio/mpeg')`` filters all audio in `.mp3` format.

        Note:
            This Filter only filters by the mime_type of the document, it doesn't check the
            validity of document. The user can manipulate the mime-type of a message and
            send media with wrong types that don't fit to this handler.
        """

        __slots__ = ('mimetype',)

        def __init__(self, mimetype: str):
            self.mimetype = mimetype  # skipcq: PTC-W0052
            self.name = f"filters.Document.MimeType('{self.mimetype}')"

        def filter(self, message: Message) -> bool:
            if message.document:
                return message.document.mime_type == self.mimetype
            return False

    APK = MimeType('application/vnd.android.package-archive')
    """Use as ``filters.Document.APK``."""
    DOC = MimeType(mimetypes.types_map.get('.doc'))
    """Use as ``filters.Document.DOC``."""
    DOCX = MimeType('application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    """Use as ``filters.Document.DOCX``."""
    EXE = MimeType(mimetypes.types_map.get('.exe'))
    """Use as ``filters.Document.EXE``."""
    MP4 = MimeType(mimetypes.types_map.get('.mp4'))
    """Use as ``filters.Document.MP4``."""
    GIF = MimeType(mimetypes.types_map.get('.gif'))
    """Use as ``filters.Document.GIF``."""
    JPG = MimeType(mimetypes.types_map.get('.jpg'))
    """Use as ``filters.Document.JPG``."""
    MP3 = MimeType(mimetypes.types_map.get('.mp3'))
    """Use as ``filters.Document.MP3``."""
    PDF = MimeType(mimetypes.types_map.get('.pdf'))
    """Use as ``filters.Document.PDF``."""
    PY = MimeType(mimetypes.types_map.get('.py'))
    """Use as ``filters.Document.PY``."""
    SVG = MimeType(mimetypes.types_map.get('.svg'))
    """Use as ``filters.Document.SVG``."""
    TXT = MimeType(mimetypes.types_map.get('.txt'))
    """Use as ``filters.Document.TXT``."""
    TARGZ = MimeType('application/x-compressed-tar')
    """Use as ``filters.Document.TARGZ``."""
    WAV = MimeType(mimetypes.types_map.get('.wav'))
    """Use as ``filters.Document.WAV``."""
    XML = MimeType(mimetypes.types_map.get('.xml'))
    """Use as ``filters.Document.XML``."""
    ZIP = MimeType(mimetypes.types_map.get('.zip'))
    """Use as ``filters.Document.ZIP``."""

    class FileExtension(MessageFilter):
        """This filter filters documents by their file ending/extension.

        Args:
            file_extension (:obj:`str` | :obj:`None`): Media file extension you want to filter.
            case_sensitive (:obj:`bool`, optional): Pass :obj:`True` to make the filter case
                sensitive. Default: :obj:`False`.

        Example:
            * ``filters.Document.FileExtension("jpg")``
              filters files with extension ``".jpg"``.
            * ``filters.Document.FileExtension(".jpg")``
              filters files with extension ``"..jpg"``.
            * ``filters.Document.FileExtension("Dockerfile", case_sensitive=True)``
              filters files with extension ``".Dockerfile"`` minding the case.
            * ``filters.Document.FileExtension(None)``
              filters files without a dot in the filename.

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
        """

        __slots__ = ('_file_extension', 'is_case_sensitive')

        def __init__(self, file_extension: Optional[str], case_sensitive: bool = False):
            self.is_case_sensitive = case_sensitive
            if file_extension is None:
                self._file_extension = None
                self.name = "filters.Document.FileExtension(None)"
            elif self.is_case_sensitive:
                self._file_extension = f".{file_extension}"
                self.name = (
                    f"filters.Document.FileExtension({file_extension!r}, case_sensitive=True)"
                )
            else:
                self._file_extension = f".{file_extension}".lower()
                self.name = f"filters.Document.FileExtension({file_extension.lower()!r})"

        def filter(self, message: Message) -> bool:
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


DOCUMENT = Document()
"""Shortcut for :class:`telegram.ext.filters.Document()`."""


class _Animation(MessageFilter):
    __slots__ = ()
    name = 'filters.ANIMATION'

    def filter(self, message: Message) -> bool:
        return bool(message.animation)


ANIMATION = _Animation()
"""Messages that contain :class:`telegram.Animation`."""


class _Photo(MessageFilter):
    __slots__ = ()
    name = 'filters.PHOTO'

    def filter(self, message: Message) -> bool:
        return bool(message.photo)


PHOTO = _Photo()
"""Messages that contain :class:`telegram.PhotoSize`."""


class _Sticker(MessageFilter):
    __slots__ = ()
    name = 'filters.STICKER'

    def filter(self, message: Message) -> bool:
        return bool(message.sticker)


STICKER = _Sticker()
"""Messages that contain :class:`telegram.Sticker`."""


class _Video(MessageFilter):
    __slots__ = ()
    name = 'filters.VIDEO'

    def filter(self, message: Message) -> bool:
        return bool(message.video)


VIDEO = _Video()
"""Messages that contain :class:`telegram.Video`."""


class _Voice(MessageFilter):
    __slots__ = ()
    name = 'filters.VOICE'

    def filter(self, message: Message) -> bool:
        return bool(message.voice)


VOICE = _Voice()
"""Messages that contain :class:`telegram.Voice`."""


class _VideoNote(MessageFilter):
    __slots__ = ()
    name = 'filters.VIDEO_NOTE'

    def filter(self, message: Message) -> bool:
        return bool(message.video_note)


VIDEO_NOTE = _VideoNote()
"""Messages that contain :class:`telegram.VideoNote`."""


class _Contact(MessageFilter):
    __slots__ = ()
    name = 'filters.CONTACT'

    def filter(self, message: Message) -> bool:
        return bool(message.contact)


CONTACT = _Contact()
"""Messages that contain :class:`telegram.Contact`."""


class _Location(MessageFilter):
    __slots__ = ()
    name = 'filters.LOCATION'

    def filter(self, message: Message) -> bool:
        return bool(message.location)


LOCATION = _Location()
"""Messages that contain :class:`telegram.Location`."""


class _Venue(MessageFilter):
    __slots__ = ()
    name = 'filters.VENUE'

    def filter(self, message: Message) -> bool:
        return bool(message.venue)


VENUE = _Venue()
"""Messages that contain :class:`telegram.Venue`."""


class StatusUpdate:
    """Subset for messages containing a status update.

    Examples:
        Use these filters like: ``filters.StatusUpdate.NEW_CHAT_MEMBERS`` etc. Or use just
        ``filters.StatusUpdate.ALL`` for all status update messages.
    """

    __slots__ = ()
    name = 'filters.StatusUpdate'

    class _NewChatMembers(MessageFilter):
        __slots__ = ()
        name = 'filters.StatusUpdate.NEW_CHAT_MEMBERS'

        def filter(self, message: Message) -> bool:
            return bool(message.new_chat_members)

    NEW_CHAT_MEMBERS = _NewChatMembers()
    """Messages that contain :attr:`telegram.Message.new_chat_members`."""

    class _LeftChatMember(MessageFilter):
        __slots__ = ()
        name = 'filters.StatusUpdate.LEFT_CHAT_MEMBER'

        def filter(self, message: Message) -> bool:
            return bool(message.left_chat_member)

    LEFT_CHAT_MEMBER = _LeftChatMember()
    """Messages that contain :attr:`telegram.Message.left_chat_member`."""

    class _NewChatTitle(MessageFilter):
        __slots__ = ()
        name = 'filters.StatusUpdate.NEW_CHAT_TITLE'

        def filter(self, message: Message) -> bool:
            return bool(message.new_chat_title)

    NEW_CHAT_TITLE = _NewChatTitle()
    """Messages that contain :attr:`telegram.Message.new_chat_title`."""

    class _NewChatPhoto(MessageFilter):
        __slots__ = ()
        name = 'filters.StatusUpdate.NEW_CHAT_PHOTO'

        def filter(self, message: Message) -> bool:
            return bool(message.new_chat_photo)

    NEW_CHAT_PHOTO = _NewChatPhoto()
    """Messages that contain :attr:`telegram.Message.new_chat_photo`."""

    class _DeleteChatPhoto(MessageFilter):
        __slots__ = ()
        name = 'filters.StatusUpdate.DELETE_CHAT_PHOTO'

        def filter(self, message: Message) -> bool:
            return bool(message.delete_chat_photo)

    DELETE_CHAT_PHOTO = _DeleteChatPhoto()
    """Messages that contain :attr:`telegram.Message.delete_chat_photo`."""

    class _ChatCreated(MessageFilter):
        __slots__ = ()
        name = 'filters.StatusUpdate.CHAT_CREATED'

        def filter(self, message: Message) -> bool:
            return bool(
                message.group_chat_created
                or message.supergroup_chat_created
                or message.channel_chat_created
            )

    CHAT_CREATED = _ChatCreated()
    """Messages that contain :attr:`telegram.Message.group_chat_created`,
        :attr:`telegram.Message.supergroup_chat_created` or
        :attr:`telegram.Message.channel_chat_created`."""

    class _MessageAutoDeleteTimerChanged(MessageFilter):
        __slots__ = ()
        name = 'filters.StatusUpdate.MESSAGE_AUTO_DELETE_TIMER_CHANGED'

        def filter(self, message: Message) -> bool:
            return bool(message.message_auto_delete_timer_changed)

    MESSAGE_AUTO_DELETE_TIMER_CHANGED = _MessageAutoDeleteTimerChanged()
    """Messages that contain :attr:`telegram.Message.message_auto_delete_timer_changed`

    .. versionadded:: 13.4
    """

    class _Migrate(MessageFilter):
        __slots__ = ()
        name = 'filters.StatusUpdate.MIGRATE'

        def filter(self, message: Message) -> bool:
            return bool(message.migrate_from_chat_id or message.migrate_to_chat_id)

    MIGRATE = _Migrate()
    """Messages that contain :attr:`telegram.Message.migrate_from_chat_id` or
        :attr:`telegram.Message.migrate_to_chat_id`."""

    class _PinnedMessage(MessageFilter):
        __slots__ = ()
        name = 'filters.StatusUpdate.PINNED_MESSAGE'

        def filter(self, message: Message) -> bool:
            return bool(message.pinned_message)

    PINNED_MESSAGE = _PinnedMessage()
    """Messages that contain :attr:`telegram.Message.pinned_message`."""

    class _ConnectedWebsite(MessageFilter):
        __slots__ = ()
        name = 'filters.StatusUpdate.CONNECTED_WEBSITE'

        def filter(self, message: Message) -> bool:
            return bool(message.connected_website)

    CONNECTED_WEBSITE = _ConnectedWebsite()
    """Messages that contain :attr:`telegram.Message.connected_website`."""

    class _ProximityAlertTriggered(MessageFilter):
        __slots__ = ()
        name = 'filters.StatusUpdate.PROXIMITY_ALERT_TRIGGERED'

        def filter(self, message: Message) -> bool:
            return bool(message.proximity_alert_triggered)

    PROXIMITY_ALERT_TRIGGERED = _ProximityAlertTriggered()
    """Messages that contain :attr:`telegram.Message.proximity_alert_triggered`."""

    class _VoiceChatScheduled(MessageFilter):
        __slots__ = ()
        name = 'filters.StatusUpdate.VOICE_CHAT_SCHEDULED'

        def filter(self, message: Message) -> bool:
            return bool(message.voice_chat_scheduled)

    VOICE_CHAT_SCHEDULED = _VoiceChatScheduled()
    """Messages that contain :attr:`telegram.Message.voice_chat_scheduled`.

    .. versionadded:: 13.5
    """

    class _VoiceChatStarted(MessageFilter):
        __slots__ = ()
        name = 'filters.StatusUpdate.VOICE_CHAT_STARTED'

        def filter(self, message: Message) -> bool:
            return bool(message.voice_chat_started)

    VOICE_CHAT_STARTED = _VoiceChatStarted()
    """Messages that contain :attr:`telegram.Message.voice_chat_started`.

    .. versionadded:: 13.4
    """

    class _VoiceChatEnded(MessageFilter):
        __slots__ = ()
        name = 'filters.StatusUpdate.VOICE_CHAT_ENDED'

        def filter(self, message: Message) -> bool:
            return bool(message.voice_chat_ended)

    VOICE_CHAT_ENDED = _VoiceChatEnded()
    """Messages that contain :attr:`telegram.Message.voice_chat_ended`.

    .. versionadded:: 13.4
    """

    class _VoiceChatParticipantsInvited(MessageFilter):
        __slots__ = ()
        name = 'filters.StatusUpdate.VOICE_CHAT_PARTICIPANTS_INVITED'

        def filter(self, message: Message) -> bool:
            return bool(message.voice_chat_participants_invited)

    VOICE_CHAT_PARTICIPANTS_INVITED = _VoiceChatParticipantsInvited()
    """Messages that contain :attr:`telegram.Message.voice_chat_participants_invited`.

    .. versionadded:: 13.4
    """

    class _All(UpdateFilter):
        __slots__ = ()
        name = "filters.StatusUpdate.ALL"

        def filter(self, update: Update) -> bool:
            return bool(
                StatusUpdate.NEW_CHAT_MEMBERS.check_update(update)
                or StatusUpdate.LEFT_CHAT_MEMBER.check_update(update)
                or StatusUpdate.NEW_CHAT_TITLE.check_update(update)
                or StatusUpdate.NEW_CHAT_PHOTO.check_update(update)
                or StatusUpdate.DELETE_CHAT_PHOTO.check_update(update)
                or StatusUpdate.CHAT_CREATED.check_update(update)
                or StatusUpdate.MESSAGE_AUTO_DELETE_TIMER_CHANGED.check_update(update)
                or StatusUpdate.MIGRATE.check_update(update)
                or StatusUpdate.PINNED_MESSAGE.check_update(update)
                or StatusUpdate.CONNECTED_WEBSITE.check_update(update)
                or StatusUpdate.PROXIMITY_ALERT_TRIGGERED.check_update(update)
                or StatusUpdate.VOICE_CHAT_SCHEDULED.check_update(update)
                or StatusUpdate.VOICE_CHAT_STARTED.check_update(update)
                or StatusUpdate.VOICE_CHAT_ENDED.check_update(update)
                or StatusUpdate.VOICE_CHAT_PARTICIPANTS_INVITED.check_update(update)
            )

    ALL = _All()
    """Messages that contain any of the above."""


class _Forwarded(MessageFilter):
    __slots__ = ()
    name = 'filters.FORWARDED'

    def filter(self, message: Message) -> bool:
        return bool(message.forward_date)


FORWARDED = _Forwarded()
"""Messages that are forwarded."""


class _Game(MessageFilter):
    __slots__ = ()
    name = 'filters.GAME'

    def filter(self, message: Message) -> bool:
        return bool(message.game)


GAME = _Game()
"""Messages that contain :class:`telegram.Game`."""


class Entity(MessageFilter):
    """
    Filters messages to only allow those which have a :class:`telegram.MessageEntity`
    where their :class:`~telegram.MessageEntity.type` matches `entity_type`.

    Examples:
        ``MessageHandler(filters.Entity("hashtag"), callback_method)``

    Args:
        entity_type (:obj:`str`): Entity type to check for. All types can be found as constants
            in :class:`telegram.MessageEntity`.

    """

    __slots__ = ('entity_type',)

    def __init__(self, entity_type: str):
        self.entity_type = entity_type
        self.name = f'filters.Entity({self.entity_type})'

    def filter(self, message: Message) -> bool:
        return any(entity.type == self.entity_type for entity in message.entities)


class CaptionEntity(MessageFilter):
    """
    Filters media messages to only allow those which have a :class:`telegram.MessageEntity`
    where their :class:`~telegram.MessageEntity.type` matches `entity_type`.

    Examples:
        ``MessageHandler(filters.CaptionEntity("hashtag"), callback_method)``

    Args:
        entity_type (:obj:`str`): Caption Entity type to check for. All types can be found as
            constants in :class:`telegram.MessageEntity`.

    """

    __slots__ = ('entity_type',)

    def __init__(self, entity_type: str):
        self.entity_type = entity_type
        self.name = f'filters.CaptionEntity({self.entity_type})'

    def filter(self, message: Message) -> bool:
        return any(entity.type == self.entity_type for entity in message.caption_entities)


class ChatType:  # A convenience namespace for Chat types.
    """Subset for filtering the type of chat.

    Examples:
        Use these filters like: ``filters.ChatType.CHANNEL`` or
        ``filters.ChatType.SUPERGROUP`` etc.

    Note:
        ``filters.ChatType`` itself is *not* a filter.
    """

    __slots__ = ()
    name = 'filters.ChatType'

    class _Channel(MessageFilter):
        __slots__ = ()
        name = 'filters.ChatType.CHANNEL'

        def filter(self, message: Message) -> bool:
            return message.chat.type == TGChat.CHANNEL

    CHANNEL = _Channel()
    """Updates from channel."""

    class _Group(MessageFilter):
        __slots__ = ()
        name = 'filters.ChatType.GROUP'

        def filter(self, message: Message) -> bool:
            return message.chat.type == TGChat.GROUP

    GROUP = _Group()
    """Updates from group."""

    class _SuperGroup(MessageFilter):
        __slots__ = ()
        name = 'filters.ChatType.SUPERGROUP'

        def filter(self, message: Message) -> bool:
            return message.chat.type == TGChat.SUPERGROUP

    SUPERGROUP = _SuperGroup()
    """Updates from supergroup."""

    class _Groups(MessageFilter):
        __slots__ = ()
        name = 'filters.ChatType.GROUPS'

        def filter(self, message: Message) -> bool:
            return message.chat.type in [TGChat.GROUP, TGChat.SUPERGROUP]

    GROUPS = _Groups()
    """Update from group *or* supergroup."""

    class _Private(MessageFilter):
        __slots__ = ()
        name = 'filters.ChatType.PRIVATE'

        def filter(self, message: Message) -> bool:
            return message.chat.type == TGChat.PRIVATE

    PRIVATE = _Private()
    """Update from private chats."""


class _ChatUserBaseFilter(MessageFilter, ABC):
    __slots__ = (
        '_chat_id_name',
        '_username_name',
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
        self._chat_id_name = 'chat_id'
        self._username_name = 'username'
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
                    f"Can't set {self._chat_id_name} in conjunction with (already set) "
                    f"{self._username_name}s."
                )
            self._chat_ids = self._parse_chat_id(chat_id)

    def _set_usernames(self, username: SLT[str]) -> None:
        with self.__lock:
            if username and self._chat_ids:
                raise RuntimeError(
                    f"Can't set {self._username_name} in conjunction with (already set) "
                    f"{self._chat_id_name}s."
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

    def _add_usernames(self, username: SLT[str]) -> None:
        with self.__lock:
            if self._chat_ids:
                raise RuntimeError(
                    f"Can't set {self._username_name} in conjunction with (already set) "
                    f"{self._chat_id_name}s."
                )

            parsed_username = self._parse_username(username)
            self._usernames |= parsed_username

    def _add_chat_ids(self, chat_id: SLT[int]) -> None:
        with self.__lock:
            if self._usernames:
                raise RuntimeError(
                    f"Can't set {self._chat_id_name} in conjunction with (already set) "
                    f"{self._username_name}s."
                )

            parsed_chat_id = self._parse_chat_id(chat_id)

            self._chat_ids |= parsed_chat_id

    def _remove_usernames(self, username: SLT[str]) -> None:
        with self.__lock:
            if self._chat_ids:
                raise RuntimeError(
                    f"Can't set {self._username_name} in conjunction with (already set) "
                    f"{self._chat_id_name}s."
                )

            parsed_username = self._parse_username(username)
            self._usernames -= parsed_username

    def _remove_chat_ids(self, chat_id: SLT[int]) -> None:
        with self.__lock:
            if self._usernames:
                raise RuntimeError(
                    f"Can't set {self._chat_id_name} in conjunction with (already set) "
                    f"{self._username_name}s."
                )
            parsed_chat_id = self._parse_chat_id(chat_id)
            self._chat_ids -= parsed_chat_id

    def filter(self, message: Message) -> bool:
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
            f'filters.{self.__class__.__name__}('
            f'{", ".join(str(s) for s in (self.usernames or self.chat_ids))})'
        )

    @name.setter
    def name(self, name: str) -> NoReturn:
        raise RuntimeError(f'Cannot set name for filters.{self.__class__.__name__}')


class User(_ChatUserBaseFilter):
    """Filters messages to allow only those which are from specified user ID(s) or
    username(s).

    Examples:
        ``MessageHandler(filters.User(1234), callback_method)``

    Args:
        user_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
            Which user ID(s) to allow through.
        username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
            Which username(s) to allow through. Leading ``'@'`` s in usernames will be
            discarded.
        allow_empty(:obj:`bool`, optional): Whether updates should be processed, if no user
            is specified in :attr:`user_ids` and :attr:`usernames`. Defaults to :obj:`False`.

    Attributes:
        usernames (set(:obj:`str`)): Which username(s) (without leading ``'@'``) to allow through.
        allow_empty (:obj:`bool`): Whether updates should be processed, if no user
            is specified in :attr:`user_ids` and :attr:`usernames`.

    Raises:
        RuntimeError: If ``user_id`` and ``username`` are both present.
    """

    __slots__ = ()

    def __init__(
        self,
        user_id: SLT[int] = None,
        username: SLT[str] = None,
        allow_empty: bool = False,
    ):
        super().__init__(chat_id=user_id, username=username, allow_empty=allow_empty)
        self._chat_id_name = 'user_id'

    def get_chat_or_user(self, message: Message) -> Optional[TGUser]:
        return message.from_user

    @property
    def user_ids(self) -> FrozenSet[int]:
        """
        Which user ID(s) to allow through.

        Warning:
            :attr:`user_ids` will give a *copy* of the saved user ids as :class:`frozenset`. This
            is to ensure thread safety. To add/remove a user, you should use :meth:`add_usernames`,
            :meth:`add_user_ids`, :meth:`remove_usernames` and :meth:`remove_user_ids`. Only update
            the entire set by ``filter.user_ids/usernames = new_set``, if you are entirely sure
            that it is not causing race conditions, as this will complete replace the current set
            of allowed users.

        Returns:
            set(:obj:`int`)
        """
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
        return super()._add_usernames(username)

    def add_user_ids(self, user_id: SLT[int]) -> None:
        """
        Add one or more users to the allowed user ids.

        Args:
            user_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which user ID(s) to allow through.
        """
        return super()._add_chat_ids(user_id)

    def remove_usernames(self, username: SLT[str]) -> None:
        """
        Remove one or more users from allowed usernames.

        Args:
            username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
                Which username(s) to disallow through.
                Leading ``'@'`` s in usernames will be discarded.
        """
        return super()._remove_usernames(username)

    def remove_user_ids(self, user_id: SLT[int]) -> None:
        """
        Remove one or more users from allowed user ids.

        Args:
            user_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which user ID(s) to disallow through.
        """
        return super()._remove_chat_ids(user_id)


USER = User(allow_empty=True)
"""
Shortcut for :class:`telegram.ext.filters.User(allow_empty=True)`. This allows to filter *any*
message that was sent from a user.
"""


class ViaBot(_ChatUserBaseFilter):
    """Filters messages to allow only those which are from specified via_bot ID(s) or
    username(s).

    Examples:
        ``MessageHandler(filters.ViaBot(1234), callback_method)``

    Args:
        bot_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
            Which bot ID(s) to allow through.
        username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
            Which username(s) to allow through. Leading ``'@'`` s in usernames will be
            discarded.
        allow_empty(:obj:`bool`, optional): Whether updates should be processed, if no user
            is specified in :attr:`bot_ids` and :attr:`usernames`. Defaults to :obj:`False`.

    Attributes:
        usernames (set(:obj:`str`)): Which username(s) (without leading ``'@'``) to allow through.
        allow_empty (:obj:`bool`): Whether updates should be processed, if no bot
            is specified in :attr:`bot_ids` and :attr:`usernames`.

    Raises:
        RuntimeError: If ``bot_id`` and ``username`` are both present.
    """

    __slots__ = ()

    def __init__(
        self,
        bot_id: SLT[int] = None,
        username: SLT[str] = None,
        allow_empty: bool = False,
    ):
        super().__init__(chat_id=bot_id, username=username, allow_empty=allow_empty)
        self._chat_id_name = 'bot_id'

    def get_chat_or_user(self, message: Message) -> Optional[TGUser]:
        return message.via_bot

    @property
    def bot_ids(self) -> FrozenSet[int]:
        """
        Which bot ID(s) to allow through.

        Warning:
            :attr:`bot_ids` will give a *copy* of the saved bot ids as :class:`frozenset`. This
            is to ensure thread safety. To add/remove a bot, you should use :meth:`add_usernames`,
            :meth:`add_bot_ids`, :meth:`remove_usernames` and :meth:`remove_bot_ids`. Only update
            the entire set by ``filter.bot_ids/usernames = new_set``, if you are entirely sure
            that it is not causing race conditions, as this will complete replace the current set
            of allowed bots.

        Returns:
            set(:obj:`int`)
        """
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
        return super()._add_usernames(username)

    def add_bot_ids(self, bot_id: SLT[int]) -> None:
        """
        Add one or more users to the allowed user ids.

        Args:
            bot_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which bot ID(s) to allow through.
        """
        return super()._add_chat_ids(bot_id)

    def remove_usernames(self, username: SLT[str]) -> None:
        """
        Remove one or more users from allowed usernames.

        Args:
            username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
                Which username(s) to disallow through.
                Leading ``'@'`` s in usernames will be discarded.
        """
        return super()._remove_usernames(username)

    def remove_bot_ids(self, bot_id: SLT[int]) -> None:
        """
        Remove one or more users from allowed user ids.

        Args:
            bot_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which bot ID(s) to disallow through.
        """
        return super()._remove_chat_ids(bot_id)


VIA_BOT = ViaBot(allow_empty=True)
"""
Shortcut for :class:`telegram.ext.filters.ViaBot(allow_empty=True)`. This allows to filter *any*
message that was sent via a bot.
"""


class Chat(_ChatUserBaseFilter):
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
            is specified in :attr:`chat_ids` and :attr:`usernames`. Defaults to :obj:`False`.

    Attributes:
        chat_ids (set(:obj:`int`)): Which chat ID(s) to allow through.
        usernames (set(:obj:`str`)): Which username(s) (without leading ``'@'``) to allow through.
        allow_empty (:obj:`bool`): Whether updates should be processed, if no chat
            is specified in :attr:`chat_ids` and :attr:`usernames`.

    Raises:
        RuntimeError: If ``chat_id`` and ``username`` are both present.
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
        return super()._add_usernames(username)

    def add_chat_ids(self, chat_id: SLT[int]) -> None:
        """
        Add one or more chats to the allowed chat ids.

        Args:
            chat_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which chat ID(s) to allow through.
        """
        return super()._add_chat_ids(chat_id)

    def remove_usernames(self, username: SLT[str]) -> None:
        """
        Remove one or more chats from allowed usernames.

        Args:
            username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
                Which username(s) to disallow through.
                Leading ``'@'`` s in usernames will be discarded.
        """
        return super()._remove_usernames(username)

    def remove_chat_ids(self, chat_id: SLT[int]) -> None:
        """
        Remove one or more chats from allowed chat ids.

        Args:
            chat_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which chat ID(s) to disallow through.
        """
        return super()._remove_chat_ids(chat_id)


CHAT = Chat(allow_empty=True)
"""
Shortcut for :class:`telegram.ext.filters.Chat(allow_empty=True)`. This allows to filter for *any*
message that was sent from any chat.
"""


class ForwardedFrom(_ChatUserBaseFilter):
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

    Attributes:
        chat_ids (set(:obj:`int`)): Which chat/user ID(s) to allow through.
        usernames (set(:obj:`str`)): Which username(s) (without leading ``'@'``) to allow through.
        allow_empty (:obj:`bool`): Whether updates should be processed, if no chat
            is specified in :attr:`chat_ids` and :attr:`usernames`.

    Raises:
        RuntimeError: If both ``chat_id`` and ``username`` are present.
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
        return super()._add_usernames(username)

    def add_chat_ids(self, chat_id: SLT[int]) -> None:
        """
        Add one or more chats to the allowed chat ids.

        Args:
            chat_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which chat/user ID(s) to allow through.
        """
        return super()._add_chat_ids(chat_id)

    def remove_usernames(self, username: SLT[str]) -> None:
        """
        Remove one or more chats from allowed usernames.

        Args:
            username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
                Which username(s) to disallow through.
                Leading ``'@'`` s in usernames will be discarded.
        """
        return super()._remove_usernames(username)

    def remove_chat_ids(self, chat_id: SLT[int]) -> None:
        """
        Remove one or more chats from allowed chat ids.

        Args:
            chat_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which chat/user ID(s) to disallow through.
        """
        return super()._remove_chat_ids(chat_id)


class SenderChat(_ChatUserBaseFilter):
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
            chat is specified in :attr:`chat_ids` and :attr:`usernames`. Defaults to :obj:`False`.

    Attributes:
        chat_ids (set(:obj:`int`)): Which sender chat chat ID(s) to allow through.
        usernames (set(:obj:`str`)): Which sender chat username(s) (without leading ``'@'``) to
            allow through.
        allow_empty (:obj:`bool`): Whether updates should be processed, if no sender
            chat is specified in :attr:`chat_ids` and :attr:`usernames`.

    Raises:
        RuntimeError: If both ``chat_id`` and ``username`` are present.
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
        return super()._add_usernames(username)

    def add_chat_ids(self, chat_id: SLT[int]) -> None:
        """
        Add one or more sender chats to the allowed chat ids.

        Args:
            chat_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which sender chat ID(s) to allow through.
        """
        return super()._add_chat_ids(chat_id)

    def remove_usernames(self, username: SLT[str]) -> None:
        """
        Remove one or more sender chats from allowed usernames.

        Args:
            username(:obj:`str` | Tuple[:obj:`str`] | List[:obj:`str`], optional):
                Which sender chat username(s) to disallow through.
                Leading ``'@'`` s in usernames will be discarded.
        """
        return super()._remove_usernames(username)

    def remove_chat_ids(self, chat_id: SLT[int]) -> None:
        """
        Remove one or more sender chats from allowed chat ids.

        Args:
            chat_id(:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
                Which sender chat ID(s) to disallow through.
        """
        return super()._remove_chat_ids(chat_id)

    class _SUPERGROUP(MessageFilter):
        __slots__ = ()
        name = "filters.SenderChat.SUPERGROUP"

        def filter(self, message: Message) -> bool:
            if message.sender_chat:
                return message.sender_chat.type == TGChat.SUPERGROUP
            return False

    class _CHANNEL(MessageFilter):
        __slots__ = ()
        name = "filters.SenderChat.CHANNEL"

        def filter(self, message: Message) -> bool:
            if message.sender_chat:
                return message.sender_chat.type == TGChat.CHANNEL
            return False

    SUPER_GROUP = _SUPERGROUP()
    """Messages whose sender chat is a super group."""
    CHANNEL = _CHANNEL()
    """Messages whose sender chat is a channel."""


SENDER_CHAT = SenderChat(allow_empty=True)
"""Shortcut for :class:`telegram.ext.filters.SenderChat(allow_empty=True)`. This allows to filter
for *any* message that was sent by a supergroup or a channel."""


class _Invoice(MessageFilter):
    __slots__ = ()
    name = 'filters.INVOICE'

    def filter(self, message: Message) -> bool:
        return bool(message.invoice)


INVOICE = _Invoice()
"""Messages that contain :class:`telegram.Invoice`."""


class _SuccessfulPayment(MessageFilter):
    __slots__ = ()
    name = 'filters.SUCCESSFUL_PAYMENT'

    def filter(self, message: Message) -> bool:
        return bool(message.successful_payment)


SUCCESSFUL_PAYMENT = _SuccessfulPayment()
"""Messages that confirm a :class:`telegram.SuccessfulPayment`."""


class _PassportData(MessageFilter):
    __slots__ = ()
    name = 'filters.PASSPORT_DATA'

    def filter(self, message: Message) -> bool:
        return bool(message.passport_data)


PASSPORT_DATA = _PassportData()
"""Messages that contain a :class:`telegram.PassportData`"""


class _Poll(MessageFilter):
    __slots__ = ()
    name = 'filters.POLL'

    def filter(self, message: Message) -> bool:
        return bool(message.poll)


POLL = _Poll()
"""Messages that contain a :class:`telegram.Poll`."""


class Dice(_Dice):
    """Dice Messages. If an integer or a list of integers is passed, it filters messages to only
    allow those whose dice value is appearing in the given list.

    .. versionadded:: 13.4

    Examples:
        To allow any dice message, simply use
        ``MessageHandler(filters.Dice.ALL, callback_method)``.

        To allow any dice message, but with value 3 `or` 4, use
        ``MessageHandler(filters.Dice([3, 4]), callback_method)``

        To allow only dice messages with the emoji 🎲, but any value, use
        ``MessageHandler(filters.Dice.DICE, callback_method)``.

        To allow only dice messages with the emoji 🎯 and with value 6, use
        ``MessageHandler(filters.Dice.Darts(6), callback_method)``.

        To allow only dice messages with the emoji ⚽ and with value 5 `or` 6, use
        ``MessageHandler(filters.Dice.Football([5, 6]), callback_method)``.

    Note:
        Dice messages don't have text. If you want to filter either text or dice messages, use
        ``filters.TEXT | filters.Dice.ALL``.

    Args:
        values (:obj:`int` | Tuple[:obj:`int`] | List[:obj:`int`], optional):
            Which values to allow. If not specified, will allow the specified dice message.
    """

    __slots__ = ()

    class Dice(_Dice):
        """Dice messages with the emoji 🎲. Supports passing a list of integers."""

        __slots__ = ()

        def __init__(self, values: SLT[int]):
            super().__init__(values, emoji=DiceEmojiEnum.DICE)

    DICE = _Dice(emoji=DiceEmojiEnum.DICE)  # skipcq: PTC-W0052
    """Dice messages with the emoji 🎲. Matches any dice value."""

    class Darts(_Dice):
        """Dice messages with the emoji 🎯. Supports passing a list of integers."""

        __slots__ = ()

        def __init__(self, values: SLT[int]):
            super().__init__(values, emoji=DiceEmojiEnum.DARTS)

    DARTS = _Dice(emoji=DiceEmojiEnum.DARTS)
    """Dice messages with the emoji 🎯. Matches any dice value."""

    class Basketball(_Dice):
        """Dice messages with the emoji 🏀. Supports passing a list of integers."""

        __slots__ = ()

        def __init__(self, values: SLT[int]):
            super().__init__(values, emoji=DiceEmojiEnum.BASKETBALL)

    BASKETBALL = _Dice(emoji=DiceEmojiEnum.BASKETBALL)
    """Dice messages with the emoji 🏀. Matches any dice value."""

    class Football(_Dice):
        """Dice messages with the emoji ⚽. Supports passing a list of integers."""

        __slots__ = ()

        def __init__(self, values: SLT[int]):
            super().__init__(values, emoji=DiceEmojiEnum.FOOTBALL)

    FOOTBALL = _Dice(emoji=DiceEmojiEnum.FOOTBALL)
    """Dice messages with the emoji ⚽. Matches any dice value."""

    class SlotMachine(_Dice):
        """Dice messages with the emoji 🎰. Supports passing a list of integers."""

        __slots__ = ()

        def __init__(self, values: SLT[int]):
            super().__init__(values, emoji=DiceEmojiEnum.SLOT_MACHINE)

    SLOT_MACHINE = _Dice(emoji=DiceEmojiEnum.SLOT_MACHINE)
    """Dice messages with the emoji 🎰. Matches any dice value."""

    class Bowling(_Dice):
        """Dice messages with the emoji 🎳. Supports passing a list of integers."""

        __slots__ = ()

        def __init__(self, values: SLT[int]):
            super().__init__(values, emoji=DiceEmojiEnum.BOWLING)

    BOWLING = _Dice(emoji=DiceEmojiEnum.BOWLING)
    """Dice messages with the emoji 🎳. Matches any dice value."""

    class _All(_Dice):
        __slots__ = ()

    ALL = _All()
    """Dice messages with any value and any emoji."""


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
        self.name = f'filters.Language({self.lang})'

    def filter(self, message: Message) -> bool:
        return bool(
            message.from_user.language_code
            and any(message.from_user.language_code.startswith(x) for x in self.lang)
        )


class _Attachment(MessageFilter):
    __slots__ = ()

    name = 'filters.ATTACHMENT'

    def filter(self, message: Message) -> bool:
        return bool(message.effective_attachment)


ATTACHMENT = _Attachment()
"""Messages that contain :meth:`telegram.Message.effective_attachment`.

.. versionadded:: 13.6"""


class UpdateType:
    """
    Subset for filtering the type of update.

    Examples:
        Use these filters like: ``filters.UpdateType.MESSAGE`` or
        ``filters.UpdateType.CHANNEL_POSTS`` etc. Or use just ``filters.UPDATE`` for all
        types.

    Note:
        ``filters.UpdateType`` itself is *not* a filter.
    """

    __slots__ = ()
    name = 'filters.UPDATE'

    class _Message(UpdateFilter):
        __slots__ = ()
        name = 'filters.UpdateType.MESSAGE'

        def filter(self, update: Update) -> bool:
            return update.message is not None

    MESSAGE = _Message()
    """Updates with :attr:`telegram.Update.message`."""

    class _EditedMessage(UpdateFilter):
        __slots__ = ()
        name = 'filters.UpdateType.EDITED_MESSAGE'

        def filter(self, update: Update) -> bool:
            return update.edited_message is not None

    EDITED_MESSAGE = _EditedMessage()
    """Updates with :attr:`telegram.Update.edited_message`."""

    class _Messages(UpdateFilter):
        __slots__ = ()
        name = 'filters.UpdateType.MESSAGES'

        def filter(self, update: Update) -> bool:
            return update.message is not None or update.edited_message is not None

    MESSAGES = _Messages()
    """Updates with either :attr:`telegram.Update.message` or
    :attr:`telegram.Update.edited_message`."""

    class _ChannelPost(UpdateFilter):
        __slots__ = ()
        name = 'filters.UpdateType.CHANNEL_POST'

        def filter(self, update: Update) -> bool:
            return update.channel_post is not None

    CHANNEL_POST = _ChannelPost()
    """Updates with :attr:`telegram.Update.channel_post`."""

    class _EditedChannelPost(UpdateFilter):
        __slots__ = ()
        name = 'filters.UpdateType.EDITED_CHANNEL_POST'

        def filter(self, update: Update) -> bool:
            return update.edited_channel_post is not None

    EDITED_CHANNEL_POST = _EditedChannelPost()
    """Updates with :attr:`telegram.Update.edited_channel_post`."""

    class _Edited(UpdateFilter):
        __slots__ = ()
        name = 'filters.UpdateType.EDITED'

        def filter(self, update: Update) -> bool:
            return update.edited_message is not None or update.edited_channel_post is not None

    EDITED = _Edited()
    """Updates with either :attr:`telegram.Update.edited_message` or
    :attr:`telegram.Update.edited_channel_post`."""

    class _ChannelPosts(UpdateFilter):
        __slots__ = ()
        name = 'filters.UpdateType.CHANNEL_POSTS'

        def filter(self, update: Update) -> bool:
            return update.channel_post is not None or update.edited_channel_post is not None

    CHANNEL_POSTS = _ChannelPosts()
    """Updates with either :attr:`telegram.Update.channel_post` or
    :attr:`telegram.Update.edited_channel_post`."""

    class _All(UpdateFilter):
        __slots__ = ()
        name = 'filters.UpdateType.ALL'

        def filter(self, update: Update) -> bool:
            return bool(
                UpdateType.MESSAGES.check_update(update)
                or UpdateType.CHANNEL_POSTS.check_update(update)
            )

    ALL = _All()
    """All updates which contain a message."""
