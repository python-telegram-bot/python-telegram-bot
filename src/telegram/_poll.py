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
"""This module contains an object that represents a Telegram Poll."""

import datetime as dtm
from typing import TYPE_CHECKING, ClassVar, Final

from telegram import constants
from telegram._chat import Chat
from telegram._files.animation import Animation
from telegram._files.audio import Audio
from telegram._files.document import Document
from telegram._files.livephoto import LivePhoto
from telegram._files.location import Location
from telegram._files.photosize import PhotoSize
from telegram._files.sticker import Sticker
from telegram._files.venue import Venue
from telegram._files.video import Video
from telegram._messageentity import MessageEntity
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils import enum
from telegram._utils.argumentparsing import (
    parse_sequence_arg,
    to_timedelta,
)
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram._utils.datetime import get_timedelta_value
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.entities import parse_message_entities, parse_message_entity
from telegram._utils.types import ODVInput

if TYPE_CHECKING:
    from telegram._files.inputmedia import InputPollOptionMedia
    from telegram._message import MaybeInaccessibleMessage


@tg_dataclass()
class PollMedia(TelegramObject):
    """
    At most one of the optional fields can be present in any given object.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if all of their attributes are equal.

    .. versionadded:: 22.8

    Args:
        animation (:class:`telegram.Animation`, optional): Media is an animation, information about
            the animation
        audio (:class:`telegram.Audio`, optional): Media is an audio file, information about the
            file; currently, can't be received in a poll option
        document (:class:`telegram.Document`, optional): Media is a general file, information about
            the file; currently, can't be received in a poll option
        live_photo (:class:`telegram.LivePhoto`, optional): Media is a live photo, information
            about the live photo
        location (:class:`telegram.Location`, optional): Media is a shared location, information
            about the location
        photo (Sequence[:class:`telegram.PhotoSize`], optional): Media is a photo, available sizes
            of the photo
        sticker (:class:`telegram.Sticker`, optional): Media is a sticker, information about the
            sticker; currently, for poll options only
        venue (:class:`telegram.Venue`, optional): Media is a venue, information about the venue
        video (:class:`telegram.Video`, optional): Media is a video, information about the video

    Attributes:
        animation (:class:`telegram.Animation`): Optional. Media is an animation, information about
            the animation
        audio (:class:`telegram.Audio`): Optional. Media is an audio file, information about the
            file; currently, can't be received in a poll option
        document (:class:`telegram.Document`): Optional. Media is a general file, information about
            the file; currently, can't be received in a poll option
        live_photo (:class:`telegram.LivePhoto`, optional): Media is a live photo, information
            about the live photo
        location (:class:`telegram.Location`): Optional. Media is a shared location, information
            about the location
        photo (tuple[:class:`telegram.PhotoSize`]): Optional. Media is a photo, available sizes
            of the photo
        sticker (:class:`telegram.Sticker`): Optional. Media is a sticker, information about the
            sticker; currently, for poll options only
        venue (:class:`telegram.Venue`): Optional. Media is a venue, information about the venue
        video (:class:`telegram.Video`): Optional. Media is a video, information about the video
    """

    animation: Animation | None = tg_field(compare=True, default=None)
    audio: Audio | None = tg_field(compare=True, default=None)
    document: Document | None = tg_field(compare=True, default=None)
    live_photo: LivePhoto | None = tg_field(compare=True, default=None)
    location: Location | None = tg_field(compare=True, default=None)
    photo: tuple[PhotoSize, ...] = tg_field(
        compare=True, default=None, converter=parse_sequence_arg
    )
    sticker: Sticker | None = tg_field(compare=True, default=None)
    venue: Venue | None = tg_field(compare=True, default=None)
    video: Video | None = tg_field(compare=True, default=None)


@tg_dataclass()
class InputPollOption(TelegramObject):
    """
    This object contains information about one answer option in a poll to be sent.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`text` is equal.

    .. versionadded:: 21.2

    Args:
        text (:obj:`str`): Option text,
            :tg-const:`telegram.PollOption.MIN_LENGTH`-:tg-const:`telegram.PollOption.MAX_LENGTH`
            characters.
        text_parse_mode (:obj:`str`, optional): |parse_mode|
            Currently, only custom emoji entities are allowed.
        text_entities (Sequence[:class:`telegram.MessageEntity`], optional): Special entities
            that appear in the option :paramref:`text`. It can be specified instead of
            :paramref:`text_parse_mode`.
            Currently, only custom emoji entities are allowed.
            This list is empty if the text does not contain entities.
        media (:class:`telegram.InputPollOptionMedia`, optional): Media added to the poll option.

            .. versionadded:: 22.8

    Attributes:
        text (:obj:`str`): Option text,
            :tg-const:`telegram.PollOption.MIN_LENGTH`-:tg-const:`telegram.PollOption.MAX_LENGTH`
            characters.
        text_parse_mode (:obj:`str`): Optional. |parse_mode|
            Currently, only custom emoji entities are allowed.
        text_entities (Sequence[:class:`telegram.MessageEntity`]): Special entities
            that appear in the option :paramref:`text`. It can be specified instead of
            :paramref:`text_parse_mode`.
            Currently, only custom emoji entities are allowed.
            This list is empty if the text does not contain entities.
        media (:class:`telegram.InputPollOptionMedia`): Optional. Media added to the poll option.

            .. versionadded:: 22.8
    """

    text: str = tg_field(compare=True)
    text_parse_mode: ODVInput[str] = tg_field(default=DEFAULT_NONE)
    text_entities: tuple[MessageEntity, ...] = tg_field(default=None, converter=parse_sequence_arg)
    media: "InputPollOptionMedia | None" = tg_field(default=None)


