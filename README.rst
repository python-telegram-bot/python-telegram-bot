Python Telegram Bot

A Python wrapper around the Telegram Bot API.

By `Leandro Toledo <leandrotoledodesouza@gmail.com>`_

.. image:: https://travis-ci.org/leandrotoledo/python-telegram.svg?branch=master
    :target: https://travis-ci.org/leandrotoledo/python-telegram
    :alt: Travis CI Status

============
Introduction
============

This library provides a pure Python interface for the `Telegram Bot API <https://core.telegram.org/bots/api>`_. It works with Python versions from 2.6+. Python 3 support is under development.

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

The API is exposed via the ``telegram.Bot`` class::

    >>> import telegram
    >>> bot = telegram.Bot(token='token')

To see if your credentials are successful::

    >>> print bot.getMe()
    {"first_name": "Toledo's Palace Bot", "username": "ToledosPalaceBot"}

**NOTE**: much more than the small sample given here will print
