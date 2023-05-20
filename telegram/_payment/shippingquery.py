#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
"""This module contains an object that represents a Telegram ShippingQuery."""

from typing import TYPE_CHECKING, Optional, Sequence

from telegram._payment.shippingaddress import ShippingAddress
from telegram._payment.shippingoption import ShippingOption
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import JSONDict, ODVInput

if TYPE_CHECKING:
    from telegram import Bot


class ShippingQuery(TelegramObject):
    """This object contains information about an incoming shipping query.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Note:
        In Python :keyword:`from` is a reserved word. Use :paramref:`from_user` instead.

    Args:
        id (:obj:`str`): Unique query identifier.
        from_user (:class:`telegram.User`): User who sent the query.
        invoice_payload (:obj:`str`): Bot specified invoice payload.
        shipping_address (:class:`telegram.ShippingAddress`): User specified shipping address.

    Attributes:
        id (:obj:`str`): Unique query identifier.
        from_user (:class:`telegram.User`): User who sent the query.
        invoice_payload (:obj:`str`): Bot specified invoice payload.
        shipping_address (:class:`telegram.ShippingAddress`): User specified shipping address.


    """

    __slots__ = ("invoice_payload", "shipping_address", "id", "from_user")

    def __init__(
        self,
        id: str,  # pylint: disable=redefined-builtin
        from_user: User,
        invoice_payload: str,
        shipping_address: ShippingAddress,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.id: str = id  # pylint: disable=invalid-name
        self.from_user: User = from_user
        self.invoice_payload: str = invoice_payload
        self.shipping_address: ShippingAddress = shipping_address

        self._id_attrs = (self.id,)

        self._freeze()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["ShippingQuery"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["from_user"] = User.de_json(data.pop("from", None), bot)
        data["shipping_address"] = ShippingAddress.de_json(data.get("shipping_address"), bot)

        return super().de_json(data=data, bot=bot)

    async def answer(  # pylint: disable=invalid-name
        self,
        ok: bool,
        shipping_options: Optional[Sequence[ShippingOption]] = None,
        error_message: Optional[str] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """Shortcut for::

             await bot.answer_shipping_query(update.shipping_query.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.answer_shipping_query`.

        """
        return await self.get_bot().answer_shipping_query(
            shipping_query_id=self.id,
            ok=ok,
            shipping_options=shipping_options,
            error_message=error_message,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