@tg_dataclass()
class PollOption(TelegramObject):
    """
    This object contains information about one answer option in a poll.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`text`, :attr:`voter_count` and :attr:`persistent_id`
    are equal.

    .. versionchanged:: 22.8
        Added attribute :attr:`persistent_id` to equality checks.


    Args:
        persistent_id (:obj:`str`): Unique identifier of the option, persistent on option addition
            and deletion.

            .. versionadded:: 22.8
        text (:obj:`str`): Option text,
            :tg-const:`telegram.PollOption.MIN_LENGTH`-:tg-const:`telegram.PollOption.MAX_LENGTH`
            characters.
        voter_count (:obj:`int`): Number of users that voted for this option.
        text_entities (Sequence[:class:`telegram.MessageEntity`], optional): Special entities
            that appear in the option text. Currently, only custom emoji entities are allowed in
            poll option texts.

            .. versionadded:: 21.2
        media (:class:`telegram.PollMedia`, optional): Media added to the poll option.

            .. versionadded:: 22.8
        added_by_user (:class:`telegram.User`, optional): User who added the option;
            omitted if the option wasn't added by a user after poll creation.

            .. versionadded:: 22.8
        added_by_chat (:class:`telegram.Chat`, optional): Chat that added the option;
            omitted if the option wasn't added by a chat after poll creation.

            .. versionadded:: 22.8
        addition_date (:obj:`datetime.datetime`, optional): Point in time
            when the option was added; omitted if the option existed in the original poll.

            .. versionadded:: 22.8

    Attributes:
        persistent_id (:obj:`str`): Unique identifier of the option, persistent on option addition
            and deletion.

            .. versionadded:: 22.8
        text (:obj:`str`): Option text,
            :tg-const:`telegram.PollOption.MIN_LENGTH`-:tg-const:`telegram.PollOption.MAX_LENGTH`
            characters.
        voter_count (:obj:`int`): Number of users that voted for this option.
        text_entities (tuple[:class:`telegram.MessageEntity`]): Special entities
            that appear in the option text. Currently, only custom emoji entities are allowed in
            poll option texts.
            This list is empty if the question does not contain entities.

            .. versionadded:: 21.2
        media (:class:`telegram.PollMedia`): Optional. Media added to the poll option.

            .. versionadded:: 22.8
        added_by_user (:class:`telegram.User`): Optional. User who added the option;
            omitted if the option wasn't added by a user after poll creation.

            .. versionadded:: 22.8
        added_by_chat (:class:`telegram.Chat`): Optional. Chat that added the option;
            omitted if the option wasn't added by a chat after poll creation.

            .. versionadded:: 22.8
        addition_date (:obj:`datetime.datetime`): Optional. Point in time
            when the option was added; omitted if the option existed in the original poll.

            .. versionadded:: 22.8
    """

    # Required
    text: str = tg_field(compare=True)
    voter_count: int = tg_field(compare=True)
    persistent_id: str = tg_field(compare=True)

    # Optional
    text_entities: tuple[MessageEntity, ...] = tg_field(default=None, converter=parse_sequence_arg)
    added_by_user: User | None = tg_field(default=None)
    added_by_chat: Chat | None = tg_field(default=None)
    addition_date: dtm.datetime | None = tg_field(default=None)
    media: PollMedia | None = tg_field(default=None)

    def parse_entity(self, entity: MessageEntity) -> str:
        """Returns the text in :attr:`text`
        from a given :class:`telegram.MessageEntity` of :attr:`text_entities`.

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice ``Message.text`` with the offset and length.)

        .. versionadded:: 21.2

        Args:
            entity (:class:`telegram.MessageEntity`): The entity to extract the text from. It must
                be an entity that belongs to :attr:`text_entities`.

        Returns:
            :obj:`str`: The text of the given entity.
        """
        return parse_message_entity(self.text, entity)

    def parse_entities(self, types: list[str] | None = None) -> dict[MessageEntity, str]:
        """
        Returns a :obj:`dict` that maps :class:`telegram.MessageEntity` to :obj:`str`.
        It contains entities from this polls question filtered by their ``type`` attribute as
        the key, and the text that each entity belongs to as the value of the :obj:`dict`.

        Note:
            This method should always be used instead of the :attr:`text_entities`
            attribute, since it calculates the correct substring from the message text based on
            UTF-16 codepoints. See :attr:`parse_entity` for more info.

        .. versionadded:: 21.2

        Args:
            types (list[:obj:`str`], optional): List of ``MessageEntity`` types as strings. If the
                    ``type`` attribute of an entity is contained in this list, it will be returned.
                    Defaults to :attr:`telegram.MessageEntity.ALL_TYPES`.

        Returns:
            dict[:class:`telegram.MessageEntity`, :obj:`str`]: A dictionary of entities mapped to
            the text that belongs to them, calculated based on UTF-16 codepoints.
        """
        return parse_message_entities(self.text, self.text_entities, types)

    MIN_LENGTH: Final[int] = constants.PollLimit.MIN_OPTION_LENGTH
    """:const:`telegram.constants.PollLimit.MIN_OPTION_LENGTH`

    .. versionadded:: 20.0
    """
    MAX_LENGTH: Final[int] = constants.PollLimit.MAX_OPTION_LENGTH
    """:const:`telegram.constants.PollLimit.MAX_OPTION_LENGTH`

    .. versionadded:: 20.0
    """


