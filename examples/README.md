# Examples

In this folder there are small examples to show what a bot written with `python-telegram-bot` looks like. Some bots focus on one specific aspect of the Telegram Bot API while others focus on one of the mechanics of this library. Except for the [`echobot.py`](#pure-api) example, they all use the high-level framework this library provides with the [`telegram.ext`](https://python-telegram-bot.readthedocs.io/en/latest/telegram.ext.html) submodule.

All examples are licensed under the [CC0 License](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/LICENSE.txt) and are therefore fully dedicated to the public domain. You can use them as the base for your own bots without worrying about copyrights.

### [`echobot2.py`](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py) 
This is probably the base for most of the bots made with `python-telegram-bot`. It simply replies to each text message with a message that contains the same text.

### [`timerbot.py`](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py) 
This bot uses the [`JobQueue`](https://python-telegram-bot.readthedocs.io/en/latest/telegram.ext.jobqueue.html) class to send timed messages. The user sets a timer by using `/set` command with a specific time, for example `/set 30`. The bot then sets up a job to send a message to that user after 30 seconds. The user can also cancel the timer by sending `/unset`. To learn more about the `JobQueue`, read [this wiki article](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-JobQueue).

### [`conversationbot.py`](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/conversationbot.py)
A common task for a bot is to ask information from the user. In v5.0 of this library, we introduced the [`ConversationHandler`](https://python-telegram-bot.readthedocs.io/en/latest/telegram.ext.conversationhandler.html) for that exact purpose. This example uses it to retrieve user-information in a conversation-like style. To get a better understanding, take a look at the [state diagram](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/conversationbot.png).

### [`conversationbot2.py`](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/conversationbot2.py)
A more complex example of a bot that uses the `ConversationHandler`. It is also more confusing. Good thing there is a [fancy state diagram](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/conversationbot2.png) for this one, too!

### [`inlinekeyboard.py`](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/inlinekeyboard.py)
This example sheds some light on inline keyboards, callback queries and message editing.

### [`inlinebot.py`](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/inlinebot.py)
A basic example of an [inline bot](https://core.telegram.org/bots/inline). Don't forget to enable inline mode with [@BotFather](https://telegram.me/BotFather).

### [`paymentbot.py`](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/paymentbot.py)
A basic example of a bot that can accept payments. Don't forget to enable and configure payments with [@BotFather](https://telegram.me/BotFather).

### [`persistentconversationbot.py`](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/persistentconversationbot.py)
A basic example of a bot store conversation state and user_data over multiple restarts.

## Pure API
The [`echobot.py`](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot.py) example uses only the pure, "bare-metal" API wrapper. 
