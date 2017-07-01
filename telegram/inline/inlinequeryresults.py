#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
"""This module contains the classes that represent inline query results"""

from telegram import TelegramObject, InlineKeyboardMarkup, InputMessageContent


class InlineQueryResult(TelegramObject):
    """This object represents a Telegram InlineQueryResult.

    Attributes:
        type (str): Type of the result.
        id (str): Unique identifier for this result, 1-64 Bytes

    Args:
        type (str): Type of the result.
        id (str): Unique identifier for this result, 1-64 Bytes
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self, type, id, **kwargs):
        # Required
        self.type = str(type)
        self.id = str(id)

        self._id_attrs = (self.id,)

    @staticmethod
    def de_json(data, bot):
        return super(InlineQueryResult, InlineQueryResult).de_json(data, bot)


class InlineQueryResultArticle(InlineQueryResult):
    """Represents a link to an article or web page.

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        title (str): Title of the result
        input_message_content (:class:`telegram.InputMessageContent`): Content of the message to
            be sent
        reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Inline keyboard attached to the
            message
        url (Optional[str]): URL of the result
        hide_url (Optional[bool]): Pass True, if you don't want the URL to be shown in the message
        description (Optional[str]): Short description of the result
        thumb_url (Optional[str]): Url of the thumbnail for the result
        thumb_width (Optional[int]): Thumbnail width
        thumb_height (Optional[int]): Thumbnail height
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 title,
                 input_message_content,
                 reply_markup=None,
                 url=None,
                 hide_url=None,
                 description=None,
                 thumb_url=None,
                 thumb_width=None,
                 thumb_height=None,
                 **kwargs):

        # Required
        super(InlineQueryResultArticle, self).__init__('article', id)
        self.title = title
        self.input_message_content = input_message_content

        # Optional
        if reply_markup is not None:
            self.reply_markup = reply_markup
        if url is not None:
            self.url = url
        if hide_url is not None:
            self.hide_url = hide_url
        if description is not None:
            self.description = description
        if thumb_url is not None:
            self.thumb_url = thumb_url
        if thumb_width is not None:
            self.thumb_width = thumb_width
        if thumb_height is not None:
            self.thumb_height = thumb_height

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultArticle, InlineQueryResultArticle).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultArticle(**data)


class InlineQueryResultAudio(InlineQueryResult):
    """Represents a link to an mp3 audio file.

    By default, this audio file will be sent by the user. Alternatively, you can use
    input_message_content to send a message with the specified content instead of the audio.

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        audio_url (Optional[str]): A valid URL for the audio file
        title (str): Title
        caption (Optional[str]): Caption, 0-200 characters
        performer (str): Performer
        audio_duration (Optional[int]): Audio duration in seconds
        reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Inline keyboard attached to the
            message
        input_message_content (:class:`telegram.InputMessageContent`): Content of the message to
            be sent instead of the audio
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 audio_url,
                 title,
                 performer=None,
                 audio_duration=None,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):

        # Required
        super(InlineQueryResultAudio, self).__init__('audio', id)
        self.audio_url = audio_url
        self.title = title

        # Optionals
        if performer is not None:
            self.performer = performer
        if audio_duration is not None:
            self.audio_duration = audio_duration
        if caption is not None:
            self.caption = caption
        if reply_markup is not None:
            self.reply_markup = reply_markup
        if input_message_content is not None:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultAudio, InlineQueryResultAudio).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultAudio(**data)


class InlineQueryResultContact(InlineQueryResult):
    """Represents a contact with a phone number.

    By default, this contact will be sent by the user. Alternatively, you can use
    input_message_content to send a message with the specified content
    instead of the contact.

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        phone_number (str): Contact's phone number
        first_name (str): Contact's first name
        last_name (Optional[str]): Contact's last name
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the contact
        thumb_url (Optional[str]): Url of the thumbnail for the result.
        thumb_width (Optional[int]): Thumbnail width
        thumb_height (Optional[int]): Thumbnail height
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 phone_number,
                 first_name,
                 last_name=None,
                 reply_markup=None,
                 input_message_content=None,
                 thumb_url=None,
                 thumb_width=None,
                 thumb_height=None,
                 **kwargs):
        # Required
        super(InlineQueryResultContact, self).__init__('contact', id)
        self.phone_number = phone_number
        self.first_name = first_name

        # Optionals
        if last_name is not None:
            self.last_name = last_name
        if reply_markup is not None:
            self.reply_markup = reply_markup
        if input_message_content is not None:
            self.input_message_content = input_message_content
        if thumb_url is not None:
            self.thumb_url = thumb_url
        if thumb_width is not None:
            self.thumb_width = thumb_width
        if thumb_height is not None:
            self.thumb_height = thumb_height

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultContact, InlineQueryResultContact).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultContact(**data)