@tg_dataclass()
class PollAnswer(TelegramObject):
    """
    This object represents an answer of a user in a non-anonymous poll.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`poll_id`, :attr:`user` and :attr:`option_ids` are equal.

    .. versionchanged:: 20.5
        The order of :paramref:`option_ids` and :paramref:`user` is changed in
        20.5 as the latter one became optional.

    .. versionchanged:: 20.6
       Backward compatiblity for changed order of :paramref:`option_ids` and :paramref:`user`
       was removed.

    Args:
        poll_id (:obj:`str`): Unique poll identifier.
        option_ids (Sequence[:obj:`int`]): Identifiers of answer options, chosen by the user. May
            be empty if the user retracted their vote.

            .. versionchanged:: 20.0
                |sequenceclassargs|
        option_persistent_ids (Sequence[:obj:`str`]): Persistent identifiers of the
            chosen answer options. May be empty if the vote was retracted.

            .. versionadded:: 22.8
        user (:class:`telegram.User`, optional): The user that changed the answer to the poll,
            if the voter isn't anonymous. If the voter is anonymous, this field will contain the
            user :tg-const:`telegram.constants.ChatID.FAKE_CHANNEL` for backwards compatibility.

            .. versionchanged:: 20.5
                :paramref:`user` became optional.
        voter_chat (:class:`telegram.Chat`, optional): The chat that changed the answer to the
            poll, if the voter is anonymous.

            .. versionadded:: 20.5

    Attributes:
        poll_id (:obj:`str`): Unique poll identifier.
        option_ids (tuple[:obj:`int`]): Identifiers of answer options, chosen by the user. May
            be empty if the user retracted their vote.

            .. versionchanged:: 20.0
                |tupleclassattrs|
        option_persistent_ids (tuple[:obj:`str`]): Persistent identifiers of the
            chosen answer options. May be empty if the vote was retracted.

            .. versionadded:: 22.8
        user (:class:`telegram.User`): Optional. The user, who changed the answer to the
            poll, if the voter isn't anonymous. If the voter is anonymous, this field will contain
            the user :tg-const:`telegram.constants.ChatID.FAKE_CHANNEL` for backwards compatibility

            .. versionchanged:: 20.5
                :paramref:`user` became optional.
        voter_chat (:class:`telegram.Chat`): Optional. The chat that changed the answer to the
            poll, if the voter is anonymous.

            .. versionadded:: 20.5
    """

    # Required
    poll_id: str = tg_field(compare=True)
    option_ids: tuple[int, ...] = tg_field(compare=True, converter=parse_sequence_arg)
    option_persistent_ids: tuple[str, ...] = tg_field(converter=parse_sequence_arg)
    # Optional
    user: User | None = tg_field(compare=True, default=None)
    voter_chat: Chat | None = tg_field(compare=True, default=None)


