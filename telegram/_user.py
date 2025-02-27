#!/usr/bin/env python
# pylint: disable=redefined-builtin
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
"""This module contains an object that represents a Telegram User."""
import datetime as dtm
from collections.abc import Sequence
from typing import TYPE_CHECKING, Optional, Union

from telegram._inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram._menubutton import MenuButton
from telegram._telegramobject import TelegramObject
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import (
    CorrectOptionID,
    FileInput,
    JSONDict,
    ODVInput,
    ReplyMarkup,
    TimePeriod,
)
from telegram.helpers import mention_html as helpers_mention_html
from telegram.helpers import mention_markdown as helpers_mention_markdown

if TYPE_CHECKING:
    from telegram import (
        Animation,
        Audio,
        Contact,
        Document,
        Gift,
        InlineKeyboardMarkup,
        InputMediaAudio,
        InputMediaDocument,
        InputMediaPhoto,
        InputMediaVideo,
        InputPollOption,
        LabeledPrice,
        LinkPreviewOptions,
        Location,
        Message,
        MessageEntity,
        MessageId,
        PhotoSize,
        ReplyParameters,
        Sticker,
        UserChatBoosts,
        UserProfilePhotos,
        Venue,
        Video,
        VideoNote,
        Voice,
    )


class User(TelegramObject):
    """This object represents a Telegram user or bot.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    .. versionchanged:: 20.0
        The following are now keyword-only arguments in Bot methods:
        ``location``, ``filename``, ``venue``, ``contact``,
        ``{read, write, connect, pool}_timeout`` ``api_kwargs``. Use a named argument for those,
        and notice that some positional arguments changed position as a result.

    Args:
        id (:obj:`int`): Unique identifier for this user or bot.
        is_bot (:obj:`bool`): :obj:`True`, if this user is a bot.
        first_name (:obj:`str`): User's or bot's first name.
        last_name (:obj:`str`, optional): User's or bot's last name.
        username (:obj:`str`, optional): User's or bot's username.
        language_code (:obj:`str`, optional): IETF language tag of the user's language.
        can_join_groups (:obj:`str`, optional): :obj:`True`, if the bot can be invited to groups.
            Returned only in :meth:`telegram.Bot.get_me`.
        can_read_all_group_messages (:obj:`str`, optional): :obj:`True`, if privacy mode is
            disabled for the bot. Returned only in :meth:`telegram.Bot.get_me`.
        supports_inline_queries (:obj:`str`, optional): :obj:`True`, if the bot supports inline
            queries. Returned only in :meth:`telegram.Bot.get_me`.

        is_premium (:obj:`bool`, optional): :obj:`True`, if this user is a Telegram Premium user.

            .. versionadded:: 20.0
        added_to_attachment_menu (:obj:`bool`, optional): :obj:`True`, if this user added
            the bot to the attachment menu.

            .. versionadded:: 20.0
        can_connect_to_business (:obj:`bool`, optional): :obj:`True`,  if the bot can be connected
            to a Telegram Business account to receive its messages. Returned only in
            :meth:`telegram.Bot.get_me`.

            .. versionadded:: 21.1
        has_main_web_app (:obj:`bool`, optional): :obj:`True`, if the bot has the main Web App.
            Returned only in :meth:`telegram.Bot.get_me`.

            .. versionadded:: 21.5

    Attributes:
        id (:obj:`int`): Unique identifier for this user or bot.
        is_bot (:obj:`bool`): :obj:`True`, if this user is a bot.
        first_name (:obj:`str`): User's or bot's first name.
        last_name (:obj:`str`): Optional. User's or bot's last name.
        username (:obj:`str`): Optional. User's or bot's username.
        language_code (:obj:`str`): Optional. IETF language tag of the user's language.
        can_join_groups (:obj:`str`): Optional. :obj:`True`, if the bot can be invited to groups.
            Returned only in :attr:`telegram.Bot.get_me` requests.
        can_read_all_group_messages (:obj:`str`): Optional. :obj:`True`, if privacy mode is
            disabled for the bot. Returned only in :attr:`telegram.Bot.get_me` requests.
        supports_inline_queries (:obj:`str`): Optional. :obj:`True`, if the bot supports inline
            queries. Returned only in :attr:`telegram.Bot.get_me` requests.
        is_premium (:obj:`bool`): Optional. :obj:`True`, if this user is a Telegram
            Premium user.

            .. versionadded:: 20.0
        added_to_attachment_menu (:obj:`bool`): Optional. :obj:`True`, if this user added
            the bot to the attachment menu.

            .. versionadded:: 20.0
        can_connect_to_business (:obj:`bool`): Optional. :obj:`True`,  if the bot can be connected
            to a Telegram Business account to receive its messages. Returned only in
            :meth:`telegram.Bot.get_me`.

            .. versionadded:: 21.1
        has_main_web_app (:obj:`bool`) Optional. :obj:`True`, if the bot has the main Web App.
            Returned only in :meth:`telegram.Bot.get_me`.

            .. versionadded:: 21.5

    .. |user_chat_id_note| replace:: This shortcuts build on the assumption that :attr:`User.id`
        coincides with the :attr:`Chat.id` of the private chat with the user. This has been the
        case so far, but Telegram does not guarantee that this stays this way.
    """

    __slots__ = (
        "added_to_attachment_menu",
        "can_connect_to_business",
        "can_join_groups",
        "can_read_all_group_messages",
        "first_name",
        "has_main_web_app",
        "id",
        "is_bot",
        "is_premium",
        "language_code",
        "last_name",
        "supports_inline_queries",
        "username",
    )

    def __init__(
        self,
        id: int,
        first_name: str,
        is_bot: bool,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        language_code: Optional[str] = None,
        can_join_groups: Optional[bool] = None,
        can_read_all_group_messages: Optional[bool] = None,
        supports_inline_queries: Optional[bool] = None,
        is_premium: Optional[bool] = None,
        added_to_attachment_menu: Optional[bool] = None,
        can_connect_to_business: Optional[bool] = None,
        has_main_web_app: Optional[bool] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        # Required
        self.id: int = id
        self.first_name: str = first_name
        self.is_bot: bool = is_bot
        # Optionals
        self.last_name: Optional[str] = last_name
        self.username: Optional[str] = username
        self.language_code: Optional[str] = language_code
        self.can_join_groups: Optional[bool] = can_join_groups
        self.can_read_all_group_messages: Optional[bool] = can_read_all_group_messages
        self.supports_inline_queries: Optional[bool] = supports_inline_queries
        self.is_premium: Optional[bool] = is_premium
        self.added_to_attachment_menu: Optional[bool] = added_to_attachment_menu
        self.can_connect_to_business: Optional[bool] = can_connect_to_business
        self.has_main_web_app: Optional[bool] = has_main_web_app

        self._id_attrs = (self.id,)

        self._freeze()

    @property
    def name(self) -> str:
        """:obj:`str`: Convenience property. If available, returns the user's :attr:`username`
        prefixed with "@". If :attr:`username` is not available, returns :attr:`full_name`.
        """
        if self.username:
            return f"@{self.username}"
        return self.full_name

    @property
    def full_name(self) -> str:
        """:obj:`str`: Convenience property. The user's :attr:`first_name`, followed by (if
        available) :attr:`last_name`.
        """
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    @property
    def link(self) -> Optional[str]:
        """:obj:`str`: Convenience property. If :attr:`username` is available, returns a t.me link
        of the user.
        """
        if self.username:
            return f"https://t.me/{self.username}"
        return None

    async def get_profile_photos(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Optional["UserProfilePhotos"]:
        """Shortcut for::

             await bot.get_user_profile_photos(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.get_user_profile_photos`.

        """
        return await self.get_bot().get_user_profile_photos(
            user_id=self.id,
            offset=offset,
            limit=limit,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    def mention_markdown(self, name: Optional[str] = None) -> str:
        """
        Note:
            :tg-const:`telegram.constants.ParseMode.MARKDOWN` is a legacy mode, retained by
            Telegram for backward compatibility. You should use :meth:`mention_markdown_v2`
            instead.

        Args:
            name (:obj:`str`): The name used as a link for the user. Defaults to :attr:`full_name`.

        Returns:
            :obj:`str`: The inline mention for the user as markdown (version 1).

        """
        if name:
            return helpers_mention_markdown(self.id, name)
        return helpers_mention_markdown(self.id, self.full_name)

    def mention_markdown_v2(self, name: Optional[str] = None) -> str:
        """
        Args:
            name (:obj:`str`): The name used as a link for the user. Defaults to :attr:`full_name`.

        Returns:
            :obj:`str`: The inline mention for the user as markdown (version 2).

        """
        if name:
            return helpers_mention_markdown(self.id, name, version=2)
        return helpers_mention_markdown(self.id, self.full_name, version=2)

    def mention_html(self, name: Optional[str] = None) -> str:
        """
        Args:
            name (:obj:`str`): The name used as a link for the user. Defaults to :attr:`full_name`.

        Returns:
            :obj:`str`: The inline mention for the user as HTML.

        """
        if name:
            return helpers_mention_html(self.id, name)
        return helpers_mention_html(self.id, self.full_name)

    def mention_button(self, name: Optional[str] = None) -> InlineKeyboardButton:
        """Shortcut for::

            InlineKeyboardButton(text=name, url=f"tg://user?id={update.effective_user.id}")

        .. versionadded:: 13.9

        Args:
            name (:obj:`str`): The name used as a link for the user. Defaults to :attr:`full_name`.

        Returns:
            :class:`telegram.InlineKeyboardButton`: InlineButton with url set to the user mention
        """
        return InlineKeyboardButton(text=name or self.full_name, url=f"tg://user?id={self.id}")

    async def pin_message(
        self,
        message_id: int,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        business_connection_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

              await bot.pin_chat_message(chat_id=update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.pin_chat_message`.

        Note:
            |user_chat_id_note|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().pin_chat_message(
            chat_id=self.id,
            message_id=message_id,
            disable_notification=disable_notification,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            business_connection_id=business_connection_id,
            api_kwargs=api_kwargs,
        )

    async def unpin_message(
        self,
        message_id: Optional[int] = None,
        business_connection_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

              await bot.unpin_chat_message(chat_id=update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.unpin_chat_message`.

        Note:
            |user_chat_id_note|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().unpin_chat_message(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            message_id=message_id,
            business_connection_id=business_connection_id,
        )

    async def unpin_all_messages(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

              await bot.unpin_all_chat_messages(chat_id=update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.unpin_all_chat_messages`.

        Note:
            |user_chat_id_note|

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().unpin_all_chat_messages(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def send_message(
        self,
        text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        link_preview_options: ODVInput["LinkPreviewOptions"] = DEFAULT_NONE,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        disable_web_page_preview: Optional[bool] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_message`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_message(
            chat_id=self.id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            link_preview_options=link_preview_options,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            entities=entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def delete_message(
        self,
        message_id: int,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.delete_message(update.effective_user.id, *argss, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.delete_message`.

        .. versionadded:: 20.8

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().delete_message(
            chat_id=self.id,
            message_id=message_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def delete_messages(
        self,
        message_ids: Sequence[int],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.delete_messages(update.effective_user.id, *argss, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.delete_messages`.

        .. versionadded:: 20.8

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().delete_messages(
            chat_id=self.id,
            message_ids=message_ids,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def send_photo(
        self,
        photo: Union[FileInput, "PhotoSize"],
        caption: Optional[str] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        has_spoiler: Optional[bool] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        show_caption_above_media: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_photo(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_photo`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_photo(
            chat_id=self.id,
            photo=photo,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            has_spoiler=has_spoiler,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
            show_caption_above_media=show_caption_above_media,
        )

    async def send_media_group(
        self,
        media: Sequence[
            Union["InputMediaAudio", "InputMediaDocument", "InputMediaPhoto", "InputMediaVideo"]
        ],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
    ) -> tuple["Message", ...]:
        """Shortcut for::

             await bot.send_media_group(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_media_group`.

        Note:
            |user_chat_id_note|

        Returns:
            tuple[:class:`telegram.Message`:] On success, a tuple of :class:`~telegram.Message`
            instances that were sent is returned.

        """
        return await self.get_bot().send_media_group(
            chat_id=self.id,
            media=media,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_audio(
        self,
        audio: Union[FileInput, "Audio"],
        duration: Optional[TimePeriod] = None,
        performer: Optional[str] = None,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        thumbnail: Optional[FileInput] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_audio(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_audio`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_audio(
            chat_id=self.id,
            audio=audio,
            duration=duration,
            performer=performer,
            title=title,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            thumbnail=thumbnail,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_chat_action(
        self,
        action: str,
        message_thread_id: Optional[int] = None,
        business_connection_id: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.send_chat_action(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_chat_action`.

        Note:
            |user_chat_id_note|

        Returns:
            :obj:`True`: On success.

        """
        return await self.get_bot().send_chat_action(
            chat_id=self.id,
            action=action,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            business_connection_id=business_connection_id,
        )

    send_action = send_chat_action
    """Alias for :attr:`send_chat_action`"""

    async def send_contact(
        self,
        phone_number: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        vcard: Optional[str] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        contact: Optional["Contact"] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_contact(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_contact`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_contact(
            chat_id=self.id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            contact=contact,
            vcard=vcard,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_dice(
        self,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        emoji: Optional[str] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_dice(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_dice`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_dice(
            chat_id=self.id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            emoji=emoji,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_document(
        self,
        document: Union[FileInput, "Document"],
        caption: Optional[str] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_content_type_detection: Optional[bool] = None,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        thumbnail: Optional[FileInput] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_document(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_document`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_document(
            chat_id=self.id,
            document=document,
            filename=filename,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            parse_mode=parse_mode,
            thumbnail=thumbnail,
            api_kwargs=api_kwargs,
            disable_content_type_detection=disable_content_type_detection,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_game(
        self,
        game_short_name: str,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_game(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_game`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_game(
            chat_id=self.id,
            game_short_name=game_short_name,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_invoice(
        self,
        title: str,
        description: str,
        payload: str,
        currency: str,
        prices: Sequence["LabeledPrice"],
        provider_token: Optional[str] = None,
        start_parameter: Optional[str] = None,
        photo_url: Optional[str] = None,
        photo_size: Optional[int] = None,
        photo_width: Optional[int] = None,
        photo_height: Optional[int] = None,
        need_name: Optional[bool] = None,
        need_phone_number: Optional[bool] = None,
        need_email: Optional[bool] = None,
        need_shipping_address: Optional[bool] = None,
        is_flexible: Optional[bool] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        provider_data: Optional[Union[str, object]] = None,
        send_phone_number_to_provider: Optional[bool] = None,
        send_email_to_provider: Optional[bool] = None,
        max_tip_amount: Optional[int] = None,
        suggested_tip_amounts: Optional[Sequence[int]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_invoice(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_invoice`.

        Warning:
            As of API 5.2 :paramref:`start_parameter <telegram.Bot.send_invoice.start_parameter>`
            is an optional argument and therefore the
            order of the arguments had to be changed. Use keyword arguments to make sure that the
            arguments are passed correctly.

        Note:
            |user_chat_id_note|

        .. versionchanged:: 13.5
            As of Bot API 5.2, the parameter
            :paramref:`start_parameter <telegram.Bot.send_invoice.start_parameter>` is optional.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_invoice(
            chat_id=self.id,
            title=title,
            description=description,
            payload=payload,
            provider_token=provider_token,
            currency=currency,
            prices=prices,
            start_parameter=start_parameter,
            photo_url=photo_url,
            photo_size=photo_size,
            photo_width=photo_width,
            photo_height=photo_height,
            need_name=need_name,
            need_phone_number=need_phone_number,
            need_email=need_email,
            need_shipping_address=need_shipping_address,
            is_flexible=is_flexible,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            provider_data=provider_data,
            send_phone_number_to_provider=send_phone_number_to_provider,
            send_email_to_provider=send_email_to_provider,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            max_tip_amount=max_tip_amount,
            suggested_tip_amounts=suggested_tip_amounts,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_location(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        live_period: Optional[TimePeriod] = None,
        horizontal_accuracy: Optional[float] = None,
        heading: Optional[int] = None,
        proximity_alert_radius: Optional[int] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        location: Optional["Location"] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_location(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_location`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_location(
            chat_id=self.id,
            latitude=latitude,
            longitude=longitude,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            location=location,
            live_period=live_period,
            api_kwargs=api_kwargs,
            horizontal_accuracy=horizontal_accuracy,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_animation(
        self,
        animation: Union[FileInput, "Animation"],
        duration: Optional[TimePeriod] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        has_spoiler: Optional[bool] = None,
        thumbnail: Optional[FileInput] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        show_caption_above_media: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_animation(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_animation`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_animation(
            chat_id=self.id,
            animation=animation,
            duration=duration,
            width=width,
            height=height,
            caption=caption,
            parse_mode=parse_mode,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            has_spoiler=has_spoiler,
            thumbnail=thumbnail,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
            show_caption_above_media=show_caption_above_media,
        )

    async def send_sticker(
        self,
        sticker: Union[FileInput, "Sticker"],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        emoji: Optional[str] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_sticker(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_sticker`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_sticker(
            chat_id=self.id,
            sticker=sticker,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            emoji=emoji,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_video(
        self,
        video: Union[FileInput, "Video"],
        duration: Optional[TimePeriod] = None,
        caption: Optional[str] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        supports_streaming: Optional[bool] = None,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        has_spoiler: Optional[bool] = None,
        thumbnail: Optional[FileInput] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        show_caption_above_media: Optional[bool] = None,
        cover: Optional[FileInput] = None,
        start_timestamp: Optional[int] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_video(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_video`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_video(
            chat_id=self.id,
            video=video,
            duration=duration,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            width=width,
            height=height,
            parse_mode=parse_mode,
            supports_streaming=supports_streaming,
            thumbnail=thumbnail,
            cover=cover,
            start_timestamp=start_timestamp,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            has_spoiler=has_spoiler,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
            show_caption_above_media=show_caption_above_media,
        )

    async def send_venue(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        title: Optional[str] = None,
        address: Optional[str] = None,
        foursquare_id: Optional[str] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        foursquare_type: Optional[str] = None,
        google_place_id: Optional[str] = None,
        google_place_type: Optional[str] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        venue: Optional["Venue"] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_venue(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_venue`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_venue(
            chat_id=self.id,
            latitude=latitude,
            longitude=longitude,
            title=title,
            address=address,
            foursquare_id=foursquare_id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            venue=venue,
            foursquare_type=foursquare_type,
            api_kwargs=api_kwargs,
            google_place_id=google_place_id,
            google_place_type=google_place_type,
            allow_sending_without_reply=allow_sending_without_reply,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_video_note(
        self,
        video_note: Union[FileInput, "VideoNote"],
        duration: Optional[TimePeriod] = None,
        length: Optional[int] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        thumbnail: Optional[FileInput] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_video_note(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_video_note`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_video_note(
            chat_id=self.id,
            video_note=video_note,
            duration=duration,
            length=length,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            thumbnail=thumbnail,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_voice(
        self,
        voice: Union[FileInput, "Voice"],
        duration: Optional[TimePeriod] = None,
        caption: Optional[str] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: Optional[str] = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_voice(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_voice`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_voice(
            chat_id=self.id,
            voice=voice,
            duration=duration,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            parse_mode=parse_mode,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            business_connection_id=business_connection_id,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_poll(
        self,
        question: str,
        options: Sequence[Union[str, "InputPollOption"]],
        is_anonymous: Optional[bool] = None,
        type: Optional[str] = None,
        allows_multiple_answers: Optional[bool] = None,
        correct_option_id: Optional[CorrectOptionID] = None,
        is_closed: Optional[bool] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        explanation: Optional[str] = None,
        explanation_parse_mode: ODVInput[str] = DEFAULT_NONE,
        open_period: Optional[TimePeriod] = None,
        close_date: Optional[Union[int, dtm.datetime]] = None,
        explanation_entities: Optional[Sequence["MessageEntity"]] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        business_connection_id: Optional[str] = None,
        question_parse_mode: ODVInput[str] = DEFAULT_NONE,
        question_entities: Optional[Sequence["MessageEntity"]] = None,
        message_effect_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.send_poll(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_poll`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().send_poll(
            chat_id=self.id,
            question=question,
            options=options,
            is_anonymous=is_anonymous,
            type=type,  # pylint=pylint,
            allows_multiple_answers=allows_multiple_answers,
            correct_option_id=correct_option_id,
            is_closed=is_closed,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            explanation=explanation,
            explanation_parse_mode=explanation_parse_mode,
            open_period=open_period,
            close_date=close_date,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            explanation_entities=explanation_entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            business_connection_id=business_connection_id,
            question_parse_mode=question_parse_mode,
            question_entities=question_entities,
            message_effect_id=message_effect_id,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_gift(
        self,
        gift_id: Union[str, "Gift"],
        text: Optional[str] = None,
        text_parse_mode: ODVInput[str] = DEFAULT_NONE,
        text_entities: Optional[Sequence["MessageEntity"]] = None,
        pay_for_upgrade: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.send_gift(user_id=update.effective_user.id, *args, **kwargs )

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_gift`.

        .. versionadded:: 21.8

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().send_gift(
            chat_id=None,
            user_id=self.id,
            gift_id=gift_id,
            text=text,
            text_parse_mode=text_parse_mode,
            text_entities=text_entities,
            pay_for_upgrade=pay_for_upgrade,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def send_copy(
        self,
        from_chat_id: Union[str, int],
        message_id: int,
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        show_caption_above_media: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        video_start_timestamp: Optional[int] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "MessageId":
        """Shortcut for::

             await bot.copy_message(chat_id=update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.copy_message`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().copy_message(
            chat_id=self.id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            caption=caption,
            video_start_timestamp=video_start_timestamp,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            show_caption_above_media=show_caption_above_media,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def copy_message(
        self,
        chat_id: Union[int, str],
        message_id: int,
        caption: Optional[str] = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Optional[Sequence["MessageEntity"]] = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_markup: Optional[ReplyMarkup] = None,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["ReplyParameters"] = None,
        show_caption_above_media: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        video_start_timestamp: Optional[int] = None,
        *,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "MessageId":
        """Shortcut for::

             await bot.copy_message(from_chat_id=update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.copy_message`.

        Note:
            |user_chat_id_note|

        Returns:
            :class:`telegram.MessageId`: On success, returns the MessageId of the sent message.

        """
        return await self.get_bot().copy_message(
            from_chat_id=self.id,
            chat_id=chat_id,
            message_id=message_id,
            caption=caption,
            video_start_timestamp=video_start_timestamp,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_parameters=reply_parameters,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            show_caption_above_media=show_caption_above_media,
            allow_paid_broadcast=allow_paid_broadcast,
        )

    async def send_copies(
        self,
        from_chat_id: Union[str, int],
        message_ids: Sequence[int],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        remove_caption: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> tuple["MessageId", ...]:
        """Shortcut for::

             await bot.copy_messages(chat_id=update.effective_user.id, *argss, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.copy_messages`.

        .. seealso:: :meth:`copy_message`, :meth:`send_copy`, :meth:`copy_messages`.

        .. versionadded:: 20.8

        Returns:
            tuple[:class:`telegram.MessageId`]: On success, a tuple of :class:`~telegram.MessageId`
            of the sent messages is returned.

        """
        return await self.get_bot().copy_messages(
            chat_id=self.id,
            from_chat_id=from_chat_id,
            message_ids=message_ids,
            disable_notification=disable_notification,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            remove_caption=remove_caption,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def copy_messages(
        self,
        chat_id: Union[str, int],
        message_ids: Sequence[int],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        remove_caption: Optional[bool] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> tuple["MessageId", ...]:
        """Shortcut for::

             await bot.copy_messages(from_chat_id=update.effective_user.id, *argss, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.copy_messages`.

        .. seealso:: :meth:`copy_message`, :meth:`send_copy`, :meth:`send_copies`.

        .. versionadded:: 20.8

        Returns:
            tuple[:class:`telegram.MessageId`]: On success, a tuple of :class:`~telegram.MessageId`
            of the sent messages is returned.

        """
        return await self.get_bot().copy_messages(
            from_chat_id=self.id,
            chat_id=chat_id,
            message_ids=message_ids,
            disable_notification=disable_notification,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            remove_caption=remove_caption,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def forward_from(
        self,
        from_chat_id: Union[str, int],
        message_id: int,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        video_start_timestamp: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.forward_message(chat_id=update.effective_user.id, *argss, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.forward_message`.

        .. seealso:: :meth:`forward_to`, :meth:`forward_messages_from`, :meth:`forward_messages_to`

        .. versionadded:: 20.0

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().forward_message(
            chat_id=self.id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            video_start_timestamp=video_start_timestamp,
            disable_notification=disable_notification,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def forward_to(
        self,
        chat_id: Union[int, str],
        message_id: int,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        video_start_timestamp: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "Message":
        """Shortcut for::

             await bot.forward_message(from_chat_id=update.effective_user.id, *argss, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.forward_message`.

        .. seealso:: :meth:`forward_from`, :meth:`forward_messages_from`,
            :meth:`forward_messages_to`

        .. versionadded:: 20.0

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return await self.get_bot().forward_message(
            from_chat_id=self.id,
            chat_id=chat_id,
            message_id=message_id,
            video_start_timestamp=video_start_timestamp,
            disable_notification=disable_notification,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
        )

    async def forward_messages_from(
        self,
        from_chat_id: Union[str, int],
        message_ids: Sequence[int],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> tuple["MessageId", ...]:
        """Shortcut for::

             await bot.forward_messages(chat_id=update.effective_user.id, *argss, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.forward_messages`.

        .. seealso:: :meth:`forward_to`, :meth:`forward_from`, :meth:`forward_messages_to`.

        .. versionadded:: 20.8

        Returns:
            tuple[:class:`telegram.MessageId`]: On success, a tuple of :class:`~telegram.MessageId`
            of sent messages is returned.

        """
        return await self.get_bot().forward_messages(
            chat_id=self.id,
            from_chat_id=from_chat_id,
            message_ids=message_ids,
            disable_notification=disable_notification,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def forward_messages_to(
        self,
        chat_id: Union[int, str],
        message_ids: Sequence[int],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        protect_content: ODVInput[bool] = DEFAULT_NONE,
        message_thread_id: Optional[int] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> tuple["MessageId", ...]:
        """Shortcut for::

             await bot.forward_messages(from_chat_id=update.effective_user.id, *argss, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.forward_messages`.

        .. seealso:: :meth:`forward_from`, :meth:`forward_to`, :meth:`forward_messages_from`.

        .. versionadded:: 20.8

        Returns:
            tuple[:class:`telegram.MessageId`]: On success, a tuple of :class:`~telegram.MessageId`
            of sent messages is returned.

        """
        return await self.get_bot().forward_messages(
            from_chat_id=self.id,
            chat_id=chat_id,
            message_ids=message_ids,
            disable_notification=disable_notification,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def approve_join_request(
        self,
        chat_id: Union[int, str],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.approve_chat_join_request(user_id=update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.approve_chat_join_request`.

        Note:
            |user_chat_id_note|

        .. versionadded:: 13.8

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().approve_chat_join_request(
            user_id=self.id,
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def decline_join_request(
        self,
        chat_id: Union[int, str],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.decline_chat_join_request(user_id=update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.decline_chat_join_request`.

        Note:
            |user_chat_id_note|

        .. versionadded:: 13.8

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return await self.get_bot().decline_chat_join_request(
            user_id=self.id,
            chat_id=chat_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def set_menu_button(
        self,
        menu_button: Optional[MenuButton] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.set_chat_menu_button(chat_id=update.effective_user.id, *argss, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.set_chat_menu_button`.

        .. seealso:: :meth:`get_menu_button`

        Note:
            |user_chat_id_note|

        .. versionadded:: 20.0

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().set_chat_menu_button(
            chat_id=self.id,
            menu_button=menu_button,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def get_menu_button(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> MenuButton:
        """Shortcut for::

             await bot.get_chat_menu_button(chat_id=update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.get_chat_menu_button`.

        .. seealso:: :meth:`set_menu_button`

        Note:
            |user_chat_id_note|

        .. versionadded:: 20.0

        Returns:
            :class:`telegram.MenuButton`: On success, the current menu button is returned.
        """
        return await self.get_bot().get_chat_menu_button(
            chat_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def get_chat_boosts(
        self,
        chat_id: Union[int, str],
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> "UserChatBoosts":
        """Shortcut for::

             await bot.get_user_chat_boosts(user_id=update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.get_user_chat_boosts`.

        .. versionadded:: 20.8

        Returns:
            :class:`telegram.UserChatBoosts`: On success, returns the boosts applied by the user.
        """
        return await self.get_bot().get_user_chat_boosts(
            chat_id=chat_id,
            user_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def refund_star_payment(
        self,
        telegram_payment_charge_id: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.refund_star_payment(user_id=update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.refund_star_payment`.

        .. versionadded:: 21.3

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().refund_star_payment(
            user_id=self.id,
            telegram_payment_charge_id=telegram_payment_charge_id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def verify(
        self,
        custom_description: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.verify_user(user_id=update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.verify_user`.

        .. versionadded:: 21.10

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().verify_user(
            user_id=self.id,
            custom_description=custom_description,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )

    async def remove_verification(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.remove_user_verification(user_id=update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.remove_user_verification`.

        .. versionadded:: 21.10

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.
        """
        return await self.get_bot().remove_user_verification(
            user_id=self.id,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
