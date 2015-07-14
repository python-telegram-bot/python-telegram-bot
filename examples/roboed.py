#!/usr/bin/env python
# encoding: utf-8

'''Robô Ed Telegram Bot'''

__author__ = 'leandrotoledodesouza@gmail.com'

import telegram
import urllib


def main():
    bot = telegram.Bot('TOKEN')  # Telegram Bot Authorization Token

    global LAST_UPDATE_ID
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
