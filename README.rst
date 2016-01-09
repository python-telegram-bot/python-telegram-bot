.. image:: https://github.com/python-telegram-bot/logos/blob/master/logo-text/png/ptb-logo-text_768.png?raw=true
   :align: center
   :target: https://github.com/python-telegram-bot/logos
   :alt: python-telegram-bot Logo

A Python wrapper around the Telegram Bot API.

*Stay tuned for library updates and new releases on our* `Telegram Channel <http://telegram.me/pythontelegrambotchannel>`_.

.. image:: https://img.shields.io/pypi/v/python-telegram-bot.svg
   :target: https://pypi.python.org/pypi/python-telegram-bot
   :alt: PyPi Package Version

.. image:: https://img.shields.io/pypi/dm/python-telegram-bot.svg
   :target: https://pypi.python.org/pypi/python-telegram-bot
   :alt: PyPi Package Monthly Download

.. image:: https://readthedocs.org/projects/python-telegram-bot/badge/?version=latest
   :target: https://readthedocs.org/projects/python-telegram-bot/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/l/python-telegram-bot.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0.html
   :alt: LGPLv3 License

.. image:: https://travis-ci.org/python-telegram-bot/python-telegram-bot.svg?branch=master
   :target: https://travis-ci.org/python-telegram-bot/python-telegram-bot
   :alt: Travis CI Status

.. image:: https://codeclimate.com/github/python-telegram-bot/python-telegram-bot/badges/gpa.svg
   :target: https://codeclimate.com/github/python-telegram-bot/python-telegram-bot
   :alt: Code Climate

.. image:: https://coveralls.io/repos/python-telegram-bot/python-telegram-bot/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/python-telegram-bot/python-telegram-bot?branch=master
   :alt: Coveralls
   
.. image:: https://img.shields.io/badge/Telegram-Group-blue.svg
   :target: https://telegram.me/joinchat/ALnA-AJQm5R7Km9hdCgyng
   :alt: Telegram Group

=================
Table of contents
=================

- `Introduction`_

- `Status`_

  1. `Telegram API support`_

  2. `Python Version support`_

- `Installing`_

- `Getting the code`_

- `Getting started`_

  1. `The Updater class`_
  
  2. `API`_
  
  3. `JobQueue`_

  4. `Logging`_

  5. `Examples`_

  6. `Documentation`_

- `License`_

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
sendVoice                 Yes
sendLocation              Yes
sendChatAction            Yes
getUpdates                Yes
getUserProfilePhotos      Yes
getFile                   Yes
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
PyPy           Yes
PyPy3          Yes
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

The code is hosted at https://github.com/python-telegram-bot/python-telegram-bot

Check out the latest development version anonymously with::

    $ git clone https://github.com/python-telegram-bot/python-telegram-bot
    $ cd python-telegram-bot

Install dependencies:

    $ pip install -r requirements.txt

Run tests:

    $ make test

To see other options available, run:

    $ make help

==================
_`Getting started`
==================

View the last release API documentation at: https://core.telegram.org/bots/api

--------------------
_`The Updater class`
--------------------

The ``Updater`` class is the new way to create bots with ``python-telegram-bot``. It provides an easy-to-use interface to the ``telegram.Bot`` by caring about getting new updates from telegram and forwarding them to the ``Dispatcher`` class. We can register handler functions in the ``Dispatcher`` to make our bot react to Telegram commands, messages and even arbitrary updates.

As with the old method, we'll need an Access Token. To generate an Access Token, we have to talk to `BotFather <https://telegram.me/botfather>`_ and follow a few simple steps (described `here <https://core.telegram.org/bots#botfather>`_).

First, we create an ``Updater`` object::

   >>> from telegram import Updater
   >>> updater = Updater(token='token')

For quicker access to the ``Dispatcher`` used by our ``Updater``, we can introduce it locally::

   >>> dispatcher = updater.dispatcher

Now, we need to define a function that should process a specific type of update::

   >>> def start(bot, update):
   ...   bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

We want this function to be called on a Telegram message that contains the ``/start`` command, so we need to register it in the dispatcher::

   >>> dispatcher.addTelegramCommandHandler('start', start)
   
The last step is to tell the ``Updater`` to start working::

   >>> updater.start_polling()

Our bot is now up and running (go ahead and try it)! It's not doing anything yet, besides answering to the ``/start`` command. Let's add another handler function and register it::

   >>> def echo(bot, update):
   ...   bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)
   ...
   >>> dispatcher.addTelegramMessageHandler(echo)

Our bot should now reply to all messages that are not a command with a message that has the same content.

People might try to send commands to the bot that it doesn't understand, so we should get that covered as well::

   >>> def unknown(bot, update):
   ...   bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")
   ...
   >>> dispatcher.addUnknownTelegramCommandHandler(unknown)

Let's add some functionality to our bot. We want to add the ``/caps`` command, that will take some text as parameter and return it in all caps. We can get the arguments that were passed to the command in the handler function simply by adding it to the parameter list::

   >>> def caps(bot, update, args):
   ...   text_caps = ' '.join(args).upper()
   ...   bot.sendMessage(chat_id=update.message.chat_id, text=text_caps)
   ... 
   >>> dispatcher.addTelegramCommandHandler('caps', caps)

Now it's time to stop the bot::

   >>> updater.stop()

Check out more examples in the `examples folder <https://github.com/python-telegram-bot/python-telegram-bot/tree/master/examples>`_!

------
_`API`
------

Note: Using the ``Bot`` class directly is the 'old' method, but some of this is still important information, even if you're using the ``Updater`` class!

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

