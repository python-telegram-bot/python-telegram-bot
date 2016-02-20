#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
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

"""This module contains a object that represents Tests for Telegram
InlineResults"""

import sys

if sys.version_info[0:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest

sys.path.append('.')

import telegram
from tests.base import BaseTest


class InlineQueryResultArticleTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InlineQueryResultArticle."""

    def setUp(self):
        self.id = 'id'
        self.type = 'article'
        self.title = 'title'
        self.message_text = 'message text'
        self.parse_mode = 'HTML'
        self.disable_web_page_preview = True
        self.url = 'url'
        self.hide_url = True
        self.description = 'description'
        self.thumb_url = 'thumb url'
        self.thumb_height = 10
        self.thumb_width = 15

        self.json_dict = {
            'type': self.type,
            'id': self.id,
            'title': self.title,
            'message_text': self.message_text,
            'parse_mode': self.parse_mode,
            'disable_web_page_preview': self.disable_web_page_preview,
            'url': self.url,
            'hide_url': self.hide_url,
            'description': self.description,
            'thumb_url': self.thumb_url,
            'thumb_height': self.thumb_height,
            'thumb_width': self.thumb_width
        }

    def test_article_de_json(self):
        """Test InlineQueryResultArticle.de_json() method"""
        print('Testing InlineQueryResultArticle.de_json()')

        article = telegram.InlineQueryResultArticle.de_json(self.json_dict)

        self.assertEqual(article.type, self.type)
        self.assertEqual(article.id, self.id)
        self.assertEqual(article.title, self.title)
        self.assertEqual(article.message_text, self.message_text)
        self.assertEqual(article.parse_mode, self.parse_mode)
        self.assertEqual(article.disable_web_page_preview,
                         self.disable_web_page_preview)
        self.assertEqual(article.url, self.url)
        self.assertEqual(article.hide_url, self.hide_url)
        self.assertEqual(article.description, self.description)
        self.assertEqual(article.thumb_url, self.thumb_url)
        self.assertEqual(article.thumb_height, self.thumb_height)
        self.assertEqual(article.thumb_width, self.thumb_width)

    def test_article_to_json(self):
        """Test InlineQueryResultArticle.to_json() method"""
        print('Testing InlineQueryResultArticle.to_json()')

        article = telegram.InlineQueryResultArticle.de_json(self.json_dict)

        self.assertTrue(self.is_json(article.to_json()))

    def test_article_to_dict(self):
        """Test InlineQueryResultArticle.to_dict() method"""
        print('Testing InlineQueryResultArticle.to_dict()')

        article = \
            telegram.InlineQueryResultArticle.de_json(self.json_dict).to_dict()

        self.assertTrue(self.is_dict(article))
        self.assertDictEqual(self.json_dict, article)


class InlineQueryResultPhotoTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InlineQueryResultPhoto."""

    def setUp(self):
        self.id = 'id'
        self.type = 'photo'
        self.photo_url = 'photo url'
        self.mime_type = 'mime type'
        self.photo_width = 10
        self.photo_height = 15
        self.thumb_url = 'thumb url'
        self.title = 'title'
        self.caption = 'caption'
        self.message_text = 'message text'
        self.parse_mode = 'parse mode'
        self.disable_web_page_preview = True

        self.json_dict = {
            'type': self.type,
            'id': self.id,
            'photo_url': self.photo_url,
            'mime_type': self.mime_type,
            'photo_width': self.photo_width,
            'photo_height': self.photo_height,
            'thumb_url': self.thumb_url,
            'title': self.title,
            'caption': self.caption,
            'message_text': self.message_text,
            'parse_mode': self.parse_mode,
            'disable_web_page_preview': self.disable_web_page_preview
        }

    def test_photo_de_json(self):
        """Test InlineQueryResultPhoto.de_json() method"""
        print('Testing InlineQueryResultPhoto.de_json()')

        photo = telegram.InlineQueryResultPhoto.de_json(self.json_dict)

        self.assertEqual(photo.type, self.type)
        self.assertEqual(photo.id, self.id)
        self.assertEqual(photo.photo_url, self.photo_url)
        self.assertEqual(photo.mime_type, self.mime_type)
        self.assertEqual(photo.photo_width, self.photo_width)
        self.assertEqual(photo.photo_height, self.photo_height)
        self.assertEqual(photo.thumb_url, self.thumb_url)
        self.assertEqual(photo.title, self.title)
        self.assertEqual(photo.caption, self.caption)
        self.assertEqual(photo.message_text, self.message_text)
        self.assertEqual(photo.parse_mode, self.parse_mode)
        self.assertEqual(photo.disable_web_page_preview,
                         self.disable_web_page_preview)

    def test_photo_to_json(self):
        """Test InlineQueryResultPhoto.to_json() method"""
        print('Testing InlineQueryResultPhoto.to_json()')

        photo = telegram.InlineQueryResultPhoto.de_json(self.json_dict)

        self.assertTrue(self.is_json(photo.to_json()))

    def test_photo_to_dict(self):
        """Test InlineQueryResultPhoto.to_dict() method"""
        print('Testing InlineQueryResultPhoto.to_dict()')

        photo = \
            telegram.InlineQueryResultPhoto.de_json(self.json_dict).to_dict()

        self.assertTrue(self.is_dict(photo))
        self.assertDictEqual(self.json_dict, photo)


class InlineQueryResultGifTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InlineQueryResultGif."""

    def setUp(self):
        self.id = 'id'
        self.type = 'gif'
        self.gif_url = 'gif url'
        self.gif_width = 10
        self.gif_height = 15
        self.thumb_url = 'thumb url'
        self.title = 'title'
        self.caption = 'caption'
        self.message_text = 'message text'
        self.parse_mode = 'parse mode'
        self.disable_web_page_preview = True

        self.json_dict = {
            'type': self.type,
            'id': self.id,
            'gif_url': self.gif_url,
            'gif_width': self.gif_width,
            'gif_height': self.gif_height,
            'thumb_url': self.thumb_url,
            'title': self.title,
            'caption': self.caption,
            'message_text': self.message_text,
            'parse_mode': self.parse_mode,
            'disable_web_page_preview': self.disable_web_page_preview
        }

    def test_gif_de_json(self):
        """Test InlineQueryResultGif.de_json() method"""
        print('Testing InlineQueryResultGif.de_json()')

        gif = telegram.InlineQueryResultGif.de_json(self.json_dict)

        self.assertEqual(gif.type, self.type)
        self.assertEqual(gif.id, self.id)
        self.assertEqual(gif.gif_url, self.gif_url)
        self.assertEqual(gif.gif_width, self.gif_width)
        self.assertEqual(gif.gif_height, self.gif_height)
        self.assertEqual(gif.thumb_url, self.thumb_url)
        self.assertEqual(gif.title, self.title)
        self.assertEqual(gif.caption, self.caption)
        self.assertEqual(gif.message_text, self.message_text)
        self.assertEqual(gif.parse_mode, self.parse_mode)
        self.assertEqual(gif.disable_web_page_preview,
                         self.disable_web_page_preview)

    def test_gif_to_json(self):
        """Test InlineQueryResultGif.to_json() method"""
        print('Testing InlineQueryResultGif.to_json()')

        gif = telegram.InlineQueryResultGif.de_json(self.json_dict)

        self.assertTrue(self.is_json(gif.to_json()))

    def test_gif_to_dict(self):
        """Test InlineQueryResultGif.to_dict() method"""
        print('Testing InlineQueryResultGif.to_dict()')

        gif = telegram.InlineQueryResultGif.de_json(self.json_dict).to_dict()

        self.assertTrue(self.is_dict(gif))
        self.assertDictEqual(self.json_dict, gif)


class InlineQueryResultMpeg4GifTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InlineQueryResultMpeg4Gif."""

    def setUp(self):
        self.id = 'id'
        self.type = 'mpeg4_gif'
        self.mpeg4_url = 'mpeg4 url'
        self.mpeg4_width = 10
        self.mpeg4_height = 15
        self.thumb_url = 'thumb url'
        self.title = 'title'
        self.caption = 'caption'
        self.message_text = 'message text'
        self.parse_mode = 'parse mode'
        self.disable_web_page_preview = True

        self.json_dict = {
            'type': self.type,
            'id': self.id,
            'mpeg4_url': self.mpeg4_url,
            'mpeg4_width': self.mpeg4_width,
            'mpeg4_height': self.mpeg4_height,
            'thumb_url': self.thumb_url,
            'title': self.title,
            'caption': self.caption,
            'message_text': self.message_text,
            'parse_mode': self.parse_mode,
            'disable_web_page_preview': self.disable_web_page_preview
        }

    def test_mpeg4_de_json(self):
        """Test InlineQueryResultMpeg4Gif.de_json() method"""
        print('Testing InlineQueryResultMpeg4Gif.de_json()')

        mpeg4 = telegram.InlineQueryResultMpeg4Gif.de_json(self.json_dict)

        self.assertEqual(mpeg4.type, self.type)
        self.assertEqual(mpeg4.id, self.id)
        self.assertEqual(mpeg4.mpeg4_url, self.mpeg4_url)
        self.assertEqual(mpeg4.mpeg4_width, self.mpeg4_width)
        self.assertEqual(mpeg4.mpeg4_height, self.mpeg4_height)
        self.assertEqual(mpeg4.thumb_url, self.thumb_url)
        self.assertEqual(mpeg4.title, self.title)
        self.assertEqual(mpeg4.caption, self.caption)
        self.assertEqual(mpeg4.message_text, self.message_text)
        self.assertEqual(mpeg4.parse_mode, self.parse_mode)
        self.assertEqual(mpeg4.disable_web_page_preview,
                         self.disable_web_page_preview)

    def test_mpeg4_to_json(self):
        """Test InlineQueryResultMpeg4Gif.to_json() method"""
        print('Testing InlineQueryResultMpeg4Gif.to_json()')

        mpeg4 = telegram.InlineQueryResultMpeg4Gif.de_json(self.json_dict)

        self.assertTrue(self.is_json(mpeg4.to_json()))

    def test_mpeg4_to_dict(self):
        """Test InlineQueryResultMpeg4Gif.to_dict() method"""
        print('Testing InlineQueryResultMpeg4Gif.to_dict()')

        mpeg4 = \
            telegram.InlineQueryResultMpeg4Gif.de_json(self.json_dict).to_dict()

        self.assertTrue(self.is_dict(mpeg4))
        self.assertDictEqual(self.json_dict, mpeg4)


class InlineQueryResultVideoTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram InlineQueryResultVideo."""

    def setUp(self):
        self.id = 'id'
        self.type = 'video'
        self.video_url = 'video url'
        self.mime_type = 'mime type'
        self.video_width = 10
        self.video_height = 15
        self.video_duration = 15
        self.thumb_url = 'thumb url'
        self.title = 'title'
        self.caption = 'caption'
        self.description = 'description'
        self.message_text = 'message text'
        self.parse_mode = 'parse mode'
        self.disable_web_page_preview = True

        self.json_dict = {
            'type': self.type,
            'id': self.id,
            'video_url': self.video_url,
            'mime_type': self.mime_type,
            'video_width': self.video_width,
            'video_height': self.video_height,
            'video_duration': self.video_duration,
            'thumb_url': self.thumb_url,
            'title': self.title,
            'caption': self.caption,
            'description': self.description,
            'message_text': self.message_text,
            'parse_mode': self.parse_mode,
            'disable_web_page_preview': self.disable_web_page_preview
        }

    def test_video_de_json(self):
        """Test InlineQueryResultVideo.de_json() method"""
        print('Testing InlineQueryResultVideo.de_json()')

        video = telegram.InlineQueryResultVideo.de_json(self.json_dict)

        self.assertEqual(video.type, self.type)
        self.assertEqual(video.id, self.id)
        self.assertEqual(video.video_url, self.video_url)
        self.assertEqual(video.mime_type, self.mime_type)
        self.assertEqual(video.video_width, self.video_width)
        self.assertEqual(video.video_height, self.video_height)
        self.assertEqual(video.video_duration, self.video_duration)
        self.assertEqual(video.thumb_url, self.thumb_url)
        self.assertEqual(video.title, self.title)
        self.assertEqual(video.description, self.description)
        self.assertEqual(video.caption, self.caption)
        self.assertEqual(video.message_text, self.message_text)
        self.assertEqual(video.parse_mode, self.parse_mode)
        self.assertEqual(video.disable_web_page_preview,
                         self.disable_web_page_preview)

    def test_video_to_json(self):
        """Test InlineQueryResultVideo.to_json() method"""
        print('Testing InlineQueryResultVideo.to_json()')

        video = telegram.InlineQueryResultVideo.de_json(self.json_dict)

        self.assertTrue(self.is_json(video.to_json()))

    def test_video_to_dict(self):
        """Test InlineQueryResultVideo.to_dict() method"""
        print('Testing InlineQueryResultVideo.to_dict()')

        video = \
            telegram.InlineQueryResultVideo.de_json(self.json_dict).to_dict()

        self.assertTrue(self.is_dict(video))
        self.assertDictEqual(self.json_dict, video)


if __name__ == '__main__':
    unittest.main()