class InlineQueryResultDocument(InlineQueryResult):
    """Represents a link to a file.

    By default, this file will be sent by the user with an optional caption. Alternatively,
    you can use input_message_content to send a message with the specified content instead of
    the file. Currently, only .PDF and .ZIP files can be sent using this method.

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        title (str): Title for the result.
        caption (Optional[str]): Caption of the document to be sent, 0-200 characters.
        document_url (Optional[str]): A valid URL for the file.
        mime_type (Optional[str]): Mime type of the content of the file, either "application/pdf"
            or "application/zip".
        description	(Optional[str]): Short description of the result.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the file.
        thumb_url (Optional[str]): URL of the thumbnail (jpeg only) for the file.
        thumb_width (Optional[int]): Thumbnail width.
        thumb_height (Optional[int]): Thumbnail height.
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 document_url,
                 title,
                 mime_type,
                 caption=None,
                 description=None,
                 reply_markup=None,
                 input_message_content=None,
                 thumb_url=None,
                 thumb_width=None,
                 thumb_height=None,
                 **kwargs):
        # Required
        super(InlineQueryResultDocument, self).__init__('document', id)
        self.document_url = document_url
        self.title = title
        self.mime_type = mime_type

        # Optionals
        if caption is not None:
            self.caption = caption
        if description is not None:
            self.description = description
        if reply_markup is not None:
            self.reply_markup = reply_markup
        if input_message_content is not None:
            self.input_message_content = input_message_content
        if thumb_url is not None:
            self.thumb_url = thumb_url
        if thumb_width is not None:
            self.thumb_width = thumb_width
        if thumb_height is not None:
            self.thumb_height = thumb_height

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultDocument, InlineQueryResultDocument).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultDocument(**data)


class InlineQueryResultGame(InlineQueryResult):
    """Represents a Game.

    Args:
        id (str): Unique identifier for this result, 1-64 bytes
        game_short_name (str): Short name of the game
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message

    """

    def __init__(self, id, game_short_name, reply_markup=None, **kwargs):
        # Required
        super(InlineQueryResultGame, self).__init__('game', id)
        self.id = id
        self.game_short_name = game_short_name

        if reply_markup is not None:
            self.reply_markup = reply_markup

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultGame, InlineQueryResultGame).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)

        return InlineQueryResultGame(**data)


class InlineQueryResultGif(InlineQueryResult):
    """Represents a link to an animated GIF file.

    By default, this animated GIF file will be sent by the user with optional caption.
    Alternatively, you can use input_message_content to send a
    message with the specified content instead of the animation.

    Args:
        id (str): Unique identifier for this result, 1-64 bytes
        gif_url (str): A valid URL for the GIF file. File size must not exceed 1MB.
        thumb_url (str): URL of the static thumbnail for the result (jpeg or gif).
        gif_width (Optional[int]): Width of the GIF.
        gif_height (Optional[int]): Height of the GIF.
        gif_duration (Optional[int]): Duration of the GIF.
        title (Optional[str]): Title for the result.
        caption	(Optional[str]): Caption of the GIF file to be sent, 0-200 characters.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the GIF animation.
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 gif_url,
                 thumb_url,
                 gif_width=None,
                 gif_height=None,
                 title=None,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 gif_duration=None,
                 **kwargs):

        # Required
        super(InlineQueryResultGif, self).__init__('gif', id)
        self.gif_url = gif_url
        self.thumb_url = thumb_url

        # Optionals
        if gif_width is not None:
            self.gif_width = gif_width
        if gif_height is not None:
            self.gif_height = gif_height
        if gif_duration is not None:
            self.gif_duration = gif_duration
        if title is not None:
            self.title = title
        if caption is not None:
            self.caption = caption
        if reply_markup is not None:
            self.reply_markup = reply_markup
        if input_message_content is not None:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultGif, InlineQueryResultGif).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultGif(**data)


