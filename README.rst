Python Telegram Bot

A Python wrapper around the Telegram Bot API.

By `Leandro Toledo <leandrotoledodesouza@gmail.com>`_

.. image:: https://travis-ci.org/leandrotoledo/python-telegram-bot.svg?branch=master
    :target: https://travis-ci.org/leandrotoledo/python-telegram-bot
    :alt: Travis CI Status

.. image:: https://codeclimate.com/github/leandrotoledo/python-telegram-bot/badges/gpa.svg
   :target: https://codeclimate.com/github/leandrotoledo/python-telegram-bot
   :alt: Code Climate

=================
Table of contents
=================

- `Introduction`_

- `Status`_

  1. `Telegram API support`_
  
  2. `Python Version support`_

- `Installing`_

- `Getting the code`_

- `Documentation`_

  1. `API`_

  2. `Examples`_

- `Contact`_

- `TODO`_

===============
_`Introduction`
===============

This library provides a pure Python interface for the `Telegram Bot API <https://core.telegram.org/bots/api>`_. It works with Python versions from 2.6+. It also works with `Google App Engine <https://cloud.google.com/appengine>`_.

=========
_`Status`
=========

-----------------------
_`Telegram API support`
-----------------------

========================= ============
Telegram Bot API Method   *Supported?*
========================= ============
getMe                     Yes
sendMessage               Yes
forwardMessage            Yes
sendPhoto                 Yes
sendAudio                 Yes
sendDocument              Yes
sendSticker               Yes
sendVideo                 Yes
sendLocation              Yes
sendChatAction            Yes
getUpdates                Yes
getUserProfilePhotos      Yes
setWebhook                Yes
========================= ============

-------------------------
_`Python Version support`
-------------------------

============== ============
Python Version *Supported?*
============== ============
2.6            Yes
2.7            Yes
3.3            Yes
3.4            Yes
============== ============

=============
_`Installing`
=============

You can install python-telegram-bot using::

    $ pip install python-telegram-bot
    
Or upgrade to the latest version::

    $ pip install python-telegram-bot --upgrade

===================
_`Getting the code`
===================

The code is hosted at https://github.com/leandrotoledo/python-telegram-bot

Check out the latest development version anonymously with::

    $ git clone https://github.com/leandrotoledo/python-telegram-bot
    $ cd python-telegram-bot

Run tests:

    $ make test

To see other options available, run:

    $ make help

================
_`Documentation`
================

View the last release API documentation at: https://core.telegram.org/bots/api

------
_`API`
------

The API is exposed via the ``telegram.Bot`` class.

To generate an Access Token you have to talk to `BotFather <https://telegram.me/botfather>`_ and follow a few simple steps (described `here <https://core.telegram.org/bots#botfather>`_).

For full details see the `Bots: An introduction for developers <https://core.telegram.org/bots>`_.

To create an instance of the ``telegram.Bot``::

    >>> import telegram
    >>> bot = telegram.Bot(token='token')

To see if your credentials are successful::

    >>> print bot.getMe()
    {"first_name": "Toledo's Palace Bot", "username": "ToledosPalaceBot"}

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

To post an image file via URL (right now only sendPhoto supports this)::

    >>> bot.sendPhoto(chat_id=chat_id, photo='https://telegram.org/img/t_logo.png')

To post an audio file::

    >>> bot.sendAudio(chat_id=chat_id, audio=open('tests/telegram.ogg', 'rb'))

To tell the user that something is happening on bot's side::

    >>> bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

To create `Custom Keyboards <https://core.telegram.org/bots#keyboards>`_::

    >>> custom_keyboard = [[ telegram.Emoji.THUMBS_UP_SIGN, telegram.Emoji.THUMBS_DOWN_SIGN ]]
    >>> reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    >>> bot.sendMessage(chat_id=chat_id, text="Stay here, I'll be back.", reply_markup=reply_markup)

To hide `Custom Keyboards <https://core.telegram.org/bots#keyboards>`_::

    >>> reply_markup = telegram.ReplyKeyboardHide()
    >>> bot.sendMessage(chat_id=chat_id, text="I'm back.", reply_markup=reply_markup)

There are many more API methods, to read the full API documentation::

    $ pydoc telegram.Bot

To get a verbose mode to debug::
    
    >>> telegram.Bot('token', debug=True)
    
-----------
_`Examples`
-----------

Here follows some examples to help you to get your own Bot up to speed:

- `echobot <https://github.com/leandrotoledo/python-telegram-bot/blob/master/examples/echobot.py>`_ replies back messages.

- `roboed <https://github.com/leandrotoledo/python-telegram-bot/blob/master/examples/roboed.py>`_ talks to `Robô Ed <http://www.ed.conpet.gov.br/br/converse.php>`_.

- `DevOps Reaction Bot <https://github.com/leandrotoledo/gae-devops-reaction-telegram-bot>`_ sends latest or random posts from `DevOps Reaction <http://devopsreactions.tumblr.com/>`_. Running on `Google App Engine <https://cloud.google.com/appengine>`_ (billing has to be enabled for fully Socket API support).

==========
_`Contact`
==========

Feel free to join to our `Telegram group <https://telegram.me/joinchat/00b9c0f802509b949c1563d56eb053b0>`_.

=======
_`TODO`
=======

Patches and bug reports are `welcome <https://github.com/leandrotoledo/python-telegram-bot/issues/new>`_, just please keep the style consistent with the original source.

- Add commands handler.
