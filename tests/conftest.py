#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import datetime
import inspect
import os
import re
from collections import defaultdict
from queue import Queue
from threading import Thread, Event
from time import sleep
from typing import Callable, List, Dict, Any

import pytest
import pytz

from telegram import (
    Bot,
    Message,
    User,
    Chat,
    MessageEntity,
    Update,
    InlineQuery,
    CallbackQuery,
    ShippingQuery,
    PreCheckoutQuery,
    ChosenInlineResult,
)
from telegram.ext import Dispatcher, JobQueue, Updater, MessageFilter, Defaults, UpdateFilter
from telegram.error import BadRequest
from tests.bots import get_bot

GITHUB_ACTION = os.getenv('GITHUB_ACTION', False)

if GITHUB_ACTION:
    pytest_plugins = ['tests.plugin_github_group']

# THIS KEY IS OBVIOUSLY COMPROMISED
# DO NOT USE IN PRODUCTION!
PRIVATE_KEY = b"-----BEGIN RSA PRIVATE KEY-----\r\nMIIEowIBAAKCAQEA0AvEbNaOnfIL3GjB8VI4M5IaWe+GcK8eSPHkLkXREIsaddum\r\nwPBm/+w8lFYdnY+O06OEJrsaDtwGdU//8cbGJ/H/9cJH3dh0tNbfszP7nTrQD+88\r\nydlcYHzClaG8G+oTe9uEZSVdDXj5IUqR0y6rDXXb9tC9l+oSz+ShYg6+C4grAb3E\r\nSTv5khZ9Zsi/JEPWStqNdpoNuRh7qEYc3t4B/a5BH7bsQENyJSc8AWrfv+drPAEe\r\njQ8xm1ygzWvJp8yZPwOIYuL+obtANcoVT2G2150Wy6qLC0bD88Bm40GqLbSazueC\r\nRHZRug0B9rMUKvKc4FhG4AlNzBCaKgIcCWEqKwIDAQABAoIBACcIjin9d3Sa3S7V\r\nWM32JyVF3DvTfN3XfU8iUzV7U+ZOswA53eeFM04A/Ly4C4ZsUNfUbg72O8Vd8rg/\r\n8j1ilfsYpHVvphwxaHQlfIMa1bKCPlc/A6C7b2GLBtccKTbzjARJA2YWxIaqk9Nz\r\nMjj1IJK98i80qt29xRnMQ5sqOO3gn2SxTErvNchtBiwOH8NirqERXig8VCY6fr3n\r\nz7ZImPU3G/4qpD0+9ULrt9x/VkjqVvNdK1l7CyAuve3D7ha3jPMfVHFtVH5gqbyp\r\nKotyIHAyD+Ex3FQ1JV+H7DkP0cPctQiss7OiO9Zd9C1G2OrfQz9el7ewAPqOmZtC\r\nKjB3hUECgYEA/4MfKa1cvaCqzd3yUprp1JhvssVkhM1HyucIxB5xmBcVLX2/Kdhn\r\nhiDApZXARK0O9IRpFF6QVeMEX7TzFwB6dfkyIePsGxputA5SPbtBlHOvjZa8omMl\r\nEYfNa8x/mJkvSEpzvkWPascuHJWv1cEypqphu/70DxubWB5UKo/8o6cCgYEA0HFy\r\ncgwPMB//nltHGrmaQZPFT7/Qgl9ErZT3G9S8teWY4o4CXnkdU75tBoKAaJnpSfX3\r\nq8VuRerF45AFhqCKhlG4l51oW7TUH50qE3GM+4ivaH5YZB3biwQ9Wqw+QyNLAh/Q\r\nnS4/Wwb8qC9QuyEgcCju5lsCaPEXZiZqtPVxZd0CgYEAshBG31yZjO0zG1TZUwfy\r\nfN3euc8mRgZpSdXIHiS5NSyg7Zr8ZcUSID8jAkJiQ3n3OiAsuq1MGQ6kNa582kLT\r\nFPQdI9Ea8ahyDbkNR0gAY9xbM2kg/Gnro1PorH9PTKE0ekSodKk1UUyNrg4DBAwn\r\nqE6E3ebHXt/2WmqIbUD653ECgYBQCC8EAQNX3AFegPd1GGxU33Lz4tchJ4kMCNU0\r\nN2NZh9VCr3nTYjdTbxsXU8YP44CCKFG2/zAO4kymyiaFAWEOn5P7irGF/JExrjt4\r\nibGy5lFLEq/HiPtBjhgsl1O0nXlwUFzd7OLghXc+8CPUJaz5w42unqT3PBJa40c3\r\nQcIPdQKBgBnSb7BcDAAQ/Qx9juo/RKpvhyeqlnp0GzPSQjvtWi9dQRIu9Pe7luHc\r\nm1Img1EO1OyE3dis/rLaDsAa2AKu1Yx6h85EmNjavBqP9wqmFa0NIQQH8fvzKY3/\r\nP8IHY6009aoamLqYaexvrkHVq7fFKiI6k8myMJ6qblVNFv14+KXU\r\n-----END RSA PRIVATE KEY-----"  # noqa: E501