class InlineQueryResultLocation(InlineQueryResult):
    """Represents a location on a map.

    By default, the location will be sent by the user. Alternatively, you can use
    input_message_content to send a message with the specified content
    instead of the location.

    Args:
        id (str): Unique identifier for this result, 1-64 bytes
        latitude (float): Location latitude in degrees.
        longitude (float): Location longitude in degrees.
        title (str): Location title.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the location.
        thumb_url (Optional[str]): Url of the thumbnail for the result.
        thumb_width (Optional[int]): Thumbnail width.
        thumb_height (Optional[int]): Thumbnail height.
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 latitude,
                 longitude,
                 title,
                 reply_markup=None,
                 input_message_content=None,
                 thumb_url=None,
                 thumb_width=None,
                 thumb_height=None,
                 **kwargs):
        # Required
        super(InlineQueryResultLocation, self).__init__('location', id)
        self.latitude = latitude
        self.longitude = longitude
        self.title = title

        # Optionals
        if reply_markup is not None:
            self.reply_markup = reply_markup
        if input_message_content is not None:
            self.input_message_content = input_message_content
        if thumb_url is not None:
            self.thumb_url = thumb_url
        if thumb_width is not None:
            self.thumb_width = thumb_width
        if thumb_height is not None:
            self.thumb_height = thumb_height

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultLocation, InlineQueryResultLocation).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultLocation(**data)


class InlineQueryResultMpeg4Gif(InlineQueryResult):
    """Represents a link to a video animation (H.264/MPEG-4 AVC video without sound).

    By default, this animated MPEG-4 file will be sent by the user with optional caption.
    Alternatively, you can use input_message_content to send a message with the specified
    content instead of the animation.

    Args:
        id (str): Unique identifier for this result, 1-64 bytes
        mpeg4_url (str): A valid URL for the MP4 file. File size must not exceed 1MB.
        thumb_url (str): URL of the static thumbnail (jpeg or gif) for the result.
        mpeg4_width (Optional[int]): Video width.
        mpeg4_height (Optional[int]): Video height.
        mpeg4_duration (Optional[int]): Video duration
        title (Optional[str]): Title for the result.
        caption	(Optional[str]): Caption of the MPEG-4 file to be sent, 0-200 characters.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the video animation.
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 mpeg4_url,
                 thumb_url,
                 mpeg4_width=None,
                 mpeg4_height=None,
                 title=None,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 mpeg4_duration=None,
                 **kwargs):

        # Required
        super(InlineQueryResultMpeg4Gif, self).__init__('mpeg4_gif', id)
        self.mpeg4_url = mpeg4_url
        self.thumb_url = thumb_url

        # Optional
        if mpeg4_width is not None:
            self.mpeg4_width = mpeg4_width
        if mpeg4_height is not None:
            self.mpeg4_height = mpeg4_height
        if mpeg4_duration is not None:
            self.mpeg4_duration = mpeg4_duration
        if title is not None:
            self.title = title
        if caption is not None:
            self.caption = caption
        if reply_markup is not None:
            self.reply_markup = reply_markup
        if input_message_content is not None:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultMpeg4Gif, InlineQueryResultMpeg4Gif).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultMpeg4Gif(**data)


