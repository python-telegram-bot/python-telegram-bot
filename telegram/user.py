#!/usr/bin/env python
# pylint: disable=W0622
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
"""This module contains an object that represents a Telegram User."""
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional, Union, Tuple

from telegram import TelegramObject, constants
from telegram.utils.helpers import (
    mention_html as util_mention_html,
    DEFAULT_NONE,
    DEFAULT_20,
)
from telegram.utils.helpers import mention_markdown as util_mention_markdown
from telegram.utils.types import JSONDict, FileInput, ODVInput, DVInput

if TYPE_CHECKING:
    from telegram import (
        Bot,
        Message,
        UserProfilePhotos,
        MessageId,
        InputMediaAudio,
        InputMediaDocument,
        InputMediaPhoto,
        InputMediaVideo,
        MessageEntity,
        ReplyMarkup,
        PhotoSize,
        Audio,
        Contact,
        Document,
        InlineKeyboardMarkup,
        LabeledPrice,
        Location,
        Animation,
        Sticker,
        Video,
        Venue,
        VideoNote,
        Voice,
    )


class User(TelegramObject):
    """This object represents a Telegram user or bot.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Args:
        id (:obj:`int`): Unique identifier for this user or bot.
        is_bot (:obj:`bool`): :obj:`True`, if this user is a bot.
        first_name (:obj:`str`): User's or bots first name.
        last_name (:obj:`str`, optional): User's or bots last name.
        username (:obj:`str`, optional): User's or bots username.
        language_code (:obj:`str`, optional): IETF language tag of the user's language.
        can_join_groups (:obj:`str`, optional): :obj:`True`, if the bot can be invited to groups.
            Returned only in :attr:`telegram.Bot.get_me` requests.
        can_read_all_group_messages (:obj:`str`, optional): :obj:`True`, if privacy mode is
            disabled for the bot. Returned only in :attr:`telegram.Bot.get_me` requests.
        supports_inline_queries (:obj:`str`, optional): :obj:`True`, if the bot supports inline
            queries. Returned only in :attr:`telegram.Bot.get_me` requests.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.

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
        bot (:class:`telegram.Bot`): Optional. The Bot to use for instance methods.

    """

    def __init__(
        self,
        id: int,
        first_name: str,
        is_bot: bool,
        last_name: str = None,
        username: str = None,
        language_code: str = None,
        can_join_groups: bool = None,
        can_read_all_group_messages: bool = None,
        supports_inline_queries: bool = None,
        bot: 'Bot' = None,
        **_kwargs: Any,
    ):
        # Required
        self.id = int(id)  # pylint: disable=C0103
        self.first_name = first_name
        self.is_bot = is_bot
        # Optionals
        self.last_name = last_name
        self.username = username
        self.language_code = language_code
        self.can_join_groups = can_join_groups
        self.can_read_all_group_messages = can_read_all_group_messages
        self.supports_inline_queries = supports_inline_queries
        self.bot = bot

        self._id_attrs = (self.id,)

    @property
    def name(self) -> str:
        """:obj:`str`: Convenience property. If available, returns the user's :attr:`username`
        prefixed with "@". If :attr:`username` is not available, returns :attr:`full_name`."""
        if self.username:
            return f'@{self.username}'
        return self.full_name

    @property
    def full_name(self) -> str:
        """:obj:`str`: Convenience property. The user's :attr:`first_name`, followed by (if
        available) :attr:`last_name`."""

        if self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.first_name

    @property
    def link(self) -> Optional[str]:
        """:obj:`str`: Convenience property. If :attr:`username` is available, returns a t.me link
        of the user."""

        if self.username:
            return f"https://t.me/{self.username}"
        return None

    def get_profile_photos(
        self,
        offset: int = None,
        limit: int = 100,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> Optional['UserProfilePhotos']:
        """
        Shortcut for::

            bot.get_user_profile_photos(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.get_user_profile_photos`.

        """

        return self.bot.get_user_profile_photos(
            user_id=self.id,
            offset=offset,
            limit=limit,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def mention_markdown(self, name: str = None) -> str:
        """
        Note:
            :attr:`telegram.ParseMode.MARKDOWN` is is a legacy mode, retained by Telegram for
            backward compatibility. You should use :meth:`mention_markdown_v2` instead.

        Args:
            name (:obj:`str`): The name used as a link for the user. Defaults to :attr:`full_name`.

        Returns:
            :obj:`str`: The inline mention for the user as markdown (version 1).

        """
        if name:
            return util_mention_markdown(self.id, name)
        return util_mention_markdown(self.id, self.full_name)

    def mention_markdown_v2(self, name: str = None) -> str:
        """
        Args:
            name (:obj:`str`): The name used as a link for the user. Defaults to :attr:`full_name`.

        Returns:
            :obj:`str`: The inline mention for the user as markdown (version 2).

        """
        if name:
            return util_mention_markdown(self.id, name, version=2)
        return util_mention_markdown(self.id, self.full_name, version=2)

    def mention_html(self, name: str = None) -> str:
        """
        Args:
            name (:obj:`str`): The name used as a link for the user. Defaults to :attr:`full_name`.

        Returns:
            :obj:`str`: The inline mention for the user as HTML.

        """
        if name:
            return util_mention_html(self.id, name)
        return util_mention_html(self.id, self.full_name)

    def pin_message(
        self,
        message_id: int,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

             bot.pin_chat_message(chat_id=update.effective_user.id,
                                  *args,
                                  **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.pin_chat_message`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.pin_chat_message(
            chat_id=self.id,
            message_id=message_id,
            disable_notification=disable_notification,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def unpin_message(
        self,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        message_id: int = None,
    ) -> bool:
        """Shortcut for::

             bot.unpin_chat_message(chat_id=update.effective_user.id,
                                    *args,
                                    **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.unpin_chat_message`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.unpin_chat_message(
            chat_id=self.id,
            timeout=timeout,
            api_kwargs=api_kwargs,
            message_id=message_id,
        )

    def unpin_all_messages(
        self,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

             bot.unpin_all_chat_messages(chat_id=update.effective_user.id,
                                         *args,
                                         **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.unpin_all_chat_messages`.

        Returns:
            :obj:`bool`: On success, :obj:`True` is returned.

        """
        return self.bot.unpin_all_chat_messages(
            chat_id=self.id,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def send_message(
        self,
        text: str,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_message`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_message(
            chat_id=self.id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            entities=entities,
        )

    def send_photo(
        self,
        photo: Union[FileInput, 'PhotoSize'],
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_photo`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_photo(
            chat_id=self.id,
            photo=photo,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            parse_mode=parse_mode,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
        )

    def send_media_group(
        self,
        media: List[
            Union['InputMediaAudio', 'InputMediaDocument', 'InputMediaPhoto', 'InputMediaVideo']
        ],
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        timeout: DVInput[float] = DEFAULT_20,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
    ) -> List['Message']:
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_media_group`.

        Returns:
            List[:class:`telegram.Message`:] On success, instance representing the message posted.

        """
        return self.bot.send_media_group(
            chat_id=self.id,
            media=media,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def send_audio(
        self,
        audio: Union[FileInput, 'Audio'],
        duration: int = None,
        performer: str = None,
        title: str = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_audio`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_audio(
            chat_id=self.id,
            audio=audio,
            duration=duration,
            performer=performer,
            title=title,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            parse_mode=parse_mode,
            thumb=thumb,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
        )

    def send_chat_action(
        self,
        action: str,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_chat_action`.

        Returns:
            :obj:`True`: On success.

        """
        return self.bot.send_chat_action(
            chat_id=self.id,
            action=action,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    send_action = send_chat_action
    """Alias for :attr:`send_chat_action`"""

    def send_contact(
        self,
        phone_number: str = None,
        first_name: str = None,
        last_name: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        contact: 'Contact' = None,
        vcard: str = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_contact`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_contact(
            chat_id=self.id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            contact=contact,
            vcard=vcard,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def send_dice(
        self,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        emoji: str = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_dice`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_dice(
            chat_id=self.id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            emoji=emoji,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def send_document(
        self,
        document: Union[FileInput, 'Document'],
        filename: str = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        disable_content_type_detection: bool = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_document`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_document(
            chat_id=self.id,
            document=document,
            filename=filename,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            parse_mode=parse_mode,
            thumb=thumb,
            api_kwargs=api_kwargs,
            disable_content_type_detection=disable_content_type_detection,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
        )

    def send_game(
        self,
        game_short_name: str,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'InlineKeyboardMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_game`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_game(
            chat_id=self.id,
            game_short_name=game_short_name,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def send_invoice(
        self,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: List['LabeledPrice'],
        start_parameter: str = None,
        photo_url: str = None,
        photo_size: int = None,
        photo_width: int = None,
        photo_height: int = None,
        need_name: bool = None,
        need_phone_number: bool = None,
        need_email: bool = None,
        need_shipping_address: bool = None,
        is_flexible: bool = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'InlineKeyboardMarkup' = None,
        provider_data: Union[str, object] = None,
        send_phone_number_to_provider: bool = None,
        send_email_to_provider: bool = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        max_tip_amount: int = None,
        suggested_tip_amounts: List[int] = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_invoice`.

        Warning:
            As of API 5.2 :attr:`start_parameter` is an optional argument and therefore the order
            of the arguments had to be changed. Use keyword arguments to make sure that the
            arguments are passed correctly.

        .. versionchanged:: 13.5
            As of Bot API 5.2, the parameter :attr:`start_parameter` is optional.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_invoice(
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
            reply_markup=reply_markup,
            provider_data=provider_data,
            send_phone_number_to_provider=send_phone_number_to_provider,
            send_email_to_provider=send_email_to_provider,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            max_tip_amount=max_tip_amount,
            suggested_tip_amounts=suggested_tip_amounts,
        )

    def send_location(
        self,
        latitude: float = None,
        longitude: float = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        location: 'Location' = None,
        live_period: int = None,
        api_kwargs: JSONDict = None,
        horizontal_accuracy: float = None,
        heading: int = None,
        proximity_alert_radius: int = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_location`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_location(
            chat_id=self.id,
            latitude=latitude,
            longitude=longitude,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            location=location,
            live_period=live_period,
            api_kwargs=api_kwargs,
            horizontal_accuracy=horizontal_accuracy,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def send_animation(
        self,
        animation: Union[FileInput, 'Animation'],
        duration: int = None,
        width: int = None,
        height: int = None,
        thumb: FileInput = None,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_animation`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_animation(
            chat_id=self.id,
            animation=animation,
            duration=duration,
            width=width,
            height=height,
            thumb=thumb,
            caption=caption,
            parse_mode=parse_mode,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
        )

    def send_sticker(
        self,
        sticker: Union[FileInput, 'Sticker'],
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_sticker`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_sticker(
            chat_id=self.id,
            sticker=sticker,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def send_video(
        self,
        video: Union[FileInput, 'Video'],
        duration: int = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        width: int = None,
        height: int = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        supports_streaming: bool = None,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_video`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_video(
            chat_id=self.id,
            video=video,
            duration=duration,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            width=width,
            height=height,
            parse_mode=parse_mode,
            supports_streaming=supports_streaming,
            thumb=thumb,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
        )

    def send_venue(
        self,
        latitude: float = None,
        longitude: float = None,
        title: str = None,
        address: str = None,
        foursquare_id: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        venue: 'Venue' = None,
        foursquare_type: str = None,
        api_kwargs: JSONDict = None,
        google_place_id: str = None,
        google_place_type: str = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_venue`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_venue(
            chat_id=self.id,
            latitude=latitude,
            longitude=longitude,
            title=title,
            address=address,
            foursquare_id=foursquare_id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            venue=venue,
            foursquare_type=foursquare_type,
            api_kwargs=api_kwargs,
            google_place_id=google_place_id,
            google_place_type=google_place_type,
            allow_sending_without_reply=allow_sending_without_reply,
        )

    def send_video_note(
        self,
        video_note: Union[FileInput, 'VideoNote'],
        duration: int = None,
        length: int = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        thumb: FileInput = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        filename: str = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_video_note`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_video_note(
            chat_id=self.id,
            video_note=video_note,
            duration=duration,
            length=length,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            thumb=thumb,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            filename=filename,
        )

    def send_voice(
        self,
        voice: Union[FileInput, 'Voice'],
        duration: int = None,
        caption: str = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: DVInput[float] = DEFAULT_20,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        caption_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
        filename: str = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_voice`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_voice(
            chat_id=self.id,
            voice=voice,
            duration=duration,
            caption=caption,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            timeout=timeout,
            parse_mode=parse_mode,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            caption_entities=caption_entities,
            filename=filename,
        )

    def send_poll(
        self,
        question: str,
        options: List[str],
        is_anonymous: bool = True,
        # We use constant.POLL_REGULAR instead of Poll.REGULAR here to avoid circular imports
        type: str = constants.POLL_REGULAR,  # pylint: disable=W0622
        allows_multiple_answers: bool = False,
        correct_option_id: int = None,
        is_closed: bool = None,
        disable_notification: ODVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        explanation: str = None,
        explanation_parse_mode: ODVInput[str] = DEFAULT_NONE,
        open_period: int = None,
        close_date: Union[int, datetime] = None,
        api_kwargs: JSONDict = None,
        allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
        explanation_entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
    ) -> 'Message':
        """Shortcut for::

            bot.send_message(update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.send_poll`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.send_poll(
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
            reply_markup=reply_markup,
            timeout=timeout,
            explanation=explanation,
            explanation_parse_mode=explanation_parse_mode,
            open_period=open_period,
            close_date=close_date,
            api_kwargs=api_kwargs,
            allow_sending_without_reply=allow_sending_without_reply,
            explanation_entities=explanation_entities,
        )

    def send_copy(
        self,
        from_chat_id: Union[str, int],
        message_id: int,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Union[Tuple['MessageEntity', ...], List['MessageEntity']] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        allow_sending_without_reply: DVInput[bool] = DEFAULT_NONE,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> 'MessageId':
        """Shortcut for::

            bot.copy_message(chat_id=update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.copy_message`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.copy_message(
            chat_id=self.id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )

    def copy_message(
        self,
        chat_id: Union[int, str],
        message_id: int,
        caption: str = None,
        parse_mode: ODVInput[str] = DEFAULT_NONE,
        caption_entities: Union[Tuple['MessageEntity', ...], List['MessageEntity']] = None,
        disable_notification: DVInput[bool] = DEFAULT_NONE,
        reply_to_message_id: int = None,
        allow_sending_without_reply: DVInput[bool] = DEFAULT_NONE,
        reply_markup: 'ReplyMarkup' = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> 'MessageId':
        """Shortcut for::

            bot.copy_message(from_chat_id=update.effective_user.id, *args, **kwargs)

        For the documentation of the arguments, please see :meth:`telegram.Bot.copy_message`.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        """
        return self.bot.copy_message(
            from_chat_id=self.id,
            chat_id=chat_id,
            message_id=message_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )
