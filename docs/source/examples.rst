Examples
========

In this section we display small examples to show what a bot written with
``python-telegram-bot`` looks like.
Some bots focus on one specific
aspect of the Telegram Bot API while others focus on one of the
mechanics of this library. Except for the
:any:`examples.rawapibot` example, they all use the high-level
framework this library provides with the
:any:`telegram.ext <telegram.ext>` submodule.

All examples are licensed under the `CC0
License <https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/LICENSE.txt>`__
and are therefore fully dedicated to the public domain. You can use them
as the base for your own bots without worrying about copyrights.

Do note that we ignore one pythonic convention. Best practice would
dictate, in many handler callbacks function signatures, to replace the
argument ``context`` with an underscore, since ``context`` is an unused
local variable in those callbacks. However, since these are examples and
not having a name for that argument confuses beginners, we decided to
have it present.

:any:`examples.echobot`
-----------------------

This is probably the base for most of the bots made with
``python-telegram-bot``. It simply replies to each text message with a
message that contains the same text.

:any:`examples.timerbot`
------------------------

This bot uses the
:class:`telegram.ext.JobQueue`
class to send timed messages. The user sets a timer by using ``/set``
command with a specific time, for example ``/set 30``. The bot then sets
up a job to send a message to that user after 30 seconds. The user can
also cancel the timer by sending ``/unset``. To learn more about the
``JobQueue``, read `this wiki
article <https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-JobQueue>`__.
Note: To use ``JobQueue``, you must install PTB via ``pip install python-telegram-bot[job-queue]``

:any:`examples.conversationbot`
-------------------------------

A common task for a bot is to ask information from the user. In v5.0 of
this library, we introduced the
:class:`telegram.ext.ConversationHandler`
for that exact purpose. This example uses it to retrieve
user-information in a conversation-like style. To get a better
understanding, take a look at the :ref:`state diagram <conversationbot-diagram>`.

:any:`examples.conversationbot2`
--------------------------------

A more complex example of a bot that uses the ``ConversationHandler``.
It is also more confusing. Good thing there is a :ref:`fancy state diagram <conversationbot2-diagram>`.
for this one, too!

:any:`examples.nestedconversationbot`
-------------------------------------

A even more complex example of a bot that uses the nested
``ConversationHandler``\ s. While it’s certainly not that complex that
you couldn’t built it without nested ``ConversationHanldler``\ s, it
gives a good impression on how to work with them. Of course, there is a
:ref:`fancy state diagram <nestedconversationbot-diagram>`
for this example, too!

:any:`examples.persistentconversationbot`
-----------------------------------------

A basic example of a bot store conversation state and user_data over
multiple restarts.

:any:`examples.inlinekeyboard`
------------------------------

This example sheds some light on inline keyboards, callback queries and
message editing. A wiki site explaining this examples lives
`here <https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example>`__.

:any:`examples.inlinekeyboard2`
-------------------------------

A more complex example about inline keyboards, callback queries and
message editing. This example showcases how an interactive menu could be
build using inline keyboards.

:any:`examples.deeplinking`
---------------------------

A basic example on how to use deeplinking with inline keyboards.

:any:`examples.inlinebot`
-------------------------

A basic example of an `inline
bot <https://core.telegram.org/bots/inline>`__. Don’t forget to enable
inline mode with `@BotFather <https://telegram.me/BotFather>`_.

:any:`examples.pollbot`
-----------------------

This example sheds some light on polls, poll answers and the
corresponding handlers.

:any:`examples.passportbot`
---------------------------

A basic example of a bot that can accept passports. Use in combination
with the :ref:`HTML page <passportbot-html>`.
Don’t forget to enable and configure payments with
`@BotFather <https://telegram.me/BotFather>`_. Check out this
`guide <https://github.com/python-telegram-bot/python-telegram-bot/wiki/Telegram-Passport>`__
on Telegram passports in PTB.
Note: To use Telegram Passport, you must install PTB via ``pip install python-telegram-bot[passport]``

:any:`examples.paymentbot`
--------------------------

A basic example of a bot that can accept payments. Don’t forget to
enable and configure payments with
`@BotFather <https://telegram.me/BotFather>`_.

:any:`examples.errorhandlerbot`
-------------------------------

A basic example on how to set up a custom error handler.

:any:`examples.chatmemberbot`
-----------------------------

A basic example on how ``(my_)chat_member`` updates can be used.

:any:`examples.webappbot`
-------------------------

A basic example of how `Telegram
WebApps <https://core.telegram.org/bots/webapps>`__ can be used. Use in
combination with the :ref:`HTML page <webappbot-html>`.
For your convenience, this file is hosted by the PTB team such that you
don’t need to host it yourself. Uses the
`iro.js <https://iro.js.org>`__ JavaScript library to showcase a
user interface that is hard to achieve with native Telegram
functionality.

:any:`examples.contexttypesbot`
-------------------------------

This example showcases how ``telegram.ext.ContextTypes`` can be used to
customize the ``context`` argument of handler and job callbacks.

:any:`examples.customwebhookbot`
--------------------------------

This example showcases how a custom webhook setup can be used in
combination with ``telegram.ext.Application``.

:any:`examples.arbitrarycallbackdatabot`
----------------------------------------

This example showcases how PTBs “arbitrary callback data” feature can be
used.
Note: To use arbitrary callback data, you must install PTB via ``pip install python-telegram-bot[callback-data]``

Pure API
--------

The :any:`examples.rawapibot` example example uses only the pure, “bare-metal” API wrapper.

.. toctree::
   :hidden:

   examples.arbitrarycallbackdatabot
   examples.chatmemberbot
   examples.contexttypesbot
   examples.conversationbot
   examples.conversationbot2
   examples.customwebhookbot
   examples.deeplinking
   examples.echobot
   examples.errorhandlerbot
   examples.inlinebot
   examples.inlinekeyboard
   examples.inlinekeyboard2
   examples.nestedconversationbot
   examples.passportbot
   examples.paymentbot
   examples.persistentconversationbot
   examples.pollbot
   examples.rawapibot
   examples.timerbot
   examples.webappbot