class InlineQueryResultPhoto(InlineQueryResult):
    """Represents a link to a photo.

    By default, this photo will be sent by the user with optional caption. Alternatively,
    you can use input_message_content to send a message with the specified
    content instead of the photo.

    Args:
        id (str): Unique identifier for this result, 1-64 bytes
        photo_url (str): A valid URL of the photo. Photo must be in jpeg format. Photo size must
            not exceed 5MB.
        thumb_url (str): URL of the thumbnail for the photo.
        photo_width (Optional[int]): Width of the photo.
        photo_height (Optional[int]): Height of the photo.
        title (Optional[str]): Title for the result.
        description	(Optional[str]): Short description of the result.
        caption (Optional[str]): Caption of the photo to be sent, 0-200 characters.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the photo.
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 photo_url,
                 thumb_url,
                 photo_width=None,
                 photo_height=None,
                 title=None,
                 description=None,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):
        # Required
        super(InlineQueryResultPhoto, self).__init__('photo', id)
        self.photo_url = photo_url
        self.thumb_url = thumb_url

        # Optionals
        if photo_width is not None:
            self.photo_width = int(photo_width)
        if photo_height is not None:
            self.photo_height = int(photo_height)
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if caption is not None:
            self.caption = caption
        if reply_markup is not None:
            self.reply_markup = reply_markup
        if input_message_content is not None:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultPhoto, InlineQueryResultPhoto).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultPhoto(**data)


class InlineQueryResultVenue(InlineQueryResult):
    """Represents a venue.

    By default, the venue will be sent by the user. Alternatively, you can use
    input_message_content to send a message with the specified content instead of the venue.

    Args:
        id (str): Unique identifier for this result, 1-64 bytes
        latitude (float): Venue location latitude in degrees.
        longitude (float): Venue location longitude in degrees.
        title (str): Venue title.
        address (str): Address of the venue
        foursquare_id (Optional[str]): Foursquare identifier of the venue if known
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the location.
        thumb_url (Optional[str]): Url of the thumbnail for the result.
        thumb_width (Optional[int]): Thumbnail width.
        thumb_height (Optional[int]): Thumbnail height.
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 latitude,
                 longitude,
                 title,
                 address,
                 foursquare_id=None,
                 reply_markup=None,
                 input_message_content=None,
                 thumb_url=None,
                 thumb_width=None,
                 thumb_height=None,
                 **kwargs):
        # Required
        super(InlineQueryResultVenue, self).__init__('venue', id)
        self.latitude = latitude
        self.longitude = longitude
        self.title = title
        self.address = address

        # Optional
        if foursquare_id is not None:
            self.foursquare_id = foursquare_id
        if reply_markup is not None:
            self.reply_markup = reply_markup
        if input_message_content is not None:
            self.input_message_content = input_message_content
        if thumb_url is not None:
            self.thumb_url = thumb_url
        if thumb_width is not None:
            self.thumb_width = thumb_width
        if thumb_height is not None:
            self.thumb_height = thumb_height

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultVenue, InlineQueryResultVenue).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultVenue(**data)


class InlineQueryResultVideo(InlineQueryResult):
    """Represents a link to a page containing an embedded video player or a video file.

    By default, the video file will be sent by the user with an optional caption. Alternatively,
    you can use input_message_content to send a message with the specified content instead of
    the video.

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        video_url (str): A valid URL for the video.
        mime_type (str): Mime type of the content of video url, "text/html"
            or "video/mp4"
        thumb_url (str): URL of the thumbnail (jpeg only) for the video
        title (str): Title for the result.
        caption (Optional[str]): Caption of the video to be sent, 0-200 characters.
        video_width (Optional[int]): Video width.
        video_height (Optional[int]): Video height.
        video_duration (Optional[int]): Video duration in seconds
        description	(Optional[str]): Short description of the result.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the file.
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 video_url,
                 mime_type,
                 thumb_url,
                 title,
                 caption=None,
                 video_width=None,
                 video_height=None,
                 video_duration=None,
                 description=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):

        # Required
        super(InlineQueryResultVideo, self).__init__('video', id)
        self.video_url = video_url
        self.mime_type = mime_type
        self.thumb_url = thumb_url
        self.title = title

        # Optional
        if caption is not None:
            self.caption = caption
        if video_width is not None:
            self.video_width = video_width
        if video_height is not None:
            self.video_height = video_height
        if video_duration is not None:
            self.video_duration = video_duration
        if description is not None:
            self.description = description
        if reply_markup is not None:
            self.reply_markup = reply_markup
        if input_message_content is not None:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultVideo, InlineQueryResultVideo).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultVideo(**data)


class InlineQueryResultVoice(InlineQueryResult):
    """Represents a link to a voice recording in an .ogg container encoded with OPUS.

    By default, this voice recording file will be sent by the user. Alternatively, you can use
    input_message_content to send a message with the specified content instead of the voice
    message.

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        voice_url (Optional[str]): A valid URL for the voice recording
        title (str): Recording title
        caption (Optional[str]): Caption, 0-200 characters
        voice_duration (Optional[int]): Audio duration in seconds
        reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Inline keyboard attached to the
            message
        input_message_content (:class:`telegram.InputMessageContent`): Content of the message to
            be sent instead of the audio
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 voice_url,
                 title,
                 voice_duration=None,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):

        # Required
        super(InlineQueryResultVoice, self).__init__('voice', id)
        self.voice_url = voice_url
        self.title = title

        # Optional
        if voice_duration is not None:
            self.voice_duration = voice_duration
        if caption is not None:
            self.caption = caption
        if reply_markup is not None:
            self.reply_markup = reply_markup
        if input_message_content is not None:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultVoice, InlineQueryResultVoice).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultVoice(**data)


