.. image:: https://github.com/python-telegram-bot/logos/blob/master/logo-text/png/ptb-logo-text_768.png?raw=true
   :align: center
   :target: https://github.com/python-telegram-bot/logos
   :alt: python-telegram-bot Logo

Not **just** a Python wrapper around the Telegram Bot API

*Stay tuned for library updates and new releases on our* `Telegram Channel <https://telegram.me/pythontelegrambotchannel>`_.

.. image:: https://img.shields.io/pypi/v/python-telegram-bot.svg
   :target: https://pypi.python.org/pypi/python-telegram-bot
   :alt: PyPi Package Version

.. image:: https://img.shields.io/pypi/pyversions/python-telegram-bot.svg
   :target: https://pypi.python.org/pypi/python-telegram-bot
   :alt: Supported python versions

.. image:: https://readthedocs.org/projects/python-telegram-bot/badge/?version=latest
   :target: https://readthedocs.org/projects/python-telegram-bot/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/l/python-telegram-bot.svg
   :target: https://www.gnu.org/licenses/lgpl-3.0.html
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
   :target: https://telegram.me/pythontelegrambotgroup
   :alt: Telegram Group

=================
Table of contents
=================

- `Introduction`_

- `Telegram API support`_

- `Installing`_

- `Getting started`_

  #. `Learning by example`_

  #. `API`_

  #. `Extensions`_

  #. `JobQueue`_

  #. `Logging`_

  #. `Documentation`_

- `Getting help`_

- `Contributing`_

- `License`_

===============
_`Introduction`
===============

This library provides a pure Python interface for the `Telegram Bot API <https://core.telegram.org/bots/api>`_. It works with Python versions from 2.6+. It also works with `Google App Engine <https://cloud.google.com/appengine>`_.

=======================
_`Telegram API support`
=======================

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
answerInlineQuery         Yes
kickChatMember            Yes
unbanChatMember           Yes
answerCallbackQuery       Yes
editMessageText           Yes
editMessageCaption        Yes
editMessageReplyMarkup    Yes
========================= ============

=============
_`Installing`
=============

You can install or upgrade python-telegram-bot with:

.. code:: shell

    $ pip install python-telegram-bot --upgrade

==================
_`Getting started`
==================

View the last release API documentation at: https://core.telegram.org/bots/api

This library uses the `logging` module. To set up logging to standard output, put:

.. code:: python

    import logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

at the beginning of your script.

**Note:** The ``telegram.ext`` module will catch errors that would cause the bot to crash. All these are logged to the ``logging`` module, so it's recommended to use this if you are looking for error causes.

----------------------
_`Learning by example`
----------------------

We believe that the best way to learn and understand this simple package is by example. So here are some examples for you to review. Even if it's not your approach for learning, please take a look at ``echobot2`` (below), it is de facto the base for most of the bots out there. Best of all, the code for these examples are released to the public domain, so you can start by grabbing the code and building on top of it.

- `clibot <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/clibot.py>`_ has a command line interface.

- `echobot2 <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py>`_ replies back messages.

- `inlinebot <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/inlinebot.py>`_ basic example of an `inline bot <https://core.telegram.org/bots/inline>`_

- `state machine bot <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/state_machine_bot.py>`_ keeps the state for individual users, useful for multipart conversations

- `timerbot <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py>`_ uses the ``JobQueue`` to send timed messages.

Examples using only the API:

- `echobot <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/legacy/echobot.py>`_ replies back messages.

- `roboed <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/legacy/roboed.py>`_ talks to `Robô Ed <http://www.ed.conpet.gov.br/br/converse.php>`_.

Look at the examples on the `wiki <https://github.com/python-telegram-bot/python-telegram-bot/wiki/Examples>`_ to see other bots the community has built.

------
_`API`
------

Note: Using the ``Bot`` class directly is the 'old' method, we have an easier way to make bots described in the next section.  All of this is however still important information, even if you're using the ``telegram.ext`` submodule!

The API is exposed via the ``telegram.Bot`` class. The methods have names as described in the official `Telegram Bot API <https://core.telegram.org/bots/api>`_, but equivalent snake_case methods are available for `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ enthusiasts. So for example ``telegram.Bot.send_message`` is the same as ``telegram.Bot.sendMessage``.

To generate an Access Token you have to talk to `BotFather <https://telegram.me/botfather>`_ and follow a few simple steps (described `here <https://core.telegram.org/bots#6-botfather>`_).

For full details see the `Bots: An introduction for developers <https://core.telegram.org/bots>`_.

To create an instance of the ``telegram.Bot``:

.. code:: python

    >>> import telegram
    >>> bot = telegram.Bot(token='token')

To see if your credentials are successful:

.. code:: python

    >>> print(bot.getMe())
    {"first_name": "Toledo's Palace Bot", "username": "ToledosPalaceBot"}

