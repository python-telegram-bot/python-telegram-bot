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
"""This module contains a class that represents a Telegram InputInvoiceMessageContent."""

from typing import Any, List, Optional, TYPE_CHECKING

from telegram import InputMessageContent, LabeledPrice
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class InputInvoiceMessageContent(InputMessageContent):
    """
    Represents the content of a invoice message to be sent as the result of an inline query.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`title`, :attr:`description`, :attr:`payload`,
    :attr:`provider_token`, :attr:`currency` and :attr:`prices` are equal.

    .. versionadded:: 13.5

    Args:
        title (:obj:`str`): Product name, 1-32 characters
        description (:obj:`str`): Product description, 1-255 characters
        payload (:obj:`str`):Bot-defined invoice payload, 1-128 bytes. This will not be displayed
            to the user, use for your internal processes.
        provider_token (:obj:`str`): Payment provider token, obtained via
            `@Botfather <https://t.me/Botfather>`_.
        currency (:obj:`str`): Three-letter ISO 4217 currency code, see more on
            `currencies <https://core.telegram.org/bots/payments#supported-currencies>`_
        prices (List[:class:`telegram.LabeledPrice`]): Price breakdown, a JSON-serialized list of
            components (e.g. product price, tax, discount, delivery cost, delivery tax, bonus,
            etc.)
        max_tip_amount (:obj:`int`, optional): The maximum accepted amount for tips in the smallest
            units of the currency (integer, not float/double). For example, for a maximum tip of
            US$ 1.45 pass ``max_tip_amount = 145``. See the ``exp`` parameter in
            `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_, it
            shows the number of digits past the decimal point for each currency (2 for the majority
            of currencies). Defaults to ``0``.
        suggested_tip_amounts (List[:obj:`int`], optional): A JSON-serialized array of suggested
            amounts of tip in the smallest units of the currency (integer, not float/double). At
            most 4 suggested tip amounts can be specified. The suggested tip amounts must be
            positive, passed in a strictly increased order and must not exceed
            :attr:`max_tip_amount`.
        provider_data (:obj:`str`, optional): A JSON-serialized object for data about the invoice,
            which will be shared with the payment provider. A detailed description of the required
            fields should be provided by the payment provider.
        photo_url (:obj:`str`, optional): URL of the product photo for the invoice. Can be a photo
            of the goods or a marketing image for a service. People like it better when they see
            what they are paying for.
        photo_size (:obj:`int`, optional): Photo size.
        photo_width (:obj:`int`, optional): Photo width.
        photo_height (:obj:`int`, optional): Photo height.
        need_name (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's full name to
            complete the order.
        need_phone_number (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's
            phone number to complete the order
        need_email (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's email
            address to complete the order.
        need_shipping_address (:obj:`bool`, optional): Pass :obj:`True`, if you require the user's
            shipping address to complete the order
        send_phone_number_to_provider (:obj:`bool`, optional): Pass :obj:`True`, if user's phone
            number should be sent to provider.
        send_email_to_provider (:obj:`bool`, optional): Pass :obj:`True`, if user's email address
            should be sent to provider.
        is_flexible (:obj:`bool`, optional): Pass :obj:`True`, if the final price depends on the
            shipping method.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        title (:obj:`str`): Product name, 1-32 characters
        description (:obj:`str`): Product description, 1-255 characters
        payload (:obj:`str`):Bot-defined invoice payload, 1-128 bytes. This will not be displayed
            to the user, use for your internal processes.
        provider_token (:obj:`str`): Payment provider token, obtained via
            `@Botfather <https://t.me/Botfather>`_.
        currency (:obj:`str`): Three-letter ISO 4217 currency code, see more on
            `currencies <https://core.telegram.org/bots/payments#supported-currencies>`_
        prices (List[:class:`telegram.LabeledPrice`]): Price breakdown, a JSON-serialized list of
            components.
        max_tip_amount (:obj:`int`): Optional. The maximum accepted amount for tips in the smallest
            units of the currency (integer, not float/double).
        suggested_tip_amounts (List[:obj:`int`]): Optional. A JSON-serialized array of suggested
            amounts of tip in the smallest units of the currency (integer, not float/double).
        provider_data (:obj:`str`): Optional. A JSON-serialized object for data about the invoice,
            which will be shared with the payment provider.
        photo_url (:obj:`str`): Optional. URL of the product photo for the invoice.
        photo_size (:obj:`int`): Optional. Photo size.
        photo_width (:obj:`int`): Optional. Photo width.
        photo_height (:obj:`int`): Optional. Photo height.
        need_name (:obj:`bool`): Optional. Pass :obj:`True`, if you require the user's full name to
            complete the order.
        need_phone_number (:obj:`bool`): Optional. Pass :obj:`True`, if you require the user's
            phone number to complete the order
        need_email (:obj:`bool`): Optional. Pass :obj:`True`, if you require the user's email
            address to complete the order.
        need_shipping_address (:obj:`bool`): Optional. Pass :obj:`True`, if you require the user's
            shipping address to complete the order
        send_phone_number_to_provider (:obj:`bool`): Optional. Pass :obj:`True`, if user's phone
            number should be sent to provider.
        send_email_to_provider (:obj:`bool`): Optional. Pass :obj:`True`, if user's email address
            should be sent to provider.
        is_flexible (:obj:`bool`): Optional. Pass :obj:`True`, if the final price depends on the
            shipping method.

    """

    __slots__ = (
        'title',
        'description',
        'payload',
        'provider_token',
        'currency',
        'prices',
        'max_tip_amount',
        'suggested_tip_amounts',
        'provider_data',
        'photo_url',
        'photo_size',
        'photo_width',
        'photo_height',
        'need_name',
        'need_phone_number',
        'need_email',
        'need_shipping_address',
        'send_phone_number_to_provider',
        'send_email_to_provider',
        'is_flexible',
        '_id_attrs',
    )

    def __init__(
        self,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: List[LabeledPrice],
        max_tip_amount: int = None,
        suggested_tip_amounts: List[int] = None,
        provider_data: str = None,
        photo_url: str = None,
        photo_size: int = None,
        photo_width: int = None,
        photo_height: int = None,
        need_name: bool = None,
        need_phone_number: bool = None,
        need_email: bool = None,
        need_shipping_address: bool = None,
        send_phone_number_to_provider: bool = None,
        send_email_to_provider: bool = None,
        is_flexible: bool = None,
        **_kwargs: Any,
    ):
        # Required
        self.title = title
        self.description = description
        self.payload = payload
        self.provider_token = provider_token
        self.currency = currency
        self.prices = prices
        # Optionals
        self.max_tip_amount = int(max_tip_amount) if max_tip_amount else None
        self.suggested_tip_amounts = (
            [int(sta) for sta in suggested_tip_amounts] if suggested_tip_amounts else None
        )
        self.provider_data = provider_data
        self.photo_url = photo_url
        self.photo_size = int(photo_size) if photo_size else None
        self.photo_width = int(photo_width) if photo_width else None
        self.photo_height = int(photo_height) if photo_height else None
        self.need_name = need_name
        self.need_phone_number = need_phone_number
        self.need_email = need_email
        self.need_shipping_address = need_shipping_address
        self.send_phone_number_to_provider = send_phone_number_to_provider
        self.send_email_to_provider = send_email_to_provider
        self.is_flexible = is_flexible

        self._id_attrs = (
            self.title,
            self.description,
            self.payload,
            self.provider_token,
            self.currency,
            self.prices,
        )

    def __hash__(self) -> int:
        # we override this as self.prices is a list and not hashable
        prices = tuple(self.prices)
        return hash(
            (
                self.title,
                self.description,
                self.payload,
                self.provider_token,
                self.currency,
                prices,
            )
        )

    def to_dict(self) -> JSONDict:
        """See :meth:`telegram.TelegramObject.to_dict`."""
        data = super().to_dict()

        data['prices'] = [price.to_dict() for price in self.prices]

        return data

    @classmethod
    def de_json(
        cls, data: Optional[JSONDict], bot: 'Bot'
    ) -> Optional['InputInvoiceMessageContent']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data['prices'] = LabeledPrice.de_list(data.get('prices'), bot)

        return cls(**data, bot=bot)
