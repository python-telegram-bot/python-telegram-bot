#!/usr/bin/env python
# encoding: utf-8
#
# Robô Ed Telegram Bot
# Copyright (C) 2015 Leandro Toledo de Souza <leandrotoeldodesouza@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].


__author__ = 'leandrotoledodesouza@gmail.com'

import logging
import telegram
import urllib


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    bot = telegram.Bot('TOKEN')  # Telegram Bot Authorization Token

    LAST_UPDATE_ID = bot.getUpdates()[-1].update_id  # Get lastest update

    while True:
        for update in bot.getUpdates(offset=LAST_UPDATE_ID):
            text = update.message.text
            chat_id = update.message.chat.id
            update_id = update.update_id

            if LAST_UPDATE_ID < update_id:  # If newer than the initial
                                            # LAST_UPDATE_ID
                if text:
                    roboed = ed(text)  # Ask something to Robô Ed
                    bot.sendMessage(chat_id=chat_id, text=roboed)
                    LAST_UPDATE_ID = update_id


def ed(text):
    url = 'http://www.ed.conpet.gov.br/mod_perl/bot_gateway.cgi?server=0.0.0.0%3A8085&charset_post=utf-8&charset=utf-8&pure=1&js=0&tst=1&msg=' + text
    data = urllib.urlopen(url).read()

    return data.strip()

if __name__ == '__main__':
    main()
