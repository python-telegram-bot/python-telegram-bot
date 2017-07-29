import json

import pytest

from pytests.bots import get_bot
from telegram import Bot

@pytest.fixture(scope="session")
def bot_info():
    return get_bot()

@pytest.fixture(scope="class")
def bot(bot_info):
    return Bot(bot_info['token'])

@pytest.fixture(scope="session")
def chat_id(bot_info):
    return bot_info['chat_id']

@pytest.fixture(scope="session")
def is_json():
    def _is_json(string):
        try:
            json.loads(string)
        except ValueError:
            return False

        return True
    return _is_json

@pytest.fixture(scope="session")
def is_dict():
    def _is_dict(dictionary):
        if isinstance(dictionary, dict):
            return True
        return False
    return _is_dict

def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item

def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" % previousfailed.name)

# self._group_id = os.environ.get('GROUP_ID', '-49740850')
# self._channel_id = os.environ.get('CHANNEL_ID', '@pythontelegrambottests')
# self._bot = bot
# self._chat_id = chat_id
# self._payment_provider_token = os.environ.get('PAYMENT_PROVIDER_TOKEN', '284685063:TEST:ZGJlMmQxZDI3ZTc3')