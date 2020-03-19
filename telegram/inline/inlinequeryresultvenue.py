#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
"""This module contains the classes that represent Telegram InlineQueryResultVenue."""

from telegram import InlineQueryResult


class InlineQueryResultVenue(InlineQueryResult):
    """
    Represents a venue. By default, the venue will be sent by the user. Alternatively, you can
    use :attr:`input_message_content` to send a message with the specified content instead of the
    venue.

    Attributes:
        type (:obj:`str`): 'venue'.
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.
        latitude (:obj:`float`): Latitude of the venue location in degrees.
        longitude (:obj:`float`): Longitude of the venue location in degrees.
        title (:obj:`str`): Title of the venue.
        address (:obj:`str`): Address of the venue.
        foursquare_id (:obj:`str`): Optional. Foursquare identifier of the venue if known.
        foursquare_type (:obj:`str`): Optional. Foursquare type of the venue, if known.
            (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or
            "food/icecream".)
        reply_markup (:class:`telegram.InlineKeyboardMarkup`): Optional. Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`): Optional. Content of the
            message to be sent instead of the venue.
        thumb_url (:obj:`str`): Optional. Url of the thumbnail for the result.
        thumb_width (:obj:`int`): Optional. Thumbnail width.
        thumb_height (:obj:`int`): Optional. Thumbnail height.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.
        latitude (:obj:`float`): Latitude of the venue location in degrees.
        longitude (:obj:`float`): Longitude of the venue location in degrees.
        title (:obj:`str`): Title of the venue.
        address (:obj:`str`): Address of the venue.
        foursquare_id (:obj:`str`, optional): Foursquare identifier of the venue if known.
        foursquare_type (:obj:`str`, optional): Foursquare type of the venue, if known.
            (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or
            "food/icecream".)
        reply_markup (:class:`telegram.InlineKeyboardMarkup`, optional): Inline keyboard attached
            to the message.
        input_message_content (:class:`telegram.InputMessageContent`, optional): Content of the
            message to be sent instead of the location.
        thumb_url (:obj:`str`, optional): Url of the thumbnail for the result.
        thumb_width (:obj:`int`, optional): Thumbnail width.
        thumb_height (:obj:`int`, optional): Thumbnail height.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 latitude,
                 longitude,
                 title,
                 address,
                 foursquare_id=None,
                 foursquare_type=None,
                 reply_markup=None,
                 input_message_content=None,
                 thumb_url=None,
                 thumb_width=None,
                 thumb_height=None,
                 **kwargs):

        # Required
        super().__init__('venue', id)
        self.latitude = latitude
        self.longitude = longitude
        self.title = title
        self.address = address

        # Optional
        self.foursquare_id = foursquare_id
        self.foursquare_type = foursquare_type
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height
