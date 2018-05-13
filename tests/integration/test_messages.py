import re
import sys

import pytest

from telegram.ext import Filters, MessageHandler
from tgintegration import BotIntegrationClient

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 5),
    reason="TgIntegration requires Python 3.5 upwards")


class TestMessagesIntegration(object):
    TEST_STRING = "Hi there, I'm running integration tests."
    ECHO_STRING = "Testing echos"

    def test_echo_text(self, dp, client):
        def callback_echo(_bot, update):
            update.message.reply_text(update.message.text)

        handler = MessageHandler(Filters.regex(pattern=re.escape(self.ECHO_STRING)),
                                 callback_echo)
        dp.add_handler(handler)

        response = client.send_message_await(self.ECHO_STRING)

        assert not response.empty
        assert response.full_text == self.ECHO_STRING

    def test_message(self, dp, client):
        def callback_basic(_bot, update):
            update.message.reply_text(self.TEST_STRING)

        handler = MessageHandler(Filters.text, callback_basic)
        dp.add_handler(handler)

        response = client.send_message_await("Hola, Señor")

        assert not response.empty
        assert response.full_text == self.TEST_STRING

    @staticmethod
    def run_file_echo_test(dp, client, type_name, filename, internal_name=None):
        if internal_name is None:
            internal_name = type_name

        def echo(bot, update):
            # Get corresponding reply_* method in update.message
            reply_method = getattr(update.message, "reply_" + internal_name)

            # Extract file
            message_file = getattr(update.message, internal_name)
            if isinstance(message_file, list):
                message_file = message_file[-1]

            # Example result:
            # update.message.reply_photo(update.message.photo[-1])
            reply_method(message_file)

        handler = MessageHandler(getattr(Filters, internal_name), echo)
        dp.add_handler(handler)

        send_await_method = getattr(client, 'send_{}_await'.format(type_name))

        file = '../data/{}'.format(filename)

        # Example:
        # response = client.send_photo_await('../data/telegram.jpg')
        response = send_await_method(file)

        sent = getattr(response.action_result, internal_name)
        sent_file_size = (sent[0] if isinstance(sent, list) else sent).file_size

        assert not response.empty

        received = getattr(response.messages[0], internal_name)
        received_file_size = (received[0] if isinstance(received, list) else received).file_size

        assert sent_file_size == received_file_size

    def test_echo_photo(self, dp, client: BotIntegrationClient):
        self.run_file_echo_test(dp, client, 'photo', 'telegram.jpg')

    def test_echo_gif(self, dp, client):
        self.run_file_echo_test(dp, client, 'photo', 'telegram.gif')

    def test_echo_animated_gif(self, dp, client):
        self.run_file_echo_test(dp, client, 'video', 'animated_gif.mp4',
                                internal_name='document')

    def test_echo_voice(self, dp, client):
        self.run_file_echo_test(dp, client, 'voice', 'telegram.ogg')

    def test_echo_sticker(self, dp, client):
        self.run_file_echo_test(dp, client, 'sticker', 'telegram.webp')

    def test_echo_audio(self, dp, client):
        self.run_file_echo_test(dp, client, 'audio', 'telegram.mp3')

    def test_echo_video(self, dp, client):
        self.run_file_echo_test(dp, client, 'video', 'telegram.mp4')
