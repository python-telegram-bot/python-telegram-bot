Python Telegram Bot

A Python wrapper around the Telegram Bot API.

By `Leandro Toledo <leandrotoledodesouza@gmail.com>`_

.. image:: https://travis-ci.org/leandrotoledo/python-telegram-bot.svg?branch=master
    :target: https://travis-ci.org/leandrotoledo/python-telegram-bot
    :alt: Travis CI Status

============
Introduction
============

This library provides a pure Python interface for the `Telegram Bot API <https://core.telegram.org/bots/api>`_. It works with Python versions from 2.6+. Python 3 support is under development.

==========
Installing
==========

You can install python-telegram-bot using::

    $ pip install python-telegram-bot

================
Getting the code
================

The code is hosted at https://github.com/leandrotoledo/python-telegram-bot

Check out the latest development version anonymously with::

    $ git clone https://github.com/leandrotoledo/python-telegram-bot
    $ cd python-telegram-bot

Setup a virtual environment and install dependencies:

	$ make env

Activate the virtual environment created:

	$ source env/bin/activate

Run tests:

	$ make test

To see other options available, run:

	$ make help

=============
Documentation
=============

View the last release API documentation at: https://core.telegram.org/bots/api

---
API
---

The API is exposed via the ``telegram.Bot`` class.

To generate an Access Token you have to talk to `BotFather <https://telegram.me/botfather>`_ and follow a few simple steps (described `here <https://core.telegram.org/bots#botfather>`_).

For full details see the `Bots: An introduction for developers <https://core.telegram.org/bots>`_.

To create an instance of the ``telegram.Bot``::

    >>> import telegram
    >>> bot = telegram.Bot(token='token')

To see if your credentials are successful::

    >>> print bot.getMe()
    {"first_name": "Toledo's Palace Bot", "username": "ToledosPalaceBot"}

**NOTE**: much more than the small sample given here will print

Bots can't initiate conversations with users. A user must either add them to a group or send them a message first. People can use ``telegram.me/<bot_username>`` links or username search to find your bot.

To fetch text messages sent to your Bot::

    >>> updates = bot.getUpdates()
    >>> print [u.message.text for u in updates]

To fetch images sent to your Bot::

    >>> updates = bot.getUpdates()
    >>> print [u.message.photo for u in updates if u.message.photo]

To reply messages you'll always need the chat_id::

    >>> chat_id = bot.getUpdates()[-1].message.chat_id

To post a text message::

    >>> bot.sendMessage(chat_id=chat_id, text="I'm sorry Dave I'm afraid I can't do that.")

To post an Emoji (special thanks to `Tim Whitlock <http://apps.timwhitlock.info/emoji/tables/unicode>`_)::

    >>> bot.sendMessage(chat_id=chat_id, text=telegram.Emoji.PILE_OF_POO)

To post a audio file::

    >>> bot.sendAudio(chat_id=chat_id, audio=open('tests/telegram.ogg', 'rb'))

To tell the user that something is happening on bot's side::

    >>> bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

To create `Custom Keyboards <https://core.telegram.org/bots#keyboards>_`::

    >>> custom_keyboard = [[ telegram.Emoji.THUMBS_UP_SIGN, telegram.Emoji.THUMBS_DOWN_SIGN ]]
    >>> reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    >>> bot.sendMessage(chat_id=chat_id, text="Stay here, I'll be back.", reply_markup=reply_markup)

To hide `Custom Keyboards <https://core.telegram.org/bots#keyboards>_`::

    >>> reply_markup = telegram.ReplyKeyboardHide()
    >>> bot.sendMessage(chat_id=chat_id, text="I'm back.", reply_markup=reply_markup)

There are many more API methods, to read the full API documentation::

    $ pydoc telegram.Bot

----
TODO
----

Patches and bug reports are `welcome <https://github.com/leandrotoledo/python-telegram-bot/issues/new>`_, just please keep the style consistent with the original source.

Add more example scripts.

Add `custom keyboards <https://core.telegram.org/bots#keyboards>`_ methods.

Add commands handler.
