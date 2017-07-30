import os
import json

import pytest

from pytests.bots import get_bot
from telegram import Bot

TRAVIS = os.getenv('TRAVIS', False)


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


if TRAVIS:
    fold_plugins = {'_cov': 'Coverage report', 'flaky': 'Flaky report'}

    def terminal_summary_wrapper(original, plugin_name):
        text = fold_plugins[plugin_name]

        def pytest_terminal_summary(terminalreporter):
            terminalreporter.write("travis_fold:start:plugin.{}\n{}\n".format(plugin_name, text))
            original(terminalreporter)
            terminalreporter.write("travis_fold:end:plugin.{}\n".format(plugin_name))

        return pytest_terminal_summary


    @pytest.mark.trylast
    def pytest_configure(config):
        plugin_manager = config.pluginmanager
        for hookimpl in plugin_manager.hook.pytest_terminal_summary._nonwrappers:
            if hookimpl.plugin_name in fold_plugins.keys():
                hookimpl.function = terminal_summary_wrapper(hookimpl.function,
                                                             hookimpl.plugin_name)