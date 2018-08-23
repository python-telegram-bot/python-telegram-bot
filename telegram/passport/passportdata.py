#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
"""Contains information about Telegram Passport data shared with the bot by the user."""
import warnings

from telegram import EncryptedCredentials, EncryptedPassportElement, TelegramObject
from telegram.passport.credentials import _TelegramDecryptionError


class PassportData(TelegramObject):
    """Contains information about Telegram Passport data shared with the bot by the user.

    Attributes:
        data (List[:class:`telegram.EncryptedPassportElement`]): Array with information about
            documents and other Telegram Passport elements that was shared with the bot.
        credentials (:class:`telegram.EncryptedCredentials`): Encrypted credentials that were
            used to decrypt the data. This object also contains the user specified payload as
            `data.payload`.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.

    Args:
        data (List[:class:`telegram.EncryptedPassportElement`]): Array with information about
            documents and other Telegram Passport elements that was shared with the bot.
        credentials (:class:`telegram.EncryptedCredentials`): Encrypted credentials that will be
            used to decrypt the data
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Note:
        Python-telegram-bot automatically decrypts your :class:`telegram.PassportData` objects for
        you if you set a private key when initializing :class:`telegram.Bot` or
        :class:`telegram.Updater`, This means that the data in the :attr:`data`
        attribute despite its name, :class:`telegram.EncryptedPassportElement`, is in fact
        decrypted.

    """

    def __init__(self, data, credentials, bot=None, **kwargs):
        self.data = data
        self.credentials = credentials
        self.bot = bot

        self._id_attrs = tuple([x.type for x in data] + [credentials.hash])

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        # User did not configure any private_key, ignore PassportData (and therefore the entire
        # Update)
        if not hasattr(bot, 'private_key'):
            warnings.warn('Received update with PassportData but no private key is specified! '
                          'See https://git.io/fAvYd for more info.')
            return None

        try:
            # Try decrypting the credentials
            data = super(PassportData, cls).de_json(data, bot)
            data['credentials'] = EncryptedCredentials.de_json(data.get('credentials'), bot)
            # Passing them to where they are needed
            data['data'] = EncryptedPassportElement.de_list(data.get('data'), bot,
                                                            credentials=data['credentials'])
        except _TelegramDecryptionError as e:
            # _TelegramDecryptionError is raised on a decryption error, we turn it into a
            # warning here, since if we allowed it to propagate it might hang the Updater.
            warnings.warn('Telegram passport decryption error: {} '
                          'See https://git.io/fAvYd for more info.'.format(e))
            return None

        return cls(bot=bot, **data)

    def to_dict(self):
        data = super(PassportData, self).to_dict()

        if self.data:
            data['data'] = [p.to_dict() for p in self.data]

        return data