@pytest.fixture(scope='session')
def bot_info():
    return get_bot()


@pytest.fixture(scope='session')
def bot(bot_info):
    return make_bot(bot_info)


DEFAULT_BOTS = {}


@pytest.fixture(scope='function')
def default_bot(request, bot_info):
    param = request.param if hasattr(request, 'param') else {}

    defaults = Defaults(**param)
    default_bot = DEFAULT_BOTS.get(defaults)
    if default_bot:
        return default_bot
    else:
        default_bot = make_bot(bot_info, **{'defaults': defaults})
        DEFAULT_BOTS[defaults] = default_bot
        return default_bot


@pytest.fixture(scope='function')
def tz_bot(timezone, bot_info):
    defaults = Defaults(tzinfo=timezone)
    default_bot = DEFAULT_BOTS.get(defaults)
    if default_bot:
        return default_bot
    else:
        default_bot = make_bot(bot_info, **{'defaults': defaults})
        DEFAULT_BOTS[defaults] = default_bot
        return default_bot


@pytest.fixture(scope='session')
def chat_id(bot_info):
    return bot_info['chat_id']


@pytest.fixture(scope='session')
def super_group_id(bot_info):
    return bot_info['super_group_id']


@pytest.fixture(scope='session')
def channel_id(bot_info):
    return bot_info['channel_id']


@pytest.fixture(scope='session')
def provider_token(bot_info):
    return bot_info['payment_provider_token']


def create_dp(bot):
    # Dispatcher is heavy to init (due to many threads and such) so we have a single session
    # scoped one here, but before each test, reset it (dp fixture below)
    dispatcher = Dispatcher(bot, Queue(), job_queue=JobQueue(), workers=2, use_context=False)
    dispatcher.job_queue.set_dispatcher(dispatcher)
    thr = Thread(target=dispatcher.start)
    thr.start()
    sleep(2)
    yield dispatcher
    sleep(1)
    if dispatcher.running:
        dispatcher.stop()
    thr.join()


@pytest.fixture(scope='session')
def _dp(bot):
    for dp in create_dp(bot):
        yield dp


@pytest.fixture(scope='function')
def dp(_dp):
    # Reset the dispatcher first
    while not _dp.update_queue.empty():
        _dp.update_queue.get(False)
    _dp.chat_data = defaultdict(dict)
    _dp.user_data = defaultdict(dict)
    _dp.bot_data = {}
    _dp.persistence = None
    _dp.handlers = {}
    _dp.groups = []
    _dp.error_handlers = {}
    _dp.__stop_event = Event()
    _dp.__exception_event = Event()
    _dp.__async_queue = Queue()
    _dp.__async_threads = set()
    _dp.persistence = None
    _dp.use_context = False
    if _dp._Dispatcher__singleton_semaphore.acquire(blocking=0):
        Dispatcher._set_singleton(_dp)
    yield _dp
    Dispatcher._Dispatcher__singleton_semaphore.release()


@pytest.fixture(scope='function')
def cdp(dp):
    dp.use_context = True
    yield dp
    dp.use_context = False


@pytest.fixture(scope='function')
def updater(bot):
    up = Updater(bot=bot, workers=2, use_context=False)
    yield up
    if up.running:
        up.stop()