Bots can't initiate conversations with users. A user must either add them to a group or send them a message first. People can use ``telegram.me/<bot_username>`` links or username search to find your bot.

To fetch text messages sent to your Bot:

.. code:: python

    >>> updates = bot.getUpdates()
    >>> print([u.message.text for u in updates])

To fetch images sent to your Bot:

.. code:: python

    >>> updates = bot.getUpdates()
    >>> print([u.message.photo for u in updates if u.message.photo])

To reply messages you'll always need the ``chat_id``:

.. code:: python

    >>> chat_id = bot.getUpdates()[-1].message.chat_id

To post a text message:

.. code:: python

    >>> bot.sendMessage(chat_id=chat_id, text="I'm sorry Dave I'm afraid I can't do that.")

To post a text message with markdown:

.. code:: python

    >>> bot.sendMessage(chat_id=chat_id, text="*bold* _italic_ [link](http://google.com).", parse_mode=telegram.ParseMode.MARKDOWN)

To post a text message with Html style:

.. code:: python

	>>> bot.sendMessage(chat_id=chat_id, text='<b>bold</b> <i>italic</i> <a href="http://google.com">link</a>.', parse_mode=telegram.ParseMode.HTML)

To post an Emoji (special thanks to `Tim Whitlock <http://apps.timwhitlock.info/emoji/tables/unicode>`_):

.. code:: python

    >>> bot.sendMessage(chat_id=chat_id, text=telegram.Emoji.PILE_OF_POO)

To post an image file via URL:

.. code:: python

    >>> bot.sendPhoto(chat_id=chat_id, photo='https://telegram.org/img/t_logo.png')

To post an image file from disk:

.. code:: python

    >>> bot.sendPhoto(chat_id=chat_id, photo=open('tests/test.png', 'rb'))

To post a voice file from disk:

.. code:: python

    >>> bot.sendVoice(chat_id=chat_id, voice=open('tests/telegram.ogg', 'rb'))

To tell the user that something is happening on bot's side:

.. code:: python

    >>> bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

To create `Custom Keyboards <https://core.telegram.org/bots#keyboards>`_:

.. code:: python

    >>> custom_keyboard = [[ telegram.KeyboardButton(telegram.Emoji.THUMBS_UP_SIGN),
    ...     telegram.KeyboardButton(telegram.Emoji.THUMBS_DOWN_SIGN) ]]
    >>> reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    >>> bot.sendMessage(chat_id=chat_id, text="Stay here, I'll be back.", reply_markup=reply_markup)

To hide `Custom Keyboards <https://core.telegram.org/bots#keyboards>`_:

.. code:: python

    >>> reply_markup = telegram.ReplyKeyboardHide()
    >>> bot.sendMessage(chat_id=chat_id, text="I'm back.", reply_markup=reply_markup)

To download a file (you will need its ``file_id``):

.. code:: python

    >>> file_id = message.voice.file_id
    >>> newFile = bot.getFile(file_id)
    >>> newFile.download('voice.ogg')

There are many more API methods, to read the full API documentation:

.. code:: shell

    $ pydoc telegram.Bot

-------------
_`Extensions`
-------------

The ``telegram.ext`` submodule is built on top of the bare-metal API. It provides an easy-to-use interface to the ``telegram.Bot`` by caring about getting new updates with the ``Updater`` class from telegram and forwarding them to the ``Dispatcher`` class. We can register handler functions in the ``Dispatcher`` to make our bot react to Telegram commands, messages and even arbitrary updates.

We'll need an Access Token. **Note:** If you have done this in the previous step, you can use that one. To generate an Access Token, we have to talk to `BotFather <https://telegram.me/botfather>`_ and follow a few simple steps (described `here <https://core.telegram.org/bots#botfather>`_).

First, we create an ``Updater`` object:

.. code:: python

   >>> from telegram.ext import Updater
   >>> updater = Updater(token='token')

For quicker access to the ``Dispatcher`` used by our ``Updater``, we can introduce it locally:

.. code:: python

   >>> dispatcher = updater.dispatcher

Now, we need to define a function that should process a specific type of update:

.. code:: python

   >>> def start(bot, update):
   ...   bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

We want this function to be called on a Telegram message that contains the ``/start`` command. To do that, we have to use a ``CommandHandler`` object and register it in the dispatcher:

.. code:: python

   >>> from telegram.ext import CommandHandler
   >>> start_handler = CommandHandler('start', start)
   >>> dispatcher.add_handler(start_handler)

The last step is to tell the ``Updater`` to start working:

.. code:: python

   >>> updater.start_polling()

Our bot is now up and running (go ahead and try it)! It's not doing anything yet, besides answering to the ``/start`` command. Let's add another handler that listens for regular messages. We're using the `MessageHandler` here to echo to all text messages:

.. code:: python

   >>> def echo(bot, update):
   ...   bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)
   ...
   >>> from telegram.ext import MessageHandler, Filters
   >>> echo_handler = MessageHandler([Filters.text], echo)
   >>> dispatcher.add_handler(echo_handler)