To post a text message with markdown::

    >>> bot.sendMessage(chat_id=chat_id, text="*bold* _italic_ [link](http://google.com).", parse_mode=telegram.ParseMode.MARKDOWN)

To post an Emoji (special thanks to `Tim Whitlock <http://apps.timwhitlock.info/emoji/tables/unicode>`_)::

    >>> bot.sendMessage(chat_id=chat_id, text=telegram.Emoji.PILE_OF_POO)

To post an image file via URL (right now only sendPhoto supports this)::

    >>> bot.sendPhoto(chat_id=chat_id, photo='https://telegram.org/img/t_logo.png')

To post a voice file::

    >>> bot.sendVoice(chat_id=chat_id, voice=open('tests/telegram.ogg', 'rb'))

To tell the user that something is happening on bot's side::

    >>> bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

To create `Custom Keyboards <https://core.telegram.org/bots#keyboards>`_::

    >>> custom_keyboard = [[ telegram.Emoji.THUMBS_UP_SIGN, telegram.Emoji.THUMBS_DOWN_SIGN ]]
    >>> reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    >>> bot.sendMessage(chat_id=chat_id, text="Stay here, I'll be back.", reply_markup=reply_markup)

To hide `Custom Keyboards <https://core.telegram.org/bots#keyboards>`_::

    >>> reply_markup = telegram.ReplyKeyboardHide()
    >>> bot.sendMessage(chat_id=chat_id, text="I'm back.", reply_markup=reply_markup)

To download a file (you will need its file_id)::

    >>> file_id = message.voice.file_id
    >>> newFile = bot.getFile(file_id)
    >>> newFile.download('voice.ogg')

There are many more API methods, to read the full API documentation::

    $ pydoc telegram.Bot

-----------
_`JobQueue`
-----------

The ``JobQueue`` allows you to perform tasks with a delay or even periodically. The ``Updater`` will create one for you::

    >>> from telegram import Updater
    >>> u = Updater('TOKEN')
    >>> j = u.job_queue

The job queue uses functions for tasks, so we define one and add it to the queue. Usually, when the first job is added to the queue, it wil start automatically. We can prevent this by setting ``prevent_autostart=True``::

    >>> def job1(bot):
    ...     bot.sendMessage(chat_id='@examplechannel', text='One message every minute')
    >>> j.put(job1, 60, next_t=0, prevent_autostart=True)

You can also have a job that will not be executed repeatedly::

    >>> def job2(bot):
    ...     bot.sendMessage(chat_id='@examplechannel', text='A single message with 30s delay')
    >>> j.put(job2, 30, repeat=False)

Now, because we didn't prevent the auto start this time, the queue will start ticking. It runs in a seperate thread, so it is non-blocking. When we stop the Updater, the related queue will be stopped as well::

    >>> u.stop()

We can also stop the job queue by itself::

    >>> j.stop()

----------
_`Logging`
----------

You can get logs in your main application by calling `logging` and setting the log level you want::

    >>> import logging
    >>> logger = logging.getLogger()
    >>> logger.setLevel(logging.INFO)

If you want DEBUG logs instead::

    >>> logger.setLevel(logging.DEBUG)

-----------
_`Examples`
-----------

Here follows some examples to help you to get your own Bot up to speed:

- `echobot2 <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py>`_ replies back messages.

- `clibot <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/clibot.py>`_ has a command line interface.

- `timerbot <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py>`_ uses the ``JobQueue`` to send timed messages.

- `Welcome Bot <https://github.com/jh0ker/welcomebot>`_ greets everyone who joins a group chat.

Legacy examples (pre-3.0):

- `echobot <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/legacy/echobot.py>`_ replies back messages.

- `roboed <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/legacy/roboed.py>`_ talks to `Robô Ed <http://www.ed.conpet.gov.br/br/converse.php>`_.

- `Simple-Echo-Telegram-Bot <https://github.com/sooyhwang/Simple-Echo-Telegram-Bot>`_ simple Python Telegram bot that echoes your input with Flask microframework, setWebhook method, and Google App Engine (optional) - by @sooyhwang.

- `DevOps Reaction Bot <https://github.com/leandrotoledo/gae-devops-reaction-telegram-bot>`_ sends latest or random posts from `DevOps Reaction <http://devopsreactions.tumblr.com/>`_. Running on `Google App Engine <https://cloud.google.com/appengine>`_ (billing has to be enabled for fully Socket API support).

Other notable examples:

- `TwitterForwarderBot <https://github.com/franciscod/telegram-twitter-forwarder-bot>`_ forwards you tweets from people that you have subscribed to.

================
_`Documentation`
================

``python-telegram-bot``'s documentation lives at `Read the Docs <http://python-telegram-bot.readthedocs.org/en/latest/>`_.

==========
_`License`
==========

You may copy, distribute and modify the software provided that modifications are described and licensed for free under `LGPL-3 <http://www.gnu.org/licenses/lgpl-3.0.html>`_. Derivatives works (including modifications or anything statically linked to the library) can only be redistributed under `LGPL-3 <http://www.gnu.org/licenses/lgpl-3.0.html>`_, but applications that use the library don't have to be.

==========
_`Contact`
==========

Feel free to join to our `Telegram group <https://telegram.me/joinchat/ALnA-AJQm5R7Km9hdCgyng>`_.

=======
_`TODO`
=======

Patches and bug reports are `welcome <https://github.com/python-telegram-bot/python-telegram-bot/issues/new>`_, just please keep the style consistent with the original source.
