import asyncio

import pytest

from telegram.ext import ApplicationBuilder, Updater
from telegram.ext.filters import MessageFilter, UpdateFilter
from tests.auxil.constants import PRIVATE_KEY
from tests.auxil.envvars import TEST_WITH_OPT_DEPS
from tests.auxil.monkeypatch import return_true
from tests.auxil.networking import OfflineRequest
from tests.auxil.pytest_classes import PytestApplication, PytestBot, make_bot

# This module overrides the bot fixtures defined in the global conftest.py to use the offline bot.
# We don't want the tests on telegram.ext to depend on the network, so we use the offline bot
# instead.


@pytest.fixture(scope="session")
async def bot(bot_info, offline_bot):
    return offline_bot


@pytest.fixture
async def app(bot_info, monkeypatch):
    # We build a new bot each time so that we use `app` in a context manager without problems
    application = (
        ApplicationBuilder()
        .bot(make_bot(bot_info, offline=True))
        .application_class(PytestApplication)
        .build()
    )
    monkeypatch.setattr(application.bot, "delete_webhook", return_true)
    monkeypatch.setattr(application.bot, "set_webhook", return_true)
    yield application
    if application.running:
        await application.stop()
        await application.shutdown()


@pytest.fixture
async def updater(bot_info, monkeypatch):
    # We build a new bot each time so that we use `updater` in a context manager without problems
    up = Updater(bot=make_bot(bot_info, offline=True), update_queue=asyncio.Queue())
    monkeypatch.setattr(up.bot, "delete_webhook", return_true)
    monkeypatch.setattr(up.bot, "set_webhook", return_true)
    yield up
    if up.running:
        await up.stop()
        await up.shutdown()


@pytest.fixture
def one_time_bot(bot_info):
    """A function scoped bot since the session bot would shutdown when `async with app` finishes"""
    return make_bot(bot_info, offline=True)


@pytest.fixture(scope="session")
async def cdc_bot(bot_info):
    """Makes an ExtBot instance with the given bot_info that uses arbitrary callback_data"""
    async with make_bot(bot_info, arbitrary_callback_data=True, offline=True) as _bot:
        yield _bot


@pytest.fixture(scope="session")
async def raw_bot(bot_info):
    """Makes an regular Bot instance with the given bot_info"""
    async with PytestBot(
        bot_info["token"],
        private_key=PRIVATE_KEY if TEST_WITH_OPT_DEPS else None,
        request=OfflineRequest(),
        get_updates_request=OfflineRequest(),
    ) as _bot:
        yield _bot


@pytest.fixture
async def one_time_raw_bot(bot_info):
    """Makes an regular Bot instance with the given bot_info"""
    return PytestBot(
        bot_info["token"],
        private_key=PRIVATE_KEY if TEST_WITH_OPT_DEPS else None,
        request=OfflineRequest(),
        get_updates_request=OfflineRequest(),
    )


@pytest.fixture(
    scope="class",
    params=[{"class": MessageFilter}, {"class": UpdateFilter}],
    ids=["MessageFilter", "UpdateFilter"],
)
def mock_filter(request):
    class MockFilter(request.param["class"]):
        def __init__(self):
            super().__init__()
            self.tested = False

        def filter(self, _):
            self.tested = True

    return MockFilter()