Our bot should now reply to all text messages that are not a command with a message that has the same content.

Let's add some functionality to our bot. We want to add the ``/caps`` command, that will take some text as parameter and return it in all caps. We can get the arguments that were passed to a command in the handler function:

.. code:: python

   >>> def caps(bot, update, args):
   ...   text_caps = ' '.join(args).upper()
   ...   bot.sendMessage(chat_id=update.message.chat_id, text=text_caps)
   ...
   >>> caps_handler = CommandHandler('caps', caps, pass_args=True)
   >>> dispatcher.add_handler(caps_handler)

To enable our bot to respond to inline queries, we can add the following (you will also have to talk to BotFather):

.. code:: python

   >>> from telegram import InlineQueryResultArticle
   >>> def inline_caps(bot, update):
   ...   query = bot.update.inline_query.query
   ...   results = list()
   ...   results.append(InlineQueryResultArticle(query.upper(), 'Caps', query.upper()))
   ...   bot.answerInlineQuery(update.inline_query.id, results)
   ...
   >>> from telegram.ext import InlineQueryHandler
   >>> inline_caps_handler = InlineQueryHandler(inline_caps)
   >>> dispatcher.add_handler(inline_caps_handler)

People might try to send commands to the bot that it doesn't understand, so we can use a ``MessageHandler`` with a ``command`` filter to recognize all commands that were not recognized by the previous handlers. **Note:** This handler has to be added last, else it will be triggered before the ``CommandHandlers`` had a chance to look at the update:

.. code:: python

   >>> def unknown(bot, update):
   ...   bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")
   ...
   >>> unknown_handler = MessageHandler([Filters.command], unknown)
   >>> dispatcher.add_handler(unknown_handler)

If you're done playing around, stop the bot with this:

.. code:: python

   >>> updater.stop()

Check out more examples in the `examples folder <https://github.com/python-telegram-bot/python-telegram-bot/tree/master/examples>`_!

-----------
_`JobQueue`
-----------

The ``JobQueue`` allows you to perform tasks with a delay or even periodically. The ``Updater`` will create one for you:

.. code:: python

    >>> from telegram.ext import Updater
    >>> u = Updater('TOKEN')
    >>> j = u.job_queue

The job queue uses functions for tasks, so we define one and add it to the queue. Usually, when the first job is added to the queue, it wil start automatically. We can prevent this by setting ``prevent_autostart=True``:

.. code:: python

    >>> def job1(bot):
    ...     bot.sendMessage(chat_id='@examplechannel', text='One message every minute')
    >>> j.put(job1, 60, next_t=0, prevent_autostart=True)

You can also have a job that will not be executed repeatedly:

.. code:: python

    >>> def job2(bot):
    ...     bot.sendMessage(chat_id='@examplechannel', text='A single message with 30s delay')
    >>> j.put(job2, 30, repeat=False)

Now, because we didn't prevent the auto start this time, the queue will start ticking. It runs in a seperate thread, so it is non-blocking. When we stop the Updater, the related queue will be stopped as well:

.. code:: python

    >>> u.stop()

We can also stop the job queue by itself:

.. code:: python

    >>> j.stop()

----------
_`Logging`
----------

You can get logs in your main application by calling `logging` and setting the log level you want:

.. code:: python

    >>> import logging
    >>> logger = logging.getLogger()
    >>> logger.setLevel(logging.INFO)

If you want DEBUG logs instead:

.. code:: python

    >>> logger.setLevel(logging.DEBUG)


================
_`Documentation`
================

``python-telegram-bot``'s documentation lives at `Read the Docs <https://python-telegram-bot.readthedocs.org/en/latest/>`_.

===============
_`Getting help`
===============

You can get help in several ways:

1. We have a vibrant community of developers helping each other in our `Telegram group <https://telegram.me/pythontelegrambotgroup>`_. Join us!
   
2. You can ask for help on Stack Overflow using the `python-telegram-bot tag <https://stackoverflow.com/questions/tagged/python-telegram-bot>`_.
   
3. As last resort, the developers are ready to help you with `serious issues <https://github.com/python-telegram-bot/python-telegram-bot/issues/new>`_.


===============
_`Contributing`
===============

Contributions of all sizes are welcome. Please review our `contribution guidelines <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/CONTRIBUTING.rst>`_ to get started. You can also help by `reporting bugs <https://github.com/python-telegram-bot/python-telegram-bot/issues/new>`_.

==========
_`License`
==========

You may copy, distribute and modify the software provided that modifications are described and licensed for free under `LGPL-3 <https://www.gnu.org/licenses/lgpl-3.0.html>`_. Derivatives works (including modifications or anything statically linked to the library) can only be redistributed under `LGPL-3 <https://www.gnu.org/licenses/lgpl-3.0.html>`_, but applications that use the library don't have to be.