class InlineQueryResultCachedAudio(InlineQueryResult):
    """Represents a link to an mp3 audio file stored on the Telegram servers.

    By default, this audio file will be sent by the user. Alternatively, you can use
    input_message_content to send a message with the specified content instead of the audio.

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        audio_file_id (str):
        caption (Optional[str]):
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]):
        input_message_content (Optional[:class:`telegram.input_message_content`]):
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 audio_file_id,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):
        # Required
        super(InlineQueryResultCachedAudio, self).__init__('audio', id)
        self.audio_file_id = audio_file_id

        # Optionals
        if caption:
            self.caption = caption
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultCachedAudio, InlineQueryResultCachedAudio).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultCachedAudio(**data)


class InlineQueryResultCachedDocument(InlineQueryResult):
    """Represents a link to a file stored on the Telegram servers.

    By default, this file will be sent by the user with an optional caption. Alternatively,
    you can use input_message_content to send a message with the specified content instead of
    the file. Currently, only pdf-files and zip archives can be sent using this method.

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        title (str): Title for the result.
        document_file_id (str): A valid file identifier for the file.
        description (Optional[str]): Short description of the result.
        caption	(Optional[str]): Caption of the document to be sent, 0-200 characters.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the file.
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 title,
                 document_file_id,
                 description=None,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):
        # Required
        super(InlineQueryResultCachedDocument, self).__init__('document', id)
        self.title = title
        self.document_file_id = document_file_id

        # Optionals
        if description:
            self.description = description
        if caption:
            self.caption = caption
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultCachedDocument,
                     InlineQueryResultCachedDocument).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultCachedDocument(**data)


class InlineQueryResultCachedGif(InlineQueryResult):
    """Represents a link to an animated GIF file stored on the Telegram servers. By default, this
    animated GIF file will be sent by the user with an optional caption. Alternatively, you can use
    input_message_content to send a message with specified content instead of the animation.

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        gif_file_id (str): A valid file identifier for the GIF file.
        title (Optional[str]): Title for the result.
        caption (Optional[str]): Caption of the GIF file to be sent, 0-200 characters.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the GIF animation.
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 gif_file_id,
                 title=None,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):
        # Required
        super(InlineQueryResultCachedGif, self).__init__('gif', id)
        self.gif_file_id = gif_file_id

        # Optionals
        if title:
            self.title = title
        if caption:
            self.caption = caption
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultCachedGif, InlineQueryResultCachedGif).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultCachedGif(**data)


class InlineQueryResultCachedMpeg4Gif(InlineQueryResult):
    """Represents a link to a video animation (H.264/MPEG-4 AVC video without sound) stored on the
    Telegram servers.

    By default, this animated MPEG-4 file will be sent by the user with an optional caption.
    Alternatively, you can use input_message_content to send a message with the
    specified content instead of the animation.

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        mpeg4_file_id (str): A valid file identifier for the MP4 file.
        title (Optional[str]): Title for the result.
        caption	(Optional[str]): Caption of the MPEG-4 file to be sent, 0-200 characters.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the video animation
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 mpeg4_file_id,
                 title=None,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):
        # Required
        super(InlineQueryResultCachedMpeg4Gif, self).__init__('mpeg4_gif', id)
        self.mpeg4_file_id = mpeg4_file_id

        # Optionals
        if title:
            self.title = title
        if caption:
            self.caption = caption
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultCachedMpeg4Gif,
                     InlineQueryResultCachedMpeg4Gif).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultCachedMpeg4Gif(**data)


