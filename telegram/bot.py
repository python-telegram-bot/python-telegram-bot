#!/usr/bin/env python

"""A library that provides a Python interface to the Telegram Bots API"""

import json
import requests

from telegram import (User, Message, Update)


class Bot(object):
    def __init__(self,
                 token,
                 base_url=None):

        if base_url is None:
            self.base_url = 'https://api.telegram.org/bot%s' % token
        else:
            self.base_url = base_url + token

    def getMe(self):

        url = '%s/getMe' % (self.base_url)

        json_data = self._requestUrl(url, 'GET')
        data = self._parseAndCheckTelegram(json_data.content)

        return User.newFromJsonDict(data)

    def sendMessage(self,
                    chat_id,
                    text,
                    disable_web_page_preview=None,
                    reply_to_message_id=None,
                    reply_markup=None):

        url = '%s/sendMessage' % (self.base_url)

        data = {'chat_id': chat_id,
                'text': text}
        if disable_web_page_preview:
            data['disable_web_page_preview'] = disable_web_page_preview
        if reply_to_message_id:
            data['reply_to_message_id'] = reply_to_message_id
        if reply_markup:
            data['reply_markup'] = reply_markup

        json_data = self._requestUrl(url, 'POST', data=data)
        data = self._parseAndCheckTelegram(json_data.content)

        return Message.newFromJsonDict(data)

    def forwardMessage(self,
                       chat_id,
                       from_chat_id,
                       message_id):

        url = '%s/forwardMessage' % (self.base_url)

        data = {}
        if chat_id:
            data['chat_id'] = chat_id
        if from_chat_id:
            data['from_chat_id'] = from_chat_id
        if message_id:
            data['message_id'] = message_id

        json_data = self._requestUrl(url, 'POST', data=data)
        data = self._parseAndCheckTelegram(json_data.content)

        return Message.newFromJsonDict(data)

    def sendPhoto(self,
                  chat_id,
                  photo,
                  caption=None,
                  reply_to_message_id=None,
                  reply_markup=None):

        url = '%s/sendPhoto' % (self.base_url)

        data = {'chat_id': chat_id,
                'photo': photo}
        if caption:
            data['caption'] = caption
        if reply_to_message_id:
            data['reply_to_message_id'] = reply_to_message_id
        if reply_markup:
            data['reply_markup'] = reply_markup

        json_data = self._requestUrl(url, 'POST', data=data)
        data = self._parseAndCheckTelegram(json_data.content)

        return Message.newFromJsonDict(data)

    def sendAudio(self):
        url = '%s/sendAudio' % (self.base_url)

    def sendDocument(self):
        url = '%s/sendDocument' % (self.base_url)

    def sendSticker(self):
        url = '%s/sendSticker' % (self.base_url)

    def sendVideo(self):
        url = '%s/sendVideo' % (self.base_url)

    def sendLocation(self):
        url = '%s/sendLocation' % (self.base_url)

    def sendChatAction(self):
        url = '%s/sendChatAction' % (self.base_url)

    def getUserProfilePhotos(self):
        url = '%s/getUserProfilePhotos' % (self.base_url)

    def getUpdates(self,
                   offset=None,
                   limit=100,
                   timeout=0):

        url = '%s/getUpdates' % (self.base_url)

        data = {}
        if offset:
            data['offset'] = offset
        if limit:
            data['limit'] = limit
        if timeout:
            data['timeout'] = timeout

        json_data = self._requestUrl(url, 'POST', data=data)
        data = self._parseAndCheckTelegram(json_data.content)

        return [Update.newFromJsonDict(x) for x in data]

    def setWebhook(self):
        url = '%s/setWebhook' % (self.base_url)

    def _requestUrl(self,
                    url,
                    method,
                    data=None):

        if method == 'POST':
            try:
                return requests.post(
                    url,
                    data=data
                )
            except requests.RequestException as e:
                pass
        if method == 'GET':
            try:
                return requests.get(url)
            except requests.RequestException as e:
                pass  # raise TelegramError(str(e))
        return 0

    def _parseAndCheckTelegram(self,
                               json_data):

        try:
            data = json.loads(json_data)
        except ValueError:
            pass

        return data['result']
