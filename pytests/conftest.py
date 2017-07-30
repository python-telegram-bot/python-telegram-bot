import os
import sys

import pytest

from pytests.bots import get_bot
from telegram import Bot

TRAVIS = os.getenv('TRAVIS', True)

if TRAVIS:
    pytest_plugins = ['pytests.travis_fold']


@pytest.fixture(scope="session")
def bot_info():
    return get_bot()


@pytest.fixture(scope="class")
def bot(bot_info):
    return Bot(bot_info['token'])


@pytest.fixture(scope="session")
def chat_id(bot_info):
    return bot_info['chat_id']


def pytest_configure(config):
    if sys.version_info >= (3,):
        config.addinivalue_line('filterwarnings', 'ignore::ResourceWarning')
        # TODO: Write so good code that we don't need to ignore ResourceWarnings anymore
