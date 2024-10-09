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
"""This modules contains objects that represents Telegram Replies"""
from collections.abc import Sequence
from typing import TYPE_CHECKING, Optional, Union

from telegram._chat import Chat
from telegram._dice import Dice
from telegram._files.animation import Animation
from telegram._files.audio import Audio
from telegram._files.contact import Contact
from telegram._files.document import Document
from telegram._files.location import Location
from telegram._files.photosize import PhotoSize
from telegram._files.sticker import Sticker
from telegram._files.venue import Venue
from telegram._files.video import Video
from telegram._files.videonote import VideoNote
from telegram._files.voice import Voice
from telegram._games.game import Game
from telegram._giveaway import Giveaway, GiveawayWinners
from telegram._linkpreviewoptions import LinkPreviewOptions
from telegram._messageentity import MessageEntity
from telegram._messageorigin import MessageOrigin
from telegram._paidmedia import PaidMediaInfo
from telegram._payment.invoice import Invoice
from telegram._poll import Poll
from telegram._story import Story
from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import JSONDict, ODVInput

if TYPE_CHECKING:
    from telegram import Bot


class ExternalReplyInfo(TelegramObject):
    """
    This object contains information about a message that is being replied to, which may
    come from another chat or forum topic.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`origin` is equal.

    .. versionadded:: 20.8

    Args:
        origin (:class:`telegram.MessageOrigin`): Origin of the message replied to by the given
            message.
        chat (:class:`telegram.Chat`, optional): Chat the original message belongs to. Available
            only if the chat is a supergroup or a channel.
        message_id (:obj:`int`, optional): Unique message identifier inside the original chat.
            Available only if the original chat is a supergroup or a channel.
        link_preview_options (:class:`telegram.LinkPreviewOptions`, optional): Options used for
            link preview generation for the original message, if it is a text message
        animation (:class:`telegram.Animation`, optional): Message is an animation, information
            about the animation.
        audio (:class:`telegram.Audio`, optional): Message is an audio file, information about the
            file.
        document (:class:`telegram.Document`, optional): Message is a general file, information
            about the file.
        photo (Sequence[:class:`telegram.PhotoSize`], optional): Message is a photo, available
            sizes of the photo.
        sticker (:class:`telegram.Sticker`, optional): Message is a sticker, information about the
            sticker.
        story (:class:`telegram.Story`, optional): Message is a forwarded story.
        video (:class:`telegram.Video`, optional): Message is a video, information about the video.
        video_note (:class:`telegram.VideoNote`, optional): Message is a `video note
            <https://telegram.org/blog/video-messages-and-telescope>`_, information about the video
            message.
        voice (:class:`telegram.Voice`, optional): Message is a voice message, information about
            the file.
        has_media_spoiler (:obj:`bool`, optional): :obj:`True`, if the message media is covered by
            a spoiler animation.
        contact (:class:`telegram.Contact`, optional): Message is a shared contact, information
            about the contact.
        dice (:class:`telegram.Dice`, optional): Message is a dice with random value.
        game (:Class:`telegram.Game`. optional): Message is a game, information about the game.
            :ref:`More about games >> <games-tree>`.
        giveaway (:class:`telegram.Giveaway`, optional): Message is a scheduled giveaway,
            information about the giveaway.
        giveaway_winners (:class:`telegram.GiveawayWinners`, optional): A giveaway with public
            winners was completed.
        invoice (:class:`telegram.Invoice`, optional): Message is an invoice for a payment,
            information about the invoice. :ref:`More about payments >> <payments-tree>`.
        location (:class:`telegram.Location`, optional): Message is a shared location, information
            about the location.
        poll (:class:`telegram.Poll`, optional): Message is a native poll, information about the
            poll.
        venue (:class:`telegram.Venue`, optional): Message is a venue, information about the venue.
        paid_media (:class:`telegram.PaidMedia`, optional): Message contains paid media;
            information about the paid media.

            .. versionadded:: 21.4

    Attributes:
        origin (:class:`telegram.MessageOrigin`): Origin of the message replied to by the given
            message.
        chat (:class:`telegram.Chat`): Optional. Chat the original message belongs to. Available
            only if the chat is a supergroup or a channel.
        message_id (:obj:`int`): Optional. Unique message identifier inside the original chat.
            Available only if the original chat is a supergroup or a channel.
        link_preview_options (:class:`telegram.LinkPreviewOptions`): Optional. Options used for
            link preview generation for the original message, if it is a text message.
        animation (:class:`telegram.Animation`): Optional. Message is an animation, information
            about the animation.
        audio (:class:`telegram.Audio`): Optional. Message is an audio file, information about the
            file.
        document (:class:`telegram.Document`): Optional. Message is a general file, information
            about the file.
        photo (tuple[:class:`telegram.PhotoSize`]): Optional. Message is a photo, available sizes
            of the photo.
        sticker (:class:`telegram.Sticker`): Optional. Message is a sticker, information about the
            sticker.
        story (:class:`telegram.Story`): Optional. Message is a forwarded story.
        video (:class:`telegram.Video`): Optional. Message is a video, information about the video.
        video_note (:class:`telegram.VideoNote`): Optional. Message is a `video note
            <https://telegram.org/blog/video-messages-and-telescope>`_, information about the video
            message.
        voice (:class:`telegram.Voice`): Optional. Message is a voice message, information about
            the file.
        has_media_spoiler (:obj:`bool`): Optional. :obj:`True`, if the message media is covered by
            a spoiler animation.
        contact (:class:`telegram.Contact`): Optional. Message is a shared contact, information
            about the contact.
        dice (:class:`telegram.Dice`): Optional. Message is a dice with random value.
        game (:Class:`telegram.Game`): Optional. Message is a game, information about the game.
            :ref:`More about games >> <games-tree>`.
        giveaway (:class:`telegram.Giveaway`): Optional. Message is a scheduled giveaway,
            information about the giveaway.
        giveaway_winners (:class:`telegram.GiveawayWinners`): Optional. A giveaway with public
            winners was completed.
        invoice (:class:`telegram.Invoice`): Optional. Message is an invoice for a payment,
            information about the invoice. :ref:`More about payments >> <payments-tree>`.
        location (:class:`telegram.Location`): Optional. Message is a shared location, information
            about the location.
        poll (:class:`telegram.Poll`): Optional. Message is a native poll, information about the
            poll.
        venue (:class:`telegram.Venue`): Optional. Message is a venue, information about the venue.
        paid_media (:class:`telegram.PaidMedia`): Optional. Message contains paid media;
            information about the paid media.

            .. versionadded:: 21.4
    """

    __slots__ = (
        "animation",
        "audio",
        "chat",
        "contact",
        "dice",
        "document",
        "game",
        "giveaway",
        "giveaway_winners",
        "has_media_spoiler",
        "invoice",
        "link_preview_options",
        "location",
        "message_id",
        "origin",
        "paid_media",
        "photo",
        "poll",
        "sticker",
        "story",
        "venue",
        "video",
        "video_note",
        "voice",
    )

    def __init__(
        self,
        origin: MessageOrigin,
        chat: Optional[Chat] = None,
        message_id: Optional[int] = None,
        link_preview_options: Optional[LinkPreviewOptions] = None,
        animation: Optional[Animation] = None,
        audio: Optional[Audio] = None,
        document: Optional[Document] = None,
        photo: Optional[Sequence[PhotoSize]] = None,
        sticker: Optional[Sticker] = None,
        story: Optional[Story] = None,
        video: Optional[Video] = None,
        video_note: Optional[VideoNote] = None,
        voice: Optional[Voice] = None,
        has_media_spoiler: Optional[bool] = None,
        contact: Optional[Contact] = None,
        dice: Optional[Dice] = None,
        game: Optional[Game] = None,
        giveaway: Optional[Giveaway] = None,
        giveaway_winners: Optional[GiveawayWinners] = None,
        invoice: Optional[Invoice] = None,
        location: Optional[Location] = None,
        poll: Optional[Poll] = None,
        venue: Optional[Venue] = None,
        paid_media: Optional[PaidMediaInfo] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)

        self.origin: MessageOrigin = origin
        self.chat: Optional[Chat] = chat
        self.message_id: Optional[int] = message_id
        self.link_preview_options: Optional[LinkPreviewOptions] = link_preview_options
        self.animation: Optional[Animation] = animation
        self.audio: Optional[Audio] = audio
        self.document: Optional[Document] = document
        self.photo: Optional[tuple[PhotoSize, ...]] = parse_sequence_arg(photo)
        self.sticker: Optional[Sticker] = sticker
        self.story: Optional[Story] = story
        self.video: Optional[Video] = video
        self.video_note: Optional[VideoNote] = video_note
        self.voice: Optional[Voice] = voice
        self.has_media_spoiler: Optional[bool] = has_media_spoiler
        self.contact: Optional[Contact] = contact
        self.dice: Optional[Dice] = dice
        self.game: Optional[Game] = game
        self.giveaway: Optional[Giveaway] = giveaway
        self.giveaway_winners: Optional[GiveawayWinners] = giveaway_winners
        self.invoice: Optional[Invoice] = invoice
        self.location: Optional[Location] = location
        self.poll: Optional[Poll] = poll
        self.venue: Optional[Venue] = venue
        self.paid_media: Optional[PaidMediaInfo] = paid_media

        self._id_attrs = (self.origin,)

        self._freeze()

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["ExternalReplyInfo"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if data is None:
            return None

        data["origin"] = MessageOrigin.de_json(data.get("origin"), bot)
        data["chat"] = Chat.de_json(data.get("chat"), bot)
        data["link_preview_options"] = LinkPreviewOptions.de_json(
            data.get("link_preview_options"), bot
        )
        data["animation"] = Animation.de_json(data.get("animation"), bot)
        data["audio"] = Audio.de_json(data.get("audio"), bot)
        data["document"] = Document.de_json(data.get("document"), bot)
        data["photo"] = tuple(PhotoSize.de_list(data.get("photo"), bot))
        data["sticker"] = Sticker.de_json(data.get("sticker"), bot)
        data["story"] = Story.de_json(data.get("story"), bot)
        data["video"] = Video.de_json(data.get("video"), bot)
        data["video_note"] = VideoNote.de_json(data.get("video_note"), bot)
        data["voice"] = Voice.de_json(data.get("voice"), bot)
        data["contact"] = Contact.de_json(data.get("contact"), bot)
        data["dice"] = Dice.de_json(data.get("dice"), bot)
        data["game"] = Game.de_json(data.get("game"), bot)
        data["giveaway"] = Giveaway.de_json(data.get("giveaway"), bot)
        data["giveaway_winners"] = GiveawayWinners.de_json(data.get("giveaway_winners"), bot)
        data["invoice"] = Invoice.de_json(data.get("invoice"), bot)
        data["location"] = Location.de_json(data.get("location"), bot)
        data["poll"] = Poll.de_json(data.get("poll"), bot)
        data["venue"] = Venue.de_json(data.get("venue"), bot)
        data["paid_media"] = PaidMediaInfo.de_json(data.get("paid_media"), bot)

        return super().de_json(data=data, bot=bot)


class TextQuote(TelegramObject):
    """
    This object contains information about the quoted part of a message that is replied to
    by the given message.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`text` and :attr:`position` are equal.

    .. versionadded:: 20.8

    Args:
        text (:obj:`str`): Text of the quoted part of a message that is replied to by the given
            message.
        position (:obj:`int`): Approximate quote position in the original message in UTF-16 code
            units as specified by the sender.
        entities (Sequence[:class:`telegram.MessageEntity`], optional): Special entities that
            appear
            in the quote. Currently, only bold, italic, underline, strikethrough, spoiler, and
            custom_emoji entities are kept in quotes.
        is_manual (:obj:`bool`, optional): :obj:`True`, if the quote was chosen manually by the
            message sender. Otherwise, the quote was added automatically by the server.

    Attributes:
        text (:obj:`str`): Text of the quoted part of a message that is replied to by the given
            message.
        position (:obj:`int`): Approximate quote position in the original message in UTF-16 code
            units as specified by the sender.
        entities (tuple[:class:`telegram.MessageEntity`]): Optional. Special entities that appear
            in the quote. Currently, only bold, italic, underline, strikethrough, spoiler, and
            custom_emoji entities are kept in quotes.
        is_manual (:obj:`bool`): Optional. :obj:`True`, if the quote was chosen manually by the
            message sender. Otherwise, the quote was added automatically by the server.
    """

    __slots__ = (
        "entities",
        "is_manual",
        "position",
        "text",
    )

    def __init__(
        self,
        text: str,
        position: int,
        entities: Optional[Sequence[MessageEntity]] = None,
        is_manual: Optional[bool] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)

        self.text: str = text
        self.position: int = position
        self.entities: Optional[tuple[MessageEntity, ...]] = parse_sequence_arg(entities)
        self.is_manual: Optional[bool] = is_manual

        self._id_attrs = (
            self.text,
            self.position,
        )

        self._freeze()

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["TextQuote"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if data is None:
            return None

        data["entities"] = tuple(MessageEntity.de_list(data.get("entities"), bot))

        return super().de_json(data=data, bot=bot)


class ReplyParameters(TelegramObject):
    """
    Describes reply parameters for the message that is being sent.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`message_id` is equal.

    .. versionadded:: 20.8

    Args:
        message_id (:obj:`int`): Identifier of the message that will be replied to in the current
            chat, or in the chat :paramref:`chat_id` if it is specified.
        chat_id (:obj:`int` | :obj:`str`, optional): If the message to be replied to is from a
            different chat, |chat_id_channel|
            Not supported for messages sent on behalf of a business account.
        allow_sending_without_reply (:obj:`bool`, optional): |allow_sending_without_reply| Can be
            used only for replies in the same chat and forum topic.
        quote (:obj:`str`, optional): Quoted part of the message to be replied to; 0-1024
            characters after entities parsing. The quote must be an exact substring of the message
            to be replied to, including bold, italic, underline, strikethrough, spoiler, and
            custom_emoji entities. The message will fail to send if the quote isn't found in the
            original message.
        quote_parse_mode (:obj:`str`, optional): Mode for parsing entities in the quote. See
            :wiki:`formatting options <Code-snippets#message-formatting-bold-italic-code->` for
            more details.
        quote_entities (Sequence[:class:`telegram.MessageEntity`], optional): A JSON-serialized
            list
            of special entities that appear in the quote. It can be specified instead of
            :paramref:`quote_parse_mode`.
        quote_position (:obj:`int`, optional): Position of the quote in the original message in
            UTF-16 code units.

    Attributes:
        message_id (:obj:`int`): Identifier of the message that will be replied to in the current
            chat, or in the chat :paramref:`chat_id` if it is specified.
        chat_id (:obj:`int` | :obj:`str`): Optional. If the message to be replied to is from a
            different chat, |chat_id_channel|
            Not supported for messages sent on behalf of a business account.
        allow_sending_without_reply (:obj:`bool`): Optional. |allow_sending_without_reply| Can be
            used only for replies in the same chat and forum topic.
        quote (:obj:`str`): Optional. Quoted part of the message to be replied to; 0-1024
            characters after entities parsing. The quote must be an exact substring of the message
            to be replied to, including bold, italic, underline, strikethrough, spoiler, and
            custom_emoji entities. The message will fail to send if the quote isn't found in the
            original message.
        quote_parse_mode (:obj:`str`): Optional. Mode for parsing entities in the quote. See
            :wiki:`formatting options <Code-snippets#message-formatting-bold-italic-code->` for
            more details.
        quote_entities (tuple[:class:`telegram.MessageEntity`]): Optional. A JSON-serialized list
            of special entities that appear in the quote. It can be specified instead of
            :paramref:`quote_parse_mode`.
        quote_position (:obj:`int`): Optional. Position of the quote in the original message in
            UTF-16 code units.
    """

    __slots__ = (
        "allow_sending_without_reply",
        "chat_id",
        "message_id",
        "quote",
        "quote_entities",
        "quote_parse_mode",
        "quote_position",
    )

    def __init__(
        self,
        message_id: int,
        chat_id: Optional[Union[int, str]] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        quote: Optional[str] = None,
        quote_parse_mode: ODVInput[str] = DEFAULT_NONE,
        quote_entities: Optional[Sequence[MessageEntity]] = None,
        quote_position: Optional[int] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)

        self.message_id: int = message_id
        self.chat_id: Optional[Union[int, str]] = chat_id
        self.allow_sending_without_reply: ODVInput[bool] = allow_sending_without_reply
        self.quote: Optional[str] = quote
        self.quote_parse_mode: ODVInput[str] = quote_parse_mode
        self.quote_entities: Optional[tuple[MessageEntity, ...]] = parse_sequence_arg(
            quote_entities
        )
        self.quote_position: Optional[int] = quote_position

        self._id_attrs = (self.message_id,)

        self._freeze()

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: Optional["Bot"] = None
    ) -> Optional["ReplyParameters"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if data is None:
            return None

        data["quote_entities"] = tuple(MessageEntity.de_list(data.get("quote_entities"), bot))

        return super().de_json(data=data, bot=bot)
