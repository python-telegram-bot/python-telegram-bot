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
from collections.abc import Sequence
from typing import TYPE_CHECKING, Final

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
    de_json_optional,
    de_list_optional,
    parse_sequence_arg,
    to_timedelta,
)
from telegram._utils.datetime import (
    extract_tzinfo_from_defaults,
    from_timestamp,
    get_timedelta_value,
)
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.entities import parse_message_entities, parse_message_entity
from telegram._utils.types import JSONDict, ODVInput, TimePeriod
from telegram._utils.warnings import warn
from telegram.warnings import PTBDeprecationWarning

if TYPE_CHECKING:
    from telegram import Bot, InputPollOptionMedia, MaybeInaccessibleMessage


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

    __slots__ = (
        "animation",
        "audio",
        "document",
        "live_photo",
        "location",
        "photo",
        "sticker",
        "venue",
        "video",
    )

    def __init__(
        self,
        animation: Animation | None = None,
        audio: Audio | None = None,
        document: Document | None = None,
        live_photo: LivePhoto | None = None,
        location: Location | None = None,
        photo: Sequence[PhotoSize] | None = None,
        sticker: Sticker | None = None,
        venue: Venue | None = None,
        video: Video | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.animation: Animation | None = animation
        self.audio: Audio | None = audio
        self.document: Document | None = document
        self.live_photo: LivePhoto | None = live_photo
        self.location: Location | None = location
        self.photo: tuple[PhotoSize, ...] = parse_sequence_arg(photo)
        self.sticker: Sticker | None = sticker
        self.venue: Venue | None = venue
        self.video: Video | None = video

        self._id_attrs = (
            self.animation,
            self.audio,
            self.document,
            self.live_photo,
            self.location,
            self.photo,
            self.sticker,
            self.venue,
            self.video,
        )

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: "Bot | None" = None) -> "PollMedia":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["animation"] = de_json_optional(data.get("animation"), Animation, bot)
        data["audio"] = de_json_optional(data.get("audio"), Audio, bot)
        data["document"] = de_json_optional(data.get("document"), Document, bot)
        data["live_photo"] = de_json_optional(data.get("live_photo"), LivePhoto, bot)
        data["location"] = de_json_optional(data.get("location"), Location, bot)
        data["photo"] = de_list_optional(data.get("photo"), PhotoSize, bot)
        data["sticker"] = de_json_optional(data.get("sticker"), Sticker, bot)
        data["venue"] = de_json_optional(data.get("venue"), Venue, bot)
        data["video"] = de_json_optional(data.get("video"), Video, bot)

        return super().de_json(data=data, bot=bot)


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

    __slots__ = ("media", "text", "text_entities", "text_parse_mode")

    def __init__(
        self,
        text: str,
        text_parse_mode: ODVInput[str] = DEFAULT_NONE,
        text_entities: Sequence[MessageEntity] | None = None,
        media: "InputPollOptionMedia | None" = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.text: str = text
        self.text_parse_mode: ODVInput[str] = text_parse_mode
        self.text_entities: tuple[MessageEntity, ...] = parse_sequence_arg(text_entities)
        self.media: InputPollOptionMedia | None = media

        self._id_attrs = (self.text,)

        self._freeze()

    # tags: deprecated 22.8
    @classmethod
    def de_json(cls, data: JSONDict, bot: "Bot | None" = None) -> "InputPollOption":
        """See :meth:`telegram.TelegramObject.de_json`. The :paramref:`media` field will
        not be included for deserialization.

        .. deprecated:: 22.8
            This class is input only and will be removed in the next version.
        """
        warn(
            PTBDeprecationWarning(
                "22.8",
                "`InputPollOption.de_json` is deprecated. This class is input only and will be "
                "removed in the next version. The `media` field will not be included for "
                "deserialization.",
            ),
            stacklevel=2,
        )
        data = cls._parse_data(data)

        data["text_entities"] = de_list_optional(data.get("text_entities"), MessageEntity, bot)

        return super().de_json(data=data, bot=bot)


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

    __slots__ = (
        "added_by_chat",
        "added_by_user",
        "addition_date",
        "media",
        "persistent_id",
        "text",
        "text_entities",
        "voter_count",
    )

    def __init__(
        self,
        text: str,
        voter_count: int,
        text_entities: Sequence[MessageEntity] | None = None,
        added_by_user: User | None = None,
        added_by_chat: Chat | None = None,
        addition_date: dtm.datetime | None = None,
        media: PollMedia | None = None,
        # tags: required in 22.8, bot api 9.6
        # temporarily optional to avoid breaking changes
        persistent_id: str | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        if persistent_id is None:
            raise TypeError("`persistent_id` is a required argument since Bot API 9.6")

        super().__init__(api_kwargs=api_kwargs)
        self.text: str = text
        self.voter_count: int = voter_count
        self.added_by_user: User | None = added_by_user
        self.added_by_chat: Chat | None = added_by_chat
        self.addition_date: dtm.datetime | None = addition_date
        self.persistent_id: str = persistent_id
        self.media: PollMedia | None = media

        self.text_entities: tuple[MessageEntity, ...] = parse_sequence_arg(text_entities)

        self._id_attrs = (self.text, self.voter_count, self.persistent_id)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: "Bot | None" = None) -> "PollOption":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        # Get the local timezone from the bot if it has defaults
        loc_tzinfo = extract_tzinfo_from_defaults(bot)

        data["text_entities"] = de_list_optional(data.get("text_entities"), MessageEntity, bot)
        data["added_by_user"] = de_json_optional(data.get("added_by_user"), User, bot)
        data["added_by_chat"] = de_json_optional(data.get("added_by_chat"), Chat, bot)
        data["addition_date"] = from_timestamp(data.get("addition_date"), tzinfo=loc_tzinfo)
        data["media"] = de_json_optional(data.get("media"), PollMedia, bot)

        return super().de_json(data=data, bot=bot)

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

    __slots__ = ("option_ids", "option_persistent_ids", "poll_id", "user", "voter_chat")

    def __init__(
        self,
        poll_id: str,
        option_ids: Sequence[int],
        user: User | None = None,
        voter_chat: Chat | None = None,
        # tags: required in 22.8, bot api 9.6
        # temporarily optional to avoid breaking changes
        option_persistent_ids: Sequence[str] | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        if option_persistent_ids is None:
            raise TypeError("`option_persistent_ids` is a required argument since Bot API 9.6")

        super().__init__(api_kwargs=api_kwargs)
        self.poll_id: str = poll_id
        self.voter_chat: Chat | None = voter_chat
        self.option_ids: tuple[int, ...] = parse_sequence_arg(option_ids)
        self.user: User | None = user
        self.option_persistent_ids: tuple[str, ...] = parse_sequence_arg(option_persistent_ids)

        self._id_attrs = (
            self.poll_id,
            self.option_ids,
            self.user,
            self.voter_chat,
        )

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: "Bot | None" = None) -> "PollAnswer":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["user"] = de_json_optional(data.get("user"), User, bot)
        data["voter_chat"] = de_json_optional(data.get("voter_chat"), Chat, bot)

        return super().de_json(data=data, bot=bot)


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

    __slots__ = ("option_persistent_id", "option_text", "option_text_entities", "poll_message")

    def __init__(
        self,
        option_persistent_id: str,
        option_text: str,
        poll_message: "MaybeInaccessibleMessage | None" = None,
        option_text_entities: Sequence[MessageEntity] | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.option_persistent_id: str = option_persistent_id
        self.option_text: str = option_text
        self.poll_message: MaybeInaccessibleMessage | None = poll_message

        self.option_text_entities: tuple[MessageEntity, ...] = parse_sequence_arg(
            option_text_entities
        )

        self._id_attrs = (self.option_persistent_id, self.option_text)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: "Bot | None" = None) -> "PollOptionAdded":
        """See :meth:`telegram.TelegramObject.de_json`."""
        from telegram._message import (  # pylint: disable=import-outside-toplevel  # noqa: PLC0415
            MaybeInaccessibleMessage,
        )

        data = cls._parse_data(data)

        data["poll_message"] = de_json_optional(
            data.get("poll_message"), MaybeInaccessibleMessage, bot
        )
        data["option_text_entities"] = de_list_optional(
            data.get("option_text_entities"), MessageEntity, bot
        )

        return super().de_json(data=data, bot=bot)

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

    __slots__ = ("option_persistent_id", "option_text", "option_text_entities", "poll_message")

    def __init__(
        self,
        option_persistent_id: str,
        option_text: str,
        poll_message: "MaybeInaccessibleMessage | None" = None,
        option_text_entities: Sequence[MessageEntity] | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.option_persistent_id: str = option_persistent_id
        self.option_text: str = option_text
        self.poll_message: MaybeInaccessibleMessage | None = poll_message

        self.option_text_entities: tuple[MessageEntity, ...] = parse_sequence_arg(
            option_text_entities
        )

        self._id_attrs = (self.option_persistent_id, self.option_text)

        self._freeze()

    @classmethod
    def de_json(cls, data: JSONDict, bot: "Bot | None" = None) -> "PollOptionDeleted":
        """See :meth:`telegram.TelegramObject.de_json`."""
        from telegram._message import (  # pylint: disable=import-outside-toplevel  # noqa: PLC0415
            MaybeInaccessibleMessage,
        )

        data = cls._parse_data(data)

        data["poll_message"] = de_json_optional(
            data.get("poll_message"), MaybeInaccessibleMessage, bot
        )
        data["option_text_entities"] = de_list_optional(
            data.get("option_text_entities"), MessageEntity, bot
        )

        return super().de_json(data=data, bot=bot)

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
        members_only (:obj:`bool`): :obj:`True`, if voting is limited to users who have been
            members of the chat where the poll was originally sent for more than
            :tg-const:`telegram.Poll.MIN_MEMBERSHIP_HOURS` hours.

            .. versionadded:: 22.8
        correct_option_id (:obj:`int`, optional): A zero based identifier of the correct answer
            option. Available only for closed polls in the quiz mode, which were sent
            (not forwarded), by the bot or to a private chat with the bot.

            .. deprecated:: 22.8
                Use :paramref:`correct_option_ids` instead.
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
        allows_revoting (:obj:`bool`, optional): :obj:`True`, if the poll allows to
            change the chosenanswer options.

            .. versionadded:: 22.8
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
        allows_revoting (:obj:`bool`): :obj:`True`, if the poll
            allows to change the chosenanswer options

            .. versionadded:: 22.8
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

    __slots__ = (
        "_open_period",
        "allows_multiple_answers",
        "allows_revoting",
        "close_date",
        "correct_option_ids",
        "country_codes",
        "description",
        "description_entities",
        "explanation",
        "explanation_entities",
        "explanation_media",
        "id",
        "is_anonymous",
        "is_closed",
        "media",
        "members_only",
        "options",
        "question",
        "question_entities",
        "total_voter_count",
        "type",
    )

    def __init__(
        self,
        id: str,  # pylint: disable=redefined-builtin
        question: str,
        options: Sequence[PollOption],
        total_voter_count: int,
        is_closed: bool,
        is_anonymous: bool,
        type: str,  # pylint: disable=redefined-builtin
        allows_multiple_answers: bool,
        # tags: deprecated 22.8
        # Removed in bot api 9.6:
        correct_option_id: int | None = None,
        # ---
        explanation: str | None = None,
        explanation_entities: Sequence[MessageEntity] | None = None,
        open_period: TimePeriod | None = None,
        close_date: dtm.datetime | None = None,
        question_entities: Sequence[MessageEntity] | None = None,
        # tags: required in 22.8
        # temporarily optional to avoid breaking changes
        allows_revoting: bool | None = None,
        members_only: bool | None = None,
        # ---
        correct_option_ids: Sequence[int] | None = None,
        description: str | None = None,
        description_entities: Sequence[MessageEntity] | None = None,
        country_codes: Sequence[str] | None = None,
        media: PollMedia | None = None,
        explanation_media: PollMedia | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        if allows_revoting is None:
            raise TypeError("`allows_revoting` is a required argument since Bot API 9.6")

        if members_only is None:
            raise TypeError("`members_only` is a required argument since Bot API 10.0")

        super().__init__(api_kwargs=api_kwargs)
        self.id: str = id
        self.question: str = question
        self.options: tuple[PollOption, ...] = parse_sequence_arg(options)
        self.total_voter_count: int = total_voter_count
        self.is_closed: bool = is_closed
        self.is_anonymous: bool = is_anonymous
        self.type: str = enum.get_member(constants.PollType, type, type)
        self.allows_multiple_answers: bool = allows_multiple_answers
        self.allows_revoting: bool = allows_revoting
        self.members_only: bool = members_only

        # tag: deprecated 22.8
        if correct_option_id is not None:
            warn(
                PTBDeprecationWarning(
                    "22.8",
                    "The parameter `correct_option_id` is deprecated. "
                    "Use `correct_option_ids` instead.",
                ),
                stacklevel=2,
            )
            if correct_option_ids is None:
                correct_option_ids = [correct_option_id]

        self.correct_option_ids: tuple[int, ...] = parse_sequence_arg(correct_option_ids)
        self.description: str | None = description
        self.description_entities: tuple[MessageEntity, ...] = parse_sequence_arg(
            description_entities
        )
        self.explanation: str | None = explanation
        self.explanation_entities: tuple[MessageEntity, ...] = parse_sequence_arg(
            explanation_entities
        )
        self._open_period: dtm.timedelta | None = to_timedelta(open_period)
        self.close_date: dtm.datetime | None = close_date
        self.question_entities: tuple[MessageEntity, ...] = parse_sequence_arg(question_entities)
        self.country_codes: tuple[str, ...] = parse_sequence_arg(country_codes)
        self.media: PollMedia | None = media
        self.explanation_media: PollMedia | None = explanation_media

        self._id_attrs = (self.id,)

        self._freeze()

    @property
    def open_period(self) -> int | dtm.timedelta | None:
        return get_timedelta_value(self._open_period, attribute="open_period")

    @classmethod
    def de_json(cls, data: JSONDict, bot: "Bot | None" = None) -> "Poll":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        # Get the local timezone from the bot if it has defaults
        loc_tzinfo = extract_tzinfo_from_defaults(bot)

        data["options"] = de_list_optional(data.get("options"), PollOption, bot)
        data["explanation_entities"] = de_list_optional(
            data.get("explanation_entities"), MessageEntity, bot
        )
        data["close_date"] = from_timestamp(data.get("close_date"), tzinfo=loc_tzinfo)
        data["question_entities"] = de_list_optional(
            data.get("question_entities"), MessageEntity, bot
        )
        data["description_entities"] = de_list_optional(
            data.get("description_entities"), MessageEntity, bot
        )
        data["media"] = de_json_optional(data.get("media"), PollMedia, bot)
        data["explanation_media"] = de_json_optional(data.get("explanation_media"), PollMedia, bot)

        return super().de_json(data=data, bot=bot)

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

    @property
    def correct_option_id(self) -> int | None:
        """A zero based identifier of the correct answer
        option. Available only for closed polls in the quiz mode, which were sent
        (not forwarded), by the bot or to a private chat with the bot.

        .. deprecated:: 22.8
            Use :attr:`correct_option_ids` instead.
        """
        warn(
            PTBDeprecationWarning(
                "22.8",
                "The attribute `correct_option_id` is deprecated. "
                "Use `correct_option_ids` instead.",
            ),
            stacklevel=2,
        )
        return self.correct_option_ids[0] if self.correct_option_ids else None

    REGULAR: Final[str] = constants.PollType.REGULAR
    """:const:`telegram.constants.PollType.REGULAR`"""
    QUIZ: Final[str] = constants.PollType.QUIZ
    """:const:`telegram.constants.PollType.QUIZ`"""
    MAX_EXPLANATION_LENGTH: Final[int] = constants.PollLimit.MAX_EXPLANATION_LENGTH
    """:const:`telegram.constants.PollLimit.MAX_EXPLANATION_LENGTH`

    .. versionadded:: 20.0
    """
    MAX_EXPLANATION_LINE_FEEDS: Final[int] = constants.PollLimit.MAX_EXPLANATION_LINE_FEEDS
    """:const:`telegram.constants.PollLimit.MAX_EXPLANATION_LINE_FEEDS`

    .. versionadded:: 20.0
    """
    MIN_OPEN_PERIOD: Final[int] = constants.PollLimit.MIN_OPEN_PERIOD
    """:const:`telegram.constants.PollLimit.MIN_OPEN_PERIOD`

    .. versionadded:: 20.0
    """
    MAX_OPEN_PERIOD: Final[int] = constants.PollLimit.MAX_OPEN_PERIOD
    """:const:`telegram.constants.PollLimit.MAX_OPEN_PERIOD`

    .. versionadded:: 20.0
    """
    MIN_QUESTION_LENGTH: Final[int] = constants.PollLimit.MIN_QUESTION_LENGTH
    """:const:`telegram.constants.PollLimit.MIN_QUESTION_LENGTH`

    .. versionadded:: 20.0
    """
    MAX_QUESTION_LENGTH: Final[int] = constants.PollLimit.MAX_QUESTION_LENGTH
    """:const:`telegram.constants.PollLimit.MAX_QUESTION_LENGTH`

    .. versionadded:: 20.0
    """
    MIN_OPTION_LENGTH: Final[int] = constants.PollLimit.MIN_OPTION_LENGTH
    """:const:`telegram.constants.PollLimit.MIN_OPTION_LENGTH`

    .. versionadded:: 20.0
    """
    MAX_OPTION_LENGTH: Final[int] = constants.PollLimit.MAX_OPTION_LENGTH
    """:const:`telegram.constants.PollLimit.MAX_OPTION_LENGTH`

    .. versionadded:: 20.0
    """
    MIN_OPTION_NUMBER: Final[int] = constants.PollLimit.MIN_OPTION_NUMBER
    """:const:`telegram.constants.PollLimit.MIN_OPTION_NUMBER`

    .. versionadded:: 20.0
    """
    MAX_OPTION_NUMBER: Final[int] = constants.PollLimit.MAX_OPTION_NUMBER
    """:const:`telegram.constants.PollLimit.MAX_OPTION_NUMBER`

    .. versionadded:: 20.0
    """
    MAX_DESCRIPTION_CHARACTERS: Final[int] = constants.PollLimit.MAX_DESCRIPTION_CHARACTERS
    """:const:`telegram.constants.PollLimit.MAX_DESCRIPTION_CHARACTERS`

    .. versionadded:: 22.8
    """
    MIN_MEMBERSHIP_HOURS: Final[int] = constants.PollLimit.MIN_MEMBERSHIP_HOURS
    """:const:`telegram.constants.PollLimit.MIN_MEMBERSHIP_HOURS`

    .. versionadded:: 22.8
    """