@pytest.fixture(scope='function')
def thumb_file():
    f = open(u'tests/data/thumb.jpg', 'rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
def class_thumb_file():
    f = open(u'tests/data/thumb.jpg', 'rb')
    yield f
    f.close()


def pytest_configure(config):
    config.addinivalue_line('filterwarnings', 'ignore::ResourceWarning')
    # TODO: Write so good code that we don't need to ignore ResourceWarnings anymore


def make_bot(bot_info, **kwargs):
    return Bot(bot_info['token'], private_key=PRIVATE_KEY, **kwargs)


CMD_PATTERN = re.compile(r'/[\da-z_]{1,32}(?:@\w{1,32})?')
DATE = datetime.datetime.now()


def make_message(text, **kwargs):
    """
    Testing utility factory to create a fake ``telegram.Message`` with
    reasonable defaults for mimicking a real message.
    :param text: (str) message text
    :return: a (fake) ``telegram.Message``
    """
    return Message(
        message_id=1,
        from_user=kwargs.pop('user', User(id=1, first_name='', is_bot=False)),
        date=kwargs.pop('date', DATE),
        chat=kwargs.pop('chat', Chat(id=1, type='')),
        text=text,
        bot=kwargs.pop('bot', make_bot(get_bot())),
        **kwargs,
    )


def make_command_message(text, **kwargs):
    """
    Testing utility factory to create a message containing a single telegram
    command.
    Mimics the Telegram API in that it identifies commands within the message
    and tags the returned ``Message`` object with the appropriate ``MessageEntity``
    tag (but it does this only for commands).

    :param text: (str) message text containing (or not) the command
    :return: a (fake) ``telegram.Message`` containing only the command
    """

    match = re.search(CMD_PATTERN, text)
    entities = (
        [
            MessageEntity(
                type=MessageEntity.BOT_COMMAND, offset=match.start(0), length=len(match.group(0))
            )
        ]
        if match
        else []
    )

    return make_message(text, entities=entities, **kwargs)


def make_message_update(message, message_factory=make_message, edited=False, **kwargs):
    """
    Testing utility factory to create an update from a message, as either a
    ``telegram.Message`` or a string. In the latter case ``message_factory``
    is used to convert ``message`` to a ``telegram.Message``.
    :param message: either a ``telegram.Message`` or a string with the message text
    :param message_factory: function to convert the message text into a ``telegram.Message``
    :param edited: whether the message should be stored as ``edited_message`` (vs. ``message``)
    :return: ``telegram.Update`` with the given message
    """
    if not isinstance(message, Message):
        message = message_factory(message, **kwargs)
    update_kwargs = {'message' if not edited else 'edited_message': message}
    return Update(0, **update_kwargs)


def make_command_update(message, edited=False, **kwargs):
    """
    Testing utility factory to create an update from a message that potentially
    contains a command. See ``make_command_message`` for more details.
    :param message: message potentially containing a command
    :param edited: whether the message should be stored as ``edited_message`` (vs. ``message``)
    :return: ``telegram.Update`` with the given message
    """
    return make_message_update(message, make_command_message, edited, **kwargs)


@pytest.fixture(
    scope='class',
    params=[{'class': MessageFilter}, {'class': UpdateFilter}],
    ids=['MessageFilter', 'UpdateFilter'],
)
def mock_filter(request):
    class MockFilter(request.param['class']):
        def __init__(self):
            self.tested = False

        def filter(self, _):
            self.tested = True

    return MockFilter()


def get_false_update_fixture_decorator_params():
    message = Message(1, DATE, Chat(1, ''), from_user=User(1, '', False), text='test')
    params = [
        {'callback_query': CallbackQuery(1, User(1, '', False), 'chat', message=message)},
        {'channel_post': message},
        {'edited_channel_post': message},
        {'inline_query': InlineQuery(1, User(1, '', False), '', '')},
        {'chosen_inline_result': ChosenInlineResult('id', User(1, '', False), '')},
        {'shipping_query': ShippingQuery('id', User(1, '', False), '', None)},
        {'pre_checkout_query': PreCheckoutQuery('id', User(1, '', False), '', 0, '')},
        {'callback_query': CallbackQuery(1, User(1, '', False), 'chat')},
    ]
    ids = tuple(key for kwargs in params for key in kwargs)
    return {'params': params, 'ids': ids}


@pytest.fixture(scope='function', **get_false_update_fixture_decorator_params())
def false_update(request):
    return Update(update_id=1, **request.param)


@pytest.fixture(params=['Europe/Berlin', 'Asia/Singapore', 'UTC'])
def tzinfo(request):
    return pytz.timezone(request.param)


@pytest.fixture()
def timezone(tzinfo):
    return tzinfo


def expect_bad_request(func, message, reason):
    """
    Wrapper for testing bot functions expected to result in an :class:`telegram.error.BadRequest`.
    Makes it XFAIL, if the specified error message is present.

    Args:
        func: The callable to be executed.
        message: The expected message of the bad request error. If another message is present,
            the error will be reraised.
        reason: Explanation for the XFAIL.

    Returns:
        On success, returns the return value of :attr:`func`
    """
    try:
        return func()
    except BadRequest as e:
        if message in str(e):
            pytest.xfail(f'{reason}. {e}')
        else:
            raise e


def check_shortcut_signature(
    shortcut: Callable,
    bot_method: Callable,
    shortcut_kwargs: List[str],
    additional_kwargs: List[str],
) -> bool:
    """
    Checks that the signature of a shortcut matches the signature of the underlying bot method.

    Args:
        shortcut: The shortcut, e.g. :meth:`telegram.Message.reply_text`
        bot_method: The bot method, e.g. :meth:`telegram.Bot.send_message`
        shortcut_kwargs: The kwargs passed by the shortcut directly, e.g. ``chat_id``
        additional_kwargs: Additional kwargs of the shortcut that the bot method doesn't have, e.g.
            ``quote``.

    Returns:
        :obj:`bool`: Whether or not the signature matches.
    """
    shortcut_arg_spec = inspect.getfullargspec(shortcut)
    effective_shortcut_args = set(shortcut_arg_spec.args).difference(additional_kwargs)
    effective_shortcut_args.discard('self')

    bot_arg_spec = inspect.getfullargspec(bot_method)
    expected_args = set(bot_arg_spec.args).difference(shortcut_kwargs)
    expected_args.discard('self')

    args_check = expected_args == effective_shortcut_args

    # TODO: Also check annotation of return type. Would currently be a hassle b/c typing doesn't
    # resolve `ForwardRef('Type')` to `Type`. For now we rely on MyPy, which probably allows the
    # shortcuts to return more specific types than the bot method, but it's only annotations after
    # all
    annotation_check = True
    for kwarg in effective_shortcut_args:
        if bot_arg_spec.annotations[kwarg] != shortcut_arg_spec.annotations[kwarg]:
            if isinstance(bot_arg_spec.annotations[kwarg], type):
                if bot_arg_spec.annotations[kwarg].__name__ != str(
                    shortcut_arg_spec.annotations[kwarg]
                ):
                    print(
                        f'Expected {bot_arg_spec.annotations[kwarg]}, but '
                        f'got {shortcut_arg_spec.annotations[kwarg]}'
                    )
                    annotation_check = False
                    break
            else:
                print(
                    f'Expected {bot_arg_spec.annotations[kwarg]}, but '
                    f'got {shortcut_arg_spec.annotations[kwarg]}'
                )
                annotation_check = False
                break

    bot_method_signature = inspect.signature(bot_method)
    shortcut_signature = inspect.signature(shortcut)
    default_check = all(
        shortcut_signature.parameters[arg].default == bot_method_signature.parameters[arg].default
        for arg in expected_args
    )

    return args_check and annotation_check and default_check


def check_shortcut_call(
    kwargs: Dict[str, Any],
    bot_method: Callable,
) -> bool:
    """
    Checks that a shortcut passes all the existing arguments to the underlying bot method. Use as::

        send_message = message.bot.send_message

        def make_assertion(*_, **kwargs):
            return check_shortcut_call(send_message, kwargs)

        monkeypatch.setattr(message.bot, 'send_message', make_assertion)
        assert message.reply_text('foobar')


    Args:
        kwargs: The kwargs passed to the bot method by the shortcut
        bot_method: The bot method, e.g. :meth:`telegram.Bot.send_message`

    Returns:
        :obj:`bool`
    """
    bot_arg_spec = inspect.getfullargspec(bot_method)
    expected_args = set(bot_arg_spec.args).difference(['self'])

    return expected_args == set(kwargs.keys())