@tg_dataclass()
class PollOptionAdded(TelegramObject):
    """
    Describes a service message about an option added to a poll.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`option_persistent_id`, and :attr:`option_text` are equal.

    .. versionadded:: 22.8

    Args:
        option_persistent_id (:obj:`str`): Unique identifier of the added option.
        option_text (:obj:`str`): Option text.
        poll_message (:class:`telegram.MaybeInaccessibleMessage`, optional): Message
            containing the poll to which the option was added, if known.
            Note that the Message object in this field will not contain the
            :attr:`~telegram.Message.reply_to_message` field even if it itself is a reply.
        option_text_entities (Sequence[:class:`telegram.MessageEntity`], optional): Special
            entities that appear in the :paramref:`option_text`.

    Attributes:
        option_persistent_id (:obj:`str`): Unique identifier of the added option.
        option_text (:obj:`str`): Option text.
        poll_message (:class:`telegram.MaybeInaccessibleMessage`): Optional. Message
            containing the poll to which the option was added, if known.
            Note that the Message object in this field will not contain the
            :attr:`~telegram.Message.reply_to_message` field even if it itself is a reply.
        option_text_entities (tuple[:class:`telegram.MessageEntity`]): Optional. Special
            entities that appear in the :paramref:`option_text`.
    """

    # Required
    option_persistent_id: str = tg_field(compare=True)
    option_text: str = tg_field(compare=True)
    # Optional
    poll_message: "MaybeInaccessibleMessage | None" = tg_field(default=None)
    option_text_entities: tuple[MessageEntity, ...] = tg_field(
        default=None, converter=parse_sequence_arg
    )

    def parse_option_text_entity(self, entity: MessageEntity) -> str:
        """Returns the text in :attr:`option_text`
        from a given :class:`telegram.MessageEntity` of :attr:`option_text_entities`.

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice ``Message.text`` with the offset and length.)

        Args:
            entity (:class:`telegram.MessageEntity`): The entity to extract the text from. It must
                be an entity that belongs to :attr:`option_text_entities`.

        Returns:
            :obj:`str`: The text of the given entity.
        """
        return parse_message_entity(self.option_text, entity)

    def parse_option_text_entities(
        self, types: list[str] | None = None
    ) -> dict[MessageEntity, str]:
        """
        Returns a :obj:`dict` that maps :class:`telegram.MessageEntity` to :obj:`str`.
        It contains entities from this polls option text filtered by their ``type`` attribute as
        the key, and the text that each entity belongs to as the value of the :obj:`dict`.

        Note:
            This method should always be used instead of the :attr:`option_text_entities`
            attribute, since it calculates the correct substring from the message text based on
            UTF-16 codepoints. See :attr:`parse_entity` for more info.

        Args:
            types (list[:obj:`str`], optional): List of ``MessageEntity`` types as strings. If the
                    ``type`` attribute of an entity is contained in this list, it will be returned.
                    Defaults to :attr:`telegram.MessageEntity.ALL_TYPES`.

        Returns:
            dict[:class:`telegram.MessageEntity`, :obj:`str`]: A dictionary of entities mapped to
            the text that belongs to them, calculated based on UTF-16 codepoints.
        """
        return parse_message_entities(self.option_text, self.option_text_entities, types)


@tg_dataclass()
class PollOptionDeleted(TelegramObject):
    """
    Describes a service message about an option deleted from a poll.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`option_persistent_id`, :attr:`option_text` are equal.

    .. versionadded:: 22.8

    Args:
        option_persistent_id (:obj:`str`): Unique identifier of the deleted option.
        option_text (:obj:`str`): Option text.
        poll_message (:class:`telegram.MaybeInaccessibleMessage`, optional): Message
            containing the poll to which the option was deleted, if known.
            Note that the Message object in this field will not contain the
            :attr:`~telegram.Message.reply_to_message` field even if it itself is a reply.
        option_text_entities (Sequence[:class:`telegram.MessageEntity`], optional): Special
            entities that appear in the option_text.

    Attributes:
        option_persistent_id (:obj:`str`): Unique identifier of the deleted option.
        option_text (:obj:`str`): Option text.
        poll_message (:class:`telegram.MaybeInaccessibleMessage`): Optional. Message
            containing the poll to which the option was deleted, if known.
            Note that the Message object in this field will not contain the
            :attr:`~telegram.Message.reply_to_message` field even if it itself is a reply.
        option_text_entities (tuple[:class:`telegram.MessageEntity`]): Optional. Special
            entities that appear in the option_text.
    """

    # Required
    option_persistent_id: str = tg_field(compare=True)
    option_text: str = tg_field(compare=True)
    # Optional
    poll_message: "MaybeInaccessibleMessage | None" = tg_field(default=None)
    option_text_entities: tuple[MessageEntity, ...] = tg_field(
        default=None, converter=parse_sequence_arg
    )

    def parse_option_text_entity(self, entity: MessageEntity) -> str:
        """Returns the text in :attr:`option_text`
        from a given :class:`telegram.MessageEntity` of :attr:`option_text_entities`.

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice ``Message.text`` with the offset and length.)

        Args:
            entity (:class:`telegram.MessageEntity`): The entity to extract the text from. It must
                be an entity that belongs to :attr:`option_text_entities`.

        Returns:
            :obj:`str`: The text of the given entity.
        """
        return parse_message_entity(self.option_text, entity)

    def parse_option_text_entities(
        self, types: list[str] | None = None
    ) -> dict[MessageEntity, str]:
        """
        Returns a :obj:`dict` that maps :class:`telegram.MessageEntity` to :obj:`str`.
        It contains entities from this polls option text filtered by their ``type`` attribute as
        the key, and the text that each entity belongs to as the value of the :obj:`dict`.

        Note:
            This method should always be used instead of the :attr:`option_text_entities`
            attribute, since it calculates the correct substring from the message text based on
            UTF-16 codepoints. See :attr:`parse_entity` for more info.

        Args:
            types (list[:obj:`str`], optional): List of ``MessageEntity`` types as strings. If the
                    ``type`` attribute of an entity is contained in this list, it will be returned.
                    Defaults to :attr:`telegram.MessageEntity.ALL_TYPES`.

        Returns:
            dict[:class:`telegram.MessageEntity`, :obj:`str`]: A dictionary of entities mapped to
            the text that belongs to them, calculated based on UTF-16 codepoints.
        """
        return parse_message_entities(self.option_text, self.option_text_entities, types)


@tg_dataclass()
class Poll(TelegramObject):
    """
    This object contains information about a poll.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Examples:
        :any:`Poll Bot <examples.pollbot>`

    Args:
        id (:obj:`str`): Unique poll identifier.
        question (:obj:`str`): Poll question, :tg-const:`telegram.Poll.MIN_QUESTION_LENGTH`-
            :tg-const:`telegram.Poll.MAX_QUESTION_LENGTH` characters.
        options (Sequence[:class:`~telegram.PollOption`]): List of poll options.

            .. versionchanged:: 20.0
                |sequenceclassargs|
        is_closed (:obj:`bool`): :obj:`True`, if the poll is closed.
        is_anonymous (:obj:`bool`): :obj:`True`, if the poll is anonymous.
        type (:obj:`str`): Poll type, currently can be :attr:`REGULAR` or :attr:`QUIZ`.
        allows_multiple_answers (:obj:`bool`): :obj:`True`, if the poll allows multiple answers.
        allows_revoting (:obj:`bool`): :obj:`True`, if the poll allows to
            change the chosen answer options.

            .. versionadded:: 22.8
        members_only (:obj:`bool`): :obj:`True`, if voting is limited to users who have been
            members of the chat where the poll was originally sent for more than
            :tg-const:`telegram.Poll.MIN_MEMBERSHIP_HOURS` hours.

            .. versionadded:: 22.8
        explanation (:obj:`str`, optional): Text that is shown when a user chooses an incorrect
            answer or taps on the lamp icon in a quiz-style poll,
            0-:tg-const:`telegram.Poll.MAX_EXPLANATION_LENGTH` characters.
        explanation_entities (Sequence[:class:`telegram.MessageEntity`], optional): Special
            entities like usernames, URLs, bot commands, etc. that appear in the
            :attr:`explanation`. This list is empty if the message does not contain explanation
            entities.

            .. versionchanged:: 20.0

               * This attribute is now always a (possibly empty) list and never :obj:`None`.
               * |sequenceclassargs|
        explanation_media (:class:`telegram.PollMedia`, optional): Media added to the quiz
            explanation.

            .. versionadded:: 22.8
        open_period (:obj:`int` | :class:`datetime.timedelta`, optional): Amount of time in seconds
            the poll will be active after creation.

            .. versionchanged:: v22.2
                |time-period-input|
        close_date (:obj:`datetime.datetime`, optional): Point in time (Unix timestamp) when the
            poll will be automatically closed. Converted to :obj:`datetime.datetime`.

            .. versionchanged:: 20.3
                |datetime_localization|
        question_entities (Sequence[:class:`telegram.MessageEntity`], optional): Special entities
            that appear in the :attr:`question`. Currently, only custom emoji entities are allowed
            in poll questions.

            .. versionadded:: 21.2
        correct_option_ids (Sequence[:class:`int`], optional): Array of 0-based identifiers of
            the correct answer options. Available only for polls in quiz mode which are closed or
            were sent (not forwarded) by the bot or to the private chat with the bot.

            .. versionadded:: 22.8
        country_codes (Sequence[:obj:`str`], optional): A list of two-letter ``ISO 3166-1 alpha-2``
            country codes indicating the countries from which users can vote in the poll. The
            country code ``"FT"`` is used for users with anonymous numbers. If omitted, then users
            from any country can participate in the poll.

            .. versionadded:: 22.8
        description (:obj:`str`, optional): Description of the poll;
            for polls inside the :class:`~telegram.Message` object only.

            .. versionadded:: 22.8
        description_entities (Sequence[:class:`telegram.MessageEntity`], optional): Special
            entities like usernames, URLs, bot commands, etc. that appear in the description

            .. versionadded:: 22.8
        media (:class:`telegram.PollMedia`, optional): Media added to the poll description;
            for polls inside the :class:`~telegram.Message` object only.

            .. versionadded:: 22.8

    Attributes:
        id (:obj:`str`): Unique poll identifier.
        question (:obj:`str`): Poll question, :tg-const:`telegram.Poll.MIN_QUESTION_LENGTH`-
            :tg-const:`telegram.Poll.MAX_QUESTION_LENGTH` characters.
        options (tuple[:class:`~telegram.PollOption`]): List of poll options.

            .. versionchanged:: 20.0
                |tupleclassattrs|
        total_voter_count (:obj:`int`): Total number of users that voted in the poll.
        is_closed (:obj:`bool`): :obj:`True`, if the poll is closed.
        is_anonymous (:obj:`bool`): :obj:`True`, if the poll is anonymous.
        type (:obj:`str`): Poll type, currently can be :attr:`REGULAR` or :attr:`QUIZ`.
        allows_multiple_answers (:obj:`bool`): :obj:`True`, if the poll allows multiple answers.
        allows_revoting (:obj:`bool`): :obj:`True`, if the poll
            allows to change the chosen answer options

            .. versionadded:: 22.8
        members_only (:obj:`bool`): :obj:`True`, if voting is limited to users who have been
            members of the chat where the poll was originally sent for more than
            :tg-const:`telegram.Poll.MIN_MEMBERSHIP_HOURS` hours.

            .. versionadded:: 22.8
        explanation (:obj:`str`): Optional. Text that is shown when a user chooses an incorrect
            answer or taps on the lamp icon in a quiz-style poll,
            0-:tg-const:`telegram.Poll.MAX_EXPLANATION_LENGTH` characters.
        explanation_entities (tuple[:class:`telegram.MessageEntity`]): Special entities
            like usernames, URLs, bot commands, etc. that appear in the :attr:`explanation`.
            This list is empty if the message does not contain explanation entities.

            .. versionchanged:: 20.0
                |tupleclassattrs|

            .. versionchanged:: 20.0
               This attribute is now always a (possibly empty) list and never :obj:`None`.
        explanation_media (:class:`telegram.PollMedia`): Optional. Media added to the quiz
            explanation.

            .. versionadded:: 22.8
        open_period (:obj:`int` | :class:`datetime.timedelta`): Optional. Amount of time in seconds
            the poll will be active after creation.

            .. deprecated:: v22.2
                |time-period-int-deprecated|
        close_date (:obj:`datetime.datetime`): Optional. Point in time when the poll will be
            automatically closed.

            .. versionchanged:: 20.3
                |datetime_localization|
        question_entities (tuple[:class:`telegram.MessageEntity`]): Special entities
            that appear in the :attr:`question`. Currently, only custom emoji entities are allowed
            in poll questions.
            This list is empty if the question does not contain entities.

            .. versionadded:: 21.2
        correct_option_ids (tuple[:class:`int`]): Array of 0-based identifiers of the
            correct answer options. Available only for polls in quiz mode which are closed or were
            sent (not forwarded) by the bot or to the private chat with the bot.

            .. versionadded:: 22.8
        country_codes (tuple[:obj:`str`]): Optional. A list of two-letter ``ISO 3166-1 alpha-2``
            country codes indicating the countries from which users can vote in the poll. The
            country code ``"FT"`` is used for users with anonymous numbers. If omitted, then users
            from any country can participate in the poll.

            .. versionadded:: 22.8
        description (:obj:`str`): Optional. Description of the poll;
            for polls inside the Message object only

            .. versionadded:: 22.8
        description_entities (tuple[:class:`telegram.MessageEntity`]): Special
            entities like usernames, URLs, bot commands, etc. that appear in the description

            .. versionadded:: 22.8
        media (:class:`telegram.PollMedia`): Optional. Media added to the poll description;
            for polls inside the Message object only.

            .. versionadded:: 22.8

    """

    @staticmethod
    def _type_converter(value: str) -> str:
        return enum.get_member(constants.PollType, value, value)

    # Required
    id: str = tg_field(compare=True)
    question: str = tg_field()
    options: tuple[PollOption, ...] = tg_field(converter=parse_sequence_arg)
    total_voter_count: int = tg_field()
    is_closed: bool = tg_field()
    is_anonymous: bool = tg_field()
    type: str = tg_field(converter=_type_converter)
    allows_multiple_answers: bool = tg_field()
    allows_revoting: bool = tg_field()
    members_only: bool = tg_field()
    # Optional
    explanation: str | None = tg_field(default=None)
    explanation_entities: tuple[MessageEntity, ...] = tg_field(
        default=None, converter=parse_sequence_arg
    )
    _open_period: dtm.timedelta | None = tg_field(
        default=None, alias="open_period", converter=to_timedelta
    )
    close_date: dtm.datetime | None = tg_field(default=None)
    question_entities: tuple[MessageEntity, ...] = tg_field(
        default=None, converter=parse_sequence_arg
    )
    correct_option_ids: tuple[int, ...] = tg_field(default=None, converter=parse_sequence_arg)
    description: str | None = tg_field(default=None)
    description_entities: tuple[MessageEntity, ...] = tg_field(
        default=None, converter=parse_sequence_arg
    )
    country_codes: tuple[str, ...] = tg_field(default=None, converter=parse_sequence_arg)
    media: PollMedia | None = tg_field(default=None)
    explanation_media: PollMedia | None = tg_field(default=None)

    @property
    def open_period(self) -> int | dtm.timedelta | None:
        return get_timedelta_value(self._open_period, attribute="open_period")

    def parse_explanation_entity(self, entity: MessageEntity) -> str:
        """Returns the text in :attr:`explanation` from a given :class:`telegram.MessageEntity` of
        :attr:`explanation_entities`.

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice ``Message.text`` with the offset and length.)

        Args:
            entity (:class:`telegram.MessageEntity`): The entity to extract the text from. It must
                be an entity that belongs to :attr:`explanation_entities`.

        Returns:
            :obj:`str`: The text of the given entity.

        Raises:
            RuntimeError: If the poll has no explanation.

        """
        if not self.explanation:
            raise RuntimeError("This Poll has no 'explanation'.")

        return parse_message_entity(self.explanation, entity)

    def parse_explanation_entities(
        self, types: list[str] | None = None
    ) -> dict[MessageEntity, str]:
        """
        Returns a :obj:`dict` that maps :class:`telegram.MessageEntity` to :obj:`str`.
        It contains entities from this polls explanation filtered by their ``type`` attribute as
        the key, and the text that each entity belongs to as the value of the :obj:`dict`.

        Note:
            This method should always be used instead of the :attr:`explanation_entities`
            attribute, since it calculates the correct substring from the message text based on
            UTF-16 codepoints. See :attr:`parse_explanation_entity` for more info.

        Args:
            types (list[:obj:`str`], optional): List of ``MessageEntity`` types as strings. If the
                    ``type`` attribute of an entity is contained in this list, it will be returned.
                    Defaults to :attr:`telegram.MessageEntity.ALL_TYPES`.

        Returns:
            dict[:class:`telegram.MessageEntity`, :obj:`str`]: A dictionary of entities mapped to
            the text that belongs to them, calculated based on UTF-16 codepoints.

        Raises:
            RuntimeError: If the poll has no explanation.

        """
        if not self.explanation:
            raise RuntimeError("This Poll has no 'explanation'.")

        return parse_message_entities(self.explanation, self.explanation_entities, types)

    def parse_question_entity(self, entity: MessageEntity) -> str:
        """Returns the text in :attr:`question` from a given :class:`telegram.MessageEntity` of
        :attr:`question_entities`.

        .. versionadded:: 21.2

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice ``Message.text`` with the offset and length.)

        Args:
            entity (:class:`telegram.MessageEntity`): The entity to extract the text from. It must
                be an entity that belongs to :attr:`question_entities`.

        Returns:
            :obj:`str`: The text of the given entity.
        """
        return parse_message_entity(self.question, entity)

    def parse_question_entities(self, types: list[str] | None = None) -> dict[MessageEntity, str]:
        """
        Returns a :obj:`dict` that maps :class:`telegram.MessageEntity` to :obj:`str`.
        It contains entities from this polls question filtered by their ``type`` attribute as
        the key, and the text that each entity belongs to as the value of the :obj:`dict`.

        .. versionadded:: 21.2

        Note:
            This method should always be used instead of the :attr:`question_entities`
            attribute, since it calculates the correct substring from the message text based on
            UTF-16 codepoints. See :attr:`parse_question_entity` for more info.

        Args:
            types (list[:obj:`str`], optional): List of ``MessageEntity`` types as strings. If the
                    ``type`` attribute of an entity is contained in this list, it will be returned.
                    Defaults to :attr:`telegram.MessageEntity.ALL_TYPES`.

        Returns:
            dict[:class:`telegram.MessageEntity`, :obj:`str`]: A dictionary of entities mapped to
            the text that belongs to them, calculated based on UTF-16 codepoints.

        """
        return parse_message_entities(self.question, self.question_entities, types)

    def parse_description_entity(self, entity: MessageEntity) -> str:
        """Returns the text in :attr:`description` from a given :class:`telegram.MessageEntity` of
        :attr:`description_entities`.

        .. versionadded:: 22.8

        Note:
            This method is present because Telegram calculates the offset and length in
            UTF-16 codepoint pairs, which some versions of Python don't handle automatically.
            (That is, you can't just slice ``Message.text`` with the offset and length.)

        Args:
            entity (:class:`telegram.MessageEntity`): The entity to extract the text from. It must
                be an entity that belongs to :attr:`description_entities`.

        Returns:
            :obj:`str`: The text of the given entity.

        Raises:
            RuntimeError: If the poll has no description.

        """
        if not self.description:
            raise RuntimeError("This Poll has no 'description'.")

        return parse_message_entity(self.description, entity)

    def parse_description_entities(
        self, types: list[str] | None = None
    ) -> dict[MessageEntity, str]:
        """
        Returns a :obj:`dict` that maps :class:`telegram.MessageEntity` to :obj:`str`.
        It contains entities from this polls description filtered by their ``type`` attribute as
        the key, and the text that each entity belongs to as the value of the :obj:`dict`.

        .. versionadded:: 22.8

        Note:
            This method should always be used instead of the :attr:`description_entities`
            attribute, since it calculates the correct substring from the message text based on
            UTF-16 codepoints. See :attr:`parse_description_entity` for more info.

        Args:
            types (list[:obj:`str`], optional): List of ``MessageEntity`` types as strings. If the
                    ``type`` attribute of an entity is contained in this list, it will be returned.
                    Defaults to :attr:`telegram.MessageEntity.ALL_TYPES`.
        Returns:
            dict[:class:`telegram.MessageEntity`, :obj:`str`]: A dictionary of entities
            mapped to the text that belongs to them, calculated based on UTF-16 codepoints.
        Raises:
            RuntimeError: If the poll has no description.
        """
        if not self.description:
            raise RuntimeError("This Poll has no 'description'.")

        return parse_message_entities(self.description, self.description_entities, types)

    REGULAR: ClassVar[str] = constants.PollType.REGULAR
    """:const:`telegram.constants.PollType.REGULAR`"""
    QUIZ: ClassVar[str] = constants.PollType.QUIZ
    """:const:`telegram.constants.PollType.QUIZ`"""
    MAX_EXPLANATION_LENGTH: ClassVar[int] = constants.PollLimit.MAX_EXPLANATION_LENGTH
    """:const:`telegram.constants.PollLimit.MAX_EXPLANATION_LENGTH`

    .. versionadded:: 20.0
    """
    MAX_EXPLANATION_LINE_FEEDS: ClassVar[int] = constants.PollLimit.MAX_EXPLANATION_LINE_FEEDS
    """:const:`telegram.constants.PollLimit.MAX_EXPLANATION_LINE_FEEDS`

    .. versionadded:: 20.0
    """
    MIN_OPEN_PERIOD: ClassVar[int] = constants.PollLimit.MIN_OPEN_PERIOD
    """:const:`telegram.constants.PollLimit.MIN_OPEN_PERIOD`

    .. versionadded:: 20.0
    """
    MAX_OPEN_PERIOD: ClassVar[int] = constants.PollLimit.MAX_OPEN_PERIOD
    """:const:`telegram.constants.PollLimit.MAX_OPEN_PERIOD`

    .. versionadded:: 20.0
    """
    MIN_QUESTION_LENGTH: ClassVar[int] = constants.PollLimit.MIN_QUESTION_LENGTH
    """:const:`telegram.constants.PollLimit.MIN_QUESTION_LENGTH`

    .. versionadded:: 20.0
    """
    MAX_QUESTION_LENGTH: ClassVar[int] = constants.PollLimit.MAX_QUESTION_LENGTH
    """:const:`telegram.constants.PollLimit.MAX_QUESTION_LENGTH`

    .. versionadded:: 20.0
    """
    MIN_OPTION_LENGTH: ClassVar[int] = constants.PollLimit.MIN_OPTION_LENGTH
    """:const:`telegram.constants.PollLimit.MIN_OPTION_LENGTH`

    .. versionadded:: 20.0
    """
    MAX_OPTION_LENGTH: ClassVar[int] = constants.PollLimit.MAX_OPTION_LENGTH
    """:const:`telegram.constants.PollLimit.MAX_OPTION_LENGTH`

    .. versionadded:: 20.0
    """
    MIN_OPTION_NUMBER: ClassVar[int] = constants.PollLimit.MIN_OPTION_NUMBER
    """:const:`telegram.constants.PollLimit.MIN_OPTION_NUMBER`

    .. versionadded:: 20.0
    """
    MAX_OPTION_NUMBER: ClassVar[int] = constants.PollLimit.MAX_OPTION_NUMBER
    """:const:`telegram.constants.PollLimit.MAX_OPTION_NUMBER`

    .. versionadded:: 20.0
    """
    MAX_DESCRIPTION_CHARACTERS: ClassVar[int] = constants.PollLimit.MAX_DESCRIPTION_CHARACTERS
    """:const:`telegram.constants.PollLimit.MAX_DESCRIPTION_CHARACTERS`

    .. versionadded:: 22.8
    """
    MIN_MEMBERSHIP_HOURS: ClassVar[int] = constants.PollLimit.MIN_MEMBERSHIP_HOURS
    """:const:`telegram.constants.PollLimit.MIN_MEMBERSHIP_HOURS`

    .. versionadded:: 22.8
    """