class InlineQueryResultCachedPhoto(InlineQueryResult):
    """Represents a link to a photo stored on the Telegram servers.

    By default, this photo will be sent by the user with an optional caption. Alternatively,
    you can use input_message_content to send a message with the specified content instead of
    the photo.

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        photo_file_id (str): A valid file identifier of the photo.
        title (Optional[str]): Title for the result.
        description (Optional[str]): Short description of the result.
        caption (Optional[str]): Caption of the photo to be sent, 0-200 characters.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the photo
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 photo_file_id,
                 title=None,
                 description=None,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):
        # Required
        super(InlineQueryResultCachedPhoto, self).__init__('photo', id)
        self.photo_file_id = photo_file_id

        # Optionals
        if title:
            self.title = title
        if description:
            self.description = description
        if caption:
            self.caption = caption
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultCachedPhoto, InlineQueryResultCachedPhoto).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultCachedPhoto(**data)


class InlineQueryResultCachedSticker(InlineQueryResult):
    """Represents a link to a sticker stored on the Telegram servers.

    By default, this sticker will be sent by the user. Alternatively, you can use
    input_message_content to send a message with the specified content instead of the sticker.

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        sticker_file_id (str): A valid file identifier of the sticker.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the sticker.
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 sticker_file_id,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):
        # Required
        super(InlineQueryResultCachedSticker, self).__init__('sticker', id)
        self.sticker_file_id = sticker_file_id

        # Optionals
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultCachedSticker,
                     InlineQueryResultCachedSticker).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultCachedSticker(**data)


class InlineQueryResultCachedVideo(InlineQueryResult):
    """Represents a link to a video file stored on the Telegram servers.

    By default, this video file will be sent by the user with an optional caption.
    Alternatively, you can use input_message_content to send a message with the specified
    content instead of the video.

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        video_file_id (str): A valid file identifier for the video file.
        title (str): Title for the result.
        description (Optional[str]): Short description of the result.
        caption (Optional[str]): Caption of the video to be sent, 0-200 characters.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the video
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 video_file_id,
                 title,
                 description=None,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):
        # Required
        super(InlineQueryResultCachedVideo, self).__init__('video', id)
        self.video_file_id = video_file_id
        self.title = title

        # Optionals
        if description:
            self.description = description
        if caption:
            self.caption = caption
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultCachedVideo, InlineQueryResultCachedVideo).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultCachedVideo(**data)


class InlineQueryResultCachedVoice(InlineQueryResult):
    """Represents a link to a voice message stored on the Telegram servers.

    By default, this voice message will be sent by the user. Alternatively, you can use
    input_message_content to send a message with the specified content instead of the voice
    message.

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        voice_file_id (str): A valid file identifier for the voice message.
        title (str): Voice message title.
        caption (Optional[str]): Caption, 0-200 characters.
        reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): Inline keyboard attached
            to the message.
        input_message_content (Optional[:class:`telegram.InputMessageContent`]): Content of the
            message to be sent instead of the voice message.'
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 voice_file_id,
                 title,
                 caption=None,
                 reply_markup=None,
                 input_message_content=None,
                 **kwargs):
        # Required
        super(InlineQueryResultCachedVoice, self).__init__('voice', id)
        self.voice_file_id = voice_file_id
        self.title = title

        # Optionals
        if caption:
            self.caption = caption
        if reply_markup:
            self.reply_markup = reply_markup
        if input_message_content:
            self.input_message_content = input_message_content

    @staticmethod
    def de_json(data, bot):
        data = super(InlineQueryResultCachedVoice, InlineQueryResultCachedVoice).de_json(data, bot)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'), bot)
        data['input_message_content'] = InputMessageContent.de_json(
            data.get('input_message_content'), bot)

        return InlineQueryResultCachedVoice(**data)
