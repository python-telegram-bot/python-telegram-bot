import os
import time

import pytest

from telegram.ext import Updater
from tests.bots import get_userbot
from tests.conftest import reset_dispatcher
from tests.integration import USERBOT_SESSION_ENV_VAR
from tgintegration import BotIntegrationClient, InteractionClient

# Parse a base64-encoded Pyrogram session from environment variables, decode it, and save it as a
# regular session.
session_encoded = os.environ.get(USERBOT_SESSION_ENV_VAR)

# Same module as this file
output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'userbot_account.session')

# If session does not exist, create it from environment variable value.
if not os.path.exists(output_file):
    if session_encoded is not None:
        InteractionClient.create_session_from_export(session_encoded, output_file)


@pytest.fixture(scope='module')
def userbot_info():
    return get_userbot()


@pytest.fixture(scope='module')
def updater(bot_info):
    up = Updater(bot_info['token'])
    print("Starting to poll...", end=' ', flush=True)
    up.start_polling()
    time.sleep(2)
    print("listening.")
    yield up
    time.sleep(1)
    if up.running:
        up.stop()


@pytest.fixture(scope='module')
def client(userbot_info, bot):
    c = BotIntegrationClient(
        bot_under_test=bot.get_me().username,
        session_name=userbot_info['session_name'],
        api_id=int(userbot_info['api_id']),
        api_hash=userbot_info['api_hash'],
        phone_number=userbot_info['phone_number'],
        max_wait_response=15,  # seconds
        min_wait_consecutive=None,  # We do not neet to wait for more than one message
        raise_no_response=False,  # We will check for `response.empty` instead
        global_action_delay=2.0  # Let's never cause flood timeouts, even if it takes longer
    )
    print("Initializing integration test client...", end=' ', flush=True)
    c.start(debug=True)
    time.sleep(1)
    print("done.")
    yield c
    c.stop()


@pytest.fixture(scope='function')
def dp(updater):
    for d in reset_dispatcher(updater.dispatcher):
        def error(bot, update, error):
            print(error)  # TODO: this is not right

        d.add_error_handler(error)
        yield d
